import random
from requests import Request
from requests_oauthlib.oauth1_auth import SIGNATURE_TYPE_BODY
from requests_oauthlib import OAuth1
import oauthlib.common
import urllib.parse
import string

import tornado.web
import tornado.ioloop

# technically, every client (i.e. consumer) should have and individual key
# and to those keys an individual secret should be associated.
# that way you can validate who the consumer really is and e.g. perform
# an automated login on our provider side.
# however, for simplicity of this example, every consumer uses the same secret which
# is randomly generated each time the script runs, rendering the consumer_key actually useless, 
# but it has to be present in the request as per the LTI standard
CONSUMER_KEY = "test_consumer"
CONSUMER_SECRET = "".join(random.choices(string.ascii_letters, k=10))


class ToolProviderHandler(tornado.web.RequestHandler):
    """
    Example implementation of an LTI1.0 Tool Provider that sends out a
    tool (here html string) that can be used by any LTI-compliant consumer that
    has a valid Consumer Secret.

    Example - Integrate this tool in a Moodle Course:

    Start this Tornado Server from the command line by simply running the script::

        python3 tool_provider.py

    It will output a Consumer Key and a Consumer Secret.

    Head over to your moodle course, add a new activity, and choose "External Tool"
    from the selection.
    Configure it as follows:
    - set any name you want for the activity
    - Hit "show more..", put the Consumer Key into the field called "Consumer key"
      and the Consumer Secret into "Shared secret"
    - set the "Tool URL" to: http://localhost:13000/launch
    - hit "Save and Display" to finish

    If everything went right, the activity should render "take this awesome tool" in bold text,
    which is obviously not a full tool, but serves its purpose for this demo. A real tool can be
    virtually anything, because moodle renders it inside an iframe, allowing it to basically be a
    full-on website.
    """

    def get(self):
        self.write("Launch requests should be a POST request!")

    def post(self):
        """
        Processes an incoming launch request. In order to be eligible to receive the tool,
        the OAuth1.0 signature must be valid. If not, a HTTP Status of 401 Unauthorized is
        sent back.
        If the signature verifies, i.e. the correct secret has been used by the consumer and
        the message was not modified after signing it, therefore access will be granted.
        """

        # first, decode the url-encoded query string in the body to a dict
        # and save the signature to compare against later
        data = self.parse_qs(self.request.body.decode("utf8"), keep_blank_values=True)
        signature = data["oauth_signature"]

        # the oauth1.0 signature has to be verified, as per the standard,
        # this is done by rebuilding the request, signing it again and
        # checking if the signatures match:

        # 1. delete the to-be-verified signature from the data, since the signature itself
        # cannot be signed (obviously)
        del data["oauth_signature"]

        # 2. transform the data into a url-encoded request (rebuild request)
        # we have to create a full ready-to-send request again just as it was sent to this endpoint,
        # because the base string (method, url, ...) is signed as well
        data_as_request = Request("POST", self.request.full_url(), data=data).prepare()

        # 3. sign the request again
        # since requests and oauthlib's Request classes are not interchangeable (why should...),
        # we gotta transform the request to a representation that oauthlib understands.
        # secondly, we cannot simply use the lib's sign method, because it would generate all
        # the oauth parameters, which we obviously don't want, because we have those parameters.
        # so we hack the lib a little bit and just sign our data with the parameters that we have
        sign = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_type=SIGNATURE_TYPE_BODY)
        new_signature = sign.client.get_oauth_signature(
            oauthlib.common.Request(
                data_as_request.url,
                data_as_request.method,
                data_as_request.body,
                data_as_request.headers,
                "utf-8",
            )
        )

        # 4. verify the signature
        # if the supplied one matches the one we just computed again,
        # access will be granted, i.e. send the tool to the consumer
        # and do anything else  you want in a successful case
        if signature == new_signature:
            print("Signature validated, sending tool to embed")
            self.write("<div><h1>take this awesome tool</h1></div>")

        # the signatures don't match, so the supplied signature is invalid, respond
        # with 401 Unauthorized
        else:
            print("Signature didn't validate, sending 401 Unauthorized response")
            self.set_status(401)
            self.write({"reason": "invalid_signature"})

    def parse_qs(self, qs, keep_blank_values=False):
        """
        decode a percent-encoded query string into a dictionary of query parameters
        """

        params = urllib.parse.parse_qs(
            qs, keep_blank_values=int(keep_blank_values)
        ).items()
        return dict((k, v if len(v) > 1 else v[0]) for k, v in params)


def make_app():
    """
    build the tornado application by mapping routes/endpoints to handlers
    """

    return tornado.web.Application([(r"/launch", ToolProviderHandler)])


if __name__ == "__main__":
    print("Starting on port 13000")
    print("Generating consumer key and secret for demo purposes...")
    print("Consumer Key: {}".format(CONSUMER_KEY))
    print("CONSUMER SECRET: {}".format(CONSUMER_SECRET))
    
    # spin up the tornado server
    app = make_app()
    app.listen(13000)
    tornado.ioloop.IOLoop.current().start()
