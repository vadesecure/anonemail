#!/usr/bin/python3
# coding = utf8

import unittest, email, argparse, sys, os.path
from python.anonemail import replace, tokenize_to, clean_token, email_open
from python.anonemail import create_parser, get_dest, decode_hdr

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

	def test_decode_hdr(self):

		self.assertListEqual(
			decode_hdr(["=?iso-8859-1?q?p=F6stal?="]),
			["pöstal"])

		self.assertListEqual(
			decode_hdr(["=?UTF-8?B?U1VI5bqD5aCx5a6j5Lyd6YOo44CA56eL5ZCJ?=\
 <akiyoshi@yolo.co.jp>", "suh@yolo.jp"]),
			["SUH広報宣伝部\u3000秋吉", "akiyoshi@yolo.co.jp", "suh@yolo.jp"])

class TestAnonEmail(unittest.TestCase):

	def setUp(self):
		self.parser = create_parser()

	def test_email_open(self):
		args = self.parser.parse_args("-i corpus/koi8r.eml".split())
		self.assertIsInstance(email_open(args),email.message.Message)

	def test_get_dest(self):
		args = self.parser.parse_args("-i corpus/toinbody.eml".split())
		msg = email_open(args)
		self.assertListEqual(
			["foo.bar@phonydomain.fr"],
			get_dest(msg, ""))


if __name__ == '__main__':
	unittest.main()
