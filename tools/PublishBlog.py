import time
import functools
import codecs
import re
import os
import PingAllSe
import sys

scriptDir = os.path.split(os.path.realpath(__file__))[0]
postDir = scriptDir + '/..//_posts'


def getBlogFilePath(blogTitle):
    files = os.listdir(postDir)
    for filename in files:
        filepath = postDir + "/" + filename
        if not filepath.endswith('.md'):
            continue
        if filepath.find(blogTitle) != -1:
            return filepath
    return ''


def getFileContent(filePath):
    with codecs.open(filePath, 'r', 'utf-8') as f:
        return f.readlines()


def publishBlog(blogTitle):
    filePath = getBlogFilePath(blogTitle)
    if filePath == '':
        print('can not find blog')
        sys.exit(-1)
    print('file path: %s' % filePath)
    fileContent = getFileContent(filePath)
    metaFileContent = re.sub(
        r'(---.*---).*', r'\1', ''.join(fileContent), flags=re.M | re.S)
    pattern = r'---.*permalink: ([\S]+).*---'
    postLinkStr = re.sub(pattern, r'\1', metaFileContent, flags=re.M | re.S)
    postRealLink = "http://www.cloudchou.com" + postLinkStr
    print(postRealLink)
    # pingAllSeCmd = '%s/PingAllSe.py' % (scriptDir)
    siteName = "tech2ipo"
    siteHost = "http://www.cloudchou.com"
    # postUrl = 'http://www.cloudchou.com/android/100855.html'
    rssUrl = "http://www.cloudchou.com/feed.xml"
    PingAllSe.pingAllSe(siteName, siteHost, postRealLink, rssUrl)


def main():
    blogTitle = input("请输入文章标题：")
    publishBlog(blogTitle)


if __name__ == '__main__':
    main()