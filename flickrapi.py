#!/usr/bin/python

import auth

import json

class FlickrApi:
	def __init__(self, auth):
		self.auth = auth

	def addApiArgs(self, method, args):
		args["method"] = method
		args["format"] = "json"
		args["nojsoncallback"] = 1
		args["api_key"] = self.auth.getAppId()

	def createRestGetRequest(self, method, args):
		self.addApiArgs(method, args)
		return self.auth.createGetRequest("http://api.flickr.com/services/rest", args)

	def createRestPostRequest(self, method, args):
		self.addApiArgs(method, args)
		return self.auth.createPostRequest("http://api.flickr.com/services/rest", args)

	def createAuthenticatedRestGetRequest(self, method, args):
		self.addApiArgs(method, args)
		return self.auth.createOauthGetRequest("http://api.flickr.com/services/rest", args)

	def createAuthenticatedRestPostRequest(self, method, args):
		self.addApiArgs(method, args)
		return self.auth.createOauthPostRequest("http://api.flickr.com/services/rest", args)

	@staticmethod
	def isSuccessfulResponse(response):
		res = json.loads(response)
		if res["stat"] != "ok":
			return false

		return True
