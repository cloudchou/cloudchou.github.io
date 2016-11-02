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
本系列博客将详细阐述Activity的启动流程，这些博客基于Cm 10.1源码研究。

  * <a href="http://www.cloudchou.com/android/post-788.html" target="_blank">深入理解Activity启动流程(一)&#8211;Activity启动的概要流程</a>
  * <a href="http://www.cloudchou.com/android/post-805.html" target="_blank">深入理解Activity启动流程(三)&#8211;Activity启动的详细流程1</a>
  * <a href="http://www.cloudchou.com/android/post-815.html" target="_blank">深入理解Activity启动流程(三)&#8211;Activity启动的详细流程2</a>
  * <a href="http://www.cloudchou.com/android/post-858.html" target="_blank">深入理解Activity启动流程(四)&#8211;Activity Task的调度算法</a>

在介绍Activity的详细启动流程之前，先为大家介绍Activity启动时涉及到的类，这样大家可以有大概的了解，不至于在细节中迷失。

Activity启动时涉及到的类有IActivityManager相关类, I<a href="http://www.cloudchou.com/tag/applicationthread" title="View all posts in ApplicationThread" target="_blank" class="tags">ApplicationThread</a>相关类, <a href="http://www.cloudchou.com/tag/activitymanagerservice" title="View all posts in ActivityManagerService" target="_blank" class="tags">ActivityManagerService</a>相关类。

## IActivityManager相关类

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager.png" alt="IActivityManager" width="764" height="755" class="aligncenter size-full wp-image-797" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager.png 764w, http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager-300x296.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/05/IActivityManager-151x150.png 151w" sizes="(max-width: 764px) 100vw, 764px" /></a>

Activity的管理采用binder机制，管理Activity的接口是IActivityManager. ActivityManagerService实现了Activity管理功能,位于system_server进程，ActivityManagerProxy对象是ActivityManagerService在普通应用进程的一个代理对象，应用进程通过ActivityManagerProxy对象调用ActivityManagerService提供的功能。应用进程并不会直接创建ActivityManagerProxy对象，而是通过调用ActiviyManagerNative类的工具方法getDefault方法得到ActivityManagerProxy对象。所以在应用进程里通常这样启动Activty:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">ActivityManagerNative.<span style="color: #006633;">getDefault</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">startActivity</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span></pre>
      </td>
    </tr>
  </table>
</div>

## IApplicationThread相关类

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread.png" alt="IApplicationThread" width="780" height="619" class="aligncenter size-full wp-image-798" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread.png 780w, http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread-300x238.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/05/IApplicationThread-189x150.png 189w" sizes="(max-width: 780px) 100vw, 780px" /></a>

应用进程需要调用ActivityManagerService提供的功能，而ActivityManagerService也需要主动调用应用进程以控制应用进程并完成指定操作。这样ActivityManagerService也需要应用进程的一个Binder代理对象，而这个代理对象就是ApplicationThreadProxy对象。

ActivityManagerService通过IApplicationThread接口管理应用进程，ApplicationThread类实现了IApplicationThread接口，实现了管理应用的操作，ApplicationThread对象运行在应用进程里。ApplicationThreadProxy对象是ApplicationThread对象在ActivityManagerService线程 (ActivityManagerService线程运行在system_server进程)内的代理对象，ActivityManagerService通过ApplicationThreadProxy对象调用ApplicationThread提供的功能，比如让应用进程启动某个Activity。

## ActivityManagerService相关类

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService.png" alt="ActivityManagerService" width="1168" height="1048" class="aligncenter size-full wp-image-795" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService.png 1168w, http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService-300x269.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService-1024x918.png 1024w, http://www.cloudchou.com/wp-content/uploads/2015/05/ActivityManagerService-167x150.png 167w" sizes="(max-width: 1168px) 100vw, 1168px" /></a>

ActivityManagerService管理Activity时，主要涉及以下几个类:

  * 1) ActivityManagerService，它是管理activity的入口类，聚合了ProcessRecord对象和ActivityStack对象
  * 2) ProcessRecord，表示应用进程记录，每个应用进程都有对应的ProcessRecord对象
  * 3) ActivityStack，该类主要管理回退栈 
  * 4) ActivityRecord，每次启动一个Actvity会有一个对应的ActivityRecord对象，表示Activity的一个记录
  * 5) ActivityInfo，Activity的信息，比如启动模式，taskAffinity，flag信息(这些信息在AndroidManifest.xml里声明Activity时填写)
  * 6) TaskRecord，Task记录信息，一个Task可能有多个ActivityRecord，但是一个ActivityRecord只能属于一个TaskRecord

<span style="color:red">注意:</span>

ActivityManagerService里只有一个ActivityStack对象，并不会像Android官方文档描述的一样，每个Task都有一个activity stack对象。ActivityStack管理ActivityRecord时，不是下面这样组织ActivityRecord的:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">List<span style="color: #339933;">&lt;</span>TaskRecord<span style="color: #339933;">&gt;</span> taskList<span style="color: #339933;">;</span> <span style="color: #666666; font-style: italic;">//ActivityStack类</span>
List<span style="color: #339933;">&lt;</span>ActivityRecord<span style="color: #339933;">&gt;</span> recordList<span style="color: #339933;">;</span><span style="color: #666666; font-style: italic;">// TaskRecord类</span></pre>
      </td>
    </tr>
  </table>
</div>

而是像下面这样组织ActivityRecord:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">ArrayList<span style="color: #339933;">&lt;</span>ActivityRecord<span style="color: #339933;">&gt;</span> mHistory <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ArrayList<span style="color: #339933;">&lt;</span>ActivityRecord<span style="color: #339933;">&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> <span style="color: #666666; font-style: italic;">//ActivityStack类里</span>
TaskRecord task<span style="color: #339933;">;</span> <span style="color: #666666; font-style: italic;">// ActivityRecord类里</span></pre>
      </td>
    </tr>
  </table>
</div>

也就是说ActivityManagerService组织回退栈时以ActivityRecord为基本单位，所有的ActivityRecord放在同一个ArrayList里，可以将mHistory看作一个栈对象，索引0所指的对象位于栈底，索引mHistory.size()-1所指的对象位于栈顶。

但是ActivityManagerService调度ActivityRecord时以task为基本单位，每个ActivityRecord对象都属于某个TaskRecord，一个TaskRecord可能有多个ActivityRecord。

ActivityStack没有TaskRecord列表的入口，只有在ActivityManagerService才有TaskRecord列表的入口:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> ArrayList<span style="color: #339933;">&lt;</span>TaskRecord<span style="color: #339933;">&gt;</span> mRecentTasks</pre>
      </td>
    </tr>
  </table>
</div>

ActivityStack管理ActivityRecord时，将属于同一个task的ActivityRecord放在一起，如下所示:

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack.png" alt="backstack" width="217" height="269" class="aligncenter size-full wp-image-796" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack.png 217w, http://www.cloudchou.com/wp-content/uploads/2015/05/backstack-121x150.png 121w" sizes="(max-width: 217px) 100vw, 217px" /></a>

回退栈里可看到两个task，假设上面的task为task1，下面的task为task2，task1包含D,E两个Activity Record，task2包含3个ActivityRecord。task1位于回退栈的栈顶，task2位于task1下面，task1中E位于栈顶，task2中C位于栈顶。需注意两个task的Activity不会混在一起，也就是说task2的B不能放在task1的D和E中间。

因为回退栈是栈结构，所以此时不断按返回键，显示的Activity的顺序为E&#8211;>D&#8211;>C&#8211;>B&#8211;>A。

下一篇博客为大家讲述Activity的详细启动流程。