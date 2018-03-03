#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""Define exceptions of FRUMUL"""
import os
import sys

# redefining excepthook in order to free user from useless python messages
def excepthook(type,value,traceback):
    msg = type.__name__ + ": " + str(value)
    sys.stderr.write(msg)


if not os.environ.get('FRUMULTEST',False) : # export FRUMULTEST=0 // for tests
    sys.excepthook = excepthook # use it only with the user
else:
    print("Developement traceback activated.")

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

        
# header errors
class HeaderError(_ExceptionBase):
    """Exception raised when an error
    occurs in a header"""
    pass

class InconsistentTagNumber(HeaderError):
    """Raise this error if a symbol
    is updated with a non equal tag number
    or if the symbol has a number of placeholders
    unequal to tag number"""
    pass

class NameConflict(HeaderError):
    """Raise this error when a symbol matches
    with two or more other symbols,
    or when updating a symbol,
    long & short names (if set) don't match"""
    pass

# text errors
class TextError(_ExceptionBase):
    """Exception raised when an error
    occurs in a text"""
    pass

# errors raised when frumul does not know
# if the error is in the header or in the text.

class UnavailableLanguage(TextError,HeaderError):
    """Raise this error when a value is not available
    for the requested language"""
    pass
