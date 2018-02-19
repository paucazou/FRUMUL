#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""This module manages the parser part of the interpreter"""

import collections
import keywords
import lexer

# AST nodes

Document = collections.namedtuple('Document',('header','fulltext'))
FullText = collections.namedtuple('FullText',('fulltext',))
Header = collections.namedtuple('Header',('statement_list'))
Statement = collections.namedtuple('Statement',('constant','assignment'))
Constant = collections.namedtuple('Constant',('id')) # USELESS ?
Assignment = collections.namedtuple('Assignment',('lang','definition'))
Definition = collections.namedtuple('Definition',('mark','value','statement_list'))
class NoOp: pass
# parser

class Parser:
    """Parses the tokens and return an AST"""
    def __init__(self,tokens: list):
        """Inits the instance"""
        self.tokens = tokens
        self._pos = -1
        self.parse()

    def _error(self):
        """Raises error"""
        raise ValueError('Invalid syntax. Line: {}\nColumn: {}'.format(
            self._current_token.line,self._current_token.column)) # TODO add the word itself

    def _eat(self,type):
        """Compare type with current token type"""
        if self._current_token.type == type:
            self._advance()
        else:
            self._error()

    def _eatnskip_eol(self,type):
        """Skip EOL token if necessary"""
        while self._current_token.type in (EOL,type):
            self._advance()

    def _advance(self):
        """Set self._current_token"""
        self._pos += 1
        if self._pos < len(self.tokens):
            self._current_token = self.tokens[self._pos]
        else:
            self._current_token = None

    def parse(self):
        """Parse the tokens"""
        self._advance()
        node = self._document()
        return node

    def _document(self):
        """document : header fulltext"""
        header = self._header()
        fulltext = self._fulltext()
        self._eat(EOF)
        return Document(header,fulltext)

    def _fulltext(self):
        """return fulltext"""
        if self._current_token.type == 'FULLTEXT':
            node = FullText(self._current_token)
            self._eat(FULLTEXT)
        else:
            node = NoOp()
        return node

    def _header(self):
        """header : statement_list"""
        self._eatnskip_eol(HEADER)
        return self._statement_list()

    def _statement_list(self):
        """statement_list : empty | statement*"""
        statement_list = []
        while self._current_token.type == 'ID':
            statement_list.append(self._statement())
        return tuple(statement_list)

    def _statement(self):
        """statement : constant ':' assignment EOL"""
        constant = self._current_token
        self._eat(ID)
        self._eat(ASSIGN)
        assignment = self._assignment()
        self._eat(EOL)
        return Statement(constant,assignment)

    def _assignment(self):
        """assignment : [language] definition"""
        lang = self._language()
        definition = self._definition()
        return Assignment(lang,definition)

    def _language(self):
        """'lang' value"""
        if self._current_token.type == LANG:
            self._eat(LANG)
            result = self._current_token
            self._eat(VALUE)
        else:
            result = NoOp()
        return result

    def _definition(self):
        """(file_assignment | [mark] value [statement_list] EOL)"""
        if self._current_token.type == FILE:
            result = self._file_assignment()
        else:
            mark = self._mark()
            value = self._current_token
            self._eat(VALUE)
            statement_list = self._statement_list()
            self._eat(EOL)
            result = Definition(mark,value,statement_list)

        return result

    def _file_assignment(self):
        """file_assignment : 'file' value EOF"""
        self._eat(FILE)
        path = self._current_token # there will be probably a problem here -> use normpath or something like that
        self._eat(VALUE)
        self._eat(EOF)

        with open(path) as f:
            headerfile = f.read()

        tokens = lexer.Lexer(headerfile,path).tokensHeader
        parser = Parser(tokens)
        parser._advance()
        AST = parser._definition()
        return AST

    def _mark(self):
        """'mark' value"""
        self._eat(MARK)
        result = self._current_token
        self._eat(VALUE)
        return result









    

