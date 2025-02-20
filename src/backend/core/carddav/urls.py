from django.urls import re_path, path
from .views import RadicaleWrapperView, WellKnownView

urlpatterns = [
    path('.well-known/carddav', WellKnownView.as_view(), name='well-known-carddav'),
    path('carddav/', RadicaleWrapperView.as_view(), name='carddav-root'),
    re_path(r'^carddav/(?P<path>.*)$', RadicaleWrapperView.as_view(), name='carddav'),
]