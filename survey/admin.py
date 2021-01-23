from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path

from survey.models import Survey, Question, SurveyAnswer

class containQuestion(admin.StackedInline):
    model = Question
    extra = 3

class SurveyAdmin(admin.ModelAdmin):
    fieldsets = [('title', {'fields':['title']}), ('type', {'fields':['type']})]
    inlines = [containQuestion]

class SurveyAdminView(AdminSite) :
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'results/', self.admin_view(self.test_view))
        ]
        urls = custom_urls + urls
        return urls

    def test_view(self, request):
        return HttpResponse("HELLO")

    def post_results_view(self, request):
        body = {'test' : 'test'}
        return TemplateResponse(request, "admin/results.html", body)

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question)

custom_admin = SurveyAdminView()


