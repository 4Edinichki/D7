import django.forms
from django_filters import FilterSet, ModelChoiceFilter, DateFilter
from .models import Post, Category
from django.db.models.functions import Lower


class PostFilter(FilterSet):
    time_add_news = DateFilter(
        lookup_expr='gt',
        widget=django.forms.DateInput(
            attrs={
                'type': 'date'
            }
        )
    )

    class Meta:
        model = Post  # Модель корорую будем фильтровать
        # Настройка фильтра
        fields = {
            'heading_news': ['icontains'],
            # 'author_id': ['exect'],
        }
