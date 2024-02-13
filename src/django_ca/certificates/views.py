from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.mixins import AccessMixin
from django.views.generic import TemplateView

from django_ca.certificates.models import Certificate, Key, Server
from django_ca.lib.views import DownloadTextFileView

if TYPE_CHECKING:
    from django_ca.certificates.types import ServerInfo
    from django_ca.lib.types import JSONDict


class CertificateHomeView(TemplateView):
    template_name = "certificates/base.html"


class UserServerView(AccessMixin, TemplateView):
    template_name = "certificates/certificates.html"

    def get_context_data(self, **kwargs: object) -> JSONDict:
        context = super().get_context_data(**kwargs)
        context["ca_cert_id"] = Certificate.objects.get(server__user__is_ca=True).id

        servers_info: dict[tuple[int, int], ServerInfo] = {}
        for server in Server.objects.filter(user=self.request.user).values(
            "alternative_names__name", "key__id", "certificate__id"
        ):
            key = (server["key__id"], server["certificate__id"])
            servers_info.setdefault(
                key,
                {"names": [], "count": 0},
            )
            servers_info[key]["count"] += 1
            servers_info[key]["names"].append(server["alternative_names__name"])
        variations = max((info["count"] for info in servers_info.values()), default=0)
        context["range"] = list(range(variations))
        context["servers"] = [
            {
                "key_id": key_id,
                "cert_id": cert_id,
                "names": [
                    self._get_names(info["names"], index) for index in range(variations)
                ],
            }
            for (key_id, cert_id), info in servers_info.items()
        ]
        return context

    @staticmethod
    def _get_names(names: list[str], index: int) -> str:
        try:
            return names[index]
        except IndexError:
            return "N/A"


class DownloadCertificateView(DownloadTextFileView):
    model = Certificate


class DownloadKeyView(DownloadTextFileView):
    model = Key
