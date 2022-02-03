from django.urls import path
from django.views.generic import TemplateView
from . import views

from .views import (
    add_to_cart,
    home_view,
    contact_view,
    about_view,
    letters,
    HomeView,
    remove_from_cart,
    OrderSummaryView,
    CheckoutView,
    success,
    failure,
    cancel,
    error404,
    viewpdf,
    organizations_trained,
    pilot_list,
    gallery,
    testimonial,
    course_detail,
    IIDLocations,
    TrainingSchedule,
    franchise,
    webinar,
    databaserror,
    CheckoutView_student,
    Domptest

)

app_name = 'app'

urlpatterns = [

    # URLs for navbar and homepage
    path('', home_view, name="home"),
    path('courses_list/', HomeView.as_view(), name='courses'),
    path('about/', about_view, name="about"),
    path('gallery/', gallery, name="gallery"),
    path('instructors/', TemplateView.as_view(template_name='app/instructors.html'), name="instructors"),
    path('FAQs/', TemplateView.as_view(template_name='app/faqs.html'), name="FAQs"),
    path('DGCA/', TemplateView.as_view(template_name='app/dgca.html'), name="DGCA"),
    path('certification/', TemplateView.as_view(template_name='app/certification.html'), name="certification"),
    path('pilot-list/', pilot_list, name="pilot-list"),
    path('drone-jobs/', TemplateView.as_view(template_name='app/about_us.html'), name="drone-jobs"),
    path('testimonials/', testimonial, name="testimonials"),
    path('news-and-media/', TemplateView.as_view(template_name='app/news-events.html'), name="news-and-events"),
    path('infrastructure/', TemplateView.as_view(template_name='app/infrastructure.html'), name="infrastructure"),
    path('organizations-trained/', organizations_trained, name="organizations"),
    path('contact/', contact_view, name="contact"),
    path('satisfactory-letters/', letters, name="letters"),
    path('error/', error404, name="error"),
    path('terms-and-conditions/', TemplateView.as_view(template_name='app/terms-conditions.html'), name="t-c"),
    path('indemnity/', TemplateView.as_view(template_name='app/indemnity.html'), name="indemnity"),
    path('privacy/', TemplateView.as_view(template_name='app/privacy.html'), name="privacy"),
    path('cookies/', TemplateView.as_view(template_name='app/cookies.html'), name="cookies"),
    #path('franchise/', TemplateView.as_view(template_name='app/franchise.html'), name="franchise"),
    path('franchise/', franchise, name="franchise"),
    
    # URLs for Courses, Cart, Payment and pdf
    path('course/<slug>/', course_detail, name='course-detail'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('success/', success, name='order.success'),
    path('failure/', failure, name='order.failure'),
    path('cancel/', cancel, name='order.cancel'),

    path('pdf_view/<slug:tid>', viewpdf, name="pdf_view"),

    path('pdf_template/', TemplateView.as_view(template_name='app/invoice.html')),

    path('iid-locations',IIDLocations.as_view(),name="iid-loc"),
    path('training-schedule',TrainingSchedule.as_view(),name="tr-schedule"),
    path('webinar-events',webinar, name="webinar"),
    path("databaserror",databaserror,name="databaserror"),
    # path("success",success,name="success"),
    path("CheckoutView_student",CheckoutView_student.as_view(),name="CheckoutView_student"),
    path('certificationform',Domptest,name="Domptest")
    
]
