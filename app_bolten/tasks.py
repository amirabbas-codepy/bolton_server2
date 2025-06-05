
from background_task import background
from django.shortcuts import render, redirect, HttpResponse
from .models import *
from datetime import datetime, date, timedelta
import requests
import feedparser
from django.core.mail import send_mail, EmailMultiAlternatives


@background(schedule=0)
def send_emails():
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
                print('news.news_published_date == pubdate')
                print(news.news_published_date == pubdate)
                print(news.title == title)
                print(news.summary == summary)
                news.update_news_time = news.update_news_time + timedelta(news.frequency_days)
                news.save()
            
                # return redirect(home_view)
            else:
                news.title = title
                news.link = link
                news.update_news_time = news.update_news_time + timedelta(news.frequency_days)
                news.news_published_date = pubdate
                news.save()
                

                # print("Saved updated news.")

                # send_mail(
                #         news.title,           
                #         news.link,            
                #         'ghafarsoft@gmail.com',     
                #         [subscriber.email],     
                #         fail_silently=False,
                #     )
                subject = news.keyword
                from_email = "ghafarsoft@gmail.com"
                to = [news.user.email]

                text_content = "این ایمیل از فرمت HTML پشتیبانی نمی‌کند."
                
                html_content = f"""
                <html>
                <body>
                    <h2>Hi !!! {news.user.email}</h2>
                    <h2>Hi !!! {news.title}</h2>
                    <a href={news.summary}</a>
                    <a href={news.link}>Site Link</a>
                    
                </body>
                </html>
                """
                
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                
                msg.attach_alternative(html_content, "text/html")
                
                msg.send()
        else:
            print('not found')
