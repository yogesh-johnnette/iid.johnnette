
from app.views import success,databaserror
from django.shortcuts import render,redirect
from store.models import KingOrder
from account.models import Account

from app.models import Order
from .models import Order as shakti

class RoleMiddleware:

    def __init__(self,get_response):
        self.get_response=get_response
        

    def __call__(self,request):
        
        response=self.get_response(request)

        return response
    
    
    def process_view(self,request,view_func,*view_args,**view_kargs):

 
        if view_func == success:
            
            pass
    
         
    
        
    

