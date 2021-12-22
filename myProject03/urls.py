"""myProject03 URL Configuration

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
from django.urls import path
from django.contrib.auth import views as auth_views

from myapp03 import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.list),
    path('write_form/', views.write_form),
    path('list/', views.list),
    path('insert/', views.insert),

    path('download_count/',views.download_count),
    path('download/',views.download),

    path('detail/<int:board_id>/', views.detail),
    path('comment_insert/', views.comment_insert),

    path('delete/<int:board_id>/', views.delete),
    path('update_form/<int:board_id>/', views.update_form),
    path('update/', views.update),
    #############
    path('movie/', views.movie),
    path('movie_chart/', views.movie_chart),
    path('weather/',views.weather),
    path('map/',views.map),
    




    #####
    path('login/', 
        auth_views.LoginView.as_view(template_name='common/login.html'),
        name='login'),   #import
    path('logout/', auth_views.LogoutView.as_view(),name='logout'),    
    path('signup/', views.signup),
    
]
