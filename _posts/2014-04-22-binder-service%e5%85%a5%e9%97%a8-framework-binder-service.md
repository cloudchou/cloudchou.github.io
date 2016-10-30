---
id: 447
title: 'Binder service入门—Framework  binder service'
date: 2014-04-22T01:18:53+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=447
permalink: /android/post-447.html
views:
  - 5591
categories:
  - Android
tags:
  - android binder example
  - android binder framework example
  - android binder 使用
  - android binder 入门
  - android binder 实例
---
## 1.前言

Binder service入门系列：

  * Binder service入门–创建native binder service:   
    <a href="http://www.cloudchou.com/android/post-332.html" target="_blank">http://www.cloudchou.com/android/post-332.html</a>
  * Binder service入门—应用层binder service:   
    <a href="http://www.cloudchou.com/android/post-458.html" target="_blank">http://www.cloudchou.com/android/post-458.html</a>
  * Binder service入门—框架层、应用层调用native binder service:   
    <a href="http://www.cloudchou.com/android/post-468.html" target="_blank">http://www.cloudchou.com/android/post-468.html</a>

上一篇介绍了natvie binder Service，本篇将介绍如何创建框架层binder service，并交给ServiceManager管理，客户端通过ServiceManager获取binder service的引用，然后测试binder service。

## 2.程序构成

Framework程序的开发必须要在源码开发环境下，本示例在vendor目录下建立了子目录shuame，然后把工程放在该目录下。

整个工程都可以在github上下载： <a href="https://github.com/cloudchou/FrameworkBinderTest" target="_blank">https://github.com/cloudchou/FrameworkBinderTest</a> 

程序由服务端和客户端组成，服务端包括启动服务端的shell脚本bserver和放在framework目录的bserver.jar，客户端包括启动客户端的shell脚本bclient和放在framework目录的bclient.jar。

服务端 Android.mk如下所示：

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
<span style="color: #339900; font-style: italic;">#生成framwork目录下的库bserver.jar</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> all<span style="color: #004400;">-</span>subdir<span style="color: #004400;">-</span>java<span style="color: #004400;">-</span>files<span style="color: #004400;">&#41;</span>
LOCAL_MODULE <span style="color: #004400;">:=</span> bserver 
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_JAVA_LIBRARY</span><span style="color: #004400;">&#41;</span>
<span style="color: #339900; font-style: italic;">#生成system/bin目录下的shell脚本bserver </span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_MODULE <span style="color: #004400;">:=</span> bserver
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
LOCAL_MODULE_PATH <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_OUT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">/</span>bin
LOCAL_MODULE_CLASS <span style="color: #004400;">:=</span> UTILITY_EXECUTABLES
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> bserver
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_PREBUILT</span><span style="color: #004400;">&#41;</span></pre>
      </td>
    </tr>
  </table>
</div>

客户端Android.mk如下所示：

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
&nbsp;
<span style="color: #339900; font-style: italic;">#生成framwork目录下的库bclient.jar</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> all<span style="color: #004400;">-</span>subdir<span style="color: #004400;">-</span>java<span style="color: #004400;">-</span>files<span style="color: #004400;">&#41;</span>
LOCAL_MODULE <span style="color: #004400;">:=</span> bclient 
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_JAVA_LIBRARY</span><span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #339900; font-style: italic;">#生成system/bin目录下的shell脚本bclient</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_MODULE <span style="color: #004400;">:=</span> bclient
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
LOCAL_MODULE_PATH <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_OUT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">/</span>bin
LOCAL_MODULE_CLASS <span style="color: #004400;">:=</span> UTILITY_EXECUTABLES
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> bclient
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_PREBUILT</span><span style="color: #004400;">&#41;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 3.程序源码构成

程序源码构成如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_fbs.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_fbs-1024x470.png" alt="framework_fbs" width="1024" height="470" class="alignnone size-large wp-image-452" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_fbs-1024x470.png 1024w, http://www.cloudchou.com/wp-content/uploads/2014/04/framework_fbs-300x137.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/framework_fbs-200x91.png 200w, http://www.cloudchou.com/wp-content/uploads/2014/04/framework_fbs.png 1559w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

整个程序由服务端和客户端两部分组成，分别放在bserver和bclient目录，顶层目录只有一个Android.mk，该Android.mk的内容如下所示：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
</pre>
      </td>
      
      <td class="code">
        <pre class="make" style="font-family:monospace;"><span style="color: #339900; font-style: italic;">#包含所有子目录的makefiles，这样在顶层目录就可以编译所有模块</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> all<span style="color: #004400;">-</span>subdir<span style="color: #004400;">-</span>makefiles<span style="color: #004400;">&#41;</span></pre>
      </td>
    </tr>
  </table>
</div>

ICloudManager:服务端和客户端共用同一个接口文件ICloudManager.java，这里通过软链接实现共用，该接口声明了binder service供外界调用的方法。

CloudManager:binder service实体类，接收客户端的调用，进行相关逻辑处理后返回结果给客户端

BServer: 创建CloudManage对象，并调用ServiceManager注册binder service

CloudManagerProxy: binder service引用类，其实是binder service在客户端的代理，客户端通过该类调用服务端的操作

BClient: 测试binder service的客户端，先通过ServiceManager获取binder对象，然后再利用它创建CloudManagerProxy对象，通过CloudManagerProxy对象调用服务端的操

### 实现Framework binder service的步骤

  * 1) 定义binder service接口ICloudManager以及binder service的描述字符串，并为接口里的每个方法声明对应的操作常量：
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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">interface</span> ICloudManager <span style="color: #000000; font-weight: bold;">extends</span> IInterface <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//binder sevice的描述字符串</span>
  <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> DESCRIPTOR <span style="color: #339933;">=</span> <span style="color: #0000ff;">"com.cloud.test.BServer"</span><span style="color: #339933;">;</span>
  <span style="color: #666666; font-style: italic;">//操作</span>
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #339933;">;</span>
  <span style="color: #666666; font-style: italic;">//操作常量</span>
  <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_print <span style="color: #339933;">=</span> 
         <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_add <span style="color: #339933;">=</span> 
        <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

声明binder service接口时必须从IInterface继承，IInterface接口如下所示：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">interface</span> IInterface
<span style="color: #009900;">&#123;</span>
    <span style="color: #008000; font-style: italic; font-weight: bold;">/**
     * Retrieve the Binder object associated with this interface.
     * You must use this instead of a plain cast, so that proxy objects
     * can return the correct result.
     */</span>
    <span style="color: #000000; font-weight: bold;">public</span> IBinder asBinder<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

IInterface声明了asBinder方法，用于转为Binder对象。

  * 2) 实现binder service实体类CloudManager
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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> CloudManager <span style="color: #000000; font-weight: bold;">extends</span> Binder <span style="color: #000000; font-weight: bold;">implements</span> ICloudManager <span style="color: #009900;">&#123;</span>  
   <span style="color: #000000; font-weight: bold;">public</span> CloudManager<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//保存 binder service描述字符串</span>
      <span style="color: #000000; font-weight: bold;">this</span>.<span style="color: #006633;">attachInterface</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span>, DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span>
&nbsp;
   @Override
   <span style="color: #000000; font-weight: bold;">public</span> IBinder asBinder<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000000; font-weight: bold;">this</span><span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #666666; font-style: italic;">//静态方法 转为ICloudManager接口对象</span>
   <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span> asInterface<span style="color: #009900;">&#40;</span>
         android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> obj<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>obj <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
      android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IInterface</span> iin <span style="color: #339933;">=</span> obj.<span style="color: #006633;">queryLocalInterface</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>iin <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&&</span> 
          <span style="color: #009900;">&#40;</span>iin <span style="color: #000000; font-weight: bold;">instanceof</span> com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span><span style="color: #009900;">&#41;</span> iin<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #666666; font-style: italic;">//接收客户端的调用，根据不同的操作码进行不同的处理，然后返回结果给客户端</span>
   @Override
   <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000066; font-weight: bold;">boolean</span> onTransact<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> code, Parcel data, 
                            Parcel reply, <span style="color: #000066; font-weight: bold;">int</span> flags<span style="color: #009900;">&#41;</span>
         <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">switch</span> <span style="color: #009900;">&#40;</span>code<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">case</span> INTERFACE_TRANSACTION<span style="color: #339933;">:</span> <span style="color: #009900;">&#123;</span>
         reply.<span style="color: #006633;">writeString</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #000000; font-weight: bold;">case</span> TRANSACTION_print<span style="color: #339933;">:</span> <span style="color: #009900;">&#123;</span>
         data.<span style="color: #006633;">enforceInterface</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         <span style="color: #003399;">String</span> str <span style="color: #339933;">=</span> data.<span style="color: #006633;">readString</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         print<span style="color: #009900;">&#40;</span>str<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         reply.<span style="color: #006633;">writeNoException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #000000; font-weight: bold;">case</span> TRANSACTION_add<span style="color: #339933;">:</span> <span style="color: #009900;">&#123;</span>
         data.<span style="color: #006633;">enforceInterface</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         <span style="color: #000066; font-weight: bold;">int</span> a <span style="color: #339933;">=</span> data.<span style="color: #006633;">readInt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         <span style="color: #000066; font-weight: bold;">int</span> b <span style="color: #339933;">=</span> data.<span style="color: #006633;">readInt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         <span style="color: #000066; font-weight: bold;">int</span> c <span style="color: #339933;">=</span> add<span style="color: #009900;">&#40;</span>a, b<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         reply.<span style="color: #006633;">writeNoException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         reply.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>c<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onTransact</span><span style="color: #009900;">&#40;</span>code, data, reply, flags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span>
&nbsp;
   @Override
   <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>str<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span>
&nbsp;
   @Override
   <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">return</span> a <span style="color: #339933;">+</span> b<span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

注意必须从Binder继承，并实现ICloudManager接口

  * 3) 实现服务端 BServer，创建CloudManager对象，并通过ServiceManager注册服务
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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> BServer <span style="color: #009900;">&#123;</span>
   <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> main<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> args<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Cloud Manager Service Starts"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//准备Looper</span>
      Looper.<span style="color: #006633;">prepareMainLooper</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>         
      android.<span style="color: #006633;">os</span>.<span style="color: #003399;">Process</span>.<span style="color: #006633;">setThreadPriority</span><span style="color: #009900;">&#40;</span>
                android.<span style="color: #006633;">os</span>.<span style="color: #003399;">Process</span>.<span style="color: #006633;">THREAD_PRIORITY_FOREGROUND</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//注册binder service</span>
      ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"CloudService"</span>, <span style="color: #000000; font-weight: bold;">new</span> CloudManager<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//进入Looper死循环，</span>
      Looper.<span style="color: #006633;">loop</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 4) 实现服务端脚本bserver
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
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">base</span>=<span style="color: #000000; font-weight: bold;">/</span>system
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">CLASSPATH</span>=<span style="color: #007800;">$base</span><span style="color: #000000; font-weight: bold;">/</span>framework<span style="color: #000000; font-weight: bold;">/</span>bserver.jar
<span style="color: #666666; font-style: italic;">#调用app_process启动BServer</span>
<span style="color: #7a0874; font-weight: bold;">exec</span> app_process <span style="color: #007800;">$base</span><span style="color: #000000; font-weight: bold;">/</span>bin com.cloud.test.BServer <span style="color: #ff0000;">"$@"</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 5) 实现binder service引用类CloudManagerProxy
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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> CloudManagerProxy <span style="color: #000000; font-weight: bold;">implements</span> ICloudManager <span style="color: #009900;">&#123;</span>
   <span style="color: #000000; font-weight: bold;">private</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> mRemote<span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//保存通过ServiceManager查询服务得到的IBinder对象</span>
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
      <span style="color: #000066; font-weight: bold;">int</span> result<span style="color: #339933;">=</span><span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
         _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         _data.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>a<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         _data.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>b<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span>TRANSACTION_add, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
         result<span style="color: #339933;">=</span>_reply.<span style="color: #006633;">readInt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
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
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

接口方法的实现实际上是通过调用IBinder对象的transact方法将调用参数传递给服务端，然后读取服务端返回的结果，再返回给接口方法的调用者。

  * 6) 实现客户端BClient
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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> BClient <span style="color: #009900;">&#123;</span> 
&nbsp;
   <span style="color: #008000; font-style: italic; font-weight: bold;">/** 
    * 
    * @param args
    *            The command-line arguments
    * @throws RemoteException
    */</span>
   <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> main<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> args<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"==========Client starts==========="</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
       <span style="color: #666666; font-style: italic;">//通过ServiceManager查询服务获得IBinder对象</span>
      IBinder binder <span style="color: #339933;">=</span> ServiceManager.<span style="color: #006633;">getService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"CloudService"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//创建CloudManagerProxy对象</span>
      ICloudManager manager <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> CloudManagerProxy<span style="color: #009900;">&#40;</span>binder<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//通过CloudManagerProxy对象调用接口的方法</span>
      manager.<span style="color: #006633;">print</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Hello world"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #000066; font-weight: bold;">int</span> result <span style="color: #339933;">=</span> manager.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">2</span>, <span style="color: #cc66cc;">3</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"manager.add(2, 3)="</span> <span style="color: #339933;">+</span> result<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 7) 实现客户端脚本bclient
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
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">base</span>=<span style="color: #000000; font-weight: bold;">/</span>system
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">CLASSPATH</span>=<span style="color: #007800;">$base</span><span style="color: #000000; font-weight: bold;">/</span>framework<span style="color: #000000; font-weight: bold;">/</span>bclient.jar
<span style="color: #666666; font-style: italic;">#调用app_process启动Bclient</span>
<span style="color: #7a0874; font-weight: bold;">exec</span> app_process <span style="color: #007800;">$base</span><span style="color: #000000; font-weight: bold;">/</span>bin com.cloud.test.BClient <span style="color: #ff0000;">"$@"</span></pre>
      </td>
    </tr>
  </table>
</div>

## 4.测试

编译时若提示错误，缺少framwork之类的jar，可先用mka framework编译framework，编译好之后再使用mm进行模块编译。

编译好之后将相关文件上传至手机并修改权限：

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
        <pre class="text" style="font-family:monospace;">adb push bserver /system/bin
adb push bclient /system/bin
adb push bserver.jar /system/framework
adb push bclient.jar /system/framework
adb shell chmod 755 /system/bin/bserver
adb shell chmod 755 /system/bin/bclient</pre>
      </td>
    </tr>
  </table>
</div>

测试：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/framework\_test.png" external\_blank><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_test-1024x229.png" alt="framework_test" width="1024" height="229" class="alignnone size-large wp-image-453" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_test-1024x229.png 1024w, http://www.cloudchou.com/wp-content/uploads/2014/04/framework_test-300x67.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/framework_test-200x44.png 200w, http://www.cloudchou.com/wp-content/uploads/2014/04/framework_test.png 1052w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>