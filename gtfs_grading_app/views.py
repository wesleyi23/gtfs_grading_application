from django.forms import formset_factory
from django.forms.models import inlineformset_factory
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import tempfile
import zipfile
import partridge as ptg
from django.contrib import messages

# Create your views here.
from django.views.generic import ListView, DetailView

from gtfs_grading_app.forms import GtfsZipForm, AddReviewCategory, AddReviewWidget, AddConsistencyWidget, \
    AddResultsCaptureWidget
from gtfs_grading_app.models import review_category, review_widget, consistency_widget, results_capture_widget


def home(request):
    '''Home page view'''
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

            try:
                # TODO implement better file management
                tmp_dir = tempfile.mkdtemp()
                zip_ref = zipfile.ZipFile(request.FILES['file'], 'r')
                zip_ref.extractall(tmp_dir)
                gtfs_feed = ptg.load_feed(tmp_dir)
                request.session['gtfs_feed'] = tmp_dir
                messages.success(request, "Your GTFS file has been successfully uploaded and parsed!")
            except:
                messages.error(request, 'There was an error uploading your GTFS feed.  Please be sure you submitted a valid .zip GTFS file and try again.')
        else:
            messages.error(request,
                           'There was an error uploading your GTFS feed.  Please be sure you submitted a valid .zip GTFS file and try again.')

        return redirect(home)


def gtfs_admin(request):
    """admin page for adding new review categories (and potentially other features down the road)"""

    return render(request, 'admin/gtfs_admin.html')


class ViewReviewCategory(ListView):
    template_name = 'admin/view_review_category.html'
    queryset = review_category.objects.select_related()
    context_object_name = 'review_category'


class ViewReviewWidget(DetailView):
    def get(self, request, *args, **kwargs):
        this_review_widget = get_object_or_404(review_widget, pk=kwargs['pk'])
        context = {'review_widget': this_review_widget}
        return render(request, 'admin/view_review_widget.html', context)



def add_review_category(request):
    """View all review categories or a specific one"""
    if request.method == 'POST':
        form_ReviewCategory = AddReviewCategory(request.POST, prefix="form_ReviewCategory")
        form_ReviewWidget = AddReviewWidget(request.POST, prefix="form_ReviewWidget")
        form_AddConsistencyWidget = AddConsistencyWidget(request.POST, prefix="form_AddConsistencyWidget")
        form_AddResultsCaptureWidget = AddResultsCaptureWidget(request.POST, prefix="form_AddResultsCaptureWidget")


        if form_ReviewCategory.is_valid() and form_ReviewWidget.is_valid() and \
                form_AddConsistencyWidget.is_valid() and form_AddResultsCaptureWidget.is_valid():
            this_review_widget = form_ReviewWidget.save()
            this_consistency_widget = form_AddConsistencyWidget.save()
            this_results_capture_widget = form_AddResultsCaptureWidget.save()

            this_review_category = form_ReviewCategory.save(commit=False)
            this_review_category.review_widget = this_review_widget
            this_review_category.consistency_widget = this_consistency_widget
            this_review_category.results_capture_widget = this_results_capture_widget

            this_review_category.save()
            
            return redirect('home')

    else:

        form_ReviewCategory = AddReviewCategory(prefix="form_ReviewCategory")
        form_ReviewWidget = AddReviewWidget(prefix="form_ReviewWidget")
        form_AddConsistencyWidget = AddConsistencyWidget(prefix="form_AddConsistencyWidget")
        form_AddResultsCaptureWidget = AddResultsCaptureWidget(prefix="form_AddResultsCaptureWidget")

    return render(request, 'admin/add_review_category.html', {'form_ReviewCategory': form_ReviewCategory,
                                                        'form_ReviewWidget': form_ReviewWidget,
                                                        'form_AddConsistencyWidget': form_AddConsistencyWidget,
                                                        'form_AddResultsCaptureWidget': form_AddResultsCaptureWidget})