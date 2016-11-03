---
id: 596
title: Android Binder总结
date: 2014-06-09T23:11:30+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=596
permalink: /android/post-596.html
views:
  - 5851
categories:
  - Android
tags:
  - android binder example
  - android binder service
  - android binder 分析
  - android binder 实例
  - android binder 设计与实现
---
<p>从前面的博客中我们已经学习到如何使用binder，也学习到binder的框架及原理。今天就聊聊我对android为什么使用binder作为最重要的IPC机制这个问题的想法，并总结一下先前的android binder相关博客。</p>


<p>binder其实不是android首先提出来的IPC机制，它是基于OpenBinder来实现的。OpenBinder有许可问题，andriod不能直接使用，故此重新开发了自己的一套binder实现，基于宽松的Apache协议发布，架构与OpenBinder类似，相关信息可以参考: <a href="http://www.open-binder.org" target="_blank">http://www.open-binder.org</a>。</p>
<h2>Android为什么选用Binder作为最重要的IPC机制</h2>
<p>我们知道在Linux系统中，进程间的通信方式有socket，named pipe，message queue，signal，sharememory等。这几种通信方式的优缺点如下：</p>
<ul>
<li>1)named pipe: 任何进程都能通讯，但速度慢</li>
<li>2)message queue: 容量受到系统限制，且要注意第一次读的时候，要考虑上一次没有读完数据的问题</li>
<li>3)signal: 不能传递复杂消息，只能用来同步</li>
<li>4)shared memory: 能够很容易控制容量，速度快，但要保持同步，比如一个进程在写的时候，另一个进程要注意读写的问题，相当于线程中的线程安全，当然，共享内存同样可以作为线程通讯，不过没这个必要，线程间本来就已经共享了同一进程内的一块内存。</li>
<li>5)socket：本机进程之间可以利用socket通信，跨主机之间也可利用socket通信，通常rpc的实现最底层都是通过socket通信。socket通信是一种比较复杂的通信方式，通常客户端需要开启单独的监听线程来接收从服务端发送过来的数据，客户端线程发送数据给服务端后，如果需要等待服务端的响应，并通过监听线程接收数据，需要进行同步，是一件很麻烦的事情。socket通信速度也不快。</li>
</ul>
<p>Android中属性服务的实现和vold服务的实现采用了socket，getprop和setprop等命令都是通过socket和init进程通信来获得属性或者设置属性，vdc命令和mount service也是通过socket和vold服务通信来操作外接设备，比如sd卡。</p>
<p>message queue允许任意进程共享消息队列实现进程间通信，并由内核负责消息发送和接收之间的同步，从而使得用户在使用消息队列进行通信时不再需要考虑同步问题。这样使用方便，但是信息的复制需要额外消耗CPU时间，不适合信息量大或者操作频繁的场合。共享内存针对消息缓冲的缺点改而利用内存缓冲区直接交换信息，无须复制，快速，信息量大是其优点。</p>
<p>共享内存块提供了在任意数量的进程之间进行高效双向通信的机制，每个使用者都可以读取写入数据，但是所有程序之间必须达成并遵守一定的协议，以防止诸如在读取信息之前覆盖内存空间等竞争状态的实现。不幸的是，Linux无法严格保证对内存块的独占访问，甚至是您通过使用IPC_PRIVATE创建新的共享内存块的时候，也不能保证访问的独占性。同时，多个使用共享内存块的进程之间必须协调使用同一个键值。</p>
<p>Android应用程序开发者开发应用程序时，对系统框架的进程和线程运作机制不必了解，只需要利用四大组件开发，Android应用开发时可以轻易调用别的软件提供的功能，甚至可以调用系统App，在Android的世界里，所有应用生而平等，但实质上应用进程被隔离在不同的沙盒里。</p>
<p>Android平台的进程之间需要频繁的通信，比如打开一个应用便需要Home应用程序进程和运行在system_server进程里的AcitivityManagerService通信才能打开。正是由于Android平台的进程需要非常频繁的通信，故此对进程间通信机制要求比较高，速度要快，还要能进行复杂数据的交换，应用开发时应尽可能简单，并能提供同步调用。虽然共享内存的效率高，但是它需要复杂的同步机制，使用时很麻烦，故此不能采用。binder能满足这些要求，所以Android选择了binder作为最核心的进程间通信方式。binder主要提供以下一些功能：</p>
<ul>
<li>1)用驱动程序来推进进程间的通信方式</li>
<li>2)通过共享内存来提高性能</li>
<li>3)为进程请求分配每个进程的线程池，每个应用进程默认启动两个binder服务线程</li>
<li>4)针对系统中的对象引入了引用技术和跨进程的对象引用映射</li>
<li>5)进程间同步调用。</li>
</ul>
<h2>Binder入门和详解系列博客汇总</h2>
<p>《service manager和binder service的关系》</p>
<p><a href="http://www.cloudchou.com/android/post-327.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-327.html</a></p>
<p>阐述了servicemanager和binder service的关系，并说明了servicemananger,binder service的服务端，客户端程序运行时各自所在进程</p> 
<p>《Binder service入门–创建native binder service》</p>
<p><a href="http://www.cloudchou.com/android/post-332.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-332.html</a></p>
<p>用实例说明如何创建native binder service的服务端和客户端，并说明了如何编译以及运行程序，代码在github上可下载。</p> 
<p>《Binder service入门—Framework binder service》</p>
<p><a href="http://www.cloudchou.com/android/post-447.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-447.html</a></p>
<p>用实例说明如何创建framework层 binder service的服务端和客户端，并说明了如何编译以及运行程序，代码在github上可下载</p> 
<p>《Binder service入门—应用层binder service》</p>
<p><a href="http://www.cloudchou.com/android/post-458.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-458.html</a></p>
<p>用实例说明如何创建应用层binder service的服务端和客户端，并说明了如何编译以及运行程序，代码在github上可下载</p> 
<p>《Binder service入门—框架层、应用层调用native binder service》</p>
<p><a href="http://www.cloudchou.com/android/post-468.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-468.html</a></p>
<p>综合运用了前面几篇博客的知识，用实例说明了如何在框架层，应用层调用native binder service，所有代码均可在github上下载</p> 
<p>《Binder 机制详解—Binder IPC 程序结构》</p>
<p><a href="http://www.cloudchou.com/android/post-497.html" target="_blank" style="padding-left: 10px;"></a>http://www.cloudchou.com/android/post-497.html</p>
<p>从本篇博客开始分析binder机制，简单介绍了binder机制运行时服务端，客户端和servicemananger的关系</p> 
<p>《Binder 机制详解—Binder 系统架构》</p>
<p><a href="http://www.cloudchou.com/android/post-507.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-507.html</a></p>
<p>分析了Binder系统架构，层次划分，并着重分析了Binder Adaper层和Binder的核心部分</p> 
<p>《本地Binder框架通信原理》</p>
<p><a href="http://www.cloudchou.com/android/post-534.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-534.html</a></p>
<p>分析了binder本地框架通信原理，主要就两个重要函数调用流程进行分析，分析了如何获得servicemananger的IBinder指针，还分析了客户端如何获得IBinder指针</p> 
<p>《Binder 机制详解—Binder 本地框架》</p>
<p><a href="http://www.cloudchou.com/android/post-547.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-547.html</a></p>
<p>分析了Binder本地框架各个类之间的关系，以及IServiceManager相关类之间的关系</p> 
<p>《Binder 机制详解—Binder Java框架》</p>
<p><a href="http://www.cloudchou.com/android/post-558.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-558.html</a></p>
<p>分析了Binder Java框架各个类之间的关系，并分析了Binder java框架的相关Jni源码，给出了Java层Binder,BinderProxy，Parcel和本地的BnBinder，BpBinder，Parcel之间的关系。</p> 
<p>《Java层Binder框架通信原理》</p>
<p><a href="http://www.cloudchou.com/android/post-573.html" target="_blank" style="padding-left: 10px;">http://www.cloudchou.com/android/post-573.html</a></p>
<p>分析了Java层Binder框架通信原理，主要分析了Java层如何获得IServiceManager对象，和Java层如何获得IBinder接口对象，还分析了Java层binder的数据流动</p> 
<h2>参考资料</h2>
<p>《Android技术内幕—系统卷》 第3章 Android的IPC机制—Binder</p>
