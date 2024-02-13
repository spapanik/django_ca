from django.urls import path

from django_ca.certificates import views

app_name = "certificates"
urlpatterns = [
    path("", views.CertificateHomeView.as_view(), name="home"),
    path("server/", views.UserServerView.as_view(), name="server"),
    path(
        "key/<int:obj_id>/<field>/<filename>/",
        views.DownloadKeyView.as_view(),
        name="key",
    ),
    path(
        "certificate/<int:obj_id>/<str:field>/<str:filename>/",
        views.DownloadCertificateView.as_view(),
        name="certificate",
    ),
]
