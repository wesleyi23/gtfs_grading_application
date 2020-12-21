
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

from abc import ABC, abstractmethod, ABCMeta
# from django.core.files import File
from typing import final, Type, Union, List, Any, Dict
from django.forms import forms

from gtfs_grading_app.forms import AddConsistencyWidgetVisualExample, AddConsistencyWidgetLink, \
    AddConsistencyWidgetOtherText, AddReviewWidgetRelatedFieldSameTable, AddResultCaptureScore, AddReviewWidget, \
    AddConsistencyWidget, AddResultsCaptureWidget
from gtfs_grading_app.models import review_category, consistency_widget_visual_example, consistency_widget_link, score


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

    @property
    def get_next_widget_type(self) -> Union[None, str]:
        if self.widget_type == "review":
            return "consistency"
        elif self.widget_type == "consistency":
            return "results_capture"
        elif self.widget_type == "results_capture":
            return None
        else:
            raise NotImplementedError

    @property
    def get_next_widget_id(self) -> Union[None, int]:
        if self.widget_type == "review":
            return review_category.objects.get(review_widget_id=self.model_instance.id).consistency_widget_id
        elif self.widget_type == "consistency":
            return review_category.objects.get(consistency_widget_id=self.model_instance.id).results_capture_widget_id
        elif self.widget_type == "results_capture":
            return None
        else:
            raise NotImplementedError

    @property
    def get_previous_widget_type(self) -> Union[None, str]:
        if self.widget_type == "review":
            return None
        elif self.widget_type == "consistency":
            return "review"
        elif self.widget_type == "results_capture":
            return "consistency"
        else:
            raise NotImplementedError

    @property
    def get_previous_widget_id(self) -> Union[None, int]:
        if self.widget_type == "review":
            return None
        elif self.widget_type == "consistency":
            return review_category.objects.get(consistency_widget_id=self.model_instance.id).review_widget_id
        elif self.widget_type == "results_capture":
            return review_category.objects.get(results_capture_widget_id=self.model_instance.id).consistency_widget_id
        else:
            raise NotImplementedError

    def get_creation_form(self, *args, **kwargs):
        if self.widget_type == "review":
            return AddReviewWidget(*args, **kwargs)
        elif self.widget_type == "consistency":
            return AddConsistencyWidget(*args, **kwargs)
        elif self.widget_type == "results_capture":
            return AddResultsCaptureWidget(*args, **kwargs)
        else:
            raise NotImplementedError

    @abstractmethod
    def get_template_data(self) -> Union[None, str]:
        """returns data needed for django template to display this class"""
        raise NotImplementedError

    @abstractmethod
    def get_template(self) -> None:
        """returns django template to display this class"""
        raise NotImplementedError

    @abstractmethod
    def get_configuration_form(self) -> Union[None, Dict[str, Any]]:
        """returns django form to configure the widget"""
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

    def get_configuration_form(self, request_post=None, request_files=None) -> Union[None, Dict[str, Any]]:
        """returns django form to configure this widget """
        my_forms = {}
        my_gtfs_table_name = self.review_category.gtfs_field.table
        if self.my_review_widget.has_related_field_same_table:
            form = AddReviewWidgetRelatedFieldSameTable(request_post,
                                                        my_gtfs_table_name=my_gtfs_table_name,  # type: ignore
                                                        prefix="form_ReviewWidgetRelatedFieldSameTable",
                                                        initial={'review_widget_id': self.my_review_widget.id})

            template_data = self.my_review_widget.related_field_same_table.all()

            my_forms['related_field_same_table'] = [form, template_data]


        if self.my_review_widget.has_related_field_other_table:
            my_forms['related_field_other_table'] = 'Yes' # type: ignore
        if my_forms == {}:
            return None
        else:
            return my_forms


    def get_configuration_template(self) -> Union[None, str]:
        """returns django template form to configure this widget"""
        return 'admin/default_review_widget_configure.html'



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

    def get_template_data(self) -> Union[None, str]:
        pass

    def get_template(self) -> None:
        pass


class DefaultReviewWidget(ReviewWidget):

    def get_template_data(self) -> Union[None, str]:
        return None

    def get_template(self) -> None:
        pass

# endregion

# region ReviewField


class ReviewField(ABC):
    """A ReviewField has all of the information about a field in a GTFS feed that is needed by the application to
    display that field. For example field is a color and needs a method to display it."""

    @abstractmethod
    def get_field_for_template(self) -> None:
        """returns HTML for use in a template"""
        raise NotImplementedError


def review_field_factory(gtfs_field):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

    Args:
        gtfs_field: an instance of the gtfs_field model
    """

    if gtfs_field.field_type == "Text":
        return TextReviewField(gtfs_field)


class TextReviewField(ReviewField):

    def __init__(self, gtfs_field):
        self.gtfs_field = gtfs_field

    def get_field_for_template(self) -> None:
        pass

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

    def get_configuration_form(self, request_post=None, request_files=None) -> Union[None, Dict[str, Any]]:
        my_forms = {}
        if self.my_consistency_widget.has_visual_example:
            if request_post:
                form = AddConsistencyWidgetVisualExample(request_post, request_files,
                                                         prefix="form_AddConsistencyWidgetVisualExample",
                                                         )
            else:
                form = AddConsistencyWidgetVisualExample(prefix="form_AddConsistencyWidgetVisualExample",
                                                         initial={'consistency_widget': self.my_consistency_widget})# type: ignore
            template_data = consistency_widget_visual_example.objects.filter(consistency_widget_id=self.my_consistency_widget.id)# type: ignore
            my_forms['visual_example'] = [form, template_data] # type: ignore
        if self.my_consistency_widget.has_link:
            form = AddConsistencyWidgetLink(request_post, prefix="form_AddConsistencyWidgetLink",
                                            initial={'consistency_widget': self.my_consistency_widget}) # type: ignore
            template_data = consistency_widget_link.objects.filter(consistency_widget_id=self.my_consistency_widget.id)# type: ignore
            my_forms['link'] = [form, template_data] # type: ignore
        if self.my_consistency_widget.has_other_text:
            if request_post:
                form = AddConsistencyWidgetOtherText(request_post,
                                                     prefix="form_AddConsistencyWidgetOtherText",
                                                     instance=self.my_consistency_widget)# type: ignore
            else:
                form = AddConsistencyWidgetOtherText(prefix="form_AddConsistencyWidgetOtherText",
                                                     instance=self.my_consistency_widget)# type: ignore
            my_forms['other_text'] = [form, None] # type: ignore

        if my_forms == {}:
            my_forms = None # type: ignore
        return my_forms

    def get_configuration_template(self) -> Union[None, str]:
        return 'admin/default_consistency_widget_configure.html'


def consistency_widget_factory(consistency_widget):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

    Args:
        consistency_widget: an instance of the consistency_widget model
    """

    return DefaultConsistencyWidget(consistency_widget)


class DefaultConsistencyWidget(ConsistencyWidget):

    def get_template_data(self) -> Union[None, str]:
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


    def get_configuration_form(self, request_post=None, request_files=None) -> Union[None, Dict[str, Any]]:
        """returns a django form or form factory that may be used to capture the results of a review"""
        my_forms = {}
        if self.my_results_capture_widget.has_score:
            form = AddResultCaptureScore(request_post, prefix="form_AddResultCaptureScore",
                                     initial={'results_capture_widget': self.my_results_capture_widget}) # type: ignore


            template_data = score.objects.filter(results_capture_widget_id=self.my_results_capture_widget.id)# type: ignore
            my_forms['score'] = [form, template_data] # type: ignore

        if my_forms == {}:
            my_forms = None # type: ignore
        return my_forms

    def get_configuration_template(self) -> Union[None, str]:
        return 'admin/default_result_capture_configure.html'


def results_capture_widget_factory(results_capture_widget):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

        Args:
            results_capture_widget: an instance of the results_capture_widget model
    """

    return DefaultResultsCaptureWidget(results_capture_widget)


class DefaultResultsCaptureWidget(ResultsCaptureWidget):

    def get_template(self) -> None:
        pass

    def get_template_data(self) -> Union[None, str]:
        pass



# endregion

# region DataSelector

class DataSelector(ABC):
    """DataSelector abstract class are variation of methods for selecting data from GTFS Feeds"""

    @abstractmethod
    def get_gtfs_for_review(self) -> None:
        raise NotImplementedError

# endregion