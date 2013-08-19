#!/usr/bin/python
import sys
import os
import os.path as path
import urllib2

from auth import Auth
from photosets import Photosets
from flickrapi import FlickrApi
from httpmultipart import HttpMultipartRequest
from uploader import Uploader
from photos import Photos
from workqueue import WorkQueue

def get_photos(dir):
	files = os.listdir(dir)
	f = lambda x: dir + "/" + x
	
	paths = map(f, files)

	g = lambda x: path.isfile(x) and (x.lower().endswith("jpg") or
		x.lower().endswith('png'))

	photos = filter(g, paths)
	
	return photos

def execute(request):
	handle = urllib2.urlopen(request)
	return handle.read()

def upload_photo(photo, auth):
	while True:
		try:
			f = open(photo, "rb")
			data = f.read()

			u = Uploader(photo, data, auth)
			u.setPublic()
			req = u.getRequest()

			res = execute(req)
			photo_id = u.getPhotoIdFromResponse(res)

			return photo_id
		except urllib2.HTTPError as e:
			pass


def add_to_set(set_id, photo_id, set_controller):
	success = False

	while not success:
		try:
			req = set_controller.createAddPhotoRequest(photo_id, set_id)
			execute(req)

			success = True
		except urllib2.HTTPError as e:
			pass


def create_set(set_name, photo_id, set_controller):
	while True:
		try:
			req = set_controller.createNewSetRequest(set_name,
				set_name, photo_id)
			res = execute(req)
			set_id = set_controller.getPhotosetIdFromResult(res)
			
			return set_id
		except urllib2.HTTPError as e:
			pass

def upload_and_add(photo, set_id, auth, set_controller, ui_wq):
	photo_id = upload_photo(photo, auth)
	add_to_set(set_id, photo_id, set_controller)
	ui_wq.add("Successfully uploaded " + photo)

def print_status(str):
	print str

def upload_photos(set, photos, key, secret):
	try:
		auth = Auth(key, secret)
		auth.authenticate()
	except urllib2.HTTPError as e:
		print e.read()
		raise

	set_controller = Photosets(auth)

	photo_id = upload_photo(photos[0], auth)
	set_id = create_set(set, photo_id, set_controller)

	ui_wq = WorkQueue(print_status, num_workers = 1)
	ui_wq.add("Successfully created set " + set)
	ui_wq.add("Successfully uploaded " + photos[0])

	wq = WorkQueue(upload_and_add, 
		num_workers = 16, 
		max_queue_size = 50, 
		set_id= set_id, 
		auth = auth, 
		set_controller = set_controller,
		ui_wq = ui_wq)

	for photo in photos[1:]:
		wq.add(photo)
	
	wq.done()
	ui_wq.done()

def main():
	if (len(sys.argv) != 5):
		print "Usage: " + sys.argv[0] + " <directory> <album name> <app key> <app secret>"
		sys.exit(1)

	photos = get_photos(sys.argv[1])

	upload_photos(sys.argv[2], photos, sys.argv[3], sys.argv[4])
	
if __name__ == "__main__":
	main()
