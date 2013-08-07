#!/usr/local/bin/python

import urllib, urllib2, sys

from auth import Auth
from photosets import Photosets
from flickrapi import FlickrApi
from httpmultipart import HttpMultipartRequest
from uploader import Uploader

def execute(request, test_case):
	handle = urllib2.urlopen(request)
	response = handle.read()
	if not FlickrApi.isSuccessfulResponse(response):
		print test_case + "failed"
		print response
		return None
	else:
		return response

x = Auth('ad7b7b6be35e8a6acbca6eb897c6dc63', '1fcc24be59b57ba4')
x.authenticate()

filename = "/Users/riyer/Desktop/Screen Shot 2013-06-28 at 7.36.02 PM.png"

f = open(filename, "rb")
pic = f.read()

u = Uploader("test_pic", pic, x)
u.addTitle("test_pic")
u.setPublic()

req = u.getRequest()

handle = urllib2.urlopen(req)
res = handle.read()

photo_id = u.getPhotoIdFromResponse(res)

p = Photosets(x)
r = p.createGetListRequest()
res = execute(r, "createGetListRequest")

names = p.getPhotosetNames(res)
print names

try:
	r = p.createNewSetRequest("test set", "test desc", '9404583236')
	res = execute(r, "createNewSetRequest")
	set_id = p.getPhotosetIdFromResult(res)
	print set_id
except urllib2.HTTPError as e:
	print e.read()
	raise

r = p.createAddPhotoRequest(photo_id, set_id)
execute(r, "createAddPhotoRequest")

#r = p.createPhotosetDeleteRequest(set_id)
#execute(r, "createPhotosetDeleteRequest")

