from django import forms
from django.core.exceptions import ValidationError

from .models import Post, Author, User


class PostForm(forms.ModelForm):
    heading_news = forms.CharField(min_length=20)

    class Meta:
        model = Post
        # author_id = Author.objects.get(id=3)
        fields = [
            # '__all__'
            # 'category_news',
            'heading_news',
            'text_news',
            'author',
        ]

    def clean(self):
        cleaned_data = super().clean()
        heading_news = cleaned_data.get("heading_news")
        text_news = cleaned_data.get("text_news")

        if heading_news == text_news:
            raise ValidationError(
                "Текст не должен быть идентичен названию статьи"
            )

        return cleaned_data
