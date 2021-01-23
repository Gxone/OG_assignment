from django.shortcuts import render
from django.views import View

from .models import Survey, SurveyAnswer, User

class SurveyView(View):
    def get(self, request):
        # 설문 질문과 문항을 함께 가져온다.
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
            # 사용자가 선택한 답변을 가져온다. input 태그의 name을 통해 input 값(value)을 리스트로 가져온다.
            answer_list = request.POST.getlist(survey.title)

            for answer in answer_list:
                answer = SurveyAnswer(user = user, question = survey.question_set.get(question = answer))
                answer.save()

        return render(request, 'surveys/success.html')