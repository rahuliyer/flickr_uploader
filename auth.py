#!/usr/bin/python

import os
import sys
import json
import os.path as path
import urllib2
import urllib

import oauth

AUTH_TOKEN_FILE = "~/.flickr_token"
REQUEST_TOKEN_URL = "http://www.flickr.com/services/oauth/request_token"
AUTHORIZE_URL = "http://www.flickr.com/services/oauth/authorize"
ACCESS_TOKEN_URL = "http://www.flickr.com/services/oauth/access_token"

class Auth:
	def __init__(self, app_id, app_secret):
		self.appId = app_id
		self.appSecret = app_secret
		self.oauth = oauth.OAuth(app_id,
			app_secret, 
			REQUEST_TOKEN_URL, 
			ACCESS_TOKEN_URL, 
			self.authorizeCb)

	def authorizeCb(self, request_token):
		url = AUTHORIZE_URL + "?oauth_token=" + request_token
		print "Please go to " + url + " to authorize the app."
		return raw_input("Enter the verifier on the page: ")

	def authenticate(self):
		creds = None
		try:
			creds = self.readAuthToken()
		except:
			pass

		if creds != None:
			self.oauth.setCredentials(creds["token"], creds["secret"])
		else:
			self.oauth.authenticate()
			self.writeToken(self.oauth.getAccessToken(), 
				self.oauth.getAccessTokenSecret())
		print self.oauth.getAccessToken()
		print self.oauth.getAccessTokenSecret()

	def getAppId(self):
		return self.appId

	def signRequest(self, request):
		params = request.getParams()
		self.oauth.addOauthParams(request.getMethod(), 
			request.getUrl(),
			params,
			self.oauth.getAccessToken(),
			self.oauth.getAccessTokenSecret())

	def writeToken(self, token, token_secret):
		d = { "token": token, "secret": token_secret }
		serialized_str = json.dumps(d)

		try:
			fd = os.open(path.expanduser(AUTH_TOKEN_FILE), 
				os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0600)
			handle = os.fdopen(fd, "w")
			handle.write(serialized_str)
			handle.close()

		except:
			sys.stderr.write("Error writing token to file!\n")
			raise

	def readAuthToken(self):
		file_path = path.expanduser(AUTH_TOKEN_FILE)
		if not path.exists(file_path):
			return None

		try:
			handle = open(file_path, "r")
			data = handle.read()
			return json.loads(data)
		except:
			sys.stderr.write("Error reading token from token file")
			raise

