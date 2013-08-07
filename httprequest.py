#!/usr/bin/python

class HttpRequest:
	def addParam(name, value, type):
		raise NotImplementedError
	
	def getRequest():
		raise NotImplementedError

	def getSignedRequest():
		raise NotImplementedError
		
	def getParams():
		raise NotImplementedError

	def getMethod():
		raise NotImplementedError
	
	def getUrl():
		raise NotImplementedError
