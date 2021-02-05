"""gtfs_grading URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from gtfs_grading import settings
from gtfs_grading_app import views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', name='home', view=views.home),
    path('home/', name='new_home', view=views.new_home),
    path('administration/', name='administration', view=views.administration),
    path('administration/add_new', name='admin_add_new', view=views.amdin_add_new),
    path('administration/details/<int:review_id>', name='admin_details', view=views.admin_details),
    path('about/', name='about', view=views.about),
    path('post_gtfs_zip/', name='post_gtfs', view=views.post_gtfs_zip),
    path('gtfs_admin/', name='admin', view=views.gtfs_admin),
    path('gtfs_admin/view_review_category/', name="view_review_category", view=views.ViewReviewCategory.as_view()),
    path('gtfs_admin/view_review_widget/<int:pk>/', views.ViewReviewWidget.as_view(), name='view_review_widget'),
    path('gtfs_admin/add_review_category/', name="add_review_category", view=views.add_review_category),
    path('gtfs_admin/delete_review_category/<int:review_category_id>/', name="delete_review_category", view=views.delete_review_category),
    path('gtfs_admin/configure_widget/main_page/<str:widget_type>/<int:widget_id>/', name="configure_widget", view=views.configure_widget),
    path('gtfs_admin/configure_widget/delete_consistency_widget_visual_example/<int:image_id>/', name="delete_consistency_widget_visual_example", view=views.delete_consistency_widget_visual_example),
    path('gtfs_admin/configure_widget/delete_consistency_widget_link/<int:link_id>/', name="delete_consistency_widget_link", view=views.delete_consistency_widget_link),
    path('gtfs_admin/configure_widget/delete_review_widget_related_field_same_table/<int:widget_id>/<int:field_id>/', name="delete_review_widget_related_field_same_table", view=views.delete_review_widget_related_field_same_table),
    path('gtfs_admin/configure_widget/delete_results_capture_score/<int:score_id>/', name="delete_results_capture_score", view=views.delete_results_capture_score),
    path('start_new_evaluation/', name='start_new_evaluation', view=views.start_new_evaluation),
    # path('start_new_evaluation/<str:new_file>', name='start_new_evaluation_new_file', view=views.start_new_evaluation),
    path('evaluate_feed/', name='evaluate_feed', view=views.evaluate_feed),
    path('evaluate_feed/<int:review_id>/', name='evaluate_feed', view=views.evaluate_feed),
    path('evaluate_feed/<int:review_id>/<int:active_review_category_id>/', name='evaluate_feed', view=views.evaluate_feed),
    path('evaluate_feed/<int:review_id>/<int:active_review_category_id>/<int:active_result_number>', name='evaluate_feed', view=views.evaluate_feed),
    path('review/<int:review_id>/', name='review_evaluation_results', view=views.review_evaluation_results),
    path('review/<int:review_id>/<int:active_result_id>/', name='review_evaluation_results', view=views.review_evaluation_results),
    path('mark_review_complete/<int:review_id>/', name='mark_review_complete', view=views.mark_review_complete),
    path('search_competed_review/', name='search_competed_review', view=views.search_competed_review),
    path('view_completed_review/<int:review_id>/', name='view_completed_review', view=views.view_completed_review),
    path('view_completed_review/<int:review_id>/<int:active_result_id>/', name='view_completed_review', view=views.view_completed_review)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)