from django.urls import path, include, re_path
from test_app import views


app_name = 'test_app'
urlpatterns = [
    path('', include('rest_framework.urls', namespace='rest_framework_category')),
]