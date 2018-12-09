import json

from django.http import JsonResponse

from api.corpus.initializer import corpus


def createXmlDict(request):
    # dictionary = Dictionary.objects.filter(name='المعجم الوسيط')[0]
    # entries = Entry.objects.filter(dictionary=dictionary)
    entries = json.loads(open("dicts/wassit.json").read())
    entries = [entry for entry in entries]
    apps = corpus.words_apparitions(set(entries))
    print(len(apps))
    # return JsonResponse(apps,safe=False)

if __name__ == '__main__':
    createXmlDict(None)