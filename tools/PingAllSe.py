# -*- coding:utf-8 -*-

import xmlrpc.client


def ping(ping_url, *args, **kwds):
    """args: site_name, site_host, post_url, rss_url."""
    print('ping %s' % ping_url)
    rpc_server = xmlrpc.client.ServerProxy(ping_url)
    result = rpc_server.weblogUpdates.extendedPing(*args)
    print(result)


def pingAllSe(*args, **kwds):
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
    post_url = 'http://www.cloudchou.com//web/post-994.html'
    rss_url = "http://www.cloudchou.com/feed.xml"
    pingAllSe(site_name, site_host, post_url, rss_url)
    # raw_input_B = input("raw_input: ")
    # print(raw_input_B)


if __name__ == '__main__':
    main()