#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
###############################################################################
#  AST visualizer - generates a DOT file for Graphviz.                        #
#                                                                             #
#  To generate an image from the DOT file run $ dot -Tpng -o ast.png ast.dot  #
#                                                                             #
###############################################################################
import argparse
import textwrap

import frumul

class GenericNode:
    def __init__(self,node):
        self._originalClassName = type(node).__name__
        if node is None:
            self.value = None
            return
        for k,v in zip(node._fields,node.__getnewargs__()):
            if k in self.__dict__:
                raise NameError("{} already present".format(k))
            setattr(self,k,v)


class ASTVisualizer(frumul.walker.NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.ncount = 1
        self.dot_header = [textwrap.dedent("""\
        digraph astgraph {
          node [shape=circle, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]

        """)]
        self.dot_body = []
        self.dot_footer = ['}']

    def visit(self,node):
        """main node visitor"""
        node = GenericNode(node)
        method_name = 'visit_' + node._originalClassName
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)
        return node

    def addNode(self,label,node):
        s = '  node{} [label="{}"]\n'.format(self.ncount,label)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_NoneType(self,node):
        self.addNode('None',node)


    def visitChild(self,node,child):
        if not isinstance(child,GenericNode):
            print(child)
        s = '  node{} -> node{}\n'.format(node._num, child._num)
        self.dot_body.append(s)


    def visit_Document(self,node):
        self.addNode('Document',node)
        header = self.visit(node.header)
        fulltext = self.visit(node.fulltext)

        for child in (header,fulltext):
            self.visitChild(node,child)

    def visit_FullText(self,node):
        self.addNode('FullText',node)

    def visit_Header(self,node):
        self.addNode('Header',node)
        for child in node.statement_list:
            child = self.visit(child)
            self.visitChild(node,child)

    def visit_Statement(self,node):
        self.addNode('Statement',node)
        constant = self.visit(node.constant)
        options = self.visit(node.options)
        definition = self.visit(node.definition)
        for child in (constant,options,definition):
            self.visitChild(node,child)

    def visit_Options(self,node):
        self.addNode('Options',node)
        lang = self.visit(node.lang)
        mark = self.visit(node.mark)
        for child in (lang,mark):
            self.visitChild(node,child)

    def visit_Definition(self,node):
        value = self.visit(node.value)
        #self.addNode(value.value,value)
        node._num = value._num

        for stmt in node.statement_list:
            stmt = self.visit(stmt)
            self.visitChild(value,stmt)

    def visit_Token(self,node):
        self.addNode(node.value,node)

    def visit_Text(self,node):
        self.addNode('Text',node)
        for child in node.children:
            child = self.visit(child)
            self.visitChild(node,child)

    def visit_Sentence(self,node):
        self.addNode(node.token.value,node)
    
    def visit_Tag(self,node):
        self.addNode(node.symbol,node)
        if node.text.children:
            for child in node.text.children:
                child = self.visit(child)
                self.visitChild(node,child)

    def gendot(self):
        tree = self.parser()
        self.visit(tree)
        return ''.join(self.dot_header + self.dot_body + self.dot_footer)


def main():
    argparser = argparse.ArgumentParser(
        description='Generate an AST DOT file.'
    )
    argparser.add_argument(
        'fname',
        help='Source file'
    )
    argparser.add_argument('--text',help="Return Text AST, not Header",action='store_true')
    args = argparser.parse_args()
    with open(args.fname) as fname:
        text = fname.read()

    if args.text:
        tokens = frumul.lexer.Lexer(text,args.fname)()
        AST = frumul.parser.Parser(tokens)()
        sem = frumul.semizer.Semizer(AST)()
        ttokens = frumul.lexer.TextLexer(AST,sem)()
        parser = frumul.parser.TextParser(ttokens,sem)
    else:
        parser = frumul.parser.Parser(frumul.lexer.Lexer(text,args.fname)())
    viz = ASTVisualizer(parser)
    content = viz.gendot()
    print(content) # there can be a problem if label contain " inside


if __name__ == '__main__':
    main()




