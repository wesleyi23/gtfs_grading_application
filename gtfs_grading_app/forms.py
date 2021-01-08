from django import forms

from gtfs_grading import settings
from gtfs_grading_app.Functions.functions import list_to_tuple_of_tuples

from gtfs_grading_app.models import review_category, review_widget, consistency_widget, results_capture_widget, \
    gtfs_field, consistency_widget_visual_example, consistency_widget_link, score, data_selector, result, result_image, \
    result_reference
from gtfs_grading_app.gtfs_spec.import_gtfs_spec import get_gtfs_table_tuple, get_field_type, \
    get_gtfs_field_tuple_from_table, get_all_gtfs_field_tuple
from gtfs_grading_app.classes.classes import DataSelector

class GtfsZipForm(forms.Form):
    file = forms.FileField()


class AddReviewCategory(forms.Form):

    review_table = forms.ChoiceField(label='Table',
                                     widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
    gtfs_field = forms.ChoiceField(label='Field',
                                   widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))

    def __init__(self, *args, **kwargs):
        CHOICES_TABLE = get_gtfs_table_tuple()
        CHOICES_FIELD = get_all_gtfs_field_tuple()
        print(CHOICES_FIELD)
        super().__init__(*args, **kwargs)
        self.fields['review_table'].choices = CHOICES_TABLE
        self.fields['gtfs_field'].choices = CHOICES_FIELD

    def save(self):
        data = self.cleaned_data

        gtfs_type = get_field_type(data['gtfs_field'],
                                   data['review_table'])

        obj, created = gtfs_field.objects.get_or_create(name=data['gtfs_field'],
                                                        table=data['review_table'],
                                                        type=gtfs_type)

        my_review_widget = review_widget.objects.create()
        my_consistency_widget = consistency_widget.objects.create()
        my_results_capture_widget = results_capture_widget.objects.create()

        my_review_category = review_category()
        my_review_category.gtfs_field = obj
        my_review_category.review_widget = my_review_widget
        my_review_category.consistency_widget = my_consistency_widget
        my_review_category.results_capture_widget = my_results_capture_widget
        my_review_category = my_review_category.save()
        return my_review_category

class AddReviewWidget(forms.ModelForm):

    class Meta:
        model = review_widget
        exclude = ['related_field_same_table', 'related_field_other_table']


# class AddRelatedFieldSameTable(forms.ModelForm):
#     class Meta:
#         EXAMPLE_FIELD_CHOICES = [
#             ('blue', 'Blue'),
#             ('green', 'Green'),
#             ('black', 'Black'),
#         ]
#         model = gtfs_field
#         exclude = ['table', 'type']
#         widgets = {'name': forms.SelectMultiple(choices=EXAMPLE_FIELD_CHOICES,)}



class AddConsistencyWidget(forms.ModelForm):
    class Meta:
        model = consistency_widget
        exclude = ['other_text']


class AddResultsCaptureWidget(forms.ModelForm):
    class Meta:
        model = results_capture_widget
        exclude = ['']


class AddConsistencyWidgetVisualExample(forms.ModelForm):
    class Meta:
        model = consistency_widget_visual_example
        exclude = ['']
        widgets = {'consistency_widget': forms.HiddenInput()}


class AddConsistencyWidgetLink(forms.ModelForm):
    class Meta:
        model = consistency_widget_link
        exclude = ['']
        widgets = {'consistency_widget': forms.HiddenInput()}


class AddConsistencyWidgetOtherText(forms.ModelForm):
    class Meta:
        model = consistency_widget
        fields = ['other_text']


class AddReviewWidgetRelatedFieldSameTable(forms.Form):

    def __init__(self, *args, **kwargs):
        my_gtfs_table_name = kwargs.pop("my_gtfs_table_name")
        super(AddReviewWidgetRelatedFieldSameTable, self).__init__(*args, **kwargs)
        self.gtfs_table_name = my_gtfs_table_name
        CHOICES = get_gtfs_field_tuple_from_table(my_gtfs_table_name)
        self.fields['field_name'] = forms.ChoiceField(choices=CHOICES, widget=forms.Select(attrs={'class': "form-select form-select-sm"}))
        self.fields['review_widget_id'] = forms.IntegerField(widget=forms.HiddenInput())

    def save(self):
        field_type = get_field_type(self.cleaned_data['field_name'], self.gtfs_table_name)
        my_gtfs_field, created = gtfs_field.objects.get_or_create(name=self.cleaned_data['field_name'],
                                                                  table=self.gtfs_table_name,
                                                                  type=field_type)
        # if created:
        #     my_gtfs_field.save()
        my_review_widget = review_widget.objects.get(id=self.cleaned_data['review_widget_id'])
        my_review_widget.related_field_same_table.add(my_gtfs_field)


class AddResultCaptureScore(forms.ModelForm):
    class Meta:
        model = score
        exclude = ['']
        widgets = {'results_capture_widget': forms.HiddenInput(),
                   'score': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                   'help_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2})}


class ChooseDataSelector(forms.Form):
    # see java script in admin_details.html when making changes

    def __init__(self, *args, **kwargs):
        self.my_review_catagory = kwargs.pop("my_review_category")
        CHOICES, related_fields = DataSelector.get_valid_choices_and_related_fields()
        super(ChooseDataSelector, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.ChoiceField(choices=CHOICES,
                                                label=False,
                                                widget=forms.Select(
                                                    attrs={'class': 'form-select form-select-sm'}))
        self.fields['number_to_review'] = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}))
        self.related_fields = related_fields

    def save(self):
        if self.cleaned_data['name'] == "log10(n) + 2":
            self.cleaned_data['number_to_review'] = None

        my_data_selector, created = data_selector.objects.get_or_create(name=self.cleaned_data['name'],
                                                                        number_to_review=self.cleaned_data['number_to_review'])
        self.my_review_catagory.data_selector = my_data_selector
        self.my_review_catagory.save()


class NewReviewForm(forms.Form):

    def __init__(self, *args, **kwargs):
        agency_options_choices = kwargs.pop('agency_options')
        mode_options_choices = kwargs.pop('mode_options')


        super(NewReviewForm, self).__init__(*args, **kwargs)
        self.fields['agency'] = forms.ChoiceField(choices=agency_options_choices,
                                                  label='Agency',
                                                  widget=forms.Select(
                                                      attrs={}))
        self.fields['mode'] = forms.ChoiceField(choices=mode_options_choices,
                                                label='Mode',
                                                widget=forms.Select(
                                                    attrs={}))


class ResultForm(forms.Form):

    result_id = forms.IntegerField(required=True, widget=forms.NumberInput())
    score_id = forms.IntegerField(required=True, widget=forms.NumberInput())
    score_reason = forms.Textarea()
    image = forms.ImageField()
    reference_name = forms.CharField()
    reference_url = forms.URLField()
    published_reference_date = forms.DateField()

    def __save__(self):
        my_review_category = review_category.objects.get(id=self.cleaned_data['review_category_id'])
        my_results_capture_widget = results_capture_widget.objects.get(id=my_review_category.results_capture_widget.id)
        my_result = result.objects.get(id=self.cleaned_data['result_id'])
        my_result.score_id = self.cleaned_data['score_id']

        if my_results_capture_widget.has_score_reason:
            my_result.score_reason = self.cleaned_data['score_reason']
        if my_results_capture_widget.has_score_image:
            result_image.objects.create(image=self.cleaned_data['image'],
                                        result_id=self.cleaned_data['result_id'])
        if my_result.has_reference_link:
            r = result_reference.objects.create(reference_name=self.cleaned_data['reference_name'],
                                                url=self.cleaned_data['reference_url'])
            if my_result.has_reference_date:
                r.published_reference_date = self.cleaned_data['published_reference_date']
                r.save()








