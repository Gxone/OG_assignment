from django.contrib import admin
from django.urls import path, include

from survey.admin import custom_admin

urlpatterns = [
    path('survey/', include('survey.urls')),
    path('admin/', admin.site.urls),
    path('admin/', custom_admin.urls),
]