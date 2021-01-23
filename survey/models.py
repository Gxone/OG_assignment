from django.db import models
from django.core.validators import MinLengthValidator

class Survey(models.Model):
    title = models.CharField(max_length = 256)
    type  = models.ForeignKey('SurveyType', on_delete = models.CASCADE)

    def __str__(self):
        return self.title

class Question(models.Model):
    question = models.CharField(max_length = 256)
    survey   = models.ForeignKey(Survey, on_delete = models.CASCADE)

    def __str__(self):
        return self.question

class SurveyType(models.Model):
    name = models.CharField(max_length = 24)

    def __str__(self):
        return self.name

class User(models.Model):
    phone_number = models.CharField(max_length = 50)

    def __str__(self):
        return self.phone_number

class SurveyAnswer(models.Model):
    user     = models.ForeignKey(User, on_delete = models.CASCADE)
    question = models.ForeignKey(Question, on_delete = models.CASCADE)