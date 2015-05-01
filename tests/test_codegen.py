import narratr.parser as parser
import narratr.codegen as codegen
import unittest
import subprocess


class TestCodeGen(unittest.TestCase):

    def test_codegen_helloworld(self):

        """Test that Hello World code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/0_helloworld.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Hello, World!\n'
        self.assertEqual(real_output, expected_output,
                         "Hello World is messed up.")

    def test_codegen_comments(self):

        """Test that Comments code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/1_comments.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Hello.\n'
        self.assertEqual(real_output, expected_output,
                         "Comments is messed up.")

    def test_codegen_conliterals(self):

        """Test that Constant/Literals code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/1_constantsliterals.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = '3\n3.3\nHello.\n'
        self.assertEqual(real_output, expected_output,
                         "Constants/Literals is messed up.")

    def test_codegen_derived(self):
        pass

    def test_codegen_list(self):

        """Test that List code can be generated"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/1_constantsliterals.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct()

    def test_codegen_andor(self):

        """Test that And/Or code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/3_andor.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Okay.\nOkay.\n'
        self.assertEqual(real_output, expected_output,
                         "And/or is messed up.")

    def test_codegen_arithmetic(self):

        """Test that Arithmetic code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/3_arithmetic.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = '2\n4\n4\n3\n3\n'
        self.assertEqual(real_output, expected_output,
                         "Arithmetic is messed up.")

    def test_codegen_assignment(self):

        """Test that Assignment code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/3_assignment.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Oh, hello.\n'
        self.assertEqual(real_output, expected_output,
                         "Assignment is messed up.")

    def test_codegen_comparison(self):

        """Test that Comparison code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/3_comparison.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Okay.\nOkay.\nOkay.\nOkay.\n'
        self.assertEqual(real_output, expected_output,
                         "Comparison is messed up.")

    def test_codegen_break(self):

        """Test that Break code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/4_break.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Okay.\nOkay.\n'
        self.assertEqual(real_output, expected_output,
                         "Break is messed up.")

    def test_codegen_continue(self):

        """Test that Continue code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/4_continue.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = '0\n2\n'
        self.assertEqual(real_output, expected_output,
                         "Continue is messed up.")

    def test_codegen_elseif(self):

        """Test that Else/If code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/4_elseif.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Okay.\n'
        self.assertEqual(real_output, expected_output,
                         "Else/if is messed up.")

    def test_codegen_exposition(self):

        """Test that Exposition code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/4_exposition.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Sadness is infinite.\n'
        self.assertEqual(real_output, expected_output,
                         "Exposition is messed up.")

    def test_codegen_for(self):

        """Test that For code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/4_for.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = '0\n1\n2\n'
        self.assertEqual(real_output, expected_output,
                         "For is messed up.")

    def test_codegen_if(self):

        """Test that If code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/4_if.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Okay.\n'
        self.assertEqual(real_output, expected_output,
                         "If is messed up.")

    def test_codegen_truefalse(self):

        """Test that True/False code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/4_truefalse.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Okay.\n'
        self.assertEqual(real_output, expected_output,
                         "True/False is messed up.")

    def test_codegen_while(self):

        """Test that While code can be generated and is correct"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/4_while.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct('temp.py')

        real_output = subprocess.check_output(['python', 'temp.py'])
        expected_output = 'Okay.\nOkay.\nOkay.\n'
        self.assertEqual(real_output, expected_output,
                         "While is messed up.")

    def test_codegen_moves(self):

        """Test that Moves code can be generated"""
        p = parser.ParserForNarratr()
        with open('sampleprograms/5_moves.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        c.process(ast, symtab)
        c.construct()

    def test_parser_nonexistent_start_scene(self):

        """Test that codegen has error for nonexistent_start_scene."""
        p = parser.ParserForNarratr()
        with open('sampleprograms/6_nonexistent_start_scene.ntr') as f:
            ast = p.parse(f.read())
        symtab = p.symtab
        c = codegen.CodeGen()
        self.assertRaises(Exception, lambda: c.process(ast, symtab))
