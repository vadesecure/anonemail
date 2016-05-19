from setuptools import setup
 
setup(name='AnonEmail', # nom du projet
      version='1.0',  # version du projet
      description='Tool to remove personal information from body and headers of an email message (anonymization)', # description du projet en une ligne
      author='Vade Retro Technology',
      author_email="support@vade-retro.com",
      url='https://github.com/VadeRetro/tools/tree/master/anonemail',  # url du github
      keywords=["email", "anonymization", "honeypot"], # mettre la liste des keywords associés
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",  # mettre la licence choisie
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
      long_description="""
      Good for quickly transmit samples from an honeypot without compromising it.
Or any other needs ;)

Requires: Python 3.4 or newer for issues with encoding
Beautiful Soup (http://www.crummy.com/software/BeautifulSoup/)

What does it do ?python setup.py sdist upload -r http://testpypi.python.org

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
      """,  
      install_requires=[
        "beautifulsoup4"
      ],
	test_suite = "tests",
      )
