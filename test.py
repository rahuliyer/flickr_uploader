#!/usr/local/bin/python

import urllib, urllib2, sys

from auth import Auth
from photosets import Photosets
from flickrapi import FlickrApi
from httpmultipart import HttpMultipartRequest
from uploader import Uploader
from photos import Photos

def execute(request, test_case):
	try:
		handle = urllib2.urlopen(request)
		response = handle.read()
			
		if not FlickrApi.isSuccessfulResponse(response):
			print test_case + " failed"
			print response
			return None
		else:
			print test_case + " success"
			return response
	except urllib2.HTTPError as e:
		print e.read()
		raise

def run_tests(key, secret):
	try:
		x = Auth(key, secret)
		x.authenticate()
	except urllib2.HTTPError as e:
		print e.read()
		raise

	filename = "/Users/riyer/Desktop/Screen Shot 2013-06-28 at 7.36.02 PM.png"

	f = open(filename, "rb")
	pic = f.read()

	u = Uploader("test_pic", pic, x)
	u.addTitle("test pic")
	u.setPublic()

	req = u.getRequest()
	try:
		handle = urllib2.urlopen(req)
		res = handle.read()
	except urllib2.HTTPError as e:
		print e.read()
		raise

	photo_id = u.getPhotoIdFromResponse(res)

	p = Photosets(x)
	r = p.createGetListRequest()
	res = execute(r, "createGetListRequest")

	names = p.getPhotosetList(res)

	r = p.createNewSetRequest("test set", "test desc", '9404583236')
	res = execute(r, "createNewSetRequest")

	set_id = p.getPhotosetIdFromResult(res)

	r = p.createAddPhotoRequest(photo_id, set_id)
	execute(r, "createAddPhotoRequest")

	r = p.createPhotosetDeleteRequest(set_id)
	execute(r, "createPhotosetDeleteRequest")

	photos = Photos(x)
	r = photos.createDeletePhotoRequest(photo_id)
	execute(r, "createDeletePhotoRequest")

def main():
	if len(sys.argv) != 3:
		sys.stderr.write("Usage: " + sys.argv[0] + " <api key> <api secret>\n")
		sys.exit(1)

	run_tests(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
	main()
