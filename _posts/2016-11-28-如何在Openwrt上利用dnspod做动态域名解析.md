---
id: 984
title: 如何在Openwrt上利用dnspod做动态域名解析
date: 2016-11-28T08:21:49+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=984
permalink: /android/post-984.html
categories:
  - work
tags:
  - ddns
  - dnspod
  - 动态域名解析
  - OpenWrt
---

Openwrt有一个Dynamic DNS的插件可以支持动态域名解析，也就是ddns，虽然它没有直接支持dnspod的动态域名解析，但是支持dnspod是非常简单的事情，本篇讲述如何让Openwrt支持dnspod的动态域名解析。

## 背景

一直都想即使不在家里的时候，也能访问家里的网络及设备。为了实现这样的功能，必须直到家中路由器ip，但是因为是非公司网络，不会有固定ip，在网上找了一下方案，有说用花生壳ddns的，但是花生壳ddns不稳定。后来看到文章[《让OpenWrt原生ddns使用dnspod动态解析域名》](https://zhuanlan.zhihu.com/p/20629213)，试着操作了一下，发现有一些概念这篇文章并没有讲清楚，所以和大家分享一下我是如何做到动态域名解析的。

所谓ddns，也就是动态域名解析，其实就是说域名对应的ip不是固定的，会经常变化，这种情况下我们只需要维持域名和最新ip的对应关系，就可以通过域名去访问主机。而域名和最新ip对应的关系都是由dns服务提供商提供的，比如dnspod。所以，当ip变化时，我们只需要告知域名提供商将域名对应的ip更新至最新的ip即可。dnspod和其它域名提供商有些不同，其它域名提供商提供的修改的域名ip对应关系的接口需要用户名和密码，而dnspod提供的修改接口需要的是api token，这种方式更安全，因为就算token泄漏出去了，只需要登录后将token重新创建就好了，不用担心密码泄漏。

另外,dnspod提供了完整的操作域名的API接口，详情请查看[dnpsod API文档](https://www.dnspod.cn/docs/index.html)


## 准备工作

本篇介绍的方案基于OpenWrt Chaos Calmer 15.05,如果openwrt版本低于15.05，请自行升级到该版本。

1.  安装luci-app-ddns应用

    进入路由器设置网站，进入System->Software，然后搜索luci-app-ddns并安装，该应用依赖ddns，安装luci-app-ddns时会自动安装ddns应用。

2.  在路由器上安装curl

    进入路由器设置网站，进入System->Software，然后搜索curl并安装

## 操作步骤

1.  在dnspod上创建API token
    
    登录dnspod之后，进入用户中心，安全设置, 就可以看到如何创建API TOKEN了，创建成功后的示意图如下图所示:

    ![dnspod_create_token](/assets/blogimgs/dnspod_create_token.png)

    一定要注意api token形式是"id,token"，而不只是token，所以ID和token都需要记录下来，以备接下来使用，所以完整的api token类似于"13456,a5ee6fdfw3e24c8286bcb822bb1fb4e69f"

2.  获取domain id
    
    可以参考[dnpsod API文档](https://www.dnspod.cn/docs/index.html)，本篇给出用于获取的简单命令:

    ```bash
    curl -k  -X POST https://dnsapi.cn/Domain.List -d 'login_token=13456,a5ee6fdfw3e24c8286bcb822bb1fb4e69f&format=json'
    ```

    注意将api token换成你自己的api token，返回的数据类似于下面这个样子:

    ```json
    {
        "status": {
            "code": "1",
            // ...
        },
        "info": {
            "domain_total": 1,
            // ...
        },
        "domains": [
            {
                "id": 123456789,
                // ...
            }
        ]
    }

    ```

    上面的id就是domain id，请保存这个id，后续步骤会使用这个id

3.  利用domain id和api token获取子域名的record id

    用于获取的简单命令:

    ```bash
    curl -X POST https://dnsapi.cn/Record.List -d 'login_token=13456,a5ee6fdfw3e24c8286bcb822bb1fb4e69f&format=json&domain_id=123456789'
    ```

    注意将api token,domain id换成你自己的api token, domain id，返回的数据类似于下面这个样子:

    ```json
    {
        "status": {
            "code": "1",
            "message": "Action completed successful",
            "created_at": "2016-11-27 22:37:36"
        },
        "domain": {
            "id": 123456789,
            //...
        },
        "info": {
            "sub_domains": "20",
            // ...
        },
        "records": [
            //...
            {
                "id": "13413512",
                //...
                "name": "router",
                //...
            },
            //...
        ]
    }

    ```

    找到你的子域名对应的记录，其中的id就是你的子域名的record id， 如这里router子域名的id是13413512

4.  利用api token, domain id, record id 测试修改域名    

    测试命令如下所示:

    ```
    curl -k -X POST https://dnsapi.cn/Record.Modify -d 'login_token=13456,a5ee6fdfw3e24c8286bcb822bb1fb4e69f&format=json&domain_id=123456789&record_id=13413512&sub_domain=router&value=3.2.2.2&record_type=A&record_line=%e9%bb%98%e8%ae%a4'
    ```

    注意将api token,domain id, record id换成你自己的，修改成功后，你可以上dnspod看你的子域名对应的ip是否是3.2.2.2了，测试成功后可以继续下一个步骤

5.  在路由器上编写脚本/usr/bin/ddns_update.sh
    
    脚本内容如下所示:

    ```bash
    #!/bin/sh
    curl -k -X POST https://dnsapi.cn/Record.Modify -d "login_token=13456,a5ee6fdfw3e24c8286bcb822bb1fb4e69&format=json&domain_id=123456789&record_id=13413512&sub_domain=router&value=$1&record_type=A&record_line=%e9%bb%98%e8%ae%a4"
    return $?
    ```

    注意将api token,domain id, record id换成你自己的。 

6.  路由器上更新关联脚本

    在路由器设置网站上进入Services->Dynamic DNS，然后选择myddns_ipv4进行编辑，将enabled勾选，然后为DDNS Service provider选择custom，然后在Custom update-script里输入/usr/bin/ddns_update.sh,Hostname/Domain里填入完整的子域名，比如router.test.com，如下图所示:

    ![ddns_settings](/assets/images/ddns_settings.png)

    设置完毕后，点击Save & Apply，就可以关联成功了， 你测试一下把。 

    系统的操作日志可以查看/var/log/ddns/myddns_ipv4.log。

## 总结

因为dnspod提供了完整的操作域名的API接口，而openwrt也提供了动态修改域名的插件，并可以轻松地自定义，所以在openwrt上实现动态域名解析并不是一件很难的事情。

## 参考资料

[让OpenWrt原生ddns使用dnspod动态解析域名](https://zhuanlan.zhihu.com/p/20629213)

[dnpsod API文档](https://www.dnspod.cn/docs/index.html)

