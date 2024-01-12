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
Airsonic-Advanced-To-Jellyfin
Version 0.0.1
Author: Michael Lubert (Adanufgail@Github)
Date: 2024-01-11
'''

'''
TODO:

Airsonic:
	Pull all song directories into array
	Pull Playlists

Jellyfin:
	Connect To Jellyfin API
	Confirm how API returns song paths
	Find song by path?
	Star songs
	Create playlists and add songs to them
'''


'''
TWEAKABLES
'''

cred_filename="credentials"

'''
FUNCTION DELCARATION
'''

# Look for a given credential file in the current directory and the user home directory, and quit if it doesn't exist.

def cred_exist(filename):
	global cred
	if not os.path.exists(filename):
		if not os.path.exists(os.getenv("HOME")+"/"+filename):
			print("Credentials file "+filename+" does not exist")
			quit(1);
		else:
			cred=os.getenv("HOME")+"/"+filename
	else:
		cred=filename

#  Read the credentials

def cred_read():
	config=configparser.ConfigParser()
	config.read(cred)
	
	global air
	global jel
	
	jel=config["jellyfin"]
	air=config["airsonic"]

# Generate a random token to use when connecting to Airsonic

def token_gen():
	global salt
	global token
	salt='%030x' % random.randrange(16**30)
	cram=air["pass"]+salt
	token=hashlib.md5(cram.encode()).hexdigest()

# Use Airsonic REST API to run "command"

def airsonic_rest(page,args):
	url = air["url"]+"/rest/"+page+"?v=1.15.0&c=python&username="+air["user"]+"&u="+air["user"]+"&s="+salt+"&t="+token+args
	print(url)
	data = urlopen(url)
	usable=ET.fromstring(data.read())
	return usable


'''
MAIN PROGRAM LOGIC
'''

# Get Config File

cred_exist(cred_filename)
cred_read()


# Connect to Airsonic and pull all starred songs

token_gen() #this only needs to be called once per session
astar_raw=airsonic_rest("getStarred2","")
astar=astar_raw[0]

# Get file path for each song
# This is the raw path, based on the Airsonic configured directory (ie "ARTIST/Album/Song.mp3" and not /media/music/ARTIST/Album/Song.mp3"

#for stared in astar: #Add this back in for all songs, debug below for one to get formatting right
song_raw=airsonic_rest("getSong","&id="+astar[0].attrib["id"])
print(song_raw[0].attrib["path"]);
