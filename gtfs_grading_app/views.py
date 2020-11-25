from django.shortcuts import render

# Create your views here.
from gtfs_grading_app.forms import GtfsZipForm


def home(request):
    if request.method == 'POST':
        form = GtfsZipForm(request.POST, request.FILES)
        if form.is_valid():
            print("file received!")
    else:
        form = GtfsZipForm()
    return render(request, 'base.html', {'form': form})

    return render(request, "base.html")



