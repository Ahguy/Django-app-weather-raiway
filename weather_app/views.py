from django.shortcuts import render, HttpResponse, redirect
import requests
from django.http import JsonResponse

from .models import City
from django.contrib import messages
# Create your views here.

def home(request):
     
    #define api key and url
    API_KEY = '925cc78d00cdad861aee9c11c1d10b73'
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'

    #checking if the request method is post (when adding a new city)
    if request.method == 'POST':  # Fixed: changed 'requests' to 'request'
        city_name = request.POST.get('city')  # Fixed: changed 'requests' to 'request'
        response = requests.get(url.format(city_name, API_KEY)).json()#fetch the weather data from the api
        if response['cod']==200:#check if the city exists in the api response
            if not City.objects.filter(name=city_name).exists():#check if the city already exists in the database
             City.objects.create(name=city_name)#add the city to the database
             messages.success(request, f"City '{city_name}' added successfully!")
            else:
             messages.warning(request, f"City '{city_name}' already exists in the database.")
        else:
            messages.error(request, f"City '{city_name}' does not exist.")
        
        return redirect('home')  # Added: redirect after POST to avoid resubmission
    
    weather_data = []
    #fetch weather data for all cities in the database
    try:
     cities = City.objects.all()  # Fixed typo: 'citties' to 'cities'
     for city in cities:
        response = requests.get(url.format(city.name, API_KEY)).json()
        if response['cod']==200:
           city_weather = {
              'city': city.name,
              'temperature': response['main']['temp'],
              'description': response['weather'][0]['description'],
              'icon': response['weather'][0]['icon'],
           }
           weather_data.append(city_weather)
        else:
           City.objects.filter(name=city.name).delete()#delete the city if it no longer exists in the api
    except requests.RequestException as e :
        print(f"Error fetching weather data: {e}")


    context = {'weather_data': weather_data}

    return render(request,'index.html', context)