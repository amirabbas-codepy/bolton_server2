from django.shortcuts import render, redirect, HttpResponse
from .froms import *
from .models import *
from datetime import date, datetime, timedelta
import requests
import feedparser
from django.core.mail import send_mail, EmailMultiAlternatives
from background_task.models import Task
from .tasks import send_emails
# Create your views here.

def easy_login(request):
    # if request.method == 'GET':
        # email = request.COOKIES.get('subscriber_email')
        # if not email:
        #     return redirect(easy_login)  

        # subscriber = Subscriber.objects.filter(email=email).first()
        # if not subscriber:
        #     return redirect(easy_login)

    #     return redirect(home_view)

    if request.method == 'POST':
        data = LoginForm(request.POST)
        if data.is_valid():
            form_data = data.cleaned_data
            email = form_data.get('email')
        # email = request.POST.get('email')
        if email:
            print('email get')
            username = email.split('@')
            subscriber, created = Subscriber.objects.get_or_create(email=email, username=username[0])
            response = redirect(home_view)  # صفحه بعدی
            response.set_cookie('subscriber_email', email, max_age=3600*24*7)  # کوکی 7 روزه
            
            return response
    # فرم ثبت ایمیل
    # return render(request, 'index.html')

    
    form = LoginForm()
    print('last here')
    return render(request=request, template_name='login.html', context={'form':form})

def home_view(request):
    email = request.COOKIES.get('subscriber_email')
    if not email:
        return redirect(easy_login)  

    subscriber = Subscriber.objects.filter(email=email).first()
    print(subscriber.email)
    if not subscriber:
        return redirect(easy_login)
    
    context = {
        'subscriber': subscriber,
        'traker':NewsItem.objects.filter(user=subscriber)
    }
    return render(request, 'index.html', context)

def logout_view(request):
    response = redirect(easy_login)  
    response.delete_cookie('subscriber_email') 
    return response

def traket_item_mpage(request):
    email = request.COOKIES.get('subscriber_email')
    if not email:
        return redirect(easy_login)

    subscriber = Subscriber.objects.filter(email=email).first()
    if not subscriber:
        return redirect(easy_login)

    if request.method == 'POST':
        data = TraketForm(request.POST)
        if data.is_valid():
            form_data = data.cleaned_data
            keyword = form_data.get('keyword')
            frequency_days = form_data.get('frequency_days')

              
            url = f'https://news.google.com/rss/search?q={keyword}&hl=en-US&gl=US&ceid=US:en'
            response = requests.get(url)
            feed = feedparser.parse(response.content)


            if feed.entries:
                #BUG FIX JUST 1 URL
                res = feed.entries[0].link
                first_entry = feed.entries[0]
                title = first_entry.title
                summary = first_entry.summary  
                pubdate = first_entry.published
                # tra = TrackedItem.objects.create(keyword=keyword, frequency_days=frequency_days, user=subscriber)

                time_ = datetime.now() + timedelta(frequency_days)
                NewsItem.objects.create(title=title, 
                                        link=res, 
                                        update_news_time=time_, 
                                        user=subscriber, 
                                        keyword=keyword, 
                                        summary=summary, 
                                        frequency_days=frequency_days, 
                                        news_published_date=pubdate)

                return render(request=request, template_name='traket.html', context={'mess':'success'})
                # link = first_entry.link
                # print("Title:", title)
                # print(summary)
                
            else:
                return redirect(home_view)
                # print(entry.title)
                # print(entry.link)
                # print(entry.published)

            
            # return render(request=request, template_name='index.html', context={'message':''})
            
    form = TraketForm()
    return render(request=request, template_name='traket.html', context={'form':form})

def send_all_emails(request):
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
                print(news.link)

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

    return redirect(easy_login)

def delete_news_item(request):
    if request.method == 'POST':
        email = request.COOKIES.get('subscriber_email')
        if not email:
            return redirect(easy_login)

        subscriber = Subscriber.objects.filter(email=email).first()
        if not subscriber:
            return redirect(easy_login)
        
        form_data = DeletedForm(request.POST)
        if form_data.is_valid():
            data = form_data.cleaned_data
            id_ = data.get('news_id')

            try:
                news = NewsItem.objects.filter(user=subscriber).get(id=id_)
                news.delete()
                return render(request=request, template_name='delpage.html', context={'mess':'Deleted News Success'})
            
            except:
                return render(request=request, template_name='delpage.html', context={'mess':'News Not Fund'})
    
    form = DeletedForm()
    context = {'form':form}
    return render(request=request, template_name='delpage.html', context=context)

def send_news_with_emails(request):
    # بررسی وجود تسک ثبت شده با نام تسک ما
    task_exists = Task.objects.filter(task_name='app_bolten.tasks.send_emails').exists()
    print(task_exists)
    if not task_exists:
        send_emails(repeat=100)
        return HttpResponse("Task scheduled successfully!")
    else:
        return HttpResponse("Task is already scheduled.")

