
####
# This file contains classes used in this application.
#
# The application is organized around a number of abstract classes, representing widgets, that
# are displayed to the end user. These include:
#   - ReviewWidget - A widget to display information that is reviewed
#   - ConsistencyWidget - A widget to display information that may be helpful to the reviewer while they complete their
#     review
#   - ResultsCaptureWidget - A widget that captures the results of the review
#
# There are also two other abstract classes that facilitate reviews:
#   - ReviewField - which enables the display of different types of data in GTFS feed. For example color and text.
#   - DataSelector - which enables different methods for selecting data from a GTFS feed.
#
# A review of an individual field or other element will use the concrete implementations of each of these widgets for
# example:
#   - A field may need to be reviewed log10(n) times, have related data in the same table that needs to be displayed,
#     a link to a best practice, and need a screen shot from a website that is captured during the review.
#   - Another field might need to be reviewed 5 times, only display itself, have visual examples, and capture only a
#     score and text.
#   - A new field might come along that needs totally different functionality. Rather than updating the existing code to
#     to meet these new requirements new concrete classes can be developed , without needing to worry about breaking
#     existing code.
#
#
# For each abstract class in this file there is also:
#   - A factory to generate the appropriate concrete class
#   - Any classes derived from the abstract class
#####
import math
import tempfile
from abc import ABC, abstractmethod, ABCMeta
# from django.core.files import File
from typing import final, Type, Union, List, Any, Dict
# from django.forms import forms

# from gtfs_grading_app.forms import AddConsistencyWidgetVisualExample, AddConsistencyWidgetLink, \
#     AddConsistencyWidgetOtherText, AddReviewWidgetRelatedFieldSameTable, AddResultCaptureScore, AddReviewWidget, \
#     AddConsistencyWidget, AddResultsCaptureWidget
from django.db import transaction

from gtfs_grading_app.models import review_category, consistency_widget_visual_example, consistency_widget_link, score, \
    review, result, related_field
import partridge as ptg # type: ignore

# region ReviewWidget

class Widget(ABC):

    @property
    @abstractmethod
    def widget_type(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def model_instance(self):
        raise NotImplementedError

    @property
    def review_category(self) -> review_category:
        if self.widget_type == "review":
            return review_category.objects.get(review_widget=self.model_instance)
        elif self.widget_type == "consistency":
            return review_category.objects.get(consistency_widget=self.model_instance)
        elif self.widget_type == "results_capture":
            return review_category.objects.get(results_capture_widget=self.model_instance)
        else:
            raise NotImplementedError

    @abstractmethod
    def get_template_context(self, active_result) -> Union[None, dict]:
        """returns data needed for django template to display this class"""
        raise NotImplementedError

    @abstractmethod
    def get_template(self) -> Union[None, str]:
        """returns django template to display this class"""
        raise NotImplementedError


class ReviewWidget(Widget):
    """A ReviewWidget presents all data from a GTFS feed a user needs to complete their review."""

    @property
    def widget_type(self):
        return 'review'

    def __init__(self, my_review_widget):
        self.my_review_widget = my_review_widget

    @property
    def model_instance(self):
        return self.my_review_widget


def review_widget_factory(review_widget) -> ReviewWidget:
    """This factory produces the appropriate ReviewWidget based on the configuration data stored in the review widget table

    Args:
        review_widget: an instance of the review widget model
    """

    if not review_widget.has_related_field_same_table and not review_widget.has_related_field_other_table:
        return SingleFieldReviewWidget(review_widget)
    else:
        return DefaultReviewWidget(review_widget)


class SingleFieldReviewWidget(ReviewWidget):
    """This class produces a review widget that only displays the field"""

    def get_template_context(self, active_result) -> Union[None, dict]:
        pass

    def get_template(self) -> Union[None, str]:
        pass


class DefaultReviewWidget(ReviewWidget):

    def get_template(self) -> Union[None, str]:
        return "review_widgets/default_review_widget.html"

    def get_template_context(self, active_result) -> Union[None, dict]:
        active_gtfs_field = active_result.review_category.gtfs_field
        review_field = review_field_factory(active_gtfs_field)

        related_fields = related_field.objects.filter(result=active_result)

        context = {'review_field_template': review_field.get_field_template(),
                   'related_fields': related_fields}
        context.update(review_field.get_template_context(active_result))

        return context

    # endregion

# region ReviewField


class ReviewField(ABC):
    """A ReviewField has all of the information about a field in a GTFS feed that is needed by the application to
    display that field. For example field is a color and needs a method to display it."""

    @abstractmethod
    def get_field_template(self) -> Union[None, str]:
        """returns HTML for use in a template"""
        raise NotImplementedError

    @abstractmethod
    def get_template_context(self, active_result) -> Union[None, dict]:
        """returns context for use in a template"""
        raise NotImplementedError



def review_field_factory(gtfs_field):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

    Args:
        gtfs_field: an instance of the gtfs_field model
    """

    if gtfs_field.type == "Text":
        return TextReviewField(gtfs_field)
    else:
        raise NotImplementedError


class TextReviewField(ReviewField):

    def __init__(self, gtfs_field):
        self.gtfs_field = gtfs_field

    def get_field_template(self) -> Union[None, str]:
        return 'review_field/text.html'

    def get_template_context(self, active_result) -> Union[None, dict]:
        field_value = active_result.reviewed_data
        return {'field_value': field_value}


# endregion

# region ConsistencyWidget

class ConsistencyWidget(Widget):
    """A consistency widget contains information, not related to the GTFS Feed that may be helpful to the reviewer
    as they complete their review.  It could include things like links, examples, or images."""

    @property
    def widget_type(self):
        return 'consistency'

    def __init__(self, my_consistency_widget):
        self.my_consistency_widget = my_consistency_widget

    @property
    def model_instance(self):
        return self.my_consistency_widget


def consistency_widget_factory(consistency_widget):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

    Args:
        consistency_widget: an instance of the consistency_widget model
    """

    return DefaultConsistencyWidget(consistency_widget)


class DefaultConsistencyWidget(ConsistencyWidget):

    def get_template_context(self, active_result) -> Union[None, dict]:
        return None

    def get_template(self) -> None:
        pass

# endregion

# region ResultsCaptureWidget
class ResultsCaptureWidget(Widget):
    """A results capture widget contains information and methods to record the results of a review"""

    @property
    def widget_type(self):
        return 'results_capture'

    def __init__(self, my_results_capture_widget):
        self.my_results_capture_widget = my_results_capture_widget

    @property
    def model_instance(self):
        return self.my_results_capture_widget


def results_capture_widget_factory(results_capture_widget):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

        Args:
            results_capture_widget: an instance of the results_capture_widget model
    """

    return DefaultResultsCaptureWidget(results_capture_widget)


class DefaultResultsCaptureWidget(ResultsCaptureWidget):

    def get_template(self) -> str:
        return "result_capture_widgets/default_result_capture_widget.html"

    def get_template_context(self, active_result) -> Union[None, dict]:
        scores = score.objects.filter(results_capture_widget=self.my_results_capture_widget).order_by('score')
        return {'scores': scores}



# endregion

# region DataSelector

class DataSelector(ABC):
    """DataSelector abstract class are variation of methods for selecting data from GTFS Feeds"""

    @staticmethod
    def get_valid_choices_and_related_fields():
        choices = (
            ("log10(n) + 2", "log10(n) + 2"),
            ("number", 'number')
        )
        related_fields = [None, 'number_to_review']
        return choices, related_fields

    @abstractmethod
    def select_row_sample_count(self, total_row) -> int:
        '''This method takes the total number of rows in a table and returns the number of rows to sample'''
        raise NotImplementedError


    @staticmethod
    def setup_initial_data_for_review(gtfs_feed_zip_file, agency, mode):
        '''This method will select the initial set of data that will be reviewed from the provided GTFS zip file'''
        my_review = review.objects.create(agency=agency,
                                          mode=mode)
        view = {
            'agency.txt': {'agency_name': agency},
            'routes.txt': {'route_type': mode},
        }
        new_tmp_dir = tempfile.mkdtemp()
        outpath = new_tmp_dir
        ptg.extract_feed(gtfs_feed_zip_file, outpath + "view.zip", view)
        gtfs_feed = ptg.load_feed(gtfs_feed_zip_file)

        new_session_gtfs_path = outpath + "view.zip"

        for category in review_category.objects.all():
            target_field_name = category.gtfs_field.name
            target_table = category.gtfs_field.table
            has_related_field_same_table = category.review_widget.has_related_field_same_table
            has_related_field_other_table = category.review_widget.has_related_field_other_table
            ptg_target_table = getattr(gtfs_feed, target_table.replace('.txt', ''))
            total_table_rows = ptg_target_table.shape[0]
            ds = data_selector_factory(category.data_selector)

            number_to_sample = ds.select_row_sample_count(total_table_rows)
            random_sample = ptg_target_table.sample(n=number_to_sample)

            for index, row in random_sample.iterrows():
                this_result = result.objects.create(review=my_review,
                                                    review_category=category,
                                                    reviewed_data=row[target_field_name])
                if has_related_field_same_table:
                    related_fields = category.review_widget.related_field_same_table.all()
                    for field in related_fields:
                        my_field = related_field.objects.create(gtfs_field=field,
                                                                result=this_result,
                                                                gtfs_field_value=row[field.name])

                if has_related_field_other_table:
                    raise NotImplementedError

        return new_session_gtfs_path, my_review

    def select_new_data_for_review(self, gtfs_feed, current_result_id):
        '''This method will replace the specified current result with a new one from the gtfs_feed'''
        raise NotImplementedError


def data_selector_factory(data_selector):
    """This factory produces the appropriate DataSelector based on the configuration data provided

        Args:
            data_selector: an instance of the data_selector model
    """
    if data_selector.name == "log10(n) + 2":
        return LogPlusTwoDataSelector()

    elif data_selector.name == "number":
        return NumberDataSelector()

    else:
        raise NotImplementedError


class LogPlusTwoDataSelector(DataSelector):

    def __int__(self, data_selector):
        self.data_selector = data_selector

    def select_row_sample_count(self, total_row) -> int:
        x = math.log10(total_row) + 2
        print(x)
        x = round(x)
        if total_row > x:
            return x
        else:
            return total_row


class NumberDataSelector(DataSelector):

    def __int__(self, data_selector):
        self.data_selector = data_selector

    def select_row_sample_count(self, total_row) -> int:
        x = self.data_selector.number_to_review
        if total_row > x:
            return x
        else:
            return total_row
# endregion