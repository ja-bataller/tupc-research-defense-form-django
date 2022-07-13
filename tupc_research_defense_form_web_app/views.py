from django.shortcuts import render

# INDEX PAGE
def index(request):
    return render(request, 'index.html')

def signup(request):
    return render(request, 'signup.html')