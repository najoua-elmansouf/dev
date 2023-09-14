from django.shortcuts import render


def home(request):
    """slm """
    return render(request, 'users/home.html')

def register(request):
    """slm """
    return render(request, 'users/register.html')
