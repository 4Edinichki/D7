from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse


class Author(models.Model):
    range_author = models.IntegerField(default=0)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def update_raiting(self):
        post_rang = self.post_set.aggregate(postRating=Sum('rang_news'))
        temp_rang = 0
        temp_rang += post_rang.get("postRating")

        comment_rang = self.user.comment_set.aggregate(commentRating=Sum('rang_comment'))
        temp_comment = 0
        temp_comment += comment_rang.get("commentRating")

        self.range_author = temp_rang * 3 + temp_comment
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscribe = models.ManyToManyField(User, through='UserCategory')


class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Post(models.Model):
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )

    category_news = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    time_add_news = models.DateTimeField(auto_now_add=True)
    heading_news = models.CharField(max_length=256)
    text_news = models.TextField()
    rang_news = models.IntegerField(default=0)

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, through="PostCategory")

    def like(self):
        self.rang_news += 1
        self.save()

    def dislike(self):
        self.rang_news -= 1
        self.save()

    def preview(self):
        return f'{self.text_news[0:123]} ... Рейтинг {self.rang_news}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    text_comment = models.TextField()
    time_add_comment = models.DateTimeField(auto_now_add=True)
    rang_comment = models.IntegerField(default=0)

    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rang_comment += 1
        self.save()

    def dislike(self):
        self.rang_comment -= 1
        self.save()
