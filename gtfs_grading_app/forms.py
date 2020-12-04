from django import forms

from gtfs_grading_app.models import review_category, review_widget, consistency_widget, results_capture_widget, \
    gtfs_field


class GtfsZipForm(forms.Form):
    file = forms.FileField()


class AddReviewCategory(forms.ModelForm):
    class Meta:
        model = review_category
        exclude = ['review_widget', 'consistency_widget', 'results_capture_widget', 'review_table']


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
        exclude = []