== Simple python tool to quickly anonymize email ==

Good for quickly transmit samples from an honeypot without compromising it.
Or any other needs ;)

Requires: Python 3.4 or newer for issues with encoding
Beautiful Soup (http://www.crummy.com/software/BeautifulSoup/)

What does it do ?

Look for recipients in headers, tokenize them to extract surname or every other info and replace token in body and headers.
Also:
— replace parameters in URLs for encoded versions of recipients or tracking number
— remove custom tracking headers (X-Something:…)
— remove DKIM fiels (optional)

Features:
— manage encoding or international charsets
— manage encoded headers
— forward to an error address in case of failure
— sampling included if you want to look after the result

How to use it ?

For an exhaustive list of options, just append --help to the programme

$ ./anohp.py --help

To send the anonymized version of an eml file from bonnie@clyde.com to tips@police.net

./anohp.py --from bonnie@clyde.com --to tips@police.net -i myfile.eml



