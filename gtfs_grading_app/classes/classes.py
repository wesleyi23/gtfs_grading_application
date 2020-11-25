from abc import ABC, abstractmethod, ABCMeta
# from django.core.files import File
from typing import final

####
# This file contains classes used in this application.
#
# For each abstract class in this file there is a region below which contains:
#   - A factory to generate the appropriate concrete class
#   - Any classes derived from the abstract class
#
#####

#region AbstractClasses

# # Replaced by Partridge
# class GtfsFeed(ABC):
#     """GtfsFeed is an abstract class and/or interface working classes GTFS data and
#
#     It contains an interface for multiple methods of getting gtfs data which are parsed using the
#     parse_gtfs_method.  Regardless of how GTFS data is parsed it should be in a consistent format
#     so the interface methods in this abstract class can function.
#     """
#
#     @final
#     def get_list_of_tables(self) -> None:
#         """Returns a list of tables in the GTFS feed"""
#         print("get_list_of_tables NotImplemented")
#         raise NotImplementedError
#
#     @final
#     def get_table(self, table_name) -> None:
#         """Gets a table by the provided table name"""
#         print("get_table NotImplemented")
#         raise NotImplementedError
#
#
#
#     @final
#     def get_row_by_table_and_index(self, table_name, row_index) -> None:
#         """Gets a row of data by the table name and index."""
#         print("get_row_by_table_and_index NotImplemented")
#         # raise NotImplementedError
#
#     @abstractmethod
#     def parse_gtfs(self) -> None:
#         # if file:
#         #   one class
#         # if url:
#         #   another class
#         raise NotImplementedError


class ReviewWidget(ABC):
    """A ReviewWidget presents all data a user needs from a GTFS feed to complete their review.

    Attributes:
        review_field_id: the review field that is the subject of the review
        related_field_same_table_ids: A list of lists of GtfsField ids from the same table as the review field
        related_field_other_table: a text description of the appropriate function to use to pull related fields in other tables
    """

    def __init__(self, review_field_id, related_field_same_table_ids=None, related_field_other_table=None):
        self.review_field_id = review_field_id
        self.related_field_same_table_ids = related_field_same_table_ids
        self.related_field_other_table = related_field_other_table

    @abstractmethod
    def get_template_data(self) -> None:
        """returns data needed for django template to display this class"""
        raise NotImplementedError

    @abstractmethod
    def get_template(self) -> None:
        """returns django template to display this class"""
        raise NotImplementedError


class ReviewField(ABC):
    """A ReviewField has all of the information about a field in a GTFS feed that is needed to display the field to the user

    Attributes:
        name: the name of the field
        table: the name of the table the field is found in
        field_type: the type of the field for example: text, int, color, url, ext
        description: the description of the field that is subject to review
        enum: an enumeration of the possible values of a field or None if their are many possible values
        value: the actual value of the field that is displayed to the user
    """
    def __init__(self, name, table, field_type, description, enum, value):
        self.name = name
        self.table = table
        self.field_type = field_type
        self.description = description
        self.enum = enum
        self.value = value

    @abstractmethod
    def get_field_for_template(self) -> None:
        """returns HTML for use in a template"""
        raise NotImplementedError


class ConsistencyWidget(ABC):
    """A consistency widget contains information that may be helpful to the reviewer as they complete their review

    Attributes:
        visual_examples: list of Base64 encoded images to be displayed in the ConsistencyWidget
        link_urls: list of links to information
        link_text: list of link text to display for URLs
        link_descriptions: list of text to describe links
        other_text: List of other text descriptions
        consistency_template: the location of the template to use for the widget
    """

    def __init__(self, visual_examples, link_urls, link_text, link_descriptions, other_text, consistency_template):
        self.visual_examples = visual_examples
        self.link_urls = link_urls
        self.link_text = link_text
        self.link_descriptions = link_descriptions
        self.other_text = other_text
        self.consistency_template = consistency_template


    @abstractmethod
    def get_template_data(self) -> None:
        """returns data needed for django template to display this class"""
        raise NotImplementedError

    @abstractmethod
    def get_template(self) -> None:
        """returns django template to display this class"""
        raise NotImplementedError


class ResultsCaptureWidget(ABC):
    """A results capture widget contains information and methods to the results of a review

    Attributes:
        possible_scores: list of lists of possible scores
        score_help_text: list score help text
    """

    def __init__(self, possible_scores, score_help_text):
        self.possible_scores = possible_scores
        self.score_help_text = score_help_text


    @abstractmethod
    def get_result_capture_form(self) -> None:
        """returns a django form or form factory that may be used to capture the results of a review"""
        raise NotImplementedError

    @abstractmethod
    def get_result_capture_template(self) -> None:
        """Returns a template that may be used to display the form generated by get_result_capture_form"""
        raise NotImplementedError


class DataSelector(ABC):
    """DataSelector abstract class - for selecting data from GtfsFeeds"""

    @abstractmethod
    def get_gtfs_for_review(self) -> None:
        raise NotImplementedError

#endregion


#region ConcreteClasses


#region GtfsFeed

# # replaced by Partridge
# class GtfsUrlParser(GtfsFeed):
#
#     def parse_gtfs(self) -> None:
#         pass
#
# class GtfsFileParser(GtfsFeed):
#
#     def parse_gtfs(self) -> None:
#         pass


#endregion


#region ReviewWidget

def review_widget_factory(review_field_id, related_field_same_table_ids=None, related_field_other_table=None):
    """This factory produces the appropriate ReviewWidget based on the configuration data provided

    Attributes:
        review_field_id: the review field that is the subject of the review
        related_field_same_table_ids: A list of lists of GtfsField ids from the same table as the review field
        related_field_other_table: a text description of the appropriate function to use to pull related fields in other tables
    """

    if not related_field_same_table_ids and not related_field_other_table:
        return SingleFieldReviewWidget(review_field_id)


class SingleFieldReviewWidget(ReviewWidget):

    def get_template_data(self) -> None:
        pass

    def get_template(self) -> None:
        pass


#endregion


#region ReviewField


#endregion


#region ConsistencyWidget


#endregion


#region ResultsCaptureWidget


#endregion


#region DataSelector


#endregion

#endregion


