---
id: 468
title: Binder service入门—框架层、应用层调用native binder service
date: 2014-04-22T01:21:15+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=468
permalink: /android/post-468.html
views:
  - 8608
categories:
  - Android
tags:
  - android binder example
  - android binder 使用
  - android binder 入门
  - android binder 实例
  - android 框架层调用底层binder service
---
## 1.前言

Binder service入门系列：

  * Binder service入门–创建native binder service:   
    <a href="http://www.cloudchou.com/android/post-332.html" target="_blank">http://www.cloudchou.com/android/post-332.html</a>
  * Binder service入门—Framework binder service:   
    <a href="http://www.cloudchou.com/android/post-447.html" target="_blank">http://www.cloudchou.com/android/post-447.html</a>
  * Binder service入门—应用层binder service:   
    <a href="http://www.cloudchou.com/android/post-458.html" target="_blank">http://www.cloudchou.com/android/post-458.html</a>

上一篇介绍了如何创建应用层binder service，本篇将综合先前介绍的native binder service，framework binder service，应用层binder service等知识，讲述如何使用native 的client，framework层的client，应用层的client测试native binder service。

## 2.程序构成

因为编译native的binder service，framework层的client都需要在源码环境下编译，故此本篇讲述的工程需要在源码环境下编译。

整个工程可以在github上下载： 

<a href="https://github.com/cloudchou/NativeBinderJavaClientDemo" target="_blank">https://github.com/cloudchou/NativeBinderJavaClientDemo</a>

程序由4个部分组成：

  * 1) native_bserver 创建并注册native binder service的本地服务端
  * 2) native_bclient 测试native binder service的本地客户端
  * 3) fclient和fclient.jar测试native binder service的框架层客户端
  * 4) NativeBinderServiceTest 测试native binder service的应用层客户端

## 3.程序源码构成

源程序目录结构如下所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest_f.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest_f.png" alt="nativetest_f" width="451" height="708" class="alignnone size-full wp-image-472" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest_f.png 451w, http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest_f-191x300.png 191w, http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest_f-95x150.png 95w" sizes="(max-width: 451px) 100vw, 451px" /></a>

顶层Android.mk只是简单包含各个子目录的Android.mk，BServer目录存放本地服务端和本地客户端源码，FClient存放框架层客户端源码，NatviveBinderServiceTest存放应用层客户端源码。

### 本地服务端和本地客户端

  * ### 1) BServer的Android.mk源码如下所示：
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="make" style="font-family:monospace;">LOCAL_PATH <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> my<span style="color: #004400;">-</span>dir<span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #339900; font-style: italic;">#生成binder service的本地服务端</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_SHARED_LIBRARIES <span style="color: #004400;">:=</span> \
    libcutils \
    libutils \
    libbinder       
LOCAL_MODULE    <span style="color: #004400;">:=</span> native_bserver
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> \
    ICloudManager<span style="color: #004400;">.</span>cpp \
    TestServer<span style="color: #004400;">.</span>cpp   
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_EXECUTABLE</span><span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #339900; font-style: italic;">#生成binder service的本地客户端</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_SHARED_LIBRARIES <span style="color: #004400;">:=</span> \
    libcutils \
    libutils \
    libbinder
LOCAL_MODULE    <span style="color: #004400;">:=</span> native_bclient
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> \
    ICloudManager<span style="color: #004400;">.</span>cpp \
    TestClient<span style="color: #004400;">.</span>cpp
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_EXECUTABLE</span><span style="color: #004400;">&#41;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 2) binder service接口ICloudManager(ICloudManager.h)： 
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">namespace</span> android
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">class</span> ICloudManager <span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> IInterface
    <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
        DECLARE_META_INTERFACE<span style="color: #008000;">&#40;</span>CloudManager<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span> <span style="color: #666666;">// declare macro</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span> test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000080;">=</span><span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span> print<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">char</span><span style="color: #000040;">*</span> str<span style="color: #008000;">&#41;</span><span style="color: #000080;">=</span><span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">int</span> add<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int</span> a, <span style="color: #0000ff;">int</span> b<span style="color: #008000;">&#41;</span><span style="color: #000080;">=</span><span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">enum</span>
    <span style="color: #008000;">&#123;</span>
        TEST <span style="color: #000080;">=</span> IBinder<span style="color: #008080;">::</span><span style="color: #007788;">FIRST_CALL_TRANSACTION</span><span style="color: #000040;">+</span><span style="color: #0000dd;">1</span>,
        PRINT <span style="color: #000080;">=</span> IBinder<span style="color: #008080;">::</span><span style="color: #007788;">FIRST_CALL_TRANSACTION</span><span style="color: #000040;">+</span><span style="color: #0000dd;">2</span>,
        ADD <span style="color: #000080;">=</span> IBinder<span style="color: #008080;">::</span><span style="color: #007788;">FIRST_CALL_TRANSACTION</span><span style="color: #000040;">+</span><span style="color: #0000dd;">3</span>,
    <span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #0000ff;">class</span> BpCloudManager<span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> BpInterface<span style="color: #000080;">&lt;</span>ICloudManager<span style="color: #000080;">&gt;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
        BpCloudManager<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> impl<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span> test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span> print<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">char</span><span style="color: #000040;">*</span> str<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">int</span> add<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int</span> a, <span style="color: #0000ff;">int</span> b<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 3) 实现实现ICloudManager接口的方法(ICloudManager.cpp)
    
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
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">namespace</span> android
<span style="color: #008000;">&#123;</span>
    IMPLEMENT_META_INTERFACE<span style="color: #008000;">&#40;</span>CloudManager, <span style="color: #FF0000;">"com.cloud.test.ICloudManager"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 4) 实现服务端(TestServer.cpp)
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"> <span style="color: #0000ff;">namespace</span> android
<span style="color: #008000;">&#123;</span>
     <span style="color: #666666;">//binder service 实体类</span>
    <span style="color: #0000ff;">class</span> BnCloudManager <span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> BnInterface<span style="color: #000080;">&lt;</span>ICloudManager<span style="color: #000080;">&gt;</span>
    <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
        <span style="color: #0000ff;">virtual</span> status_t
        onTransact<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">uint32_t</span> code, <span style="color: #0000ff;">const</span> Parcel<span style="color: #000040;">&</span> data, Parcel<span style="color: #000040;">*</span> reply, <span style="color: #0000ff;">uint32_t</span> flags <span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span>   test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span>   print<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">char</span><span style="color: #000040;">*</span> str<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">int</span>   add<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int</span> a, <span style="color: #0000ff;">int</span> b<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span>
&nbsp;
    status_t
    BnCloudManager<span style="color: #008080;">::</span><span style="color: #007788;">onTransact</span><span style="color: #008000;">&#40;</span>uint_t code, <span style="color: #0000ff;">const</span> Parcel<span style="color: #000040;">&</span> data, Parcel<span style="color: #000040;">*</span> reply, <span style="color: #0000ff;">uint32_t</span> flags<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000ff;">switch</span> <span style="color: #008000;">&#40;</span>code<span style="color: #008000;">&#41;</span>
            <span style="color: #008000;">&#123;</span>
        <span style="color: #0000ff;">case</span> TEST<span style="color: #008080;">:</span>
            <span style="color: #008000;">&#123;</span>
                CHECK_INTERFACE<span style="color: #008000;">&#40;</span>ICloudManager, data, reply<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                reply<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>writeInt32<span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #0000ff;">return</span> NO_ERROR<span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
            <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">case</span> PRINT<span style="color: #008080;">:</span>
            <span style="color: #008000;">&#123;</span>
                CHECK_INTERFACE<span style="color: #008000;">&#40;</span>ICloudManager, data, reply<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                String16 str <span style="color: #000080;">=</span> data.<span style="color: #007788;">readString16</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                String8 str8 <span style="color: #000080;">=</span> String8<span style="color: #008000;">&#40;</span>str<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                print<span style="color: #008000;">&#40;</span>str8.<span style="color: #007788;">string</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                reply<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>writeInt32<span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #0000ff;">return</span> NO_ERROR<span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
            <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">case</span> ADD<span style="color: #008080;">:</span>
            <span style="color: #008000;">&#123;</span>
                CHECK_INTERFACE<span style="color: #008000;">&#40;</span>ITest, data, reply<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #0000ff;">int</span> a<span style="color: #008080;">;</span>
                <span style="color: #0000ff;">int</span> b<span style="color: #008080;">;</span>
                data.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>a<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                data.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>b<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #0000ff;">int</span> c <span style="color: #000080;">=</span> add<span style="color: #008000;">&#40;</span>a,b<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                reply<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>writeInt32<span style="color: #008000;">&#40;</span><span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                reply<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>writeInt32<span style="color: #008000;">&#40;</span>c<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
                <span style="color: #0000ff;">return</span> NO_ERROR<span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
            <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">default</span><span style="color: #008080;">:</span>
            <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
            <span style="color: #008000;">&#125;</span>
        <span style="color: #0000ff;">return</span> NO_ERROR<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">void</span>
    BnCloudManager<span style="color: #008080;">::</span><span style="color: #007788;">test</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Now server receive requset from client: [call test]<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">void</span>
    BnCloudManager<span style="color: #008080;">::</span><span style="color: #007788;">print</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">char</span><span style="color: #000040;">*</span> str<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Now server receive requset from client: [call print %s]<span style="color: #000099; font-weight: bold;">\n</span>"</span>, str<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">int</span>
    BnCloudManager<span style="color: #008080;">::</span><span style="color: #007788;">add</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int</span> a, <span style="color: #0000ff;">int</span> b<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Now server receive requset from client: [call add %d %d]<span style="color: #000099; font-weight: bold;">\n</span>"</span>, a, b<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">return</span> a <span style="color: #000040;">+</span> b<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
<span style="color: #008000;">&#125;</span>
<span style="color: #0000ff;">int</span>
main<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    sp<span style="color: #000080;">&lt;</span>ProcessState<span style="color: #000080;">&gt;</span> proc<span style="color: #008000;">&#40;</span>ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
sp<span style="color: #000080;">&lt;</span>IServiceManager<span style="color: #000080;">&gt;</span> sm <span style="color: #000080;">=</span> defaultServiceManager<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #666666;">//注册binder service</span>
    sm<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>addService<span style="color: #008000;">&#40;</span>String16<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"cloudservice"</span><span style="color: #008000;">&#41;</span>, <span style="color: #0000dd;">new</span> BnCloudManager<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Native binder server starts to work<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>startThreadPool<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    IPCThreadState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>joinThreadPool<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">return</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 5) 实现客户端(TestClient.cpp)
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">namespace</span> android
<span style="color: #008000;">&#123;</span>
    BpCloudManager<span style="color: #008080;">::</span><span style="color: #007788;">BpCloudManager</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> impl<span style="color: #008000;">&#41;</span> <span style="color: #008080;">:</span>
            BpInterface<span style="color: #000080;">&lt;</span>ICloudManager<span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>impl<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #008000;">&#125;</span>
    <span style="color: #0000ff;">void</span>
    BpCloudManager<span style="color: #008080;">::</span><span style="color: #007788;">test</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Client call server test method<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        Parcel data, reply<span style="color: #008080;">;</span>
        data.<span style="color: #007788;">writeInterfaceToken</span><span style="color: #008000;">&#40;</span>ICloudManager<span style="color: #008080;">::</span><span style="color: #007788;">getInterfaceDescriptor</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        remote<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>transact<span style="color: #008000;">&#40;</span>TEST, data, <span style="color: #000040;">&</span>reply<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">int</span> code <span style="color: #000080;">=</span> reply.<span style="color: #007788;">readExceptionCode</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Server exepction code: %d<span style="color: #000099; font-weight: bold;">\n</span>"</span>, code<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">void</span>
    BpCloudManager<span style="color: #008080;">::</span><span style="color: #007788;">print</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> <span style="color: #0000ff;">char</span><span style="color: #000040;">*</span> str<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Client call server print method<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        Parcel data, reply<span style="color: #008080;">;</span>
        data.<span style="color: #007788;">writeInterfaceToken</span><span style="color: #008000;">&#40;</span>ICloudManager<span style="color: #008080;">::</span><span style="color: #007788;">getInterfaceDescriptor</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        data.<span style="color: #007788;">writeString16</span><span style="color: #008000;">&#40;</span>String16<span style="color: #008000;">&#40;</span>str<span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        remote<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>transact<span style="color: #008000;">&#40;</span>PRINT, data, <span style="color: #000040;">&</span>reply<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">int</span> code <span style="color: #000080;">=</span> reply.<span style="color: #007788;">readExceptionCode</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Server exepction code: %d<span style="color: #000099; font-weight: bold;">\n</span>"</span>, code<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">int</span>
    BpCloudManager<span style="color: #008080;">::</span><span style="color: #007788;">add</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int</span> a, <span style="color: #0000ff;">int</span> b<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Client call server add method<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        Parcel data, reply<span style="color: #008080;">;</span>
        data.<span style="color: #007788;">writeInterfaceToken</span><span style="color: #008000;">&#40;</span>ICloudManager<span style="color: #008080;">::</span><span style="color: #007788;">getInterfaceDescriptor</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        data.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span>a<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        data.<span style="color: #007788;">writeInt32</span><span style="color: #008000;">&#40;</span>b<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        remote<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>transact<span style="color: #008000;">&#40;</span>ADD, data, <span style="color: #000040;">&</span>reply<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">int</span> code <span style="color: #000080;">=</span> reply.<span style="color: #007788;">readExceptionCode</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">int</span> result<span style="color: #008080;">;</span>
        reply.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>result<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Server exepction code: %d<span style="color: #000099; font-weight: bold;">\n</span>"</span>, code<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">return</span> result<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
<span style="color: #008000;">&#125;</span>
&nbsp;
<span style="color: #0000ff;">int</span>
main<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
sp<span style="color: #000080;">&lt;</span>IServiceManager<span style="color: #000080;">&gt;</span> sm <span style="color: #000080;">=</span> defaultServiceManager<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #666666;">//查询服务</span>
sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span> binder <span style="color: #000080;">=</span> sm<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>getService<span style="color: #008000;">&#40;</span>String16<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"cloudservice"</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #666666;">//转换接口</span>
sp<span style="color: #000080;">&lt;</span>ICloudManager<span style="color: #000080;">&gt;</span> cs <span style="color: #000080;">=</span> interface_cast<span style="color: #000080;">&lt;</span>ICloudManager<span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>binder<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #666666;">//测试接口方法</span>
    cs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    cs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>print<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Hello world"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">int</span> result<span style="color: #000080;">=</span>cs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>add<span style="color: #008000;">&#40;</span><span style="color: #0000dd;">2</span>,<span style="color: #0000dd;">3</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"client receive add result from server : %d<span style="color: #000099; font-weight: bold;">\n</span>"</span>,result<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">return</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

### 框架层客户端

  * ### 1) Android.mk
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="make" style="font-family:monospace;">LOCAL_PATH<span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> my<span style="color: #004400;">-</span>dir<span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
<span style="color: #339900; font-style: italic;">#生成fclient.jar</span>
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> all<span style="color: #004400;">-</span>subdir<span style="color: #004400;">-</span>java<span style="color: #004400;">-</span>files<span style="color: #004400;">&#41;</span>
LOCAL_MODULE <span style="color: #004400;">:=</span> fclient 
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_JAVA_LIBRARY</span><span style="color: #004400;">&#41;</span>
<span style="color: #339900; font-style: italic;">#生成fclient</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_MODULE <span style="color: #004400;">:=</span> fclient
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
LOCAL_MODULE_PATH <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_OUT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">/</span>bin
LOCAL_MODULE_CLASS <span style="color: #004400;">:=</span> UTILITY_EXECUTABLES
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> fclient
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_PREBUILT</span><span style="color: #004400;">&#41;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 2) 定义接口类(ICloudManager.java)
    
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
            <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">interface</span> ICloudManager <span style="color: #000000; font-weight: bold;">extends</span> IInterface <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//接口描述字符串</span>
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> DESCRIPTOR <span style="color: #339933;">=</span> <span style="color: #0000ff;">"com.cloud.test.ICloudManager"</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000066; font-weight: bold;">void</span> test<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_test <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_print <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;">2</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_add <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;">3</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 3) 定义接口代理类(CloudManagerProxy.java)
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> CloudManagerProxy <span style="color: #000000; font-weight: bold;">implements</span> ICloudManager <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> mRemote<span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> CloudManagerProxy<span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> remote<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        mRemote <span style="color: #339933;">=</span> remote<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> getInterfaceDescriptor<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> DESCRIPTOR<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _data <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _reply <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">writeString</span><span style="color: #009900;">&#40;</span>str<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span>TRANSACTION_print, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _reply.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _data <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _reply <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000066; font-weight: bold;">int</span> result <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>a<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>b<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span>TRANSACTION_add, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            result <span style="color: #339933;">=</span> _reply.<span style="color: #006633;">readInt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _reply.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #000000; font-weight: bold;">return</span> result<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> IBinder asBinder<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> mRemote<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> test<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _data <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _reply <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
            mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span>TRANSACTION_test, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _reply.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 4) 客户端(FClient.java)
    
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
            <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> FClient <span style="color: #009900;">&#123;</span> 
&nbsp;
    <span style="color: #008000; font-style: italic; font-weight: bold;">/**
     * Command-line entry point.
     * 
     * @param args
     *            The command-line arguments
     * @throws RemoteException
     */</span>
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> main<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> args<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"==========Client starts==========="</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        IBinder binder <span style="color: #339933;">=</span> ServiceManager.<span style="color: #006633;">getService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"cloudservice"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        ICloudManager manager <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> CloudManagerProxy<span style="color: #009900;">&#40;</span>binder<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"========== client call server  test ==========="</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        manager.<span style="color: #006633;">test</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"========== client call server print ==========="</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        manager.<span style="color: #006633;">print</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Hello world"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"========== client call server add ==========="</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000066; font-weight: bold;">int</span> result <span style="color: #339933;">=</span> manager.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">2</span>, <span style="color: #cc66cc;">3</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"manager.add(2, 3)="</span> <span style="color: #339933;">+</span> result<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 5) 客户端脚本fclient
    
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
            <pre class="bash" style="font-family:monospace;"><span style="color: #666666; font-style: italic;"># Script to start "am" on the device, which has a very rudimentary</span>
<span style="color: #666666; font-style: italic;"># shell.</span>
<span style="color: #666666; font-style: italic;">#</span>
<span style="color: #007800;">base</span>=<span style="color: #000000; font-weight: bold;">/</span>system
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">CLASSPATH</span>=<span style="color: #007800;">$base</span><span style="color: #000000; font-weight: bold;">/</span>framework<span style="color: #000000; font-weight: bold;">/</span>fclient.jar
<span style="color: #7a0874; font-weight: bold;">exec</span> app_process <span style="color: #007800;">$base</span><span style="color: #000000; font-weight: bold;">/</span>bin com.cloud.test.FClient <span style="color: #ff0000;">"$@"</span></pre>
          </td>
        </tr>
      </table>
    </div>

### 应用层客户端

先前我们有讲到在应用层是不能直接使用ServiceManager这个类的，因为Sdk并未包含该类，应用层只能通过bind service去使用binder service，但是我们的native service并不是使用应用层的Service子类创建的，这样看来貌似应用层不能使用native的binder service。

这里介绍一个技巧，其实我们的应用在运行时可以使用系统隐藏的类，比如ServiceManager，SystemProperties，只是编译时Sdk并未提供这些类，我们若使用这些类就无法编译。但是我们可以创建这些类所在的包，并创建这些类，在类里定义我们要使用的那些方法，我们就可以通过编译了。比如ServiceManager这个类，我们就可以为之创建android.os这个package，并在这个package下创建ServiceManager类，定义我们需要的方法getService。也许读者会担心运行时使用的ServiceManger类就是我们创建的ServiceManager类，但实际上运行时使用的ServiceManager类是framework.jar里的ServiceManager类，这是因为classloader在查找类时优先使用系统的类。

  * ### 1) Android.mk
    
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
            <pre class="make" style="font-family:monospace;">LOCAL_PATH<span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> my<span style="color: #004400;">-</span>dir<span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
&nbsp;
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
&nbsp;
LOCAL_STATIC_JAVA_LIBRARIES <span style="color: #004400;">:=</span> android<span style="color: #004400;">-</span>support<span style="color: #004400;">-</span>v13
LOCAL_STATIC_JAVA_LIBRARIES <span style="color: #004400;">+=</span> android<span style="color: #004400;">-</span>support<span style="color: #004400;">-</span>v4
&nbsp;
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> all<span style="color: #004400;">-</span>java<span style="color: #004400;">-</span>files<span style="color: #004400;">-</span>under<span style="color: #004400;">,</span> src<span style="color: #004400;">&#41;</span>
&nbsp;
LOCAL_PACKAGE_NAME <span style="color: #004400;">:=</span> NativeBinderServiceTest  
<span style="color: #339900; font-style: italic;">#LOCAL_PROGUARD_FLAG_FILES := proguard.flags</span>
&nbsp;
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_PACKAGE</span><span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #339900; font-style: italic;"># Use the following include to make our test apk.</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> all<span style="color: #004400;">-</span>makefiles<span style="color: #004400;">-</span>under<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">LOCAL_PATH</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 2) 我们创建的ServiceManager源码
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> ServiceManager <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> IBinder getService<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> name<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 3) 定义接口ICloudManager
    
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
            <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">interface</span> ICloudManager <span style="color: #000000; font-weight: bold;">extends</span> IInterface <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> DESCRIPTOR <span style="color: #339933;">=</span> <span style="color: #0000ff;">"com.cloud.test.ICloudManager"</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000066; font-weight: bold;">void</span> test<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_test <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_print <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;">2</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_add <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;">3</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 4) 定义代理类CloudManagerProxy
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> CloudManagerProxy <span style="color: #000000; font-weight: bold;">implements</span> ICloudManager <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> mRemote<span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> CloudManagerProxy<span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> remote<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        mRemote <span style="color: #339933;">=</span> remote<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> getInterfaceDescriptor<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> DESCRIPTOR<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _data <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _reply <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">writeString</span><span style="color: #009900;">&#40;</span>str<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span>TRANSACTION_print, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _reply.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _data <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _reply <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000066; font-weight: bold;">int</span> result <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>a<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>b<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span>TRANSACTION_add, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            result <span style="color: #339933;">=</span> _reply.<span style="color: #006633;">readInt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _reply.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #000000; font-weight: bold;">return</span> result<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> IBinder asBinder<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> mRemote<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> test<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _data <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _reply <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
            mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span>TRANSACTION_test, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _reply.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            _data.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 5) 测试用的Activity(TestAc.java)
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> TestAc <span style="color: #000000; font-weight: bold;">extends</span> Activity <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> TAG <span style="color: #339933;">=</span> TestAc.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getSimpleName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> ICloudManager manager <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000066; font-weight: bold;">void</span> onCreate<span style="color: #009900;">&#40;</span>Bundle savedInstanceState<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onCreate</span><span style="color: #009900;">&#40;</span>savedInstanceState<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        setContentView<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">layout</span>.<span style="color: #006633;">main</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"[ThreadId "</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> 
                  <span style="color: #339933;">+</span> <span style="color: #0000ff;">"] [ProcessId"</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Process</span>.<span style="color: #006633;">myPid</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">"]  onCreate"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        findViewById<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">id</span>.<span style="color: #006633;">btn_print</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setOnClickListener</span><span style="color: #009900;">&#40;</span>
          <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">View</span>.<span style="color: #006633;">OnClickListener</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            @Override
            <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onClick<span style="color: #009900;">&#40;</span><span style="color: #003399;">View</span> v<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                    Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"=========== Client call CloudService"</span>
                               <span style="color: #339933;">+</span><span style="color: #0000ff;">" print function"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    manager.<span style="color: #006633;">print</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Hello world"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RemoteException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        findViewById<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">id</span>.<span style="color: #006633;">btn_add</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setOnClickListener</span><span style="color: #009900;">&#40;</span>
        <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">View</span>.<span style="color: #006633;">OnClickListener</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            @Override
            <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onClick<span style="color: #009900;">&#40;</span><span style="color: #003399;">View</span> v<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                    Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"======Client call CloudService"</span>
                               <span style="color: #339933;">+</span><span style="color: #0000ff;">" add function"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #000066; font-weight: bold;">int</span> a <span style="color: #339933;">=</span> manager.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">3</span>, <span style="color: #cc66cc;">2</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"======Client add function reuslt : "</span>
                                <span style="color: #339933;">+</span> a<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RemoteException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        findViewById<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">id</span>.<span style="color: #006633;">btn_test</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setOnClickListener</span><span style="color: #009900;">&#40;</span>
          <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">View</span>.<span style="color: #006633;">OnClickListener</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            @Override
            <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onClick<span style="color: #009900;">&#40;</span><span style="color: #003399;">View</span> v<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                    Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"======Client call CloudService"</span>
                               <span style="color: #339933;">+</span><span style="color: #0000ff;">" test function"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    manager.<span style="color: #006633;">test</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RemoteException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000066; font-weight: bold;">void</span> onStart<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onStart</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        IBinder binder <span style="color: #339933;">=</span> ServiceManager.<span style="color: #006633;">getService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"cloudservice"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        manager <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> CloudManagerProxy<span style="color: #009900;">&#40;</span>binder<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        findViewById<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">id</span>.<span style="color: #006633;">btn_print</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setEnabled</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        findViewById<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">id</span>.<span style="color: #006633;">btn_add</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setEnabled</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        findViewById<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">id</span>.<span style="color: #006633;">btn_test</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setEnabled</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000066; font-weight: bold;">void</span> onStop<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onStop</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000066; font-weight: bold;">void</span> onDestroy<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
&nbsp;
        <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onDestroy</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

## 4.测试

上传程序：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="text" style="font-family:monospace;">adb push native_bclient /system/bin
adb push native_bserver /system/bin
adb push fclient /system/bin
adb push fclient.jar /system/framework
adb shell chmod 755 /system/bin/native_bserver
adb shell chmod 755 /system/bin/native_bclient
adb shell chmod 755 /system/bin/fclient</pre>
      </td>
    </tr>
  </table>
</div>

使用native_client测试：

[<img src="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest.png" alt="nativetest" width="873" height="246" class="alignnone size-full wp-image-480" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest.png 873w, http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest-300x84.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest-200x56.png 200w" sizes="(max-width: 873px) 100vw, 873px" />](http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest.png)

使用框架层的client测试：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/frameworktest.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/frameworktest.png" alt="frameworktest" width="989" height="204" class="alignnone size-full wp-image-476" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/frameworktest.png 989w, http://www.cloudchou.com/wp-content/uploads/2014/04/frameworktest-300x61.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/frameworktest-200x41.png 200w" sizes="(max-width: 989px) 100vw, 989px" /></a>

使用应用层的client测试：

服务端： 

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_server.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_server.png" alt="apptest_server" width="621" height="213" class="alignnone size-full wp-image-478" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_server.png 621w, http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_server-300x102.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_server-200x68.png 200w" sizes="(max-width: 621px) 100vw, 621px" /></a>

客户端：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_client.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_client.png" alt="apptest_client" width="781" height="165" class="alignnone size-full wp-image-477" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_client.png 781w, http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_client-300x63.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_client-200x42.png 200w" sizes="(max-width: 781px) 100vw, 781px" /></a>