#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
# WARNING rien n'est prêt pour la mise à jour des symbols s'ils sont définis pour un autre langage, par exemple
"""Semantic analysis"""
from . import symbols, walker

class Semizer(walker.NodeVisitor):
    """Defines constants"""
    def __init__(self,node):
        """node is a Document node"""
        self.node = node

    def __call__(self):
        """Visit self.node
        Set self.constants
        return self.constants"""
        return self.visit(self.node)

    def visit_Document(self,node):
        """Visit Document"""
        return self.visit(node.header)

    def visit_Header(self,node):
        """Visit Document"""
        self.constants = symbols.ChildrenSymbols()
        for stmt in node.statement_list:
            self.constants.updateChild(self.visit(stmt),declaration=False) 
        for constant in self.constants:
            if constant.hasValue() and constant.hasChildren():
                raise ValueError('''An Opening tag canno't have a value and a child: {}'''.format(constant)) # if a constant has both, it is impossible to parse the text without ambiguity
        return self.constants

    def visit_Statement(self,node):
        """Visit Statement"""
        lang, tag_nb = self.visit(node.options)
        constant = symbols.Symbol(temp_name=node.constant.value,tag_nb=tag_nb)
        value, children = self.visit(node.definition)
        if children:
            children.parent = constant
            if lang:
                children.updateValues(lang) 
            constant.children = children
            if constant.children.childrenUndefined: 
                raise ValueError("Children declared, but not defined: {}".format(constant.children.childrenUndefined))
        elif value is not None: 
            constant.setValue(value,lang)

        return constant
        
    def visit_Options(self,node):
        """Visit Options"""
        lang = node.lang.value if node.lang else None
        try:
            mark = int(node.mark.value) if node.mark else None 
        except ValueError:
            raise ValueError("Invalid integer: {}".format(node.mark))
        return lang, mark

    def visit_Definition(self,node):
        """Visit Definition"""
        value = children = None
        if not node.statement_list:
            value = node.value.value
        else:
            children = symbols.ChildrenSymbols()
            children.declare(node.value)
            for stmt in node.statement_list:
                children.updateChild(self.visit(stmt)) 

        return value, children 




