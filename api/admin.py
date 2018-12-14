from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(Corpus)
admin.site.register(Document)
admin.site.register(Appears)
admin.site.register(Period)
admin.site.register(Meaning)
admin.site.register(Example)
admin.site.register(Entry)
admin.site.register(Dictionary)
admin.site.register(WordAppear)