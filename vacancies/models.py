from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Vacancy(models.Model):
    """Модель для хранения вакансий."""
    
    hh_id = models.IntegerField(unique=True, verbose_name="ID на HH")
    name = models.CharField(max_length=255, verbose_name="Название вакансии")
    company_name = models.CharField(max_length=255, verbose_name="Название компании")
    company_logo = models.URLField(max_length=500, blank=True, null=True, verbose_name="Логотип компании")
    area_name = models.CharField(max_length=100, verbose_name="Город")
    salary_from = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Зарплата от"
    )
    salary_to = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Зарплата до"
    )
    salary_currency = models.CharField(max_length=10, blank=True, null=True, verbose_name="Валюта")
    description = models.TextField(verbose_name="Описание вакансии")
    specialization = models.CharField(max_length=255, verbose_name="Специализация")
    published_at = models.DateTimeField(verbose_name="Дата публикации")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-published_at']
    
    def __str__(self):
        return f"{self.name} - {self.company_name}"
    
    def get_salary_display(self):
        if self.salary_from and self.salary_to:
            return f"{self.salary_from} - {self.salary_to} {self.salary_currency}"
        elif self.salary_from:
            return f"от {self.salary_from} {self.salary_currency}"
        elif self.salary_to:
            return f"до {self.salary_to} {self.salary_currency}"
        return "Зарплата не указана"


class SearchQuery(models.Model):
    """Модель для хранения поисковых запросов."""
    
    query = models.CharField(max_length=255, verbose_name="Поисковый запрос")
    area = models.CharField(max_length=100, blank=True, null=True, verbose_name="Регион")
    per_page = models.IntegerField(default=20, verbose_name="Количество вакансий")
    vacancies = models.ManyToManyField(Vacancy, verbose_name="Найденные вакансии", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Поисковый запрос"
        verbose_name_plural = "Поисковые запросы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.query} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"