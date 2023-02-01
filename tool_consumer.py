from typing import Dict, Tuple
import requests
from requests import Request, PreparedRequest
from requests_oauthlib.oauth1_auth import SIGNATURE_TYPE_BODY
from requests_oauthlib import OAuth1
import urllib.parse


class LTIToolConsumer:
    """
    Wrapper class to consume an LTI 1.0 Tool from any LTI 1.0 -compliant provider.

    Example - Consume a moodle course:

    Publish your moodle course as an LTI tool (course settings -> publish as LTI tools),
    which will provide you with a Cartridge URL, a Secret, a Launch URL and a registration URL

    You'll only need the secret and the launch URL.

    Initialize this class as follows and consume the resource::

        tool_consumer = LTIToolConsumer("any_consumer_key", "<secret_from_moodle>", "<launch_url_from_moodle>")
        response = tool_consumer.launch_request()

        tool_html = response[2]

    The LTIToolConsumer expects a `consumer_key` to be specified. However, the sole purpose
    of this key is to let the provider be able to distinguish consumers and react accordingly.
    In case of Moodle, it seemingly doesn't care about who consumes the resource (as long as secret
    and signature is correct of course), so use any value you want. However, it cannot be left
    out from the request because that would break the format of an LTI Launch Request.
    """

    def __init__(
        self, consumer_key: str, consumer_secret: str, launch_url: str
    ) -> None:
        """
        Initialize the Consumer, setting the minimal required parameters for the request.

        :param consumer_key: an arbitrary key that the Tool Provider may use to distinguish
        its consumers. While a Provider might or might not need this value, it cannot be left
        out of the request as per LTI standard.
        :param consumer_secret: the secret that provider and consumer agreed upon to authenticate
        this request. Typically this value is configured by the provider when publishing an LTI tool
        and given to you as the consumer
        :param launch_url: the launch URL of the LTI tool that should be consumed. (careful: NOT a
        cartridge URL, but the actual launch URL)
        """

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.launch_url = launch_url
        self.lti_message_type = "basic-lti-launch-request"
        self.lti_version = "LTI-1p0"

    def launch_request(self, extra_params: Dict = None) -> Tuple[int, dict, str]:
        """
        Consume the LTI Tool by sending a request to the provider.
        The request is signed with a OAuth1.0 HMAC_SHA1 signature as per the LTI standard.

        Optionally, extra parameters may be specified as dict to extend the request payload further.
        By doing so, default parameter values such as e.g. `lti_message_type`, or `lti_version` may
        be overwritten.

        :param extra_params: dict containing extra key/value pairs to append to the request

        :returns: a tuple containing the relevant response information: HTTP status code,
        HTTP Response Headers, Reponse Content (LTI tool itself)
        """

        # generate request and sign it with OAuth1.0 signature
        # however we have to create a request, sign it and then decode the query parameters again
        # to prevent blank values from getting deleted and as such messing up the signature.
        # there is probably a smarter way, however this works for now
        request = self.sign_request(
            self.generate_launch_request_payload(extra_params=extra_params)
        )
        payload_body = self.parse_qs(
            request.body.decode("utf8"), keep_blank_values=True
        )

        # get LTI resource from the Tool Provider
        response = requests.post(self.launch_url, payload_body)

        # return status code, headers and parsed html content
        return (
            response.status_code,
            response.headers,
            response.content.decode("utf8").replace("\\n", ""),
        )

    def parse_qs(self, qs, keep_blank_values=False):
        """
        decode a percent-encoded query string into a dictionary of query parameters
        """

        params = urllib.parse.parse_qs(
            qs, keep_blank_values=int(keep_blank_values)
        ).items()
        return dict((k, v if len(v) > 1 else v[0]) for k, v in params)

    def generate_launch_request_payload(
        self, extra_params: Dict = None
    ) -> PreparedRequest:
        """
        Generate and prepare the request content that will be later sent to the
        tool provider to request the LTI Resource.

        Optionally, extra parameters may be specified as dict to extend the request payload further.
        By doing so, default parameter values such as e.g. `lti_message_type`, or `lti_version` may
        be overwritten.

        :param extra_params: dict containing extra key/value-pairs to extend the request

        :returns: PreparedRequest
        """

        payload = {
            "lti_message_type": self.lti_message_type,
            "lti_version": self.lti_version,
            "resource_link_id": 1,
        }

        # if present, add additional parameters to the request
        # also allowing to override the standard parameters
        if extra_params:
            payload |= extra_params

        return Request("POST", self.launch_url, data=payload).prepare()

    def sign_request(self, request: PreparedRequest) -> PreparedRequest:
        """
        Sign the given request with a OAuth1.0 HMAC-SHA1 signature

        :param request: the request to be signed

        :returns: the signed request
        """

        sign = OAuth1(
            self.consumer_key, self.consumer_secret, signature_type=SIGNATURE_TYPE_BODY
        )
        return sign(request)


if __name__ == "__main__":
    consumer_secret = "<secret_from_provider>"
    launch_url = "<launch_url_from_provider"

    response = LTIToolConsumer(
        "test", consumer_secret, launch_url
    ).launch_request()

    print(response[0])
    print(response[1])
    print(response[2])
