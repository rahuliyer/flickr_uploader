#!/usr/bin/python

import auth
import flickrapi
import json

class Photosets:
	def __init__(self, auth):
		self.flickrapi = flickrapi.FlickrApi(auth)
			
	def createGetListRequest(self):
		return self.flickrapi.createRestGetRequest(
			"flickr.photosets.getList", {}, True);

	def getPhotosetList(self, response):
		if not flickrapi.FlickrApi.isSuccessfulResponse(response):
			return None

		res = json.loads(response)
		sets = {}
		for i in res['photosets']['photoset']:
			sets[i['id']] = i['title']['_content']

		return sets
		
	def createNewSetRequest(self, name, description, primary_photo_id):
		return self.flickrapi.createRestPostRequest(
			"flickr.photosets.create", {"title": name, 
				"description": description, 
				"primary_photo_id": primary_photo_id}, True)	

	def getPhotosetIdFromResult(self, response):
		if not flickrapi.FlickrApi.isSuccessfulResponse(response):
			return None

		res = json.loads(response)

		return res["photoset"]["id"]
	
	def createAddPhotoRequest(self, photo_id, set_id):
		return self.flickrapi.createRestPostRequest(
			"flickr.photosets.addPhoto", 
			{"photoset_id":	set_id, "photo_id": photo_id},
			True)

	def createPhotosetDeleteRequest(self, set_id):
		return self.flickrapi.createRestPostRequest(
			"flickr.photosets.delete",
			{"photoset_id": set_id},
			True)
