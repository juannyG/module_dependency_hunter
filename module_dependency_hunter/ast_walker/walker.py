#-*- coding: utf-8 -*-
"""
@see: https://gist.github.com/lrq3000/6175522
Copyright (C) 2001-2007 Martin Blais. All Rights Reserved
Copyright (C) 2010 Bear http://code-bear.com/bearlog/
Copyright (C) 2013 lrq3000

Excerpt from SnakeFood to recursively list all imports of modules using AST parsing
"""

import compiler
from compiler.ast import Discard, Const
from compiler.visitor import ASTVisitor

__all__ = ['parse_python_source']


class ImportVisitor(object):
    """Class to "visit" imports"""
    def __init__(self):
        self.modules = []
        self.recent = []

    def visitImport(self, node):
        self.accept_imports()
        self.recent.extend((x[0], None, x[1] or x[0]) for x in node.names)

    def visitFrom(self, node):
        self.accept_imports()
        modname = node.modname
        if modname == '__future__':
            return # Ignore these.
        for name, as_ in node.names:
            if name == '*':
                # We really don't know...
                mod = (modname, None, None)
            else:
                mod = (modname, name, as_ or name)
            self.recent.append(mod)

    def default(self, _):
        """Needed for compiler.walk"""
        self.accept_imports()

    def accept_imports(self):
        """accept imports"""
        self.modules.extend((m, r, l)
                            for (m, r, l) in self.recent)
        self.recent = []

    def finalize(self):
        """finalize"""
        self.accept_imports()
        return self.modules


class ImportWalker(ASTVisitor):
    """Walker for imports"""
    def __init__(self, visitor):
        ASTVisitor.__init__(self)
        self._visitor = visitor

    def default(self, node, *args):
        self._visitor.default(node)
        ASTVisitor.default(self, node, *args)


def parse_python_source(path):
    """Wrapper for walking import tree"""
    contents = open(path, 'rU').read()
    ast = compiler.parse(contents)
    vis = ImportVisitor()

    compiler.walk(ast, vis, ImportWalker(vis))
    return vis.finalize()
