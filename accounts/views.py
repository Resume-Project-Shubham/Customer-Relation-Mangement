from django.shortcuts import redirect, render


from django.http import HttpResponse
from .models import *
from .forms import OrderForm
from django.forms import inlineformset_factory
from .filters import OrderFilter
# Create your views here.


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

def product(request):
    products = Product.objects.all()

    # return HttpResponse('products')
    return render(request,'accounts/products.html',{'products':products})

    
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

def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = {'item':order}
    return render(request,'accounts/delete.html',context)
