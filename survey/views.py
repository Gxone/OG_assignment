from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views import View
from django.conf.urls import url
from django.contrib import admin

from .forms import UserForm
from .models import Survey, Question, SurveyAnswer, User

class SurveyView(View):
    def get(self, request):
        surveys = Survey.objects.prefetch_related('question_set')
        survey_list = [{
            'survey_title'   : survey.title,
            'survey_type'    : survey.type.name,
            'question_title' : [s.question for s in survey.question_set.filter(survey = survey.id)]
        } for survey in surveys]

        body = {'survey_list' : survey_list}

        return render(request, 'surveys/index.html', body)

    def post(self, request):
        surveys = Survey.objects.prefetch_related('question_set')
        user = User(phone_number = request.POST['user'])
        user.save()

        for survey in surveys:
            # 사용자가 선택한 답변을 가져온다. form 의 name 을 통해 input 값(선택지 value)을 리스트로 가져온다.
            answer_list = request.POST.getlist(survey.title)

            for answer in answer_list:
                answer = SurveyAnswer(user = user, question = survey.question_set.get(question = answer))
                answer.save()

        body = {'test' : answer_list}
        return render(request, 'surveys/success.html', body)