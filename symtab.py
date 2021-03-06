# -----------------------------------------------------------------------------
# narrtr: symtab.py
# This file defines the Symbol Table class for narratr that is used by the
# parser and code generator.
#
# Copyright (C) 2015 Team narratr
# All Rights Reserved
# Team narratr: Yelin Hong, Shloka Kini, Nivvedan Senthamil Selvan, Jonah
# Smith, Cecilia Watt
#
# File Created: 13 April 2015
# Primary Author: Nivvedan Senthamil Selvan <nivvedan.s@columbia.edu>
#
# Any questions, bug reports and complaints are to be directed at the primary
# author.
#
# -----------------------------------------------------------------------------

POCKET = -0x90CCE7
GLOBAL = -0xC10BA1


class SymTabEntry:
    """An entry in the narratr symbol table.

    symbol        the actual symbol. "x" for variable x, "key" for item key
                  and "$1" for scene $1.
    value         the value of variables. This is the AST of the definitions
                  for scenes and items.
    symboltype    the type of the symbol - "scene", "item", "integer",
                  "string", "float", "boolean", "list"
    scope         applicable for all variables. It is the scene ID in which a
                  variable has scope. It may also be POCKET, or GLOBAL.
                  GLOBAL is for scenes and items.
    god           a boolean corresponding to whether the variable was
                  declared as a god variable."""
    def __init__(self, symbol, value, symboltype, scope, god):
        self.symbol = symbol
        self.value = value
        self.symboltype = symboltype
        self.scope = scope
        self.god = god

    def __repr__(self):
        return "[" + str(self.symbol) + ", " + str(self.value) + ", " \
                + str(self.symboltype) + ", " + str(self.scope) + ", " \
                + str(self.god) + "]"


class SymTab:
    def __init__(self):
        self.table = {}

    def getKey(self, symbol, scope):
        """Use scope and symbol to construct the internal key representation.

        Note, this is just string manipulation; it does not access the symbol
        table entries."""
        if scope == POCKET:
            key = "POCKET." + str(symbol)
        elif scope == GLOBAL:
            key = "GLOBAL." + str(symbol)
        else:
            key = str(scope) + "." + str(symbol)
        return key

    def overwrite(self, entry):
        """Overwrites an existing entry in the Symbol Table."""
        if isinstance(entry, SymTabEntry):
            self.table[self.getKey(entry.symbol, entry.scope)] = entry
        else:
            raise Exception("Insert needs a valid Symbol Table entry.")

    def insert(self, symbol, value, symboltype, scope, god=False):
        """Interface used to add new SymTab entries.

        Parameters are explained above in SymTabEntry. god defaults to
        False for backward compatability."""
        if self.getKey(symbol, scope) in self.table:
            raise Exception("Symbol already in the Symbol Table in " +
                            "the same scope.")
        else:
            self.overwrite(SymTabEntry(symbol, value, symboltype, scope, god))

    def get(self, symbol, scope):
        """The interface used to get a SymTab Entry from the table.

        Returns None if there is no entry."""
        return self.table.get(self.getKey(symbol, scope), None)

    def getWithKey(self, key):
        """Get a symbol table entry if you already have the key."""
        return self.table.get(key, None)

    def update(self, symbol, value, symboltype, scope, god=False):
        """Update an existing entry in the symbol table."""
        if self.getKey(symbol, scope) not in self.table:
            raise Exception("Symbol not in the Symbol Table in the same" +
                            "scope. Nothing to update")
        else:
            self.overwrite(SymTabEntry(symbol, value, symboltype, scope, god))

    # String representation of the Symbol Table
    def __repr__(self):
        items = []
        for key in self.table:
            items.append(str(key) + " : " + self.table[key].__repr__())
        return "\n".join(items)
