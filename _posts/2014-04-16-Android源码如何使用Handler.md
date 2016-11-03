---
id: 414
title: Android源码如何使用Handler
date: 2014-04-16T23:03:14+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=414
permalink: /android/post-414.html
views:
  - 3360
categories:
  - Android
tags:
  - ActivityThread
  - android handler and asynctask
  - android handler thread
  - android handler 使用
  - android handler 用法
  - HandlerThread
  - IntentService
---
## 前言

<a href="http://www.cloudchou.com/android/post-388.html" target="_blank">前一篇</a>文章我们详细分析了Handler机制的实现，这一篇会给大家介绍Android源码里如何使用Handler。这里会介绍以下4个例子：

  * ### 1) <a href="http://www.cloudchou.com/tag/activitythread" title="View all posts in ActivityThread" target="_blank" class="tags">ActivityThread</a>
    
    Activity运行在ActivityThread里，ActivityThread就是Android应用开发时所说的UI线程，或者说是主线程，它使用了Handler机制。

  * ### 2) AsyncTask
    
    AsyncTask的实现也用到了Handler机制。

  * ### 3) <a href="http://www.cloudchou.com/tag/handlerthread" title="View all posts in HandlerThread" target="_blank" class="tags">HandlerThread</a>
    
    HandlerThread继承自Thread，它的run方法里会创建Looper，并调用Looper.loop方法进入死循环，我们可以用HandlerThread实现worker thread。

  * ### 4) <a href="http://www.cloudchou.com/tag/intentservice" title="View all posts in IntentService" target="_blank" class="tags">IntentService</a>
    
    IntentService的实现使用了HandlerThread，将客户端的请求交给了HanderThread，这样不会阻塞主线程，也就不会产生ANR问题。

## 1. ActivityThread使用Handler

ActivityThread源码位于：frameworks/base/core/java/android/app/ActivityThread.java

  * 1) 准备Looper 
<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> main<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> args<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #666666; font-style: italic;">//创建主线程的Looper实例和MessageQueue实例</span>
  Looper.<span style="color: #006633;">prepareMainLooper</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #666666; font-style: italic;">//创建ActivityThread			</span>
  ActivityThread thread <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ActivityThread<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #666666; font-style: italic;">//交给ActivityManagerService管理</span>
  thread.<span style="color: #006633;">attach</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #666666; font-style: italic;">//设置mainHandler</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sMainThreadHandler <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      sMainThreadHandler <span style="color: #339933;">=</span> thread.<span style="color: #006633;">getHandler</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #666666; font-style: italic;">//初始化AsyncTask，设置它的Handler，这样在Activity里使用AsyncTask才可正常使用</span>
  AsyncTask.<span style="color: #006633;">init</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      Looper.<span style="color: #006633;">myLooper</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setMessageLogging</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span>
              LogPrinter<span style="color: #009900;">&#40;</span>Log.<span style="color: #006633;">DEBUG</span>, <span style="color: #0000ff;">"ActivityThread"</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #666666; font-style: italic;">//进入loop循环，会不断从MessageQueue里取出Message，并分发Message</span>
  Looper.<span style="color: #006633;">loop</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Main thread loop unexpectedly exited"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 2) 创建Handler
<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> H mH <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> H<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">class</span> H <span style="color: #000000; font-weight: bold;">extends</span> Handler <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> LAUNCH_ACTIVITY         <span style="color: #339933;">=</span> <span style="color: #cc66cc;">100</span><span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> PAUSE_ACTIVITY          <span style="color: #339933;">=</span> <span style="color: #cc66cc;">101</span><span style="color: #339933;">;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #003399;">String</span> codeToString<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> code<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>DEBUG_MESSAGES<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #000000; font-weight: bold;">switch</span> <span style="color: #009900;">&#40;</span>code<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              <span style="color: #000000; font-weight: bold;">case</span> LAUNCH_ACTIVITY<span style="color: #339933;">:</span> <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #0000ff;">"LAUNCH_ACTIVITY"</span><span style="color: #339933;">;</span>
              <span style="color: #000000; font-weight: bold;">case</span> PAUSE_ACTIVITY<span style="color: #339933;">:</span> <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #0000ff;">"PAUSE_ACTIVITY"</span><span style="color: #339933;">;</span>
          <span style="color: #666666; font-style: italic;">//...</span>
          <span style="color: #009900;">&#125;</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #003399;">Integer</span>.<span style="color: #006633;">toString</span><span style="color: #009900;">&#40;</span>code<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #666666; font-style: italic;">//覆盖Handler的handleMessage方法，针对不同的消息类型进行不同的处理</span>
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> handleMessage<span style="color: #009900;">&#40;</span>Message msg<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>DEBUG_MESSAGES<span style="color: #009900;">&#41;</span> Slog.<span style="color: #006633;">v</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"&gt;&gt;&gt; handling: "</span> <span style="color: #339933;">+</span> 
                                   codeToString<span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">what</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">switch</span> <span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">what</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #000000; font-weight: bold;">case</span> LAUNCH_ACTIVITY<span style="color: #339933;">:</span> <span style="color: #009900;">&#123;</span>
              Trace.<span style="color: #006633;">traceBegin</span><span style="color: #009900;">&#40;</span>Trace.<span style="color: #006633;">TRACE_TAG_ACTIVITY_MANAGER</span>,
               <span style="color: #0000ff;">"activityStart"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              ActivityClientRecord r <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>ActivityClientRecord<span style="color: #009900;">&#41;</span>msg.<span style="color: #006633;">obj</span><span style="color: #339933;">;</span>
&nbsp;
              r.<span style="color: #006633;">packageInfo</span> <span style="color: #339933;">=</span> getPackageInfoNoCheck<span style="color: #009900;">&#40;</span>
                      r.<span style="color: #006633;">activityInfo</span>.<span style="color: #006633;">applicationInfo</span>, r.<span style="color: #006633;">compatInfo</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              handleLaunchActivity<span style="color: #009900;">&#40;</span>r, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              Trace.<span style="color: #006633;">traceEnd</span><span style="color: #009900;">&#40;</span>Trace.<span style="color: #006633;">TRACE_TAG_ACTIVITY_MANAGER</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">break</span><span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">case</span> RELAUNCH_ACTIVITY<span style="color: #339933;">:</span> <span style="color: #009900;">&#123;</span>
              Trace.<span style="color: #006633;">traceBegin</span><span style="color: #009900;">&#40;</span>Trace.<span style="color: #006633;">TRACE_TAG_ACTIVITY_MANAGER</span>, 
              <span style="color: #0000ff;">"activityRestart"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              ActivityClientRecord r <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>ActivityClientRecord<span style="color: #009900;">&#41;</span>msg.<span style="color: #006633;">obj</span><span style="color: #339933;">;</span>
              handleRelaunchActivity<span style="color: #009900;">&#40;</span>r<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              Trace.<span style="color: #006633;">traceEnd</span><span style="color: #009900;">&#40;</span>Trace.<span style="color: #006633;">TRACE_TAG_ACTIVITY_MANAGER</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">break</span><span style="color: #339933;">;</span>
         <span style="color: #666666; font-style: italic;">//...</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>DEBUG_MESSAGES<span style="color: #009900;">&#41;</span> Slog.<span style="color: #006633;">v</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"&lt;&lt;&lt; done: "</span> <span style="color: #339933;">+</span> 
                           codeToString<span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">what</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
 <span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 3) 使用Handler发送消息
<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> queueOrSendMessage<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> what, <span style="color: #003399;">Object</span> obj, <span style="color: #000066; font-weight: bold;">int</span> arg1, <span style="color: #000066; font-weight: bold;">int</span> arg2<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>DEBUG_MESSAGES<span style="color: #009900;">&#41;</span> Slog.<span style="color: #006633;">v</span><span style="color: #009900;">&#40;</span>
          TAG, <span style="color: #0000ff;">"SCHEDULE "</span> <span style="color: #339933;">+</span> what <span style="color: #339933;">+</span> <span style="color: #0000ff;">" "</span> <span style="color: #339933;">+</span> mH.<span style="color: #006633;">codeToString</span><span style="color: #009900;">&#40;</span>what<span style="color: #009900;">&#41;</span>
          <span style="color: #339933;">+</span> <span style="color: #0000ff;">": "</span> <span style="color: #339933;">+</span> arg1 <span style="color: #339933;">+</span> <span style="color: #0000ff;">" / "</span> <span style="color: #339933;">+</span> obj<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      Message msg <span style="color: #339933;">=</span> Message.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      msg.<span style="color: #006633;">what</span> <span style="color: #339933;">=</span> what<span style="color: #339933;">;</span>
      msg.<span style="color: #006633;">obj</span> <span style="color: #339933;">=</span> obj<span style="color: #339933;">;</span>
      msg.<span style="color: #006633;">arg1</span> <span style="color: #339933;">=</span> arg1<span style="color: #339933;">;</span>
      msg.<span style="color: #006633;">arg2</span> <span style="color: #339933;">=</span> arg2<span style="color: #339933;">;</span>
      mH.<span style="color: #006633;">sendMessage</span><span style="color: #009900;">&#40;</span>msg<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

ActivityThread里的Schedule系列方法都是调用queueOrSendMessage发送Message，然后在Handler里处理消息

## 2. AsyncTask使用Handler

  * 1) Handler子类
<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">class</span> InternalHandler <span style="color: #000000; font-weight: bold;">extends</span> Handler <span style="color: #009900;">&#123;</span>
  @SuppressWarnings<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"unchecked"</span>, <span style="color: #0000ff;">"RawUseOfParameterizedType"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
  @Override
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> handleMessage<span style="color: #009900;">&#40;</span>Message msg<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      AsyncTaskResult result <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>AsyncTaskResult<span style="color: #009900;">&#41;</span> msg.<span style="color: #006633;">obj</span><span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">switch</span> <span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">what</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #000000; font-weight: bold;">case</span> MESSAGE_POST_RESULT<span style="color: #339933;">:</span><span style="color: #666666; font-style: italic;">//告知结果，会回调onPostExecute方法</span>
              <span style="color: #666666; font-style: italic;">// There is only one result</span>
              result.<span style="color: #006633;">mTask</span>.<span style="color: #006633;">finish</span><span style="color: #009900;">&#40;</span>result.<span style="color: #006633;">mData</span><span style="color: #009900;">&#91;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#93;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              <span style="color: #000000; font-weight: bold;">break</span><span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">case</span> MESSAGE_POST_PROGRESS<span style="color: #339933;">:</span><span style="color: #666666; font-style: italic;">//汇报进度，会回调onProgressUpdate</span>
              result.<span style="color: #006633;">mTask</span>.<span style="color: #006633;">onProgressUpdate</span><span style="color: #009900;">&#40;</span>result.<span style="color: #006633;">mData</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              <span style="color: #000000; font-weight: bold;">break</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> InternalHandler sHandler <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> InternalHandler<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 2) 初始化
关联loope和MessageQueue

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> init<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  sHandler.<span style="color: #006633;">getLooper</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

实际上不执行sHandler.getLooper()也可以正常关联looper和MessageQueue，在ui线程里创建AsyncTask时，就会初始化好sHandler。

  * 3) 发送消息
<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> Result postResult<span style="color: #009900;">&#40;</span>Result result<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  @SuppressWarnings<span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"unchecked"</span><span style="color: #009900;">&#41;</span>
  Message message <span style="color: #339933;">=</span> sHandler.<span style="color: #006633;">obtainMessage</span><span style="color: #009900;">&#40;</span>MESSAGE_POST_RESULT,
          <span style="color: #000000; font-weight: bold;">new</span> AsyncTaskResult<span style="color: #339933;">&lt;</span>Result<span style="color: #339933;">&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span>, result<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  message.<span style="color: #006633;">sendToTarget</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">return</span> result<span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">void</span> publishProgress<span style="color: #009900;">&#40;</span>Progress... <span style="color: #006633;">values</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>isCancelled<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      sHandler.<span style="color: #006633;">obtainMessage</span><span style="color: #009900;">&#40;</span>MESSAGE_POST_PROGRESS,
              <span style="color: #000000; font-weight: bold;">new</span> AsyncTaskResult<span style="color: #339933;">&lt;</span>Progress<span style="color: #339933;">&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span>, values<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">sendToTarget</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 3. HandlerThread

HandlerThread从Thread类继承，run方法里会创建Looper，并调用Looper.prepare和Looper.loop方法，这样HandlerThread有了自己的Looper对象和MessageQueue对象。

使用HandlerThread时，必须调用start方法，这样便启动了一个带有Looper的新线程。

HandlerThread使用示例：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> Handler sAsyncHandler
<span style="color: #000000; font-weight: bold;">static</span><span style="color: #009900;">&#123;</span>
HandlerThread thr <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> HandlerThread<span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Open browser download async"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
thr.<span style="color: #006633;">start</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
sAsyncHandler <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Handler<span style="color: #009900;">&#40;</span>thr.<span style="color: #006633;">getLooper</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span> 
@Override
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onReceive<span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">Context</span> context, Intent intent<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #003399;">Runnable</span> worker <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Runnable</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      @Override
      <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          onReceiveAsync<span style="color: #009900;">&#40;</span>context, id<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          result.<span style="color: #006633;">finish</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span><span style="color: #339933;">;</span>
  <span style="color: #666666; font-style: italic;">//worker会在HandlerThread里运行，而不会在调用onReceive的线程里执行</span>
  sAsyncHandler.<span style="color: #006633;">post</span><span style="color: #009900;">&#40;</span>worker<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 4. IntentService

IntentService继承于Service，用于处理异步请求。Client通过startService(Intent)发送请求给IntentService，这样便启动了service，它会使用worker thread处理每个Intent请求，处理完所有请求后，它就会停止。

IntentService使用了work queue processor模式将任务从主线程剥离，IntentService的子类不用关心这些事情，只需关注自己的逻辑即可，不用担心ANR异常，因为所有的任务都会在非主线程里按序执行。使用IntentService时只需从IntentService继承，并实现onHandleIntent(Intent)方法，注意onHandleIntent是运行在非主线程里的。IntentService接收Intent后，会启动一个worker thread，并在适当的时候停止。

所有的请求都会在同一个worker thread里处理，不用担心他们运行时间非常长，它们也不会阻塞程序的main loop。这些请求会形成队列，每次处理一个，处理完一个后再从队列里取出下一个进行处理。

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">abstract</span> <span style="color: #000000; font-weight: bold;">class</span> IntentService <span style="color: #000000; font-weight: bold;">extends</span> Service <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">volatile</span> Looper mServiceLooper<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">volatile</span> ServiceHandler mServiceHandler<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">String</span> mName<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">boolean</span> mRedelivery<span style="color: #339933;">;</span>
&nbsp;
   <span style="color: #008000; font-style: italic; font-weight: bold;">/**
    *ServiceHandler使用HandlerThread的Looper
    *没有使用主线程的Looper
    *故此它的handleMessage方法在HandlerThread里执行，而非主线程
		*/</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000000; font-weight: bold;">class</span> ServiceHandler <span style="color: #000000; font-weight: bold;">extends</span> Handler <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">public</span> ServiceHandler<span style="color: #009900;">&#40;</span>Looper looper<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">super</span><span style="color: #009900;">&#40;</span>looper<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        @Override
        <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> handleMessage<span style="color: #009900;">&#40;</span>Message msg<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            onHandleIntent<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>Intent<span style="color: #009900;">&#41;</span>msg.<span style="color: #006633;">obj</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            stopSelf<span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">arg1</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//name用于给worker thread命名，方便调试 </span>
    <span style="color: #000000; font-weight: bold;">public</span> IntentService<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> name<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">super</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        mName <span style="color: #339933;">=</span> name<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
   <span style="color: #008000; font-style: italic; font-weight: bold;">/**
    *设置intent redelivery偏好 
    *如果enabled设置为true， 
    *那么当进程在onHandleIntent(Intent)返回之前被杀死了， 
    *onStartCommand(Intent, int, int)会返回Service.START_REDELIVER_INTENT
    *进程会被重启，intent会被重新发送
    *如果多个Intent被发送了，那么只有最新的那个会被保证重新发送
    *如果enabled设置为false，
    *那么当进程在onHandleIntent(Intent)返回之前被杀死了
    *onStartCommand(Intent, int, int)会返回Service.START_NOT_STICKY
    *Intent也不会被重新发送     
    */</span>
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> setIntentRedelivery<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">boolean</span> enabled<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        mRedelivery <span style="color: #339933;">=</span> enabled<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onCreate<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span> 
        <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onCreate</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//在HandlerThread里处理请求，而非UI线程</span>
        HandlerThread thread <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> HandlerThread
                            <span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"IntentService["</span> <span style="color: #339933;">+</span> mName <span style="color: #339933;">+</span> <span style="color: #0000ff;">"]"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        thread.<span style="color: #006633;">start</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//mServiceHandler使用HandlerThread的looper对象，而非主线程的</span>
        mServiceLooper <span style="color: #339933;">=</span> thread.<span style="color: #006633;">getLooper</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        mServiceHandler <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ServiceHandler<span style="color: #009900;">&#40;</span>mServiceLooper<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
   <span style="color: #008000; font-style: italic; font-weight: bold;">/**
    *收到Intent后，让HandlerThread处理，
    *然后mServiceHandler的handleMessage会调用
    *留给子类实现的onHandleIntent方法
    */</span>
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onStart<span style="color: #009900;">&#40;</span>Intent intent, <span style="color: #000066; font-weight: bold;">int</span> startId<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        Message msg <span style="color: #339933;">=</span> mServiceHandler.<span style="color: #006633;">obtainMessage</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        msg.<span style="color: #006633;">arg1</span> <span style="color: #339933;">=</span> startId<span style="color: #339933;">;</span>
        msg.<span style="color: #006633;">obj</span> <span style="color: #339933;">=</span> intent<span style="color: #339933;">;</span>
        mServiceHandler.<span style="color: #006633;">sendMessage</span><span style="color: #009900;">&#40;</span>msg<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//不要覆盖该方法，而是要覆盖onHandleIntent方法</span>
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">int</span> onStartCommand<span style="color: #009900;">&#40;</span>Intent intent, <span style="color: #000066; font-weight: bold;">int</span> flags, <span style="color: #000066; font-weight: bold;">int</span> startId<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        onStart<span style="color: #009900;">&#40;</span>intent, startId<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> mRedelivery <span style="color: #339933;">?</span> START_REDELIVER_INTENT <span style="color: #339933;">:</span> START_NOT_STICKY<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
		<span style="color: #666666; font-style: italic;">//退出</span>
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onDestroy<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        mServiceLooper.<span style="color: #006633;">quit</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #008000; font-style: italic; font-weight: bold;">/**
     *  不需要覆盖onBind方法，在IntentService里不用这个方法     
     */</span>
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> IBinder onBind<span style="color: #009900;">&#40;</span>Intent intent<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #008000; font-style: italic; font-weight: bold;">/**
     *这个方法会在worker thread线程执行，即HandlerThread，
     *一次只处理一个Intent请求，
     *处理请求时会和程序的其它逻辑完全独立
     *因此如果处理请求需要一段时间的话，发送给IntentService的Intent请求会被排队
     *所有请求都被处理完毕后，IntentService会干掉自己，
     *子类实现该方法时不需要调用stopSelf。
     */</span>
    <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000000; font-weight: bold;">abstract</span> <span style="color: #000066; font-weight: bold;">void</span> onHandleIntent<span style="color: #009900;">&#40;</span>Intent intent<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>