import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from radicale import Application
from radicale.config import Configuration, DEFAULT_CONFIG_SCHEMA
from radicale.log import set_level as set_log_level

CARDDAV_URL = "carddav"


def load_radicale_config():
    config = {
        # 'server': {
        #     'hosts': getattr(settings, 'RADICALE_HOSTS', ['0.0.0.0:5232']),
        #     'max_connections': getattr(settings, 'RADICALE_MAX_CONNECTIONS', '20'),
        #     'max_content_length': getattr(settings, 'RADICALE_MAX_CONTENT_LENGTH', '100000000'),
        # },
        'storage': {
            'type': 'core.carddav.storage',
        },
        'auth': {
            'type': 'core.carddav.auth',
        },
        'rights': {
            'type': 'core.carddav.rights',
        },
        # 'web': {
        #     'type': 'none',  # Disable built-in web interface
        # },
        "logging": {
            "request_content_on_debug": True,
            "response_content_on_debug": True,
            "bad_put_request_content": True,
            "request_header_on_debug": False,

        },
    }

    configuration = Configuration(DEFAULT_CONFIG_SCHEMA)
    configuration.update(config)

    return configuration

# Load Radicale configuration from Django settings
config = load_radicale_config()

# Initialize Radicale application
application = Application(config)


class RadicaleWrapperView(View):
    http_method_names = [
        'delete',
        'get',
        'head',
        'mkcalendar',
        'mkcol',
        'move',
        'options',
        'propfind',
        'proppatch',
        'put',
        'report',
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._radicale_application = Application(config)
        self._response = None

    def start_response(self, status_text, headers):
        status_code, _ = status_text.split(' ', 1)
        self._response = HttpResponse(status=status_code, headers=headers)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.method.lower() in self.http_method_names:
            return self.http_method_not_allowed(request, *args, **kwargs)

        path = request.META['PATH_INFO']
        carddav_prefix = f"/{CARDDAV_URL}/"

        if path.startswith(carddav_prefix):
            # cut known prefix from path (PATH_INFO) and
            # move it into the base prefix (HTTP_X_SCRIPT_NAME)
            request.META['PATH_INFO'] = path[len(carddav_prefix):]
            request.META['HTTP_X_SCRIPT_NAME'] = carddav_prefix.rstrip('/')

        answer = self._radicale_application(request.META, self.start_response)
        self._response.content = answer

        return self._response



class WellKnownView(RedirectView):
    def get_redirect_url(self):
        return self.request.build_absolute_uri(f"/{CARDDAV_URL}/")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
