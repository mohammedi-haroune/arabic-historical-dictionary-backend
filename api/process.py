from django.http import HttpResponse, JsonResponse

from api.models import Meaning


def means(request):
    meanings = Meaning.objects.all()
    meanings = [{"posTag":meaning.posTag,"name":meaning.entry.term,"definition":meaning.text} for meaning in meanings]
    return JsonResponse(meanings,safe=False)