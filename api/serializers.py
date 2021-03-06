from rest_framework import serializers
from api.models import Dictionary, Entry, Meaning, Period, Document, Appears, WordAppear
from api.corpus.initializer import corpus


# Serializers define the API representation.

class AppearsSerializer(serializers.ModelSerializer):
    #period_id = serializers.SerializerMethodField(required=False, allow_null=True)

    #def get_period_id(self, obj):
    #    return obj.document.period.id

    class Meta:
        model = Appears
        fields = ['sentence', 'position', 'word_position', 'document', 'confirmed']

class MeaningSerializer(serializers.ModelSerializer):
    is_appears = serializers.SerializerMethodField(required=False, allow_null=True)
    appears_set = AppearsSerializer(many=True, allow_null=True, required=False)

    def get_is_appears(self, obj):
        return obj.appears_set.count() > 0

    class Meta:
        model = Meaning
        fields = ['id', 'posTag', 'text', 'appears_set', 'is_appears']



class MeaningAppearsSerializer(serializers.ModelSerializer):
    appears_set = AppearsSerializer(many=True)

    class Meta:
        model = Meaning
        fields = ['id', 'appears_set']


class EntrySerializer(serializers.ModelSerializer):
    meaning_set = MeaningSerializer(many=True, required=False, allow_null=True)
    class Meta:
        model = Entry
        fields = ['id', 'term', 'dictionary', 'meaning_set']
        validators = []

    def create(self, validated_data):
        # set the use created entry to the user dictionary
        print('validated_data', validated_data)


        meaning_set = validated_data.pop('meaning_set', [])
        entry, created = Entry.objects.get_or_create(**validated_data)

        print('term', entry)

        for meaning in meaning_set:
            appears_set = meaning.pop('appears_set', [])

            print('meaning', meaning)
            print('appears_set', appears_set)

            if 'id' not in meaning:
                meaning, created = Meaning.objects.get_or_create(entry=entry, **meaning)

            for appears in appears_set:
                print('appears', dict(appears))
                Appears.objects.create(meaning=meaning, **appears)
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
        fields = ['id', 'name', 'category', 'author', 'period']



class WordAppearsSerializer(serializers.ModelSerializer):
    document = DocumentSerializer()
    entry = EntrySerializer()
    class Meta:
        model = WordAppear
        fields = ['id', 'entry', 'sentence', 'document']