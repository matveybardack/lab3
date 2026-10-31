from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("add/", views.AddRecipeView.as_view(), name="add_recipe"),
    path("generate/", views.GenerateView.as_view(), name="generate"),
    path("delete/<int:pk>/", views.DeleteRecipeView.as_view(), name="delete_recipe"),
    path("api/activity/", views.ActivityStatsView.as_view(), name="activity_stats"),
    path("exit/", views.ExitView.as_view(), name="exit"),
]
