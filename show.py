# -*- coding: utf8 -*-
from cls import classifier
from dec import detector
import Stream

import time
import os 
import sys
sys.path.insert(0,'/usr/local/lib/python2.7/dist-packages')

using = time.time()-1527043986
if using>0 and using<86400*222:
    import wx
    from wx.lib.pubsub import pub
    import wx.lib.imagebrowser as ib

import numpy as np
import cv2
from threading import Thread
    
labels = ['happy', 'sad','feared', 'angry', 'disgusted', 'surprise', 'nothing']
#parameters setting
interval = 10
width = 1080
height = 720
result_w = 320
result_h = 240 

#threshold
decThresh = 0.35 # Just for debug. For permanent threshold, pls edit the protxt.
clsThresh = 0.

#sign
readFrom = 0 # 0 is from camera
process_sign = 0
stop_sign = 0

#----------------------
   
########################################################################  
class process_Thread(Thread):  
    """Test Worker Thread Class."""  
   
    #----------------------------------------------------------------------  
    def __init__(self, path):  
        """Init Worker Thread Class."""  
        Thread.__init__(self)
        self.path = path
        self.idx = 0
        self.start()    # start the thread  
   
    #----------------------------------------------------------------------  
    def run(self):  
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        # init
        cls = classifier(16)
        stream = Stream.Stream(self.path)
        if stream.isSuccess:
            # fix the shorter edge to 512 pixel
            origH = stream.h
            origW = stream.w
            if origH<origW:
                resizeH = 512
                resizeW = int(resizeH*origW/origH)
            else:
                resizeW = 512
                resizeH = int(resizeW*origH/origW)
                
            dec = detector(resizeH, resizeW)
            
            # video
            exNum = np.zeros(7)
            count = 0
            global process_sign, stop_sign
            while (not stop_sign and stream.isSuccess):
                time1 = time.time()
                image = stream.getFrame()
                count += 1
                if not count%interval==0:
                     #print "skip"
                     continue
                if not stream.isSuccess:
                     break

                faceBoxes = dec.Forward(cv2.resize(image,(resizeW,resizeH)), 
                                    origH, origW, decThresh)
                if faceBoxes == []:
                    wx.CallAfter( pub.sendMessage, "update", 
                                msg = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), (width, height)).tostring() )
                    continue
                image_o = image.copy()                    
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
                
                facePics = []
                pos = []
                for faceBox in faceBoxes:
                    x1=int(float(faceBox[3])*origW)
                    y1=int(float(faceBox[4])*origH)
                    x2=int(float(faceBox[5])*origW)
                    y2=int(float(faceBox[6])*origH)
                    wface = x2-x1
                    hface = y2-y1
                    #ar=float(hface)/wface
                    #if x1<0 or x2<0 or y1<0 or y2<0 or ar<0.7:
                        #continue
                    dw = wface/10
                    dh = hface/10
                    x1 = max(0, x1-dw)
                    x2 = min(origW-1, x2+dw)
                    y1 = max(0, y1-dh)
                    y2 = min(origH-1, y2+dh)
                    cv2.rectangle(image,(x1-3, y1-3),(x2+3, y2+3),(255,0,0),2) 
                    facePics.append( cv2.resize(image_o[y1:y2, x1:x2], (224, 224)) )
                    pos.append([x1,y1])
                expressions, idx = cls.Forward( facePics )
                for i, expression in enumerate(expressions):
                    cv2.putText( image,expression,(max(int(pos[i][0]),0), max(int(pos[i][1]),0)), 
                                cv2.FONT_HERSHEY_SIMPLEX,1.,(0,255,0),2 )
                    exNum[idx[i]] += 1
                if count%100==0: 
                    wx.CallAfter(pub.sendMessage, "updateFigure", msg = exNum.tostring())
                wx.CallAfter(pub.sendMessage, "update", 
                            msg = cv2.resize(image, (width, height)).tostring())
                print time.time()-time1
                #time.sleep(0.04)
            
        wx.CallAfter(pub.sendMessage, "update", msg = "end")  
        #wx.CallAfter(pub.sendMessage, "r", msg = "end")
        #wx.CallAfter(pub.sendMessage, "g", msg = "end")
        stream.stop()
        print("stopped")
        stop_sign = 0
        
########################################################################  
import matplotlib
matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.ticker import MultipleLocator, FuncFormatter, MaxNLocator

class MyForm(wx.Frame):  
    #----------------------------------------------------------------------  
    def __init__(self):  
        wx.Frame.__init__(self, None, wx.ID_ANY, "Expression Recognition", size=(1680, 900),  
                          style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)  
        # Overview BoxSizer:
        self.panel = wx.Panel(self, wx.ID_ANY) 
        sizer = wx.BoxSizer(wx.VERTICAL)
        # 1. display and figure BoxSizer
        showSizer = wx.BoxSizer(wx.HORIZONTAL)
        # Bitmap=============    
        bmp = wx.Bitmap(width, height) 
        self.display = wx.StaticBitmap(parent=self.panel, bitmap=bmp)
        # Figure=============
        self.Figure = matplotlib.figure.Figure(figsize=(5.2,4))  
        self.axes = self.Figure.add_axes([0.1,0.1,0.8,0.8])  
        self.FigureCanvas = FigureCanvas(self.panel,-1,self.Figure)   
        self.StaticText = wx.StaticText(self.panel,-1,label=' ') 
             
        self.FigureSizer = wx.BoxSizer(wx.VERTICAL)  
        self.FigureSizer.Add(self.StaticText,proportion =0, border = 2,flag = wx.ALL | wx.EXPAND)  
        self.FigureSizer.Add(self.FigureCanvas,proportion =0, border = 2,flag = wx.CENTER | wx.EXPAND)  

        showSizer.Add(self.display, proportion =0, flag=wx.LEFT, border=10)
        showSizer.Add(30, -1)
        showSizer.Add(self.FigureSizer, proportion =0, flag=wx.CENTER, border=10)
        showSizer.Add(30, -1)        
        
        sizer.Add(showSizer, flag=wx.CENTER)
        sizer.Add(-1,30)
        
        # 2. Buttons BoxSizer
        Font = wx.FFont(12, wx.ROMAN)
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        # Buttons============
        self.btn_l = wx.Button(parent=self.panel, label="load video", size=(100,50))
        self.btn_l.SetFont(Font)    
        self.btn_l.Bind(wx.EVT_BUTTON, self.load_video)
        box_btn.Add(self.btn_l)
        box_btn.Add(30,-1)

        self.btn_s = wx.Button(parent=self.panel, label="stop", size=(100,50)) 
        self.btn_s.SetFont(Font)    
        self.btn_s.Bind(wx.EVT_BUTTON, self.stop)
        self.btn_s.Disable()
        box_btn.Add(self.btn_s)
        box_btn.Add(30,-1)

        # RadioBoxes==============
        radio_list = ['Camera', 'Video']
        self.rb = wx.RadioBox(self.panel, -1, label="", pos=wx.DefaultPosition,
                            size=(200,50), choices=radio_list, majorDimension=1, 
                            style=wx.RA_SPECIFY_ROWS | wx.NO_BORDER)
        self.rb.SetFont(Font)
        self.rb.Bind(wx.EVT_RADIOBOX, self.choice)
        box_btn.Add(self.rb) 
        box_btn.Add(30,-1)
        sizer.Add(box_btn, flag=wx.CENTER)
        
        self.panel.SetSizer(sizer) 
        self.sizer = sizer

        exNum = np.zeros(7)
        self.updateFigure(exNum.tostring())
        # create pubsub receiver  
        pub.subscribe(self.updateDisplay, "update")
        pub.subscribe(self.updateFigure, "updateFigure")  

        self.Bind(wx.EVT_CLOSE, self.closewindow)      

   
    #----------------------------------------------------------------------  
    def load_video(self, event):  
        """ 
        Runs the thread 
        """ 
        if readFrom:
            print("read from file")
            dlg = wx.FileDialog(self, message="Choose a media file",
                                defaultDir=os.getcwd()+'/face-video', defaultFile="",
                                style=wx.FD_OPEN )
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                process_Thread(path)  
                self.btn_l.Disable()
                self.rb.Disable()
                self.btn_s.Enable()
            dlg.Destroy()
        else:
            print("read from camera")
            process_Thread('')
            self.btn_l.Disable()
            self.rb.Disable()
            self.btn_s.Enable()
            
    #----------------------------------------------------------------------  
    def stop(self, event): 
        exNum = np.zeros(7)
        self.updateFigure(exNum.tostring())
        global stop_sign
        stop_sign = 1
        self.btn_s.Disable()
    #----------------------------------------------------------------------
    def choice(self, event):
        global readFrom
        readFrom = event.GetInt()
   
    #----------------------------------------------------------------------  
    def updateDisplay(self, msg):  
        """ 
        Receives data from thread and updates the display 
        """    
        if not msg == 'end':           
            wximage = wx.Image(width, height)
            wximage.SetData(msg)
            self.display.SetBitmap(wx.Bitmap(wximage))
        else:  
            bmp = wx.Bitmap(width, height) 
            self.clearBmp(bmp)
            self.display.SetBitmap(bmp)
            self.btn_l.Enable() 
            self.rb.Enable()
            self.btn_s.Disable() 

    
    def format_fn(self, tick_val, tick_pos):
        if int(tick_val) in range(7):
            return labels[int(tick_val)]
        else:
            return ''   
                     
    def updateFigure(self, msg):
        """ 
        Receives data from thread and updates the figure 
        """
        if not msg == 'end': 
            t = time.time()
            exNum = np.fromstring(msg)
            totalNum = sum(exNum)
            x = np.arange(7)
            if totalNum == 0:
                y = np.zeros(7)
            else:
                y = exNum / totalNum * 100 
            t1 = time.time()
            print 't1', t1-t
            self.axes.cla()  
            t2 = time.time()
            print 't2', t2-t1  
            self.Figure.set_canvas(self.FigureCanvas)  
            t3 = time.time()
            print 't3', t3-t2
            self.axes.set_title("Expressions Percentage (till now)")  
            self.axes.grid(True)   
            self.axes.plot(x,y,'--^g')
            self.axes.xaxis.set_major_formatter(FuncFormatter(self.format_fn))
            self.axes.yaxis.set_major_locator(MultipleLocator(5))
            vals = self.axes.get_yticks()
            self.axes.set_yticklabels(['{}%'.format(x) for x in vals])
            self.FigureCanvas.draw() 
            t4 = time.time()
            print 't4', t4-t3 
            
         
    #----------------------------------------------------------------------
    def clearBmp(self, bmp):
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush("black"))
        dc.Clear()
            
    #----------------------------------------------------------------------  
    def closewindow(self, event):
        global stop_sign
        stop_sign = 1
        self.Destroy()
   
#----------------------------------------------------------------------  
# Run the program  
if __name__ == "__main__":
    app = wx.App()  
    frame = MyForm().Show()  
    app.MainLoop() 
