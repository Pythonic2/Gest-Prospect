from django.urls import path

from . import views


app_name = "prospects"

urlpatterns = [
    path("", views.prospect_list, name="list"),
    path("importar/", views.import_prospects, name="import"),
    path("<int:pk>/status/", views.update_status, name="update_status"),
    path("<int:pk>/whatsapp/", views.open_whatsapp, name="open_whatsapp"),
]
