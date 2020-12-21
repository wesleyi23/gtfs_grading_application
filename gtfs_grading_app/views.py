from django.forms import formset_factory
from django.forms.models import inlineformset_factory
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
import tempfile
import zipfile
import partridge as ptg
from django.contrib import messages

# Create your views here.
from django.views.generic import ListView, DetailView

from gtfs_grading_app.classes.classes import review_widget_factory, consistency_widget_factory, \
    results_capture_widget_factory
from gtfs_grading_app.forms import GtfsZipForm, AddReviewCategory, AddReviewWidget, AddConsistencyWidget, \
    AddResultsCaptureWidget
from gtfs_grading_app.models import review_category, review_widget, consistency_widget, results_capture_widget, \
    gtfs_field, consistency_widget_visual_example, consistency_widget_link, score

from gtfs_grading_app.gtfs_spec.import_gtfs_spec import get_cascading_drop_down, get_field_type


def home(request):
    """Home page view"""
    form = GtfsZipForm()
    if 'gtfs_feed' in request.session:
        print('GTFS Feed present: ' + request.session['gtfs_feed'])

    else:
        print('no session')

    return render(request, 'file_upload.html', {'form': form})


def post_gtfs_zip(request):
    """This view is a post request for saving GTFS zip files to a temp folder for use latter"""
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
                messages.error(request,
                               'There was an error uploading your GTFS feed.  Please be sure you submitted a valid .zip GTFS file and try again.')
        else:
            messages.error(request,
                           'There was an error uploading your GTFS feed.  Please be sure you submitted a valid .zip GTFS file and try again.')

        return redirect(home)


def gtfs_admin(request):
    """admin page for adding new review categories (and potentially other features down the road)"""

    return render(request, 'admin/gtfs_admin.html')


class ViewReviewCategory(ListView):
    """List view of review categories"""
    template_name = 'admin/view_review_category.html'
    queryset = review_category.objects.select_related()
    context_object_name = 'review_category'


class ViewReviewWidget(DetailView):

    def get(self, request, *args, **kwargs):
        this_review_widget = get_object_or_404(review_widget, pk=kwargs['pk'])
        context = {'review_widget': this_review_widget}
        return render(request, 'admin/view_review_widget.html', context)


def add_review_category(request):
    if request.method == 'POST':
        updated_data = request.POST.copy()

        gtfs_type = get_field_type(request.POST.get('form_ReviewCategory-gtfs_field'), request.POST.get('form_ReviewCategory-review_table'))

        obj, created = gtfs_field.objects.get_or_create(name=request.POST.get('form_ReviewCategory-gtfs_field'),
                                                        table=request.POST.get('form_ReviewCategory-review_table'),
                                                        type=gtfs_type)

        updated_data.update({'form_ReviewCategory-gtfs_field': obj})

        form_ReviewCategory = AddReviewCategory(updated_data, prefix="form_ReviewCategory")
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

            return redirect('configure_widget', widget_type="review", widget_id=this_review_widget.id)

    else:
        from gtfs_grading_app.gtfs_spec.import_gtfs_spec import get_gtfs_table_tuple
        t = get_gtfs_table_tuple()
        form_ReviewCategory = AddReviewCategory(prefix="form_ReviewCategory")
        form_ReviewWidget = AddReviewWidget(prefix="form_ReviewWidget")
        form_AddConsistencyWidget = AddConsistencyWidget(prefix="form_AddConsistencyWidget")
        form_AddResultsCaptureWidget = AddResultsCaptureWidget(prefix="form_AddResultsCaptureWidget")

    drop_down = get_cascading_drop_down()

    return render(request, 'admin/add_review_category.html', {'form_ReviewCategory': form_ReviewCategory,
                                                              'form_ReviewWidget': form_ReviewWidget,
                                                              'form_AddConsistencyWidget': form_AddConsistencyWidget,
                                                              'form_AddResultsCaptureWidget': form_AddResultsCaptureWidget,
                                                              'drop_down': drop_down})


def delete_review_category(request, review_category_id):
    instance = review_category.objects.get(id=review_category_id)
    instance.delete()
    messages.success(request, 'The review category has been deleted')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def configure_widget(request, widget_type, widget_id):
    if widget_type == "review":
        this_widget = review_widget_factory(get_object_or_404(review_widget, id=widget_id))
    elif widget_type == "consistency":
        this_widget = consistency_widget_factory(get_object_or_404(consistency_widget, id=widget_id))
    elif widget_type == "results_capture":
        this_widget = results_capture_widget_factory(get_object_or_404(results_capture_widget, id=widget_id))
    else:
        raise NotImplementedError

    creation_form = this_widget.get_creation_form(instance=this_widget.model_instance)

    if request.POST:
        forms = this_widget.get_configuration_form(request.POST, request.FILES)

        any_valid = False
        for key, value in forms.items():
            if value[0].is_valid():
                all_valid = True
                value[0].save()
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        forms = this_widget.get_configuration_form()

    template = this_widget.get_configuration_template()

    if not template:
        template = 'admin/configure_widget.html'

    return render(request, template, {'forms': forms,
                                      'this_widget': this_widget,
                                      'creation_form': creation_form
                                      })


def delete_consistency_widget_visual_example(request, image_id):
    image = get_object_or_404(consistency_widget_visual_example, id=image_id)
    image.delete()
    messages.success(request, 'The image has been deleted')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_consistency_widget_link(request, link_id):
    image = get_object_or_404(consistency_widget_link, id=link_id)
    image.delete()
    messages.success(request, 'The link has been deleted')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_review_widget_related_field_same_table(request, widget_id, field_id):
    widget = get_object_or_404(review_widget, id=widget_id)
    field = get_object_or_404(gtfs_field, id=field_id)
    widget.related_field_same_table.remove(field)
    messages.success(request, 'The related field has been removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_results_capture_score(request, score_id):
    my_score = score.objects.get(id=score_id)
    my_score.delete()
    messages.success(request, 'The score has been deleted')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))