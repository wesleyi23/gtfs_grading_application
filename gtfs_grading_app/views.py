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

from gtfs_grading_app.Functions.functions import list_to_tuple_of_tuples, get_next_review_item, get_previous_review_item
from gtfs_grading_app.classes.classes import review_widget_factory, consistency_widget_factory, \
    results_capture_widget_factory, ReviewWidget, DataSelector
from gtfs_grading_app.forms import GtfsZipForm, AddReviewCategory, AddReviewWidget, AddConsistencyWidget, \
    AddResultsCaptureWidget, AddResultCaptureScore, AddReviewWidgetRelatedFieldSameTable, ChooseDataSelector, \
    NewReviewForm, ResultForm
from gtfs_grading_app.models import review_category, review_widget, consistency_widget, results_capture_widget, \
    gtfs_field, consistency_widget_visual_example, consistency_widget_link, score, review, result

from gtfs_grading_app.gtfs_spec.import_gtfs_spec import get_cascading_drop_down, get_field_type

# TODO change name
def new_home(request):
    """Home page view"""

    return render(request, 'home.html', {})

def about(request):
    """Home page view"""
    active_page = 'about'
    return render(request, 'about.html', {'active_page':active_page})

def administration(request):
    active_page = 'admin'
    existing_review_categories = review_category.objects.select_related().all()

    return render(request, 'admin/administration.html', {'active_page': active_page,
                                                         'existing_review_categories': existing_review_categories})

def amdin_add_new(request):
    active_page = 'admin'
    active_review = 'add_new'
    drop_down = get_cascading_drop_down()

    existing_review_categories = review_category.objects.select_related().all()

    if request.POST:
        form = AddReviewCategory(request.POST, prefix="form_ReviewCategory")
        if form.is_valid():
            form.save()
    else:
        form = AddReviewCategory(prefix="form_ReviewCategory")

    return render(request, 'admin/admin_add_new.html', {'active_page': active_page,
                                                        'active_review': active_review,
                                                        'form': form,
                                                        'drop_down': drop_down,
                                                        'existing_review_categories': existing_review_categories})


def admin_details(request, review_id):
    active_page = 'admin'
    existing_review_categories = review_category.objects.select_related().all()
    current_review = review_category.objects.select_related().get(id=review_id)
    active_review = current_review.id

    scores = score.objects.filter(results_capture_widget_id=current_review.results_capture_widget_id).order_by('-score')


    related_fields_same_table = current_review.review_widget.related_field_same_table.all()


    choose_data_selector = ChooseDataSelector(my_review_category=current_review,
                                              prefix="choose_data_selector",
                                              initial={'name': current_review.data_selector.name,
                                                       'number_to_review': current_review.data_selector.number_to_review})

    add_score_form = AddResultCaptureScore(initial={
        'results_capture_widget': current_review.results_capture_widget}, prefix='score_form')
    add_field_same_table_form = AddReviewWidgetRelatedFieldSameTable(my_gtfs_table_name=current_review.gtfs_field.table,
                                                                     prefix="field_same_table_form",
                                                                     initial={'review_widget_id': current_review.review_widget.id})

    update_results_capture_widget = AddResultsCaptureWidget(instance=current_review.results_capture_widget,
                                                            prefix="update_results_capture_widget")


    if request.POST:
        if 'choose_data_selector' in request.POST:
            choose_data_selector = ChooseDataSelector(request.POST,
                                                      my_review_category=current_review,
                                                      prefix="choose_data_selector",
                                                      )
            if choose_data_selector.is_valid():
                choose_data_selector.save()
                choose_data_selector = ChooseDataSelector(my_review_category=current_review,
                                                          prefix="choose_data_selector",
                                                          initial={'name': current_review.data_selector.name,
                                                                   'number_to_review': current_review.data_selector.number_to_review})


        if 'add_new_score' in request.POST:
            add_score_form = AddResultCaptureScore(request.POST, prefix='score_form')
            if add_score_form.is_valid():
                add_score_form.save()
                add_score_form = AddResultCaptureScore(initial={
                    'results_capture_widget': current_review.results_capture_widget}, prefix='score_form')

        if 'add_field_same_table' in request.POST:
            add_field_same_table_form = AddReviewWidgetRelatedFieldSameTable(request.POST,
                                                                             my_gtfs_table_name=current_review.gtfs_field.table,
                                                                             prefix="field_same_table_form",
                                                                             )
            if add_field_same_table_form.is_valid():
                add_field_same_table_form.save()
                add_field_same_table_form = AddReviewWidgetRelatedFieldSameTable(my_gtfs_table_name=current_review.gtfs_field.table,
                                                                                 prefix="field_same_table_form",
                                                                                 initial={'review_widget_id': current_review.review_widget.id})
            else:
                raise ValueError

        if 'update_results_capture_widget' in request.POST:
            update_results_capture_widget = AddResultsCaptureWidget(request.POST,
                                                                    instance=current_review.results_capture_widget,
                                                                    prefix="update_results_capture_widget",
                                                                    )
            if update_results_capture_widget.is_valid():
                update_results_capture_widget.save()
                update_results_capture_widget = AddResultsCaptureWidget(instance=current_review.results_capture_widget,
                                                                        prefix="update_results_capture_widget")

    return render(request, 'admin/admin_details.html', {'active_page': active_page,
                                                        'active_review': active_review,
                                                        'current_review': current_review,
                                                        'existing_review_categories': existing_review_categories,
                                                        'choose_data_selector': choose_data_selector,
                                                        'scores': scores,
                                                        'add_score_form': add_score_form,
                                                        'related_fields_same_table': related_fields_same_table,
                                                        'add_field_same_table_form': add_field_same_table_form,
                                                        'update_results_capture_widget': update_results_capture_widget})


def evaluate_feed(request, review_id=None, active_review_category_id=None, active_result_number=None):
    if review_id is None:
        return redirect(start_new_evaluation)
    if active_review_category_id is None:
        active_review_category = review_category.objects.first()
    else:
        active_review_category = get_object_or_404(review_category, pk=active_review_category_id)
    if active_result_number is None:
        active_result_number = 1

    active_review = get_object_or_404(review, pk=review_id)

    review_categories = review_category.objects.all()
    results = result.objects.filter(review_id=review_id, review_category_id=active_review_category.id)
    active_result = results[active_result_number-1]
    max_items = results.count()

    # one result form for all widgets save method in forms
    #   The form lives at this level - scores and display of the form lives within the result capture widget
    form = ResultForm(initial={'result_id': active_result.id})

    active_review_widget = review_widget_factory(active_review_category.review_widget)
    review_widget_template = active_review_widget.get_template()
    review_widget_context = active_review_widget.get_template_context(active_result)

    active_result_capture_widget = results_capture_widget_factory(active_review_category.results_capture_widget)
    result_capture_template = active_result_capture_widget.get_template()
    result_capture_context = active_result_capture_widget.get_template_context(active_result)

    next_review_path = get_next_review_item(active_result_number,
                                            max_items,
                                            active_review,
                                            active_review_category,
                                            review_categories)
    previous_review_path = get_previous_review_item(active_result_number,
                                                    max_items,
                                                    active_review,
                                                    active_review_category,
                                                    review_categories)


    context = {'active_review': active_review,
               'review_categories': review_categories,
               'active_review_category': active_review_category,
               'active_result': active_result,
               'active_result_number': active_result_number,
               'max_items': max_items,
               'review_widget_template': review_widget_template,
               'result_capture_template': result_capture_template,
               'form': form,
               'next_review_path': next_review_path,
               'previous_review_path': previous_review_path}

    context.update(review_widget_context)
    context.update(result_capture_context)

    return render(request, 'evaluate_feed.html', context)


def start_new_evaluation(request):
    tmp_dir = request.session['gtfs_feed']
    gtfs_feed = ptg.load_feed(tmp_dir)
    agency_options = gtfs_feed.agency['agency_name'].tolist()
    agency_options = list_to_tuple_of_tuples(agency_options)
    mode_options = list(set(gtfs_feed.routes['route_type'].tolist()))
    mode_options = list_to_tuple_of_tuples(mode_options)
    if request.POST:
        my_new_review_form = NewReviewForm(request.POST, agency_options=agency_options, mode_options=mode_options)
        if my_new_review_form.is_valid():
            agency_name = my_new_review_form.cleaned_data['agency']
            mode = my_new_review_form.cleaned_data['mode']
            new_session_gtfs_path, my_review = DataSelector.setup_initial_data_for_review(request.session['gtfs_feed'],
                                                                                          agency_name,
                                                                                          mode)
            request.session['gtfs_feed'] = new_session_gtfs_path
            return redirect(evaluate_feed, review_id=my_review.id)

    if request.session.get('gtfs_feed', None):
        tmp_dir = request.session['gtfs_feed']
        gtfs_feed = ptg.load_feed(tmp_dir)
        agency_options = gtfs_feed.agency['agency_name'].tolist()
        agency_options = list_to_tuple_of_tuples(agency_options)
        mode_options = list(set(gtfs_feed.routes['route_type'].tolist()))
        mode_options = list_to_tuple_of_tuples(mode_options)
        my_new_review_form = NewReviewForm(agency_options=agency_options, mode_options=mode_options)
    else:
        my_new_review_form = None

    return render(request, 'start_new_evaluation.html', {'my_new_review_form': my_new_review_form})


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

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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

