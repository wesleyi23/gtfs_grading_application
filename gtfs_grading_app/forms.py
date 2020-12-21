from django import forms

from gtfs_grading import settings
from gtfs_grading_app.models import review_category, review_widget, consistency_widget, results_capture_widget, \
    gtfs_field, consistency_widget_visual_example, consistency_widget_link, score
from gtfs_grading_app.gtfs_spec.import_gtfs_spec import get_gtfs_table_tuple, get_field_type, \
    get_gtfs_field_tuple_from_table


class GtfsZipForm(forms.Form):
    file = forms.FileField()


class AddReviewCategory(forms.ModelForm):

    class Meta:
        model = review_category
        fields = ['review_table', 'gtfs_field']
        widgets = {'review_table': forms.Select(choices=get_gtfs_table_tuple())}


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
        self.fields['field_name'] = forms.ChoiceField(choices=CHOICES)
        self.fields['review_widget_id'] = forms.IntegerField(widget=forms.HiddenInput())

    def save(self):
        field_type = get_field_type(self.cleaned_data['field_name'], self.gtfs_table_name)
        my_gtfs_field, created = gtfs_field.objects.get_or_create(name=self.cleaned_data['field_name'],
                                                                  table=self.gtfs_table_name,
                                                                  type=field_type)
        if created:
            my_gtfs_field.save()
        my_review_widget = review_widget.objects.get(id=self.cleaned_data['review_widget_id'])
        my_review_widget.related_field_same_table.add(my_gtfs_field)


class AddResultCaptureScore(forms.ModelForm):
    class Meta:
        model = score
        exclude = ['']
        widgets = {'results_capture_widget': forms.HiddenInput()}







