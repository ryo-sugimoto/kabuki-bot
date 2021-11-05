from django.urls import path
from django.shortcuts import redirect
from . import views
app_name = 'museum'


urlpatterns = [
    path('store', views.StoreList.as_view(), name='store_list'),
    path('store/<int:pk>/staffs/', views.StaffList.as_view(), name='staff_list'),
    path('staff/<int:pk>/calendar/', views.StaffCalendar.as_view(), name='calendar'),
    path('staff/<int:pk>/calendar/<int:year>/<int:month>/<int:day>/', views.StaffCalendar.as_view(), name='calendar'),
    path('staff/<int:pk>/booking/<int:year>/<int:month>/<int:day>/<int:hour>/', views.Booking.as_view(), name='booking'),
    path('posts', views.post_list, name='post_list'),
    path('posts/<int:post_id>', views.post_show, name="post_show"),
    path('news', views.news, name="news"),
    path('news/<int:news_id>', views.news_show, name="news_show"),
    path('thanks', views.thanks, name='thanks'),
    path('profile', views.profile, name='profile'),
    path('terms', views.terms, name='terms'),
    path('aboutus', views.aboutus, name='aboutus'),
    path('map', views.map, name='map'),
    path('', views.top, name='top'),
    path('home', views.home, name='home'),
    path('send_test_mail', views.send_simple_message, name='send_test_mail'),
]