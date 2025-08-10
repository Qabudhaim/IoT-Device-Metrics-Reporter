from django.shortcuts import render

# Create your views here.
# make an index file

def index(request):
    """
    Render the index page for the Metrics application.
    
    Args:
        request: The HTTP request object.
    
    Returns:
        HttpResponse: Rendered index page.
    """
    return render(request, 'index.html')


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
