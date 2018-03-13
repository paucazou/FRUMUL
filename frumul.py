#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""Main entry to use FRUMUL"""

import argparse
import os
import sys
from frumul import lexer, parser, semizer, transpiler

dir = os.path.dirname(os.path.abspath(__file__)) + '/'

# env variables
os.environ['STDLIB'] = dir + 'frumul/headers/'

def checkHeader(name: str) -> bool:
    """Checks if name is in standard library
    if name has no '.h' suffix."""
    if name[-2:] == '.h':
        return True
    return os.path.isfile(os.environ['STDLIB'] + name + '.h')




def transpile(input,output,lang: str):
    """Transpile from input to output for requested lang"""
    content = input.read()
    path = os.path.abspath(input.name)
    # header
    tokens = lexer.Lexer(content,path)()
    AST = parser.Parser(tokens)()
    constants = semizer.Semizer(AST)()
    # text
    tokens = lexer.TextLexer(AST,constants)()
    AST = parser.TextParser(tokens,constants)()
    new_text = transpiler.Transpiler(AST,lang)()
    
    #write output
    output.write(new_text)

    # close files
    input.close()
    output.close()
    

def newFile(output,headers):
    """Create a new file with specific headers"""
    assignments = ''
    for header in headers: 
        if not checkHeader(header[0]):
            raise NameError("No header of this name in standard lib: {}".format(header[0])) # TODO # delete file if error
        assignments += ': file "'.join(header[::-1]) + '"\n'
    content = '___header___\n'+ assignments + '___text___\n'

    output.write(content)
    output.close()
    # rename file
    if output.name[-3:] != '.uu' and not os.path.isfile(output.name + '.uu'):
        os.rename(output.name,output.name+'.uu')


def main():
    """Main function, called if this module is used
    directly"""
    parser = argparse.ArgumentParser(description="FRUMUL: Fast and Readable Universal MarkUp Language")

    transpiler = parser.add_argument_group('Transpiler','Transpile options')
    transpiler.add_argument('-i','--input',type=argparse.FileType('r'),help="Input FRUMUL file")
    transpiler.add_argument('-o','--output',type=argparse.FileType('w'),default=sys.stdout,help="Output file")
    lang_required = '--input' in sys.argv or '-i' in sys.argv
    transpiler.add_argument('-l','--lang',help="Language output",required=lang_required)


    newfile = parser.add_argument_group('New file','Create a new Frumul file')
    newfile.add_argument('--new-file',type=argparse.FileType('w'),default=sys.stdout,
            help="Create a new FRUMUL file with given path. Use it with header")
    newfile.add_argument('--header',default=[],action='append',nargs=2,
            help="Header + opening tag in new file\nUse a path for your own header, a name for standard header\nExample: --header json jj")

    args = parser.parse_args()

    if args.input:
        transpile(args.input,args.output,args.lang)
    else:
        newFile(args.new_file,args.header)


if __name__ == '__main__':
    main()
