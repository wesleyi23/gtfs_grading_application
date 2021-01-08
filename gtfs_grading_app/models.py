from django.db import models

# Create your models here.


class gtfs_field(models.Model):
    name = models.CharField(max_length=150, null=False)
    table = models.CharField(max_length=150, null=False)
    type = models.CharField(max_length=150, null=False)

    def __str__(self):
        return self.name

    @property
    def field_name_to_label(self):
        value = self.name.replace('_', ' ')
        return value.title()


class review_widget(models.Model):
    has_field = models.BooleanField(null=False, default=True)
    related_field_same_table = models.ManyToManyField(gtfs_field, related_name='+')
    related_field_other_table = models.CharField(max_length=150, null=True) # named reference to a function that will be coded to select this data

    @property
    def has_related_field_same_table(self):
        return self.related_field_same_table.count() > 0

    @property
    def has_related_field_other_table(self):
        if self.related_field_other_table:
            return True
        else:
            return False


class consistency_widget(models.Model):
    other_text = models.TextField(null=True)

    @property
    def has_visual_example(self):
        return consistency_widget_visual_example.objects.filter(consistency_widget=self).count() > 0

    @property
    def has_link(self):
        return consistency_widget_link.objects.filter(consistency_widget=self).count() > 0

    @property
    def has_other_text(self):
        if self.other_text:
            return True
        else:
            return False


class consistency_widget_visual_example(models.Model):
    consistency_widget = models.ForeignKey(consistency_widget, on_delete=models.PROTECT)
    name = models.CharField(max_length=150, null=False)
    description = models.CharField(max_length=150)
    image = models.ImageField(null=False, upload_to='consistency_images/')


class consistency_widget_link(models.Model):
    consistency_widget = models.ForeignKey(consistency_widget, on_delete=models.PROTECT)
    url = models.URLField(null=False)
    url_display_text = models.CharField(max_length=150, null=False)


class results_capture_widget(models.Model):
    has_score_reason = models.BooleanField(null=False, default=True)
    has_score_image = models.BooleanField(null=False, default=False)
    has_reference_link = models.BooleanField(null=False, default=False)
    has_reference_date = models.BooleanField(null=False, default=False)

    @property
    def has_score(self):
        return score.objects.filter(results_capture_widget=self).count()


class score(models.Model):
    score = models.DecimalField(decimal_places=2, max_digits=4, null=False)
    help_text = models.TextField(null=False)
    results_capture_widget = models.ForeignKey(results_capture_widget, on_delete=models.PROTECT)


class data_selector(models.Model):
    name = models.CharField(max_length=150)
    number_to_review = models.IntegerField(null=True)


class review_category(models.Model):
    gtfs_field = models.ForeignKey(gtfs_field, on_delete=models.PROTECT)
    review_widget = models.OneToOneField(review_widget, on_delete=models.CASCADE)
    consistency_widget = models.OneToOneField(consistency_widget, on_delete=models.CASCADE)
    results_capture_widget = models.OneToOneField(results_capture_widget, on_delete=models.CASCADE)
    data_selector = models.ForeignKey('data_selector', default=1, on_delete=models.PROTECT)


class review(models.Model):
    agency = models.CharField(max_length=150, null=False)
    mode = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True)


class result(models.Model):
    review = models.ForeignKey(review, on_delete=models.PROTECT)
    review_category = models.ForeignKey(review_category, on_delete=models.PROTECT)
    score = models.ForeignKey(score, null=True, on_delete=models.PROTECT)
    score_reason = models.TextField(null=True)
    reviewed_data = models.TextField()


class related_field(models.Model):
    result = models.ForeignKey(result, on_delete=models.PROTECT)
    gtfs_field = models.ForeignKey(gtfs_field, on_delete=models.PROTECT)
    gtfs_field_value = models.TextField()


class result_image(models.Model):
    result = models.ForeignKey(result, on_delete=models.PROTECT)
    image = models.ImageField(null=False)


class result_reference(models.Model):
    result = models.ForeignKey(result, on_delete=models.PROTECT)
    reference_name = models.CharField(null=True, max_length=200)
    url = models.URLField()
    published_reference_date = models.DateTimeField(auto_now_add=True)








