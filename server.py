# -*- coding: utf-8 -*-

import flask
import requests
import pickle

from time import time
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

app = flask.Flask(__name__)
#cache.init_app(app)
new_dict = dict()
method_requests_mapping = {
    'GET': requests.get,
    'HEAD': requests.head,
    'POST': requests.post,
    'PUT': requests.put,
    'DELETE': requests.delete,
    'PATCH': requests.patch,
    'OPTIONS': requests.options,
}


def read_or_new_pickle(path, default):
    try:
        foo = pickle.load(open(path, "rb"))
    except StandardError:
        foo = default
        pickle.dump(foo, open(path, "wb"))
    return foo


@app.route('/<path:url>', methods=method_requests_mapping.keys())
def proxy(url):
    global new_dict
    #print(new_dict)
    parameter_hash = str(hash(frozenset(flask.request.args.items())));
    key = url+parameter_hash
    if(new_dict and parameter_hash in new_dict and int(new_dict[url][0]) > time()):
        print("cached")
        print(new_dict[parameter_hash][0])
        print(url)
        print(time())
        resp = flask.Response(new_dict[parameter_hash][1])
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    requests_function = method_requests_mapping[flask.request.method]
    request = requests_function(url, stream=True, params=flask.request.args)
    response = flask.Response(flask.stream_with_context(request.iter_content()),
                              content_type=request.headers['content-type'],
                              status=request.status_code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    new_dict[url]=[int(time())+5,response.data]
    print("new" + str(response))
    return response


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port="5001")