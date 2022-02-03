from django.db import models
from account.models import Account
from django.shortcuts import reverse
from payu.models import Transaction
from datetime import datetime
from django.utils.timezone import make_aware, make_naive
from ckeditor.fields import RichTextField
from store.models import KingOrder
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    slug = models.SlugField()
    duration = models.CharField(max_length=10, null=True)
    image = models.ImageField(upload_to='CourseImages/',help_text=' please upload  1300*600 ')
    online_course = models.NullBooleanField(blank=False, null=False)  # default is None
    expiry = models.DurationField(verbose_name="Course Expiry", blank=False, null=False, help_text='Eg: 30 days')
    description1 = models.CharField(max_length=50, blank=True, null=True)
    description2 = models.CharField(max_length=50, blank=True, null=True)
    description3 = models.CharField(max_length=50, blank=True, null=True)
    description4 = models.CharField(max_length=50, blank=True, null=True)
    description5 = models.CharField(max_length=50, blank=True, null=True)
    test_link = models.CharField(verbose_name='Test Link', max_length=250, blank=True, null=True)
    text_book = models.FileField(verbose_name='Text Book', upload_to='Text Book/', blank=True, null=True)
   
    
    class Meta:
        verbose_name = 'COURSE'
        verbose_name_plural = 'COURSES'
       

    def __str__(self):
        return self.title

    def get_add_to_cart_url(self):
        return reverse("app:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("app:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def get_lesson_list(self):
        return reverse("account:lesson_list", kwargs={
            'slug': self.slug
        })

    def get_absolute_url(self):
        return reverse("app:course-detail", kwargs={
            'slug': self.slug
        })

    

class OrderItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Course")

    class Meta:
        verbose_name = 'COURSE PURCHASED'
        verbose_name_plural = 'COURSES PURCHASED'

    def __str__(self):
        return self.item.title

    def get_total_item_price(self):
        return self.item.price

    def get_item(self):
        return self.item

    #
    def course_age(self):
        order = self.order_set.all()[0]
        age = make_aware(datetime.now()) - order.ordered_date
        course = self.item
        if not course.online_course or age <= course.expiry:
            return True
        else:
            return False

    # returns the date on which, the course will expire
    def get_expiry_date(self):
        order = self.order_set.all()[0]
        course = self.item
        exp_date = order.ordered_date + course.expiry
        return make_naive(exp_date)

    def get_order_transaction(self):
        order = self.order_set.all()[0]
        transaction = order.transaction
        if transaction:
            return transaction.transaction_id
        else:
            return None


class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE,blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, blank=True, null=True)
    invoice = models.FileField(upload_to='Invoice/', null=True, blank=True)

    class Meta:
        verbose_name = 'ORDER'
        verbose_name_plural = 'ORDERS'

    def __str__(self):
        return self.user.first_name+str(' ')+self.user.last_name

    def get_total(self):
        total = 0
        ss=KingOrder.objects.get(user= self.user,ordered=False)
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total+ss.get_total()

    def get_total1(self):
        total = 0
        
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total
    
    


class Lesson(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=120)
    course = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField()
    thumbnail = models.ImageField(null=True, blank=True, upload_to='LessonThumb/',help_text='please upload high resolution images')
    video_file = models.FileField(upload_to='Lesson Videos/')
    description1 = models.CharField(max_length=50, blank=True, null=True)
    description2 = models.CharField(max_length=50, blank=True, null=True)
    description3 = models.CharField(max_length=50, blank=True, null=True)
    description4 = models.CharField(max_length=50, blank=True, null=True)
    description5 = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Course Lesson'
        verbose_name_plural = 'Course Lessons'

    def __str__(self):
        return self.title
    

class Query(models.Model):
    first_name = models.CharField(verbose_name="First Name", max_length=20)
    last_name = models.CharField(verbose_name="Last Name", max_length=20)
    email = models.EmailField(verbose_name="Email", max_length=50)
    phone = models.CharField(verbose_name="Phone No.", max_length=20)
    query = models.TextField(verbose_name="Query")
    Location = models.CharField(verbose_name="Location", max_length=20, null=True)

    class Meta:
        verbose_name = 'Query'
        verbose_name_plural = 'Queries'

    def __str__(self):
        return self.email


class Organization(models.Model):
    name = models.CharField(verbose_name="Organization", max_length=50)
    location = models.CharField(verbose_name="Location", max_length=30)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return self.name


class PilotList(models.Model):
    name = models.CharField(verbose_name="Pilot Name", max_length=30)
    organization = models.CharField(verbose_name="Organization", max_length=50)
    date = models.DateField()
    course = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    certificate_no = models.CharField(verbose_name="Certificate Number", max_length=30)


    class Meta:
        verbose_name = "Pilot"
        verbose_name_plural = "Pilot List"

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    name = models.CharField(verbose_name="Student Name", max_length=30)
    location = models.CharField(verbose_name="Location", max_length=20)
    certificate_no = models.CharField(verbose_name="Certificate No", max_length=20)
    video_url = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return self.name


class Gallery(models.Model):
    batch_no = models.CharField(verbose_name="Batch No", max_length=3)
    course = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    location = models.CharField(verbose_name="Location", max_length=20)
    image = models.ImageField(upload_to='Gallery/',help_text='Image resolution must be 800px * 450px')
    position = models.AutoField(primary_key=True)

    class Meta:
        verbose_name = 'Batch'
        verbose_name_plural = 'Gallery'

    def __str__(self):
        return self.batch_no

    def clean(self):
        w,h=get_image_dimensions(self.image)
        
        file_size=self.image.file.size

        if file_size <100000:
            raise ValidationError("Size of the image must be > 100 KB and < 2 MB")

        if file_size >2000000:
             raise ValidationError("Size of the image must be < 2 MB and > 100 KB")

        if w<800 or w>800 and h<450 or h>450:
            raise ValidationError("Image resolution must be 800px x 450px")
    

class IIDLocations(models.Model):
    choice = [('Head_Office','Head Office'),('Partners','Partners'),('Franchisee','Franchisee')]
    city = models.CharField(max_length=100)
    mapiframe = models.TextField()
    Address = models.TextField()
    Phone1 = models.CharField(max_length=14)
    Phone2 = models.CharField(max_length=14,blank=True,null=True)
    email1 = models.EmailField(default="",null=True)
    email2 = models.EmailField(default="",blank=True,null=True)
    type = models.CharField(max_length=100,choices=choice,default="Franchisee")


    def __str__(self):
        return self.city

    class Meta:
        verbose_name = 'IID Location'
        verbose_name_plural = 'IID Locations'


class TrainingSchedule(models.Model):

    city = models.ForeignKey(IIDLocations,on_delete=models.CASCADE)
    date = models.DateField()
    coursename = models.ForeignKey(Item,on_delete=models.CASCADE)
    objects=models.Manager()
    
    def callme(self):
        return str(self.coursename.description1) 

    def __str__(self):
        return str("Traning" + str(self.id))

    def callme2(self):
        return str(self.coursename.description2)

    def get_absolute_url(self):
        self.slug="app:course-detail/"+self.coursename.title
        t=str()
        t="app:course-detail/"+self.coursename.title
        return reverse("app:course-detail" , kwargs={"slug": self.slug})

    def sum(self):
        s=self.coursename.slug
        return str(s)
    
    class Meta:
        verbose_name = 'Training Schedule'
        verbose_name_plural = 'Training Schedule'
        

class Webinar(models.Model):
    date=models.DateField(verbose_name="Date")
    topic=models.CharField(verbose_name="Topic", max_length=200)
    registration_url=models.URLField(verbose_name="Registration Link", max_length=200)
    description1 = models.CharField(verbose_name="Speaker 1", max_length=50, blank=True, null=True)
    description2 = models.CharField(verbose_name="Speaker 2", max_length=50, blank=True, null=True)
    description3 = models.CharField(verbose_name="Speaker 3", max_length=50, blank=True, null=True)
    description4 = models.CharField(verbose_name="Speaker 4", max_length=50, blank=True, null=True)
    description5 = models.CharField(verbose_name="Speaker 5", max_length=50, blank=True, null=True)

    def __str__(self):
        return "Webinar on "+str(self.date)
    
    class Meta:
        verbose_name = 'Webinar'
        verbose_name_plural = 'Webinars'
