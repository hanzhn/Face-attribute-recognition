import numpy as np
import cv2
import camera
from utils import ParameterReader

#cameraIP = "192.168.10.235"
#userName = "admin"
#password = "smile627"
#cameraIP = 192.168.10.235
#cameraUserName = admin
#cameraPassword = smile627


class Stream():
	
	def __init__(self, path):
		self.path = path

		if self.path == '':
			self.fromCamera = True
			self.fromVideo = False
			paraReader = ParameterReader("cameraInfo.txt")
			cameraIP = paraReader.getData("cameraIP")
			cameraPort = int( paraReader.getData("cameraPort") )
			cameraUserName = paraReader.getData("cameraUserName")
			cameraPassword = paraReader.getData("cameraPassword")
#			self.isSuccess = camera.transinit("192.168.10.235", 8000, "admin", "smile627")
			self.isSuccess = camera.transinit(cameraIP, cameraPort, cameraUserName, cameraPassword)
			print self.isSuccess
			if self.isSuccess:
				w = camera.get_width()
				h = camera.get_height()
				while w <=0:
					print("w=%d, h=%d"%(w,h))
					w = camera.get_width()
				while  h <=0:
					print("w=%d, h=%d"%(w,h))
					h = camera.get_height()
				self.w = w
				self.h = h
			else:
				print('camera error')
			print("--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>--->>>>")
		else:
			self.fromCamera = False
			self.fromVideo = True
			self.video = cv2.VideoCapture(self.path)
			self.isSuccess, image = self.video.read()
			if self.isSuccess:
				self.h = image.shape[0]
				self.w = image.shape[1]
			else:
				print("video error")

	def getFrameFromCamera(self):
		frame = camera.get_frame()
		while len(frame)<=0:
			frame = camera.get_frame()
		frame = np.fromstring(frame,np.uint8).reshape(self.h, self. w,3)
		return frame

	def getFrameFromVideo(self):
		self.isSuccess, image = self.video.read()
		return image
		
	def getFrame(self):
		if not self.isSuccess:
			return None
		if self.fromCamera:
			return self.getFrameFromCamera()
		else:
			return self.getFrameFromVideo()
	def stop(self):
		if self.isSuccess:
			if self.fromCamera:
				pass
'''
if __name__ == "__main__":
	camera.transinit()
	w = camera.get_width()
	h = camera.get_height()
	while True:
		frame = camera.get_frame()
		if frame == "":
			continue
		frame = np.fromstring(frame,np.uint8).reshape(h,w,3)
		cv2.imshow('video', frame)
		cv2.waitKey(10)

	camera.closeinit()
'''
