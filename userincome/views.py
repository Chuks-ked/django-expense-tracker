from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference

# Create your views here.


@login_required(login_url='/authentication/login/')
def index(request):
    # if UserPreference.objects.filter(user = request.user).exists():
    #     currency = UserPreference.objects.get(user = request.user).currency
    # else:
    #     currency = 'INR - Indian Rupee'
    source = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator= Paginator(income, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    return render(request, 'income/index.html',{
        'income':income,
        'page_obj':page_obj,
        'currency':currency,
    })


def search_income(request):
    if request.method=='POST':
        search_str = json.loads(request.body).get('searchText')

        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        
        data = income.values()
        return JsonResponse(list(data), safe=False)
   

@login_required(login_url='/authentication/login/')
def add_income(request):
    sources = Source.objects.all()
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'amount is required')
            return render(request, 'income/add_income.html',{
                "sources":sources,
                'values': request.POST,
            })
        date = request.POST['income_date']
        source = request.POST['source']
        description = request.POST['description']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html',{
                "source":source,
                'values': request.POST,
            })
        UserIncome.objects.create(owner=request.user, amount=amount, date=date, source=source, description=description)
        messages.success(request, 'Record saved successfully')
        return redirect('income')

    return render(request, 'income/add_income.html',{
        "sources":sources,
    })

@login_required(login_url='/authentication/login/')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'amount is required')
            return render(request, 'income/edit_income.html',{
                "sources":sources,
                'values': request.POST,
            })
        date = request.POST['income_date']
        source = request.POST['source']
        description = request.POST['description']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html',{
                "sources":sources,
                'values': request.POST,
            })
        
        income.amount=amount
        income.date=date
        income.source=source
        income.description=description
        income.save()
        messages.success(request, 'Record Updated successfully')
        return redirect('income')

    return render(request, 'income/edit_income.html',{
        "sources":sources,
        "income":income,
        'values':income,
    })

@login_required(login_url='/authentication/login/')
def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()

    messages.success(request, 'Record removed')
    return redirect ('income')