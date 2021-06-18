from accounts.decorators import unauthenticated_user
from django.contrib import auth
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth import authenticate,login,logout

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.
from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter
from .decorators import allowed_user, unauthenticated_user, admin_only

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')

                group = Group.objects.get(name='customer')
                user.groups.add(group)

                messages.success(request,'Account was created for '+username)

                return redirect('login')

        context = {'form':form}
        return render(request,'accounts/register.html',context)


@unauthenticated_user
def loginPage(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')

        password = request.POST.get('password')


        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Username OR Password is incorrect')

    context = {}
    return render(request,'accounts/login.html',context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    
    order = Order.objects.all()
    customer = Customer.objects.all()

    total_customer = customer.count()
    total_order = order.count()
    delivered = order.filter(status = "Delivered").count()
    pending = order.filter(status = "Pending").count()


    context = {'orders':order,'customers':customer,'total_customer':total_customer,'total_order':total_order,'delivered':delivered,'pending':pending}
    # return HttpResponse('Home Page')
    return render(request,'accounts/dashboard.html',context)

def userPage(request):
    context = {}
    return render(request,'accounts/user.html')


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def product(request):
    products = Product.objects.all()

    # return HttpResponse('products')
    return render(request,'accounts/products.html',{'products':products})

    
@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def customer(request,pk_test):

    user = Customer.objects.get(id = pk_test)
    # order = Order.objects.filter(customer = user.name)
    # order = Order.objects.get(id = pk_test)
    orders = user.order_set.all()
    total_order = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'user':user,'orders':orders,'total_order':total_order,'myFilter':myFilter}
    # return HttpResponse('customer')
    return render(request,'accounts/customer.html',context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def createOrder(request,pk):

    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product','status'),extra = 10)


    customer = Customer.objects.get(id = pk)
    
    formset = OrderFormSet(queryset = Order.objects.none(),instance=customer)

    # form = OrderForm(initial={'customer':customer})

    if request.method == 'POST':
        # print("Printing",request.POST)
        formset = OrderFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'formset':formset}

    return render(request, 'accounts/order_form.html',context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def updateOrder(request,pk):
    
    order = Order.objects.get(id=pk)
    form  = OrderForm(instance=order)

    if request.method == 'POST':
        # print("Printing",request.POST)
        form = OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form':form}
    return render(request,'accounts/order_form.html',context)


@login_required(login_url='login')
@allowed_user(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = {'item':order}
    return render(request,'accounts/delete.html',context)
