#!/usr/bin/python

import urllib
import urllib2
import random
import string

from httprequest import HttpRequest

class HttpMultipartRequest(HttpRequest):
	def __init__(self, url, params, auth):
		self.url = url
		self.params = params
		self.paramTypes = {}
		self.auth = auth
		
	def addParam(self, name, value, type=''):
		self.params[name] = value
		self.paramTypes[name] = type

	def addBody(self, filename, name, data, type):
		self.bodyFileName = filename
		self.bodyFieldName = name
		self.bodyData = data
		self.bodyType = type

	def getParams(self):
		return self.params

	def getParamTypes(self):
		return self.paramTypes

	def getMethod(self):
		return "POST"

	def getUrl(self):
		return self.url

	def createBoundary(self):
		boundary_size = 64
		boundary = ""

		for i in range(boundary_size):
			boundary += random.choice(string.ascii_lowercase +
			string.ascii_uppercase + string.digits)

		return boundary

	def createMultipartBody(self, boundary):
		data = ""

		for i in sorted(self.params.keys()):
			data += "--" + boundary + "\r\n"
			data += "Content-Disposition: form-data; name=\"" + i + "\"\r\n\r\n"
			data += str(self.params[i]) + "\r\n"
		
		data += "--" + boundary + "\n"
		data += "Content-Disposition: form-data; name=\"" + \
			self.bodyFieldName + \
			"\"; filename=\"" + \
			self.bodyFileName + \
			"\"\r\n"
		
		data += "Content-Type: " + self.bodyType + "\r\n"
		data += "Content-Transfer-Encoding: binary\r\n\r\n"
		data += self.bodyData
		data += "\r\n"
		data += "--" + boundary + "--"

		return data

	def getRequest(self):
		req = urllib2.Request(self.url, urllib.urlencode(self.params))
	
		boundary = self.createBoundary()
		body = self.createMultipartBody(boundary)
		body_len = len(body)

		req.add_data(body)
		req.add_header("Content-Type",
			"multipart/form-data; boundary=" + boundary)
		req.add_header("Content-Length", body_len)

		return req

	def getSignedRequest(self):
		self.auth.signRequest(self)

		# Egregious hack :( Flickr doesn't seem to support oauth in
		# parameters for multipart
		auth_header_val = "OAuth "
		for i in ("oauth_consumer_key", "oauth_nonce", "oauth_signature",
			"oauth_signature_method", "oauth_timestamp", "oauth_token",
			"oauth_version"):
			auth_header_val += i + "=\"" + str(self.params[i]) + "\", "
			del self.params[i]

		auth_header_val = auth_header_val[:-1]
		req = self.getRequest()
		req.add_header("Authorization", auth_header_val)

		return req
