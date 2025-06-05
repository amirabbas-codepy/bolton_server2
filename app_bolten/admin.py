from django.contrib import admin
from .models import *

admin.site.register([NewsItem, Subscriber, BulletinSendHistory])

# Register your models here.
