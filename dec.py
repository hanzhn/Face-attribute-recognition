#encoding:utf-8
import cv2
import numpy as np

from time import time
import caffe

def getOver(faces, thresh):
    #print faces
    #print type(faces)
    if faces[-1,2] < thresh:
        print("HZwarning: If U are debugging with thresh, after debugging, pls set the final threshold in prototxt to speed up!")
        overPart = faces[ faces[:,2] >= thresh ]
        if overPart.shape[0] == 0:
            return []
        else:
            return overPart
    else:
        return faces

def getLargest(faces):
    if faces.shape[0] == 1:
        return faces[0]
    else:
        ws = faces[:,5] - faces[:,3]
        hs = faces[:,6] - faces[:,4]
        ss = ws * hs
        return faces[ss.argmax()]
# caffe init
net = caffe.Net('model/deploy.prototxt', 
                'model/VGG_WIDER_FACE_ZYQ_iter_50000.caffemodel', caffe.TEST)      
class detector():
    def __init__(self, h, w):
        # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
        net.blobs['data'].reshape(1,3,h,w)      # set net to batch size of 1
        self.transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
        self.transformer.set_transpose('data', (2,0,1))
        #transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
        #transformer.set_mean('data', np.load('out.npy').mean(1).mean(1)) # mean pixel
        #transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB
            
    # Network forward thread
    def Forward(self, img, w, h, thresh):
        caffe.set_mode_gpu()
        t = time()
        print w, h
        #print self.transformer.preprocess('data',img).shape
        net.blobs['data'].data[0,:,:] = self.transformer.preprocess('data',img)
        net.forward()
        data = net.blobs["detection_out"].data
        print 'Dec forward time:', time()-t
        
        flatten = data[0,0,:,:]
        num = flatten.shape[0]
        th = thresh
        recs = getOver(flatten, th)
        return recs
        #==============================
        if recs==[]:
            return 0,0,0,0,0.
        rec = getLargest(recs)

        x1=int(float(rec[3])*w)
        y1=int(float(rec[4])*h)
        x2=int(float(rec[5])*w)
        y2=int(float(rec[6])*h)
        wface = x2-x1
        hface = y2-y1
        #ar=float(hface)/wface
        #if x1<0 or x2<0 or y1<0 or y2<0 or ar<0.7:
            #continue
        dw = wface/10
        dh = hface/10
        x1 = max(0, x1-dw)
        x2 = min(w-1, x2+dw)
        y1 = max(0, y1-dh)
        y2 = min(h-1, y2+dh)
        #print x1, x2, y1, y2, rec[2]

        return x1, y1, x2, y2, rec[2]


if __name__ == '__main__':
    d = detector(300,300)
    f = open("/home/smiles/hz/databases/FDDB/FDDB-folds/FDDB-fold-all.txt", 'r')
    line = f.readline().strip('\n')
    while(line):
        img = cv2.imread("/home/smiles/hz/databases/FDDB/image/"+line+".jpg")
        origH = img.shape[0]
        origW = img.shape[1]
        if origH<origW:
            resizeH = 512
            resizeW = int(resizeH*origW/origH)
        else:
            resizeW = 512
            resizeH = int(resizeW*origH/origW)

        img = cv2.resize(img,(resizeW,resizeH))
        d.Forward(img, origW, origH, 0.2)
        line = f.readline().strip('\n')
