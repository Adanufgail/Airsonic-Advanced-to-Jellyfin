#!/usr/bin/python3
import configparser
import json
import re
from urllib.request import urlopen
from urllib.parse import quote_plus as ursafe
import random
import string
import hashlib
import xml.etree.ElementTree as ET
from thefuzz import fuzz
from datetime import datetime
import os

'''
VARIABLE DECLARATION
'''
CRED=""
user=""
passa=""
subsonic=""


'''
FUNCTION DECLARATION
'''

# Look for a given credential file in the current directory and the user home directory, and quit if it doesn't exist.
def air_cred_exist(filename):
	if not os.path.exists("./"+filename):
		if not os.path.exists(os.getenv("HOME")+"/"+filename):
			print("Credentials file "+filename+" does not exist")
			quit(1);
		else:
			CRED=os.getenv("HOME")+"/."+filename
	else:
		CRED="./."+filename

#  Read the credentials
def cred_read():
	config=configparser.ConfigParser()
	config.read(CRED)
	user=data.user
	passa=data.passa
	subsonic=data.subsonic
	
