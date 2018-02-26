#!/usr/bin/python3
# -*-coding:Utf-8 -*
#Deus, in adjutorium meum intende
"""Symbols declared in the header files"""
import re
from . import lexer
# TODO try to save the tokens, in order to know file, columns, etc.

class Name:
    """This class manages the name of the symbol"""
    def __init__(self,**kw):
        self.short = kw.get('short') 
        self.long = kw.get('long') 
        self._error = "A {} name has already been defined for this name: {}"

    def __eq__(self,operand):
        """return True if operand == short or long name
        return True if operand == self"""
        if isinstance(operand,type(self)):
            return_value = self.short == operand.short and self.long == operand.long
        else:
            return_value = operand in (self.short,self.long)
        return return_value

    def _get_short(self):
        return self._short
    
    def _get_long(self):
        return self._long

    def _set_short(self,value):
        """set short name"""
        if value and len(value) > 1:
            raise ValueError("Short names must be one character length: '{}'".format(value))
        self._set_name(value,'short')

    def _set_long(self,value):
        """set long name"""
        if value and len(value) < 2:
            raise ValueError("Long names must be more than one character length: '{}'".format(value))
        self._set_name(value,'long')

    def _set_name(self,value: str,type: str):
        """Set name"""
        attribute = "_"+type
        if getattr(self,attribute,None) is not None:
            raise NameError(self._error.format(type,self))
        setattr(self,attribute,value)

    short = property(_get_short,_set_short)
    long = property(_get_long,_set_long)

    def __repr__(self):
        """Presentation of the instance"""
        short = "<SHORT: {}>".format(self._short) if self._short else ''
        long = "<LONG: {}>".format(self._long) if self._long else ""
        return "NAME: {}{}".format(short,long)

    def __hash__(self):
        """hash value of the object.
        WARNING: be careful to not use hash value BEFORE setting short AND long names"""
        return hash(str(self._short)+str(self._long))

    def partialEq(self,other) -> bool:
        """return True if at least one of the names of other is equal to one of self"""
        self_names = self.short, self.long
        #return True if other.long in self_names or other.short in self_names else False
        long_eq = other.long and other.long in self_names
        short_eq = other.short and other.short in self_names
        return short_eq or long_eq




class Symbol:
    """Base class for all the symbols"""
    def __init__(self,**kwargs):
        """Instanciates the object"""
        self._temp_name = kwargs.get('temp_name')# a temporary name, the ID at the left of the assign token
        self._tag_nb = kwargs.get('tag_nb')

        self._values = {} # lang:value

    def __repr__(self):
        """Representation of the instance"""
        name = getattr(self,'name',getattr(self,'temp_name',''))
        value = getattr(self,'_temp_value',self._values if self._values else 'No')
        tag = self._tag_nb if self._tag_nb else 'No' # TODO ask it to parent if value set
        children = len(getattr(self,'children',''))
        return "{}({}, value={}, tagNb={}, children={})".format(type(self).__name__,name,value,tag,children)

    def _get_tag(self) -> int:
        """Return number of tags requested by this symbol
        if self._tag_nb is set, return it
        else, ask it to parent and set self._tag_nb"""
        if not self._tag_nb:
            if self.parent:
                self._tag_nb = self.parent.tag
            else:
                raise ValueError("No parent have been set for this Symbol, or no tag number has been declared: {}".format(self))
        return self._tag_nb

    tag = property(_get_tag)

    def setValue(self,value: str,lang=None):
        """set a value for specific lang"""
        if value == getattr(self,'_temp_value',False):
            del(self._temp_value)
        if lang:
            #self.current_lang = lang # à vérifier avant de supprimer
            if lang not in self._values:
                self._values[lang] = value
            else:
                raise ValueError("{} has already a value for {} language: {}".format(self,lang,self._value))

        else:
            if self.__dict__.get('_temp_value',True):
                self._temp_value = value
            else:
                raise ValueError("There is already a temp value: {}".format(self._temp_value))

    def getValue(self,lang: str) -> str:
        """Get specific value"""
        if lang not in self._values:
            raise ValueError('No value for requested lang: {}'.format(lang))
        return self._values[lang]

    def hasChildren(self) -> bool:
        """Return True if object has children"""
        return bool(getattr(self,'children',False))

    def hasValue(self) -> bool:
        """Return True if object has value"""
        return bool(self._values)

class ChildrenSymbols:
    """The table of the children symbols"""
    def __init__(self,parent=None):
        """init"""
        self._children = {}
        self._parent = parent

    def __repr__(self):
        """Representation of the instance"""
        return str([child for child in self._children])

    def __iter__(self):
        """Iterates on the children"""
        for elt in self._children.values():
            yield elt

    def __len__(self):
        """Number of children"""
        return len(self._children)

    def __bool__(self):
        """Return True if it has children"""
        return bool(self._children)

    def __contains__(self,entry):
        """entry can be a Name object or a str.
        if a str, it must be a short or a long name"""
        return entry in [key for key in self._children.keys()]

    def __getitem__(self,entry):
        """entry can be an Name object or a str.
        return Symbol object which has this name inside the instance"""
        for symbol in self._children.values():
            if entry == symbol.name:
                return symbol
        else:
            raise KeyError("No symbol with requested tag: {}".format(entry))

    def _set_parent(self,parent):
        """Set parent"""
        if self._parent:
            raise NameError("A parent: {}  has yet been declared for these children: {}".format(parent,self))
        self._parent = parent
        for child in self._children.values():
            child.parent = parent

    def _get_parent(self,parent):
        """Get parent"""
        return self._parent
    
    parent = property(_get_parent,_set_parent)

    def updateChild(self,child,declaration=True):
        """If child doesn't exist yet, add it.
        Else update existing child #TODO
        if declaration==False, does not use self.declared_children""" 
        if declaration:
            if child._temp_name not in self.declared_children:
                raise NameError('{} has not been declared before definition'.format(child._temp_name))
            child.name = [name for name in self.declared_children if child._temp_name == name][0]
            self.declared_children.remove(child.name)
        else:
            child.name = Name(long=child._temp_name)
            del(child._temp_name)
        self._children[child.name] = child

    def updateValues(self, lang: str):
        """update the values of all the children
        which have not a value for specific lang"""# TODO many mistakes possible
        for child in self._children.values():
            if getattr(child,'_temp_value',False): 
                child.setValue(child._temp_value,lang)
            # for children of this child
            if getattr(child,'children',False):
                child.children.updateValues(lang)

    def declare(self,value: lexer.Token):
        """Declare children""" 
        self.declared_children = [
                name for name in self._parse(value)
                ]
        for i,name in enumerate(self.declared_children):
            double = [other for other in self.declared_children[i+1:] if name.partialEq(other)]
            if double:
                raise NameError("Two constants have the same name: {} - {}".format(name,double[0]))


    def _parse(self,value: lexer.Token):
        """Generator. Parse a string
        and send name"""
        lex = lexer.DefinitionLexer(value)
        tokens = lex()
        i = 0
        while i < len(tokens):
            current = tokens[i]
            if current.type == lexer.LONGNAME:
                yield Name(long=current.value)
            elif current.type == lexer.SHORTNAME:
                short = current.value
                long = None
                if i+1 < len(tokens) and tokens[i+1].type == lexer.LONGNAME:
                    long = tokens[i+1].value
                    i+=1

                yield Name(short=short,long=long)
            i+=1

    def giveChild(self,value: str) -> Symbol:
        """Look in self._children to find
        the child.""" # TODO verify that string does not contain spaces or is empty 
        child = None
        if value[0] == '.': # case of value starting by a dot (to separate long names)
            if '.' in self:
                child = self.__getitem__('.')
            value = value[1:]

        if not child:
            for type_name in ('long','short'):
                result = self._match_with(value,type_name)
                if result:
                    child,value = result
                    break


        if not result or value and not child.hasChildren():
            raise ValueError("'{}' canno't be interpreted".format(value))
        if value : # if value is not entirely consumed
            child = child.children.giveChild(value)

        return child

    def _match_with(self,value: str,name_type: str):
        """Method used by giveChild to see
        if the first part of value can be found
        in instance
        return tuple(Symbol,str) or None"""
        names = [ getattr(name,name_type) for name in self._children if getattr(name,name_type) ]
        for name in names:
            match = re.match(name,value)
            if match:
                child = self.__getitem__(match.group(0))
                value = value[match.end(0):]
                return child, value



