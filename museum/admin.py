from django.contrib import admin
from .models import Store, Staff, Schedule, Post, News, Profile, PictureForPost, PictureForNews

# Register your models here.
admin.site.register(Store)
admin.site.register(Staff)
admin.site.register(Schedule)
admin.site.register(Post)
admin.site.register(News)
admin.site.register(Profile)
admin.site.register(PictureForPost)
admin.site.register(PictureForNews)