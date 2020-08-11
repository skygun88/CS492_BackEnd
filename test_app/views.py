from django.shortcuts import render
from rest_framework import viewsets
from test_app.models import Test, ImageModel
from test_app.serializers import TestSerializer, ImageSerializer
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image, ImageOps
import os
import base64
import datetime


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
        ''' 2. Image Processing by using GAN model -- YeJi's part  '''
        new_path = imgProcessing(tmp_file, templateId)
        ''' 3. Send Json Response message containing Processed image (ID picture) '''
        with open(new_path, mode='rb') as file:
            img = file.read()
        data = {'img': base64.encodebytes(img).decode("utf-8")}
        #print(data['img'][:30])
        deleteTemp(tmp_file, new_path)
        return JsonResponse(data)
    elif request.method == 'GET':
        print("Test - GET")
    return HttpResponse("<http><body>hihihi</body></http>")

''' Function to process the face image to ID Picture '''
def imgProcessing(path, templateId):
    filename = path.split('/')[-1]
    print(path)
    img = Image.open(path)
    im_flip = filpImage(img)
    new_filename = path.replace(filename, 'temp_processed_') + str(datetime.datetime.now()) + '.jpg'
    print(new_filename)
    im_flip.save(new_filename, quality=100)
    return new_filename


def filpImage(img):
    return ImageOps.flip(img)

''' Delete the temporary file '''
def deleteTemp(path1, path2):
    if os.path.isfile(path1):
        os.remove(path1)
    if os.path.isfile(path2):
        os.remove(path2)
