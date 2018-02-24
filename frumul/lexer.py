#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""This is the lexer part of the interpreter.
It splits the string into tokens"""

import collections
import re
from .keywords import *

shared_regex = {
        WHITESPACE:re.compile(r'\s'),
        COMMENT:re.compile(r'//\*.*?\*//',re.DOTALL),
        }

header_regex = collections.OrderedDict([
    (WHITESPACE,re.compile(r'\s')),
    (HEADER,re.compile('___header___',re.IGNORECASE)),
    (FULLTEXT,re.compile('___text___(.*$)',re.DOTALL+re.IGNORECASE)), 
    (ASSIGN,re.compile(r':')),
    (MARK,re.compile(r'mark',re.IGNORECASE)),
    (FILE,re.compile(r'file',re.IGNORECASE)),
    (LANG,re.compile(r'lang',re.IGNORECASE)),
    (COMMENT,re.compile(r'//\*.*?\*//',re.DOTALL)),
    (LPAREN,re.compile(r'\(')), # to use a parenthesis as an ID ? Maybe an escape sign before ?
    (RPAREN,re.compile(r'\)')),
    (VALUE,re.compile(r'"(\\"|[^"])*"')),
    (ID,re.compile(r'[^ ]+(?= *:)')), # replace & TEST [^ ] by \S (not \s)
        ])
value_content = re.compile(r'(?<=").*(?=")')

definition_regex = collections.OrderedDict([
    (WHITESPACE,shared_regex[WHITESPACE]),
    (LONGNAME,re.compile(r'\((?P<content>\S+?)\)')), #TODO escape ) ->> \)
    (SHORTNAME,re.compile(r'\S')),
    ])

Token = collections.namedtuple('Token',('type','value','path','line','column'))

class Lexer:
    """Split stream into a list of tokens"""

    def __init__(self,stream: str,path: str):
        """Set the lexer"""
        self.stream = stream
        self.path = path
    
    def _error(self,word: str,line: int,column: int):
        """Raises error for invalid word"""
        raise NameError("Invalid token: {}.\nFile: {}\nLine: {}\nColumn: {}".format(
            word,self.path,line,column))

    def __call__(self) -> list:
        """get tokens of the header.
        Set self.tokens and return it.""" #http://jayconrod.com/posts/37/a-simple-interpreter-from-scratch-in-python-part-1
        self._pos = start_line = 0
        line = 1 
        self.tokens = []
        while self._pos < len(self.stream): 
            #self._skip_whitespace()
            for type,reg in header_regex.items():
                match = reg.match(self.stream,self._pos)
                if match:
                    break
            else:
                self._error(self.stream[self._pos:].split('\n')[0],line,self._pos + 1 - start_line)

            column = match.start(0) + 1 - start_line 
            if type == VALUE:
                value = value_content.search(match.group(0)).group(0)
            elif type == FULLTEXT:
                value = match.group(1)
            else:
                value = match.group(0)
            token = Token(type,value,self.path,line, column)
            if '\n' in token.value:
                line += token.value.count('\n') 
                start_line = match.end(0)
            if token.type not in ('COMMENT','WHITESPACE'):
                self.tokens.append(token)
            self._pos = match.end(0)


        self.tokens.append(Token(EOF,EOF,self.path,line,column))

        return self.tokens

class TextLexer(Lexer):
    """Tokenize the text"""

    def __init__(self,AST,constants):
        """AST: Abstract Syntax Tree (Header + Text as a FullText token)
        constants: return value of semizer"""
        self.stream = AST.fulltext.value
        self.fulltext = AST.fulltext
        self.constants = constants
        self.path = AST.fulltext.path

        tags = '|'.join([tag.name.long for tag in constants])
        regex = (
        (TAG, "(?P<tag>{})(?P<children>\S*)\s".format(tags)),
        (COMMENT,shared_regex[COMMENT].pattern))
        self.regex = "|".join("(?P<%s>%s)" % pair for pair in regex)


        
    def __call__(self) -> list: # TODO: lines, columns
        """set tokens and return it"""
        self._pos = 0
        self.tokens = []
        column = self.fulltext.column 
        line = self.fulltext.line
        for elt in re.finditer(self.regex,self.stream):
            temp_tokens = []
            type = elt.lastgroup
            
            if elt.start(0) != self._pos:
                temp_tokens.append( Token(SENTENCE,self.stream[self._pos:elt.start(0)],self.path,column,line) )
            if type == TAG:
                tag,children = elt.group('tag'), elt.group('children')
                if children:
                    temp_tokens.append( Token(OTAG,tag,self.path,column,line) )
                    temp_tokens.append( Token(CHILDREN,children,self.path,column,line) )
                else:
                    temp_tokens.append( Token(TAG,tag,self.path,column,line) )
                self.tokens.extend(temp_tokens)
            self._pos = elt.end(0)
        else:
            if self._pos + 1 < len(self.stream):
                self.tokens.append( Token(SENTENCE,self.stream[self._pos:],self.path,column,line) )
            self.tokens.append( Token(EOF,EOF,self.path,column,line) )

        return self.tokens


class DefinitionLexer(Lexer):
    """A class which handles definition values"""

    def __init__(self,token: Token):
        """inits the lexer"""
        super().__init__(token.value,token.path)
        self.column = token.column
        self.line = token.line

    def __call__(self) -> list:
        """Tokenize self.stream"""
        pos = 0
        self.tokens = []
        while pos < len(self.stream):
            for type, reg in definition_regex.items():
                match = reg.match(self.stream,pos)
                if match:
                    break
            else:
                self._error(self.stream,line,self.column + pos + 1)
            
            pos = match.end(0)

            if type != WHITESPACE:
                value = match.group('content') if type == LONGNAME else match.group(0)
                token = Token(type,value,self.path,self.line,self.column+pos+1)
                self.tokens.append(token)

        return self.tokens








