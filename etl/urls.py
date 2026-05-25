from django.urls import path
from . import views

app_name = 'etl'

urlpatterns = [
    path('upload/',           views.upload_view,       name='upload'),
    path('sources/',          views.sources_list_view, name='sources'),
    path('job/<int:pk>/',     views.job_detail_view,   name='job_detail'),
    path('api/job/<int:pk>/', views.job_status_api,    name='job_status_api'),
]