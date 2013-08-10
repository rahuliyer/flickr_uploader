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
		creds = {}
		try:
			creds = self.readAuthToken()
		except:
			pass
		
		if len(creds.keys()) != 0 and creds["app_id"] == self.appId and \
				creds["app_secret"]	== self.appSecret:
			self.oauth.setCredentials(creds["token"], creds["token_secret"])
		else:
			self.oauth.authenticate()
			self.writeToken(self.appId,
				self.appSecret,
				self.oauth.getAccessToken(), 
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

	def writeToken(self, app_id, app_secret, token, token_secret):
		d = { "app_id": app_id, 
			"app_secret": app_secret, 
			"token": token, 
			"token_secret": token_secret }
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
			return {}

		try:
			handle = open(file_path, "r")
			data = handle.read()
			dict = json.loads(data)

			if "app_id" not in dict or "app_secret" not in dict or \
					"token" not	in dict or "token_secret" not in dict:
				return {} 

			return dict
		except:
			sys.stderr.write("Error reading token from token file")
			raise

