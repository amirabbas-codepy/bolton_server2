
import os
import django
import requests
import feedparser
from datetime import date, timedelta
from django.core.mail import EmailMultiAlternatives


# تنظیمات جنگو رو لود کن
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from .models import NewsItem

# حالا کد ارسال ایمیل رو مستقیم بنویس

today = date.today()
ni = NewsItem.objects.filter(update_news_time__lte=today)

print(f"Found {ni.count()} news items to update.")

for news in ni:
    print(f'Updating news id={news.id}, keyword={news.keyword}')
    
    url = f'https://news.google.com/rss/search?q={news.keyword}&hl=en-US&gl=US&ceid=US:en'
    response = requests.get(url)
    feed = feedparser.parse(response.content)

    if feed.entries:
        first_entry = feed.entries[0]
        title = first_entry.title
        link = first_entry.link
        summary = first_entry.summary
        pubdate = first_entry.published
      
        if (news.news_published_date == pubdate) or (news.title == title) or (news.summary == summary):
            print('No updates for this news item.')
            news.update_news_time = news.update_news_time + timedelta(news.frequency_days)
            news.save()
        else:
            news.title = title
            news.link = link
            news.update_news_time = news.update_news_time + timedelta(news.frequency_days)
            news.news_published_date = pubdate
            news.summary = summary
            news.save()

            subject = news.keyword
            from_email = "ghafarsoft@gmail.com"
            to = [news.user.email]

            text_content = "این ایمیل از فرمت HTML پشتیبانی نمی‌کند."
            
            html_content = f"""
            <html>
            <body>
                <h2>Hi !!! {news.user.email}</h2>
                <h2>{news.title}</h2>
                <p>{news.summary}</p>
                <a href="{news.link}">Site Link</a>
            </body>
            </html>
            """
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
    else:
        print('No feed entries found.')
