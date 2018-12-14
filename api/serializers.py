from rest_framework import serializers
from api.models import Dictionary, Entry, Meaning, Period, Document, Appears
from api.corpus.initializer import corpus


# Serializers define the API representation.
class MeaningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meaning
        fields = ['posTag', 'text']


class EntrySerializer(serializers.ModelSerializer):
    meaning_set = MeaningSerializer(many=True, required=False, allow_null=True)
    class Meta:
        model = Entry
        fields = ['id', 'term', 'dictionary', 'meaning_set']

    def create(self, validated_data):
        # set the use created entry to the user dictionary

        meanings_data = validated_data.pop('meaning_set', [])
        entry = Entry.objects.create(**validated_data)

        for meaning in meanings_data:
            Meaning.objects.create(entry=entry, **meaning)

        appears_set = validated_data.pop('appears_set', [])
        for appears in appears_set:
            Appears.objects.create(entry=entry, **appears)
        return entry


class DictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dictionary
        fields = ['id', 'name', 'entry_set']


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    # sample = serializers.SerializerMethodField()
    # raw = serializers.SerializerMethodField()
    period = PeriodSerializer()

    # def __init__(self, *args, **kwargs):
    #     super(DocumentSerializer, self).__init__(*args, **kwargs)
    #     raw = self.context['request'].query_params.get('raw', False)
    #     if not raw:
    #         self.fields.pop('raw')

    # def get_sample(self, obj):
    #     print('getting sample words', obj.fileid)
    #     raw = ' '.join(corpus.words(fileid=obj.fileid))[:100]
    #     print(raw)
    #     return raw
    #
    # def get_raw(self, obj):
    #     print('getting sample words', obj.fileid)
    #     raw = ' '.join(corpus.sents(fileid=obj.fileid))
    #     print(raw)
    #     return raw

    class Meta:
        model = Document
        fields = '__all__'
