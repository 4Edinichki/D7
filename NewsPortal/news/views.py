from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
# from django.views.generic.detail import PermissionRequiredMixin
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.urls import reverse_lazy
from django.views import View
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, User, Category, UserCategory, PostCategory
from .filters import PostFilter
from .forms import PostForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import *

from django.http import HttpResponse
# from .tasks import hello, printer
from django.conf import settings


class IndexView(View):
    template_name = 'send_mess.html'
    # def get(self, request):
    #     hello.delay()
    #     printer.delay(10)
    #     return HttpResponse("Hello!")


class ClassMessage(View):
    # template_name = 'send_mess.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'send_mess.html', {})

    def post(self, request, *args, **kwargs):
        # appointment = Post(
        #     range_author=request.POST['range_author'],
        #     user=request.POST['user'],
        # )
        # text = request.POST['heading_news'[0]]
        # appointment.save()

        html_content = render_to_string(
            'message.html', {}
        )

        msg = EmailMultiAlternatives(
            subject='d_mess',
            body="{appointment}",
            from_email='ОПТА ОТПРАВИТЕЯ',
            to=['ПОЧТЫ ПОЛУЧАТЕЛЕЙ'],
        )

        msg.attach_alternative(html_content, 'text/html')

        msg.send()

        # send_mail(
        #     subject='d_mess',
        #     message="{appointment}",
        #     from_email='bataev.ilya99@yandex.ru',
        #     recipient_list=['bataev.ilya1999@gmail.com'],
        #     # fail_silently=False,
        # )

        return redirect('/portal/message/')


class CategoryList(ListView):
    model = Category
    template_name = 'subscribers.html'
    context_object_name = 'categories'
    queryset = Category.objects.order_by('-id')


@login_required
def add_subscribe(request):
    user = request.user
    category = Category.objects.get(pk=request.POST['id_cat'])
    subscribe = UserCategory(user_id=user.id, category_id=category.id)
    subscribe.save()
    return redirect('/')


class PostList(ListView):
    model = Post
    ordering = 'id'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


@receiver(post_save, sender=PostCategory)
def post(sender, instance, created, **kwargs):
    users = Category.objects.filter(pk=instance.postCategory).values("subscribers")
    for i in users:
        send_mail(
            subject=f"{instance.title}",
            message=f"Здравствуй, {User.objects.get(pk=i['subscribers']).username}."
                    f" Новая статья в твоём любимом разделе! \n Заголовок статьи: {instance.title} \n"
                    f" Текст статьи: {instance.text[:50]}",
            from_email='bataev.ilya99@yandex.ru',
            recipient_list=[User.objects.get(pk=i['subscribers']).email],
        )
        return redirect('/')


class ArticleList(PostList):
    template_name = 'article.html'


class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'


def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        form.save()
        return HttpResponseRedirect('//')
    form = PostForm()
    return render(request, 'news_edit.html', {'form': form})


class NewsCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        current_url = self.request.path
        post = form.save(commit=False)
        post.category_news = self.model.NEWS
        return super().form_valid(form)


class ArticleCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        current_url = self.request.path
        post = form.save(commit=False)
        post.category_news = self.model.ARTICLE
        return super().form_valid(form)


class PostUpdate(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def form_valid(self, form):
        current_url = self.request.path
        post = form.save(commit=False)
        if post.category_news(current_url.split('/')[0]) == 'NW':
            post.category_news = self.model.NEWS
        else:
            return reverse_lazy('news_list')
        return super().form_valid(form)


class PostDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('post_list')

    # def form_valid(self, form):
    #     current_url = self.request.path
    #     post = form.save(commit=False)
    #     if


@login_required
def subscribe_category(request):
    # Достаем текущего пользователя
    user = request.user
    # Получаем ссылку из адресной строки и берем pk как id категории
    id = request.META.get('HTTP_REFERER')[-1]
    # Получаем текущую категорию
    category = Category.objects.get(id=id)
    print(id)
    # Создаем связь между пользователем и категорией
    category.subscribers.add(user)
    category = f'{category}'
    email = f'{user.email}'
    send_mail_subscribe.delay(category, email)
    return redirect('/')


@login_required
def unsubscribe_category(request):
    # Достаем текущего пользователя
    user = request.user
    # Получаем ссылку из адресной строки и берем pk как id категории
    id = request.META.get('HTTP_REFERER')[-1]
    # Получаем текущую категорию
    category = Category.objects.get(id=id)
    # Разрываем связь между пользователем и категорией
    category.subscribers.remove(user)
    category = f'{category}'
    email = f'{user.email}'
    send_mail_unsubscribe.delay(category, email)

    return redirect('/')
