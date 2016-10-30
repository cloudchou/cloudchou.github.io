---
id: 507
title: Binder 机制详解—Binder 系统架构
date: 2014-05-20T22:50:54+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=507
permalink: /android/post-507.html
views:
  - 12990
categories:
  - Android
tags:
  - android service binder
  - binder service
  - binder机制
  - binder机制详解
  - binder系统架构
---
前一篇博客介绍了Binder IPC程序结构，本篇将从架构角度分析binder, 介绍<a href="http://www.cloudchou.com/tag/binder%e6%9c%ba%e5%88%b6" title="View all posts in binder机制" target="_blank" class="tags">binder机制</a>的层次划分,并着重分析驱动适配层和Binder核心框架层。

## Binder层次划分

Binder层次划分如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/binder-layer.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/binder-layer.jpg" alt="binder layer" width="330" height="290" class="aligncenter size-full wp-image-514" srcset="http://www.cloudchou.com/wp-content/uploads/2014/05/binder-layer.jpg 330w, http://www.cloudchou.com/wp-content/uploads/2014/05/binder-layer-300x263.jpg 300w, http://www.cloudchou.com/wp-content/uploads/2014/05/binder-layer-170x150.jpg 170w" sizes="(max-width: 330px) 100vw, 330px" /></a>

  * ### (1) 驱动层
    
    正如大家所知道的，Binder机制是需要Linux内核支持的，Android因此添加了binder驱动，binder 设备节点为/dev/binder，主设备号为10，binder 驱动程序在内核中的头文件和代码路径如下：
    
    kernel/drivers/staging/binder.h
    
    kernel/drivers/staging/binder.c
    
    binder驱动程序的主要作用是完成实际的binder数据传输。
    
    驱动实现时，主要通过binder\_ioctl函数与用户空间的进程交换数据(用户进程与驱动交互时使用ioctl函数，对应驱动源码的binder\_ioctl函数)。BINDDER\_WRITE\_READ命令字用来读写数据，数据包中有一个cmd域用于区分不同的请求。binder\_thread\_write函数用于发送请求，binder\_thread\_read函数用于读取结果。在binder\_thread\_write函数中调用binder\_transaction函数来转发请求并返回结果。当收到请求时，binder\_transaction函数会根据对象的handle找到对象所在的进程，如果handle为0，则认为对象是context\_mgr，把请求发给context\_mgr所在的进程。所有的binder请求对象全部放到一个RB树中，最后把请求放到目标进程的队列中，等待目标进程读取。
    
    A进程如果要使用B进程的服务，B进程首先要注册此服务，A进程通过service mananger获取该服务的handle，通过这个handle，A进程就可以使用该服务了。A进程使用B进程的服务还意味着二者遵循相同的协议，这个协议反映在代码上就是二者要实现IBinder接口。
    
    Binder的本质就是要把对象a从一个进程B映射到另一个进程A中，进程A中调用对象a的方法象调本地方法一样。但实际上进程B和进程A有不同的地址空间，对象a只有在进程B里有意义，但是驱动层可将进程B的对象a映射到进程A，得到对象a在进程A的表示，称之为handle，也叫句柄。这样，对象a在进程B的地址空间里有一个实际地址，在进程A里有对应的句柄，驱动会将这个句柄和对象a的实际地址映射起来。对象a对于进程B来说是本地对象，对象a对于进程A来说是远程对象，而handle对于进程A来说是对象a在进程A的引用。
    
    适配层使用binder驱动时使用了内存映射技术，故此进程间传输数据时只需拷贝一次，传统的IPC需拷贝两次，因此使用binder可大大提高IPC通信效率。

  * ### (2) 驱动适配层
    
    主要是IPCThreadState.cpp和ProcessState.cpp,源码位于frameworks/native/libs/binder
    
    这两个类都采用了单例模式，主要负责和驱动直接交互。
    
    ProcessState负责打开binder设备，进行一些初始化设置并做内存映射
    
    IPCThreadState负责直接和binder设备通信，使用ioctl读写binder驱动数据
    
    后面将详细分析ProcessState和IPCThreadState。

  * ### (3) Binder核心框架层
    
    Binder核心框架主要是IBinder及它的两个子类，即BBinder和BpBinder，分别代表了最基本的服务端及客户端。
    
    <a href="http://www.cloudchou.com/tag/binder-service" title="View all posts in binder service" target="_blank" class="tags">binder service</a>服务端实体类会继承BnInterface，而BnInterface会继承自BBinder，服务端可将BBinder对象注册到servicemananger进程。
    
    客户端程序和驱动交互时只能得到远程对象的句柄handle，它可以调用调用ProcessState的getStrongProxyForHandle函数，利用句柄handle建立BpBinder对象，然后将它转为IBinder指针返回给调用者。这样客户端每次调用IBinder指针的transact方法，其实是执行BpBinder的transact方法。

  * ### (4) Binder框架层
    
    本地Binder框架层包含以下类(frameworks/native/libs/binder)：
    
    RefBase，IInterface，BnInterface，BpInterface，BpRefBase，Parcel 等等
    
    Java框架层包含以下类(frameworks/base/core/java/android/os):
    
    IBinder，Binder，IInterface，ServiceManagerNative，ServiceManager，BinderInternal，IServiceManager，ServiceManagerProxy
    
    Java框架层的类的部分方法的实现在本地代码里(frameworks/base/core/jni)。
    
    后续博客会详细分析本地binder框架和Java层 binder框架各自的类关系。

  * ### (5) Binder 服务和客户端实现
    
    从Binder入门系列我们也知道，binder service服务端和binder 客户端都有native和Java之分，Java层服务端从Binder继承并实现服务接口，Java层客户端直接实现服务接口即可，而本地服务端需继承自BnInterface，本地客户端继承自BpInterface。
    
    后续博客分析本地binder框架和Java层 binder框架时会给出更详尽的类关系。

## ProcessState

ProcessState负责打开binder设备，进行一些初始化设置。

ProcessState的类图如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/processstate.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/processstate.png" alt="processstate" width="511" height="636" class="aligncenter size-full wp-image-523" srcset="http://www.cloudchou.com/wp-content/uploads/2014/05/processstate.png 511w, http://www.cloudchou.com/wp-content/uploads/2014/05/processstate-241x300.png 241w, http://www.cloudchou.com/wp-content/uploads/2014/05/processstate-120x150.png 120w" sizes="(max-width: 511px) 100vw, 511px" /></a>

我们通常在binder service的服务端象下面一样使用ProcessState:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #666666;">//初始化单例，其实不调用该语句也能正常运行</span>
sp <span style="color: #000080;">&lt;</span> ProcessState <span style="color: #000080;">&gt;</span> proc<span style="color: #008000;">&#40;</span>ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #666666;">//启动线程池</span>
ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>startThreadPool<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

注意binder service服务端提供binder service时，是以线程池的形式提供服务，也就说可以同时启动多个线程来提供服务，可以通过如下方式来启动多个线程：

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
        <pre class="cpp" style="font-family:monospace;"><span style="color: #666666;">//设置线程池支持的最大线程个数</span>
ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>setThreadPoolMaxThreadCount<span style="color: #008000;">&#40;</span><span style="color: #0000dd;">4</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #666666;">//启动一个服务线程</span>
ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>spawnPooledThread<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">false</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #666666;">//启动一个服务线程</span>
ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>spawnPooledThread<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">false</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

接下来我们分析ProcessState的构造函数：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;">ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">ProcessState</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>
    <span style="color: #008080;">:</span> mDriverFD<span style="color: #008000;">&#40;</span>open_driver<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span> <span style="color: #666666;">//打开binder设备，并将mDriverFD设置为打开的文件符</span>
    , mVMStart<span style="color: #008000;">&#40;</span>MAP_FAILED<span style="color: #008000;">&#41;</span>
    , mManagesContexts<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">false</span><span style="color: #008000;">&#41;</span>
    , mBinderContextCheckFunc<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span>
    , mBinderContextUserData<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span>
    , mThreadPoolStarted<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">false</span><span style="color: #008000;">&#41;</span> <span style="color: #666666;">//构造时，默认并未启动线程池</span>
    , mThreadPoolSeq<span style="color: #008000;">&#40;</span><span style="color: #0000dd;">1</span><span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>mDriverFD <span style="color: #000080;">&gt;=</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #666666;">// XXX Ideally, there should be a specific define for whether we</span>
        <span style="color: #666666;">// have mmap (or whether we could possibly have the kernel module</span>
        <span style="color: #666666;">// availabla).</span>
<span style="color: #339900;">#if !defined(HAVE_WIN32_IPC)</span>
        <span style="color: #666666;">// mmap the binder, providing a chunk of virtual address space </span>
        <span style="color: #666666;">// to receive transactions.</span>
        <span style="color: #666666;">//内存映射 </span>
        mVMStart <span style="color: #000080;">=</span> mmap<span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span>, BINDER_VM_SIZE, PROT_READ, 
                        MAP_PRIVATE <span style="color: #000040;">|</span> MAP_NORESERVE, mDriverFD, <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>mVMStart <span style="color: #000080;">==</span> MAP_FAILED<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            <span style="color: #666666;">// *sigh*</span>
            ALOGE<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Using /dev/binder failed: unable to 
                     mmap transaction memory.<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            close<span style="color: #008000;">&#40;</span>mDriverFD<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            mDriverFD <span style="color: #000080;">=</span> <span style="color: #000040;">-</span><span style="color: #0000dd;">1</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
<span style="color: #339900;">#else</span>
        mDriverFD <span style="color: #000080;">=</span> <span style="color: #000040;">-</span><span style="color: #0000dd;">1</span><span style="color: #008080;">;</span>
<span style="color: #339900;">#endif</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    LOG_ALWAYS_FATAL_IF<span style="color: #008000;">&#40;</span>mDriverFD <span style="color: #000080;">&lt;</span> <span style="color: #0000dd;"></span>, <span style="color: #FF0000;">"Binder driver 
                               could not be opened.  Terminating."</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

open_driver的实现：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">static</span> <span style="color: #0000ff;">int</span> open_driver<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">int</span> fd <span style="color: #000080;">=</span> open<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"/dev/binder"</span>, O_RDWR<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span> <span style="color: #666666;">//打开binder设备</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>fd <span style="color: #000080;">&gt;=</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        fcntl<span style="color: #008000;">&#40;</span>fd, F_SETFD, FD_CLOEXEC<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">int</span> vers<span style="color: #008080;">;</span>
        <span style="color: #666666;">//检查版本</span>
        status_t result <span style="color: #000080;">=</span> ioctl<span style="color: #008000;">&#40;</span>fd, BINDER_VERSION, <span style="color: #000040;">&</span>vers<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>result <span style="color: #000080;">==</span> <span style="color: #000040;">-</span><span style="color: #0000dd;">1</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            ALOGE<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Binder ioctl to obtain version failed: %s"</span>, 
                            <span style="color: #0000dd;">strerror</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">errno</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            close<span style="color: #008000;">&#40;</span>fd<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            fd <span style="color: #000080;">=</span> <span style="color: #000040;">-</span><span style="color: #0000dd;">1</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>result <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000dd;"></span> <span style="color: #000040;">||</span> vers <span style="color: #000040;">!</span><span style="color: #000080;">=</span> BINDER_CURRENT_PROTOCOL_VERSION<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            ALOGE<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Binder driver protocol does not match 
                              user space protocol!"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            close<span style="color: #008000;">&#40;</span>fd<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            fd <span style="color: #000080;">=</span> <span style="color: #000040;">-</span><span style="color: #0000dd;">1</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        <span style="color: #666666;">//默认设置支持的线程数是15</span>
        <span style="color: #0000ff;">size_t</span> maxThreads <span style="color: #000080;">=</span> <span style="color: #0000dd;">15</span><span style="color: #008080;">;</span>
        result <span style="color: #000080;">=</span> ioctl<span style="color: #008000;">&#40;</span>fd, BINDER_SET_MAX_THREADS, <span style="color: #000040;">&</span>maxThreads<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>result <span style="color: #000080;">==</span> <span style="color: #000040;">-</span><span style="color: #0000dd;">1</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            ALOGE<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Binder ioctl to set max threads failed: %s"</span>,
                           <span style="color: #0000dd;">strerror</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">errno</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #008000;">&#123;</span>
        ALOGW<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Opening '/dev/binder' failed: %s<span style="color: #000099; font-weight: bold;">\n</span>"</span>, <span style="color: #0000dd;">strerror</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">errno</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
    <span style="color: #0000ff;">return</span> fd<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

startThreadPool的实现(用于启动线程池)：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">void</span> ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">startThreadPool</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    AutoMutex _l<span style="color: #008000;">&#40;</span>mLock<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #000040;">!</span>mThreadPoolStarted<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        mThreadPoolStarted <span style="color: #000080;">=</span> <span style="color: #0000ff;">true</span><span style="color: #008080;">;</span>
        spawnPooledThread<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">true</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

spawnPooledThread的实现：

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
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">void</span> ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">spawnPooledThread</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">bool</span> isMain<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>mThreadPoolStarted<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000ff;">int32_t</span> s <span style="color: #000080;">=</span> android_atomic_add<span style="color: #008000;">&#40;</span><span style="color: #0000dd;">1</span>, <span style="color: #000040;">&</span>mThreadPoolSeq<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">char</span> buf<span style="color: #008000;">&#91;</span><span style="color: #0000dd;">16</span><span style="color: #008000;">&#93;</span><span style="color: #008080;">;</span>
        <span style="color: #0000dd;">snprintf</span><span style="color: #008000;">&#40;</span>buf, <span style="color: #0000dd;">sizeof</span><span style="color: #008000;">&#40;</span>buf<span style="color: #008000;">&#41;</span>, <span style="color: #FF0000;">"Binder_%X"</span>, s<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        ALOGV<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Spawning new pooled thread, name=%s<span style="color: #000099; font-weight: bold;">\n</span>"</span>, buf<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #666666;">//PoolThread也在ProcessState里实现</span>
        sp<span style="color: #000080;">&lt;</span>Thread<span style="color: #000080;">&gt;</span> t <span style="color: #000080;">=</span> <span style="color: #0000dd;">new</span> PoolThread<span style="color: #008000;">&#40;</span>isMain<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #666666;">//启动线程,buf是新线程的名字</span>
        t<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>run<span style="color: #008000;">&#40;</span>buf<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

PoolThread继承自Thread类，Thread类是框架层提供的一个类，和Java的Thread类相似，使用PoolThread类时需实现threadLoop函数(Java使用Thread类时需覆盖run方法)，新线程执行threadLoop函数，启动新线程需调用PoolThread对象的run方法(Java中调用start方法)。

PoolThread类的源码如下所示：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">class</span> PoolThread <span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> Thread
<span style="color: #008000;">&#123;</span>
<span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
    PoolThread<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">bool</span> isMain<span style="color: #008000;">&#41;</span>
        <span style="color: #008080;">:</span> mIsMain<span style="color: #008000;">&#40;</span>isMain<span style="color: #008000;">&#41;</span>
    <span style="color: #008000;">&#123;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
<span style="color: #0000ff;">protected</span><span style="color: #008080;">:</span>
    <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">bool</span> threadLoop<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #666666;">//加入线程池</span>
        IPCThreadState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>joinThreadPool<span style="color: #008000;">&#40;</span>mIsMain<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">return</span> <span style="color: #0000ff;">false</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">bool</span> mIsMain<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

## IPCThreadState

IPCThreadState负责直接和binder设备通信，从binder驱动读取数据，并向binder驱动写数据。

IPCThreadState也采用了单例模式。

IPCThreadState类图如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/IPCThreadState.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/IPCThreadState.png" alt="IPCThreadState" width="607" height="704" class="aligncenter size-full wp-image-525" srcset="http://www.cloudchou.com/wp-content/uploads/2014/05/IPCThreadState.png 607w, http://www.cloudchou.com/wp-content/uploads/2014/05/IPCThreadState-258x300.png 258w, http://www.cloudchou.com/wp-content/uploads/2014/05/IPCThreadState-129x150.png 129w" sizes="(max-width: 607px) 100vw, 607px" /></a>

我们通常在binder service的服务端象下面一样使用IPCThreadState:

IPCThreadState::self()->joinThreadPool();

IPCThreadState joinThreadPool的函数原型：

void joinThreadPool(bool isMain = true);

IPCThreadState的构造函数实现：

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
        <pre class="cpp" style="font-family:monospace;">IPCThreadState<span style="color: #008080;">::</span><span style="color: #007788;">IPCThreadState</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>
    <span style="color: #008080;">:</span> mProcess<span style="color: #008000;">&#40;</span>ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span>,
      mMyThreadId<span style="color: #008000;">&#40;</span>androidGetTid<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span>,
      mStrictModePolicy<span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span>,
      mLastTransactionBinderFlags<span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    pthread_setspecific<span style="color: #008000;">&#40;</span>gTLS, <span style="color: #0000dd;">this</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    clearCaller<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    mIn.<span style="color: #007788;">setDataCapacity</span><span style="color: #008000;">&#40;</span><span style="color: #0000dd;">256</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    mOut.<span style="color: #007788;">setDataCapacity</span><span style="color: #008000;">&#40;</span><span style="color: #0000dd;">256</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

joinThreadPool的函数实现如下所示：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">void</span> IPCThreadState<span style="color: #008080;">::</span><span style="color: #007788;">joinThreadPool</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">bool</span> isMain<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    LOG_THREADPOOL<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"**** THREAD %p (PID %d) IS JOINING THE THREAD POOL<span style="color: #000099; font-weight: bold;">\n</span>"</span>,
                       <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">void</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>pthread_self<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>, getpid<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span>isMain <span style="color: #008080;">?</span> BC_ENTER_LOOPER <span style="color: #008080;">:</span> BC_REGISTER_LOOPER<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #666666;">// This thread may have been spawned by a thread that was </span>
    <span style="color: #666666;">// in the background scheduling group, so first we will </span>
    <span style="color: #666666;">//make sure it is in the foreground</span>
    <span style="color: #666666;">// one to avoid performing an initial transaction in the background.</span>
    set_sched_policy<span style="color: #008000;">&#40;</span>mMyThreadId, SP_FOREGROUND<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    status_t result<span style="color: #008080;">;</span>
    <span style="color: #0000ff;">do</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000ff;">int32_t</span> cmd<span style="color: #008080;">;</span>
&nbsp;
        <span style="color: #666666;">// When we've cleared the incoming command queue, </span>
        <span style="color: #666666;">//process any pending derefs</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>mIn.<span style="color: #007788;">dataPosition</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">&gt;=</span> mIn.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            <span style="color: #0000ff;">size_t</span> numPending <span style="color: #000080;">=</span> mPendingWeakDerefs.<span style="color: #007788;">size</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>numPending <span style="color: #000080;">&gt;</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                <span style="color: #0000ff;">for</span> <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">size_t</span> i <span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span> i <span style="color: #000080;">&lt;</span> numPending<span style="color: #008080;">;</span> i<span style="color: #000040;">++</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                    RefBase<span style="color: #008080;">::</span><span style="color: #007788;">weakref_type</span><span style="color: #000040;">*</span> refs <span style="color: #000080;">=</span> mPendingWeakDerefs<span style="color: #008000;">&#91;</span>i<span style="color: #008000;">&#93;</span><span style="color: #008080;">;</span>
                    refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>decWeak<span style="color: #008000;">&#40;</span>mProcess.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #008000;">&#125;</span>
                mPendingWeakDerefs.<span style="color: #007788;">clear</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
&nbsp;
            numPending <span style="color: #000080;">=</span> mPendingStrongDerefs.<span style="color: #007788;">size</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>numPending <span style="color: #000080;">&gt;</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                <span style="color: #0000ff;">for</span> <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">size_t</span> i <span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span> i <span style="color: #000080;">&lt;</span> numPending<span style="color: #008080;">;</span> i<span style="color: #000040;">++</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                    BBinder<span style="color: #000040;">*</span> obj <span style="color: #000080;">=</span> mPendingStrongDerefs<span style="color: #008000;">&#91;</span>i<span style="color: #008000;">&#93;</span><span style="color: #008080;">;</span>
                    obj<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>decStrong<span style="color: #008000;">&#40;</span>mProcess.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #008000;">&#125;</span>
                mPendingStrongDerefs.<span style="color: #007788;">clear</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
        <span style="color: #008000;">&#125;</span>
&nbsp;
        <span style="color: #666666;">// now get the next command to be processed, waiting if necessary</span>
        <span style="color: #666666;">//跟驱动交互 获取数据 或者写入数据</span>
        result <span style="color: #000080;">=</span> talkWithDriver<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>result <span style="color: #000080;">&gt;=</span> NO_ERROR<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            <span style="color: #0000ff;">size_t</span> IN <span style="color: #000080;">=</span> mIn.<span style="color: #007788;">dataAvail</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>IN <span style="color: #000080;">&lt;</span> <span style="color: #0000dd;">sizeof</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int32_t</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">continue</span><span style="color: #008080;">;</span>
            <span style="color: #666666;">//获取命令</span>
            cmd <span style="color: #000080;">=</span> mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            IF_LOG_COMMANDS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"Processing top-level Command: "</span>
                    <span style="color: #000080;">&lt;&lt;</span> getReturnString<span style="color: #008000;">&#40;</span>cmd<span style="color: #008000;">&#41;</span> <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
&nbsp;
            <span style="color: #666666;">//执行命令</span>
            result <span style="color: #000080;">=</span> executeCommand<span style="color: #008000;">&#40;</span>cmd<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
&nbsp;
  <span style="color: #666666;">// After executing the command, ensure that the thread is returned to the</span>
  <span style="color: #666666;">// foreground cgroup before rejoining the pool.  The driver takes care of</span>
  <span style="color: #666666;">// restoring the priority, but doesn't do anything with cgroups so we</span>
  <span style="color: #666666;">// need to take care of that here in userspace.  Note that we do make</span>
  <span style="color: #666666;">// sure to go in the foreground after executing a transaction, but</span>
  <span style="color: #666666;">// there are other callbacks into user code that could have changed</span>
  <span style="color: #666666;">// our group so we want to make absolutely sure it is put back.</span>
        set_sched_policy<span style="color: #008000;">&#40;</span>mMyThreadId, SP_FOREGROUND<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
        <span style="color: #666666;">// Let this thread exit the thread pool if it is no longer</span>
        <span style="color: #666666;">// needed and it is not the main process thread.</span>
        <span style="color: #0000ff;">if</span><span style="color: #008000;">&#40;</span>result <span style="color: #000080;">==</span> TIMED_OUT <span style="color: #000040;">&&</span> <span style="color: #000040;">!</span>isMain<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">while</span> <span style="color: #008000;">&#40;</span>result <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #000040;">-</span>ECONNREFUSED <span style="color: #000040;">&&</span> result <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #000040;">-</span>EBADF<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    LOG_THREADPOOL<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"**** THREAD %p (PID %d) IS LEAVING THE THREAD POOL
                    err=%p<span style="color: #000099; font-weight: bold;">\n</span>"</span>,
        <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">void</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>pthread_self<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>, getpid<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>, <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">void</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>result<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span>BC_EXIT_LOOPER<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    talkWithDriver<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">false</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

talkWithDriver的实现：

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
103
104
105
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;">status_t IPCThreadState<span style="color: #008080;">::</span><span style="color: #007788;">talkWithDriver</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">bool</span> doReceive<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>mProcess<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>mDriverFD <span style="color: #000080;">&lt;=</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000ff;">return</span> <span style="color: #000040;">-</span>EBADF<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    binder_write_read bwr<span style="color: #008080;">;</span> <span style="color: #666666;">//和驱动交互时的数据结构</span>
&nbsp;
    <span style="color: #666666;">// Is the read buffer empty?</span>
    <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">bool</span> needRead <span style="color: #000080;">=</span> mIn.<span style="color: #007788;">dataPosition</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">&gt;=</span> mIn.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #666666;">// We don't want to write anything if we are still reading</span>
    <span style="color: #666666;">// from data left in the input buffer and the caller</span>
    <span style="color: #666666;">// has requested to read the next data.</span>
    <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">size_t</span> outAvail <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span><span style="color: #000040;">!</span>doReceive <span style="color: #000040;">||</span> needRead<span style="color: #008000;">&#41;</span> <span style="color: #008080;">?</span> mOut.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008080;">:</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
&nbsp;
    bwr.<span style="color: #007788;">write_size</span> <span style="color: #000080;">=</span> outAvail<span style="color: #008080;">;</span>
    bwr.<span style="color: #007788;">write_buffer</span> <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">long</span> <span style="color: #0000ff;">unsigned</span> <span style="color: #0000ff;">int</span><span style="color: #008000;">&#41;</span>mOut.<span style="color: #007788;">data</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #666666;">// This is what we'll read.</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>doReceive <span style="color: #000040;">&&</span> needRead<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        bwr.<span style="color: #007788;">read_size</span> <span style="color: #000080;">=</span> mIn.<span style="color: #007788;">dataCapacity</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        bwr.<span style="color: #007788;">read_buffer</span> <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">long</span> <span style="color: #0000ff;">unsigned</span> <span style="color: #0000ff;">int</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">data</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #008000;">&#123;</span>
        bwr.<span style="color: #007788;">read_size</span> <span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
        bwr.<span style="color: #007788;">read_buffer</span> <span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    IF_LOG_COMMANDS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        TextOutput<span style="color: #008080;">::</span><span style="color: #007788;">Bundle</span> _b<span style="color: #008000;">&#40;</span>alog<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>outAvail <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"Sending commands to driver: "</span> <span style="color: #000080;">&lt;&lt;</span> indent<span style="color: #008080;">;</span>
            <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">void</span><span style="color: #000040;">*</span> cmds <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">void</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>bwr.<span style="color: #007788;">write_buffer</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">void</span><span style="color: #000040;">*</span> end <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">uint8_t</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>cmds<span style="color: #008000;">&#41;</span><span style="color: #000040;">+</span>bwr.<span style="color: #007788;">write_size</span><span style="color: #008080;">;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> HexDump<span style="color: #008000;">&#40;</span>cmds, bwr.<span style="color: #007788;">write_size</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
            <span style="color: #0000ff;">while</span> <span style="color: #008000;">&#40;</span>cmds <span style="color: #000080;">&lt;</span> end<span style="color: #008000;">&#41;</span> cmds <span style="color: #000080;">=</span> printCommand<span style="color: #008000;">&#40;</span>alog, cmds<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> dedent<span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"Size of receive buffer: "</span> <span style="color: #000080;">&lt;&lt;</span> bwr.<span style="color: #007788;">read_size</span>
            <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">", needRead: "</span> <span style="color: #000080;">&lt;&lt;</span> needRead <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">", doReceive: "</span> 
            <span style="color: #000080;">&lt;&lt;</span> doReceive <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #666666;">// Return immediately if there is nothing to do.</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span>bwr.<span style="color: #007788;">write_size</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #000040;">&&</span> <span style="color: #008000;">&#40;</span>bwr.<span style="color: #007788;">read_size</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">return</span> NO_ERROR<span style="color: #008080;">;</span>
&nbsp;
    bwr.<span style="color: #007788;">write_consumed</span> <span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
    bwr.<span style="color: #007788;">read_consumed</span> <span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
    status_t err<span style="color: #008080;">;</span>
    <span style="color: #0000ff;">do</span> <span style="color: #008000;">&#123;</span>
        IF_LOG_COMMANDS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"About to read/write, write size = "</span> 
                  <span style="color: #000080;">&lt;&lt;</span> mOut.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
<span style="color: #339900;">#if defined(HAVE_ANDROID_OS)</span>
        <span style="color: #666666;">//使用ioctl与binder驱动交互，BINDER_WRITE_READ是最重要的命令字</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>ioctl<span style="color: #008000;">&#40;</span>mProcess<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>mDriverFD, BINDER_WRITE_READ, <span style="color: #000040;">&</span>bwr<span style="color: #008000;">&#41;</span> <span style="color: #000080;">&gt;=</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span>
            err <span style="color: #000080;">=</span> NO_ERROR<span style="color: #008080;">;</span>
        <span style="color: #0000ff;">else</span>
            err <span style="color: #000080;">=</span> <span style="color: #000040;">-</span><span style="color: #0000ff;">errno</span><span style="color: #008080;">;</span>
<span style="color: #339900;">#else</span>
        err <span style="color: #000080;">=</span> INVALID_OPERATION<span style="color: #008080;">;</span>
<span style="color: #339900;">#endif</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>mProcess<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>mDriverFD <span style="color: #000080;">&lt;=</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            err <span style="color: #000080;">=</span> <span style="color: #000040;">-</span>EBADF<span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        IF_LOG_COMMANDS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"Finished read/write, write size = "</span> 
                  <span style="color: #000080;">&lt;&lt;</span> mOut.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">while</span> <span style="color: #008000;">&#40;</span>err <span style="color: #000080;">==</span> <span style="color: #000040;">-</span>EINTR<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    IF_LOG_COMMANDS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"Our err: "</span> <span style="color: #000080;">&lt;&lt;</span> <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">void</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>err <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">", write consumed: "</span>
            <span style="color: #000080;">&lt;&lt;</span> bwr.<span style="color: #007788;">write_consumed</span> <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">" (of "</span> <span style="color: #000080;">&lt;&lt;</span> mOut.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>
			<span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"), read consumed: "</span> 
			<span style="color: #000080;">&lt;&lt;</span> bwr.<span style="color: #007788;">read_consumed</span> <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>err <span style="color: #000080;">&gt;=</span> NO_ERROR<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>bwr.<span style="color: #007788;">write_consumed</span> <span style="color: #000080;">&gt;</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>bwr.<span style="color: #007788;">write_consumed</span> <span style="color: #000080;">&lt;</span> <span style="color: #008000;">&#40;</span>ssize_t<span style="color: #008000;">&#41;</span>mOut.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span>
                mOut.<span style="color: #0000dd;">remove</span><span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span>, bwr.<span style="color: #007788;">write_consumed</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">else</span>
                mOut.<span style="color: #007788;">setDataSize</span><span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>bwr.<span style="color: #007788;">read_consumed</span> <span style="color: #000080;">&gt;</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            mIn.<span style="color: #007788;">setDataSize</span><span style="color: #008000;">&#40;</span>bwr.<span style="color: #007788;">read_consumed</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            mIn.<span style="color: #007788;">setDataPosition</span><span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        IF_LOG_COMMANDS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            TextOutput<span style="color: #008080;">::</span><span style="color: #007788;">Bundle</span> _b<span style="color: #008000;">&#40;</span>alog<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"Remaining data size: "</span> <span style="color: #000080;">&lt;&lt;</span> mOut.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"Received commands from driver: "</span> <span style="color: #000080;">&lt;&lt;</span> indent<span style="color: #008080;">;</span>
            <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">void</span><span style="color: #000040;">*</span> cmds <span style="color: #000080;">=</span> mIn.<span style="color: #007788;">data</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">void</span><span style="color: #000040;">*</span> end <span style="color: #000080;">=</span> mIn.<span style="color: #007788;">data</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000040;">+</span> mIn.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> HexDump<span style="color: #008000;">&#40;</span>cmds, mIn.<span style="color: #007788;">dataSize</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
            <span style="color: #0000ff;">while</span> <span style="color: #008000;">&#40;</span>cmds <span style="color: #000080;">&lt;</span> end<span style="color: #008000;">&#41;</span> cmds <span style="color: #000080;">=</span> printReturnCommand<span style="color: #008000;">&#40;</span>alog, cmds<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            alog <span style="color: #000080;">&lt;&lt;</span> dedent<span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        <span style="color: #0000ff;">return</span> NO_ERROR<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">return</span> err<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

executeCommand的实现：

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
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;">status_t IPCThreadState<span style="color: #008080;">::</span><span style="color: #007788;">executeCommand</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int32_t</span> cmd<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    BBinder<span style="color: #000040;">*</span> obj<span style="color: #008080;">;</span>
    RefBase<span style="color: #008080;">::</span><span style="color: #007788;">weakref_type</span><span style="color: #000040;">*</span> refs<span style="color: #008080;">;</span>
    status_t result <span style="color: #000080;">=</span> NO_ERROR<span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">switch</span> <span style="color: #008000;">&#40;</span>cmd<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">case</span> BR_ERROR<span style="color: #008080;">:</span>
        result <span style="color: #000080;">=</span> mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_OK<span style="color: #008080;">:</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_ACQUIRE<span style="color: #008080;">:</span>
        refs <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>RefBase<span style="color: #008080;">::</span><span style="color: #007788;">weakref_type</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        obj <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>BBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        ALOG_ASSERT<span style="color: #008000;">&#40;</span>refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>refBase<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> obj,
                   <span style="color: #FF0000;">"BR_ACQUIRE: object %p does not match cookie %p 
                     (expected %p)"</span>,
                   refs, obj, refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>refBase<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        obj<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>incStrong<span style="color: #008000;">&#40;</span>mProcess.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        IF_LOG_REMOTEREFS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            LOG_REMOTEREFS<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"BR_ACQUIRE from driver on %p"</span>, obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            obj<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>printRefs<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span>BC_ACQUIRE_DONE<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int32_t</span><span style="color: #008000;">&#41;</span>refs<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int32_t</span><span style="color: #008000;">&#41;</span>obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_RELEASE<span style="color: #008080;">:</span>
        refs <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>RefBase<span style="color: #008080;">::</span><span style="color: #007788;">weakref_type</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        obj <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>BBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        ALOG_ASSERT<span style="color: #008000;">&#40;</span>refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>refBase<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> obj,
                   <span style="color: #FF0000;">"BR_RELEASE: object %p does not match 
                    cookie %p (expected %p)"</span>,
                   refs, obj, refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>refBase<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        IF_LOG_REMOTEREFS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            LOG_REMOTEREFS<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"BR_RELEASE from driver on %p"</span>, obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            obj<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>printRefs<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        mPendingStrongDerefs.<span style="color: #007788;">push</span><span style="color: #008000;">&#40;</span>obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_INCREFS<span style="color: #008080;">:</span>
        refs <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>RefBase<span style="color: #008080;">::</span><span style="color: #007788;">weakref_type</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        obj <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>BBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>incWeak<span style="color: #008000;">&#40;</span>mProcess.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span>BC_INCREFS_DONE<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int32_t</span><span style="color: #008000;">&#41;</span>refs<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int32_t</span><span style="color: #008000;">&#41;</span>obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_DECREFS<span style="color: #008080;">:</span>
        refs <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>RefBase<span style="color: #008080;">::</span><span style="color: #007788;">weakref_type</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        obj <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>BBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #666666;">// NOTE: This assertion is not valid, because the object may no</span>
        <span style="color: #666666;">// longer exist (thus the (BBinder*)cast </span>
        <span style="color: #666666;">//above resulting in a different</span>
        <span style="color: #666666;">// memory address).</span>
        <span style="color: #666666;">//ALOG_ASSERT(refs-&gt;refBase() == obj,</span>
        <span style="color: #666666;">//           "BR_DECREFS: object %p does not match </span>
        <span style="color: #666666;">//cookie %p (expected %p)",</span>
        <span style="color: #666666;">//           refs, obj, refs-&gt;refBase());</span>
        mPendingWeakDerefs.<span style="color: #007788;">push</span><span style="color: #008000;">&#40;</span>refs<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_ATTEMPT_ACQUIRE<span style="color: #008080;">:</span>
        refs <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>RefBase<span style="color: #008080;">::</span><span style="color: #007788;">weakref_type</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        obj <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>BBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
        <span style="color: #008000;">&#123;</span>
            <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">bool</span> success <span style="color: #000080;">=</span> refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>attemptIncStrong<span style="color: #008000;">&#40;</span>mProcess.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            ALOG_ASSERT<span style="color: #008000;">&#40;</span>success <span style="color: #000040;">&&</span> refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>refBase<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> obj,
                       <span style="color: #FF0000;">"BR_ATTEMPT_ACQUIRE: object %p does not 
                         match cookie %p (expected %p)"</span>,
                       refs, obj, refs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>refBase<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
            mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span>BC_ACQUIRE_RESULT<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int32_t</span><span style="color: #008000;">&#41;</span>success<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_TRANSACTION<span style="color: #008080;">:</span> <span style="color: #666666;">//最重要的分支</span>
        <span style="color: #008000;">&#123;</span>
            binder_transaction_data tr<span style="color: #008080;">;</span>
            result <span style="color: #000080;">=</span> mIn.<span style="color: #007788;">read</span><span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>tr, <span style="color: #0000dd;">sizeof</span><span style="color: #008000;">&#40;</span>tr<span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            ALOG_ASSERT<span style="color: #008000;">&#40;</span>result <span style="color: #000080;">==</span> NO_ERROR,
                <span style="color: #FF0000;">"Not enough command data for brTRANSACTION"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>result <span style="color: #000040;">!</span><span style="color: #000080;">=</span> NO_ERROR<span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
            Parcel buffer<span style="color: #008080;">;</span>
            buffer.<span style="color: #007788;">ipcSetDataReference</span><span style="color: #008000;">&#40;</span>
                <span style="color: #0000ff;">reinterpret_cast</span><span style="color: #000080;">&lt;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">uint8_t</span><span style="color: #000040;">*</span><span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">data</span>.<span style="color: #007788;">ptr</span>.<span style="color: #007788;">buffer</span><span style="color: #008000;">&#41;</span>,
                tr.<span style="color: #007788;">data_size</span>,
                <span style="color: #0000ff;">reinterpret_cast</span><span style="color: #000080;">&lt;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">size_t</span><span style="color: #000040;">*</span><span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">data</span>.<span style="color: #007788;">ptr</span>.<span style="color: #007788;">offsets</span><span style="color: #008000;">&#41;</span>,
                tr.<span style="color: #007788;">offsets_size</span><span style="color: #000040;">/</span><span style="color: #0000dd;">sizeof</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">size_t</span><span style="color: #008000;">&#41;</span>, freeBuffer, <span style="color: #0000dd;">this</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
            <span style="color: #0000ff;">const</span> pid_t origPid <span style="color: #000080;">=</span> mCallingPid<span style="color: #008080;">;</span>
            <span style="color: #0000ff;">const</span> uid_t origUid <span style="color: #000080;">=</span> mCallingUid<span style="color: #008080;">;</span>
&nbsp;
            mCallingPid <span style="color: #000080;">=</span> tr.<span style="color: #007788;">sender_pid</span><span style="color: #008080;">;</span>
            mCallingUid <span style="color: #000080;">=</span> tr.<span style="color: #007788;">sender_euid</span><span style="color: #008080;">;</span>
&nbsp;
            <span style="color: #0000ff;">int</span> curPrio <span style="color: #000080;">=</span> getpriority<span style="color: #008000;">&#40;</span>PRIO_PROCESS, mMyThreadId<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>gDisableBackgroundScheduling<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>curPrio <span style="color: #000080;">&gt;</span> ANDROID_PRIORITY_NORMAL<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #666666;">// We have inherited a reduced priority from the caller, but do not</span>
        <span style="color: #666666;">// want to run in that state in this process.  The driver set our</span>
        <span style="color: #666666;">// priority already (though not our scheduling class), so bounce</span>
        <span style="color: #666666;">// it back to the default before invoking the transaction.</span>
                    setpriority<span style="color: #008000;">&#40;</span>PRIO_PROCESS, mMyThreadId, 
                       ANDROID_PRIORITY_NORMAL<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #008000;">&#125;</span>
            <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #008000;">&#123;</span>
                <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>curPrio <span style="color: #000080;">&gt;=</span> ANDROID_PRIORITY_BACKGROUND<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            <span style="color: #666666;">// We want to use the inherited priority from the caller.</span>
            <span style="color: #666666;">// Ensure this thread is in the background scheduling class,</span>
            <span style="color: #666666;">// since the driver won't modify scheduling classes for us.</span>
            <span style="color: #666666;">// The scheduling group is reset to default by the caller</span>
            <span style="color: #666666;">// once this method returns after the transaction is complete.</span>
                    set_sched_policy<span style="color: #008000;">&#40;</span>mMyThreadId, SP_BACKGROUND<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #008000;">&#125;</span>
            <span style="color: #008000;">&#125;</span>
&nbsp;
            <span style="color: #666666;">//ALOGI("&gt;&gt;&gt;&gt; TRANSACT from pid %d uid %d\n",</span>
            <span style="color: #666666;">// mCallingPid, mCallingUid);</span>
&nbsp;
            Parcel reply<span style="color: #008080;">;</span>
            IF_LOG_TRANSACTIONS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                TextOutput<span style="color: #008080;">::</span><span style="color: #007788;">Bundle</span> _b<span style="color: #008000;">&#40;</span>alog<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"BR_TRANSACTION thr "</span> <span style="color: #000080;">&lt;&lt;</span> <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">void</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>pthread_self<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>
                    <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">" / obj "</span> <span style="color: #000080;">&lt;&lt;</span> tr.<span style="color: #007788;">target</span>.<span style="color: #007788;">ptr</span> <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">" / code "</span>
                    <span style="color: #000080;">&lt;&lt;</span> TypeCode<span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">code</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">": "</span> <span style="color: #000080;">&lt;&lt;</span> indent <span style="color: #000080;">&lt;&lt;</span> buffer
                    <span style="color: #000080;">&lt;&lt;</span> dedent <span style="color: #000080;">&lt;&lt;</span> endl
                    <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"Data addr = "</span>
                    <span style="color: #000080;">&lt;&lt;</span> <span style="color: #0000ff;">reinterpret_cast</span><span style="color: #000080;">&lt;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">uint8_t</span><span style="color: #000040;">*</span><span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">data</span>.<span style="color: #007788;">ptr</span>.<span style="color: #007788;">buffer</span><span style="color: #008000;">&#41;</span>
                    <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">", offsets addr="</span>
                    <span style="color: #000080;">&lt;&lt;</span> <span style="color: #0000ff;">reinterpret_cast</span><span style="color: #000080;">&lt;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">size_t</span><span style="color: #000040;">*</span><span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">data</span>.<span style="color: #007788;">ptr</span>.<span style="color: #007788;">offsets</span><span style="color: #008000;">&#41;</span>
                    <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">target</span>.<span style="color: #007788;">ptr</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                sp<span style="color: #000080;">&lt;</span>BBinder<span style="color: #000080;">&gt;</span> b<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span>BBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>tr.<span style="color: #007788;">cookie</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #666666;">//调用BBinder的transact方法 最终会调用服务类的onTransact方法</span>
                <span style="color: #0000ff;">const</span> status_t error <span style="color: #000080;">=</span> b<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>transact<span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">code</span>, buffer, 
                                        <span style="color: #000040;">&</span>reply, tr.<span style="color: #007788;">flags</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>error <span style="color: #000080;">&lt;</span> NO_ERROR<span style="color: #008000;">&#41;</span> reply.<span style="color: #007788;">setError</span><span style="color: #008000;">&#40;</span>error<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
            <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #008000;">&#123;</span>
                <span style="color: #0000ff;">const</span> status_t error <span style="color: #000080;">=</span> the_context_object<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>transact<span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">code</span>,
                                 buffer, <span style="color: #000040;">&</span>reply, tr.<span style="color: #007788;">flags</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>error <span style="color: #000080;">&lt;</span> NO_ERROR<span style="color: #008000;">&#41;</span> reply.<span style="color: #007788;">setError</span><span style="color: #008000;">&#40;</span>error<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
&nbsp;
            <span style="color: #666666;">//ALOGI("&lt;&lt;&lt;&lt; TRANSACT from pid %d restore pid %d uid %d\n",</span>
            <span style="color: #666666;">//     mCallingPid, origPid, origUid);</span>
&nbsp;
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span>tr.<span style="color: #007788;">flags</span> <span style="color: #000040;">&</span> TF_ONE_WAY<span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                LOG_ONEWAY<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Sending reply to %d!"</span>, mCallingPid<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                sendReply<span style="color: #008000;">&#40;</span>reply, <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #008000;">&#123;</span>
                LOG_ONEWAY<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"NOT sending reply to %d!"</span>, mCallingPid<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
&nbsp;
            mCallingPid <span style="color: #000080;">=</span> origPid<span style="color: #008080;">;</span>
            mCallingUid <span style="color: #000080;">=</span> origUid<span style="color: #008080;">;</span>
&nbsp;
            IF_LOG_TRANSACTIONS<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
                TextOutput<span style="color: #008080;">::</span><span style="color: #007788;">Bundle</span> _b<span style="color: #008000;">&#40;</span>alog<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                alog <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">"BC_REPLY thr "</span> <span style="color: #000080;">&lt;&lt;</span> <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">void</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>pthread_self<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> 
                     <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">" / obj "</span>
                    <span style="color: #000080;">&lt;&lt;</span> tr.<span style="color: #007788;">target</span>.<span style="color: #007788;">ptr</span> <span style="color: #000080;">&lt;&lt;</span> <span style="color: #FF0000;">": "</span> <span style="color: #000080;">&lt;&lt;</span> indent <span style="color: #000080;">&lt;&lt;</span> reply 
                    <span style="color: #000080;">&lt;&lt;</span> dedent <span style="color: #000080;">&lt;&lt;</span> endl<span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
&nbsp;
        <span style="color: #008000;">&#125;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_DEAD_BINDER<span style="color: #008080;">:</span>
        <span style="color: #008000;">&#123;</span>
            BpBinder <span style="color: #000040;">*</span>proxy <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>BpBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            proxy<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>sendObituary<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span>BC_DEAD_BINDER_DONE<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            mOut.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int32_t</span><span style="color: #008000;">&#41;</span>proxy<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_CLEAR_DEATH_NOTIFICATION_DONE<span style="color: #008080;">:</span>
        <span style="color: #008000;">&#123;</span>
            BpBinder <span style="color: #000040;">*</span>proxy <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>BpBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>mIn.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            proxy<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>getWeakRefs<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>decWeak<span style="color: #008000;">&#40;</span>proxy<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_FINISHED<span style="color: #008080;">:</span>
        result <span style="color: #000080;">=</span> TIMED_OUT<span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_NOOP<span style="color: #008080;">:</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">case</span> BR_SPAWN_LOOPER<span style="color: #008080;">:</span>
        mProcess<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>spawnPooledThread<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">false</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">default</span><span style="color: #008080;">:</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"*** BAD COMMAND %d received from Binder driver<span style="color: #000099; font-weight: bold;">\n</span>"</span>, cmd<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        result <span style="color: #000080;">=</span> UNKNOWN_ERROR<span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>result <span style="color: #000040;">!</span><span style="color: #000080;">=</span> NO_ERROR<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        mLastError <span style="color: #000080;">=</span> result<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">return</span> result<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## Binder核心框架层

Binder核心框架主要是IBinder及它的两个子类，即BBinder和BpBinder，分别代表了最基本的服务端及客户端。类图如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/IBinder.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/IBinder-1024x514.png" alt="IBinder" width="1024" height="514" class="aligncenter size-large wp-image-531" srcset="http://www.cloudchou.com/wp-content/uploads/2014/05/IBinder-1024x514.png 1024w, http://www.cloudchou.com/wp-content/uploads/2014/05/IBinder-300x150.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/05/IBinder-200x100.png 200w, http://www.cloudchou.com/wp-content/uploads/2014/05/IBinder.png 1060w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

  * ### 1) IBinder(frameworks/native/include/binder/IBinder.h)
    
    IBinder有两个直接子类，代表服务端的BBinder和代表客户端的BpBinder。
    
    重要方法说明(以下方法均是抽象方法)：
    
    queryLocalInterface 用于检查IBinder是否实现了descriptor指定的接口，若实现了则会返回它的指针
    
    getInterfaceDescriptor 用于返回IBinder提供的接口名字
    
    transact 客户端用该方法向服务端提交数据，服务端实现该方法以处理客户端请求。

  * ### 2) BBinder(frameworks/native/include/binder/Binder.h)
    
    BBinder代表binder service服务端，最终声明的binder 服务类将间接从该类继承，它实现了IBinder声明的transact方法，转调留给子类实现onTrasact的方法。
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"> status_t BBinder<span style="color: #008080;">::</span><span style="color: #007788;">transact</span><span style="color: #008000;">&#40;</span>
    <span style="color: #0000ff;">uint32_t</span> code, <span style="color: #0000ff;">const</span> Parcel<span style="color: #000040;">&</span> data, Parcel<span style="color: #000040;">*</span> reply, <span style="color: #0000ff;">uint32_t</span> flags<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    data.<span style="color: #007788;">setDataPosition</span><span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    status_t err <span style="color: #000080;">=</span> NO_ERROR<span style="color: #008080;">;</span>
    <span style="color: #0000ff;">switch</span> <span style="color: #008000;">&#40;</span>code<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000ff;">case</span> PING_TRANSACTION<span style="color: #008080;">:</span>
            reply<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>writeInt32<span style="color: #008000;">&#40;</span>pingBinder<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">default</span><span style="color: #008080;">:</span>
            err <span style="color: #000080;">=</span> onTransact<span style="color: #008000;">&#40;</span>code, data, reply, flags<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>reply <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        reply<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>setDataPosition<span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">return</span> err<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 3) BpBinder(frameworks/native/include/binder/BpBinder.h)
    
    客户端使用servicemananger查询服务时实际上是先得到一个句柄handle，然后ProcessState的getStrongProxyForHandle函数里利用句柄handle建立BpBinder对象，再转为IBinder指针，代理类便是通过该指针向服务端请求。

## 参考资料

书《Android系统原理及开发要点详解》 第4章Android的底层库和程序

书《Android技术内幕 系统卷》 第3章 Android的IPC机制―Binder