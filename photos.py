#!/usr/bin/python

import flickrapi

class Photos:
	def __init__(self, auth):
		self.flickrapi = flickrapi.FlickrApi(auth)
	
	def createDeletePhotoRequest(self, photo_id):
		return self.flickrapi.createRestPostRequest(
			"flickr.photos.delete",
			{"photo_id": photo_id},
			True)

