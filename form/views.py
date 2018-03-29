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