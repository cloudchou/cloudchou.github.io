---
id: 388
title: Handler Looper MessageQueue 详解
date: 2014-04-16T01:15:54+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=388
permalink: /android/post-388.html
views:
  - 5084
categories:
  - Android
tags:
  - android handler message
  - android handler message queue
  - android handler message queue looper
  - android looper
  - android looper.prepare()
  - android looper用法
---
## 前言

一直对Android的Handler机制好奇，搞不清Handler,Looper,MessageQueue,Message之间的关系，近日对其做了一个深入研究，和大家分享一下。

## 类之间的关系

与Handler机制密切相关的类共5个，Handler，Looper，MessageQueue，Message，Messenger，Looper是最核心的类，它负责为线程建立Looper对象(通过静态方法)，还负责创建线程的消息队列MessageQueue对象，并负责处理MessageQueue的Message。MessageQueue负责管理Message。Handler会创建Message对象，同时将自己与Message对象关联，并压入MessageQueue，Looper会调用Handler分发Message。

<span style="color:red">注意:</span> 每个线程都至多只可以有一个Looper对象，也只可以有一个与该Looper对象关联的MessageQueue对象，但是可有多个Handler对象。Looper将Message取出来后，会调用与该Message关联的Handler的dispatchMessage方法。

类之间的关系如下图所示：(看不清的话请看<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图.png" target="_blank" style="text-decoration: underline">大图</a>：)

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图-979x1024.png" alt="Handler类图" width="979" height="1024" class="alignnone size-large wp-image-402" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图-979x1024.png 979w, http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图-286x300.png 286w, http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图-143x150.png 143w, http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图.png 1118w" sizes="(max-width: 979px) 100vw, 979px" /></a>

### Looper

Looper的设计使用了多线程设计模式里的Thread Specifical Storage模式，属性sThreadLocal为每个线程存储Looper对象。

sMainLooper是主线程使用的Looper对象。

使用Looper对象时，会先调用静态的prepare方法或者prepareMainLooper方法来创建线程的Looper对象。如果是主线程会调用prepareMainLooper，如果是普通线程只需调用prepare方法，两者都会调用prepare(boolean quitAllowed)方法，该方法源码如下：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> prepare<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">boolean</span> quitAllowed<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
 <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sThreadLocal.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Only one Looper may be created per thread"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
 <span style="color: #009900;">&#125;</span>
 sThreadLocal.<span style="color: #006633;">set</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> Looper<span style="color: #009900;">&#40;</span>quitAllowed<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

这样便为线程建立了Looper对象，quitAllowed表示是否允许退出，如果是主线程则不能允许退出。

prepareMainLooper创建好Looper对象之后，还会将sMainLooper引用新建立的Looper对象。

myLooper方法会返回当前线程的Looper对象，myQueue方法则会返回当前线程Looper对象的MessageQueue对象。

Looper的构造器方法里会创建当前线程的MessageQueue实例，并将mThread指向当前线程。源码如下所示：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> Looper<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">boolean</span> quitAllowed<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        mQueue <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> MessageQueue<span style="color: #009900;">&#40;</span>quitAllowed<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        mRun <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
        mThread <span style="color: #339933;">=</span> <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

使用Looper时，调用完Looper.prepare之后，还需要调用Looper.loop方法，该方法是一个死循环，会不断从MessageQueue里取出消息，并调用消息关联的Handler对象来处理该消息，Handler对象会分发该消息。loop的源码如下：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> loop<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">final</span> Looper me <span style="color: #339933;">=</span> myLooper<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>me <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"No Looper; Looper"</span>
      <span style="color: #339933;">+</span><span style="color: #0000ff;">"prepare() wasn't called on this thread."</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #000000; font-weight: bold;">final</span> MessageQueue queue <span style="color: #339933;">=</span> me.<span style="color: #006633;">mQueue</span><span style="color: #339933;">;</span>
&nbsp;
  <span style="color: #666666; font-style: italic;">// Make sure the identity of this thread is that of the local process,</span>
  <span style="color: #666666; font-style: italic;">// and keep track of what that identity token actually is.</span>
  Binder.<span style="color: #006633;">clearCallingIdentity</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">long</span> ident <span style="color: #339933;">=</span> Binder.<span style="color: #006633;">clearCallingIdentity</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
  <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">;;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//从消息队列MessageQueue上取下一个消息</span>
      Message msg <span style="color: #339933;">=</span> queue.<span style="color: #006633;">next</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> <span style="color: #666666; font-style: italic;">// might block</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>msg <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #666666; font-style: italic;">// No message indicates that the message queue is quitting.</span>
          <span style="color: #000000; font-weight: bold;">return</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
&nbsp;
      <span style="color: #666666; font-style: italic;">// This must be in a local variable, </span>
      <span style="color: #666666; font-style: italic;">//in case a UI event sets the logger</span>
      Printer logging <span style="color: #339933;">=</span> me.<span style="color: #006633;">mLogging</span><span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>logging <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          logging.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"&gt;&gt;&gt;&gt;&gt; Dispatching to "</span> <span style="color: #339933;">+</span> msg.<span style="color: #006633;">target</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">" "</span> <span style="color: #339933;">+</span>
                  msg.<span style="color: #006633;">callback</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">": "</span> <span style="color: #339933;">+</span> msg.<span style="color: #006633;">what</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
     <span style="color: #666666; font-style: italic;">//调用message关联的Hander对象分发消息</span>
      msg.<span style="color: #006633;">target</span>.<span style="color: #006633;">dispatchMessage</span><span style="color: #009900;">&#40;</span>msg<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>logging <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          logging.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"&lt;&lt;&lt;&lt;&lt; Finished to "</span> <span style="color: #339933;">+</span> msg.<span style="color: #006633;">target</span> 
          <span style="color: #339933;">+</span> <span style="color: #0000ff;">" "</span> <span style="color: #339933;">+</span> msg.<span style="color: #006633;">callback</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
&nbsp;
      <span style="color: #666666; font-style: italic;">// Make sure that during the course of dispatching the</span>
      <span style="color: #666666; font-style: italic;">// identity of the thread wasn't corrupted.</span>
      <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">long</span> newIdent <span style="color: #339933;">=</span> Binder.<span style="color: #006633;">clearCallingIdentity</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>ident <span style="color: #339933;">!=</span> newIdent<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          Log.<span style="color: #006633;">wtf</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Thread identity changed from 0x"</span>
                  <span style="color: #339933;">+</span> <span style="color: #003399;">Long</span>.<span style="color: #006633;">toHexString</span><span style="color: #009900;">&#40;</span>ident<span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">" to 0x"</span>
                  <span style="color: #339933;">+</span> <span style="color: #003399;">Long</span>.<span style="color: #006633;">toHexString</span><span style="color: #009900;">&#40;</span>newIdent<span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">" while dispatching to "</span>
                  <span style="color: #339933;">+</span> msg.<span style="color: #006633;">target</span>.<span style="color: #006633;">getClass</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">" "</span>
                  <span style="color: #339933;">+</span> msg.<span style="color: #006633;">callback</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">" what="</span> <span style="color: #339933;">+</span> msg.<span style="color: #006633;">what</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
&nbsp;
      msg.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

### MessageQueue

负责管理消息队列，实际上Message类有一个next字段，会将Message对象串在一起成为一个消息队列，所以并不需要LinkedList之类的数据结构将Message对象组在一起成为队列。

最重要的方法是next，用于获取下一个Message对象，如果没有需要处理的Message对象，该方法将阻塞。MessageQueue用本地方法做同步互斥，因为这样时间更精准。每个Message对象都有一个什么时刻处理该Message对象的属性when，没到时间都不会处理该Message对象，如果时间不精准的话，会导致系统消息不能及时处理。 源码如下：

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
102
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> Message next<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #000066; font-weight: bold;">int</span> pendingIdleHandlerCount <span style="color: #339933;">=</span> <span style="color: #339933;">-</span><span style="color: #cc66cc;">1</span><span style="color: #339933;">;</span> <span style="color: #666666; font-style: italic;">// -1 only during first iteration</span>
  <span style="color: #000066; font-weight: bold;">int</span> nextPollTimeoutMillis <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
&nbsp;
  <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">;;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>nextPollTimeoutMillis <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          Binder.<span style="color: #006633;">flushPendingCommands</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
      nativePollOnce<span style="color: #009900;">&#40;</span>mPtr, nextPollTimeoutMillis<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
      <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mQuiting<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span> 
          <span style="color: #666666; font-style: italic;">// Try to retrieve the next message.  Return if found.</span>
          <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">long</span> now <span style="color: #339933;">=</span> SystemClock.<span style="color: #006633;">uptimeMillis</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          Message prevMsg <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
          Message msg <span style="color: #339933;">=</span> mMessages<span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>msg <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> msg.<span style="color: #006633;">target</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              <span style="color: #666666; font-style: italic;">// Stalled by a barrier. </span>
              <span style="color: #666666; font-style: italic;">// Find the next asynchronous message in the queue.</span>
              <span style="color: #000000; font-weight: bold;">do</span> <span style="color: #009900;">&#123;</span>
                  prevMsg <span style="color: #339933;">=</span> msg<span style="color: #339933;">;</span>
                  msg <span style="color: #339933;">=</span> msg.<span style="color: #006633;">next</span><span style="color: #339933;">;</span>
              <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>msg <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span>msg.<span style="color: #006633;">isAsynchronous</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>msg <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>now <span style="color: #339933;">&lt;</span> msg.<span style="color: #006633;">when</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #666666; font-style: italic;">// Next message is not ready.  </span>
                <span style="color: #666666; font-style: italic;">//Set a timeout to wake up when it is ready.</span>
                nextPollTimeoutMillis <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span><span style="color: #009900;">&#41;</span> <span style="color: #003399;">Math</span>.<span style="color: #006633;">min</span><span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">when</span> <span style="color: #339933;">-</span> now, 
                           <span style="color: #003399;">Integer</span>.<span style="color: #006633;">MAX_VALUE</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
                  <span style="color: #666666; font-style: italic;">// 获得了一个Message对象，将其返回</span>
                  mBlocked <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
                  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>prevMsg <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                      prevMsg.<span style="color: #006633;">next</span> <span style="color: #339933;">=</span> msg.<span style="color: #006633;">next</span><span style="color: #339933;">;</span>
                  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
                      mMessages <span style="color: #339933;">=</span> msg.<span style="color: #006633;">next</span><span style="color: #339933;">;</span>
                  <span style="color: #009900;">&#125;</span>
                  msg.<span style="color: #006633;">next</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
                  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span> Log.<span style="color: #006633;">v</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"MessageQueue"</span>, <span style="color: #0000ff;">"Returning message: "</span>
                   <span style="color: #339933;">+</span> msg<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                  msg.<span style="color: #006633;">markInUse</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                  <span style="color: #000000; font-weight: bold;">return</span> msg<span style="color: #339933;">;</span>
              <span style="color: #009900;">&#125;</span>
          <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
              <span style="color: #666666; font-style: italic;">// No more messages.</span>
              nextPollTimeoutMillis <span style="color: #339933;">=</span> <span style="color: #339933;">-</span><span style="color: #cc66cc;">1</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
&nbsp;
          <span style="color: #666666; font-style: italic;">// If first time idle, then get the number of idlers to run.</span>
          <span style="color: #666666; font-style: italic;">// Idle handles only run if the queue is empty or </span>
          <span style="color: #666666; font-style: italic;">// if the first message</span>
          <span style="color: #666666; font-style: italic;">// in the queue (possibly a barrier) is due to </span>
          <span style="color: #666666; font-style: italic;">//be handled in the future.</span>
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>pendingIdleHandlerCount <span style="color: #339933;">&lt;</span> <span style="color: #cc66cc;"></span>
                  <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>mMessages <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">||</span> now <span style="color: #339933;">&lt;</span> mMessages.<span style="color: #006633;">when</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              pendingIdleHandlerCount <span style="color: #339933;">=</span> mIdleHandlers.<span style="color: #006633;">size</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>pendingIdleHandlerCount <span style="color: #339933;">&lt;=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              <span style="color: #666666; font-style: italic;">// No idle handlers to run.  Loop and wait some more.</span>
              mBlocked <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
              <span style="color: #000000; font-weight: bold;">continue</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
&nbsp;
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mPendingIdleHandlers <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              mPendingIdleHandlers <span style="color: #339933;">=</span> 
                <span style="color: #000000; font-weight: bold;">new</span> IdleHandler<span style="color: #009900;">&#91;</span><span style="color: #003399;">Math</span>.<span style="color: #006633;">max</span><span style="color: #009900;">&#40;</span>pendingIdleHandlerCount, <span style="color: #cc66cc;">4</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
          mPendingIdleHandlers <span style="color: #339933;">=</span> 
            mIdleHandlers.<span style="color: #006633;">toArray</span><span style="color: #009900;">&#40;</span>mPendingIdleHandlers<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
&nbsp;
      <span style="color: #666666; font-style: italic;">// Run the idle handlers.</span>
      <span style="color: #666666; font-style: italic;">// We only ever reach this code block during the first iteration.</span>
      <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> i <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span> i <span style="color: #339933;">&lt;</span> pendingIdleHandlerCount<span style="color: #339933;">;</span> i<span style="color: #339933;">++</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #000000; font-weight: bold;">final</span> IdleHandler idler <span style="color: #339933;">=</span> mPendingIdleHandlers<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
          <span style="color: #666666; font-style: italic;">// release the reference to the handler</span>
          mPendingIdleHandlers<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span> 
&nbsp;
          <span style="color: #000066; font-weight: bold;">boolean</span> keep <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
              keep <span style="color: #339933;">=</span> idler.<span style="color: #006633;">queueIdle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Throwable</span> t<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              Log.<span style="color: #006633;">wtf</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"MessageQueue"</span>, <span style="color: #0000ff;">"IdleHandler threw exception"</span>, t<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
&nbsp;
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>keep<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                  mIdleHandlers.<span style="color: #006633;">remove</span><span style="color: #009900;">&#40;</span>idler<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              <span style="color: #009900;">&#125;</span>
          <span style="color: #009900;">&#125;</span>
      <span style="color: #009900;">&#125;</span>
&nbsp;
      <span style="color: #666666; font-style: italic;">// Reset the idle handler count to 0 so we do not run them again.</span>
      pendingIdleHandlerCount <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
&nbsp;
      <span style="color: #666666; font-style: italic;">// While calling an idle handler, a new message could have been delivered</span>
      <span style="color: #666666; font-style: italic;">// so go back and look again for a pending message without waiting.</span>
      nextPollTimeoutMillis <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

enqueueMessage用于将Message对象插入消息队列，消息队列的消息是按待处理时间排序的。该方法会被Hander对象调用。源码如下：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">boolean</span> enqueueMessage<span style="color: #009900;">&#40;</span>Message msg, <span style="color: #000066; font-weight: bold;">long</span> when<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">isInUse</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> AndroidRuntimeException<span style="color: #009900;">&#40;</span>msg <span style="color: #339933;">+</span> 
      <span style="color: #0000ff;">" This message is already in use."</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">target</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> AndroidRuntimeException<span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Message must have a target."</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #000066; font-weight: bold;">boolean</span> needWake<span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mQuiting<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #003399;">RuntimeException</span> e <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span>
                  msg.<span style="color: #006633;">target</span> 
                  <span style="color: #339933;">+</span> <span style="color: #0000ff;">" sending message to a Handler on a dead thread"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          Log.<span style="color: #006633;">w</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"MessageQueue"</span>, e.<span style="color: #006633;">getMessage</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, e<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
&nbsp;
      msg.<span style="color: #006633;">when</span> <span style="color: #339933;">=</span> when<span style="color: #339933;">;</span>
      Message p <span style="color: #339933;">=</span> mMessages<span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>p <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">||</span> when <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">||</span> when <span style="color: #339933;">&lt;</span> p.<span style="color: #006633;">when</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #666666; font-style: italic;">// New head, wake up the event queue if blocked.</span>
          msg.<span style="color: #006633;">next</span> <span style="color: #339933;">=</span> p<span style="color: #339933;">;</span>
          mMessages <span style="color: #339933;">=</span> msg<span style="color: #339933;">;</span>
          needWake <span style="color: #339933;">=</span> mBlocked<span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #666666; font-style: italic;">// Inserted within the middle of the queue.  </span>
          <span style="color: #666666; font-style: italic;">//Usually we don't have to wake</span>
          <span style="color: #666666; font-style: italic;">// up the event queue unless there is a barrier </span>
          <span style="color: #666666; font-style: italic;">//at the head of the queue</span>
          <span style="color: #666666; font-style: italic;">// and the message is the earliest asynchronous </span>
          <span style="color: #666666; font-style: italic;">//message in the queue.</span>
          needWake <span style="color: #339933;">=</span> mBlocked <span style="color: #339933;">&&</span> p.<span style="color: #006633;">target</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> msg.<span style="color: #006633;">isAsynchronous</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          Message prev<span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">;;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              prev <span style="color: #339933;">=</span> p<span style="color: #339933;">;</span>
              p <span style="color: #339933;">=</span> p.<span style="color: #006633;">next</span><span style="color: #339933;">;</span>
              <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>p <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">||</span> when <span style="color: #339933;">&lt;</span> p.<span style="color: #006633;">when</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                  <span style="color: #000000; font-weight: bold;">break</span><span style="color: #339933;">;</span>
              <span style="color: #009900;">&#125;</span>
              <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>needWake <span style="color: #339933;">&&</span> p.<span style="color: #006633;">isAsynchronous</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                  needWake <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
              <span style="color: #009900;">&#125;</span>
          <span style="color: #009900;">&#125;</span>
          msg.<span style="color: #006633;">next</span> <span style="color: #339933;">=</span> p<span style="color: #339933;">;</span> <span style="color: #666666; font-style: italic;">// invariant: p == prev.next</span>
          prev.<span style="color: #006633;">next</span> <span style="color: #339933;">=</span> msg<span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>needWake<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      nativeWake<span style="color: #009900;">&#40;</span>mPtr<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

removeMessages系列的方法用于从消息队列里删除消息。

### Message

Message表示消息，它的字段有：

  * 1) <span style="color:red">what</span> 用来区分不同消息，这个是用户自定义的，通常会用常量来区分
  * 2) arg1 arg1 和 arg2 是一种轻量级的传递数据的方式
  * 3) arg2 
  * 4) obj 任意对象，但是使用Messenger跨进程传递Message时不能为null
  * 5) replyTo 可选的Messenger对象，被谁接收
  * 6) flags 一些flag FLAG\_IN\_USE FLAG\_ASYNCHRONOUS FLAGS\_TO\_CLEAR\_ON\_COPY\_FROM的组合
  * 7) <span style="color:red">when</span> 处理Message的时间
  * 8) <span style="color:red">data </span> 携带的bundle格式的数据
  * 9) <span style="color:red">target </span> 关联的Handler对象，处理Message时会调用它分发处理Message对象
  * 10) callback 关联的Runnable对象，Handler分发处理Message时会优先执行callback的run方法
  * 11) <span style="color:red">next</span> Message队列里的下一个Message对象
  * 12) sPoolSync 消息池的同步锁
  * 13) sPool 消息池，创建好的Message对象用完了会放到消息池，下次再次创建Message对象时会从消息池里取出Message对象，只有当消息池没有任何Message对象时才会新建Message对象，这样节省了内存占用。
  * 14) sPoolSize 消息池当前消息个数
管理Message对象时，Android采用了消息池，可以有效节省内存，有两个方法会操作消息池，obtain和recycle，源码如下：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> Message obtain<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span> <span style="color: #666666; font-style: italic;">//获得Message对象</span>
    <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #009900;">&#40;</span>sPoolSync<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sPool <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span> <span style="color: #666666; font-style: italic;">//只要消息池不空，则从消息池里取下一个消息</span>
            Message m <span style="color: #339933;">=</span> sPool<span style="color: #339933;">;</span>
            sPool <span style="color: #339933;">=</span> m.<span style="color: #006633;">next</span><span style="color: #339933;">;</span>
            m.<span style="color: #006633;">next</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
            sPoolSize<span style="color: #339933;">--;</span>
            <span style="color: #000000; font-weight: bold;">return</span> m<span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000000; font-weight: bold;">new</span> Message<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span><span style="color: #666666; font-style: italic;">//若消息池为空，则新建一个Message对象</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> recycle<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    clearForRecycle<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span><span style="color: #666666; font-style: italic;">//将消息携带的所有数据清空</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #009900;">&#40;</span>sPoolSync<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span><span style="color: #666666; font-style: italic;">//将消息回收到消息池</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sPoolSize <span style="color: #339933;">&lt;</span> MAX_POOL_SIZE<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            next <span style="color: #339933;">=</span> sPool<span style="color: #339933;">;</span>
            sPool <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">this</span><span style="color: #339933;">;</span>
            sPoolSize<span style="color: #339933;">++;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

Message的静态obtain系列方法都会调用上述的obtain方法来获取Message对象，而Handeler的obtainMessage系列方法都是调用Message的静态obtain系列方法来获得Message对象，故此可知Android会重复利用Message对象，从而节省了内存。

### Handler

我们平常都不怎么接触Looper类和MessageQueue类，但是经常使用Handler。我们对Looper类和MessageQueue知之甚少，甚至不知道Handler如何和Looper对象以及MessageQueue对象关联的。这是因为使用了Thread Specifical Pattern的缘故，在某个线程里只需调用Looper.prepare或者Looper. prepareMainLooper方法即可为该线程建立Looper对象和MessageQueue对象，当前线程也只需要调用Looper.myLooper即可得到当前线程的Looper对象。

创建Handler对象时，会先获得当前线程的Looper对象，以及looper对象关联的消息队列，并让自己对应的字段引用这些对象，源码如下所示：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> Handler<span style="color: #009900;">&#40;</span>Callback callback, <span style="color: #000066; font-weight: bold;">boolean</span> async<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>FIND_POTENTIAL_LEAKS<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">final</span> Class<span style="color: #339933;">&lt;?</span> <span style="color: #000000; font-weight: bold;">extends</span> Handler<span style="color: #339933;">&gt;</span> klass <span style="color: #339933;">=</span> getClass<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>klass.<span style="color: #006633;">isAnonymousClass</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">||</span> klass.<span style="color: #006633;">isMemberClass</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">||</span> klass.<span style="color: #006633;">isLocalClass</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&&</span>
                <span style="color: #009900;">&#40;</span>klass.<span style="color: #006633;">getModifiers</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&</span> <span style="color: #003399;">Modifier</span>.<span style="color: #000000; font-weight: bold;">STATIC</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            Log.<span style="color: #006633;">w</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"The following Handler class should be static"</span>
                <span style="color: #339933;">+</span><span style="color: #0000ff;">" or leaks might occur: "</span> <span style="color: #339933;">+</span>
                klass.<span style="color: #006633;">getCanonicalName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span> 
    mLooper <span style="color: #339933;">=</span> Looper.<span style="color: #006633;">myLooper</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mLooper <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span>
            <span style="color: #0000ff;">"Can't create handler inside thread "</span>
            <span style="color: #339933;">+</span><span style="color: #0000ff;">"that has not called Looper.prepare()"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    mQueue <span style="color: #339933;">=</span> mLooper.<span style="color: #006633;">mQueue</span><span style="color: #339933;">;</span>
    mCallback <span style="color: #339933;">=</span> callback<span style="color: #339933;">;</span>
    mAsynchronous <span style="color: #339933;">=</span> async<span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

我们通常会象下面这样使用Handler：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">Handler h <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Handler<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
	@Override
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> handleMessage<span style="color: #009900;">&#40;</span>Message msg<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">switch</span> <span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">what</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">case</span> TEST<span style="color: #339933;">:</span>
&nbsp;
			<span style="color: #000000; font-weight: bold;">break</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span>
	<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span><span style="color: #339933;">;</span>
h.<span style="color: #006633;">sendEmptyMessage</span><span style="color: #009900;">&#40;</span>h. <span style="color: #006633;">obtainMessage</span><span style="color: #009900;">&#40;</span>TEST<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

调用Handler的sendMessage系列方法时，会调用MessageQueue的enqueueMessage方法将Message插入到消息队列，Looper的loop方法会从MessageQueue里取出Message对象，并调用与其关联的Handler对象的dispatchMessage方法分发处理该Message对象。dispatchMessage方法的源码如下所示：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> dispatchMessage<span style="color: #009900;">&#40;</span>Message msg<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>msg.<span style="color: #006633;">callback</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span> <span style="color: #666666; font-style: italic;">//优先执行Message的callback回调</span>
        handleCallback<span style="color: #009900;">&#40;</span>msg<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//如果Handler有与其关联的callback，则调用callback的handleMessage方法</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mCallback <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>z
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mCallback.<span style="color: #006633;">handleMessage</span><span style="color: #009900;">&#40;</span>msg<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">return</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #666666; font-style: italic;">//我们通常会覆盖handleMessage方法，在该方法里写处理消息的逻辑</span>
        handleMessage<span style="color: #009900;">&#40;</span>msg<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

注意Handler类的obtainMessage系列方法其实是调用Message的静态obtain系列方法生成Message对象。

### Messenger

引用了一个Handler对象，其它地方可以用Messenger来发送消息给这个Handler。利用这点可以实现跨进程的基于消息的通信，如果创建了一个 指向某个进程A的Handler对象 的Messenger对象，并把该Messenger对象传递给另外一个进程B，那么进程B就可以发送消息给进程A了。

## 时序图

Looper准备好并进入死循环的时序图如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/loop-prepare-loop.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/loop-prepare-loop.png" alt="loop prepare loop" width="700" height="536" class="alignnone size-full wp-image-408" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/loop-prepare-loop.png 700w, http://www.cloudchou.com/wp-content/uploads/2014/04/loop-prepare-loop-300x229.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/loop-prepare-loop-195x150.png 195w" sizes="(max-width: 700px) 100vw, 700px" /></a>

Handler创建时的时序图如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-create.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-create.png" alt="Handler create" width="427" height="342" class="alignnone size-full wp-image-407" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-create.png 427w, http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-create-300x240.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-create-187x150.png 187w" sizes="(max-width: 427px) 100vw, 427px" /></a>

Handler创建消息并发送消息，然后Looper处理消息的时序图如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-send-message.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-send-message.png" alt="Handler  send message" width="862" height="758" class="alignnone size-full wp-image-410" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-send-message.png 862w, http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-send-message-300x263.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-send-message-170x150.png 170w" sizes="(max-width: 862px) 100vw, 862px" /></a>