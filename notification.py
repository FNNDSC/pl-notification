#!/usr/bin/env python

from pathlib import Path
from argparse import ArgumentParser, Namespace

import os
import os.path

import yaml
import json

import smtplib
import requests
from email.message import EmailMessage
import urllib

import time

from chris_plugin import chris_plugin
from pflog import pflog

# XXX Make sure that your cfg filename starts with '.'
_CFG_FILENAME = '.notification.yaml'

_DEFAULT_ELEMENT_HOST = 'fedora.ems.host'


parser = ArgumentParser(description='A ChRIS Plugin for notification through mail / Slack / Element')
parser.add_argument('-c', '--content', type=str, required=False, default='', help=f'Content of the notification. Optionally specified in [inputdir]/{_CFG_FILENAME} if not specified in argument.')

parser.add_argument('-t', '--title', type=str, required=False, default='', help=f'[Optional] Title of the notification. Optionally specified in [inputdir]/{_CFG_FILENAME} if not specified in argument.')

parser.add_argument('-s', '--slack-url', type=str, required=False, default='',
                    help=f'[Optional] slack-url if we want to send notification through Slack. Optionally specified in [inputdir]/{_CFG_FILENAME} if not specified in argument.')

parser.add_argument('-e', '--element-room', type=str, required=False, default='',
                    help=f'[Optional] element-room (ex: ![room-id]:fedora.im) if we want to send notification through Element. Optionally specified in [inputdir]/{_CFG_FILENAME} if not specified in argument.')

parser.add_argument('-E', '--element-token', type=str, required=False, default='',
                    help=f'[Optional] element-token if we want to send notification through Element. Required if element-url exists. Optionally specified in [inputdir]/{_CFG_FILENAME} if not specified in argument.')

parser.add_argument('--element-host', type=str, required=False, default=f'{_DEFAULT_ELEMENT_HOST}',
                    help=f'[Optional] element-host if we want to send notification through Element. [inputdir]/{_CFG_FILENAME} is with higher priority than command-line based config.')


parser.add_argument('-r', '--rcpt', type=str, required=False, default='',
                    help=f'[Optional] comma separated email receipients if we want to send notification through email. Optionally specified in [inputdir]/{_CFG_FILENAME} if not specified in argument.')

parser.add_argument('-S', '--sender', type=str, required=False, default='noreply@fnndsc.org', help=f'sender (From) in email. [inputdir]/{_CFG_FILENAME} is with higher priority than command-line based config.')
parser.add_argument('-M', '--mail-server', type=str, required=False, default='postfix.postfix.svc.k8s.galena.fnndsc', help=f'email server. [inputdir]/{_CFG_FILENAME} is with higher priority than command-line based config.')


@chris_plugin(
    parser=parser,
    title='A ChRIS plugin for notification through mail / Slack / Element',
    category='',  # ref. https://chrisstore.co/plugins
    min_memory_limit='500Mi',  # supported units: Mi, Gi
    min_cpu_limit='1000m',  # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit=0,  # set min_gpu_limit=1 to enable GPU
)
@pflog.tel_logTime(
    event='notification',
    log='Notification',
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    inputdir_str = str(inputdir)
    outputdir_str = str(outputdir)
    print(f'inputdir: {inputdir_str} outputdir: {outputdir_str}')

    yaml_cfg = {}
    yaml_filename = os.sep.join([inputdir_str, _CFG_FILENAME])
    if os.path.exists(yaml_filename):
        with open(yaml_filename, 'r') as f:
            yaml_cfg = yaml.full_load(f)

    content = _cfg_or_arg(options.content, yaml_cfg, 'content', f'Notification: not in [inputdir]/{_CFG_FILENAME} and no --content')

    title = _arg_or_cfg(options.title, yaml_cfg, 'title')

    slack_url = _arg_or_cfg(options.slack_url, yaml_cfg, 'slack-url')

    element_room = _arg_or_cfg(options.element_room, yaml_cfg, 'element-room')
    element_token = _arg_or_cfg(options.element_token, yaml_cfg, 'element-token')
    element_host = _cfg_or_arg(options.element_host, yaml_cfg, 'element-host')

    rcpt = _arg_or_cfg(options.rcpt, yaml_cfg, 'rcpt')
    sender = _cfg_or_arg(options.sender, yaml_cfg, 'sender')
    mail_server = _cfg_or_arg(options.mail_server, yaml_cfg, 'mail-server')

    if slack_url:
        _send_slack(title=title, content=content, url=slack_url)

    if element_room and element_token:
        _send_element(title=title, content=content, room=element_room, token=element_token, host=element_host)

    if rcpt:
        _send_email(title=title, content=content, rcpt=rcpt, mail_server=mail_server, sender=sender)


def _arg_or_cfg(arg_val: str, cfg: dict, index: str, err_msg: str = '') -> str:
    if arg_val:
        return arg_val

    cfg_val = cfg.get(index, '')
    if cfg_val:
        return cfg_val

    if not err_msg:
        return ''

    raise RuntimeError(err_msg)


def _cfg_or_arg(arg_val: str, cfg: dict, index: str, err_msg: str = '') -> str:
    cfg_val = cfg.get(index, '')
    if cfg_val:
        return cfg_val

    if arg_val:
        return arg_val

    if not err_msg:
        return ''

    raise RuntimeError(err_msg)


def _send_slack(title: str, content: str, url: str):
    text_list = []
    if title:
        text_list.append(f'*{title}*')
    if content:
        text_list.append(content)
    text = '\n'.join(text_list)
    the_data = {
        'text': text,
    }

    headers = {
        'Content-Type': 'application/json',
    }

    resp = requests.post(url, data=json.dumps(the_data), headers=headers)
    if resp.status_code == 200:
        return

    raise resp.raise_for_status()


def _send_element(title: str, content: str, room: str, token: str, host=f'{_DEFAULT_ELEMENT_HOST}'):
    if not host:
        host = _DEFAULT_ELEMENT_HOST

    formatted_text_list = []
    text_list = []
    if title:
        formatted_text_list.append(f'<h6>[BOT]{title}</h6>')
        text_list.append(f'[BOT][{title}]')
    else:
        formatted_text_list.append('<h6>[BOT]</h6>')
        text_list.append('[BOT]')

    if content:
        formatted_text_list.append(content)
        text_list.append(content)

    formatted_text = ''.join(formatted_text_list)
    text = ' '.join(text_list)

    the_data = {
        'formatted_body': formatted_text,
        'body': text,
        'msgtype': 'm.text',
        'format': 'org.matrix.custom.html',
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'X-Requested-With, Content-Type, Authorization',
    }

    txn_id = 'chhsiaobot' + str(time.time() * 1000)
    percent_room = _parse_element_room(room)
    url = f'https://{host}/_matrix/client/v3/rooms/{percent_room}/send/m.room.message/{txn_id}?access_token={token}'

    resp = requests.put(url, data=json.dumps(the_data), headers=headers)
    if resp.status_code == 200:
        return

    raise resp.raise_for_status()


def _parse_element_room(room: str) -> str:
    if room.startswith('%21'):
        return room

    if not room.startswith('!'):
        room = '!' + room

    return urllib.parse.quote(room, safe='/', encoding=None, errors=None)


def _send_email(title: str, content: str, rcpt: str, mail_server: str, sender: str):
    if not rcpt:
        raise RuntimeError(f'Email: no --rcpt and not in [inputdir]/{_CFG_FILENAME}')

    msg = EmailMessage()
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = rcpt
    msg.set_content(content)

    s = smtplib.SMTP(mail_server)
    s.send_message(msg)
    s.quit()


if __name__ == '__main__':
    main()
