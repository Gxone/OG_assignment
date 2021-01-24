from django.contrib import admin
from django.contrib.admin import AdminSite
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path

from survey.models import Survey, Question, SurveyAnswer

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'survey')
    list_filter = ['survey']

class containQuestion(admin.StackedInline):
    model = Question
    extra = 3

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'type')
    fieldsets = [('title', {'fields':['title']}), ('type', {'fields':['type']})]
    # 외래키 관계
    inlines = [containQuestion]

class SurveyAdminView(AdminSite) :
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'results/', self.admin_view(self.post_results_view))
        ]
        urls = custom_urls + urls
        return urls

    def post_results_view(self, request):
        survey_answers = SurveyAnswer.objects.select_related('question__survey').select_related('user')
        questions = Question.objects.all()

        # 설문 문항 리스트
        survey_title_list = [(answer.question.survey.id, answer.question.survey.title) for answer in survey_answers]
        # 선택지 리스트
        question_list = [(question.id, question.question, question.survey.id) for question in questions]
        # 문항별 선택된 응답 리스트
        survey_answer_list = [(answer.question.id, answer.question.question, answer.question.survey.id) for answer in survey_answers]
        # 유저 리스트
        user_list = [(answer.user.id, answer.user.phone_number) for answer in survey_answers]
        # 유저별 선택한 답변 리스트
        user_answer_list = [(answer.user.id, answer.question.survey.id, answer.question.question) for answer in survey_answers]

        # 문항 별 응답 비율
        rate_list = dict()
        for i in survey_title_list:
            for j in question_list:
                if i[0] == j[2]:
                    rate_list[j[0]] = round(survey_answers.filter(question = j[0]).aggregate(Count('question'))['question__count']\
                    / survey_answers.filter(question__survey = i[0]).aggregate(Count('question'))['question__count'] * 100)

        # 중복되는 문항 및 응답에 대해 중복 제거
        temp_set = set(survey_title_list)
        survey_title_list = list(temp_set)
        temp_set = set(user_list)
        user_list = list(temp_set)
        temp_set = set(user_answer_list)
        user_answer_list = list(temp_set)

        answer_result = [{
            'survey_data' : {
                'title_id'    : survey[0],
                'title'       : survey[1],
                'answer_rate' : [{
                    'answer' : question[1],
                    'rate'   : [rate_list[rate] for rate in rate_list.keys() if rate == question[0]]
                } for question in question_list if question[2] == survey[0]]}
        } for survey in survey_title_list]

        user_answer_result = [{
            'user_id'     : user[0],
            'user_number' : user[1],
            'answer_data' : [{
                'title'  : survey[1],
                'answer_list' : [answer[2] for answer in user_answer_list if answer[1] == survey[0] and user[0] == answer[0]]
            } for survey in survey_title_list]
        } for user in user_list]

        body = {
            'answer_result' : answer_result,
            'user_answer_result' : user_answer_result
        }
        return TemplateResponse(request, "admin/results.html", body)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Survey, SurveyAdmin)

custom_admin = SurveyAdminView()


