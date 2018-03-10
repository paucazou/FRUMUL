#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""Indexer leaned against FRUMUL"""
import argparse
import readline
from frumul import lexer, parser, semizer, symbols, tosource

def finput(prompt='>>> ', text=''):
    text = str(text)
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt + '\n')
    readline.set_pre_input_hook()
    return result

def checkName(value: str) -> bool:
    """Checks wether value starts and
    ends with ___ or not"""
    try:
        return value[:3] == '___' == value[-3:] and len(value) > 6
    except (IndexError, TypeError):
        return False

def setName(value: str):
    """Suppress initial & trailing ___"""
    return value[3:][:-3]

def _createItem(value: str,children: symbols.ChildrenSymbols,short_name=None,set_null_value=False):
    """Create an item inside the file
    if short_name is set, create the short name provided
    if set_null_value is True, give a "" value to symbol created"""
    name = symbols.Name(long=value,short=short_name)
    symbol = symbols.Symbol(tag_nb=1)
    symbol.name = name
    if set_null_value:
        symbol.setValue('',"every")
    children.updateChild(symbol,declaration=False) # TODO verify 

def _createColumn(value: str, children: symbols.ChildrenSymbols):
    """Create a column inside the file"""
    short_name = value[0]
    value = "___{}___".format(value)
    _createItem(value,children,short_name=short_name,set_null_value=True)



def _manage(args: argparse.Namespace):
    """Manage a project"""
    if args.start:
	#TODO vérifier qu'aucun projet n'existe déjà sous ce nom
        fake_symbol = symbols.Symbol(temp_name="FAKE")
        fake_symbol.children = symbols.ChildrenSymbols()
        _createItem("___files",fake_symbol.children,set_null_value=True) # files name has no trailing ___ in order to not let the user touch it
    elif args.update:
        with open(args.PROJECT) as f:
            content = f.read()
        tokens = lexer.Lexer(content,args.PROJECT)() 
        ast = parser.Parser(tokens)(header=True)
        fake_symbol = semizer.Semizer(ast)()
    else:
        raise ValueError("No command was given\n")

    # setting columns
    result = None
    exit_value = "_"*3 + "exit" + "_"*3
    while result != exit_value:
        print("Columns already set:")
        columns = [setName(child.name.long) for child in fake_symbol.children if checkName(child.name.long)] 
        shorts = [name[0] for name in columns]
        print("\n".join(columns))
        result = finput("1. Type a new name to create it. The first letter will be used to give its short name.\n2. Type an already set name to update it: '-' delete it;'*' modify name;\n3. type {} to exit.".format(exit_value)) # TODO rewrite text
        if result == exit_value:
            break
        if result not in columns:
            if result[0] in shorts:
                print("Short name already taken")
            else:
                _createColumn(result,fake_symbol.children)
        elif result[:-2] in columns:
            name = "___{}___".format(result[:-2])
            if result[-1] == "-":
                del(fake_symbol.children[name])
            elif result[-1] == '*':
                pass # TODO modify name
            else:
                print("Sign unrecognized")

    if finput("Save ?(y/n)","y") == "y":
        with open(args.PROJECT,'w') as f:
            content = tosource.HeaderSourcer(fake_symbol)()
            f.write(content)





def _files(args: argparse.Namespace):
    """Manage the files inside a project"""
    pass

def _items(args: argparse.Namespace):
    """Manage the items inside a project"""
    pass

def _cmdline() -> argparse.Namespace:
    """Manages the command-line arguments"""
    parser = argparse.ArgumentParser(description="FRUMUL indexer")
    parser.add_argument("PROJECT",help="Path of the project file")
    subparsers = parser.add_subparsers(help="Commands")

    project_management = subparsers.add_parser("manage",help="Project management")
    project_management.set_defaults(func=_manage)
    pm_options = project_management.add_mutually_exclusive_group()
    pm_options.add_argument("--start",action="store_true",help="Start a new project")
    pm_options.add_argument("--update",action="store_true",help="Update a project")

    files_management = subparsers.add_parser("files",help="Manage files inside a project")
    files_management.set_defaults(func=_files)
    fm_options = files_management.add_mutually_exclusive_group()
    fm_options.add_argument("--add",nargs="?",default=None,help="Add a new file to a project") 
    fm_options.add_argument("--remove",nargs="?",default=None,help="Remove a file from a project")

    items_management = subparsers.add_parser("items",help="Manage items inside a project")
    items_management.set_defaults(func=_items)
    im_options = items_management.add_mutually_exclusive_group()
    im_options.add_argument("--add",action="store_true",help="Add new entries into a project")
    im_options.add_argument("--change",action="store_true",help="Change an item inside a project")
    im_options.add_argument("--remove",action="store_true",help="Remove an item from a project")
    
    return parser.parse_args()

def _start(path: str):
    """Start a new project"""
    pass

def _update(path: str):
    """Update an already existant project"""
    pass

def _add(path: str):
    """Add some new values to an existing project"""
    pass

def _add_file(project_path: str,new_file_path: str):
    """Add a file to a project.
    Links the file itself to the project"""
    pass


def main():
    """Main function"""
    args = _cmdline()
    args.func(args)

if __name__ == '__main__':
    main()
