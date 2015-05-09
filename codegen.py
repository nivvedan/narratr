# -----------------------------------------------------------------------------
# narrtr: codegen.py
# This file contains the Code Generator to generate target Python code.
#
# Copyright (C) 2015 Team narratr
# All Rights Reserved
# Team narratr: Yelin Hong, Shloka Kini, Nivvedan Senthamil Selvan, Jonah
# Smith, Cecilia Watt
#
# File Created: 01 April 2015
# Primary Authors: Jonah Smith, Yelin Hong, Shloka Kini
#
# Any questions, bug reports and complaints are to be directed at the primary
# author.
#
# -----------------------------------------------------------------------------

from sys import stderr, exit
from node import Node


class CodeGen:
    def __init__(self):
        self.frontmatter = "#!/usr/bin/env python\nfrom sys import exit\n\n"
        self.scenes = []
        self.scene_nums = []
        self.items = []
        self.item_names = []
        self.main = ""

    # This function takes as its arguments the root node of the AST and the
    # symbol table. It saves the symbol table to a class variable (so it is
    # accessible anywhere in the code using self), and looks through the AST
    # to identify the high level nodes (i.e. scenes, items, and startstate),
    # sending the appropriate nodes to the appropriate functions for
    # processing. Note we know the structure of the AST, so we don't need
    # DFS or other tree searching algorithms, which improves efficiency.
    def process(self, node, symtab):
        self.symtab = symtab
        if len(node.children) != 1 or node.children[0].type != "blocks":
            self._process_error("Unexpected Parse Tree - Incorrect number" +
                                "or type of children for the top node",
                                node.lineno)
        blocks = node.children[0].children
        for block in blocks:
            if type(block) is dict:
                for key, s_i in block.iteritems():
                    if s_i.type == "scene_block":
                        self._add_scene(self._scene_gen(s_i, key))
                    elif s_i.type == "item_block":
                        self._add_item(self._item_gen(s_i, key))
            elif block.type == "start_state":
                self._add_main(block)
            else:
                self._process_error("Found unexpected block types.",
                                    block.lineno)

    # This function takes the instance variables constructed by the process()
    # function and writes them to an output file. (As such, it must be run
    # AFTER process()! It is intended to be called externally, within the
    # main compiler. It takes one argument, outputfile, which is a string of
    # the location where the file should be written. By convention, that file
    # should be in the form of *.ntrc. If no outputfile is specified
    # or the outputfile is specified as "stdout", the code prints to standard
    # out (e.g. usually the terminal window). That's mainly for debugging
    # purposes, and should not be used in the production compiler, as the
    # line breaks are only approximations.
    def construct(self, outputfile="stdout"):
        if self.main == "":
            self._process_warning("No start scene specified. " +
                                  "Defaulting to $1.")
            self._add_main(1)

        if outputfile == "stdout":
            print self.frontmatter
            print "\n".join(self.scenes)
            print "\n".join(self.items)
            print self.main
        else:
            with open(outputfile, 'w') as f:
                f.write(self.frontmatter)
                f.write("\n")
                f.write("\n".join(self.scenes))
                f.write("\n\n")
                f.write("\n".join(self.items))
                f.write("\n\n")
                f.write(self.main)

    # This function is used internally to add a scene to the scene list. It
    # takes a string *with correct indentation*.
    def _add_scene(self, scene):
        self.scenes.append(scene)

    # This function is used internally to add a item to the item list. It
    # takes a string *with correct indentation*.
    def _add_item(self, item):
        self.items.append(item)

    # This function generates the code for a start state given a start state
    # node. If start state code has already been generated, it produces a
    # warning and keeps the start state declared higher in the program. If
    # called without a node, it triggers the default action, which is a start
    # state of 1. This should only be used internally.
    # ABOUT THE RESPONSE CODE: the default response code, which is dropped
    # into a function called get_response(), waits for user input. When it
    # it receives this input, it strips the case (i.e. everything is made
    # lower case), removes all punctuation except double quotes (to allow
    # the programmer to add conversational capabilities), converts all
    # whitespace characters into a single space, and then checks for specific
    # situations we agree with the programmer to handle by default. 'exit'
    # will terminate the game (there is no current way to save game state),
    # and "move" followed by a single token will check the dictionary of
    # directions (which it takes as an argument) for an applicable direction.
    # If it does not appear in the dictionary, an error is reported so the user
    # is not confused.  If it does appear, it encodes the next scene's function
    # call within a list so that it can easily be identified by the caller
    # function, which will return that piece of code. This is a centerpiece of
    # our approach to avoiding an overflow of activation records in large
    # games.
    def _add_main(self, startstate):
        if self.main == "":
            self.main = "pocket = {}\n"
            self.main += '''def get_response(direction):
    response = raw_input(" -->> ")
    response = response.lower()
    response = response.translate(None,
                "!#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~")
    response = ' '.join(response.split())
    if response == "exit":
        print "== GAME TERMINATED =="
        exit(0)
    elif response[:5] == "move " and len(response.split(" ")) == 2:
        if response.split(" ")[1] in direction:
            return ["s_" + str(direction[response.split(" ")[1]])\\
                + "_inst.setup()"]
        else:
            print "\\"" + response.split(" ")[1] + "\\" is not a "\\
                + "valid direction from this scene."
    else:
        return response\n\n'''

            # Create an instance of each scene that has been declared.
            for s in self.scene_nums:
                self.main += "s_" + str(s) + "_inst = s_" + str(s) + "()\n"

            if isinstance(startstate, Node):
                ss = startstate.value
            else:
                ss = startstate

            if ss in self.scene_nums:
                self.startstate = ss
            else:
                self._process_error("Start scene $" + str(startstate.value) +
                                    " does not exist.")

            self.main += "if __name__ == '__main__':\n    next = s_"\
                + str(self.startstate) + "_inst.setup()\n    while True:\n"\
                + "        exec 'next = ' + next"
        else:
            self._process_warning("Multiple start scene declarations. " +
                                  "Using scene $" + self.startstate + ".")

    # This function takes a scene node and processes it, translating into
    # valid Python (really, a Python class). Iterates through the children
    # of the input node and constructs the setup, cleanup, and action blocks
    # using boilerplate code. This should only be used internally. In the
    # action_block part, adding while(true) loop to get response and then
    # process it. def achition is now taking direction as argument, direction
    # is an empty dictionary by default.
    def _scene_gen(self, scene, sid):
        commands = []
        direction_sign = False
        for c in scene.children:
            if c.type == "SCENEID":
                sid = c.value

            elif c.type == "setup_block":
                commands += self._process_setup_block(c)

            elif c.type == "cleanup_block":
                commands += self._process_cleanup_block(c)

            elif c.type == "action_block":
                commands += self._process_action_block(c)

        self.scene_nums.append(sid)
        scene_code = "class s_" + str(sid) + ":\n    def __init__(self):"\
            + "\n        self.__namespace = {}\n\n    "\
            + "\n    ".join(commands)

        return scene_code

    def _item_gen(self, item, iid):
        commands = []
        iid = item.value
        self.item_names.append(iid)
        item_code = "class item_" + str(iid) + ":\n    "
        # "\n    ".join(commands)
        for c in item.children:
            if c.type == "calllist":
                item_code = item_code + "def __init__(self"
                for exp in c.children:
                    item_code += "," + exp.children[0].value
                item_code += "):\n"
            elif c.type == "suite":
                commands += self._process_item_block(item)
        item_code = item_code + "    ".join(commands)
        # + "\n        pass\n\n    "

        # Here modify code so that constructor takes args
        # in python:
# class key:
#     def __init__(self, identifier)
#         self.id = identifier
        return item_code

    def _process_item_block(self, c):
        commands = []
        if len(c.children) > 0:
            commands.append(self._process_suite(c, 2))
        return commands

# in narratr: k is key(1) (is the constructor call)
# ...
# item key(identifier){
# if identifier > 1:
#     id = identifier
# else:
#     id = identifier + 5
# }

# in python:
# class key:
#     def __init__(self, identifier):
#         if identifier > 1:
#             self.id = identifier
#         else:
#             self.id = identifier + 5

    # Code for adding a setup block. Takes as input a single "setup block"
    # node. Adds boilerplate code (function definition, empty dictionary for
    # direction, and at the end, the code to move to the action block), and
    # sends the child nodes to _process_suite() to generate their code.
    def _process_setup_block(self, c):
        commands = []
        commands.append("def setup(self):" +
                        "\n        direction = {}")

        if len(c.children) > 0:
            for child in c.children:
                commands.append(self._process_suite(child, 2))
        commands.append("    return self.action(direction)\n")
        return commands

    # Code for adding a cleanup block. Takes as input a single "cleanup block"
    # node. Adds boilerplate code (function definition and "pass" if necessary,
    # explained below), then sends the child nodes to _process_suite() to
    # generate their code. "pass" is required in the scenario that there are no
    # child nodes, in which case Python syntactically requires code, we need to
    # be able to execute the function, but we don't want anything to happen. #
    # "pass" is a Python command that does nothing, so it fits the bill.
    def _process_cleanup_block(self, c):
        commands = []
        commands.append("def cleanup(self):")
        if len(c.children) > 0:
            commands.append(self._process_suite(c.children[0], 3))
        else:
            commands.append("    pass")
        return commands

    # Code for adding an action block. Takes as input a single "action block"
    # node. Adds boilerplate code (function definition, initialize "response"
    # as an empty string so it does not trip up the REPL loop, and add a "while
    # True:" loop to get the REPL loop). The action block itself takes the
    # direction dictionary for that scene as a parameter so it can pass it to
    # the get_response() function. It also passes the name of the class so
    # get_response() knows which scene's cleanup block to call if the user is
    # trying to move between scenes.
    def _process_action_block(self, c):
        commands = []
        commands.append("def action(self, direction):")
        commands.append("    response = \"\"\n        while True:")
        if len(c.children) > 0:
            for child in c.children:
                commands.append(self._process_suite(child, 3)[5:])
        commands.append("        response = get_response(" +
                        "direction)\n            " +
                        "if isinstance(response, list):" +
                        "\n                self.cleanup()\n" +
                        "                return response[0]\n")
        return commands

    def _process_suite(self, suite, indentlevel=1):
        commands = ""
        if len(suite.children) != 1:
            self._process_error("Too many children in suite.")
        else:
            if suite.value == "simple":
                commands += self._process_simple_smt(suite.children[0],
                                                     indentlevel)
            else:
                commands += self._process_statements(suite.children[0],
                                                     indentlevel)
        return commands

    def _process_statements(self, statements, indentlevel=1):
        commands = ''
        for smt in statements.children:
            commands += self._process_statement(smt, indentlevel)
        return commands

    def _process_statement(self, statement, indentlevel=1):
        commands = ''
        if statement.value == "simple":
            commands += self._process_simple_smt(statement.children[0],
                                                 indentlevel)
        elif statement.value == "block":
            commands += self._process_block_smt(statement.children[0],
                                                indentlevel)
        else:
            self._process_error("Not accepted ")
        return commands

    # Statement is actually a suite node, but we're keeping the name for
    # backwards-compatability.
    def _process_simple_smt(self, smt, indentlevel=1):
        commands = ''
        prefix = "\n" + "    "*indentlevel
        if not isinstance(smt, Node):
            self._process_error("Something bad happened while processing " +
                                "'simple statement'. Unfortunately, that is " +
                                "all we know.")
        if len(smt.children) == 0:
            self._process_error("Simple statement has no children to process.",
                                smt.lineno)
        if smt.value == "say":
            commands += prefix + self._process_say_smt(smt.children[0])
        elif smt.value == "exposition":
            commands += prefix + self._process_expo_smt(smt.children[0])
        elif smt.value == "win":
            commands += self._process_win_smt(smt.children[0], indentlevel)
        elif smt.value == "lose":
            commands += self._process_lose_smt(smt.children[0], indentlevel)
        elif smt.value == "expression":
            commands += self._process_expression_smt(smt.children[0],
                                                     indentlevel)
        elif smt.value == "flow":
            commands += self._process_flow_smt(child)
        return commands

    def _process_block_smt(self, smt, indentlevel=1):
        commands = ''
        prefix = "\n" + "    "*indentlevel
        if not isinstance(smt, Node):
            self._process_error("Something bad happened while processing " +
                                "'block statement'. Unfortunately, that is " +
                                "all we know.")
        if len(smt.children) == 0:
            self._process_error("Block statement has no children to process.",
                                smt.lineno)
        for child in smt.children:
            if child.type == "if_statement":
                self._process_ifstatement(child)
            elif child.type == "while_statement":
                self._process_whilestatement(child)
        return commands

    # Say statement function is called from simple statement and
    # passes node to _process_testlist()
    def _process_say_smt(self, smt):
        commands = 'print '
        if not isinstance(smt, Node):
            self._process_error("Something bad happened while processing " +
                                "'say statement'. Unfortunately, that is " +
                                "all we know.")
        if len(smt.children) == 0:
            self._process_error("Say statement has no children to process.",
                                smt.lineno)
        commands += self._process_testlist(smt.children[0])
        return commands

    # Exposition statement passes node to _process_testlist
    def _process_expo_smt(self, smt):
        commands = 'print '
        if not isinstance(smt, Node):
            self._process_error("Something bad happened while processing " +
                                "'exposition statement'. Unfortunately, " +
                                "that is all we know.")
        if len(smt.children) == 0:
            self._process_error("Exposition statement has no children to" +
                                " process.", smt.lineno)
        commands += self._process_testlist(smt.children[0])
        return commands

    # Win tatement, print the smt if there is and exit the scene
    def _process_win_smt(self, smt, indentlevel):
        prefix = "\n" + "    "*indentlevel
        commands = ""
        if not isinstance(smt, Node):
            self._process_error("Something bad happened while processing " +
                                "'win statement'. Unfortunately, that is " +
                                "all we know.")
        if len(smt.children) != 0:
            commands += prefix + "print "\
                        + self._process_testlist(smt.children[0])
        commands += prefix + "exit(0)"
        return commands

    # Lose tatement, print the smt if there is and exit the scene
    def _process_lose_smt(self, smt, indentlevel):
        prefix = "\n" + "    "*indentlevel
        commands = ""
        if not isinstance(smt, Node):
            self._process_error("Something bad happened while processing " +
                                "'lose statement'. Unfortunately, that is " +
                                "all we know.")
        if len(smt.children) != 0:
            commands += prefix + "print "\
                        + self._process_testlist(smt.children[0])
        commands += prefix + "exit(0)"
        return commands

    # Expression statement
    def _process_expression_smt(self, smt, indentlevel):
        prefix = '\n' + '    '*indentlevel
        commands = ''
        if not isinstance(smt, Node):
            self._process_error("Something bad happened while processing " +
                                "'lose statement'. Unfortunately, that is " +
                                "all we know.")
        if len(smt.children) == 0:
            self._process_error("Lose statement has no children to process.",
                                smt.lineno)
        elif smt.value == "testlist":
            commands += prefix + self._process_testlist(smt.children[0])
        elif smt.value == "is":
            # todo check for god variable in symtab
            god = self.symtab.getWithKey(smt.children[0].v_type).god
            if god:
                commands += prefix + "self." + smt.children[0].value
            else:
                commands += prefix + "self.__namespace['" + \
                            smt.children[0].value + "'] = "
            commands += self._process_testlist(smt.children[1])
        elif smt.value == "godis":
            commands += prefix + "try:"
            commands += prefix + "    " + smt.children[0].value
            commands += prefix + "except NameError:"
            commands += prefix + "    self." + smt.children[0].value + " = "
            commands += prefix + self._process_testlist(smt.children[1])
        return commands

    # Flow statemnt
    def _process_flow_smt(self, smt):
        commands = ''
        if not isinstance(smt, Node):
            self._process_error("Something bad happened while processing " +
                                "'flow statement'. Unfortunately, that is " +
                                "all we know.")
        if len(smt.children) == 0:
            self._process_error("Flow statement has no children to process.",
                                smt.lineno)
        for c in smt.children:
            if c.type == "flow_statement":
                for child in c.children:
                    if child.type == "continue_statement":
                        commands += child.value
                    elif child.type == "break_statement":
                        commands += child.value
                    elif child.type == "moves_declaration":
                        pass
                    elif child.type == "moveto_statement":
                        pass

    # This function takes "testlist" node as argument
    def _process_testlist(self, testlist):
        if not isinstance(testlist, Node):
            self._process_error("Something bad happened while processing " +
                                "'testlist'. Unfortunately, that is all we " +
                                "know.")
        if len(testlist.children) == 0:
            self._process_error("Testlist has no children to process.",
                                testlist.lineno)
        tests = testlist.children
        testcode = []
        for test in tests:
            testcode.append(self._process_test(test))
        return ",".join(testcode)

    def _process_test(self, test):
        if not isinstance(test, Node) or test.type != "test":
            self._process_error("Something bad happened while processing " +
                                "'test'. Unfortunately, that is all we know.")
        if len(test.children) != 1:
            self._process_error("'test' has incorrect number of children.",
                                test.lineno)
        return self._process_or_test(test.children[0])

    def _process_or_test(self, or_test):
        if not isinstance(or_test, Node) or or_test.type != "or_test":
            self._process_error("Something bad happened while processing " +
                                "'or_test'. Unfortunately, that is all we " +
                                "know.")
        if len(or_test.children) not in [1, 2]:
            self._process_error("'or_test' has incorrect number of children.",
                                or_test.lineno)
        if or_test.value == 'or':
            return '(' + self._process_or_test(or_test.children[0]) + ') or ' \
                    + self._process_and_test(or_test.children[1])
        else:
            return self._process_and_test(or_test.children[0])

    def _process_and_test(self, and_test):
        if not isinstance(and_test, Node) or and_test.type != "and_test":
            self._process_error("Something bad happened while processing " +
                                "'and_test'. Unfortunately, that is all we " +
                                "know.")
        if len(and_test.children) not in [1, 2]:
            self._process_error("'and_test' has incorrect number of children.",
                                and_test.lineno)
        if and_test.value == 'and':
            return '(' + self._process_and_test(and_test.children[0]) + \
                    ') and ' + self._process_not_test(and_test.children[1])
        else:
            return self._process_not_test(and_test.children[0])

    def _process_not_test(self, not_test):
        if not isinstance(not_test, Node) or not_test.type != "not_test":
            self._process_error("Something bad happened while processing " +
                                "'not_test'. Unfortunately, that is all we " +
                                "know.")
        if len(not_test.children) != 1:
            self._process_error("'not_test' has incorrect number of children.",
                                not_test.lineno)
        if not_test.value == 'not':
            return 'not ' + self._process_not_test(not_test.children[0])
        else:
            return self._process_comparison(not_test.children[0])

    def _process_comparison(self, comparison):
        if not isinstance(comparison, Node) or comparison.type != "comparison":
            self._process_error("Something bad happened while processing " +
                                "'comparison'. Unfortunately, that is all we" +
                                " know.")
        if len(comparison.children) not in [1, 3]:
            self._process_error("'comparison' has incorrect number of " +
                                "children.", comparison.lineno)
        if comparison.value == 'comparison':
            return '(' + self._process_comparison(comparison.children[0]) + \
                   ') ' + self._process_comparisonop(comparison.children[1]) \
                   + " " + self._process_expression(comparison.children[2])
        else:
            return self._process_expression(comparison.children[0])

    def _process_comparisonop(self, comparisonop):
        return comparisonop.value

    # This function takes statement node with "while" value.
    def _process_whilestatement(self, smt, indentlevel=1):
        commands = "while "
        commands += self._process_test(smt.children[0], 0) + ":\n    "
        for c in smt.children[1:]:
            commands += self._process_suite(c, indentlevel+1)
        return commands

    # This function takes statement node with "if" value, or an elif node.
    # Note, because of the embedding structure, we need to process it this
    # way, and the constructions are identical, except "if" vs "elif" token.
    def _process_ifstatement(self, smt, indentlevel=1):
        if smt.value is not None:
            commands = "if "
        else:
            commands = "elif "
        commands += self._process_test(smt.children[0], 0) + ":\n    "
        for c in smt.children[1:]:
            if c.value == "else":
                commands += "\n" + "    "*indentlevel + "else:\n    "
                commands += self._process_suite(c, indentlevel+1)
            elif c.type == "elif_statements":
                commands += "\n    "\
                         + self._process_suite(Node(None, "suite", [c]),
                                               indentlevel)
            else:
                commands += self._process_suite(c, indentlevel+1)
        return commands

    # This function takes "expression" node as argument
    def _process_expression(self, expression):
        return self._process_arithmetic(expression.children[0])

    # This function processes atom nodes.
    def _process_atom(self, atom):
        if not isinstance(atom, Node) or atom.type != "atom":
            self._process_error("Something bad happened while processing " +
                                "'atom'. Unfortunately, that is all we " +
                                "know.")
        if atom.is_leaf():
            if atom.v_type == "string":
                return str(atom.value)
            else:
                if not atom.v_type:
                    self._process_error("Name Error: " + str(atom.value) +
                                        " is not defined.", atom.lineno)
                else:
                    entry = self.symtab.getKey(atom.v_type)
                    if entry.god:
                        return "self." + atom.value
                    else:
                        return "self.__namespace['" + atom.value + "']"
        if len(atom.children) != 1:
            self._process_error("'atom' has incorrect number of " +
                                "children.", atom.lineno)
        if atom.type == "test":
            return "(" + self._process_test(atom.children[0]) + ")"
        elif atom.type == "list":
            return self._process_list(atom.children[0])
        elif atom.type == "number":
            return self._process_number(atom.children[0])
        elif atom.type == "boolean":
            return self._process_boolean(atom.children[0])
        else:
            self._process_error("'atom' has unknown chid type.", atom.lineno)

    # This function processes number nodes.
    def _process_number(self, number):
        if not isinstance(number, Node) or number.type != "number":
            self._process_error("Something bad happened while processing " +
                                "'number'. Unfortunately, that is all we " +
                                "know.")
        if number.is_leaf():
            return str(number.value)
        else:
            self._process_error("'number' has children. It should be sterile.",
                                number.lineno)

    # This function processes boolean nodes.
    def _process_boolean(self, boolean):
        if not isinstance(boolean, Node) or boolean.type != "boolean":
            self._process_error("Something bad happened while processing " +
                                "'boolean'. Unfortunately, that is all we " +
                                "know.")
        if boolean.is_leaf():
            return str(number.value)
        else:
            self._process_error("'boolean' has children. It should be " +
                                "sterile.", boolean.lineno)

    # This function takes "factor" node as argument
    def _process_factor(self, factors):
        commands = ""
        # When is this triggered, if ever? Is there a better way to write
        # it?
        if len(factors.children) > 0:
            if len(factors.children) == 3:
                for factor in factors.children[0].children:
                    commands += str(factor.value) + ' '
                if factors.children[1].type == "comparison_op":
                    commands += factors.children[1].value
                for factor in factors.children[2].children:
                    commands += ' ' + str(factor.value)

            elif factors.children[0].v_type == "boolean":
                if factors.children[0].children[0].value == "true":
                    commands += "True"
                elif factors.children[0].children[0].value == "false":
                    commands += "False"

        if factors.v_type in ["integer", "float"]:
            commands += str(factors.value)

        elif factors.v_type == "string":
            commands += '"' + factors.value + '"'

        elif factors.v_type == "list":
            commands += "["
            count = 0
            for lchild in factors.children:
                tl = lchild.children[0]
                commands += self._process_expression(tl)
                count += 1
                if count != len(child.children):
                    commands += ', '
            commands += "]"

        elif factors.value == "list":
            commands += "nlist"
            if len(factors.children) > 0:
                for fchild in child.children:
                    if fchild.type == "trailer":
                        if len(fchild.children) > 0:
                            fcount = 0
                            for ffchild in fchild.children:
                                if ffchild.type == "dot":
                                    commands += ffchild.value
                                elif ffchild.type == "id":
                                    if ffchild.value == "add":
                                        commands += "append("
                                elif ffchild.type == "expression":
                                    t = ffchild
                                    temp = self._process_expression(t)
                                    commands += temp
                                    fcount += 1
                                    if fcount != len(fchild.children):
                                        commands += ', '
                                    else:
                                        commands += ')'

        elif factors.v_type == "id":
            if factors.value == "pocket":
                commands += self._process_pocket(factors)
            elif(self.symtab.get(factors.value, 'GLOBAL')):
                if len(factors.children[0].children) > 0:
                    commands += "("
                    for c in factors.children[0].children:
                        commands += self._process_expression(c) + ","
                        commands = commands[:-1] + ")"
            else:
                if blocktype == 'scene':
                    commands += "self.__namespace['" + factors.value + "']"
                elif blocktype == 'item':
                    commands += factors.value
        elif factors.value is None:
            commands += self._process_factor(factors)
        elif factors.v_type == "string":
            if factors.value == "str":
                commands += "str("
                commands += self._process_expression(
                            factors.children[0].children[0])
                commands += ")"
            else:
                commands += '"' + factors.value + '"'
        elif factors.v_type == "integer":
            commands += str(factors.value)
        return commands

    # This function recursively deals with arithmetic node
    def _process_arithmetic(self, expr, expvalue):
        commands = ''
        if len(expr.children) > 0:
            for child in expr.children:
                if child.type == "arithmetic_expression":
                    if child.value not in ['+', '-', '*', '/']:
                        if len(child.children) > 0:
                            if child.children[0].type == "factor":
                                tempc = child.children[0]
                                temp = self._process_factor(tempc)
                                if datatype == "String":
                                    if tempc.v_type == 'string':
                                        commands += temp
                                    else:
                                        commands += 'str(' + temp + ')'
                                else:
                                    commands += temp
                                commands += ' ' + expvalue + ' '
                    else:
                        if child.v_type == "integer":
                            tv = child.value
                            c = child
                            temp = self._process_arithmetic(c, tv)
                            commands += temp + ' '
                            if datatype == "String":
                                commands += 'str(' + str(tv) + ')' + ' '
                            else:
                                commands += str(tv) + ' '
                        elif child.v_type == 'id':
                            tv = child.value
                            c = child
                            temp = self._process_arithmetic(c, tv)
                            commands += temp + ' '
                            commands += str(tv) + ' '
                elif child.type == "term":
                    if child.value is None:
                        if len(child.children) > 0:
                            if child.children[0].type == "factor":
                                tc = child.children[0]
                                if (datatype == "String" and
                                        tc.v_type != 'string'):
                                    commands += 'str('
                                commands += self._process_factor(tc)
                                if (datatype == "String" and
                                        tc.v_type != 'string'):
                                    commands += ')'
                    elif child.value in ['*', '/']:
                        tv = str(child.value)
                        temp = self._process_arithmetic(child, tv)
                        commands += temp
                elif child.type == "factor":
                    if child.v_type == 'id':
                        commands += ' ' + expvalue + ' '
                        if blocktype == 'scene':
                            commands += "self.__namespace['"
                            commands += str(child.value) + "']"
                        elif blocktype == 'item':
                            commands += str(child.value)
                    if child.v_type == 'integer':
                        if datatype == "String":
                            commands += ' str(' + expvalue + ') '
                        else:
                            commands += ' ' + expvalue + ' '
                        commands += str(child.value)
        return commands

    # This function takes "direction" node as argument
    # Building a dictionary for direction, using the direction as key and
    # scene number as value
    def _process_direction(self, direction):
        commands = ''
        commands += direction.value
        commands += '": '
        for scene in direction.children:
            commands += str(scene.value)
        return commands

    def _process_pocket(self, pocket_node, indentlevel=1):
        commands = ""
        add = get = remove = False
        if len(pocket_node.children) != 2:
            self._process_error("Pocket has the wrong structure.",
                                pocket_node.lineno)

        if pocket_node.children[0].children[1].value == "add":
            if len(pocket_node.children[1].children) != 2:
                l = len(pocket_node.children[1].children)
                self._process_error("Adding to the pocket requires" +
                                    " exactly two arguments. " +
                                    str(l) + " given.", pocket_node.lineno)
            else:
                commands += "pocket['"
                commands += self._process_expression(
                                    pocket_node.children[1].children[0])
                commands += "] = "
                commands += self._process_expression(
                                    pocket_node.children[1].children[1])

        elif pocket_node.children[0].children[1].value == "get":
            if len(pocket_node.children[1].children) != 1:
                l = len(pocket_node.children[1].children)
                self._process_error("Adding to the pocket requires" +
                                    " exactly one argument. " +
                                    str(l) + " given.", pocket_node.lineno)
            else:
                commands += "pocket['"
                commands += self._process_expression(
                                    pocket_node.children[1].children[0])
                commands += "]"

        elif pocket_node.children[0].children[1].value == "remove":
            if len(pocket_node.children[1].children) != 1:
                l = len(pocket_node.children[1].children)
                self._process_error("Removing from pocket requires" +
                                    " exactly one argument. " +
                                    str(l) + " given.", pocket_node.lineno)
            else:
                commands += "del pocket['"
                commands += self._process_expression(
                                    pocket_node.children[1].children[0])
                commands += "]"
        else:
            self._process_error("Cannot '" +
                                str(pocket_node.children[0].children[1]) +
                                "' the pocket.", child.children[1].lineno)
        return commands

    def _process_error(self, error, lineno=0):
        if lineno != 0:
            stderr.write("ERROR: Line " + str(lineno) + ": " + str(error) +
                         "\n")
        else:
            stderr.write("ERROR: " + str(error) + "\n")
        exit(1)

    def _process_warning(self, warning, lineno=0):
        if lineno != 0:
            stderr.write("WARNING: Line " + str(lineno) + ": " + str(warning) +
                         "\n")
        else:
            stderr.write("WARNING: " + str(warning) + "\n")
