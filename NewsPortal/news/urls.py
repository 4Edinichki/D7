from django.urls import path

from .views import PostList, PostDetail, create_post, NewsCreate, PostUpdate, PostDelete, ArticleCreate, ArticleList, \
    ClassMessage, CategoryList, add_subscribe, post, IndexView

urlpatterns = [
    path('news/', PostList.as_view(), name='post_list'),
    path('article/', ArticleList.as_view(), name='article_list'),

    path('<int:pk>', PostDetail.as_view(), name='post_detail'),

    path('create_news', NewsCreate.as_view(), name='news_create'),
    path('create_news/post', post, name='post_mess'),
    path('create_article', ArticleCreate.as_view(), name='article_create'),

    path('news/<int:pk>/delete', PostDelete.as_view(), name='news_delete'),
    path('article/<int:pk>/delete', PostDelete.as_view(), name='article_delete'),

    path('news/<int:pk>/update', PostUpdate.as_view(), name='news_update'),
    path('article/<int:pk>/update', PostUpdate.as_view(), name='article_update'),
    path('message/', ClassMessage.as_view(), name='message'),

    path('sub/', CategoryList.as_view(), name='category'),  # Путь к списку категорий с кнопками на подписку
    path('sub/subscribe/', add_subscribe, name='subscribe'),

    path('', IndexView.as_view()),
]
