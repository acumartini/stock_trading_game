"""
@newfield renders: Renders
@newflied redirects: Redirects
"""

# from django.template import Context, loader
# from django.http import HttpResponse, HttpResponseRedirect
# from django.shortcuts import render_to_response,
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages


from stocks.models import Stock
# from stocks.models import StockTicker
from stocks.forms import SearchForm

import stocks.api as api
# import urllib
# import json
# from django.db.models import Q
# import datetime
# from datetime import timedelta
# from datetime import datetime
# import copy
# import random
# import operator 

STOCKS_PER_PAGE = 50

def search(request):
    """
    Displays a search page for finding a particular stock.
    Finds the stock specified by the search request POST.
    
    @renders: stocks/index.html if there has not been a search
    @redirects: stocks/ if responding to a successful POST
    """
    
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            ticker = request.POST['ticker']
            return redirect('/stock/' + str(ticker) + '/')
    else:
        form = SearchForm()

    return render(request, 'stocks/index.html', {'form': form})


def detail(request, ticker):
    """
    Renders a detail view for the given stock.
    
    @renders: stocks/detail.html
    """
    if not Stock.objects.filter(ticker=ticker.upper()).exists():
        messages.add_message(request, messages.ERROR, "That's not a stock.")
        return redirect('/stocks/')
    
    stock_data = api.get_stock(ticker)
    stock_data.searched_count += 1
    stock_data.save()
    return render(request, 'stocks/detail.html', {'stock': stock_data})


# The documented line of demarcation.

def all(request, page=1):
    start = (int(page) - 1) * STOCKS_PER_PAGE
    page_of_stocks = Stock.objects.all().order_by('company_name')[start:start+STOCKS_PER_PAGE]
    if not page_of_stocks.exists():
        raise Http404
    return render(request, 'stocks/all_stocks.html', {'all_stocks': page_of_stocks, 'previous': int(page) - 1, 'next': int(page) + 1})


def get_top(request, reverseSort="desc"):
    top20s = ((key, Stock.objects.top20(key)) for key in ['current_price', 'volume', 'searched_count'])
    return render(request, 'stocks/top20s.html', {'top20s': top20s})



def get_history(request, ticker, daysbefore=15, startDate='' ):
    endDate = "";
    now = datetime.now()
    if startDate=='' or (datetime.strptime(startDate, "%Y%m%d")) > now:
        
        sdt = now - timedelta(days=int(float(daysbefore)))
        endDate = sdt.strftime("%Y-%m-%d") #sd.year + "-" + sd.month + "-" + sd.day
        sd = now.strftime("%Y-%m-%d")
    else:
        sd = (datetime.strptime(startDate, "%Y%m%d")).strftime("%Y-%m-%d")
        endDate = (datetime.strptime(startDate,"%Y%m%d") - timedelta(days=int(float(daysbefore)))).strftime("%Y-%m-%d")
    stockhistorylist = api.query_history(ticker, endDate,sd)
    sl = add_weekends_data(stockhistorylist, int(float(daysbefore)))
    return render_to_response('stocks/stock_history.html', {'stockhistory': sl}) 


def add_weekends_data(data, numofdays):
    startDate = data[-1]['date']
    allDays_data=[]
    
    current_date = datetime.strptime(data[-1]['date'],"%Y-%m-%d")
    current_index=1
    lastData = data[0-current_index]
    #allDays_data.append(lastData)
    leng = len(data)
    for index in range(1, numofdays+1):


        d = data[0-current_index]
        if current_date.strftime("%Y-%m-%d")==d['date']:
            allDays_data.append(d)
            lastData = data[0-current_index]
            current_index += 1
        else:
            ld = copy.copy(lastData)
            ld['date']=current_date.strftime("%Y-%m-%d")
            allDays_data.append(ld)

        current_date = current_date + timedelta(days=1)
        if current_index > leng:
            break
    """
    while current_date < (datetime.now()):

        ld = copy.copy(lastData)
        ld['date']=current_date.strftime("%Y-%m-%d")
        allDays_data.append(ld)
        current_date = current_date + timedelta(days=1)
    """
    return allDays_data
        
