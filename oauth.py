#!/usr/bin/python

import os
import sys
import json
import os.path as path
import time
import hashlib
import hmac
import base64
import urllib
import urllib2
import urlparse
import random

class OAuth:
	def __init__(self, 
			app_id, 
			app_secret, 
			req_token_url, 
			access_token_url, 
			authorize_cb):
		self.appId = app_id
		self.appSecret = app_secret
		self.requestTokenUrl = req_token_url
		self.accessTokenUrl = access_token_url
		self.authorizeCb = authorize_cb

		self.requestToken = ""
		self.requestTokenSecret = ""
		self.accessToken = ""
		self.accessTokenSecret = ""
		self.authVerifier = ""
	
	def setCredentials(self, access_token, token_secret):
		self.accessToken = access_token
		self.accessTokenSecret = token_secret

	def authenticate(self):
		self.fetchRequestToken()
		self.authorize()
		self.fetchAccessToken()

	def fetchRequestToken(self):
		url = self.requestTokenUrl
		params = {"oauth_callback": "oob"}
		request = self.createOauthRequest("GET", url, params, "", "")
		handler = urllib2.urlopen(request)
		res = urlparse.parse_qs(handler.read())
		self.requestToken = res["oauth_token"][0]
		self.requestTokenSecret = res["oauth_token_secret"][0]

	def authorize(self):
		self.authVerifier = self.authorizeCb(self.requestToken)

	def fetchAccessToken(self):
		url = self.accessTokenUrl
		params = {"oauth_verifier": self.authVerifier}
		request = self.createOauthRequest("GET", 
			url, 
			params, 
			self.requestToken, 
			self.requestTokenSecret)
		handler = urllib2.urlopen(request)
		res = urlparse.parse_qs(handler.read())
		self.accessToken = res["oauth_token"][0]
		self.accessTokenSecret = res["oauth_token_secret"][0]

	def getAccessToken(self):
		return self.accessToken

	def getAccessTokenSecret(self):
		return self.accessTokenSecret

	def createOauthRequest(self, method, url, params, token="", token_secret=""):
		self.addOauthParams(method, url, params, token, token_secret)
		if method == "GET":
			return urllib2.Request(url + "?" + urllib.urlencode(params))
		else:
			return urllib2.Request(url, urllib.urlencode(params))
			

	def addOauthParams(self, method, url, params, token, token_secret):
		ts = int(time.time())
		nonce = str(ts) + str(random.randint(0, sys.maxint))

		if token != "":
			params["oauth_token"] = token

		params["oauth_nonce"] = nonce
		params["oauth_timestamp"] = ts
		params["oauth_consumer_key"] = self.appId
		params["oauth_version"] = "1.0"
		params["oauth_signature_method"] = "HMAC-SHA1"
		params["oauth_signature"] = self.getRequestSignature(
			method, 
			url, 
			params, 
			token_secret)

	def getRequestSignature(self, method, url, params, token_secret = ""):
		base_str = method + "&" + urllib.quote_plus(url) + "&"

		param_str = ""
		for i in sorted(params.keys()):
			param_str += i + "=" + str(params[i]).replace(" ", "+") + "&"

		param_str = urllib.quote_plus(param_str[:-1])
		base_str += param_str

		key = str(self.appSecret + "&" + token_secret)
		sig = hmac.new(key, base_str, hashlib.sha1).digest()

		return base64.b64encode(sig)
