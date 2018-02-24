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
        self.visit(self.node)
        return self.constants

    def visit_Document(self,node):
        """Visit Document"""
        self.visit(node.header)

    def visit_Header(self,node):
        """Visit Document"""
        self.constants = symbols.ChildrenSymbols()
        for stmt in node.statement_list:
            self.constants.updateChild(self.visit(stmt),declaration=False) # TODO vérifier qu'aucune valeur n'ait été donnée s'il y a des enfants.

    def visit_Statement(self,node):
        """Visit Statement"""
        lang, tag_nb = self.visit(node.options)
        constant = symbols.Symbol(temp_name=node.constant.value,tag_nb=tag_nb)
        value, children = self.visit(node.definition)
        if children:
            children.parent = constant
            if lang:
                children.updateValues(lang) # que fait-on si d'autres attributs sont déclarés plus tard sans lang ? -> erreur ?
            constant.children = children
        elif value:
            constant.setValue(value,lang)

        return constant
        
    def visit_Options(self,node):
        """Visit Options"""
        lang = node.lang.value if node.lang else None
        mark = int(node.mark.value) if node.mark else None # TODO raise error if not int
        return lang, mark

    def visit_Definition(self,node):
        """Visit Definition"""
        value = children = None
        if not node.statement_list:
            value = node.value.value
        else:
            children = symbols.ChildrenSymbols()
            for stmt in node.statement_list:
                children.declare(node.value)
                children.updateChild(self.visit(stmt)) # problème : les langues ne seront pas forcément définies à ce stade... puisqu'il n'y a pas de parent !

        return value, children 




