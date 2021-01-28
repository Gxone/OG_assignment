from django.http import Http404
from django.shortcuts import render
from django.views import View

from .models import Survey, SurveyAnswer, User

class SurveyView(View):
    def get(self, request):
        """ 설문조사 데이터 전달

        설문조사 문항과 선택지 데이터를 전달합니다.

        returns:
            200: 문항 및 선택지 리스트
            404:
        """
        try:
            # 문항과 선택지 데이터
            surveys = Survey.objects.prefetch_related('question_set')

            # 설문조사 문항, 타입(radio, select, chkbox), 선택지
            survey_list = [{
                'survey_title'   : survey.title,
                'survey_type'    : survey.type.name,
                # 문항에 해당하는 선택지를 id로 필터링
                'question_title' : [survey.question for survey in survey.question_set.filter(survey = survey.id)]
            } for survey in surveys]
            body = {'survey_list' : survey_list}
            return render(request, 'surveys/index.html', body)
        except Survey.DoesNotExist:
            raise Http404('설문조사 문항이 없습니다.')

    def post(self, request):
        """ 응답 데이터 등록

        유저가 응답한 데이터를 데이터베이스에 저장합니다.

        args:
            user: 유저가 입력한 응답 데이터

        returns:
            success.html
            fail.html
        """
        # 사용자가 form 에서 입력한 응답을 가져온다.
        input_user_data = User(phone_number=request.POST['user'])

        # 설문조사 참여 여부를 알기 위해 참여한 유저의 데이터를 가져온다.
        exist_user = ''
        if User.objects.exists():
            exist_user = User.objects.filter(phone_number = input_user_data.phone_number)

        if not exist_user.exists():
            # 설문조사 문항과 선택지 데이터
            surveys = Survey.objects.prefetch_related('question_set')

            input_user_data.save()
            # 문항 별로 사용자가 선택한 답변을 가져온다.
            for survey in surveys:
                 # input 태그의 name을 통해 input 값(value)을 리스트로 가져온다.
                answer_list = request.POST.getlist(survey.title)
                for answer in answer_list:
                    answer = SurveyAnswer(user = input_user_data, question = survey.question_set.get(question = answer))
                    answer.save()
            return render(request, 'surveys/success.html')
        return render(request, 'surveys/fail.html')