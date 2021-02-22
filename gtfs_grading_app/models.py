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
    CHOICES = ((None, None),
               ("Optional", "Optional"),
               ("Required", "Required"))

    has_score_reason = models.CharField(null=True, blank=True, max_length=50, choices=CHOICES, default="Optional")
    has_score_image = models.CharField(null=True, blank=True, max_length=50, choices=CHOICES, default=None)
    has_reference_link = models.CharField(null=True, blank=True, max_length=50, choices=CHOICES, default=None)
    has_reference_date = models.CharField(null=True, blank=True, max_length=50, choices=CHOICES, default=None)

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
    CHOICES = (("In progress", "In progress"),
               ("In review", "In review"),
               ("Completed", "Completed"))

    agency = models.CharField(max_length=150, null=False)
    mode = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    review_status = models.CharField(null=False, max_length=50, default="In progress", choices=CHOICES)
    completed_date = models.DateTimeField(null=True)
    final_score = models.FloatField(null=True)

    def mark_status_in_review(self):
        self.review_status = "In review"
        self.save()

    def mark_status_complete(self):
        self.review_status = "Completed"
        self.save()

class result(models.Model):
    review = models.ForeignKey(review, on_delete=models.PROTECT)
    review_category = models.ForeignKey(review_category, on_delete=models.PROTECT)
    score = models.ForeignKey(score, null=True, on_delete=models.PROTECT)
    score_reason = models.TextField(null=True)
    reviewed_data = models.TextField()
    reviewed_data_pk_name = models.CharField(max_length=100)
    reviewed_data_pk_value = models.CharField(max_length=100)


class related_field(models.Model):
    result = models.ForeignKey(result, on_delete=models.CASCADE)
    gtfs_field = models.ForeignKey(gtfs_field, on_delete=models.PROTECT)
    gtfs_field_value = models.TextField()


class result_image(models.Model):
    result = models.ForeignKey(result, on_delete=models.CASCADE)
    image = models.ImageField(null=False, upload_to='result_images')


class result_reference(models.Model):
    result = models.ForeignKey(result, on_delete=models.CASCADE)
    reference_name = models.CharField(null=True, max_length=200)
    url = models.URLField()
    published_reference_date = models.DateTimeField(null=True)


class mode_lookup_table(models.Model):
    mode_id = models.ImageField(null=False)
    mode_name = models.CharField(null=False, max_length=150)
    mode_description = models.CharField(null=False, max_length=300)









