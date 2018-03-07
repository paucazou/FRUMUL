#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
# TODO give the possibility to collect lang/tag info at the parent level
"""A source to source compiler"""
from . import symbols, walker

class HeaderSourcer(walker.NodeVisitor):
    """Creates the source code of a header
    It does not create a full header since it can also
    create the source of a header file"""
    def __init__(self,abstract_header):
        """Inits the sourcer"""
        self.source = None
        if isinstance(abstract_header,symbols.Symbol) and abstract_header._temp_name == "FAKE":
            abstract_header = abstract_header.children
        self.abstract_header = abstract_header # a frumul.symbols.ChildrenSymbols/Symbol object

    def __call__(self) -> str:
        """Calls the sourcer and return the source code
        Set self.source"""
        self.source = self._create_source()
        return self.source

    def _create_source(self) -> str:
        """Takes the symbols and return the source code"""
        self.source = self.visit(self.abstract_header)
        return self.source

    def visit_ChildrenSymbols(self,children) -> str:
        """Manages the ChildrenSymbols object"""
        spart = '"' # returned string
        sort_key = lambda x:x.name.long if x.name.long else x.name.short
        # declaration
        for symbol in sorted(children,key=sort_key):
            if symbol.name.short:
                spart += symbol.name.short
            if symbol.name.long:
                spart += "({}) ".format(symbol.name.long)
        spart += '"\n('
        # definition
        for symbol in sorted(children,key=sort_key):
            spart += self.visit(symbol)
        spart += ")"
        return spart


    def visit_Symbol(self,symbol) -> str:
        """Manages the Symbol object"""
        spart = "" # returned string
        # get name
        name = symbol.name.long if symbol.name.long else symbol.name.short

        # printing values
        for lang in sorted(symbol.getLanguages()):
            spart += """{} : lang "{}" mark "{}" "{}"\n""".format(
                    name,lang,symbol.tag,symbol.getValue(lang)
                    )
        # printing children
        if symbol.hasChildren():
            spart += """{} : {}\n""".format(
                    name,
                    self.visit(symbol.children)
                    )

        return spart


