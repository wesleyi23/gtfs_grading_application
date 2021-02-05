from django.urls import reverse

from gtfs_grading_app.models import result


def list_to_tuple_of_tuples(list):
    output = ((list[0], list[0]), )
    for i in range(1, len(list)):
        output = output + ((list[i], list[i]),)
    return output


def get_next_review_item(active_result_number, max_items, active_review, active_review_category, review_categories):
    if active_result_number < max_items:
        return reverse('evaluate_feed',
                       kwargs={
                           'review_id': active_review.id,
                           'active_review_category_id': active_review_category.id,
                           'active_result_number': active_result_number + 1}
                       )
    else:
        item_found = False
        for cat in review_categories:
            if item_found:
                return reverse('evaluate_feed',
                               kwargs={
                                   'review_id': active_review.id,
                                   'active_review_category_id': cat.id,
                                   'active_result_number': 1}
                               )

            if active_review_category.id == cat.id:
                item_found = True
        return None


def get_previous_review_item(active_result_number, max_items, active_review, active_review_category, review_categories):
    if active_result_number > 1:
        return reverse('evaluate_feed',
                       kwargs={
                           'review_id': active_review.id,
                           'active_review_category_id': active_review_category.id,
                           'active_result_number': active_result_number - 1}
                       )
    else:
        item_found = False
        for cat in review_categories.order_by('-id'):
            if item_found:
                max_items = result.objects.filter(review_id=active_review.id, review_category_id=cat.id).count()
                return reverse('evaluate_feed',
                               kwargs={
                                   'review_id': active_review.id,
                                   'active_review_category_id': cat.id,
                                   'active_result_number': max_items}
                               )
            if active_review_category == cat:
                item_found = True
        return None


def get_or_none(class_model, **kwargs):
    try:
        return class_model.objects.get(**kwargs)
    except class_model.DoesNotExist:
        return None



