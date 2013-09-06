#!/usr/bin/python
import sys
import os
import os.path as path
import urllib2
import threading

from auth import Auth
from photosets import Photosets
from flickrapi import FlickrApi
from httpmultipart import HttpMultipartRequest
from uploader import Uploader
from photos import Photos
from workqueue import WorkQueue
from checkpoint import Checkpoint

# Checkpoint events
SET_CREATED = 1
PHOTO_UPLOADED = 2
ADDED_TO_SET = 3

# actions
CREATE_SET = 0x1
UPLOAD_PHOTO = 0X2
ADD_TO_SET = 0X4

thread_local = threading.local()
def get_checkpoint_key(checkpoint):
	key = getattr(thread_local, "checkpoint_key", "")
	if key == "":
		key = threading.current_thread().getName()
		checkpoint.createCheckpointLog(key)
		thread_local.checkpoint_key = key

	return key

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

def get_set_list(set_controller):
	while True:
		try:
			req = set_controller.createGetListRequest()
			res = execute(req)
			sets = set_controller.getPhotosetList(res)
			
			return sets
		except urllib2.HTTPError as e:
			pass

def create_set_if_needed(set, photo_id, set_controller):
	sets = get_set_list(set_controller)
	found_set_id = 0
	res = {}
	set_id = 0

	for id in sets:
		if set == sets[id]:
			found_set_id = id
			break

	if found_set_id != 0:
		print "Found set with name " + sets[found_set_id] + \
			". Add to existing set? (y/N)"
		reply = raw_input()

		if reply == 'y':
			 res["set_id"] = found_set_id
			 res["msg"] = "Using existing set " + sets[found_set_id]
			 add_to_set(found_set_id, photo_id, set_controller)
			 return res
			 
	res["set_id"] = create_set(set, photo_id, set_controller)
	res["msg"] = "Successfully created set " + set

	return res
		
def get_actions(photo, set, checkpoint):
	data = {}
	actions = CREATE_SET | UPLOAD_PHOTO

	set_cp = checkpoint.getCheckpoints(set)
	for cp in set_cp:
		if cp["status"] == SET_CREATED:
			data["set_id"] = cp["set_id"]
			actions &= ~CREATE_SET
			actions |= ADD_TO_SET
	
	photo_cp = checkpoint.getCheckpoints(photo)
	for cp in photo_cp:
		if cp["status"] == PHOTO_UPLOADED:
			data["photo_id"] = cp["photo_id"]
			actions &= ~UPLOAD_PHOTO

		if cp["status"] == ADDED_TO_SET:
			actions &= ~ADD_TO_SET
	
	return [actions, data]

def upload_and_add(photo, set, auth, set_controller, ui_wq, checkpoint):
	res = get_actions(photo, set, checkpoint)
	actions = res[0]
	data = res[1]

	checkpoint_key = get_checkpoint_key(checkpoint)

	photo_id = 0
	if actions & UPLOAD_PHOTO:
		photo_id = upload_photo(photo, auth)
		checkpoint.writeCheckpoint(checkpoint_key, photo,
			{"status": PHOTO_UPLOADED, "photo_id": photo_id})
		ui_wq.add("Successfully uploaded " + photo)
	else:
		photo_id = data["photo_id"]
	
	assert photo_id != 0

	if actions & CREATE_SET:
		res = create_set_if_needed(set, photo_id, set_controller)
		set_id = res["set_id"]
		msg = res["msg"]
		checkpoint.writeCheckpoint(checkpoint_key, set,
			{"status": SET_CREATED, "set_id": set_id})
		ui_wq.add(msg)
	elif actions & ADD_TO_SET:
		set_id = data["set_id"]
		add_to_set(set_id, photo_id, set_controller)

	checkpoint.writeCheckpoint(checkpoint_key, photo,
		{"status": ADDED_TO_SET})
	ui_wq.add("Successfully added " + photo + " to " + set)

def print_status(str):
	print str

def upload_photos(set, photos, key, secret, checkpoint):
	try:
		auth = Auth(key, secret)
		auth.authenticate()
	except urllib2.HTTPError as e:
		print e.read()
		raise

	set_controller = Photosets(auth)

	# Work queue to print upload status
	ui_wq = WorkQueue(print_status, num_workers = 1)

	upload_and_add(photos[0], set, auth, set_controller, ui_wq, checkpoint)

	wq = WorkQueue(upload_and_add, 
		num_workers = 16, 
		max_queue_size = 50, 
		set = set, 
		auth = auth, 
		set_controller = set_controller,
		ui_wq = ui_wq,
		checkpoint = checkpoint)

	for photo in photos[1:]:
		wq.add(photo)
	
	wq.done()
	ui_wq.done()

def main():
	if (len(sys.argv) != 5):
		print "Usage: " + sys.argv[0] + " <directory> <album name> <app key> <app secret>"
		sys.exit(1)

	dir = sys.argv[1]
	checkpoint = Checkpoint(dir)

	photos = get_photos(dir)

	upload_photos(sys.argv[2], photos, sys.argv[3], sys.argv[4], checkpoint)
	
if __name__ == "__main__":
	main()
