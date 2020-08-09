from rest_framework import serializers
from test_app.models import Test
from test_app.models import ImageModel


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('test', 'id',)


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ImageModel
        fields = ('image', 'id')

