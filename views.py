from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, OrderItem, Order, Query, Organization, PilotList, Testimonial, Gallery, IIDLocations, TrainingSchedule, Webinar
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm, QueryForm
from account.models import Account
# from payu.models import Transaction
from django.core import exceptions
from store.models import KingOrder
############################
import hashlib
from django.template.context_processors import csrf, request
from .forms import PayUForm, QueryForm as qs
from uuid import uuid4
from .payu_methods import check_hash
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
# pdf imports
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.core.files import File
from django.core.files.storage import default_storage


# successful and failed transaction email imports
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# pagination in gallery imports
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from .models import TrainingSchedule as NotificationModel
from store.models import BillingAddress
# Home page



@csrf_protect
def home_view(request):
    # print(settings.EMAIL_HOST_USER)
    if request.method == "POST":
        form = QueryForm(request.POST or None)

        if form.is_valid():

            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            phone = request.POST['phone']
            query = request.POST['query']
            Location = request.POST['Location']

            obj = Query.objects.create(first_name=first_name, last_name=last_name, email=email, phone=phone,
                                       query=query,Location=Location)
            obj.save()

            # Sending email to self, if a query is submitted
            data = {
                'name': first_name + ' ' + last_name,
                'email': email,
                'phone': phone,
                'query': query,
                'Location': Location
            }
            subject = "New Query from Home Page"
            html_message = render_to_string('app/query_email.html', data)
            plain_message = strip_tags(html_message)
            from_email = None  # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
            to = 'director@iiodrones.com'  # This is a string, will be sent as a list
            fail_silently = False

            send_mail(subject, plain_message, from_email, [to], fail_silently,
                      html_message=html_message)
            if obj:
                messages.info(request, "Your query has been submitted!")
            return redirect('app:home')
        else:
            messages.error(request, "Invalid Captcha!")
    else:
        form = QueryForm()
    show     = Item.objects.all()
    return render(request, 'app/home.html', {'form': form,'show':show})


@csrf_protect
def contact_view(request):
    if request.method == "POST":
        form = QueryForm(request.POST or None)

        if form.is_valid():

            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            phone = request.POST['phone']
            query = request.POST['query']
            Location = request.POST['Location']

            obj = Query.objects.create(first_name=first_name, last_name=last_name, email=email, phone=phone,
                                       query=query,Location=Location)
            obj.save()

            # Sending email to self, if a query is submitted
            
            data = {
                'name': first_name + ' ' + last_name,
                'email': email,
                'phone': phone,
                'query': query,
                'Location': Location
            }
            subject = "New Query on Contact Page"
            html_message = render_to_string('app/query_email.html', data)
            plain_message = strip_tags(html_message)
            from_email = None  # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
            to = 'director@iiodrones.com'  # This is a string, will be sent as a list
            fail_silently = False

            send_mail(subject, plain_message, from_email, [to], fail_silently,
                      html_message=html_message)
            if obj:
                messages.info(request, "Your query has been submitted!")
            return redirect('app:contact')
        else:
            messages.error(request, "Invalid Captcha!")
    else:
        form = QueryForm()
    return render(request, 'app/contact_us.html', {'form': form})


def about_view(request):
    return render(request, 'app/about_us.html')


def letters(request):
    return render(request, 'app/satisfactory-letters.html')


# courses list view
class HomeView(ListView):
    model = Item
    template_name = "app/courses_list.html"
    paginate_by = 10


@csrf_protect
def course_detail(request, slug):
    try:
        if request.method == "POST":
            form = QueryForm(request.POST or None)

            if form.is_valid():

                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                email = request.POST['email']
                phone = request.POST['phone']
                query = request.POST['query']
                Location = request.POST['Location']

                obj = Query.objects.create(first_name=first_name, last_name=last_name, email=email, phone=phone,
                                           query=query,Location=Location)
                obj.save()

                # Sending email to self, if a query is submitted
                data = {
                    'name': first_name + ' ' + last_name,
                    'email': email,
                    'phone': phone,
                    'query': query,
                    'Location': Location
                }
                subject = "New Query on Course Detail Page"
                html_message = render_to_string('app/query_email.html', data)
                plain_message = strip_tags(html_message)
                from_email = None  
                to = 'director@iiodrones.com'  
                fail_silently = False

                send_mail(subject, plain_message, from_email, [to], fail_silently,
                          html_message=html_message)
                if obj:
                    messages.info(request, "Your query has been submitted!")
                return redirect('app:course-detail', slug)
            else:
                messages.error(request, "Invalid Captcha!")
        else:
            form = QueryForm()

        course = Item.objects.get(slug=slug)
        return render(request, 'app/{}.html'.format(slug), {'course': course, 'form': form})
    except ObjectDoesNotExist:
        return redirect('app:courses')


class CheckoutView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, *args, **kwargs):
        
        try:
            
            order = Order.objects.get(user=self.request.user, ordered=False)
            productsorder= KingOrder.objects.get(user=self.request.user,ordered=False)
          
            if order.get_total() != 0:
                if productsorder.get_total() != 0:
                    
                    try:
                        
                        s1=BillingAddress.objects.get(user=self.request.user)
                   
                        if s1:
                            productsorder.billing_address=s1
                            productsorder.save()
                   
                    except Exception as e:
                        
                        messages.info(self.request, "Fill out address Field ")
                        return redirect("account:address")        

             

            else:        
                return redirect("app:order-summary")    
            
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                'temp':productsorder
                
            }
            
            return render(self.request, "app/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("app:home")

    @method_decorator(csrf_protect)
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():

                # Payment process start from here

                # Valid payment option
                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'PU':

                    # Handling payu payments from here
                    # Get all the details that will be needed to create a payu form

                    # Payu payment process

                    initial = {'txnid': uuid4().hex,
                               'productinfo': self.request.user.first_name,
                               'amount': order.get_total(),
                               'firstname': self.request.user.first_name,
                               'email': self.request.user.email,
                               'phone': self.request.user.phone,
                               'lastname': self.request.user.last_name,
                               
                             
                               }

                    payurl = settings.PAYU_BASE_URL

                    # data1 is used to calculate hash value
                    data1 = {'txnid': initial['txnid'],
                             'productinfo': self.request.user.first_name,
                             'amount': order.get_total(),
                             'firstname': self.request.user.first_name,
                             'email': self.request.user.email}

                    # creating hash
                    hash_object = hashlib.sha512(b'randint(0,20)')
                    txnid = hash_object.hexdigest()[0:20]
                    hashh = ''
                    hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
                    data1['key'] = settings.PAYU_MERCHANT_KEY
                    hash_string = ''
                    hashVarsSeq = hashSequence.split('|')
                    for i in hashVarsSeq:
                        try:
                            hash_string += str(data1[i])
                        except Exception:
                            hash_string += ''
                        hash_string += '|'
                    hash_string += settings.PAYU_MERCHANT_SALT
                    hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()

                    # Create transaction record
                    Transaction.objects.create(transaction_id=data1.get('txnid'),
                                               amount=data1.get('amount'))

                    initial.update({'key': settings.PAYU_MERCHANT_KEY,
                                    'surl': self.request.build_absolute_uri(reverse('app:order.success')),
                                    'furl': self.request.build_absolute_uri(reverse('app:order.failure')),
                                    'curl': self.request.build_absolute_uri(reverse('app:order.cancel')),
                                    'hash': hashh,
                                    'service_provider': 'payu_paisa',
                                    
                                    })

                    # Once we have the information (initial dictionary) that you need to submit to payu
                    # create a payu_form, validate it and render response using
                    # template provided by PayU.

                    payu_form = PayUForm(initial)
                    if payu_form.is_valid():

                        # payu form is valid

                        context = {'form': payu_form,
                                   'action': payurl}

                        return render(self.request, 'app/payment2.html', context)

                    else:

                        return render(self.request, 'app/error.html')

                    # return redirect('app:payment', payment_option='payu')

                #elif payment_option == 'PP':

                    #Paypal Payment process

                    #return HttpResponse("<h1>This payment option is not working for now!<br>Please choose the other "
                                        #"payment option.</h1>")

                else:

                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect("app:order-summary")

            else:

                # The form is invalid
                return redirect("app:order-summary")

        except ObjectDoesNotExist:

            # No active order
            messages.warning(self.request, "You do not have an active order")
            return redirect("app:order-summary")


class OrderSummaryView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, *args, **kwargs):
        
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)        
        except:
            order= Order.objects.create(user=self.request.user,ordered=False)
            
            order.save()
          
        try:
            temp=KingOrder.objects.get(user=self.request.user,ordered=False)               
        except:
            temp=KingOrder.objects.create(user=self.request.user,ordered=False)
         
            temp.save()

        context = {
                'object': order,
                'temp':temp,
                'empty':True
                }
        if order.get_total1()==0 and temp.get_total()==0:
            context["temp"]=temp
            context["empty"]=False
        
        return render(self.request, 'app/order_summary.html', context)


@login_required(login_url='/login/')
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    

    bought_courses = Item.objects.filter(orderitem__user=request.user, orderitem__ordered=True)  # Purchased courses
    if item in bought_courses:
        
        messages.info(request, 'Course already purchased')
        return redirect('app:course-detail', slug=slug)
    else:
        
        order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            # order_item.quantity += 1
            order_item.save()
            messages.info(request, "This course is already present in your cart.")
            return redirect("app:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This course was added to your cart.")
            return redirect("app:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This course was added to your cart.")
    return redirect("app:order-summary")


@login_required(login_url='/login/')
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This course was removed from your cart.")
         
            return redirect("app:order-summary")
        else:
            messages.info(request, "This course was not in your cart")
       

            return redirect("app:order-summary")
    else:
        messages.info(request, "You do not have an active order")
 

        return redirect("app:order-summary")


@csrf_protect
@csrf_exempt
def success(request):
    if request.method == "POST":
        if True:
            
            email = request.POST["email"]
            user = Account.objects.get(email=email)
            
        

            try:            

                order = Order.objects.get(user=user, ordered=False)
            except:
                pass
            
            try:
                order_qs = KingOrder.objects.get(user=user,ordered=False)
            except:
                pass

            transaction = Transaction.objects.get(transaction_id=request.POST["txnid"])

            # print(request.POST)

            c = {}
            discount=0
            c.update(csrf(request))
            status = request.POST["status"]
            amount = request.POST["amount"]
            # amount paid to payu
            txnid = request.POST["txnid"]
            transaction_date = request.POST["addedon"]
            
            context = {"status": status, "txnid": txnid, "amount": amount}
            
            
            if not check_hash(request.POST):
                # Response data for order (txnid: %s) has been tampered. Confirm payment with PayU
                # Invalid transaction. Please try again!
                return redirect('app:order.failure')
                    

            

            elif float(order.get_total1()) == float(request.POST["amount"]):

                order_items = order.items.all()
                                
                order_items.update(ordered=True)

                for item in order_items:
                    item.save()
                order.transaction = transaction
                order.ordered_date = transaction_date
                user.transactions.add(transaction)
                user.save()
                order.ordered = True
                order.save()
                context["order_items"] = order_items
                context["s1"]=True
                    # Generating the invoice
                invoice_num = Order.objects.filter(ordered=True).count()
                amt_no_tax = round((order.get_total() * 100 / 118), 2)
                igst = round((amt_no_tax * 0.18), 2)
                data = {
                    "transaction_id": txnid,
                    "transaction_date": transaction_date,
                    "order_items": order_items,
                    "username": user.first_name + ' ' + user.last_name,
                    "user_email": user.email,
                    "user_phone": user.phone,
                    "invoice_num": invoice_num,
                    "total_amt": amount,
                    "amt_no_tax": amt_no_tax,
                    "igst": igst,
                    "contact_url": request.build_absolute_uri(reverse('app:contact')),
                    "invoice_url": request.build_absolute_uri(reverse('app:pdf_view', args=(txnid,))),
                }
                pdf = render_to_pdf('app/invoice.html', data)
                filename = "Invoice{}-{}.pdf".format(invoice_num, txnid)
                order.invoice.save(filename, File(BytesIO(pdf.content)))

                    # Sending Email for successful transaction
                subject = "Transaction Successful"
                html_message = render_to_string('app/transaction_email.html', data)
                plain_message = strip_tags(html_message)
                from_email = None  # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
                to = email  # This is a string, will be sent as a list
                fail_silently = False

                send_mail(subject, plain_message, from_email, [to], fail_silently, html_message=html_message)

            elif float(order_qs.get_total()) == float(request.POST["amount"]):
            
                orderqs_items = order_qs.items.all()
                                
                orderqs_items.update(ordered=True)
                
                for item in orderqs_items:
                    item.save()
                    
                order_qs.transaction = transaction
                order_qs.ordered_date = transaction_date
                user.transactions.add(transaction)
                user.save()
                order_qs.ordered = True
                order_qs.save()
                context["orderqs_items"] = orderqs_items
                context["s2"]=True
                    # Generating the invoice
                invoice_num =KingOrder.objects.filter(ordered=True).count()
                amt_no_tax = round((order_qs.get_total() * 100 / 118), 2)
                igst = round((amt_no_tax * 0.18), 2)
                data = {
                    "transaction_id": txnid,
                    "transaction_date": transaction_date,
                    "orderqs_items": orderqs_items,
                    "username": user.first_name + ' ' + user.last_name,
                    "user_email": user.email,
                    "user_phone": user.phone,
                    "invoice_num": invoice_num,
                    "total_amt": amount,
                    "amt_no_tax": amt_no_tax,
                    "igst": igst,
                    "contact_url": request.build_absolute_uri(reverse('app:contact')),
                    "invoice_url": request.build_absolute_uri(reverse('app:pdf_view', args=(txnid,))),
                    }
                pdf = render_to_pdf('app/invoice.html', data)
                filename = "Invoice{}-{}.pdf".format(invoice_num, txnid)
                order.invoice.save(filename, File(BytesIO(pdf.content)))

                    # Sending Email for successful transaction
                subject = "Transaction Successful"
                html_message = render_to_string('app/transaction_email.html', data)
                plain_message = strip_tags(html_message)
                message="Check order history "

                from_email = None  # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
                to = email  # This is a string, will be sent as a list
                fail_silently = False

                    
                send_mail(subject, plain_message, from_email, [to], fail_silently, html_message=html_message)

                


            elif float(order.get_total()) == float(request.POST["amount"]):

            
                order_items = order.items.all()
                orderqs_items = order_qs.items.all()
                                
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                orderqs_items.update(ordered=True)
                    
                for item in orderqs_items:
                    item.save()
    
                order.transaction = transaction
                order_qs.transaction = transaction

                order.ordered_date = transaction_date
                order_qs.ordered_date=transaction_date

                user.transactions.add(transaction)
                user.save()
                order.ordered = True
                order_qs.ordered=True

                order.save()
                order_qs.save()

                context["order_items"] = order_items
                context["orderqs_items"]= orderqs_items
                context["s3"]=True
                    # Generating the invoice
                invoice_num = Order.objects.filter(ordered=True).count()
                invoice_num1=KingOrder.objects.filter(ordered=True).count()
                # amt_no_tax = round((order.get_total() * 100 / 118), 2)
                amt_no_tax=4
                amt_no_tax1 = round((order_qs.get_total() * 100 / 118), 2)
                igst = round((amt_no_tax * 0.18), 2)+ round((amt_no_tax1*0.18),2)
                data = {
                        "transaction_id": txnid,
                        "transaction_date": transaction_date,
                        "order_items": order_items,
                        "orderqs_items":orderqs_items,
                        #"Productitems":orderqs_items,
                        "username": user.first_name + ' ' + user.last_name,
                        "user_email": user.email,
                        "user_phone": user.phone,
                        "invoice_num": invoice_num + invoice_num1,
                        "total_amt": amount,
                        "amt_no_tax": amt_no_tax+amt_no_tax1,
                        "igst": igst,
                        "contact_url": request.build_absolute_uri(reverse('app:contact')),
                        "invoice_url": request.build_absolute_uri(reverse('app:pdf_view', args=(txnid,))),
                }
                pdf = render_to_pdf('app/invoice.html', data)
                filename = "Invoice{}-{}.pdf".format(invoice_num, txnid)
                order.invoice.save(filename, File(BytesIO(pdf.content)))

                    # Sending Email for successful transaction
                subject = "Transaction Successful"
                html_message = render_to_string('app/transaction_email.html', data)
                plain_message = strip_tags(html_message)
                from_email = None  # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
                to = email  # This is a string, will be sent as a list
                fail_silently = False
               # message="you all orderd placed"

                send_mail(subject, plain_message, from_email, [to], fail_silently, html_message=html_message) 

    
            messages.success(request, "Transaction Successful!")

            return render(request, 'app/success.html', context)
        else:
        #    ObjectDoesNotExist
           
            return render(request, "app/error.html")
    else:
    
        return render(request, "app/error.html")


@csrf_protect
@csrf_exempt
def failure(request):
    if request.method == 'POST':
        try:
            email = request.POST["email"]
            user = Account.objects.get(email=email)
            order = Order.objects.get(user=user, ordered=False)
            order_qs=KingOrder.objects.get(user=user,ordered=False)


            order_items = order.items.all()
            order_qsitems=order_qs.items.all()
            
            transaction = Transaction.objects.get(transaction_id=request.POST["txnid"])
            transaction_date = request.POST["addedon"]
            data = request.POST.copy()
            data.update({
                "discount": 0,
            })
            context = {
                "status": data["status"],
                "txnid": data["txnid"],
                "contact_url": request.build_absolute_uri(reverse('app:contact')),
                "cart_url": request.build_absolute_uri(reverse('app:order-summary', ))
            }
            email_data = {
                "transaction_id": transaction.transaction_id,
                "transaction_date": transaction_date,
                "order_items": order_items,
                "Products_items2":order_items,                
                "username": user.first_name + ' ' + user.last_name,
                "contact_url": request.build_absolute_uri(reverse('app:contact')),
                "cart_url": request.build_absolute_uri(reverse('app:order-summary'))
            }
            if not check_hash(data):
                # Response data for order (txnid: %s) has been tampered. Confirm payment with PayU
                # Invalid transaction. Please try again!
                return redirect('app:home')
            else:
                if order.get_total1()!=0:
                    order.transaction = transaction
                    order.ordered_date = transaction_date
                    order.save()
                if order_qs.get_total()!=0:
                    order_qs.transaction = transaction
                    order_qs.ordered_date = transaction_date
                    order.save()

                # Payment for order (txnid: %s) failed at PayU

                # Sending Email for failed transaction
                subject = "Transaction Failed"
                html_message = render_to_string('app/transaction_failed_email.html', email_data)
                plain_message = strip_tags(html_message)
                from_email = None  # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
                to = email  # This is a string, will be sent as a list
                fail_silently = False

                send_mail(subject, plain_message, from_email, [to], fail_silently, html_message=html_message)

            messages.warning(request, "Transaction Failed!")
            return render(request, 'app/failure.html', context)
        except ObjectDoesNotExist:
            return render(request, "app/error.html")
    else:
        return render(request, "app/error.html")


@csrf_protect
@csrf_exempt
def cancel(request):
    if request.method == 'POST':
        try:
            email = request.POST["email"]
            user = Account.objects.get(email=email)
            order = Order.objects.get(user=user, ordered=False)
            order_qs=KingOrder.objects.get(user=user,ordered=False)
            
            transaction = Transaction.objects.get(transaction_id=request.POST["txnid"])
            transaction_date = request.POST["addedon"]
            data = request.POST.copy()
            data.update({
                "discount": 0,
            })
            context = {
                "status": data["status"],
                "txnid": data["txnid"]
            }

            if not check_hash(data):
                # Response data for order (txnid: %s) has been tampered. Confirm payment with PayU
                # Invalid transaction. Please try again!
                return redirect('app:home')
            else:
                if order.get_total1()!=0:
                    order.transaction = transaction
                    order.ordered_date = transaction_date
                    order.save()
                if order_qs.get_total()!=0:
                    order_qs.transaction = transaction
                    order_qs.ordered_date = transaction_date
                    order.save()

                # Payment for order (txnid: %s) cancelled at PayU
            messages.warning(request, "Transaction Cancelled!")
            return render(request, 'app/cancel.html', context)

        except ObjectDoesNotExist:
            return render(request, "app/error.html")
    else:
        return render(request, "app/error.html")


# Creates pdf
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(
    html, dest=response, link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


# Opens up page as PDF
@login_required(login_url='/login/')
def viewpdf(request, tid):
    try:
        transaction = Transaction.objects.get(transaction_id=tid)  # getting transaction from the tid in url
        order = Order.objects.get(user=request.user, ordered=True, transaction=transaction)  # finding paid order
        # for current user with transaction object found above.
        # If any of the above object does not exist (i.e, transaction does not exist or a user is trying to access
        # some other user's invoice), redirect to error page.

        if transaction.status == 'success':

            pdf = order.invoice

            # Check if the pdf exists in the Invoice Folder
            if pdf and default_storage.exists(pdf):
                return HttpResponse(pdf, content_type='application/pdf')
            else:
                # Invoice for this order does not exist !
                return redirect("app:error")

        else:
            return redirect("app:error")
    except ObjectDoesNotExist:
        # Object does not exist
        return redirect("app:error")


def organizations_trained(request):
    organization = Organization.objects.all().order_by('name')
    return render(request, 'app/organizations-trained.html', {'organization': organization})


def pilot_list(request):
    pilots = PilotList.objects.all().order_by('-date')
    return render(request, 'app/pilot-list.html', {'pilots': pilots})


def testimonial(request):
    student = Testimonial.objects.all().order_by('-id')
    return render(request, 'app/testimonials.html', {'student': student})


def gallery(request):
    batches = Gallery.objects.all().order_by('batch_no').order_by('-batch_no')
    page = request.GET.get('page', 1)

    paginator = Paginator(batches, 12)  # no. of batches per page
    try:
        users = paginator.page(page)
    except (PageNotAnInteger, InvalidPage):
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request, 'app/gallery.html', {'page_obj': users})

class IIDLocations(ListView):
    queryset = IIDLocations.objects.all().order_by('city')
    model = IIDLocations
    template_name = "app/Contact.html"


class TrainingSchedule(ListView):
    queryset = NotificationModel.objects.all().order_by('date')
    model = NotificationModel
    template_name = "app/Training.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        list1=[]
        
        list3=[]
        d=IIDLocations()

        for i in NotificationModel.objects.all():
             
            if i.city not in list1:

                list1.append(i.city)
                d=IIDLocations()

                d.city=i.city           
                d.Address=i.city.Address
    
                d.Phone1=i.city.Phone1
                d.Phone2=i.city.Phone2
                d.email1=i.city.email1
                d.email2=i.city.email2
                list3.append(d)
 
        context['show']=list1
        context['list3']=list3
        
        return context
    

# Error page
def error404(request):
    
    return render(request, "app/error.html", status=404)


def franchise(request):
    condition = True
    if request.method == "POST":
        form = qs(request.POST or None)
        if form.is_valid():

            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            email = request.POST['email']
            phone = request.POST['phone']
            query = request.POST['query']
            Location=request.POST['Location']

            obj = Query.objects.create(first_name=first_name, last_name=last_name, email=email, phone=phone,
                                       query=query,Location=Location)
            obj.save()

            # Sending email to self, if a query is submitted
            data = {
                'name': first_name + ' ' + last_name,
                'email': email,
                'phone': phone,
                'query': query,
                'Location':Location
            }

            subject = "New Query on Franchise Page"
            html_message = render_to_string('app/query_email.html', data)
            plain_message = strip_tags(html_message)
            from_email = None  # This will have no effect is you have set DEFAULT_FROM_EMAIL in settings.py
            to = 'director@iiodrones.com'  # This is a string, will be sent as a list
            fail_silently = False

            send_mail(subject, plain_message, from_email, [to], fail_silently,
                      html_message=html_message)
            
            condition=False

            if obj:
                messages.info(request, ("Query Submitted. Please find the Download Link at the bottom of this page."))
            
            return render(request,"app/franchise.html",{'condition':condition})
        else:
            messages.error(request, "Invalid Captcha!")
    else:
        form = qs()

    return render(request,"app/franchise.html",{'form':form,'condition':condition})




def webinar(request):
    s=Webinar.objects.all()
        
    return render(request,"app/webinar.html",{'s':s})


def databaserror(request):
    pass


class CheckoutView_student(LoginRequiredMixin, View):
    login_url = '/login/'
   
    def get(self, *args, **kwargs):
        
        try:
            return redirect("/") 
            certifcate=PilotCertificates.objects.filter(completed=False).last()

            if certifcate:
                print(certifcate)
                print("i have a certificate")

            else:        
                return redirect("app:order-summary_certificate")    
            
            form = CheckoutForm()
            
            context = {
                'form': form,
                'certificate':certifcate
            }
            
            return render(self.request, "app/checkout.html", context)
        
        except ObjectDoesNotExist:
            
            messages.info(self.request, "genrate the form first")
            return redirect("app:home")



    @method_decorator(csrf_protect)
    def post(self, *args, **kwargs):
        return redirect("/") 
        form = CheckoutForm(self.request.POST or None)
        try: 
            certifcate=PilotCertificates.objects.filter(completed=False).last()
            if form.is_valid():


                payment_option = form.cleaned_data.get('payment_option')
                
                if payment_option == 'PU':

                    if  certifcate:
                        initial = {
                                'txnid': uuid4().hex,
                                'productinfo':  certifcate.name,
                                'amount': certifcate.price,
                                'firstname': certifcate.name,
                                'email': self.request.user.email,
                                'phone': self.request.user.phone,
                                'lastname': self.request.user.last_name,

                                }
   
                    payurl = settings.PAYU_BASE_URL

                    if certifcate:
                        data1 = {
                            'txnid': initial['txnid'],
                            'productinfo': certifcate.name,
                            'amount': certifcate.price,
                            'firstname': certifcate.name,
                            'email': self.request.user.email
                        }

                    # creating hash
                    hash_object = hashlib.sha512(b'randint(0,20)')
                    txnid = hash_object.hexdigest()[0:20]
                    hashh = ''
                    hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
                    data1['key'] = settings.PAYU_MERCHANT_KEY
                    hash_string = ''
                    hashVarsSeq = hashSequence.split('|')
                    for i in hashVarsSeq:
                        try:
                            hash_string += str(data1[i])
                        except Exception:
                            hash_string += ''
                        hash_string += '|'
                    hash_string += settings.PAYU_MERCHANT_SALT
                    hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()

                    # Create transaction record
                    Transaction.objects.create(transaction_id=data1.get('txnid'),
                                               amount=data1.get('amount'))

                    initial.update({'key': settings.PAYU_MERCHANT_KEY,
                                    'surl': self.request.build_absolute_uri(reverse('app:order.success')),
                                    'furl': self.request.build_absolute_uri(reverse('app:order.failure')),
                                    'curl': self.request.build_absolute_uri(reverse('app:order.cancel')),
                                    'hash': hashh,
                                    'service_provider': 'payu_paisa',
                                    
                                    })


                    payu_form = PayUForm(initial)
                    if payu_form.is_valid():

                        # payu form is valid

                        context = {'form': payu_form,
                                   'action': payurl}

                        return render(self.request, 'app/payment2.html', context)

                    else:

                        return render(self.request, 'app/error.html')

                else:

                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect("app:order-summary")
            else:

                return redirect("app:order-summary")

        except:
            # No active order
            messages.warning(self.request, "You do not have an active order")
            return redirect("app:order-summary")


from googleapiclient.discovery import build
from google.oauth2 import service_account
import io
from datetime import datetime



def Domptest(request):

    s2=Account.objects.filter(email=request.user)[0]
    s1=OrderItem.objects.filter(user=request.user,item__title='Drone Operations and Management Professionals',ordered=True).last()


    if s1:
        pass
    
    else:
        return HttpResponse("error")
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    SERVICE_ACCOUNT_FILE='iid.json'


    credential=None
    credential=service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,scopes=SCOPES)
    

    SAMPLE_SPREADSHEET_ID = '1sZQmY8E9RwFuuWJm7PgDNns5QL2ohBZiYk3rpmNbrE0'

    values=''
    if True:
        if True:
                list1=[]
                list1.append(str(request.user))
                service = build('sheets', 'v4', credentials=credential)
                sheet = service.spreadsheets()
                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range="B:B").execute()
                values = result.get('values', ' ')

                if list1 in values:
                    date=datetime.today().strftime('%d-%m-%Y')
                    data = {
                        
                    'certificate':s2,
                    'date':date
                    }
                    
                    pdf = render_to_pdf('app/domp.html', data)
                    

                    return pdf
              

                else:
                    return HttpResponse("completed your test first ")


        return HttpResponse("download certificate")
        
    else:
        
        return HttpResponse("completed your test")

    