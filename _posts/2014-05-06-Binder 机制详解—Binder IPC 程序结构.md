---
id: 497
title: Binder 机制详解—Binder IPC 程序结构
date: 2014-05-06T23:58:16+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=497
permalink: /android/post-497.html
views:
  - 5166
categories:
  - Android
tags:
  - android binder
  - android binder 分析
  - android binder 设计与实现
  - android binder机制
  - android binder详解
---
<h2>前言</h2>
<p>通过Binder入门系列，我们已知道如何创建native binder service，framework binder service，应用层binder service，并知道如何编写framework层和应用层的客户端去调用native binder service。接下来几篇博客将为大家详细分析Binder机制，目前打算写如下几篇博客：</p>
<ul>
<li>
 <h3>1)Binder IPC 程序结构</h3>
 <p>介绍binder service的服务端进程，客户端进程，ServiceManager进程三者之间的关系</p>
</li>
<li>
 <h3>2)Binder的系统架构</h3>
 <p>介绍Binder系统架构的层次划分，每个层次的作用，并详细介绍系统架构的适配层和核心库。</p>
</li>
<li>
 <h3>3)Binder的本地库框架</h3> 
</li>
<li>
 <h3>4)Binder的Java层框架</h3> 
</li>
</ul>
<h2>Binder IPC 程序结构</h2>
<p>Binder IPC 程序结构如下图所示：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/Binder-IPC-程序结构.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/Binder-IPC-程序结构.jpg" alt="Binder IPC 程序结构" width="554" height="376" class="aligncenter size-full wp-image-500" /></a>
<p>我们先从进程的角度来分析，Binder机制共涉及3个进程， 服务端进程，客户端进程，管理各种binder service的service manager进程。图中进程2是服务端进程，进程1是客户端进程，IServiceManager服务对象所在进程便是ServiceManager进程。</p>
<p>我们知道servicemanager进程是init进程解析init.rc启动的关键本地服务，但是多个binder service提供者可能在同一个进程里，并不是说每个binder service提供者都各自独占一个进程，象system_server进程就有多个binder service，比如activity manager service，package manager service，power manager service。</p>
<p>服务端进程启动后会获取IServiceManager的引用，然后调用它的addService方法在ServiceManager里注册binder service。客户端进程启动后也会获取IServiceManager的引用，然后调用它的getService方法获取binder service引用，再调用引用的方法。</p>
<p>我们再从程序框架角度分析，服务端进程的BnXXX和客户端进程的BpXXX同时实现了接口xxx，这里其实使用了代理模式，并且是远程代理。客户端进程通过IServiceManager获取的binder引用其实是一个IBinder指针，BpXXX会保存这个IBinder指针，BpXXX实现接口xxx的方法时都是通过IBinder指针提交一些信息到服务端进程，这些信息包括方法的参数信息，用于接收返回值的Parcel对象，代表某个方法的常量(不同的常量表示调用不同的方法)。IBinder指针提交信息其实是通过驱动层提交到服务端进程的。服务端进程实现BnXXX时，框架层最终会调用onTransact方法，根据不同的code调用不同的方法，并将结果返回给客户端。</p>
<h2>参考资料</h2>
<p>书《Android系统原理及开发要点详解》 第4章Android的底层库和程序</p>
