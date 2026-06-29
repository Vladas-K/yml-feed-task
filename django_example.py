# views.py

from datetime import datetime

from django.http import HttpResponse

from feed_task import (
    build_yml,
    PRODUCTS,
    CATEGORIES,
)


def yml_feed(request):
    xml = build_yml(
        PRODUCTS,
        CATEGORIES,
        datetime.now(),
    )

    return HttpResponse(
        xml,
        content_type="application/xml; charset=utf-8",
    )


# urls.py

from django.urls import path


urlpatterns = [
    path("yml/", yml_feed, name="yml_feed"),
]
