# -*- coding:utf-8 -*-

import xmlrpc.client
import requests
import urllib


def ping(pingUrl, name, siteUrl, changesURL, rssUrl):
    """args: site_name, site_host, post_url, rss_url."""
    print('ping %s' % pingUrl)
    rpc_server = xmlrpc.client.ServerProxy(pingUrl)
    result = rpc_server.weblogUpdates.extendedPing(name, siteUrl, changesURL,
                                                   rssUrl)
    print(result)


def ping2(pingUrl, name, siteUrl, changesURL):
    data = {'name': name, 'url': siteUrl, 'changesURL': changesURL}
    reqUrl = '%s?%s' % (pingUrl, urllib.parse.urlencode(data))
    response = requests.get(reqUrl)
    print('ping %s' % pingUrl)
    if response.status_code == 200:
        print('ping google success')
    else:
        print('ping google failure.\n status: %d \n messge:\n%s',
              response.status_code, response.content)


def pingAllSe(siteName, siteHost, postUrl, rssUrl):
    pingUrlList = [
        'http://ping.baidu.com/ping/RPC2',
    ]
    for pingUrl in pingUrlList:
        ping(pingUrl, siteName, siteHost, postUrl, rssUrl)

    pingUrlList2 = [
        'http://blogsearch.google.com/ping/RPC2',
    ]
    for pingUrl in pingUrlList2:
        ping2(pingUrl, siteName, siteHost, postUrl)


def main():
    siteName = "CloudChou's Tech Blog"
    siteHost = "http://www.cloudchou.com"
    postUrl = 'http://www.cloudchou.com//web/post-994.html'
    rssUrl = "http://www.cloudchou.com/feed.xml"
    pingAllSe(siteName, siteHost, postUrl, rssUrl)
    # raw_input_B = input("raw_input: ")
    # print(raw_input_B)


if __name__ == '__main__':
    main()