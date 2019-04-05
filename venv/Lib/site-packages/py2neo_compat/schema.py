#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""py2neo schema"""

from __future__ import absolute_import, print_function

import logging
from functools import partial

from six.moves.urllib.parse import urljoin

try:
    # noinspection PyCompatibility,PyUnresolvedReferences
    from typing import NamedTuple, Iterator, Iterable, Tuple, List, Union
    OptionalStrBool = Union[str, bool, None]
except ImportError:  # pragma: no cover
    "Module 'typing' is optional for 2.7-compatible types in comments"

# This works for 1.6, 2, 3.1 but not 4b2
from py2neo.packages.httpstream import Resource
from py2neo.packages.httpstream.http import URITemplate

from . import py2neo_compat
from .py2neo_compat import Graph, graph_metadata, py2neo_ver

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())

SchemaItem = NamedTuple('SchemaItem', fields=(
    ('label', str),
    ('property_key', str),
))


def schema_constraints(graph):
    # type: (Graph) -> Iterable[Tuple[str, List[str], str]]
    """Query iterable list of *all* schema constraints.

    This works around the fact that, in Neo4j 2.3 and :mod:`py2neo` 2.0.8 at
    least, `graph.node_labels` only returns labels used by extant nodes, whereas
    previously it returned all labels, which are needed for clearing the
    constrain schema by iterating over the labels.
    """
    resource_type = type(Resource)

    constraint_resource = Resource(graph_metadata(graph, 'constraints'))

    return ((c['label'], c['property_keys'], c['type'])
            for c in constraint_resource.get().content)


def schema_indexes(graph):
    # type: (Graph) -> List[Tuple[str, List[str]]]
    """Query iterable list of *all* schema indexes.

    This works around the fact that, in Neo4j 2.3 and :mod:`py2neo` 2.0.8 at
    least, `graph.node_labels` only returns labels used by extant nodes, whereas
    previously it returned all labels, which are needed for clearing the
    constrain schema by iterating over the labels.
    """
    index_resource = Resource(graph_metadata(graph, 'indexes'))

    return [(n['label'], n['property_keys']) for n in
            index_resource.get().content]


def schema_template_subpath(label='', property_key='', constraint_type=''):
    # type: (OptionalStrBool, OptionalStrBool, OptionalStrBool) -> str
    """Get a string URI template by looking up in a map.

    The content of label and property_key do not matter, provided that `bool`
    accurately reflects the intended absence or presence in the resulting URI.

    Cases:
    * All indexes or constraints (GET):
        e.g., http://localhost:7474/db/data/schema/constraint
    * All indexes or constraints for a given label (GET, POST (index)):
        e.g., http://localhost:7474/db/data/schema/constraint/person
    * A particular index for a label and property key (DELETE (index))
        e.g., http://localhost:7474/db/data/schema/index/{label}/{key}
    * All constraints for a given label and constraint type (GET, POST):
        e.g., http://localhost:7474/db/data/schema/constraint/person/uniqueness
    * A particular constraint for a given label, constraint type and key (DELETE)
    """

    # noinspection PyPep8Naming
    CR = ConditionRecord = NamedTuple('ConditionRecord', fields=(
        ('label', bool),
        ('property_key', bool),
        ('constraint_type', bool),
    ))

    condition_map = {
        CR(label=False, property_key=False, constraint_type=False): '',
        CR(True,        property_key=False, constraint_type=False): '{label}/',

        CR(True,        True,               constraint_type=False):
            '{label}/{property_key}',

        CR(True,        property_key=False, constraint_type=True):
            '{label}/%(constraint_type)s',

        CR(True,        True,               True):
            '{label}/%(constraint_type)s/{property_key}',

    }

    condition_key = CR(bool(label), bool(property_key), bool(constraint_type))

    try:
        template = condition_map[condition_key]
    except KeyError:
        raise ValueError('Invalid params for schema subpath condition_key="%s"'
                         % (condition_key,))

    template = template % {'constraint_type': constraint_type}

    return template


def _schema_template(graph, schema_type, label=None, property_key=None,
                     constraint_type=''):
    """Generate a URITemplate for schema."""

    subpath = schema_template_subpath(label=label,
                                      property_key=property_key,
                                      constraint_type=constraint_type)

    uri = graph_metadata(graph, schema_type)
    uri = urljoin(uri + '/', subpath)
    key_template = URITemplate(uri)

    return key_template


def _drop_constraint(graph, constraint_type, label, property_key):
    # type: (Graph, str, str) -> None

    key_template = _schema_template(graph,
                                    schema_type='constraints',
                                    constraint_type=constraint_type,
                                    label=label,
                                    property_key=property_key)

    url_expanded = key_template.expand(label=label, property_key=property_key)
    resource = Resource(url_expanded)

    try:
        resource.delete()
    except Exception:
        log.exception('error deleting constraint'
                      ' type="%s" label="%s" property="%s"',
                      constraint_type, label, property_key)
        raise


def _create_constraint(graph, constraint_type, label, property_key):
    """Create a uniqueness constraint."""
    tpl = _schema_template(graph, 'constraints',
                           label=label, property_key=False,
                           constraint_type=constraint_type)
    resource = Resource(tpl.expand(label=label,
                                   property_key=property_key))
    resource.post({"property_keys": [property_key]})


def create_uniqueness_constraint(graph, label, property_key):
    """Create uniqueness constraint."""
    # type: (Graph, str, str) -> None
    if hasattr(graph.schema, 'create_uniqueness_constraint'):
        graph.schema.create_uniqueness_constraint(label, property_key)
    else:
        _create_constraint(graph, 'uniqueness', label, property_key)


def drop_schema(graph):
    # type: (Graph) -> None
    """Drop all constraints and indexes."""
    drop_constraints(graph)
    drop_indexes(graph)


def drop_constraints(graph):
    # type: (Graph) -> None
    """Drop all constraints."""
    constraint_dispatch = {
        'UNIQUENESS': getattr(graph.schema,
                              'drop_uniqueness_constraint',
                              partial(_drop_constraint, graph, 'uniqueness')),
    }

    for label, property_keys, type_ in schema_constraints(graph):
        log.debug('dropping schema constraint for label="%s" properties="%s",'
                  ' type="%s"', label, ','.join(property_keys), type_)
        constraint_dispatch[type_](label, property_keys)


def drop_indexes(graph):
    # type: (Graph) -> None
    """Drop all schema indexes."""
    for label, property_keys in schema_indexes(graph):
        log.debug('dropping schema index for label="%s" properties="%s"',
                  label, ','.join(property_keys))
        try:
            graph.schema.drop_index(label, property_keys)
        except py2neo_compat.ServerError:
            # Usually means it doesn't have the index or
            # otherwise can't do it (e.g., py2neo v1.6)
            log.exception('dropping index label="%s" properties="%s"',
                          label, ','.join(property_keys))
        except Exception:  # FIXME more specific
            log.exception('dropping index label="%s" properties="%s"',
                          label, ','.join(property_keys))
            raise


dup_schema_exception_messages = [
    'Property key already indexed',
    'an index is already created',
    'There already exists an index for label',
    'Conflict',
    'Constraint already exists',
]

def create_schema(graph, schema_map, ignoredups=True):
    # type: (Graph) -> None
    """Create constraints and indexes.

    :param Graph graph: Instance of :class:`py2neo.Graph`.
    :param dict schema_map: Mapping describing schema where the key is the
        name of the schema type (corresponding with the keys of the `creators`
        dict below), and the values a list of :class:`SchemaItem` instances.

    e.g.:
        'uniqueness_constraints'|'indexes': [
            SchemaItem(label=..., property_key=...),
            ...
        ]
    """

    creators = {
        'uniqueness_constraints': partial(create_uniqueness_constraint, graph),
        'indexes': graph.schema.create_index
    }

    for schema_type, schema_items in schema_map.items():
        schema_creator = creators[schema_type]

        for item in schema_items:
            log.debug('creating schema_type="%s" for label="%s"'
                      ' property_key="%s"',
                      schema_type,
                      item.label,
                      item.property_key)

            try:
                schema_creator(item.label, item.property_key)
            except Exception as excp:
                if not ignoredups:
                    raise

                # We could be more specific with the exception but then we'd
                # have to deal with yet more symbol compatibility, so instead
                # we catch everything and match on the message.
                msg = excp.args[0]

                flag = False
                # import sys
                # print('Comparing msg="%s"' % msg, file=sys.stderr)
                for m in dup_schema_exception_messages:
                    # print('with m="%s"' % m, file=sys.stderr)
                    if m in msg:
                        flag = True
                        break

                if not flag:
                    raise
