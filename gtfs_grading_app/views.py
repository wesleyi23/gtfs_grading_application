from django.http.response import HttpResponse
from django.shortcuts import render, redirect
import tempfile
import zipfile
import partridge as ptg
from django.contrib import messages

# Create your views here.
from gtfs_grading_app.forms import GtfsZipForm


def home(request):
    form = GtfsZipForm()
    if 'gtfs_feed' in request.session:
        print('GTFS Feed present: ' + request.session['gtfs_feed'])

    else:
        print('no session')

    return render(request, 'file_upload.html', {'form': form})


def post_gtfs_zip(request):
    '''This view is a post request for saving GTFS zip files to a temp folder for use latter'''
    if not request.method == 'POST' or not request.FILES:
        return HttpResponse('You must submit a .zip file', status=400)
    else:
        form = GtfsZipForm(request.POST, request.FILES)
        if form.is_valid():
            # TODO implement better file management
            try:
                tmp_dir = tempfile.mkdtemp()
                zip_ref = zipfile.ZipFile(request.FILES['file'], 'r')
                zip_ref.extractall(tmp_dir)
                gtfs_feed = ptg.load_feed(tmp_dir)
                request.session['gtfs_feed'] = tmp_dir
            except:
                messages.error(request, 'There was an error uploading your GTFS feed.  Please be sure you submitted a valid .zip GTFS file and try again.')

        return redirect(home)





