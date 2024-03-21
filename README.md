# pl-notification

`pl-notification` is a _[ChRIS plugin](https://chrisproject.org/)_ to send notifications through mail / Slack /Element.

usage: `notifcation [-t TITLE] [-c CONTENT] [-s SLACK_URL] [-e ELEMENT_ROOM] [-E ELEMENT_TOKEN] [--element-host ELEMENT_HOST] [-r RCPT] [-S SENDER] [-M MAIL_SERVER]
                    inputdir outputdir`

Alternatively, we can create a `[inputdir]/.notification.yaml` and setup the configuration.

## Abstract

Sometimes we would like to be notified in various scenarios in the ChRIS environment. Some typical scenarios are system monitoring and task monitoring.
`pl-notification` is a _[ChRIS plugin](https://chrisproject.org/)_ to send notifications through mail / Slack / Element.

## Installation

`pl-notification` is a _[ChRIS plugin](https://chrisproject.org/)_, meaning it can
run from either within _ChRIS_ or the command-line.

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/)
(a.k.a. Singularity) to run `pl-notification` as a container:

```shell
apptainer exec docker://fnndsc/pl-notification notification [--args values...] input/ output/
```

To print its available options, run:

```shell
apptainer exec docker://fnndsc/pl-notification notification --help
```

## Examples

To post some message (optionally with title) to some Slack channel:
```shell
notification -t 'the title' -c 'test from pl-notification' -s [slack-url from Slack Incoming Webhooks] inputdir outputdir
```

To post some message (optionally with title) to some Element room:
```shell
notification -t 'the title' -c 'test from pl-notification' -e [full room ID (!something:domain.tld) from Room Info -> Settings -> Advanced -> Internal room ID] -E [access token from Settings -> Help & About -> Advanced -> AccessToken] inputdir outputdir
```

To send some message with title through Email:
```shell
notification -t 'the title' -c 'test from pl-notification' -r [comma separated valid email recipent addresses] [-S [valid email sender address]] [-M [email server]] inputdir outputdir
```

Different methods can be sent simultaneously with the combined command:
```shell
notification -t 'the title' -c 'test from pl-notification' -s [slack-url] -e [room ID] -E [access token] -r [email recipents] [-S [email sender]] [-M [email server]] inputdir outputdir
```

## Development

### Building

Build a local container image:

```shell
docker build -t localhost/fnndsc/pl-notification .
```

### Running

Mount the source code `notification.py` into a container to try out changes without rebuild.

```shell
docker run --rm -it --userns=host -u $(id -u):$(id -g) \
    -v $PWD/notification.py:/usr/local/lib/python3.11/site-packages/notification.py:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-notification notification /incoming /outgoing
```

### Testing

Run unit tests using `pytest`.

## Release

Steps for release can be automated by [Github Actions](.github/workflows/ci.yml).
