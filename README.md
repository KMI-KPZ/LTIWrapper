# Python Wrapper for LTI 1.0

Python Wrapper classes to consume and provide LTI 1.0 Tools.

The consumer is a simple script that runs once and ends after consumption of the tool from the provider.

The Tool Provider on the other hand is a Tornado Server that hosts a simple demo tool.

## Requirements
- requests
- requests-oauthlib
- tornado

## Usage
(in-depth examples and explanations are in the corresponding scripts)

### Tool Consumer
fill in the values for consumer_key, consumer_secret and launch_url at the bottom of the script as stated by your tool provider (e.g. Moodle) and run the script to see the response from the provider.

### Tool Provider
Spin up the Tornado server by starting the script and supply the consumer key and secret to your Consumer (e.g. Moodle, or you might as well test it with this ToolConsumer). Launch the tool by whatever functionality your Consumer provides (e.g. open the activity in the Moodle course).