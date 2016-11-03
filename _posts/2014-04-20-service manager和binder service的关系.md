---
id: 327
title: service manager和binder service的关系
date: 2014-04-20T14:01:36+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=327
permalink: /android/post-327.html
views:
  - 4299
categories:
  - Android
tags:
  - binder service manager
  - binder service service manager
  - binder机制
  - IPC框架
  - service manager android
---
<p>service manager是所有binder service的管理者，但它并不是这些binder service的创建者。</p>
<p>这些binder service有些是init进程启动的服务创建的，有些是system_server进程创建的，但是service manager会管理所有binder service的信息，方便client查询以及调用。</p>
<p>service manager是由init进程直接启动的，在init.rc里有 </p>
```makefile
service servicemanager /system/bin/servicemanager
    class core
    user system
    group system
    critical
    onrestart restart zygote
    onrestart restart media
    onrestart restart surfaceflinger
    onrestart restart drm
```   
<p>ActivityManagerService,PackageManagerService等由system_server进程启动的binder service实际上并没有单独的进程，它们只是system_server的一个子线程。init进程会启动surface flinger，media server, drmserver等服务，在这些服务里会创建binder service，并注册到service manager。</p>
<p>init.rc声明了surfaceflinger：</p>
```makefile
service surfaceflinger /system/bin/surfaceflinger
    class main
    user system
    group graphics drmrpc
\t\tonrestart restart zygote
```    
<p>native binder service 和 java 层的binder service，都会交由service manager注册，然后由service manager管理。客户端使用binder service时需要向service manager查询得到binder service在当前进程的一个代理，通过代理与binder service的服务端交互。</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/binder线程.png"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/binder线程.png" alt="binder线程" width="480" height="573" class="alignnone size-full wp-image-329" /></a>
