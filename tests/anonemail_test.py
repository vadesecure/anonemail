#!/usr/bin/python3
# coding = utf8

import unittest, email, argparse, sys, glob, random
from python.anonemail import replace, tokenize_to, clean_token, email_open
from python.anonemail import create_parser, get_dest, decode_hdr, url_replace
from python.anonemail import anon_part, encode_part

class TestAnonString(unittest.TestCase):

	def test_replace(self):
		self.assertEqual(
			replace( "aaa bbb", ("aaa", "bbb") ),
				 ("xxx xxx", 2) )

	def test_tokenize(self):
		result = set(["anonemail", "project", "vade-retro.com"])
		
		self.assertSetEqual(
			tokenize_to("anonemail.project@vade-retro.com"),
				result)

		result = set(["robot","usa-network.com"])

		self.assertSetEqual(
			tokenize_to("mr-robot@usa-network.com"),
				result)

		result = set(["wolfgang","amadeus","mozart","wamoz1756","wien.austria.at"])
		
		self.assertSetEqual(
			tokenize_to("Wolfgang Amadeus Mozart <wamoz1756@wien.austria.at>"),
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

	def test_url_replace(self):
 
                self.assertEqual(
                        url_replace("Look what I found: https://encrypted.google.com/search?hl=fr&q=love%20your%20email !"),
                        "Look what I found: https://encrypted.google.com/search?hl=xx&q=xxxx+xxxx+xxxxx !")

class TestAnonEmail(unittest.TestCase):

	def setUp(self):
		self.parser = create_parser()

		# randomEmail take a random eml file in corpus folder
		emails = glob.glob("corpus/*.eml")
		self.random_email = random.choice(emails)

	def test_email_open(self):
		args = self.parser.parse_args(["-i", self.random_email])
		self.assertIsInstance(email_open(args),email.message.Message)

	def test_get_dest(self):
		args = self.parser.parse_args("-i corpus/toinbody.eml".split())
		msg = email_open(args)
		self.assertListEqual(
			["foo.bar@phonydomain.fr"],
			get_dest(msg, ""))

	def test_anon_part(self):
		args = self.parser.parse_args("-i corpus/multipart.eml".split())
		msg = email_open(args)
		for part in msg.walk():
			if not part.is_multipart() and part.get_content_maintype() == 'text':
				part = anon_part(part, ("pamela","green","phonydomain.fr"))
				self.assertNotRegex(part.get_payload(), "pamela")
				self.assertNotRegex(part.as_string(), "green")
				self.assertNotRegex(part.as_string(), "phonydomain")

	def test_url_replace(self):
		args = self.parser.parse_args("-i corpus/multipart.eml".split())
		msg = email_open(args)
		for part in msg.walk():
			if not part.is_multipart() and part.get_content_maintype() == 'text':
				self.assertNotRegex(
					url_replace(part.get_payload()),
					"\=[^x]")

	def test_encode_part(self):
		args = self.parser.parse_args( ["-i", self.random_email] )
		msg = email_open(args)
		for part in msg.walk():
			if not part.is_multipart() and part.get_content_maintype() == 'text':
				self.assertNotEqual(
					encode_part(part, part.get_content_charset(), part.get("content-transfer-encoding")),
					"!ERR!")

if __name__ == '__main__':
	unittest.main()
