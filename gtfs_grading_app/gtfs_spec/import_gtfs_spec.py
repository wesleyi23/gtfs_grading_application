#####
# This file contains a script that takes a Frictionless data standard version of the GTFS spec and transforms it into
# a python object, strings that may be used to produce cascading dropdowns shown in templates, or other structures that
# may be needed in the application.
#
# GTFS-Spec updated: 12/14/2020
#####

import json

from django.http import Http404

from gtfs_grading import settings


def load_data_package(path):
    with open(path, encoding='utf8') as f:
        gtfs_spec = json.load(f)
    return gtfs_spec


def get_cascading_drop_down(gtfs_spec=None):
    """returns a dictionary in the appropriate format for cascading dropdowns to select fields from tables"""
    if not gtfs_spec:
        gtfs_spec = settings.GTFS_SPEC
    gtfs_dict = {}
    for i in gtfs_spec['resources']:
        field_list = []
        for j in i['schema']['fields']:
            field_list.append(j['name'])
        gtfs_dict[i['name']] = field_list
    return gtfs_dict


def get_gtfs_table_tuple(gtfs_spec=None):
    """returns a tuple of GTFS tables in the GTFS Spec"""
    if not gtfs_spec:
        gtfs_spec = settings.GTFS_SPEC
    choice_tuple = (('',''),)
    for t in gtfs_spec['resources']:
        choice_tuple = choice_tuple + ((t['name'], t['name']),)
    return choice_tuple


def get_gtfs_field_tuple_from_table(table_name, gtfs_spec=None):
    """returns a tuple of GTFS fields in a specific table"""
    if not gtfs_spec:
        gtfs_spec = settings.GTFS_SPEC
    choice_tuple = choice_tuple = (('',''),)
    for t in gtfs_spec['resources']:
        if t['name'] == table_name:
            for f in t['schema']['fields']:
                choice_tuple = choice_tuple + ((f['name'], f['name']),)
            return choice_tuple
    raise ValueError("Table name not found in GTFS spec.")


def get_field_type(field, table):
    """returns the GTFS field type of the given field in a given table"""
    for i in settings.GTFS_SPEC['resources']:
        print(i['name'])
        if i['name'] == table:
            for j in i['schema']['fields']:
                print(j['name'])
                if j['name'] == field:
                    return j['gtfs_type']
    raise ValueError("Field not found in GTFS spec.")



