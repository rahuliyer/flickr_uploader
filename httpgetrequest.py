#!/usr/bin/python

import urllib
import urllib2

from httprequest import HttpRequest

class HttpGetRequest(HttpRequest):
	def __init__(self, url, params, auth):
		self.url = url
		self.params = params
		self.auth = auth
	
	def addParam(self, name, value, type=''):
		self.params[name] = value

	def getParams(self):
		return self.params

	def getMethod(self):
		return "GET"

	def getUrl(self):
		return self.url

	def getRequest(self):
		url = self.url + "?" + HttpRequest.urlencode(self.params)
		return urllib2.Request(url)
	
	def getSignedRequest(self):
		self.auth.signRequest(self)
		return self.getRequest()
