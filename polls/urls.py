from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # 新規作成画面遷移
    path('create/', views.ToCreate, name='create'),
    path('create/regist/', views.regist, name='regist'),
    path('<int:question_id>/update/', views.update, name='update'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/edit/', views.edit, name='edit'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
