g++ -fPIC -shared camera.cpp -o ../camera.so -I/usr/include/python2.7 -I/usr/local/include -I./ -L../HCNetSDKCom -L/usr/local/lib -Wl,-rpath=./HCNetSDKCom:/usr/local/lib -lhcnetsdk  -lPlayCtrl -lAudioRender -lSuperRender -lboost_python-py27 -lopencv_highgui  -lopencv_core -lopencv_imgproc -lopencv_video -lviplnet -O3 -std=c++11
