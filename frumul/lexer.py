#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""This is the lexer part of the interpreter.
It splits the string into tokens"""

import collections
import re
from keywords import *


header_regex = collections.OrderedDict([
    (HEADER,re.compile('___header___')),
    (FULLTEXT,re.compile('___text___.*$',re.DOTALL)), 
    (ASSIGN,re.compile(r':')),
    (ELLP,re.compile(r'\n\(')),
    (ELRP,re.compile(r'\)\n')),
    (EOL,re.compile(r'\n')),
    #(LPAREN,re.compile(r'\(')),
    #(RPAREN,re.compile(r'\)')),
    (MARK,re.compile(r'mark')),
    (FILE,re.compile(r'file')),
    (LANG,re.compile(r'lang')),
    ('COMMENT',re.compile("//.*\n")),
    (VALUE,re.compile(r'"(\\"|[^"])*"')),
    (ID,re.compile(r'[^ ]+(?= *:)')),
        ])

Token = collections.namedtuple('Token',('type','value','path','line','column'))

class Lexer:
    """Split stream into a list of tokens"""

    def __init__(self,stream: str,path: str) -> list:
        """Set the lexer and return the list of tokens"""
        self.stream = stream
        self.path = path
        self.tokenizeHeader()
    
    def _error(self,word: str,line: int,column: int):
        """Raises error for invalid word"""
        raise NameError("Invalid token: {}.\nFile: {}\nLine: {}\nColumn: {}".format(
            word,self.path,line,column))

    def _skip_whitespace(self):
        """Ignore whitespace, except EOL"""
        while self._pos < len(self.stream) and self.stream[self._pos].isspace() and self.stream[self._pos] != '\n':
            self._pos += 1

    def tokenizeHeader(self) -> list:
        """get tokens of the header.
        Set self.tokensHeader and return it.""" #http://jayconrod.com/posts/37/a-simple-interpreter-from-scratch-in-python-part-1
        self._pos = start_line = 0
        line = 1 
        self.tokensHeader = []
        while self._pos < len(self.stream): 
            self._skip_whitespace()
            for type,reg in header_regex.items():
                match = reg.match(self.stream,self._pos)
                if match:
                    break
            else:
                self._error(self.stream[self._pos:].split('\n')[0],line,self._pos + 1 - start_line)

            column = match.start(0) + 1 - start_line 
            token = Token(type,match.group(0),self.path,line, column)
            if token.type == 'COMMENT':
                token = Token(EOL,'\n',self.path,line,column)
            elif '\n' in token.value:
                line += 1
                start_line = match.end(0)
            self.tokensHeader.append(token)
            self._pos = match.end(0)


        self.textStream = self.tokensHeader[-1].value
        self.tokensHeader.append(Token(EOF,EOF,self.path,line,column))

        return self.tokensHeader

    def tokenizeText(self,ids) -> list:
        """set tokensText and return it"""
        self._pos = 0
        column = 1
        line = self.textStream.line
        self.tokensText = []
        self.ids = ids
        while self._pos < len(self.textStream):
            for type, reg in text_regex.items():
                match = reg.match(self.textStream,self._pos)
                if match:
                    token = Token(type,match.group(0))
                    break
            if not match:
                self._error(self.textStream[self._pos:])
            else:
                self.tokensText.append(token)
                self._pos = match.end(0)

        return self.tokensText



