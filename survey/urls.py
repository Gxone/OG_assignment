from django.urls import path, include
from django.contrib import admin

from .views import SurveyView


urlpatterns = [
    path('', SurveyView.as_view()),
    # path('admin/', custom_admin.urls),
]