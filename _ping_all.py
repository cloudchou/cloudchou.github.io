#!/usr/bin/env python
# -*- coding:utf-8 -*-

import xmlrpclib


def ping(ping_url, *args, **kwds):
    """args: site_name, site_host, post_url, rss_url."""
    rpc_server = xmlrpclib.ServerProxy(ping_url)
    result = rpc_server.weblogUpdates.extendedPing(*args)
    print result


def ping_all(*args, **kwds):
    ping_url_list = [
        'http://ping.baidu.com/ping/RPC2',
        'http://blogsearch.google.com/ping/RPC2',
    ]
    for url in ping_url_list:
        ping(url, *args, **kwds)


# def main():
#     client = redis.pubsub()
#     client.subscribe(['ping'])
#     while True:
#         for item in client.listen():
#             if item['type'] == 'message':
#                 msg = item['data']
#                 if msg:
#                     post = json.loads(msg)
#                     print post
#                     ping_all(post.get('site_name'), post.get('site_host'),
#                              post.get('post_url'), post.get('rss_url'))


def main():
    site_name = "tech2ipo"
    site_host = "http://www.cloudchou.com"
    post_url = 'http://www.cloudchou.com/android/100855.html'
    rss_url = "http://www.cloudchou.com/feed.xml"
    ping_all(site_name, site_host, post_url, rss_url)
    raw_input_B = raw_input("raw_input: ")
    print(raw_input_B)

main()
