import glob, os, sys
import argparse
import pandas as pd
from tqdm import tqdm
from subprocess import call
import sys
import click
from line_protocol_parser import parse_line
from time import sleep

assert sys.version[:1] == "3"

import paho.mqtt.client as mqtt
import json
import threading

data = {"flag": False}

t = None


def on_connect(self, client, userdata, rc):
    global data
    if rc == 0:
        data['flag'] = True
        print("connected OK Returned code=", rc)
    else:
        print("Bad connection Returned code=", rc)


def on_message(client, userdata, message):
    global data
    data['msg_count'] += 1

@click.group()
def cli():
    """A CLI wrapper for Line2Pub-lish"""


if __name__ == '__main__':
    cli()


def filename(path):
    return os.path.basename(path).split('.csv')[0]


def loop(data):
    while not data['flag']:
        pass

    print(data['file'])
    data['msg_count'] = 0
    file = data['file']
    model = data['model']
    delay = data['delay']
    pub_topic = data['pub_topic']
    client = data['client']

    num_lines = sum(1 for line in open(file, 'r'))
    pbar = tqdm(total=num_lines, leave=False, unit='lines')
    # telegraf/mart-ubuntu-s-1vcpu-1gb-sgp1-01/Model-PRO
    with open(file, 'r') as f:
        for line in f:
            sleep(delay)
            # sleep(0.00066)
            parsed = parse_line(line)
            topic = parsed['tags']['topic'].split("/")[-2]
            topic = "DUSTBOY/{}/{}".format(model, topic[1])
            parsed['timestamp'] = str(parsed['time']) + '000'
            # print(parsed['timestamp'])
            parsed['tags']['topic'] = topic
            client.publish(pub_topic, json.dumps(parsed, sort_keys=True))
            pbar.update(1)
        pbar.close()
        print('msg_count =  ', data['msg_count'])
        client.loop_stop()
        client.disconnect()
        raise SystemExit


t = threading.Thread(target=loop, args=(data,))
t.start()


# @click.option('--output-dir', required=True, type=str, help='Output directory')
@click.option('--file', required=True, type=str, help='Text file with line protocol format')
@click.option('--model', required=True, type=str, help='Model ID')
@click.option('--username', required=False, type=str, help='')
@click.option('--password', required=False, type=str, help='')
@click.option('--host', required=True, type=str, help='')
@click.option('--delay', required=True, type=float, help='')
@click.option('--port', required=True, type=int, help='')
@click.option('--echo', required=False, type=bool, help='')
@cli.command("publish")
def cc(file, model, username, password, host, port, delay, echo):
    """publish influx line protocol to mqtt !!!"""

    # print(file, model, username, password, host, port)

    client = mqtt.Client()
    pub_topic = 'etl/x/{}'.format(model)
    data['file'] = file
    data['model'] = model
    data['delay'] = delay
    data['pub_topic'] = pub_topic


    if username:
        client.username_pw_set(username, password)
    client.on_connect = on_connect
    if echo:
        client.on_message = on_message

    # client.on_message = on_message
    client.connect(host, port)
    client.subscribe(pub_topic)

    data['client'] = client

    client.loop_start()


def to_line(row):
    time = row['time']
    name = row['name']
    topic = row['topic']
    if 'host' in row:
        row = row.drop(labels=['time', 'name', 'topic', 'host'])
    else:
        row = row.drop(labels=['time', 'name', 'topic'])

    row = row[row != 0]
    s = "{},topic={} ".format(name, topic)
    for (key, val) in row.iteritems():
        s += "{}={},".format(key, val)
    s = s[:-1] + ' ' + str(time) + '\n'
    return s

# def write_meta(db, output_dir):
# 	lines = [
# 		"# DDL",
# 		"CREATE DATABASE {}".format(db),
# 		"",
# 		"# DML",
# 		"# CONTEXT-DATABASE: {}".format(db),
# 		""
# 	]
# 	with open(os.path.abspath(output_dir) + '/../meta.txt', 'w') as meta:
# 		meta.write("\n".join(lines))
