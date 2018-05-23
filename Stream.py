import numpy as np
import cv2
import camera

class Stream():
    
    def __init__(self, path):
        self.path = path
        if self.path == '':
            self.fromCamera = True
            self.fromVideo = False
            self.isSuccess = camera.transinit()
            print self.isSuccess
            if self.isSuccess:
                self.w = camera.get_width()
                self.h = camera.get_height()
            else:
                print('camera error')
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
        while True:
            frame = camera.get_frame()
            if frame != "":
                break
        frame = np.fromstring(frame,np.uint8).reshape(self.h,self.w,3)
        #cv2.imshow('video', frame)
        #cv2.waitKey(10)
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
                camera.transclose()

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
