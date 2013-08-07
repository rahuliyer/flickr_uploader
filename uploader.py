#!/usr/bin/python

from httpmultipart import HttpMultipartRequest

import xml.etree.ElementTree as et

class Uploader:
	def __init__(self, filename, data, auth):
		self.auth = auth
		self.data = data
		self.params = {}
		self.filename = filename

	def addTitle(self, title):
		self.params["title"] = title

	def addDescription(self, desc):
		self.params["description"] = desc
	
	def setPublic(self):
		self.params["is_public"] = 1

	def getRequest(self):
		r = HttpMultipartRequest("http://api.flickr.com/services/upload/",
			self.params, self.auth)

		r.addBody(self.filename, "photo", self.data, "image/jpeg")
		return r.getSignedRequest()

	def getPhotoIdFromResponse(self, response):
		root = et.fromstring(response)
		if root.attrib['stat'] != "ok":
			return None

		return root.find("photoid").text
