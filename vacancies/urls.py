from django.urls import path
from . import views

app_name = 'vacancies'

urlpatterns = [
    path('', views.vacancy_search, name='vacancy_search'),
    path('history/', views.search_history, name='search_history'),
    path('history/<int:pk>/', views.search_history_detail, name='search_history_detail'),
    path('vacancy/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
]