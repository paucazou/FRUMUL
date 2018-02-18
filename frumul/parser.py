#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""This module manages the parser part of the interpreter"""

import collections
import keywords
import lexer

# AST nodes

Document = collections.namedtuple('Document',('header','fulltext'))
Header = collections.namedtuple('Header',('statement_list'))
Statement = collections.namedtuple('Statement',('constant','assignment'))
Constant = collections.namedtuple('Constant',('id'))
Assignment = collections.namedtuple('Assignment',('lang','assignment_value'))
Lang = collections.namedtuple('Lang',('name'))
Definition = collections.namedtuple('Definition',('mark','value'))
Translation = collections.namedtuple('Translation',('mark','value'))
class NoOp: pass
# parser


