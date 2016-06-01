import flickr_api
import os
import cStringIO
import requests
import random
from flask import Flask
from flask import jsonify
from flask import abort
from flask import make_response
from flask import send_file
from flickr_api import Walker
from flickr_api import Photo
from bson import Binary

app = Flask(__name__)

debug = False


def dpr(s):
    if(debug):
        print s


try:
    api_key = os.environ['FLICKR_API_KEY']
    api_secret = os.environ['FLICKR_API_SECRET']
except KeyError as KE:
    dpr("Bailing out: environment variable missing: {}".format(KE))
    exit(1)


def search_flickr_for_images(text):
    flickr_api.set_keys(api_key=api_key, api_secret=api_secret)
    photos = []
    try:
        photo_search = Walker(Photo.search, text=text)
    except Exception as e:
        dpr(e)
        abort(503)
    for photo in photo_search[:16]:
        url = photo.getSizes()["Medium"]["source"]
        photos.append({
            "url": url,
            "title": photo.title.encode('ascii', 'replace'),
            "id": photo.id,
            })
    return photos


def display_image(url):
    print "url: {}".format(url)
    r = requests.get(url, stream=True)
    r.raw.decode_content = True
    data = Binary(r.raw.read())
    img_io = cStringIO.StringIO()
    img_io.write(data)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@app.errorhandler(404)
def not_found(error):
    dpr(error)
    return make_response(jsonify({'error': '404: not found'}), 404)


@app.errorhandler(400)
def bad_request_400(error):
    dpr(error)

    return make_response(jsonify({'error': '400: bad request'}), 400)


@app.errorhandler(409)
def bad_request_409(error):
    dpr(error)
    return make_response(jsonify({'error': '409: duplicate resource id'}), 409)


@app.errorhandler(500)
def internal_server_error(error):
    dpr(error)
    return make_response(jsonify({'error': '500: internal server error'}), 500)


@app.errorhandler(501)
def not_implemented(error):
    dpr(error)
    return make_response(jsonify(
        {'error': '501: HTTP request not understood in this context'}), 501)


@app.errorhandler(502)
def bad_gateway(error):
    dpr(error)
    return make_response(jsonify(
        {'error': '502: server received an invalid response from an upstream server'}), 502)


@app.errorhandler(503)
def service_unavailable(error):
    dpr(error)
    return make_response(jsonify({'error': '503: service unavailable - try back later'}), 503)


@app.errorhandler(504)
def gateway_timeout(error):
    dpr(error)
    return make_response(jsonify({'error': '504: upstream timeout - the server stopped waiting for a response from upstream'}), 504)


@app.route('/search/<string:text>', methods=['GET'])
def search(text):
    results = search_flickr_for_images(text)
    if len(results) != 0:
        return jsonify({'results': [result for result in results]})
    else:
        abort(404)


@app.route('/random/<string:text>', methods=['GET'])
def get_random(text):
    print "Getting results"
    results = search_flickr_for_images(text)
    print "Got results"
    result = random.choice(results)
    print "Randomly chose {}".format(result)
    if len(results) != 0:
        return display_image(result["url"])
    else:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=8008, host='0.0.0.0')
