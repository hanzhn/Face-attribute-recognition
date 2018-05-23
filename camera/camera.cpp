#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <queue>
#include "boost/python.hpp"
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include "HCNetSDK.h"
#include "iniFile.h"
#include "PlayM4.h"

using namespace std;
using namespace cv;

int lPort=-1;
queue <Mat> framelist;
int width_c=0;
int height_c=0;
int widthStep=0;

void yv12toYUV(char *outYuv, char *inYv12, int width_c, int height_c,int widthStep)
{
	int col,row;
	unsigned int Y=0,U=0,V=0;
	int tmp;
	int idx;
	int WH0=width_c*height_c;
	int WH= WH0+WH0/4;
	for (row=0; row<height_c; row++)
	{
		idx=row * widthStep;
		int rowptr=row*width_c;

		//int RWC= row*width_c;
		int tmp0=(row/2)*(width_c/2);
		for (col=0; col<width_c; col++)
		{
			tmp =tmp0 +(col/2);
			Y=(unsigned int) inYv12[rowptr+col];
			U=(unsigned int) inYv12[WH+tmp];
			V=(unsigned int) inYv12[WH0+tmp];
			if(Y!=0) outYuv[idx+col*3]   = Y;
			if(U!=0) outYuv[idx+col*3+1] = U;
			if(V!=0) outYuv[idx+col*3+2] = V;
		}
	}

}

void CALLBACK DecCBFun(int lPort,char * pBuf,int nSize,
					   FRAME_INFO * pFrameInfo, 
					   void* nReserved1,int nReserved2) 
{
     //---------------------------------------
     if (pFrameInfo->nType == T_AUDIO16)
     {
       printf("test:: get audio data !\n");
      }

     //---------------------------------------
     else if ( pFrameInfo->nType == T_YV12 ) 
     { 
        //printf("test:: get video data !\n");
	char *frameYUV;

	width_c=pFrameInfo->nWidth;
	height_c=pFrameInfo->nHeight;
	if((width_c*3)%4!=0) widthStep=(width_c*3/4+1)*4;
	else widthStep=width_c*3;	
	frameYUV=new char[widthStep*height_c]();
	memset(frameYUV,1,widthStep*height_c*sizeof(char));
	yv12toYUV(frameYUV,pBuf,width_c,height_c,widthStep);
	Mat img;
	Mat imgYUV(height_c,width_c,CV_8UC3,frameYUV,width_c*3);
	cvtColor(imgYUV,img,CV_YUV2RGB);
	framelist.push(img);
     }

}


void CALLBACK PsDataCallBack(LONG lRealHandle, DWORD dwDataType,BYTE *pPacketBuffer,DWORD nPacketSize, void* pUser)
{
        PLAYM4_HWND hWnd=NULL;

	switch (dwDataType)
	{
	case NET_DVR_SYSHEAD:

		if (!PlayM4_GetPort(&lPort)) 
		{
			break;
		}
		if (nPacketSize > 0)
		{
			if (!PlayM4_SetStreamOpenMode(lPort, STREAME_REALTIME))
			{
				break;
			}

			if (!PlayM4_OpenStream(lPort,pPacketBuffer,nPacketSize, 1024*1024))
			{
				break;
			}
			if (!PlayM4_Play(lPort, hWnd)) 
			{
				break;
			}
                        if(!PlayM4_SetDecCallBack(lPort,DecCBFun))
                        {
                                break;
                        }
		}

	case NET_DVR_STREAMDATA:  

		if (nPacketSize > 0 && lPort != -1)
		{

			if (!PlayM4_InputData(lPort,pPacketBuffer,nPacketSize))
			{
				break;
			} 
		}

	}
			

}

void CALLBACK g_ExceptionCallBack(DWORD dwDataType,int iUserID,int lRealHandle,void* pUser)
{
	char tempbuf[256];
        switch(dwDataType)
        {
        case EXCEPTION_RECONNECT:
		printf("--reconnect--%d\n",time(NULL));
		break;
	default:
		break;
	}
}


bool GetStream()
{

	IniFile ini("Device.ini");
	unsigned int dwSize = 0;
	char sSection[16] = "DEVICE";

	
	char *sIP = ini.readstring(sSection, "ip", "error", dwSize);
	int iPort = ini.readinteger(sSection, "port", 0);
	char *sUserName = ini.readstring(sSection, "username", "error", dwSize); 
	char *sPassword = ini.readstring(sSection, "password", "error", dwSize);
	int iChannel = ini.readinteger(sSection, "channel", 0);
		
	NET_DVR_DEVICEINFO_V30 struDeviceInfo;
	int iUserID = NET_DVR_Login_V30(sIP, iPort, sUserName, sPassword, &struDeviceInfo);
     
	NET_DVR_SetExceptionCallBack_V30(0,NULL,g_ExceptionCallBack,NULL);
        int iRealPlayHandle;
	if(iUserID >= 0)
	{

		NET_DVR_PREVIEWINFO struPreviewInfo = {0};
		struPreviewInfo.lChannel =iChannel;
		struPreviewInfo.dwStreamType = 1;
		struPreviewInfo.dwLinkMode = 1;
		struPreviewInfo.bBlocked = 1;
                struPreviewInfo.hPlayWnd = 0;

		iRealPlayHandle = NET_DVR_RealPlay_V40(iUserID, &struPreviewInfo, PsDataCallBack, NULL);
		if(iRealPlayHandle >= 0)
		{
			printf("[GetStream]---RealPlay %s:%d success, \n", sIP, iChannel);
			sleep(1);
            return true;
		}
		else
		{
			printf("[GetStream]---RealPlay %s:%d failed, error = %d\n", sIP, iChannel, NET_DVR_GetLastError());
			sleep(1);
			return false;
		}
	}
	else
	{
		printf("[GetStream]---Login %s failed, error = %d\n", sIP, NET_DVR_GetLastError());
		sleep(1);
		return false;
	}
}


int get_width()
{
	return width_c;
}

int get_height()
{
	return height_c;
}

bool transinit()
{
	NET_DVR_Init();

    return GetStream();
}

string get_frame()
{
	Mat frame;
	if (framelist.empty()) return "";
	frame=framelist.front();
	string sframe((char *)frame.data, frame.cols*frame.rows*3);
	framelist.pop();
	return sframe;
}
void clear(queue<Mat>& q) {
    queue<Mat> empty;
    swap(empty, q);
}
void transclose()
{
	clear(framelist);
	NET_DVR_Cleanup();
}

BOOST_PYTHON_MODULE(camera)
{
using namespace boost::python;
def("transinit",transinit);
def("get_frame",get_frame);
def("get_width",get_width);
def("get_height",get_height);
def("transclose",transclose);
}




