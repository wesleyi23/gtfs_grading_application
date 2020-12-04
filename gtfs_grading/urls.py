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
from gtfs_grading_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', name='home', view=views.home),
    path('post_gtfs_zip/', name='post_gtfs', view=views.post_gtfs_zip),
    path('gtfs_admin/', name='admin', view=views.gtfs_admin),
    path('gtfs_admin/view_review_category/', name="view_review_category", view=views.ViewReviewCategory.as_view()),
    path('gtfs_admin/add_review_category/', name="add_review_category", view=views.add_review_category),
    path('gtfs_admin/view_review_widget/<int:pk>/', views.ViewReviewWidget.as_view(), name='view_review_widget'),
]
