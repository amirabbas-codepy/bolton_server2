"""
URL configuration for boltenict project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from app_bolten.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', easy_login, name='login'),
    path('home/', home_view, name='home'),
    path('logout/', logout_view, name='logout'),
    path('createtr/', traket_item_mpage, name='tr'),
    path('deltr/', delete_news_item, name='del'),
    path('000999/', send_all_emails, name='0000'),
    path('taskemails/', send_news_with_emails, name='task_view'),
]
