from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
# Create your views here.

def search_expenses(request):
    if request.method=='POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        
        data = expenses.values()
        return JsonResponse(list(data), safe=False)
        

@login_required(login_url='/authentication/login/')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator= Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    return render(request, 'expenses/index.html',{
        'expenses':expenses,
        'page_obj':page_obj,
    })

@login_required(login_url='/authentication/login/')
def add_expense(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'amount is required')
            return render(request, 'expenses/add_expense.html',{
                "categories":categories,
                'values': request.POST,
            })
        date = request.POST['expense_date']
        category = request.POST['category']
        description = request.POST['description']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html',{
                "categories":categories,
                'values': request.POST,
            })
        Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
        messages.success(request, 'Expense saved successfully')
        return redirect('expenses')

    return render(request, 'expenses/add_expense.html',{
        "categories":categories,
    })

@login_required(login_url='/authentication/login/')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'amount is required')
            return render(request, 'expenses/edit-expense.html',{
                "categories":categories,
                'values': request.POST,
            })
        date = request.POST['expense_date']
        category = request.POST['category']
        description = request.POST['description']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit-expense.html',{
                "categories":categories,
                'values': request.POST,
            })
        
        expense.owner=request.user
        expense.amount=amount
        expense.date=date
        expense.category=category
        expense.description=description
        expense.save()
        messages.success(request, 'Expense Updated successfully')
        return redirect('expenses')

    return render(request, 'expenses/edit-expense.html',{
        "categories":categories,
        "expense":expense,
        'values':expense,
    })

@login_required(login_url='/authentication/login/')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()

    messages.success(request, 'Expense removed')
    return redirect ('expenses')