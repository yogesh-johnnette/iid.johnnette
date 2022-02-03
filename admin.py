from django.contrib import admin
from .models import Order, OrderItem, Item, Lesson, Query, Organization, PilotList, Testimonial, Gallery, IIDLocations, TrainingSchedule, Webinar
class MembershipInline(admin.TabularInline):
    model = Order.items.through


class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration', 'online_course', 'expiry')


class GalleryAdmin(admin.ModelAdmin):
    list_display = ('batch_no', 'course', 'location', 'position')


class PilotAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'date', 'course', 'certificate_no')
    list_filter = ('course',)

class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'slug', 'position')


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')


class QueryAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone')


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'certificate_no')


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'ordered')
    list_filter = ('item', 'ordered')

class IIDLocationsAdmin(admin.ModelAdmin):
    list_display = ('city', 'email1', 'type')

class TrainingScheduleAdmin(admin.ModelAdmin):
    list_display = ('city', 'date', 'coursename')    

class OrderAdmin(admin.ModelAdmin):

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('user', 'transaction', 'ordered', 'ordered_date', 'start_date')
    list_filter = ('ordered', 'ordered_date')
    search_fields = ('user__first_name', 'user__last_name', 'transaction__transaction_id', 'items__item__title',
                     'items__item__slug',)
    filter_horizontal = ('items',)
    ordering = ['-ordered_date']
    exclude = ('items',)
    inlines = [
        MembershipInline,
    ]

class WebinarAdmin(admin.ModelAdmin):
    list_display = ('date', 'topic')    

admin.site.register(Item, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(PilotList, PilotAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(IIDLocations,IIDLocationsAdmin)
admin.site.register(TrainingSchedule,TrainingScheduleAdmin)
admin.site.register(Webinar, WebinarAdmin)
