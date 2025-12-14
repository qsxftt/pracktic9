from django.contrib import admin
from .models import Vacancy, SearchQuery


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_name', 'area_name', 'salary_from', 'salary_to', 'published_at']
    list_filter = ['area_name', 'specialization', 'published_at']
    search_fields = ['name', 'company_name', 'description']
    readonly_fields = ['created_at']


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'area', 'per_page', 'created_at', 'vacancies_count']
    list_filter = ['created_at', 'area']
    search_fields = ['query']
    readonly_fields = ['created_at']
    
    def vacancies_count(self, obj):
        return obj.vacancies.count()
    vacancies_count.short_description = 'Количество вакансий'