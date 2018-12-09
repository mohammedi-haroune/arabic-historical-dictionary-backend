import json

from django.db.models.sql import Query
from django.http import HttpResponse, JsonResponse

from api.models import Dictionary, Meaning, Entry


def addMaany(request):
    dictionary = Dictionary.objects.filter(name='معجم المعاني الجامع')
    if not dictionary:
        dictionary = Dictionary(name='معجم المعاني الجامع')
        dictionary.save()
    else:
        dictionary = dictionary[0]

    words = json.loads(open("api/fill_database/dictionaries_files/elmaany.json").read())
    wordsToCreate = [Entry(term=key, dictionary=dictionary) for key in words]

    meaningsToCreate = []
    Entry.objects.bulk_create(wordsToCreate)
    wordsMap = dict([(entry.term, entry) for entry in Entry.objects.all()])
    for key in words:
        word = wordsMap[key]
        # wordsToCreate.append(word)
        for postag in words[key]:
            meanings = words[key][postag]
            for mean in meanings:
                meaning = Meaning(text=mean, entry_id=word.pk,posTag=postag)
                meaningsToCreate.append(meaning)
                # word.meaning_set.add(Meaning(text=mean, entry=word))

    Meaning.objects.bulk_create(meaningsToCreate)
    return HttpResponse("done!")


def elghani(request):
    dictionary = Dictionary.objects.filter(name='المعجم الغانى')
    if not dictionary:
        dictionary = Dictionary(name='المعجم الغانى')
        dictionary.save()
    else:
        dictionary = dictionary[0]

    words = json.loads(open('api/fill_database/dicts/elghani.json').read())

    created_words = [entry.term for entry in Entry.objects.filter(dictionary=dictionary)]

    wordsToCreate = [Entry(term=key, dictionary=dictionary) for key in words if key not in created_words]

    meaningsToCreate = []
    Entry.objects.bulk_create(wordsToCreate)
    wordsMap = dict([(entry.term, entry) for entry in Entry.objects.all()])
    for key in words:
        word = wordsMap[key]
        # wordsToCreate.append(word)
        for postag in words[key]:
            meanings = words[key][postag]
            for mean in meanings:
                meaning = Meaning(text=mean, entry_id=word.pk,posTag=postag)
                meaningsToCreate.append(meaning)
                # word.meaning_set.add(Meaning(text=mean, entry=word))

    Meaning.objects.bulk_create(meaningsToCreate)
    return HttpResponse("done!")


def wassit(request):

    dictionary = Dictionary.objects.filter(name='المعجم الوسيط')
    if not dictionary:
        dictionary = Dictionary(name='المعجم الوسيط')
        dictionary.save()
    else:
        dictionary = dictionary[0]

    words = json.loads(open("api/fill_database/dictionaries_files/wassit.json").read())
    wordsToCreate = [Entry(term=key, dictionary=dictionary) for key in words]

    meaningsToCreate = []
    Entry.objects.bulk_create(wordsToCreate)
    wordsMap = dict([(entry.term, entry) for entry in Entry.objects.all()])
    for key in words:
        word = wordsMap[key]
        # wordsToCreate.append(word)
        for mean in words[key]:
            meaning = Meaning(text=mean, entry_id=word.pk)
            meaningsToCreate.append(meaning)
            # word.meaning_set.add(Meaning(text=mean, entry=word))

    Meaning.objects.bulk_create(meaningsToCreate)
    return HttpResponse("done!")