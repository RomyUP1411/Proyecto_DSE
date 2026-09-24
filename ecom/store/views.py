from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm 
from django import forms
from .forms import SignUpForm 
from django.shortcuts import render, redirect 
from .models import Product 
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages 
from .models import Product, Category

def home(request): 
    products = Product.objects.all() 
    ctgs = Category.objects.all()  # Obtener todas las categorías 
    return render(request, 'home.html', {'products': products, 'ctgs': ctgs})

def about(request): 
    return render(request, 'about.html')  

def login_user(request):
    if request.method == "POST":
        username = request.POST['username'] 
        password = request.POST['password'] 
        user = authenticate(request, username=username, password=password) 
        if user is not None: 
            login(request, user) 
            messages.success(request, ("You Have Been Logged In")) 
            return redirect('home') 
        else: 
            messages.success(request, ("There was an error, please try again")) 
            return redirect('login') 
    else: 
        return render(request, 'login.html', {}) 
 
def logout_user(request): 
    logout(request) 
    messages.success(request, ("You have been logget out. We appreciate your visit.")) 
    return redirect('home')

def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "User created. Welcome!")
            return redirect('home')
        else:
            messages.error(request, "There has been an issue with your registration.")
            return render(request, 'register.html', {'form': form})  #mostrar errores
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})  #mostrar formulario vacío

def product(request,pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product':product})

def category(request, foo): 
    # reemplaza guiones por espacios 
    foo = foo.replace('-',' ') 
    ctgs = Category.objects.all() 
    # categoria de url 
    try: 
        #Buscar la categoria 
        category = Category.objects.get(name=foo) 
        #Buscar los productos en esta categoría 
        products = Product.objects.filter(category=category) 
        return render(request, 'category.html', {'products':products, 'category':category, 'ctgs':ctgs}) 
    except: 
        messages.success(request, ("That category doesn't exist")) 
        return redirect(request, 'home')
