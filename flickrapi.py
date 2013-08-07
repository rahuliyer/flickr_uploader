#!/usr/bin/python

import auth
from httpgetrequest import HttpGetRequest
from httppostrequest import HttpPostRequest

import json

class FlickrApi:
	def __init__(self, auth):
		self.auth = auth

	def addApiArgs(self, method, args):
		args["method"] = method
		args["format"] = "json"
		args["nojsoncallback"] = 1
		args["api_key"] = self.auth.getAppId()

	def createRestGetRequest(self, method, args, sign = False):
		self.addApiArgs(method, args)
		req = HttpGetRequest("http://api.flickr.com/services/rest",
			args,
			self.auth)

		if sign:
			return req.getSignedRequest()
		else:
			return req.getRequest()

	def createRestPostRequest(self, method, args, sign = False):
		self.addApiArgs(method, args)
		req = HttpPostRequest("http://api.flickr.com/services/rest",
			args,
			self.auth)
		if sign:
			return req.getSignedRequest()
		else:
			return req.getRequest()

	@staticmethod
	def isSuccessfulResponse(response):
		res = json.loads(response)
		if res["stat"] != "ok":
			return False

		return True
