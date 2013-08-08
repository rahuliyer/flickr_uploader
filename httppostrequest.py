#!/usr/bin/python

import urllib
import urllib2

from httprequest import HttpRequest

class HttpPostRequest(HttpRequest):
	def __init__(self, url, params, auth):
		self.url = url
		self.params = params
		self.auth = auth

	def addParam(self, name, value, type=''):
		self.params[name] = value

	def getParams(self):
		return self.params

	def getMethod(self):
		return "POST"

	def getUrl(self):
		return self.url

	def getRequest(self):
		return urllib2.Request(self.url, HttpRequest.urlencode(self.params))
	
	def getSignedRequest(self):
		self.auth.signRequest(self)
		return self.getRequest()
