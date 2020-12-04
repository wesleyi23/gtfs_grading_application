from django.db import models

# Create your models here.
from gtfs_grading_app.classes.classes import review_widget_factory, review_field_factory, consistency_widget_factory


class gtfs_field(models.Model):
    name = models.CharField(max_length=150, null=False)
    table = models.CharField(max_length=150, null=False)
    type = models.CharField(max_length=150, null=False)

    @property
    def get_review_field(self):
        return review_field_factory(self)

    def __str__(self):
        return self.name


class review_widget(models.Model):
    has_field = models.BooleanField(null=False, default=True)
    has_related_field_same_table = models.BooleanField(null=False, default=False)
    related_field_same_table = models.ManyToManyField(gtfs_field, related_name='+')
    has_related_field_other_table = models.BooleanField(null=False, default=False)
    related_field_other_table = models.CharField(max_length=150, null=True) # named reference to a function that will be coded to select this data

    def get_review_widget(self):
        return review_widget_factory(self)


class consistency_widget(models.Model):
    has_visual_example = models.BooleanField(null=False, default=False)
    has_link = models.BooleanField(null=False, default=False)
    has_other_text = models.BooleanField(null=False, default=False)
    other_text = models.CharField(max_length=500)

    def get_consistency_widget(self):
        consistency_widget_factory(self)


class consistency_widget_visual_example(models.Model):
    consistency_widget = models.ForeignKey(consistency_widget, on_delete=models.PROTECT)
    name = models.CharField(max_length=150, null=False)
    description = models.CharField(max_length=150)
    image = models.ImageField(null=False)


class consistency_widget_link(models.Model):
    consistency_widget = models.ForeignKey(consistency_widget, on_delete=models.PROTECT)
    url = models.URLField(null=False)
    url_display_text = models.CharField(max_length=150, null=False)


class results_capture_widget(models.Model):
    has_score = models.BooleanField(null=False, default=True)
    has_score_reason = models.BooleanField(null=False, default=True)
    has_score_image = models.BooleanField(null=False, default=False)


class score(models.Model):
    score = models.DecimalField(decimal_places=2, max_digits=4, null=False)
    score_help_text = models.CharField(max_length=150, null=False)
    results_capture_widget = models.ForeignKey(results_capture_widget, on_delete=models.PROTECT)


class selected_rows(models.Model):
    gtfs_field = models.ForeignKey(gtfs_field, on_delete=models.PROTECT)
    row_number = models.IntegerField(null=False)


class review_category(models.Model):
    gtfs_field = models.ForeignKey(gtfs_field, on_delete=models.PROTECT)
    review_table = models.CharField(max_length=150, null=False)
    review_widget = models.OneToOneField(review_widget, on_delete=models.PROTECT)
    consistency_widget = models.OneToOneField(consistency_widget, on_delete=models.PROTECT)
    results_capture_widget = models.OneToOneField(results_capture_widget, on_delete=models.PROTECT)


class result(models.Model):
    review_category = models.ForeignKey(review_category, on_delete=models.PROTECT)
    selected_rows = models.ManyToManyField(selected_rows)
    score = models.ForeignKey(score, on_delete=models.PROTECT)
    score_reason = models.CharField(max_length=150)
    reviewed_data = models.CharField(max_length=150)


class result_image(models.Model):
    result = models.ForeignKey(result, on_delete=models.PROTECT)
    image = models.ImageField(null=False)










