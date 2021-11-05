import datetime
from django.conf import settings
from django.db.models import Q

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError

from django.shortcuts import render, get_object_or_404
from django.views import generic

from django.shortcuts import redirect
from django.utils import timezone
from django.template import Context, Template
from django.template.loader import render_to_string
from .models import Store, Staff, Schedule, Post, News, Profile, PictureForPost, PictureForNews

from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def home(request):
    return render(request, 'museum/home.html')


def send_simple_message(context, staff, schedule):
    storemail = "bacistyle2020@gmail.com"
    subject = 'Beauty salon bijouの予約が完了しました'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [schedule.email,storemail]

    print(recipient_list)
    message = f"{schedule.name}様<br /><br />"
    message += f"Beauty salon bijouの予約が完了しました。<br /><br />"
    message += "予約日時："+context["h"]+"〜 <br />"
    message += f"スタッフ:{staff}"
    message += "<br /><br />"
    message += f"ご予約の変更は<a href=\"mailto:{storemail}\">こちら</a>まで"
    message += "<br /><br />※このメールは返信不可です。"
    message += f"お客様の電話番号<a href=\"tel:{schedule.number}\">{schedule.number}</a>"
    print(subject, message, email_from, recipient_list, message)
    print("res")
    print(send_mail(subject, message, email_from, recipient_list, html_message=message))
    return HttpResponse('Mail successfully sent')

class StoreList(generic.ListView):
    model = Store
    ordering = 'name'


class StaffList(generic.ListView):
    model = Staff
    ordering = 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store'] = self.store
        return context

    def get_queryset(self):
        store = self.store = get_object_or_404(Store, pk=self.kwargs['pk'])
        queryset = super().get_queryset().filter(store=store)
        return queryset


class StaffCalendar(generic.TemplateView):
    template_name = 'museum/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = get_object_or_404(Staff, pk=self.kwargs['pk'])
        today = datetime.date.today()

        # どの日を基準にカレンダーを表示するかの処理。
        # 年月日の指定があればそれを、なければ今日からの表示。
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        if year and month and day:
            base_date = datetime.date(year=year, month=month, day=day)
        else:
            base_date = today

        # カレンダーは1週間分表示するので、基準日から1週間の日付を作成しておく
        days = [base_date + datetime.timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]

        # 9時から18時まで1時間刻み、1週間分の、値がTrueなカレンダーを作る
        calendar = {}
        hours = ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00","18:30","19:00"]
        for hour in hours:
            row = {}
            for day in days:
                row[day] = True
            calendar[hour] = row

        # カレンダー表示する最初と最後の日時の間にある予約を取得する
        start_time = datetime.datetime.combine(start_day, datetime.time(hour=9, minute=0, second=0))
        end_time = datetime.datetime.combine(end_day, datetime.time(hour=19, minute=0, second=0))
        for schedule in Schedule.objects.filter(staff=staff).exclude(Q(start__gt=end_time) | Q(end__lt=start_time)):
            local_dt = timezone.localtime(schedule.start)
            booking_date = local_dt.date()
            booking_hour = local_dt.hour
            booking_minute = local_dt.minute
            booking_hour = str(booking_hour).zfill(2) + ":" + str(booking_minute).zfill(2)
            if booking_hour in calendar and booking_date in calendar[booking_hour]:
                calendar[booking_hour][booking_date] = False

        context['staff'] = staff
        context['calendar'] = calendar
        context['days'] = days
        context['start_day'] = start_day
        context['end_day'] = end_day
        context['before'] = days[0] - datetime.timedelta(days=7)
        context['next'] = days[-1] + datetime.timedelta(days=1)
        context['today'] = today

       
        return context

class Booking(generic.CreateView):
    model = Schedule
    fields = ('name','email',"number")
    template_name = 'museum/booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = get_object_or_404(Staff, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        staff = get_object_or_404(Staff, pk=self.kwargs['pk'])
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = int(self.kwargs.get('hour') / 100)
        minute = self.kwargs.get('hour') % 100
        #email = self.kwargs.get('email')
        start = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        end = datetime.datetime(year=year, month=month, day=day, hour=hour + 1, minute=minute)
        if Schedule.objects.filter(staff=staff, start=start).exists():
            messages.error(self.request, 'すみません、入れ違いで予約がありました。別の日時はどうですか。')
        else:
            schedule = form.save(commit=False)
            schedule.staff = staff
            schedule.start = start
            schedule.month = month
            schedule.day = day
            schedule.end = end
            schedule.save()
            context = {
            "m": str(month),
            "d": str(day),
            "h": str(start),
            }
            
            print(schedule.email)
            send_simple_message(context, staff, schedule)

            if minute == 0:
                start = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute+30)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour + 1, minute=minute)
                second = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                second.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour + 1 , minute=minute)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour + 1, minute=minute + 30)
                third = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                third.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour + 1, minute=minute + 30)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour + 2, minute=minute)
                fourth = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                fourth.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour -1, minute=minute+30)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
                fifth = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                fifth.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour -1, minute=minute)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour - 1, minute=minute+30)
                sixth = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                sixth.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour - 2, minute=minute+30)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour - 1, minute=minute)
                seventh = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                seventh.save()
            else:
                start = datetime.datetime(year=year, month=month, day=day, hour=hour+1, minute=0)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour + 1, minute=30)
                second = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                second.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour + 1 , minute=30)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour + 2, minute=0)
                third = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                third.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour + 2, minute=0)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour + 2, minute=30)
                fourth = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                fourth.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=0)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=30)
                fifth = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                fifth.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour -1, minute=30)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=0)
                sixth = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                sixth.save()
                start = datetime.datetime(year=year, month=month, day=day, hour=hour - 1, minute=0)
                end = datetime.datetime(year=year, month=month, day=day, hour=hour - 1, minute=30)
                seventh = Schedule(staff=staff, start=start, end=end, email=schedule.email, name=schedule.name)
                seventh.save()
       
        return redirect('museum:calendar', pk=staff.pk, year=year, month=month, day=day)


        

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    
    return render(request, 'museum/posts.html', {'posts': posts})



def post_show(request, post_id):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    post = Post.objects.all().get(id=post_id)
    pictureforpost = post.pictureforpost.all()
    return render(request, 'museum/post_show.html', {'posts': posts,'post': post, 'pictureforpost':pictureforpost})



def top(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    newss = News.objects.all()
    return render(request, 'museum/top.html', {'posts': posts, 'newss': newss})



def news(request):
    newss = News.objects.all()
    return render(request, 'museum/news.html', {'newss': newss})

def news_show(request, news_id):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    news = News.objects.all().get(id=news_id)
    picturefornews = news.picturefornews.all()
    return render(request, 'museum/news_show.html', {'posts': posts,'news': news, 'picturefornews':picturefornews})





def thanks(request):
    return render(request, 'museum/thanks.html')

def profile(request):
    profile = Profile.objects.all()
    return render(request, 'museum/profile.html',{'profiles': profile})

def terms(request):
    return render(request, 'museum/terms.html')

def aboutus(request):
    return render(request, 'museum/aboutus.html')

def map(request):
    return render(request, 'museum/map.html')


