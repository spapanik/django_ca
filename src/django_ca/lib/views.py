from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from django_ca.lib.models import BaseModel


class DownloadTextFileView(View):
    model: type[BaseModel]

    def get(
        self, _request: HttpRequest, obj_id: int, field: str, filename: str
    ) -> HttpResponse:
        obj = get_object_or_404(self.model, pk=obj_id)

        response = HttpResponse(getattr(obj, field), content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={filename}"

        return response
