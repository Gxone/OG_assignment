from django.urls import path
from .views import SurveyView

urlpatterns = [
    path('', SurveyView.as_view()),
]