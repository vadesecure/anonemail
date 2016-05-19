#!/usr/bin/python3
# coding = utf8

import unittest, email, argparse
from anonemail import replace, tokenize_to, clean_token, email_open
from anonemail import create_parser

class TestAnonString(unittest.TestCase):

	def test_replace(self):
		self.assertEqual(
			replace( "aaa bbb", ("aaa", "bbb") ),
				 ("xxx xxx", 2) )

	def test_tokenize(self):
		result = set(["anonemail","project","vade-retro.com"])
		
		self.assertSetEqual(
			tokenize_to("anonemail.project@vade-retro.com"),
				result)

		result = set(["robot","usa-network.com"])

		self.assertSetEqual(
			tokenize_to("mr-robot@usa-network.com"),
				result)

		result = set(["wolfgang","amadeus","mozart","wamoz1756","wien.austria.at"])
		
		self.assertSetEqual(
			tokenize_to("Wolfgang Amadeus Mozart <wamoz1756@wien.austria.at"),
				result)


	def test_clean_token(self):
		self.assertEqual(
			clean_token("<NeedLove>\n"),
			"NeedLove")

class TestAnonEmail(unittest.TestCase):

	def setUp(self):
		self.parser = create_parser()

	def test_email_open(self):
		args = self.parser.parse_args("-i ../corpus/koi8r.eml".split())
		self.assertIsInstance(email_open(args),email.message.Message)


if __name__ == '__main__':
	unittest.main()
