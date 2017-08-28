from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^quest/$', views.quest, name='quest'),
    url(r'^prediction/$', views.prediction, name='prediction'),
    url(r'^estimation/$', views.estimation, name='estimation')
]