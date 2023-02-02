import random
import urllib.parse
import string

import tornado.web
import tornado.ioloop

CONSUMER_KEY = "test_consumer"
CONSUMER_SECRET = "blublub"
#CONSUMER_SECRET = "".join(random.choices(string.ascii_letters, k=10))

class ToolProviderHandler(tornado.web.RequestHandler):

    def get(self):
        pass

    def post(self):
        print(self.request)
        print(self.parse_qs(self.request.body.decode("utf8"), keep_blank_values=True))
        
        # verify signature:
        # 1. remove oauth stuff from request payload
        # 2. generate request base string and parameters new
        # 3. urlencode
        # 4. sign again with expected secret
        # 5. check provided signature == freshly generated signature

        self.write("<div><h1>take this awesome tool</h1></div>")

    def parse_qs(self, qs, keep_blank_values=False):
        """
        decode a percent-encoded query string into a dictionary of query parameters
        """

        params = urllib.parse.parse_qs(
            qs, keep_blank_values=int(keep_blank_values)
        ).items()
        return dict((k, v if len(v) > 1 else v[0]) for k, v in params)

def make_app():
    return tornado.web.Application([
        (r"/launch", ToolProviderHandler)
    ])

if __name__ == "__main__":
    print("Generating consumer key and secret for demo purposes...")
    print("Consumer Key: {}".format(CONSUMER_KEY))
    print("CONSUMER SECRET: {}".format(CONSUMER_SECRET))
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()