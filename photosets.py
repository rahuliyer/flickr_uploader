#!/usr/bin/python

import auth
import flickrapi
import json

class Photosets:
	def __init__(self, auth):
		self.flickrapi = flickrapi.FlickrApi(auth)
			
	def createGetListRequest(self):
		return self.flickrapi.createAuthenticatedRestGetRequest(
			"flickr.photosets.getList", {});

	def getPhotosetNames(self, response):
		if not flickrapi.FlickrApi.isSuccessfulResponse(response):
			return None

		res = json.loads(response)
		names = []
		for i in res['photosets']['photoset']:
			names.append(i['title']['_content'])
		
		return names
		
	def createNewSetRequest(self, name, description, primary_photo_id):
		return self.flickrapi.createAuthenticatedRestPostRequest(
			"flickr.photosets.create", {"title": name, 
				"description": description, 
				"primary_photo_id": primary_photo_id})	

	def getPhotosetIdFromResult(self, response):
		if not flickrapi.FlickrApi.isSuccessfulResponse(response):
			return None

		res = json.loads(response)

		return res["photoset"]["id"]
	
	def createAddPhotoRequest(self, photo_id, set_id):
		return self.flickrapi.createAuthenticatedRestPostRequest(
			"flickr.photosets.addPhoto", 
			{"photoset_id":	set_id, "photo_id": photo_id})
	
