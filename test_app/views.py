from django.shortcuts import render
from rest_framework import viewsets
from test_app.models import Test, ImageModel
from test_app.serializers import TestSerializer, ImageSerializer
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image, ImageOps

import os, sys
import base64
import datetime
import pyimgur
import socket
import threading

import warnings
warnings.filterwarnings("ignore")

sys.path.append("/home/ubuntu/CS492_BackEnd/test_app/")

CLIENT_ID = "bed4f9ee849a845"
thread_queue = dict()

# Create your views here.
class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = ImageModel.objects.all()
    serializer_class = ImageSerializer


def api_test(request, content):
    if request.method == 'POST':
        print("Test - POST")
        ''' 1. Get Image file from content as temp_img_ + date + .jpg '''
        templateId = int(content)
        image_file = request.FILES.get('uploaded_file')
        print("Template_ID: " + str(templateId) + ", File: " + str(request.FILES.get('uploaded_file')))
        filename = 'temp/temp_img_' + str(datetime.datetime.now()) + '.jpg'
        path = default_storage.save(filename, ContentFile(image_file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        print("Requested image Saved")
        print(path)
        ''' 2. Image Processing by using GAN model -- YeJi's part  '''
        new_path = imgProcessing(path, templateId)
        
        
        ''' 3. Send Json Response message containing Processed image (ID picture) '''
        with open(new_path, mode='rb') as file:
            img = file.read()
        data = {'img': base64.encodebytes(img).decode("utf-8")}
        
        if os.path.isfile(path):
            os.remove(path)

        return JsonResponse(data)
    elif request.method == 'GET':
        print("Test - GET")
    return HttpResponse("<http><body>hihihi</body></http>")

def media_test(request, content):
    if request.method == 'POST':
        print("Test - upload")
        image_file = request.FILES.get('uploaded_file')
        filename = 'temp/temp_img_' + str(datetime.datetime.now()) + '.jpg'
        path = default_storage.save(filename, ContentFile(image_file.read()))
        path = os.path.join(settings.MEDIA_ROOT, path)
        print(path)
        thread_queue[path] = ''
        t = threading.Thread(target=imgurRequest, args=(path,))
        t.start()
        t.join()
        imgur_link = thread_queue[path]
        if os.path.isfile(path):
            os.remove(path)
        del thread_queue[path]
        print(imgur_link)
        #data = {'url': upload_image.link}
        data = {'img': imgur_link}
    else:
        print('upload failed')
        data = {'img': 'fail'} 
    return JsonResponse(data, safe=False)

def imgurRequest(path):
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(path, title="test")
    thread_queue[path] = uploaded_image.link
    return

''' Function to process the face image to ID Picture '''
def imgProcessing(path, templateId):
    HOST = '127.0.0.1'
    PORT = 46000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    filename = path.split("/")[-1]
    send_data = filename + "/" + str(templateId)
    client_socket.sendall(send_data.encode())
    new_path = client_socket.recv(1024).decode()
    print('Result -', new_path)
    client_socket.close()
    return new_path

def filpImage(img):
    return ImageOps.flip(img)

''' Delete the temporary file '''
def deleteTemp(path1, path2):
    if os.path.isfile(path1):
        os.remove(path1)
    if os.path.isfile(path2):
        os.remove(path2)
