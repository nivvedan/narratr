from parser import ParserForNarratr
import unittest


class TestParser(unittest.TestCase):

	def test_parser_helloworld(self):
		"""Test that parser can parse helloworld."""
		ast = ""
		correct_ast = ""
		with open('tests/parsed_helloworld') as f:
			correct_ast = f.read()
		p = ParserForNarratr()
		with open('sampleprograms/helloworld.ntr') as f:
			ast = str(p.parse(f.read()))
		self.assertEqual(ast, correct_ast, "ruh roh")

if __name__ == "__main__":
	unittest.main()