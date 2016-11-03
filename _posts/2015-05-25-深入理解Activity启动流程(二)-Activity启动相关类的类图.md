---
id: 793
title: '深入理解Activity启动流程(二)&#8211;Activity启动相关类的类图'
date: 2015-05-25T09:10:12+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=793
permalink: /android/post-793.html
views:
  - 4058
categories:
  - Android
  - 个人总结
tags:
  - ActivityManagerService
  - activity启动流程
  - activity启动过程
  - android activity启动
  - ApplicationThread
---
<p>本系列博客将详细阐述Activity的启动流程，这些博客基于Cm 10.1源码研究。</p>
<ul>
<li><a href="http://www.cloudchou.com/android/post-788.html" target="_blank">深入理解Activity启动流程(一)--Activity启动的概要流程</a></li>
<li><a href="http://www.cloudchou.com/android/post-805.html" target="_blank">深入理解Activity启动流程(三)--Activity启动的详细流程1</a></li>
<li><a href="http://www.cloudchou.com/android/post-815.html" target="_blank">深入理解Activity启动流程(三)--Activity启动的详细流程2</a></li>
<li><a href="http://www.cloudchou.com/android/post-858.html" target="_blank">深入理解Activity启动流程(四)--Activity Task的调度算法</a></li>
</ul>
<p>在介绍Activity的详细启动流程之前，先为大家介绍Activity启动时涉及到的类，这样大家可以有大概的了解，不至于在细节中迷失。</p>
<p>Activity启动时涉及到的类有IActivityManager相关类, IApplicationThread相关类, ActivityManagerService相关类。</p>
<h2>IActivityManager相关类</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager.png" alt="IActivityManager" width="764" height="755" class="aligncenter size-full wp-image-797" /></a>
<p>Activity的管理采用binder机制，管理Activity的接口是IActivityManager. ActivityManagerService实现了Activity管理功能,位于system_server进程，ActivityManagerProxy对象是ActivityManagerService在普通应用进程的一个代理对象，应用进程通过ActivityManagerProxy对象调用ActivityManagerService提供的功能。应用进程并不会直接创建ActivityManagerProxy对象，而是通过调用ActiviyManagerNative类的工具方法getDefault方法得到ActivityManagerProxy对象。所以在应用进程里通常这样启动Activty:</p>
```java
ActivityManagerNative.getDefault().startActivity()
```

<h2>IApplicationThread相关类</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread.png" alt="IApplicationThread" width="780" height="619" class="aligncenter size-full wp-image-798" /></a>
<p>应用进程需要调用ActivityManagerService提供的功能，而ActivityManagerService也需要主动调用应用进程以控制应用进程并完成指定操作。这样ActivityManagerService也需要应用进程的一个Binder代理对象，而这个代理对象就是ApplicationThreadProxy对象。</p>
<p>ActivityManagerService通过IApplicationThread接口管理应用进程，ApplicationThread类实现了IApplicationThread接口，实现了管理应用的操作，ApplicationThread对象运行在应用进程里。ApplicationThreadProxy对象是ApplicationThread对象在ActivityManagerService线程 (ActivityManagerService线程运行在system_server进程)内的代理对象，ActivityManagerService通过ApplicationThreadProxy对象调用ApplicationThread提供的功能，比如让应用进程启动某个Activity。</p>


<h2>ActivityManagerService相关类</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService.png" alt="ActivityManagerService" width="1168" height="1048" class="aligncenter size-full wp-image-795" /></a>
<p>ActivityManagerService管理Activity时，主要涉及以下几个类:</p>
<ul>
<li>1)\tActivityManagerService，它是管理activity的入口类，聚合了ProcessRecord对象和ActivityStack对象</li>
<li>2)\tProcessRecord，表示应用进程记录，每个应用进程都有对应的ProcessRecord对象</li>
<li>3)\tActivityStack，该类主要管理回退栈 </li>
<li>4)\tActivityRecord，每次启动一个Actvity会有一个对应的ActivityRecord对象，表示Activity的一个记录</li>
<li>5)\tActivityInfo，Activity的信息，比如启动模式，taskAffinity，flag信息(这些信息在AndroidManifest.xml里声明Activity时填写)</li>
<li>6)\tTaskRecord，Task记录信息，一个Task可能有多个ActivityRecord，但是一个ActivityRecord只能属于一个TaskRecord</li>
</ul>

<p><span style="color:red">注意:</span></p>
<p>ActivityManagerService里只有一个ActivityStack对象，并不会像Android官方文档描述的一样，每个Task都有一个activity stack对象。ActivityStack管理ActivityRecord时，不是下面这样组织ActivityRecord的:</p>
```java
List<TaskRecord> taskList; //ActivityStack类
List<ActivityRecord> recordList;// TaskRecord类
```
<p>而是像下面这样组织ActivityRecord:</p>
```java
ArrayList<ActivityRecord> mHistory = new ArrayList<ActivityRecord>(); //ActivityStack类里
TaskRecord task; // ActivityRecord类里
```
<p>也就是说ActivityManagerService组织回退栈时以ActivityRecord为基本单位，所有的ActivityRecord放在同一个ArrayList里，可以将mHistory看作一个栈对象，索引0所指的对象位于栈底，索引mHistory.size()-1所指的对象位于栈顶。</p>
<p>但是ActivityManagerService调度ActivityRecord时以task为基本单位，每个ActivityRecord对象都属于某个TaskRecord，一个TaskRecord可能有多个ActivityRecord。</p>
<p>ActivityStack没有TaskRecord列表的入口，只有在ActivityManagerService才有TaskRecord列表的入口:</p>
```java
final ArrayList<TaskRecord> mRecentTasks
```
<p>ActivityStack管理ActivityRecord时，将属于同一个task的ActivityRecord放在一起，如下所示:</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack.png" alt="backstack" width="217" height="269" class="aligncenter size-full wp-image-796" /></a>
<p>回退栈里可看到两个task，假设上面的task为task1，下面的task为task2，task1包含D,E两个Activity Record，task2包含3个ActivityRecord。task1位于回退栈的栈顶，task2位于task1下面，task1中E位于栈顶，task2中C位于栈顶。需注意两个task的Activity不会混在一起，也就是说task2的B不能放在task1的D和E中间。</p>
<p>因为回退栈是栈结构，所以此时不断按返回键，显示的Activity的顺序为E-->D-->C-->B-->A。</p>
<p>下一篇博客为大家讲述Activity的详细启动流程。</p>
