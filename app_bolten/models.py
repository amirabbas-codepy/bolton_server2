from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Subscriber(AbstractUser):
    
    def __str__(self):
        return self.email


class NewsItem(models.Model):
    # فیلدهای قبلی
    title = models.CharField(max_length=500)
    link = models.URLField()
    published = models.DateTimeField(auto_now_add=True)
    update_news_time = models.DateField(null=True)
    image_url = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    keyword = models.CharField(max_length=200)
    user = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    frequency_days = models.IntegerField(default=7)
    time_updated = models.DateTimeField(auto_now=True, null=True)
    news_published_date = models.CharField(null=True, max_length=250)

    def __str__(self):
        return self.keyword

class BulletinSendHistory(models.Model):
    tracked_item = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='send_logs')
    news_items = models.ManyToManyField(NewsItem)  # مجموعه‌ای از اخبار ارسال‌شده
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)  # آیا ایمیل موفق بود؟
    error_message = models.TextField(blank=True, null=True)  # اگر ارسال شکست خورد

    def __str__(self):
        return f"بولتن {self.tracked_item.keyword} برای {self.tracked_item.user.username}"
