#!/usr/bin/python3
import configparser
import json
import re
#from urllib.request import urlopen
import urllib.request
from urllib.parse import quote as ursafe
import random
import string
import hashlib
import xml.etree.ElementTree as ET
from thefuzz import fuzz
from datetime import datetime
import os

'''
Airsonic-Advanced-To-Jellyfin
Version 0.0.2
Author: Michael Lubert (Adanufgail@Github)
Date: 2024-01-12
'''

'''
TODO:

Airsonic:
	Pull Playlists

Jellyfin:
	Confirm the same song in Jellyfin and Subsonic
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

def air_token_gen():
	global air_salt
	global air_token
	air_salt='%030x' % random.randrange(16**30)
	cram=air["pass"]+air_salt
	air_token=hashlib.md5(cram.encode()).hexdigest()

# Use Airsonic REST API to run "command"

def airsonic_rest(page,args):
	url = air["url"]+"/rest/"+page+"?v=1.15.0&c=python&username="+air["user"]+"&u="+air["user"]+"&s="+air_salt+"&t="+air_token+args
	data = urllib.request.urlopen(url)
	usable=ET.fromstring(data.read())
	return usable

def airsonic_starred():
	global air_stars

	# Connect to Airsonic and pull all starred songs
	air_token_gen() #this only needs to be called once per session
	astar_raw=airsonic_rest("getStarred2","")
	astar=astar_raw[0]
	air_stars = {}

	# Parse each entry for the Artist/Album/Title/Track
	for song in astar:
		sid=song.attrib["id"]
		air_stars[sid]={}
		air_stars[sid]["title"]=song.get("title","")
		air_stars[sid]["artist"]=song.get("artist","")
		air_stars[sid]["album"]=song.get("album","")
		air_stars[sid]["track"]=song.get("track","")
		

def jellyfin_rest(page,args="NULL",http_method="GET"):
	# Log In with Username Code
	if page == "Users/AuthenticateByName":
		login = { "Username" : jel["user"], "Pw" : jel["pass"] }
		login = json.dumps(login)
		login = str(login)
		login = login.encode('utf-8')
		url = jel["url"]+"/"+page
		hdr = { 
			"Content-Type" : "application/json",
			"accept" : "application/json",
         "x-emby-authorization":'MediaBrowser Client="Jellyfin CLI",Device="Jellyfin-CLI", DeviceId="None", Version="10.8.0"'
		}
		req = urllib.request.Request(url,headers=hdr,data=login,method="POST")
		data = urllib.request.urlopen(req)
		usable=data.read()
		usable = json.loads(usable)
	# Normal Page Loading
	else:
		if(args=="NULL"):
			url = jel["url"]+"/"+page
		else:
			url = jel["url"]+"/"+page+"?"+args
		hdr = { 
			"accept" : "application/json",
         "x-emby-authorization":'MediaBrowser Client="Jellyfin CLI",Device="Jellyfin-CLI", DeviceId="None", Version="10.8.13"',
			"accept" : "application/json",
			"x-mediabrowser-token": jel_token
		}
		req = urllib.request.Request(url,headers=hdr,method=http_method)
		data = urllib.request.urlopen(req)
		usable=json.loads(data.read())
	return usable

def jellyfin_gettoken():
	global jel_token
	global jel_uid
	
	# Log In and get AccessToken
	jel_token = jellyfin_rest("Users/AuthenticateByName","","POST")["AccessToken"]
	jel_uid = jellyfin_rest("Users/AuthenticateByName","","POST")["User"]["Id"]
	

def jellyfin_findsong(title,band,album="",track=""):
	args="recursive=true&includeItemTypes=Audio&userId="+jel_uid+"&artists="+ursafe(band)+"&searchTerm="+ursafe(title)
	# Find a song by Title, Artist, and Album (if available). Will then cross reference Track Number (if available)
	if(album!=""):
		args=args+"&albums="+ursafe(album)
	#if(track!=""):
	#	args=args+"&track="+ursafe(album)
	return jellyfin_rest("Users/"+jel_uid+"/Items",args,"GET")
	
def jellyfin_favoritesong(songid):
	jellyfin_rest("Users/"+jel_uid+"/FavoriteItems/"+songid,"","POST")

def jellyfin_getsong(songid):
	return jellyfin_rest("Users/"+jel_uid+"/Items/"+songid,"","GET")


'''
MAIN PROGRAM LOGIC
'''

def main():
	# Get Config File

	cred_exist(cred_filename)
	cred_read()
		
	airsonic_starred()
	jellyfin_gettoken()

	new_fave=jellyfin_findsong(air_stars[astar]["title"],air_stars[astar]["artist"],air_stars[astar]["album"],air_stars[astar]["track"])
	#for astar in air_stars:
		#new_fave=jellyfin_findsong(air_stars[astar]["title"],air_stars[astar]["artist"],air_stars[astar]["album"],air_stars[astar]["track"])
		#try:
		#	jel_id=new_fave["Items"][0]["Id"]
		#except:
		#	print("DEUBG: "+air_stars[astar]["title"]+" - "+air_stars[astar]["artist"]+" - "+air_stars[astar]["album"]+" - "+air_stars[astar]["track"])
		#	print(new_fave)
		#jellyfin_favoritesong(jel_id)
	

main()
