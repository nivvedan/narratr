import narratr.parser as parser
import unittest


class TestParserForStatements(unittest.TestCase):

    def test_parser_break(self):

        """Test that parser can parse break"""
        ast = ""

        p = parser.ParserForNarratr()
        with open('sampleprograms/4_break.ntr') as f:
            ast = str(p.parse(f.read()))

    def test_parser_continue(self):

        """Test that parser can parse continue."""
        ast = ""

        p = parser.ParserForNarratr()
        with open('sampleprograms/4_continue.ntr') as f:
            ast = str(p.parse(f.read()))

    def test_parser_elseif(self):

        """Test that parser can parse else/if."""
        ast = ""

        p = parser.ParserForNarratr()
        with open('sampleprograms/4_elseif.ntr') as f:
            ast = str(p.parse(f.read()))

    def test_parser_exposition(self):

        """Test that parser can parse exposition."""
        ast = ""

        p = parser.ParserForNarratr()
        with open('sampleprograms/4_exposition.ntr') as f:
            ast = str(p.parse(f.read()))

    def test_parser_if(self):

        """Test that parser can parse if."""
        ast = ""

        p = parser.ParserForNarratr()
        with open('sampleprograms/4_if.ntr') as f:
            ast = str(p.parse(f.read()))

    def test_parser_truefalse(self):

        """Test that parser can parse true/false."""
        ast = ""

        p = parser.ParserForNarratr()
        with open('sampleprograms/4_truefalse.ntr') as f:
            ast = str(p.parse(f.read()))

    def test_parser_while(self):

        """Test that parser can parse while."""
        ast = ""

        p = parser.ParserForNarratr()
        with open('sampleprograms/4_while.ntr') as f:
            ast = str(p.parse(f.read()))
