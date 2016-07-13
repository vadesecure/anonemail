#!/usr/bin/python3
 
"""
Copyright (c) 2015 "Vade Secure"
anonemail is an email anonymization script
This file is part of anonemail.
anonemail is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import email,smtplib,re, urllib, io
import argparse,sys,base64, quopri, random
from bs4 import BeautifulSoup
from email.parser import BytesFeedParser
from email.header import decode_header,Header
try:
    from mailoutstream import FileMailOutStream, SMTPMailOutStream
except ImportError:
    from python.mailoutstream import FileMailOutStream, SMTPMailOutStream

# Separators for getting user "parts" as in name.surname@email.tld or name_surname@email.tld
USERSEP = re.compile("[._-]")
# Separators for multiple/list of emails
# eg: in the To field
TKENSEP = re.compile("[ ,;]")
# List of emails used
FROMADDR="from@email.tld"
FWDADDR = "sampling@email.tld"
ERRADDR = "oops@email.tld"
SMPADDR = "sampling@email.tld"
# Server to forward anonymized messages to
SRVSMTP = "localhost"
# Recipient Headers
RCPTHDR = ("To", "Cc", "Bcc", "Delivered-To", "X-RCPT-To")
# Custom headers to anonymize (List Id…)
CSTMHDR = ("X-Mailer-RecptId",)
# Headers to decode before tokenizing (RFC 2822)
CODDHDR = ("To", "Cc", "Subject") 

addr_rgx = re.compile("for ([^;]+);") # to clean received headers
url_rgx = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

def replace(text, elmts):
	""" Find tokens in part and replace them """
	count = 0
	for elmt in elmts:
		ins_elmt = re.compile(re.escape(elmt), re.IGNORECASE)
		text, c = ins_elmt.subn(ano_x(elmt), text)
		count = count + c
	return text, count

def ano_x(str):
	""" Replace a string by 'xxxx' """
	return re.sub(r'\w', 'x', str)

	
def tokenize_to(to):
	""" Parse the To field and extract elements that should be anonymized """
	emails = set()
	tokens = set()
	
	# Get both aliases and email addresses
	fields  = TKENSEP.split(to.lower())
	for token in fields:
		token = clean_token(token)
		if '@' in token:
			emails.add(token)
		elif len(token) != 0:
			tokens.add(token)
			
	# For every email address, extract element of interest (name, surname, domain…)
	for email in emails:
		fulluser, todom = email.split('@',1)
		for user_part in USERSEP.split(fulluser, 4):
			if len(user_part) > 2: 
				tokens.add(user_part)
		tokens.add(todom)
		
	return tokens
	
def clean_token(t):
	""" Clean token from unwanted character """
	return t.strip('<>" \n\t')
	
def error(msg, error_msg, out_streams):
	""" Forward message to the error handling email address """
	if msg.get('Subject') is not None:
		subj = "[ " + error_msg + " ] " + msg.get("Subject")
		msg.replace_header("Subject", subj)

	for stream in out_streams:
		stream.send_error(msg)
	exit(1)

def get_dest(msg, orig_to):
	""" Find the recipient(s) """
	dest = []

	# Find all recipients in the RCPTHDR fields
	for hdr in RCPTHDR:
		if msg.get(hdr) is not None and '@' in msg.get(hdr):
			
			if hdr in CODDHDR:
				dcd_hdr = decode_hdr(msg.get_all(hdr))
				dest.extend(dcd_hdr)
			else:
				dest.extend(msg.get_all(hdr))
	

	# If no To nor Cc, we look for recipient into the received
	if orig_to is None:
		for rcvd in msg.get_all('Received', []):
			dest.extend(addr_rgx.findall(rcvd,re.IGNORECASE))
	else:
		dest.extend(orig_to)

	return dest

def decode_hdr(dest):
	""" Decode non-ASCII header fields """
	dcd_dest = []

	for i in dest:
		for b, charset in decode_header(i):
			# Dirty hack - if bytes
			if isinstance(b, bytes):
				dcd_str = b.decode(charset) if charset != None else b.decode()
				dcd_dest.append(clean_token(dcd_str))
			# or string (because Python returns both)
			else:
				dcd_dest.append(clean_token(b))
			
	return dcd_dest

def encode_part(part, charset = "utf-8" , cte = None):
	""" Reencode part using Content-Transfer-Encoding information """
	donothing = [ '7bit', '8bit', 'binary' ]
	encoders = { "base64": base64.b64encode, \
			"quoted-printable": quopri.encodestring }

	if cte is None:
		return part
	if cte.lower() in donothing:
		return part
	elif cte.lower() in encoders:
		buffer = part.encode(charset, errors='replace')
		coded_str = encoders[cte.lower()](buffer)
		return coded_str.decode()
	else:
		return "!ERR!"
		
def url_replace(text):
	""" Replace tokens inside urls """
	
	urlz = url_rgx.finditer(text)
	for url in urlz:
		url_object = urllib.parse.urlparse(url.group(0))
		if url_object.query is not "":
			new_url = url_ano_params(url_object)
			text = text[:url.start()] + new_url + text[url.end():]
	
	return text
	
def url_ano_params(url):
	""" Replace every parameter in URLs """
	new_query = []
	for query in urllib.parse.parse_qsl(url.query):
		new_query.append((query[0], ano_x(query[1])))
		new_url = urllib.parse.urlunparse((url[0], url[1], url[2], url[3], urllib.parse.urlencode(new_query), url[5]))
		
	return new_url
	
def url_replace_html(html):
	""" Parse HMTL and extract URLs """
	
	soup = BeautifulSoup(html, "html.parser")
	for tag in soup.findAll('a', href=True):
		url = tag['href']
		o = urllib.parse.urlparse(url)
		if o.query is not "":
			new_url = url_ano_params(o)
			tag['href'] = new_url
		
	return str(soup)

def email_open(args):
	""" Read the file descriptor and return a msg file """
	p=email.parser.BytesFeedParser()
	if args.stdin or args.infile is None:
		input = io.BufferedReader(sys.stdin.buffer)
	else:
		input = open(args.infile, 'rb')
	p.feed(input.read())
	msg = p.close()
	input.close()

	# Check for invalid (0 bytes) message
	if len(msg) == 0:
		error(msg, "Invalid Message", out_streams)
	else:
		return msg

def anon_part(part, elmts):
	""" Process part to anonymize """
	charset = part.get_content_charset()

	# If there is a charset, we decode the content
	if charset is None:
		payload = part.get_payload()
		new_load = replace(payload, elmts)[0]
	else:
		payload = part.get_payload(decode=True).decode(charset)
		new_load = replace(payload, elmts)[0]

	# URL anonymization
	if part.get_content_subtype() == 'plain':
		new_load = url_replace(new_load)
	elif part.get_content_subtype() == 'html':
		new_load = url_replace_html(new_load)
	
	# Encoding back in the previously used encoding (if any)
	cdc_load = encode_part(new_load, charset, part.get('content-transfer-encoding'))
	if cdc_load == "!ERR!":
		error(msg, "Encoding error", out_streams)
	else:
		part.set_payload(cdc_load)
	return part

def ano_coddhdr(msg, coddhdr, elmts):
	""" Anonymize internationalized headers """
	anohdr = []
	for b, charset in decode_header(msg.get(coddhdr)):
		
		if charset != None:
			dcd_hdr = b.decode(charset)
			dcd_hdr, count = replace(dcd_hdr, elmts)
			anohdr.append((dcd_hdr , charset))
		elif isinstance(b,str):
			anohdr.append((b, charset))
		else:
			anohdr.append((b.decode(), charset))

	return anohdr

def create_parser():
	""" Define every options for argument parsing """
	parser = argparse.ArgumentParser(description='')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-', help="Read from standard input", dest='stdin', action='store_true')
	group.add_argument('-i','--infile', help="Read from a file (eml/plain text format)", nargs='?')
	parser.add_argument('--server', dest='srvsmtp', help="SMTP server to use", default=SRVSMTP)
	parser.add_argument('--from', dest='from_addr', help="Sender address", default=FROMADDR)
	parser.add_argument('--to', dest='to_addr', help="Recipient address", default=FWDADDR)
	parser.add_argument('--orig-to', dest='orig_to', help="To used in SMTP transaction", nargs='*', default=None)
	parser.add_argument('--err', dest='err_addr', help="Error handling address", default=ERRADDR)
	parser.add_argument('--sample', dest='smpl_addr', help="Sampling address", default=SMPADDR)
	parser.add_argument('--no-dkim', dest='no_dkim', help="Remove DKIM fields", action='store_true')
	parser.add_argument('-s', '--anonymise-sender', dest="is_sender_anon", action="store_true", default=False)
	parser.add_argument('--no-mail', dest="send_mail", action="store_false", default=True,help="Tels the program not to send anonymized mail to smtp server")
	parser.add_argument('--to-file', dest="to_file", default=False, action="store_true",
				help="Send a copy of anonymized mail to a file must be used with at least --dest-dir and --error-dir")
	parser.add_argument('--dest-dir', dest="dest_dir", default=None)
	parser.add_argument('--error-dir', dest="error_dir", default=None)


	return parser

def get_streams(args):
	out_streams = []
	if args.send_mail:
		out_streams.append(SMTPMailOutStream(args.from_addr, args.to_addr, args.err_addr, args.smpl_addr,SRVSMTP, True))
	if args.to_file:
        	out_streams.append(FileMailOutStream(args.dest_dir, args.error_dir, args.sample_dir, args.sample_dir is not None))
	if len(out_streams) == 0:
		print("You can't use --no-mail without --to-file")
		exit()

	return out_streams

def get_newmsg(msg,elmts):
	""" Build the new, anonymized messaged and encode it correctly """
	# Concatenate the anonymized headers with anonymized body = BOUM ! anonymized email !
	hdr_end = msg.as_string().find('\n\n')
	if hdr_end == -1:
		error(msg, "No neck", out_streams)
	else:
		hdr = msg.as_string()[:hdr_end]
		new_hdr = url_replace(hdr)
		(new_hdr, count) = replace(new_hdr,elmts)
		new_msg = new_hdr + msg.as_string()[hdr_end:]

		
	## Force reencoding to avoid issues during sending with Python SMTP Lib
	if msg.get_content_charset() is not None:
		new_msg = new_msg.encode(msg.get_content_charset(), errors='replace')
	else:
		for charset in msg.get_charsets():
			if charset is not None:
				new_msg = new_msg.encode(charset, errors='replace')
				break
	return new_msg

def clean_hdr(msg, args, elmts):
	""" Anonymize headers """
	# Looking for custom header to clean
	for cstmhdr in CSTMHDR:
		if cstmhdr in msg.keys():
			msg.replace_header(cstmhdr, ano_x(msg.get(cstmhdr)))

	# Anonmyzation of encoded headers
	for coddhdr in CODDHDR:
		if coddhdr in msg.keys():
			anohdr = ano_coddhdr(msg, coddhdr, elmts)
			msg.replace_header(coddhdr, email.header.make_header(anohdr))

	# If defined, clean DKIM fields
	if args.no_dkim:
		del msg["DKIM-Signature"]
		del msg["DomainKey-Signature"]
	
	return msg

def main():
	global args, out_streams
	
	parser = create_parser()
	args = parser.parse_args()
	out_streams = get_streams(args)
	msg = email_open(args)

	# Grab recipient from To field
	dest = get_dest(msg, args.orig_to)
	if len(dest) == 0:
		error(msg, "No explicit To", out_streams)
	
	# Get tokens from recipient
	elmts = set()
	for d in dest:
		elmts.update(tokenize_to(d))
	elmts = sorted(elmts, key=str.__len__, reverse = True)
	
	# Main part - loop on every part of the email
	for part in msg.walk():
		if not part.is_multipart() and part.get_content_maintype() == 'text':
			part = anon_part(part, elmts)
		else:
			part = part

	# Clean headers
	msg = clean_hdr(msg, args, elmts)

	new_msg = get_newmsg(msg, elmts)

	s = smtplib.SMTP(args.srvsmtp)
	
	# Sampling part 
	if random.randint(0,10) == 0:
		for stream in out_streams:
			stream.send_sample(new_msg)

	# Send final message 
	for stream in out_streams:
			stream.send_success(new_msg)

	s.quit()
	exit(0)


if __name__ == '__main__':
    main()
