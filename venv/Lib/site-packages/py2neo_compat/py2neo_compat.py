# -*- coding: utf-8 -*-

"""Main module."""

from __future__ import absolute_import, print_function

import logging
import sys
from collections import namedtuple

try:
    # noinspection PyUnresolvedReferences
    from typing import (
        Any, Dict, List, Mapping, NamedTuple, Optional,
        Union, Tuple, Iterable,  # noqa
    )
except ImportError:  # pragma: no cover
    """Module :mod:`typing` not required for Py27-compatible type comments."""

import six
from boltons.cacheutils import cachedproperty

from .util import import_symbol, qualify_symbol, SimpleNamespace, foremost

import py2neo
if py2neo.__version__.startswith('1.6'):
    py2neo_ver = 1
elif py2neo.__version__.startswith('2.0'):
    py2neo_ver = 2
elif py2neo.__version__.startswith('3'):  # pragma: no cover
    py2neo_ver = 3
else:  # pragma: no cover
    raise NotImplementedError("py2neo %d not supported" % py2neo.__version__)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())

__all__ = ('py2neo_ver',)


_ = ImportMap = namedtuple('ImportMap', ('name', 'v1', 'v2', 'v3'))

IMPORT_TABLE = [    # v1                    v2          v3
_('Graph',          '.neo4j.GraphDatabaseService',
                                            '.',        '.'),
_('Node',           '.neo4j.',              '.',        '.'),
_('Relationship',   '.neo4j.',              '.',        '.'),
_('Record',         '.neo4j.',              '.cypher.core.', '.'),
_('node',           '.',                    '.',        '.cast_node'),
_('rel',            '.',                    '.',        '.cast_relationship'),
_('ServerError',    '.neo4j.',              '.core.',   '.'),
_('ClientError',    '.neo4j.',              '.core.',   '.'),
_('URI',            '.neo4j.',              '.core.',   '.'),
_('Resource',       '.neo4j.',              '.core.',   '.database.'),
]

del _


this_module = sys.modules[__name__]



def import_all():
    """Import symbols from the IMPORT_TABLE."""
    global __all__, this_module

    for item in IMPORT_TABLE:
        ns = item[py2neo_ver]
        modname, symname = qualify_symbol(item.name, ns)
        obj = import_symbol(modname, symname)
        setattr(this_module, item.name, obj)
        __all__ += (item.name,)


import_all()

if False:  # Trick PyCharm into believing that these exist
    Graph = py2neo.Graph
    Node = py2neo.Node
    Relationship = py2neo.Relationship
    Resource = py2neo.Resource
    rel = py2neo.rel
    node = py2neo.node


py2neo_property_classes = (Node, Relationship)

if py2neo_ver == 1:
    pass
elif py2neo_ver == 2:
    # noinspection PyUnresolvedReferences
    from py2neo import PropertySet, PropertyContainer
    py2neo_property_classes += (PropertySet, PropertyContainer)
elif py2neo_ver == 3:
    # noinspection PyUnresolvedReferences
    from py2neo import PropertyDict
    py2neo_property_classes += (PropertyDict,)


def monkey_patch_py2neo():
    # type: () -> None
    """Install compat code into py2neo mod namespace & objects."""

    for item in IMPORT_TABLE:
        if not hasattr(py2neo, item.name):
            setattr(py2neo, item.name, getattr(this_module, item.name))

    if py2neo_ver == 1:
        monkey_patch_py2neo_v1()
    elif py2neo_ver == 2:
        monkey_patch_py2neo_v2()
    elif py2neo_ver == 3:
        monkey_patch_py2neo_v3()


__all__ += ('monkey_patch_py2neo',)


# noinspection PyUnresolvedReferences
def monkey_patch_py2neo_v1():
    # type: () -> None
    """Install compat code into py2neo v1 mod namespace & objects."""

    global Graph, Node, Relationship

    Graph.delete_all = Graph.clear
    Graph.uri = Graph.__uri__
    # noinspection PyProtectedMember
    Graph.resource = property(lambda s: s._resource)
    Graph.find_one = lambda s, *args, **kws: foremost(s.find(*args, **kws))

    def cypher_prop(self):
        # noinspection PyUnresolvedReferences
        from py2neo.neo4j import CypherQuery

        cypher_ns = SimpleNamespace()
        cypher_ns.stream = six.create_bound_method(
            lambda s, q, **ps: CypherQuery(s, q).stream(**ps),
            self.graph_db)
        cypher_ns.execute = six.create_bound_method(
            lambda s, q, **ps: CypherQuery(s, q).execute(**ps),
            self.graph_db)
        return cypher_ns

    Graph.cypher = cachedproperty(cypher_prop)
    del cypher_prop

    def legacy_prop(graph):
        """Emulate py2neo 2.0's Graph.legacy namespace.

        All of the GraphDatabaseService.get_index* (and related) methods have
        been moved to a separate class."""

        legacy_ns = SimpleNamespace()

        index_methods = [
            'delete_index',
            'get_index',
            'get_indexed_node',
            'get_indexed_relationship',
            'get_indexes',
            'get_or_create_index',
            'get_or_create_indexed_node',
        ]

        for m in index_methods:
            setattr(legacy_ns, m, getattr(graph, m))

        return legacy_ns

    Graph.legacy = cachedproperty(legacy_prop)
    del legacy_prop

    def create_unique(relation):
        # type: (Relationship) -> Tuple(Relationship)
        """Create a unique path like in py2neo 2.0.

        Only attempt to create a single relationship with this; both 2.0's
        `create_unique` and `Node.get_or_create_path` can do more, but this
        is enough and keeps it simple.
        """
        start = relation.start_node
        end = relation.end_node
        path = start.get_or_create_path(relation, end)
        return tuple(path.relationships)

    Graph.create_unique = staticmethod(create_unique)

    # py2neo 1.6 did everything eagerly; 2.0 requires explicit sync
    Node.push = Node.refresh
    Node.pull = Node.refresh
    # noinspection PyPropertyAccess
    Node.labels = property(lambda s: s.get_labels())
    Relationship.push = Relationship.refresh
    Relationship.pull = Relationship.refresh

    py2neo_legacy = SimpleNamespace()
    sys.modules['py2neo.legacy'] = py2neo_legacy
    py2neo.legacy = py2neo_legacy
    py2neo_legacy.LegacyWriteBatch = py2neo.neo4j.WriteBatch
    py2neo_legacy.Index = py2neo.neo4j.Index

    py2neo_batch = SimpleNamespace()
    sys.modules['py2neo.batch'] = py2neo_batch
    py2neo.batch = py2neo_batch
    py2neo_batch.WriteBatch = py2neo.neo4j.WriteBatch


# noinspection PyUnresolvedReferences
def monkey_patch_py2neo_v2():
    # type: () -> None
    """Install compat code into py2neo v2 mod namespace & objects."""

    import py2neo.core
    import py2neo.cypher.core

    py2neo.Record = py2neo.cypher.core.Record
    py2neo.ServerError = py2neo.core.ServerError
    py2neo.URI = py2neo.core.URI


def monkey_patch_py2neo_v3():
    # type: () -> None
    """Install compat code into py2neo v3 mod namespace & objects."""

    # WHY can't get just have the URI like normal adults?
    py2neo.Graph.uri = property(lambda s: s.__remote__.uri)
    # TODO
    # py2neo.ext.batman.ManualIndexWriteBatch
    # Graph.create changed incompatibly
    pass


def graph_metadata(graph, key=None):
    # type: (Graph, Optional[str]) -> Union[Dict, str]
    """Get graph metadata or a key in the metadata."""

    # v1.6 has Graph.__metadata__
    metadata = getattr(graph, '__metadata__', None)
    if metadata is not None:
        metadata = dict(metadata)
    elif hasattr(graph, 'resource'):
        # v2.0 has Graph.resource.metadata
        # noinspection PyUnresolvedReferences
        metadata = graph.resource.metadata
    elif hasattr(graph, '__remote__'):
        metadata = graph.__remote__.metadata

    if key is not None:
        return metadata[key]
    else:
        return metadata


__all__ += ('graph_metadata',)


def py2neo_entity_to_dict(entity):
    # type: (Union[Node,Relationship,PropertySet]) -> Dict[str, Any]
    """Convert an "entity" to a `dict`.

    All three major versions are incompatible with how to get a dict
    from the properties of an entity:

    * 1.6 only needs get_properties() (but dict() doesn't hurt)
    * 2 requires both get_properties and dict()
    * 3 only needs dict() and has no get_properties

    Catching :class:`AttributeError` also allows this to work a PropertySet,
    which is the output of `get_properties()` on 2.
    """
    assert isinstance(entity, py2neo_property_classes)

    try:
        # noinspection PyUnresolvedReferences
        entity = entity.get_properties()
    except AttributeError:
        pass
    finally:
        entity = dict(entity)
    return entity


to_dict = py2neo_entity_to_dict
__all__ += ('py2neo_entity_to_dict', 'to_dict')


if py2neo_ver == 1:
    def create_node(
            graph=None,  # type: Optional[py2neo.Graph]
            labels=None,  # type: Optional[Iterable[str]]
            properties=None,  # type: Optional[Mapping[str, Any]]
    ):
        # type: (...) -> Node
        """Cross-version function to create a node."""
        properties = properties or {}

        if labels and graph is None:
            raise TypeError('Parameter "graph" is required for py2neo v1 with'
                            ' labels')

        node = py2neo.node(properties)
        if graph is not None:
            node = foremost(graph.create(node))
        if labels:
            node.add_labels(*labels)
        return node

elif py2neo_ver == 2:
    def create_node(
        graph=None,  # type: Optional[py2neo.Graph]
        labels=None,  # type: Optional[Iterable[str]]
        properties=None,  # type: Optional[Mapping[str, Any]]
    ):
        # type: (...) -> Node
        """Cross-version function to create a node."""
        properties = properties or {}
        labels = labels or []

        node = py2neo.node(*labels, **properties)
        if graph is not None:
            node = foremost(graph.create(node))
        return node


__all__ += ('create_node',)


if py2neo_ver == 1:
    def update_properties(entity, properties):
        entity.update_properties(properties)
elif py2neo_ver == 2:
    def update_properties(entity, properties):
        entity.properties.update(properties)


__all__ += ('update_properties',)
