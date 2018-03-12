#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""Indexer leaned against FRUMUL"""
import argparse
import collections
import os
import pydoc
import readline
import shutil
import textwrap
from colorama import Fore, Style
from frumul import lexer, parser, semizer, symbols, tosource

inred = lambda x: Fore.RED + x + Style.RESET_ALL
ingreen = lambda x: Fore.GREEN + x + Style.RESET_ALL
inmagenta = lambda x: Fore.MAGENTA + x + Style.RESET_ALL

def finput(prompt='>>> ', text=''):
    text = str(text)
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt + '\n')
    readline.set_pre_input_hook()
    return result

def finputWrapper(prompt=">>>", text="",exval="") -> str:
    """Handle ctrl+D: exval is returned"""
    try:
        res=finput(prompt,text)
    except EOFError:
        res = exval
    return res

def checkName(value: str) -> bool:
    """Checks wether value starts and
    ends with ___ or not"""
    try:
        return value[:3] == '___' == value[-3:] and len(value) > 6
    except (IndexError, TypeError):
        return False

def itemsOnly(children: symbols.ChildrenSymbols) -> list:
    """Return a list of items, not special constants
    defined by the indexer"""
    return [symbol for symbol in children if symbol.name.long != '___files' and not checkName(symbol.name.long)]

def setName(value: str):
    """Suppress initial & trailing ___"""
    return value[3:][:-3]

def _createItem(value: str,children: symbols.ChildrenSymbols,short_name=None,set_base_value=False):
    """Create an item inside the file
    if short_name is set, create the short name provided
    if set_base_value is not False, give its value to symbol created"""
    name = symbols.Name(long=value,short=short_name)
    symbol = symbols.Symbol(tag_nb=1)
    symbol.name = name
    if set_base_value is not False:
        symbol.setValue(set_base_value,"every")
    children.updateChild(symbol,declaration=False) # TODO verify 

def _createColumn(value: str, children: symbols.ChildrenSymbols):
    """Create a column inside the file"""
    short_name = value[0]
    value = "___{}___".format(value)
    _createItem(value,children,short_name=short_name,set_base_value=" ")
    items = itemsOnly(children)
    if items:
        column = children[value]
        column.children = symbols.ChildrenSymbols()
        for item in items:
            _createItem(item.name.long,column.children,set_base_value='')

def _loadProject(path: str) -> symbols.Symbol:
    """Load a project as a fake symbol"""
    with open(path) as f:
        content = f.read()
    tokens = lexer.Lexer(content,path)() 
    ast = parser.Parser(tokens)(header_file=True)
    return semizer.Semizer(ast)()

def _saveProject(path: str, data: symbols.Symbol):
    """Save a project"""
    if finput("Save ?(y/n)","y") == "y":
        with open(path,'w') as f:
            content = tosource.HeaderSourcer(data)()
            f.write(content)
        print("Data saved")
    else:
        print("Discard")


def _manage(args: argparse.Namespace):
    """Manage a project"""
    if args.start:
        if os.path.isfile(args.PROJECT):
            raise NameError("'{}' already exist.".format(args.PROJECT))
        fake_symbol = symbols.Symbol(temp_name="FAKE")
        fake_symbol.children = symbols.ChildrenSymbols()
        _createItem("___files",fake_symbol.children,set_base_value=" ") # files name has no trailing ___ in order to not let the user touch it
    elif args.update:
        fake_symbol = _loadProject(args.PROJECT)
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
        result = finputWrapper("1. Type a new name to create it. The first letter will be used to give its short name.\n2. Type an already set name to update it: '-' delete it;'*' modify name;\n3. Type {} to exit (or Ctrl+D).".format(exit_value),exval=exit_value) # TODO rewrite text
        if result == exit_value:
            break
        elif result[:-1] in columns:
            name = "___{}___".format(result[:-1])
            if result[-1] == "-":
                del(fake_symbol.children[name])
            elif result[-1] == '*':
                pass # TODO modify name
            else:
                print("Sign unrecognized")
        elif result not in columns:
            if result[0] in shorts:
                print("Short name already taken")
            else:
                _createColumn(result,fake_symbol.children)

    _saveProject(args.PROJECT,fake_symbol)





def _files(args: argparse.Namespace):
    """Manage the files inside a project"""
    project = _loadProject(args.PROJECT)
    files = project.children['___files']
    if args.add: # TODO ne sauvegarder que le chemin relatif vers le fichier depuis le projet. # use relpath
        if not files.hasChildren():
            files.children = symbols.ChildrenSymbols()
        if args.add not in files.children:
            _createItem(args.add,files.children,set_base_value=" ")
            print("'{}' registered in project '{}'".format(args.add,args.PROJECT))
        else:
            raise NameError("'{}' already saved inside files".format(args.add))
    elif args.remove: # TODO idem que là haut
        if not getattr(files,'children',False) or args.remove not in files.children:
            raise NameError("'{}' can't be found.".format(args.remove))
        else:
            del(files.children[args.remove])
            print("'{}' removed from project '{}'".format(args.remove,args.PROJECT))

    else:
        raise ValueError("No name entered")

    _saveProject(args.PROJECT,project)

def _enterValue(columns: list,name: str,update=False):
    """Enter a value inside a project"""
    exit_value = "_"*3 + "exit" + "_"*3
    # create the value inside columns
    if not update:
        for column in columns:
            if not column.hasChildren():
                column.children = symbols.ChildrenSymbols()
            _createItem(name,column.children,set_base_value='')

    # setting value
    for i,column in enumerate(columns):
        cname = 'main' if i == 0 else setName(column.name.long)
        container = column.children[name]
        res = finputWrapper("Set value for column '{}'".format(cname),container.getValue('every'),exval=exit_value)
        if res == exit_value:
            return exit_value
        container.setValue(res,'every',change_authorized=True) 

def _items(args: argparse.Namespace):
    """Manage the items inside a project"""
    if not args.add and not args.change and not args.remove:
        raise ValueError("No option entered")

    project = _loadProject(args.PROJECT)
    columns = [project] + [child for child in project.children if checkName(child.name.long)]
    
    result = None
    exit_value = "_"*3 + "exit" + "_"*3
    while result != exit_value:
        print("Values already entered:")
        base = [child.name.long for child in project.children if child.name != '___files' and not checkName(child.name.long)]
        print('><'.join(base))
        print("You can exit by typing {} or Ctrl+D".format(exit_value))
        result = finputWrapper("Enter id:",exval=exit_value)
        if result == exit_value:
            break
        elif args.add or args.change:
            result = _enterValue(columns,result,args.change)
        elif args.remove:
            if result not in base:
                print("No ID : '{}'".format(result))
            else:
                for column in columns:
                    del(column.children[result])
                print("'{}' deleted".format(result))

    _saveProject(args.PROJECT,project)

def _print(args: argparse.Namespace): # TODO add color
    """A representation of a project"""
    termlen = shutil.get_terminal_size().columns
    sep = '='*termlen + '\n'
    # infos
    project = _loadProject(args.PROJECT)
    project.name = symbols.Name(long='___Main___')
    title = os.path.basename(args.PROJECT) + '\n'
    ##files
    files_column = project.children['___files']
    if files_column.hasChildren():
        files = [file for file in files_column.children]
    else:
        files = []
    ## items
    items_id = [child.name.long for child in itemsOnly(project.children)]
    columns = [project] + [column for column in project.children if checkName(column.name.long)]
    items = {}
    for id in items_id:
        key = id
        value = collections.OrderedDict(
                [(setName( column.name.long ),column.children[id].getValue('every')) for column in columns]
                )
        items[key] = value


    # infos creations
    infos = inred(title) + sep
    infos += inred('[FILES]\n') + '\n'.join(files) + sep
    infos += inred('[ITEMS]\n')
    for id,values in items.items():
        infos += inmagenta(' '*4 + id + '\n')
        for column, value in values.items(): # column in green
            list = ('\n').join(textwrap.wrap("{}: {}".format(ingreen(column),value),
                    width=termlen-8))
            print(list)
            infos += textwrap.indent(list,prefix = ' '*8,predicate=lambda x:True)
            infos += "\n"


    # page it on screen
    pydoc.pager(infos)

def _cmdline() -> argparse.Namespace:
    """Manages the command-line arguments"""
    parser = argparse.ArgumentParser(description="FRUMUL indexer")
    parser.add_argument("PROJECT",help="Path of the project file")
    parser.set_defaults(func=_print)
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
    im_options.add_argument("--change",action="store_true",default=False,help="Change an item inside a project")
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
