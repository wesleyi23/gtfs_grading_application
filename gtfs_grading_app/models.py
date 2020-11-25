from django.db import models

# Create your models here.


class GtfsField(models.Model):
    name = models.CharField(max_length=150, null=False)
    table = models.CharField(max_length=150, null=False)
    type = models.CharField(max_length=150, null=False)


class ReviewWidget(models.Model):
    review_field = models.ForeignKey(GtfsField, on_delete=models.PROTECT)
    related_field_same_table = models.ManyToManyField(GtfsField, related_name='+')
    related_field_other_table = models.CharField(max_length=150, null=True) # named reference to a function that will be coded to select this data

    def save(self, *args, **kwargs):
        if self.related_field_same_table.table != self.review_field.table:
            raise ValueError("Related field must be in the same table.")
        else:
            super().save(*args, **kwargs)


class ConsistencyWidget(models.Model):
    other_text = models.CharField(max_length=500)


class ConsistencyWidgetVisualExample(models.Model):
    consistency_widget = models.ForeignKey(ConsistencyWidget, on_delete=models.PROTECT)
    name = models.CharField(max_length=150, null=False)
    description = models.CharField(max_length=150)
    image = models.ImageField(null=False)


class ConsistencyWidgetLink(models.Model):
    consistency_widget = models.ForeignKey(ConsistencyWidget, on_delete=models.PROTECT)
    url = models.URLField(null=False)
    url_display_text = models.CharField(max_length=150, null=False)


class Score(models.Model):
    ReviewWidget = models.ForeignKey(ReviewWidget, on_delete=models.PROTECT)
    score = models.DecimalField(decimal_places=2, max_digits=4, null=False)
    score_help_text = models.CharField(max_length=150, null=False)


class ResultsCaptureWidget(models.Model):
    review_widget = models.ForeignKey(ReviewWidget, on_delete=models.PROTECT)
    score = models.ForeignKey(Score, on_delete=models.PROTECT)


class SelectedRows(models.Model):
    review_field = models.ForeignKey(GtfsField, on_delete=models.PROTECT)
    row_number = models.IntegerField(null=False)


class ReviewCategory(models.Model):
    review_widget = models.OneToOneField(ReviewWidget, on_delete=models.PROTECT)
    consistency_widget = models.OneToOneField(ConsistencyWidget, on_delete=models.PROTECT)
    results_widget = models.OneToOneField(ResultsCaptureWidget, on_delete=models.PROTECT)
    selected_rows = models.ManyToManyField(SelectedRows)


class Result(models.Model):
    reviewed_field = models.ForeignKey(GtfsField, on_delete=models.PROTECT)
    review_category = models.ForeignKey(ReviewCategory, on_delete=models.PROTECT)
    score = models.ForeignKey(Score, on_delete=models.PROTECT)
    score_reason = models.CharField(max_length=150)
    reviewed_data = models.CharField(max_length=150)


class ResultImage(models.Model):
    result = models.ForeignKey(Result, on_delete=models.PROTECT)
    image = models.ImageField(null=False)










