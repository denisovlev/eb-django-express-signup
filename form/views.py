import json
import os
from collections import Counter

from django.http import HttpResponse
from django.shortcuts import render
from .models import Leads

def home(request):
    return render(request, 'index.html')


def signup(request):
    leads = Leads()
    status = leads.insert_lead(request.POST['name'], request.POST['email'], request.POST['previewAccess'])
    if status == 200:
        leads.send_notification(request.POST['email'])
    return HttpResponse('', status=status)

def search(request):
    domain = request.GET.get('domain')
    preview = request.GET.get('preview')
    leads = Leads()

    if domain or preview:
        items = leads.get_leads(domain, preview)
        return render(request, 'search.html', {'items': items})
    else:
        items = leads.get_lead_domains()
        count = [(item["domain"], item["num"]) for item in items]
        return render(request, 'search.html', {'domains': sorted(count)})

import vincent
from django.conf import settings

BASE_DIR = getattr(settings, "BASE_DIR", None)

def chart(request):
    domain = request.GET.get('domain')
    preview = request.GET.get('preview')
    leads = Leads()
    domain_count = Counter()
    if domain or preview:
        items = leads.get_leads(domain, preview)
        domain_count.update([item['email'].split('@')[1] for item in items])
        print(domain_count)
        domain_freq = domain_count.most_common(15)
        if len(domain_freq) == 0:
            return HttpResponse('No items to show', status=200)
        labels, freq = zip(*domain_freq)
        data = {'data': freq, 'x': labels}
        bar = vincent.Bar(data, iter_idx='x')
        content = json.dumps(bar.to_json())
        return render(request, 'chart.html', {'items': items, 'content': content})
    else:
        items = leads.get_lead_domains()
        print(items)
        for item in items:
            print(item)
            num = int(item["num"])
            print(num)
            for i in range(0,num):
                print(i)
                domain_count.update([item["domain"]])

        domain_freq = domain_count.most_common(15)
        if len(domain_freq) == 0:
            return HttpResponse('No items to show', status=200)
        labels, freq = zip(*domain_freq)
        data = {'data': freq, 'x': labels}
        bar = vincent.Bar(data, iter_idx='x')
        content = json.dumps(bar.to_json())
        return render(request, 'chart.html', {'items': items, 'content': content})