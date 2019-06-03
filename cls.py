#encoding:utf-8
import cv2
import numpy as np

from time import time
import caffe

# caffe init
expressions = ['happy', 'sad','feared', 'angry', 'disgusted', 'surprise', 'nothing']


class classifier():
    def __init__(self, b):
        self.batchsize = b
        
        self.net = caffe.Net('model/test_vgg.prototxt', 'model/_iter_5000.caffemodel', caffe.TEST)
        # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
        self.net.blobs['data'].reshape(b,3,224,224)      # set net to batch size of 1
        self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
        self.transformer.set_transpose('data', (2,0,1))
        #transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
        self.transformer.set_mean('data',np.array((104.0, 117.0, 123.0), dtype=np.float32) ) # mean pixel
        #transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB      
        
    # Network forward thread
    def Forward(self, images):
        caffe.set_mode_gpu()
        t = time()
        
        batchsize = self.batchsize
        imgNum = len(images)
        batchNum = int(imgNum / batchsize)
        residualNum = imgNum % batchsize
        results = np.zeros( (imgNum, len(expressions)) )
        
        if batchNum > 0:
            self.net.blobs['data'].reshape(batchsize,3,224,224)
        for i in range(batchNum):
            for j in range(batchsize):
                self.net.blobs['data'].data[j,:,:] = self.transformer.preprocess('data',images[i*batchsize+j])
            self.net.forward()
            results[ i*batchsize : (i+1)*batchsize ] = self.net.blobs["prob"].data
            
        if residualNum > 0:
            self.net.blobs['data'].reshape(residualNum,3,224,224)
        for j in range(residualNum):
            self.net.blobs['data'].data[j,:,:] = self.transformer.preprocess('data',images[batchNum*batchsize+j])
            if j+1 >= residualNum:
                #print(net.blobs['data'].data[35],net.blobs['data'].data[34],net.blobs['data'].data[63])
                self.net.forward()
                #print(net.blobs["prob"].data[35],net.blobs["prob"].data[34],net.blobs['prob'].data[63])
                results[ batchNum*batchsize : ] = self.net.blobs["prob"].data[:residualNum]
        print 'Cls forward time:', time()-t
        idx = np.argmax(results, axis = 1)
        
        #expression = expressions[ np.where(data == np.max(data))[0][0] ]
        return np.asarray(expressions)[idx], idx

if __name__ == '__main__':
    batch = 2
    totalFaces = 128
    
    cls = classifier(batch)
    f = open("/home/smiles/hz/databases/FDDB/FDDB-folds/FDDB-fold-all.txt", 'r')
    line = f.readline().strip('\n')
    #for i in range(4):
    imgs = []
    
    cnt = 0
    timeAll = 0
    while(line):
        img = cv2.imread("/home/smiles/hz/databases/FDDB/image/"+line+".jpg")
        img = cv2.resize(img,(224,224))
        imgs.append(img)
        if len(imgs) < totalFaces:
            line = f.readline().strip('\n')
            continue
        else:
            cnt += 1
            ts = time()
            cls.Forward(imgs)
            if cnt > 1:
                timeAll += time()-ts
                print 'ave time: ', timeAll/(cnt-1)
            imgs = []
            line = f.readline().strip('\n')
        
        
        
        
        
        
        
        
