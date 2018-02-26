#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""This module can be used to test the interpreter
at different steps of the job"""

import os
import sys
sys.path.append('..')
import frumul

afile = "afile.uu"
os.environ['STDLIB'] = os.path.abspath('../frumul/headers') + '/'

def lexer(content,filename=afile):
    """return the results of lexer.Lexer()"""
    l=frumul.lexer.Lexer(content,filename)
    return l()

def parser(content,filename=afile):
    """return the results of parser.Parser()"""
    tokens = lexer(content,filename)
    p=frumul.parser.Parser(tokens)
    return p()

def semizer(content,filename=afile):
    """return the result of the semizer"""
    ast = parser(content,filename)
    sem = frumul.semizer.Semizer(ast)
    return sem()

def text_lexer(content,filename=afile):
    """return the result of lexer.TextLexer"""
    ast = parser(content,filename)
    sem = semizer(content,filename)
    tl = frumul.lexer.TextLexer(ast,sem)
    return tl()

def text_parser(content,filename=afile):
    """return the result of parser.TextParser"""
    sem = semizer(content,filename)
    tokens = text_lexer(content,filename)
    tp = frumul.parser.TextParser(tokens,sem)
    return tp()

def transpiler(content,lang,filename=afile):
    """return the result of transpiler.Transpiler"""
    ast = text_parser(content,filename)
    return frumul.transpiler.Transpiler(ast,lang)
