from django.shortcuts import render
from movies.models import Movie


def index(request):
    movies = Movie.objects.all()[:3]
    template_data = {}
    template_data["title"] = "GT Movies Store"
    template_data["movies"] = movies
    return render(request, "home/index.html", {"template_data": template_data})


def about(request):
    template_data = {}
    template_data["title"] = "About"
    return render(request, "home/about.html", {"template_data": template_data})
