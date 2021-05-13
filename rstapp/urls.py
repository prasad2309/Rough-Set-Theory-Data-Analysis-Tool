from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("ajax/", views.using_ajax, name="ajax"),
    path("ajaxjson/", views.ajaxjson, name="ajaxjson"),
    path("usage/", views.usage, name="usage"),

]
