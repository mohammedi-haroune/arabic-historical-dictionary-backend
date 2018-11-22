from django.db import models

# Create your models here.
class Dictionary(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name
    # class Meta:
    #     order_with_respect_to = 'name'

class Entry(models.Model):
    term = models.CharField(max_length=255)
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    def __str__(self):
        return self.term
    class Meta:
        ordering = ('term',)


class Meaning(models.Model):
    text = models.TextField()
    posTag = models.CharField(max_length=200)
    entry = models.ForeignKey(Entry,on_delete=models.CASCADE)

    def __str__(self):
        return self.text
    # class Meta:
    #     order_with_respect_to = 'text'

class Example(models.Model):
    text = models.TextField()
    meaning = models.ForeignKey(Meaning,on_delete=models.CASCADE)
    def __str__(self):
        return self.text

    # class Meta:
    #     order_with_respect_to = 'text'


class Corpus(models.Model):
    name = models.CharField(max_length=255)
    path = models.TextField()
    def __str__(self):
        return self.name
    # class Meta:
    #     order_with_respect_to = 'name'

class Period(models.Model):
    name = models.CharField(max_length=255)
    start = models.DateField()
    end = models.DateField()
    def __str__(self):
        return self.name
    # class Meta:
    #     order_with_respect_to = 'name'

class Document(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    path = models.TextField()
    corpus = models.ForeignKey(Corpus,on_delete=models.CASCADE)
    period = models.ForeignKey(Period,on_delete=models.PROTECT)
    meanings = models.ManyToManyField(Meaning,through='Appears')
    def __str__(self):
        return self.name
    # class Meta:
    #     order_with_respect_to = 'name'

class Appears(models.Model):
    sentence = models.TextField()
    confirmed = models.BooleanField(default=False)
    position = models.BigIntegerField()
    document = models.ForeignKey(Document,on_delete=models.CASCADE)
    meaning = models.ForeignKey(Meaning,on_delete=models.CASCADE)
    def __str__(self):
        return self.sentence
    # class Meta:
    #     order_with_respect_to = 'sentence'