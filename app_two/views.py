from django.shortcuts import render
from django.http import HttpResponse
from app_two.models import User

# Create your views here.

def index2(request):
	return HttpResponse("<em>My Second App</em>")

def help(request):
	my_dict = {'help_text':"Help Page"}
	return render(request,'app_two/help.html',context=my_dict)

def users(request):
	user_list = User.objects.order_by('first_name')
	users = {'user_records':user_list}
	return render(request,'app_two/users.html',context=users)
