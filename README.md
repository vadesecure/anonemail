# anonemail

*anonemail* is a script used to anonymize an email, i.e. to remove *Personally Identifiable Information* from the content of the email.

It can be used for instance to anonymize a [spamtrap](https://en.wikipedia.org/wiki/Spamtrap) so that it can be forwarded to third parties without the risk of beeing compromised. 



## Description

*anonemail* extracts all relevant data from *To* header that may identify the recipient: alias, local-part, domain... 

These relevant data are then removed in email headers and body.

Furthermore:

 - Links are anonymized by removing relevant data and tracking tokens.
 - Extended headers are removed. 
 - DKIM fields can be optionally removed.

Other features:

 - Supports the following encodings: 7bit, 8bit,
   [quoted-printable](https://en.wikipedia.org/wiki/Quoted-printable),
   [base64](https://en.wikipedia.org/wiki/Base64).
 - Supports international charsets.



## Dependencies

Requires Python 3.4 or newer.
Also requires [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/).



## How to use the script

For an exhaustive list of available options, use *-h* option:

<code>
$ ./anonemail.py -h
</code>

To send the anonymized version of *myfile.eml* file from *bonnie@clyde.com* to *tips@police.net*:

<code>
$ ./anonemail.py --from bonnie@clyde.com --to tips@police.net -i myfile.eml
</code>

