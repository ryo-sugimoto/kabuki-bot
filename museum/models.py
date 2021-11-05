from django.db import models

# Create your models here.
from django.conf import settings
from django.utils import timezone


class Store(models.Model):
    """店舗"""
    name = models.CharField('店名', max_length=255)

    class Meta:
        verbose_name = '店舗'
        verbose_name_plural = '店舗'

    def __str__(self):
        return self.name


class Staff(models.Model):
    """店舗スタッフ"""
    name = models.CharField('表示名', max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='ログインユーザー', on_delete=models.CASCADE
    )
    store = models.ForeignKey(Store, verbose_name='店舗', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'store'], name='unique_staff'),
        ]
        verbose_name = 'スタッフ'
        verbose_name_plural = 'スタッフ'

    def __str__(self):
        return f'{self.store.name} - {self.name}'


class Schedule(models.Model):
    """予約スケジュール."""
    start = models.DateTimeField('開始時間')
    end = models.DateTimeField('終了時間')
    name = models.CharField('予約者名', max_length=255)
    email = models.CharField('メールアドレス', max_length=255, default='メールアドレス@')
    number = models.CharField('電話番号', max_length=255,blank=True, null=True, default='電話番号')
    staff = models.ForeignKey('Staff', verbose_name='スタッフ', on_delete=models.CASCADE,blank=True, null=True)

    class Meta:
        verbose_name = 'スケジュール'
        verbose_name_plural = 'スケジュール'

    def __str__(self):
        start = timezone.localtime(self.start).strftime('%Y/%m/%d %H:%M:%S')
        end = timezone.localtime(self.end).strftime('%Y/%m/%d %H:%M:%S')
        return f'{self.name} {start} ~ {end} {self.staff}'




class Post(models.Model):
    title = models.CharField(max_length=200,default='タイトル')
    price = models.CharField(max_length=200,blank=True, null=True)
    text = models.TextField(max_length=100000,blank=True, null=True,default='本文')
    created_date = models.DateTimeField('制作日',default=timezone.now,null=True)
    published_date = models.DateTimeField('発表日',blank=True, null=True)
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'メニュー'
        verbose_name_plural = 'メニュー'

class News(models.Model):
    GENRE_CHOICES = (
        (u'日記', u'日記'),
        (u'お得情報', u'お得情報'),
        (u'お知らせ', u'お知らせ'),
        (u'その他', u'その他'),
    )
    genre = models.CharField('ジャンル',max_length=200,blank=True, null=True, choices=GENRE_CHOICES)
    title = models.CharField('タイトル',max_length=200,blank=True, null=True)
    text = models.TextField('本文',blank=True, null=True)
    created_date = models.DateTimeField('制作日',default=timezone.now,null=True)
    published_date = models.DateTimeField('発表日',blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    class Meta:
        verbose_name = 'ニュース'
        verbose_name_plural = 'ニュース'
    
    def __str__(self):
        return self.title


class Profile(models.Model):
    title = models.CharField('名前',max_length=200,blank=True, null=True)
    text = models.TextField('自己紹介',blank=True, null=True)
    created_date = models.DateTimeField('制作日',default=timezone.now,null=True)
    published_date = models.DateTimeField('発表日',blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    class Meta:
        verbose_name = 'プロフィール'
        verbose_name_plural = 'プロフィール'

    def __str__(self):
        return self.title


class PictureForPost(models.Model):
    post = models.ForeignKey('museum.Post', on_delete=models.CASCADE, related_name='pictureforpost')
    avator = models.CharField('URL',max_length=200,blank=True, null=True)
    

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.avator
    
    class Meta:
        verbose_name = 'メニュー写真'
        verbose_name_plural = 'メニュー写真'


class PictureForNews(models.Model):
    news = models.ForeignKey('museum.News', on_delete=models.CASCADE, related_name='picturefornews')
    avator = models.CharField('URL',max_length=200,blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.avator

    class Meta:
        verbose_name = 'ニュース写真'
        verbose_name_plural = 'ニュース写真'

class PictureForProfile(models.Model):
    profile = models.ForeignKey('museum.Profile', on_delete=models.CASCADE, related_name='pictureforprofile')
    avator = models.CharField('URL',max_length=200,blank=True, null=True)
    

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.avator
    
    class Meta:
        verbose_name = 'ブログ写真'
        verbose_name_plural = 'ブログ写真'