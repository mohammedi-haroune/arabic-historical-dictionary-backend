from rest_framework import serializers
from api.models import Dictionary, Entry, Meaning


# Serializers define the API representation.
class MeaningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meaning
        fields = '__all__'

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['term', 'meaning_set']

class DictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dictionary
        fields = ['name', 'entry_set']