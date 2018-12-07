import json

from django.http import HttpResponse, JsonResponse
#
try:
    from api.models import Dictionary, Meaning, Entry
except Exception:
    pass

def addWassit(request):

    dictionary = Dictionary.objects.filter(name='el_wassit')
    if not dictionary:
        dictionary = Dictionary(name='el_wassit')
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

def entries(request):
    dictionary = Dictionary.objects.filter(name='el_wassit')[0]
    entryMap = {}
    for element in dictionary.entry_set.all()[:100]:
        meanings = [meaning.text for meaning in element.meaning_set.all()]
        entryMap[element.term] = meanings
    Entry.objects.all().delete()
    return JsonResponse(entryMap, safe=False)

def fixWassit():
    import re
    words = json.loads(open("dictionaries_files/wassit.json").read())
    words = dict([(re.sub("^(.*?)\s*$",'\1',word),words[word]) for word in words])
    with open('dictionaries_files/wassit2.json', 'w') as fp:
        json.dump(words, fp)


if __name__ == '__main__':
    fixWassit()




