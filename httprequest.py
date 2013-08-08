#!/usr/bin/python

import urllib

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
	
	@staticmethod
	def urlencode(param_dict):
		param_str = ""
		
		for i in param_dict.keys():
			param_str += str(i) + "=" + urllib.quote(str(param_dict[i])) + "&"

		return param_str[:-1]
