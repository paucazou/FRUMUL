#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""This module describes the transpiler"""
import collections
import re
from . import walker

patterns_and_sub = (
    ('EOL','\n'),
    ('TAB','\t'),
    ('\\\\',''), # for \" and \{ for example
    )

change_sequences = (
        (re.compile(r'(?<!\\){}'.format(key)),value)
        for key, value in patterns_and_sub )
change_sequences = collections.OrderedDict(change_sequences)

sentence_breaker = re.compile(r'(?<!\\){}')


class Transpiler(walker.NodeVisitor):
    """Takes an AST and changes it into another
    source code"""

    def __init__(self,ast,lang: str):
        """Inits the instance. 
        AST is a Text instance
        lang defines the output language"""
        self.ast = ast
        self.lang = lang # TODO create error if lang doesn't exist

    def __call__(self):
        """Launches the transpilation"""
        return self.visit(self.ast)

    def _transformSentence(self,sentence: str) -> str:
        """Takes a string and modifies it.
        Deletes escapes characters. Transform
        words like EOL, TAB, etc."""
        for reg, sub in change_sequences.items():
            sentence = reg.sub(sub,sentence)

        return sentence

    def visit_Text(self,node) -> list:
        """Visit Text node"""
        string_return = ''
        for child in node.children:
            string_return += self.visit(child)

        return string_return

    def visit_Sentence(self,node):
        """Visit Sentence node"""
        return node.token.value

    def visit_Tag(self,node): 
        """Visit tag"""
        sentence = node.symbol.getValue(self.lang)
        broken_sentence = sentence_breaker.split(sentence)
        broken_sentence = ( self._transformSentence(sentence) for sentence in broken_sentence )
        string_return = next(broken_sentence)

        #assert len(broken_sentence) + 1 == len(node.children) # develop !!
        for text, sentence in zip(node.text,broken_sentence):
            string_return += self.visit(text)
            string_return += sentence

        return string_return







