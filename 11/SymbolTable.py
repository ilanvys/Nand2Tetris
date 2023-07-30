"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    kind_dict = {"var":"local", "field":"this", "static":"static", "argument":"argument"}
    
    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.num_of_var = 0
        self.num_of_arg = 0
        self.num_of_static = 0
        self.num_of_field = 0
        self.class_sym_table = []
        self.sub_sym_table = []        

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.num_of_var = 0
        self.num_of_arg = 0
        self.sub_sym_table = []

    
    def kind_counter(self, kind: str) -> int:
        """Adds 1 to the current counter of "kind".
        Returns:
            The current counter of "kind"
        """
        if kind == "var":
            self.num_of_var += 1
            return self.num_of_var - 1
        elif kind == "argument":
            self.num_of_arg += 1
            return self.num_of_arg - 1
        elif kind == "static":
            self.num_of_static += 1
            return self.num_of_static - 1
        elif kind == "field":
            self.num_of_field += 1
            return self.num_of_field - 1

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in ["static", "field"]:
            self.class_sym_table.append([name, type, kind, self.kind_counter(kind)])
            
        elif kind in ["var", "argument"]:
            self.sub_sym_table.append([name, type, kind, self.kind_counter(kind)])
            

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "var":
            return self.num_of_var 
        elif kind == "arg":
            return self.num_of_arg
        elif kind == "static":
            return self.num_of_static
        elif kind == "field":
            return self.num_of_field 

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        for entry in self.sub_sym_table:
            if entry[0] == name:
                return self.kind_dict[entry[2]]
        for entry in self.class_sym_table:
            if entry[0] == name:
                return self.kind_dict[entry[2]]
        return None

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        for entry in self.sub_sym_table:
            if entry[0] == name:
                return entry[1]
        for entry in self.class_sym_table:
            if entry[0] == name:
                return entry[1]
        return None

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        for entry in self.sub_sym_table:
            if entry[0] == name:
                return entry[3]
        for entry in self.class_sym_table:
            if entry[0] == name:
                return entry[3]
        return None
