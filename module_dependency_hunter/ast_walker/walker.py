#-*- coding: utf-8 -*-
"""
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
        self.recent.extend((x[0], None, x[1] or x[0], node.lineno, 0)
                           for x in node.names)

    def visitFrom(self, node):
        self.accept_imports()
        modname = node.modname
        if modname == '__future__':
            return # Ignore these.
        for name, as_ in node.names:
            if name == '*':
                # We really don't know...
                mod = (modname, None, None, node.lineno, node.level)
            else:
                mod = (modname, name, as_ or name, node.lineno, node.level)
            self.recent.append(mod)

    def default(self, node):
        """Needed for compiler.walk"""
        pragma = None
        if self.recent:
            if isinstance(node, Discard):
                children = node.getChildren()
                if len(children) == 1 and isinstance(children[0], Const):
                    const_node = children[0]
                    pragma = const_node.value
        self.accept_imports(pragma)

    def accept_imports(self, pragma=None):
        """accept imports"""
        self.modules.extend((m, r, l, n, lvl, pragma)
                            for (m, r, l, n, lvl) in self.recent)
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
