import pandas as pd

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Count
from django.http import Http404
from django.template.response import TemplateResponse
from django.urls import path

from survey.models import Survey, Question, SurveyAnswer, User

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'survey')
    list_filter = ['survey']

class containQuestion(admin.StackedInline):
    model = Question
    extra = 3

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'type')
    fieldsets = [('title', {'fields' : ['title']}), ('type', {'fields' : ['type']})]
    # 외래키 관계
    inlines = [containQuestion]

class SurveyAnswersView(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'results/', self.admin_view(self.get_results_view))
        ]
        urls = custom_urls + urls
        return urls

    def cal_rate(self, survey_title_list, questions, survey_answers):
        # 문항 별 응답 비율
        rate_list = dict()
        for survey in survey_title_list:
            for question in questions:
                if survey.id == question.survey.id:
                    # 문항에 대한 답변 별 개수
                    count = survey_answers.filter(question=question.id).aggregate(Count('question'))['question__count']
                    # 문항에 대한 모든 답변의 개수
                    sum = survey_answers.filter(question__survey=survey.id).aggregate(Count('question'))[
                        'question__count']
                    # = 문항 별 답변 비율 계산
                    rate_list[question.id] = round(count / sum * 100)
        return rate_list

    def get_results_view(self, request):
        """ 문항 별 응답 비율 데이터 전달

        문항 별 선택지의 응답 비율 리스트를 전달합니다.

        returns:
            200: 문항, 선택지 비율 테이터
        """
        survey_answers = SurveyAnswer.objects.select_related('question__survey')
        questions = Question.objects.all()

        # 설문 문항 리스트
        surveys = [survey.question.survey for survey in survey_answers]

        # 문항 순서 유지 중복 제거
        survey_title_list = list()
        for survey in surveys:
            if survey not in survey_title_list:
                survey_title_list.append(survey)

        # 문항 별 응답 비율
        rate_list = self.cal_rate(survey_title_list, questions, survey_answers)

        # 반환 data
        answer_result = [{
            'survey_data' : {
                'title_id'    : survey.id,
                'title'       : survey.title,
                'answer_rate' : [{
                    'answer' : question.question,
                    'rate'   : [str(rate_list[rate]) + '%' for rate in rate_list.keys() if rate == question.id][0]
                } for question in questions if question.survey.id == survey.id]}
        } for survey in survey_title_list]

        body = {
            'answer_result' : answer_result
        }
        return TemplateResponse(request, "admin/survey_results.html", body)

class MakeExcelView(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'results/excel/', self.admin_view(self.make_excel()))
        ]
        urls = custom_urls + urls
        return urls

    def make_excel(self):
        """ 문항 별 선택지 응답 데이터 엑셀 파일 다운로드

        문항 별 선택한 응답 비율을 엑셀 파일로 다운로드합니다.
        """


        # make excel file
        writer = pd.ExcelWriter('../survey_result.xlsx')

        results = SurveyAnswer.objects.select_related('question__survey')

        survey_answers = SurveyAnswer.objects.select_related('question__survey')
        questions = Question.objects.all()

        # 설문 문항 리스트
        surveys = [survey.question.survey for survey in survey_answers]

        # 문항 순서 유지 중복 제거
        survey_title_list = list()
        for survey in surveys:
            if survey not in survey_title_list:
                survey_title_list.append(survey)

        # 문항 별 응답 비율
        rate_list = dict()
        for survey in survey_title_list:
            for question in questions:
                if survey.id == question.survey.id:
                    # 문항에 대한 답변 별 개수
                    count = survey_answers.filter(question=question.id).aggregate(Count('question'))['question__count']
                    # 문항에 대한 모든 답변의 개수
                    sum = survey_answers.filter(question__survey=survey.id).aggregate(Count('question'))[
                        'question__count']
                    # = 문항 별 답변 비율 계산
                    rate_list[question.id] = round(count / sum * 100)

        df = pd.DataFrame({
            "질문": result,
            "답변": result,
            "비율": result} for result in rate_list)

        df.to_excel(writer, 'sheet1')
        writer.save()

class UsersView(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'user-results/', self.admin_view(self.get_user_results_view))
        ]
        urls = custom_urls + urls
        return urls

    def get_user_results_view(self, request):
        """ 유저 리스트 전달

        설문에 참여한 유저의 리스트를 전달합니다.

        returns:
            200: 유저 리스트
        """
        survey_users = User.objects.all()

        user_list = [{
            'user_id'     : user.id,
            'user_number' : user.phone_number[0:3] + "-" + user.phone_number[3:7] + "-" + user.phone_number[7:11] # 핸드폰 번호 포맷으로 보여주기 위해
        } for user in survey_users]

        # user_answer_result = json.dumps(user_answer_result)
        body = {"user_list" : user_list}

        return TemplateResponse(request, "admin/user_results.html", body)

class UserAnswerView(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'user-results/<int:user_id>/', self.admin_view(self.get_user_result_view))
        ]
        urls = custom_urls + urls
        return urls

    def get_user_result_view(self, request, user_id):
        """ 유저 응답 상세 데이터 전달

        유저 별로 응답한 문항과 응답 내용 리스트를 전달합니다.

        args:
            user_id:

        returns:
            200: 유저 별 응답 데이터 리스트
            404: Exception
        """
        try:
            survey_answers = SurveyAnswer.objects.filter(user = user_id).select_related('question__survey').select_related('user')
            surveys = [survey.question.survey for survey in survey_answers]
            # user_queryset = get_object_or_404(User.objects.filter(id = user_id).prefetch_related('surveyanswer_set__question__survey'))

            # 문항 순서 유지 중복 제거
            survey_title_list = list()
            for survey in surveys:
                if survey not in survey_title_list:
                    survey_title_list.append(survey)

            # 핸드폰 번호 포맷으로 보여주기 위해
            num = survey_answers[0].user.phone_number
            num = num[0:3] + "-" + num[3:7] + "-" + num[7:11]

            # 반환 data
            body = {
                'user_id' : user_id,
                'user_number' : num,
                'answer_data' : [{
                    'title'       : survey.title,
                    'answer_list' : ', '.join([answer.question.question for answer in survey_answers if answer.question.survey.id == survey.id])
                } for survey in survey_title_list]}

            return TemplateResponse(request, "admin/user_result_detail.html", body)
        except IndexError:
            raise Http404('NO_DATA')


admin.site.register(Question, QuestionAdmin)
admin.site.register(Survey, SurveyAdmin)

admin_survey_results = SurveyAnswersView()
admin_user_results = UsersView()
admin_user_result = UserAnswerView()
admin_make_excel = MakeExcelView()