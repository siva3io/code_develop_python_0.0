import json
import logging
import werkzeug.exceptions
from odoo.tools import date_utils
from odoo.http import Response, request, Root, JsonRequest
from odoo.service import security

_logger = logging.getLogger(__name__)


def get_response(self, httprequest, result, explicit_session):
    if isinstance(result, Response) and result.is_qweb:
        try:
            result.flatten()
        except Exception as e:
            if request.db:
                result = request.registry['ir.http']._handle_exception(e)
            else:
                raise

    if isinstance(result, (bytes, str)):
        response = Response(result, mimetype='text/html')
    else:
        response = result
        self.set_csp(response)

    save_session = (not request.endpoint) or request.endpoint.routing.get('save_session', True)
    if not save_session:
        return response

    if httprequest.session.should_save:
        if httprequest.session.rotate:
            self.session_store.delete(httprequest.session)
            httprequest.session.sid = self.session_store.generate_key()
            if httprequest.session.uid:
                httprequest.session.session_token = security.compute_session_token(httprequest.session, request.env)
            httprequest.session.modified = True
        self.session_store.save(httprequest.session)
    # We must not set the cookie if the session id was specified using a http header or a GET parameter.
    # There are two reasons to this:
    # - When using one of those two means we consider that we are overriding the cookie, which means creating a new
    #   session on top of an already existing session and we don't want to create a mess with the 'normal' session
    #   (the one using the cookie). That is a special feature of the Session Javascript class.
    # - It could allow session fixation attacks.
    if not explicit_session and hasattr(response, 'set_cookie'):
        if '/api/v1/web/session/authenticate' in httprequest.url:
            if response and response.data:
                data = json.loads(response.data.decode('utf-8'))
                if data.get('result'):
                    data['result']['session_id'] = httprequest.session.sid
                response = Response(json.dumps(data), mimetype='application/json')
            # ToDo: Check if domain is required for session cookie
            domain = '127.0.0.1 localhost dev.localhost'
            response.set_cookie(
                'session_id', httprequest.session.sid, max_age=90 * 24 * 60 * 60, samesite=None, secure=True)
            response.access_control_allow_credentials = True
            response.access_control_allow_origin = httprequest.headers.get('Origin', '*')
        else:
            response.set_cookie('session_id', httprequest.session.sid, max_age=90 * 24 * 60 * 60, httponly=True)

    return response


def _json_response(self, result=None, error=None):
    response = {
        'jsonrpc': '2.0',
        'id': self.jsonrequest.get('id')
    }
    if error is not None:
        response['error'] = error
    if result is not None:
        response['result'] = result

    mime = 'application/json'
    body = json.dumps(response, default=date_utils.json_default)

    return Response(
        body, status=error and error.pop('http_status', 200) or 200,
        headers=[('Content-Type', mime), ('Content-Length', len(body))]
    )


def overwrite__init__(self, *args):
    super(JsonRequest, self).__init__(*args)

    self.params = {}

    args = self.httprequest.args
    request = None
    request_id = args.get('id')

    # regular jsonrpc2
    request = self.httprequest.get_data().decode(self.httprequest.charset)
    # for handling get jsonrpc2 requests with empty body
    if not request:
        request = '{"jsonrpc":"2.0"}'

    # Read POST content or POST Form Data named "request"
    try:
        self.jsonrequest = json.loads(request)
    except ValueError:
        msg = 'Invalid JSON data: %r' % (request,)
        _logger.info('%s: %s', self.httprequest.path, msg)
        raise werkzeug.exceptions.BadRequest(msg)

    self.params = dict(self.jsonrequest.get("params", {}))
    self.context = self.params.pop('context', dict(self.session.context))


Root.get_response = get_response
JsonRequest._json_response = _json_response
JsonRequest.__init__ = overwrite__init__
