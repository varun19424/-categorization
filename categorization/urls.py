from django.urls import path

from categorization.views import CategorizationSuggestView, HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("categorize/", CategorizationSuggestView.as_view(), name="categorize"),
    path("categorizations/suggest/", CategorizationSuggestView.as_view(), name="categorization-suggest"),
]
