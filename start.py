#! /usr/bin/python3

import sys
from app import app
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix

debug_mode = (len(sys.argv) >= 2 and sys.argv[1] == '--debug')

if not debug_mode:
	from wsgi_door.providers import init_providers
	from wsgi_door.middleware import WsgiDoorAuth, WsgiDoorFilter
	app.wsgi_app = WsgiDoorFilter(app.wsgi_app, protected_paths=["/"], allowed_groups=app.config['ALLOWED_GROUPS'])
	app.wsgi_app = WsgiDoorAuth(app.wsgi_app, init_providers(app.config['AUTH_CLIENT_KEYS']), app.config['SECRET_KEY'])

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_for=1)
run_simple('0.0.0.0', 5000, app, threaded=True)
