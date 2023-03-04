"""amgad_image_text_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home,name='home'),
    path('main', views.main_page,name='main_page'),
    path('upload_file', views.upload_file,name='upload_file'),
    path('img_to_table', views.img_to_table_view, name='img_to_table_view'),
    path('img_to_text', views.img_to_text_view, name='img_to_text_view'),
    path('pdf_to_text', views.pdf_to_text_view, name='pdf_to_text_view'),
    path('download_text', views.download_text, name='download_text'),


    # path('change_values',views.update_data,name='home'),
    # path('download',views.download_json,name='download_json'),
    # path('download_txt',views.download_txt,name='download_txt'),
    path('accounts/login/',views.login,name='login'),
    path('accounts/signup',views.signup,name='signup'),
    path('logout',views.logout_user,name='logout'),
]
 