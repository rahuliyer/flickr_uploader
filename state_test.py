#!/usr/bin/python

import unittest
import os

import flickr_uploader
from checkpoint import Checkpoint

class TestActionsStateMachine(unittest.TestCase):
	TEST_DIR = "/tmp/state_test"
	TEST_KEY = "test_key"

	def setUp(self):
		os.mkdir(TestActionsStateMachine.TEST_DIR)
		self.cp = Checkpoint(TestActionsStateMachine.TEST_DIR)
		self.cp.createCheckpointLog(TestActionsStateMachine.TEST_KEY)

	def tearDown(self):
		os.system("rm -rf " + TestActionsStateMachine.TEST_DIR)

	def testBasic(self):
		actions = flickr_uploader.get_actions("photo", "set", self.cp)[0]

		self.assertTrue(actions & flickr_uploader.UPLOAD_PHOTO)
		self.assertTrue(actions & flickr_uploader.CREATE_SET)
		self.assertFalse(actions & flickr_uploader.ADD_TO_SET)

	def testSetCreation(self):
		self.cp.writeCheckpoint(TestActionsStateMachine.TEST_KEY, "photo",
			{"status": flickr_uploader.PHOTO_UPLOADED, "photo_id": 3})

		res = flickr_uploader.get_actions("photo", "set", self.cp)
		actions = res[0]
		data = res[1]

		self.assertTrue(actions & flickr_uploader.CREATE_SET)
		self.assertFalse(actions & flickr_uploader.UPLOAD_PHOTO)
		self.assertFalse(actions & flickr_uploader.ADD_TO_SET)

		self.assertEquals(3, data["photo_id"])

	def testUploadAndAdd(self):
		self.cp.writeCheckpoint(TestActionsStateMachine.TEST_KEY, "photo",
			{"status": flickr_uploader.PHOTO_UPLOADED, "photo_id": 3})

		self.cp.writeCheckpoint(TestActionsStateMachine.TEST_KEY, "set",
			{"status": flickr_uploader.SET_CREATED, "set_id": 3})

		self.cp.writeCheckpoint(TestActionsStateMachine.TEST_KEY, "photo",
			{"status": flickr_uploader.ADDED_TO_SET})

		res = flickr_uploader.get_actions("photo2", "set", self.cp)
		actions = res[0]
		data = res[1]

		self.assertFalse(actions & flickr_uploader.CREATE_SET)
		self.assertTrue(actions & flickr_uploader.UPLOAD_PHOTO)
		self.assertTrue(actions & flickr_uploader.ADD_TO_SET)

		self.assertEquals(3, data["set_id"])

	def testAddToSet(self):
		self.cp.writeCheckpoint(TestActionsStateMachine.TEST_KEY, "photo",
			{"status": flickr_uploader.PHOTO_UPLOADED, "photo_id": 3})

		self.cp.writeCheckpoint(TestActionsStateMachine.TEST_KEY, "set",
			{"status": flickr_uploader.SET_CREATED, "set_id": 3})

		self.cp.writeCheckpoint(TestActionsStateMachine.TEST_KEY, "photo",
			{"status": flickr_uploader.ADDED_TO_SET})

		self.cp.writeCheckpoint(TestActionsStateMachine.TEST_KEY, "photo2",
			{"status": flickr_uploader.PHOTO_UPLOADED, "photo_id": 4})
		
		res = flickr_uploader.get_actions("photo2", "set", self.cp)
		actions = res[0]
		data = res[1]

		self.assertFalse(actions & flickr_uploader.CREATE_SET)
		self.assertFalse(actions & flickr_uploader.UPLOAD_PHOTO)
		self.assertTrue(actions & flickr_uploader.ADD_TO_SET)

		self.assertEquals(3, data["set_id"])
		self.assertEquals(4, data["photo_id"])

if __name__ == "__main__":
	unittest.main()

