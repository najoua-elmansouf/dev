from django.shortcuts import render

# Create your views here.
def myview(request):
    return render(request, "app/graph.html")