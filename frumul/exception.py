#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""Define exceptions of FRUMUL"""

class _ExceptionBase(Exception):
    """Base class of every other exception"""
    def __init__(self,token,message:str):
        """Set the exception.
        token is a lexer.Token class"""
        super().__init__(token,message)
        self.token = token
        self.message = message
        self.file = token.file

        self.lineno = token.line + 1 # +1: to cause the line/column nb to start at 1, not 0
        self.columnno = token.column + 1
        print(self.file.content.split('\n'))
        self.line = self.file.content.split('\n')[token.line]


    def __str__(self):
        delimiter = '\n' + "="*len(self.line) + '\n'

        s = self.message + '\n'
        s += "FILE: '{}' LINE: {} COLUMN: {}".format(
                self.file.path,
                self.lineno,
                self.columnno)
        s += delimiter
        s += self.line + '\n'
        s += ' '*(self.columnno -1) + '^'

        return s

        

class HeaderError(_ExceptionBase):
    """Exception raised when an error
    occurs in a header"""
    pass

class TextError(_ExceptionBase):
    """Exception raised when an error
    occurs in a text"""
    pass
