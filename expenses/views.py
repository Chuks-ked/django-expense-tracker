from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
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
    # if UserPreference.objects.filter(user = request.user).exists():
    #     currency = UserPreference.objects.get(user = request.user).currency
    # else:
    #     currency = 'INR - Indian Rupee'
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator= Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    return render(request, 'expenses/index.html',{
        'expenses':expenses,
        'page_obj':page_obj,
        'currency':currency,
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

def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    finalrep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)
    
    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_view(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses' + str(datetime.datetime.now()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    expenses=Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response

def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses' + str(datetime.datetime.now()) + '.xls'
    wb= xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows= Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')

    for row in rows:
        row_num +=1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='inline; attachment; filename=Expenses' + str(datetime.datetime.now()) + '.pdf'

    response['Content-Transfer-Encoding'] = 'binary'

    expenses=Expense.objects.filter(owner=request.user)

    sum = expenses.aggregate(Sum('amount'))

    html_string=render_to_string('expenses/pdf-output.html', {'expenses':expenses, 'total':sum['amount__sum']})
    html=HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()

        output = open(output.name, 'rb')
        response.write(output.read())

    return response