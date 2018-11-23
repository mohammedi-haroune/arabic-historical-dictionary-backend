from rest_framework import serializers
from api.models import  Dictionary

# Serializers define the API representation.
class DictionarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dictionary
        fields = '__all__'