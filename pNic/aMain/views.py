# from django.http import HttpResponse
# from django.template import loader

from django.shortcuts import (
    render,
    redirect,
)


def empty(request):
    return redirect("index")


def index(request):
    context = {}
    return render(request, "base_generic.html", context)
    # return HttpResponse("Hello, world. You're at the aMain index.")
