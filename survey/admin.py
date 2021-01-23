from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse
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
        survey_answer = SurveyAnswer.objects.all()
        body = {'test' : survey_answer[2].user.phone_number}
        return TemplateResponse(request, "admin/results.html", body)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Survey, SurveyAdmin)

custom_admin = SurveyAdminView()


