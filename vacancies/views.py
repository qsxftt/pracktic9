import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Vacancy, SearchQuery
from .forms import SearchForm, FilterForm


def fetch_vacancies_from_hh(search_query, area='1', per_page=20):
    """
    Получает вакансии из HH API по запросу.
    
    Args:
        search_query (str): Поисковый запрос
        area (str): Код региона
        per_page (int): Количество вакансий
    
    Returns:
        list: Список объектов Vacancy
    """
    vacancies = []
    base_url = "https://api.hh.ru/vacancies"
    
    params = {
        'text': search_query,
        'area': area,
        'per_page': min(per_page, 100),
        'page': 0
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        
        for item in data.get('items', []):
            try:
                # Получаем детальную информацию о вакансии
                vacancy_detail = requests.get(
                    f"https://api.hh.ru/vacancies/{item['id']}",
                    timeout=10
                )
                
                if vacancy_detail.status_code == 200:
                    vacancy_data = vacancy_detail.json()
                    
                    # Извлекаем информацию о зарплате
                    salary = vacancy_data.get('salary')
                    salary_from = salary.get('from') if salary else None
                    salary_to = salary.get('to') if salary else None
                    salary_currency = salary.get('currency') if salary else None
                    
                    # Извлекаем специализацию
                    specialization = ''
                    if vacancy_data.get('specializations'):
                        specialization = vacancy_data['specializations'][0].get('name', '')
                    
                    # Создаем или обновляем вакансию
                    vacancy, created = Vacancy.objects.update_or_create(
                        hh_id=vacancy_data['id'],
                        defaults={
                            'name': vacancy_data.get('name', ''),
                            'company_name': vacancy_data.get('employer', {}).get('name', ''),
                            'company_logo': vacancy_data.get('employer', {}).get('logo_urls', {}).get('90'),
                            'area_name': vacancy_data.get('area', {}).get('name', ''),
                            'salary_from': salary_from,
                            'salary_to': salary_to,
                            'salary_currency': salary_currency,
                            'description': vacancy_data.get('description', ''),
                            'specialization': specialization,
                            'published_at': vacancy_data.get('published_at'),
                        }
                    )
                    vacancies.append(vacancy)
                    
            except Exception as e:
                print(f"Ошибка при обработке вакансии: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Ошибка при запросе к API: {str(e)}")
    
    return vacancies


def vacancy_search(request):
    """
    Поиск вакансий через HH API и отображение результатов.
    """
    vacancies = []
    search_query_obj = None
    
    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        filter_form = FilterForm()
        
        if search_form.is_valid():
            search_text = search_form.cleaned_data['search_text']
            per_page = search_form.cleaned_data['per_page']
            area = search_form.cleaned_data['area']
            
            # Сохраняем поисковый запрос
            search_query_obj = SearchQuery.objects.create(
                query=search_text,
                area=area,
                per_page=per_page
            )
            
            # Получаем вакансии из API
            vacancies = fetch_vacancies_from_hh(search_text, area, per_page)
            
            # Сохраняем найденные вакансии в запросе
            if vacancies:
                search_query_obj.vacancies.set(vacancies)
                search_query_obj.save()
            
            messages.success(request, f'Найдено {len(vacancies)} вакансий по запросу "{search_text}"')
            
            # Сохраняем ID поискового запроса в сессии для фильтрации
            request.session['current_search_id'] = search_query_obj.id
            
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    
    else:
        search_form = SearchForm()
        filter_form = FilterForm()
        
        # Если есть ID поиска в сессии, показываем эти вакансии
        search_id = request.session.get('current_search_id')
        if search_id:
            search_query_obj = SearchQuery.objects.filter(id=search_id).first()
            if search_query_obj:
                vacancies = search_query_obj.vacancies.all()
    
    # Применяем фильтры если есть
    if 'salary_min' in request.GET or 'salary_max' in request.GET:
        filter_form = FilterForm(request.GET)
        if filter_form.is_valid():
            salary_min = filter_form.cleaned_data.get('salary_min')
            salary_max = filter_form.cleaned_data.get('salary_max')
            
            if vacancies:
                # Применяем фильтры к вакансиям
                filtered_vacancies = vacancies
                
                if salary_min:
                    filtered_vacancies = [v for v in filtered_vacancies if v.salary_from and v.salary_from >= salary_min]
                
                if salary_max:
                    filtered_vacancies = [v for v in filtered_vacancies if v.salary_to and v.salary_to <= salary_max]
                
                vacancies = filtered_vacancies
    
    # Пагинация
    paginator = Paginator(vacancies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'vacancies/vacancy_list.html', {
        'search_form': search_form,
        'filter_form': filter_form,
        'vacancies': page_obj,
        'search_query': search_query_obj,
    })


def search_history(request):
    """Отображение истории поисковых запросов."""
    search_queries = SearchQuery.objects.all().order_by('-created_at')
    
    paginator = Paginator(search_queries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'vacancies/search_history.html', {
        'search_queries': page_obj,
    })


def search_history_detail(request, pk):
    """Просмотр конкретного поискового запроса и его результатов."""
    search_query = get_object_or_404(SearchQuery, pk=pk)
    
    # Сохраняем ID поискового запроса в сессии
    request.session['current_search_id'] = search_query.id
    
    vacancies = search_query.vacancies.all()
    
    # Пагинация
    paginator = Paginator(vacancies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Формы
    search_form = SearchForm(initial={
        'search_text': search_query.query,
        'area': search_query.area,
        'per_page': search_query.per_page,
    })
    filter_form = FilterForm()
    
    return render(request, 'vacancies/vacancy_list.html', {
        'search_form': search_form,
        'filter_form': filter_form,
        'vacancies': page_obj,
        'search_query': search_query,
        'from_history': True,
    })


def vacancy_detail(request, pk):
    """Детальная информация о вакансии."""
    vacancy = get_object_or_404(Vacancy, pk=pk)
    
    # Генерируем ссылку на HH
    hh_url = f"https://hh.ru/vacancy/{vacancy.hh_id}"
    
    return render(request, 'vacancies/vacancy_detail.html', {
        'vacancy': vacancy,
        'hh_url': hh_url,
    })