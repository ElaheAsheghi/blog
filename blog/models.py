from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels
from django.urls import reverse
from django_resized import ResizedImageField
import os
from django.template.defaultfilters import slugify

#Managers
class PublishedManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

# Create your models here.
class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'
        REJECTED = 'RJ', 'Rejected'
    CATEGORY_CHOICES = (
        ('تکنولوژی', 'تکنولوژی'),
        ('علمی', 'علمی'),
        ('سایر', 'سایر'),  
    )
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PUBLISHED, verbose_name="وضعیت")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts", verbose_name="نویسنده")
    title = models.CharField(max_length=250, verbose_name="عنوان")
    description = models.TextField(verbose_name="متن پست")
    slug = models.SlugField(max_length=250, verbose_name="اسلاگ", default=title)
    #DATE
    publish = jmodels.jDateTimeField(default=timezone.now, verbose_name="زمان انتشار")
    created = jmodels.jDateTimeField(auto_now_add=True)
    updated = jmodels.jDateTimeField(auto_now=True)
    reading_time = models.PositiveBigIntegerField(default=0, verbose_name="زمان مطالعه")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="سایر", verbose_name="دسته بندی")

    objects = models.Manager()
    Published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])    
        ]

        verbose_name = "پست"
        verbose_name_plural = "پست ها"

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id])
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        for img in self.images.all():
            storage, path = img.image_file.storage, img.image_file.path
            storage.delete(path)
        super().delete(*args, **kwargs)

        
    
class Ticket(models.Model):
    message = models.TextField(verbose_name="پیام")
    name = models.CharField(max_length=250, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=11, verbose_name="شماره تماس")
    subject = models.CharField(max_length=250, verbose_name="موضوع")

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت ها"

    def __str__(self):
         return self.subject   
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="پست")
    name = models.CharField(max_length=250, verbose_name="نام")
    body = models.TextField(verbose_name="کامنت")
    created = jmodels.jDateTimeField(auto_now_add=True)
    updated = jmodels.jDateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created'])]
        verbose_name = "کامنت"
        verbose_name_plural = "کامنت ها"

    def __str__(self):
        return f"{self.name} : {self.post}"
    

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images",\
                              verbose_name="تصویر")
    image_file = ResizedImageField(upload_to="post_images/%Y/%m/%d", size= [500, 500],\
                                   quality= 75, crop= ['middle', 'center'])
    title = models.CharField(max_length=250, verbose_name="عنوان", null= True, blank= True)
    description = models.TextField(verbose_name= "توضیحات", null= True, blank= True)
    created = jmodels.jDateTimeField(auto_now_add= True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created'])]
        verbose_name = "تصویر"
        verbose_name_plural = "تصویر ها"
    
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.post.id])
    

    def __str__(self):
        return self.title if self.title else self.image_file.name

    def delete(self, *args, **kwargs):
        storage, path = self.image_file.storage, self.image_file.path
        storage.delete(path)
        super().delete(*args, **kwargs)


class Account(models.Model):
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    date_of_birth = jmodels.jDateField(verbose_name="تاریخ تولد", blank=True, null=True)
    bio = models.TextField(verbose_name="بایو", null=True, blank=True)
    photo = ResizedImageField(upload_to="account_images/", size=[500, 500], quality=60,\
                              crop=['middle', 'center'], blank=True, null=True)
    job = models.CharField(max_length=250, verbose_name="شغل", null=True, blank=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "اکانت"
        verbose_name_plural = "اکانت ها"


    