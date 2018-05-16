# -*- coding: utf8 -*-
import datetime
import time
import functools
import re
import codecs
import os
import sys
import string

# reload(sys)
# sys.setdefaultencoding('utf-8')  # 允许打印unicode字符

scriptDir = os.path.split(os.path.realpath(__file__))[0]
postDir = scriptDir + '/..//_posts'


def getFileContent(filename):
    with codecs.open(filename, 'r', 'utf-8') as f:
        s = f.readlines()
        return s


def writeFileContent(filepath, content):
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.writelines(content)

def getMaxPostId(postDir):
    files = os.listdir(postDir)
    maxPostId = 1
    # maxMetaFileContent = ''
    for filename in files:
        filepath = postDir + "/" + filename
        if not filepath.endswith('.md'):
            continue
        # print('open file : %s' % filepath)
        fileContent = ''.join(getFileContent(filepath))
        flags = re.M | re.S
        pattern = r'(---.*---).*'
        metaFileContent = re.sub(pattern, r'\1', fileContent, flags=flags)
        idStr = re.sub(r'.*id:\s*(\d+).*', r'\1', metaFileContent, flags=flags)
        id = int(idStr)
        if id > maxPostId:
            maxPostId = id
            # maxMetaFileContent = metaFileContent
    # print('max id file: \n'+maxMetaFileContent)
    return maxPostId


def getContentTemplate():
    return '''
    ---
    id: %d
    title: %s
    date: %s
    author: cloud
    layout: post
    guid: http://www.cloudchou.com/?p=%d
    permalink: /android/post-%d.html
    categories:
        - Android
    tags:
        - Android
    ---
    '''


def createBlog(blogTitle):
    print("blog title: " + blogTitle)
    # 2013-12-26T23:40:06+08:00
    nowDateTime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    maxId = getMaxPostId(postDir)
    newId = maxId + 1
    contentTemplate = getContentTemplate()
    content = contentTemplate % (newId, blogTitle, nowDateTime, newId, newId)
    content = re.sub(r' {4}', r'', content)
    content = re.sub(r'^\n', r'', content)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    fileName = '%s-%s.md' % (today, blogTitle)
    filePath = postDir + '/' + fileName
    print('blog file name : %s \n %s' % (fileName, content))
    writeFileContent(filePath, content)
    return filePath


def main():
    blogTitle = input("请输入文章标题：")
    blogFilePath = createBlog(blogTitle)
    os.system('code %s' % blogFilePath)


if __name__ == '__main__':
    main()
