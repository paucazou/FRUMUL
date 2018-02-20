#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""Implement the node visitor"""

class NodeVisitor:
    """Skeleton of any node visitor"""
    def visit(self,node):
        """Calls specific node visitor from the name
        of the class"""
        method_name = 'visit_{}'.format(type(node).__name__)
        visitor = getattr(self, method_name,self.generic_visit)
        return visitor(node)

    def generic_visit(self,node):
        """Raise an error"""
        raise RuntimeError("This type of node canno't be visited: {}. Please implement it.".format(
            type(node).__name__))
