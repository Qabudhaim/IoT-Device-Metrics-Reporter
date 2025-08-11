from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Device

# Create your views here.
# make an index file

def index(request):
    """Render the index page for the Metrics application."""

    query = request.GET.get('query', '')

    devices_list = Device.objects.filter(Q(device_id__icontains=query)).order_by('-created_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(devices_list, 8)

    try:
        devices = paginator.page(page)
    except PageNotAnInteger:
        devices = paginator.page(1)
    except EmptyPage:
        devices = paginator.page(paginator.num_pages)

    context = {
        'Devices': devices,
    }
    
    return render(request, 'index.html', context)

def show_device(request, device_id):
    """Render the page for a specific device."""

    context = {
        'device_id': device_id,
    }
    
    return render(request, 'show_device.html', context)


def handler500(request, *args, **argv):
    context = {
        'Name': 'Error500',
        'Message': 'Internal Server Error'
    }
    return render(request, 'error_template.html', context, status=500)

def handler404(request, *args, **argv):
    context = {
        'Name': 'Error404',
        'Message': 'Page Not Found'
    }
    return render(request, 'error_template.html', context, status=404)

def handler403(request, *args, **argv):
    context = {
        'Name': 'Error403',
        'Message': 'Permission Denied'
    }
    return render(request, 'error_template.html', context, status=403)

def handler400(request, *args, **argv):
    context = {
        'Name': 'Error400',
        'Message': 'Bad Request'
    }
    return render(request, 'error_template.html', context, status=400)
