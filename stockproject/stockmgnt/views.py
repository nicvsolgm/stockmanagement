from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
import csv, io
from django.contrib import messages
from .models import *
from .forms import * #StockCreateForm, StockSearchForm, StockUpdateForm
#from .forms import IssueForm, ReceiveForm
# Create your views here.

def home(request):
	title = 'Welcome: This is the Home Page'
	context = {
	"title": title,
	}
	return render(request, "home.html",context)

@login_required
def list_item(request):
	header = 'List of Items'
	form = StockSearchForm(request.POST or None)
	queryset = Stock.objects.all()
	context = {
		"header": header,
		"queryset": queryset,
		"form": form,
	}
	if request.method == 'POST':
		queryset = Stock.objects.filter(#category__icontains=form['category'].value(),
										item_name__icontains=form['item_name'].value()
										)
		if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
			writer = csv.writer(response)
			writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
			instance = queryset
			for stock in instance:
				writer.writerow([stock.category, stock.item_name, stock.quantity])
			return response
		context = {
			"form": form,
			"header": header,
			"queryset": queryset,
		}
	return render(request, "list_item.html", context)

@login_required
def add_items(request):
	form = StockCreateForm(request.POST or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Successfully Saved')
		return redirect('/list_items')
	context = {
		"form": form,
		"title": "Add Item",
	}
	return render(request, "add_items.html", context)

def update_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = StockUpdateForm(instance=queryset)
	if request.method == 'POST':
		form = StockUpdateForm(request.POST, instance=queryset)
		if form.is_valid():
			form.save()
			messages.success(request, 'Successfully Updated')
			return redirect('/list_items')

	context = {
		'form': form
	}
	return render(request, 'add_items.html', context)


def delete_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	if request.method == 'POST':
		queryset.delete()
		messages.success(request, 'Successfully Deleted')
		return redirect('/list_items')
	return render(request, 'delete_items.html')


def stock_detail(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"title": queryset.item_name,
		"queryset": queryset,
	}
	return render(request, "stock_detail.html", context)

def issue_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = IssueForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity -= instance.issue_quantity
		#instance.issue_by = str(request.user)
		messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in Store")
		instance.save()

		return redirect('/stock_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"title": 'Issue ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		"username": 'Issue By: ' + str(request.user),
	}
	return render(request, "add_items.html", context)



def receive_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReceiveForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity += instance.receive_quantity
		instance.save()
		messages.success(request, "Received SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name)+"s now in Store")

		return redirect('/stock_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())
	context = {
			"title": 'Reaceive ' + str(queryset.item_name),
			"instance": queryset,
			"form": form,
			"username": 'Receive By: ' + str(request.user),
		}
	return render(request, "add_items.html", context)

def reorder_level(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReorderLevelForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Reorder level for " + str(instance.item_name) + " is updated to " + str(instance.reorder_level))

		return redirect("/list_items")
	context = {
			"instance": queryset,
			"form": form,
		}
	return render(request, "add_items.html", context)

#@permission_required('admin.can_add_log_entry')
#def contact_upload(request):
#        prompt = {
#		       "order" : 'order of the csv should be first_name, last_name, email, ip_address, message'
#      	}
#    	if request.method == "GET"
#              return render(request, "contact_upload.html", prompt)

#    csv_file = request.FILES('files')
#	if not csv_file.name.endswith('.csv'):
#	messages.error(request, 'This is not a csv file')
#	data_set = csv_file.read().decode('UTF-8')
#	io_string = io.StringIO(data_set)
#    next(io_string)
#    for column in csv.reader(io_string, delimiter = ',', quotechar = '|'):
#	_, created = Contact.objects.update_or_create(
#		first_name = column[0],
#		last_name = column[1],
#		email = column[2],
#		ip_address = column[3],
#		message = column[4]
#			)
#		context = {}
#		return render(request, template, context)

@login_required
def list_history(request):
	header = 'LIST OF ITEMS'
	queryset = StockHistory.objects.all()
	context = {
		"header": header,
		"queryset": queryset,
	}
	return render(request, "list_history.html",context)
