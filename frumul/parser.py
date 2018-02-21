#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""This module manages the parser part of the interpreter"""

import collections
from . import lexer

from .keywords import *

# AST nodes

Document = collections.namedtuple('Document',('header','fulltext'))
FullText = collections.namedtuple('FullText',('fulltext',))
Header = collections.namedtuple('Header',('statement_list'))
Statement = collections.namedtuple('Statement',('constant','options','definition'))
Constant = collections.namedtuple('Constant',('id')) # USELESS ?
Options = collections.namedtuple('Options',('lang','mark'))
Definition = collections.namedtuple('Definition',('value','statement_list'))
class NoOp: pass
# parser

class Parser:
    """Parses the tokens and return an AST"""
    def __init__(self,tokens: list):
        """Inits the instance"""
        self.tokens = tokens

    def _error(self,type):
        """Raises error"""
        raise ValueError('Invalid syntax. Token: {}\nType waited: {}'.format(self._current_token,type))
        raise ValueError('Invalid syntax.\nFile: {}\nLine: {}\nColumn: {}'.format(
            self._current_token.path,self._current_token.line,self._current_token.column)) # TODO add the word itself

    def _eat(self,type):
        """Compare type with current token type"""
        if self._current_token.type == type:
            #print(self._current_token)
            self._advance()
        else:
            self._error(type)

    def _advance(self):
        """Set self._current_token"""
        self._pos += 1
        if self._pos < len(self.tokens):
            self._current_token = self.tokens[self._pos]
        else:
            self._current_token = None

    def parse(self):
        """Parse the tokens"""
        self._pos = -1
        self._advance()
        node = self._document()
        self._pos = -1
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
        self._eat(HEADER)
        return Header(self._statement_list())

    def _statement_list(self):
        """statement_list : empty | statement*"""
        statement_list = []
        while self._current_token.type == 'ID':
            statement_list.append(self._statement())
        return tuple(statement_list)

    def _statement(self):
        """statement : constant ':' definition"""
        constant = self._current_token
        self._eat(ID)
        self._eat(ASSIGN)
        options, definition = self._definition()
        return Statement(constant,options,definition)

    def _options(self):
        """options ::= ( language mark? | mark language? )?"""
        if self._current_token.type == LANG:
            lang = self._language()
            mark = self._mark()
        elif self._current_token.type == MARK:
            mark = self._mark()
            lang = self._language()
        else:
            lang = mark = None
        return Options(lang,mark)


    def _language(self):
        """'lang' value"""
        if self._current_token.type == LANG:
            self._eat(LANG)
            result = self._current_token
            self._eat(VALUE)
        else:
            result = None
        return result

    def _definition(self):
        """options (file_assignment | value [LPAREN statement_list RPAREN] )"""
        if self._current_token.type == FILE:
            result = self._file_assignment()
        else:
            options = self._options()
            value = self._current_token
            self._eat(VALUE)
            if self._current_token.type != LPAREN:
                statement_list = tuple()
            else:
                self._eat(LPAREN)
                statement_list = self._statement_list() 
                self._eat(RPAREN)
            result = options, Definition(value,statement_list)

        return result

    def _file_assignment(self):
        """file_assignment : 'file' value EOF"""
        self._eat(FILE)
        path = self._current_token # there will be probably a problem here -> use normpath or something like that
        self._eat(VALUE)

        with open(path.value) as f:
            headerfile = f.read()

        tokens = lexer.Lexer(headerfile,path.value).tokensHeader
        parser = Parser(tokens)
        parser._pos = -1
        parser._advance()
        definition = parser._definition()
        parser._eat(EOF)
        return definition

    def _mark(self):
        """'mark' value"""
        if self._current_token.type != MARK:
            result = None
        else:
            self._eat(MARK)
            result = self._current_token
            self._eat(VALUE)
        return result









    

