from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
# Create your views here.

@login_required(login_url='/authentication/login/')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    return render(request, 'expenses/index.html',{
        'expenses':expenses,
    })

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

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()

    messages.success(request, 'Expense removed')
    return redirect ('expenses')