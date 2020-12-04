from abc import ABC, abstractmethod, ABCMeta
# from django.core.files import File
from typing import final, Type

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
# A review of an individual field will use the concrete implementations of each of these widgets for example:
#   - A field may need to be reviewed log10(n) times, have related data in the same table that needs to be displayed,
#     a link to a best practice, and need a screen shot from a website that is captured during the review.
#   - Another field might need to be reviewed 5 times, only display itself, have vissual examples, and capture only a
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

# region ReviewWidget

class ReviewWidget(ABC):
    """A ReviewWidget presents all data from a GTFS feed a user needs to complete their review."""

    @abstractmethod
    def get_template_data(self) -> None:
        """returns data needed for django template to display this class"""
        raise NotImplementedError

    @abstractmethod
    def get_template(self) -> None:
        """returns django template to display this class"""
        raise NotImplementedError


def review_widget_factory(review_widget) -> ReviewWidget:
    """This factory produces the appropriate ReviewWidget based on the configuration data stored in the review widget table

    Args:
        review_widget: an instance of the review widget model
    """

    if not review_widget.has_related_field_same_table and not review_widget.has_related_field_other_table:
        return SingleFieldReviewWidget()
    else:
        raise NotImplementedError


class SingleFieldReviewWidget(ReviewWidget):
    """This class produces a review widget that only displays the field"""

    def get_template_data(self) -> None:
        pass

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


class ConsistencyWidget(ABC):
    """A consistency widget contains information, not related to the GTFS Feed that may be helpful to the reviewer
    as they complete their review.  It could include things like links, examples, or images."""

    @abstractmethod
    def get_template_data(self) -> None:
        """returns data needed for django template to display this class"""
        raise NotImplementedError

    @abstractmethod
    def get_template(self) -> None:
        """returns django template to display this class"""
        raise NotImplementedError


def consistency_widget_factory(consistency_widget):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

    Args:
        consistency_widget: an instance of the consistency_widget model
    """


    return DefaultConsistencyWidget(consistency_widget)


class DefaultConsistencyWidget(ConsistencyWidget):

    def __init__(self, consistency_widget):
        self.consistency_widget = consistency_widget

    def get_template_data(self) -> None:
        pass

    def get_template(self) -> None:
        pass

# endregion

# region ResultsCaptureWidget
class ResultsCaptureWidget(ABC):
    """A results capture widget contains information and methods to record the results of a review"""

    @abstractmethod
    def get_result_capture_form(self) -> None:
        """returns a django form or form factory that may be used to capture the results of a review"""
        raise NotImplementedError

    @abstractmethod
    def get_result_capture_template(self) -> None:
        """Returns a template that may be used to display the form generated by get_result_capture_form"""
        raise NotImplementedError


def results_capture_widget_factory(results_capture_widget):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

        Args:
            results_capture_widget: an instance of the results_capture_widget model
    """

    return DefaultResultsCaptureWidget(results_capture_widget)


class DefaultResultsCaptureWidget(ResultsCaptureWidget):

    def __init__(self, results_capture_widget):
        self.results_capture_widget = results_capture_widget

    def get_result_capture_form(self) -> None:
        pass

    def get_result_capture_template(self) -> None:
        pass


# endregion

# region DataSelector

class DataSelector(ABC):
    """DataSelector abstract class are variation of methods for selecting data from GTFS Feeds"""

    @abstractmethod
    def get_gtfs_for_review(self) -> None:
        raise NotImplementedError

# endregion