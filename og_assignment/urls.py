from django.contrib import admin
from django.urls import path, include

from survey.admin import admin_survey_results, admin_user_results, admin_user_result

urlpatterns = [
    path('survey/', include('survey.urls')),
    path('admin/', admin.site.urls),
    path('admin/', admin_survey_results.urls),
    path('admin/', admin_user_results.urls),
    path('admin/', admin_user_result.urls),
]