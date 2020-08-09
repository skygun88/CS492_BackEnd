from django.shortcuts import render
from rest_framework import viewsets
from test_app.models import Test, ImageModel
from test_app.serializers import TestSerializer, ImageSerializer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

import os
import base64
import json
from PIL import Image, ImageOps


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
        print(request)
        print(request.method)
        # image_file = request.FILES['uploaded_file']
        image_file = request.FILES.get('uploaded_file')
        path = default_storage.save('test.jpg', ContentFile(image_file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        print("Save finish")
        img = Image.open(tmp_file)
        im_flip = ImageOps.flip(img)
        im_flip.save('media/test_flip.jpg', quality=95)
    else:
        print("Test - not Post")
    return HttpResponse("<http><body>hihihi</body></http>")
    # data = {}
    # with open('media/t1.png', mode='rb') as file:
    #     img = file.read()
    # data['img'] = base64.encodebytes(img).decode("utf-8")
    # json_data = json.dumps(data)
    # print(json_data)
    # return JsonResponse(json_data, json_dumps_params={'ensure_ascii': True}, status=200)
