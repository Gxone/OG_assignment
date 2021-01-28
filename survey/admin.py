import csv

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.urls import path

from survey.models import Survey, Question, SurveyAnswer, User

class containQuestion(admin.StackedInline):
    model = Question
    extra = 3

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    # 목록에 보여질 survey 모델의 필드
    list_display = ('title', 'type')
    # 세부 양식에서 연관된 모델 정보를 그룹화
    fieldsets = [('문항', {'fields' : ['title']}), ('타입', {'fields' : ['type']})]
    # 문항에 해당하는 선택지들을 함께 수정하기 위해 작성 (외래키 관계)
    inlines = [containQuestion]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    # 목록에 보여질 question 모델의 필드
    list_display = ('question', 'survey')
    # 세부 양식에서 연관된 모델 정보를 그룹화
    fieldsets = [('선택지', {'fields': ['question']}), ('문항', {'fields': ['survey']})]
    # 필터 옵션 추가할 필드
    list_filter = ['survey']

@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):
    # 목록에 보여질 surveyanswer 모델의 필드
    list_display = ('user', 'id')
    # 필터 옵션 추가할 필드
    list_filter = ['question__survey', 'user']
    # csv 다운로드 액션 추가
    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        """ csv 파일 다운로드

        선택한 답변을 csv 파일로 다운로드 합니다.

        returns:
            200: csv 파일 다운로드
        """
        meta = self.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename = survey_result.csv'.format(meta)
        writer = csv.writer(response)
        queryset = queryset.select_related('question__survey')

        # field row 지정
        writer.writerow(['id', '전화번호', '문항', '선택지'])
        for obj in queryset:
            writer.writerow([obj.id, obj.user, obj.question.survey, obj.question])
        return response

    export_as_csv.short_description = "Export to csv"

class SurveyAnswersView(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'results/', self.admin_view(self.get_results_view))
        ]
        urls = custom_urls + urls
        return urls

    def get_results_view(self, request):
        """ 문항 별 응답 비율 데이터 전달

        문항 별 선택지의 응답 비율 리스트를 전달합니다.

        returns:
            200: 문항, 선택지 비율 테이터
        """
        # 설문조사 결과와 문항 데이터
        survey_answers = SurveyAnswer.objects.select_related('question__survey')
        # 답변하지 않은 선택지도 표출하기 위해
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

        # 반환 딕셔너리
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

    def cal_rate(self, survey_title_list, questions, survey_answers):
        """ 문항 별 응답 비율 계산

        문항 별 선택지의 응답 비율 리스트를 전달합니다.

        args:
            survey_title_list: 문항 리스트
            questions: 선택지 리스트
            survey_answers: 설문조사 응답 데이터

        returns:
            문항 별 선택지 응답 비율
        """
        rate_list = dict()
        for survey in survey_title_list:
            for question in questions:
                if survey.id == question.survey.id:
                    # 문항에 대한 답변 별 개수
                    count = survey_answers.filter(question = question.id).aggregate(Count('question'))['question__count']
                    # 문항에 대한 모든 답변의 개수
                    sum = survey_answers.filter(question__survey = survey.id).aggregate(Count('question'))['question__count']
                    # = 문항 별 답변 비율 계산
                    rate_list[question.id] = round(count / sum * 100)
        return rate_list

class UsersView(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'user-results/', self.admin_view(self.get_user_results_view))
        ]
        urls = custom_urls + urls
        return urls

    def get_user_results_view(self, request):
        """ 응답자 리스트 전달

        설문에 참여한 유저의 리스트를 전달합니다.

        returns:
            200: 유저 리스트
        """
        # 응답자 데이터
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
            user_id: 응답자 id

        returns:
            200: 유저 별 응답 데이터 리스트
            404: Exception
        """
        try:
            # 설문조사 응답 데이터
            survey_answers = SurveyAnswer.objects.filter(user = user_id).select_related('question__survey').select_related('user')
            # 문항 리스트
            surveys = [survey.question.survey for survey in survey_answers]

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

admin_survey_results = SurveyAnswersView()
admin_user_results = UsersView()
admin_user_result = UserAnswerView()