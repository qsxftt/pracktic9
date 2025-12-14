from django import forms


class SearchForm(forms.Form):
    """Форма для поиска вакансий через HH API."""
    
    search_text = forms.CharField(
        label='Название вакансии',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python разработчик'})
    )
    per_page = forms.IntegerField(
        label='Количество вакансий',
        initial=20,
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    area = forms.CharField(
        label='Регион (код)',
        initial='1',
        help_text='1 - Москва, 2 - Санкт-Петербург, 113 - Россия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_per_page(self):
        per_page = self.cleaned_data['per_page']
        if per_page > 100:
            raise forms.ValidationError("Максимальное количество - 100 вакансий")
        return per_page


class FilterForm(forms.Form):
    """Форма для фильтрации уже загруженных вакансий."""
    
    # Убрали поле specialization, оставили только зарплату
    salary_min = forms.IntegerField(
        required=False,
        label='Зарплата от',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Минимальная зарплата'})
    )
    salary_max = forms.IntegerField(
        required=False,
        label='Зарплата до',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Максимальная зарплата'})
    )