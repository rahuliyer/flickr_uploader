import os
import os.path as path
import time
import json

class Checkpoint:
	def __init__(self, dir):
		self.checkpointState = {}
		self.checkpointLogs = {}

		self.checkpoint_dir = dir + "/.checkpoint"

		if path.exists(self.checkpoint_dir):
			files = os.listdir(self.checkpoint_dir)
			f = lambda x: self.checkpoint_dir + "/" + x

			paths = map(f, files)

			for i in paths:
				self.processFiles(i)
		else:
			os.mkdir(self.checkpoint_dir)

	def updateState(self, key, value):
		state = []
		if key in self.checkpointState:
			state = self.checkpointState[key]

		state.append(value)
		self.checkpointState[key] = state

	def processFiles(self, file):
		f = open(file, "r")
		
		while True:
			line = f.readline()
			if line == '':
				break

			checkpoint = json.loads(line)
			key = checkpoint.keys()[0]
			self.updateState(key, checkpoint[key])

		f.close()

	def createCheckpointLog(self, key):
		checkpoint_file = key + str(int(time.time()))
		f = open(self.checkpoint_dir + "/" + checkpoint_file, "wb+")

		self.checkpointLogs[key] = f
	
	def releaseCheckpointLog(self, key):
		self.checkpointLogs[key].close()
		del self.checkpointLogs[key]
	
	def writeCheckpoint(self, log_key, key, value):
		f = self.checkpointLogs[log_key]
		f.write(json.dumps({key: value}) + "\n")
		self.updateState(key, value)

	def getCheckpointLogKeys(self):
		return self.checkpointLogs.keys()

	def getCheckpointKeys(self):
		return self.checkpointState.keys()

	def getCheckpoints(self, key):
		if key not in self.checkpointState:
			return []

		return self.checkpointState[key]
