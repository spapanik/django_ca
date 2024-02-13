from django.urls import include, path

urlpatterns = [
    path("api/accounts/", include("django.contrib.auth.urls")),
    path(
        "api/certificates/",
        include("django_ca.certificates.urls", namespace="certificates"),
    ),
]
