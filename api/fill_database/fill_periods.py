import json

from django.http import HttpResponse, JsonResponse

from api.models import Dictionary, Meaning, Entry, Period


def addPeriods():

    periods = json.loads(open("api/fill_database/periods.json").read())

    print(periods)

    periodsToCreate = [Period(name=word['name'],
                              start=word['start'],
                              end=word['end'],
                              description=word['description']) for word in periods]

    print(periodsToCreate)

    Period.objects.bulk_create(periodsToCreate)

    #
    # periodsToCreate = []
    # wordsMap = dict([(entry.term, entry) for entry in Entry.objects.all()])
    # for key in words:
    #     word = wordsMap[key]
    #     # wordsToCreate.append(word)
    #     for mean in words[key]:
    #         meaning = Meaning(text=mean, entry_id=word.pk)
    #         periodsToCreate.append(meaning)
    #         # word.meaning_set.add(Meaning(text=mean, entry=word))
    #
    # Meaning.objects.bulk_create(periodsToCreate)
    # return HttpResponse("done!")