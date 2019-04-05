#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Misc utilities"""

from __future__ import absolute_import, print_function

import logging

import importlib

try:  # pragma: no cover
    from typing import Iterable, TypeVar, Callable, Union, Optional
    C = TypeVar('C')  # Constructor/Class
    D = TypeVar('D')  # Default
    E = TypeVar('E')  # Element
    ElementPredicate = Callable[[E], bool]
except:
    """Module *typing* is optional for Python 2.7 type annotations."""

from boltons.iterutils import first


log = logging.getLogger(__name__)  # pylint: disable=invalid-name
log.addHandler(logging.NullHandler())


def foremost(iterable, default=None, key=lambda x: x is not None):
    # type: (Iterable[E], Optional[D], Optional[ElementPredicate]) -> Union[E, D]
    """Return first non-*None* element from an iterable or *default*.

    *foremost* is a specialized version of :func:`boltons.iterutils.first`,
    with its *key* parameter defaulting to a predicate for non-*None* instead
    of *True*.

    This is especially useful with py2neo, because an entity without properties
    evaluates to *False*, whereas we usually just want the first non-*None*
    item from a result.

    :param Iterable iterable: Iterable to work on.
    :param default: Default if all elements of *iterable* are *None*. Default is *None*.
    :return: First non-None element of Iterable.
    """
    return first(iterable, default=default, key=key)


# From the Python 3.3 doc:
# https://docs.python.org/3.3/library/types.html#standard-interpreter-types
#
# class types.SimpleNamespace
#
# A simple object subclass that provides
# attribute access to its namespace, as well as a meaningful repr.
#
# Unlike object, with SimpleNamespace you can add and remove
# attributes. If a SimpleNamespace object is initialized with keyword
# arguments, those are directly added to the underlying namespace.
#
# SimpleNamespace may be useful as a replacement for class NS: pass.
# However, for a structured record type use namedtuple() instead.

# This is useful for testing, where one might want to monkeypatch a
# more minimal object than the original, to avoid unexpected
# side-effects

try:
    from types import SimpleNamespace
except ImportError:
    class SimpleNamespace:
        """An empty, modifiable class for compatibility with Python < 3.3."""

        def __init__(self, **kwargs):
            """Initialize."""
            self.__dict__.update(kwargs)

        def __repr__(self):  # pragma: no cover
            """Represent."""
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format(type(self).__name__, ", ".join(items))


def qualify_symbol(symname, ns):
    """Build a fully-qualified symbol name from a name & part of namespace."""

    if ns[0] == '.':
        ns = 'py2neo' + ns

    if ns[-1] == '.':
        ns += symname

    return tuple(ns.rsplit('.', 1))


def import_symbol(modname, symname):
    """Load the object by its fully-qualified name."""

    mod = importlib.import_module(modname)
    return getattr(mod, symname)
