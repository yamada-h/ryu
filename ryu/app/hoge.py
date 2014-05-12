import itertools
import json
from webob import Response

from ryu.app.wsgi import route, ControllerBase, WSGIApplication
from ryu.base import app_manager
from ryu.lib import hub
from ryu.contrib._eventlet import websocket


class HogeController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(HogeController, self).__init__(req, link, data, **config)
        self._counter = data['counter']

    @route('hoge', '/hoge', methods=['GET'])
    def hoge(self, req, **kwargs):
        body = json.dumps({'hoge': self._counter.next()})
        return Response(content_type='application/json', body=body)

    @websocket.WebSocketWSGI
    def _ws_handler(self, ws):
        for i in self._counter:
            data = {
                'count': i,
            }
            ws.send(unicode(json.dumps(data)))
            hub.sleep(1)

    @route('hoge', '/hoge/ws')
    def websocket(self, req, **kwargs):
        return self._ws_handler(req.environ, req.start_response)


class HogeApp(app_manager.RyuApp):
    _CONTEXTS = {
        'wsgi': WSGIApplication,
    }

    def __init__(self, *args, **kwargs):
        super(HogeApp, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(
            HogeController,
            data={
                'counter': itertools.count(),
            },
        )
