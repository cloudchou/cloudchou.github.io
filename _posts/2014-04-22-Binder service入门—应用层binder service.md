---
id: 458
title: Binder service入门—应用层binder service
date: 2014-04-22T01:20:12+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=458
permalink: /android/post-458.html
views:
  - 5165
categories:
  - Android
tags:
  - android binder example
  - android binder 使用
  - android binder 入门
  - android binder 实例
  - android 应用层 binder
---
## 1.前言

Binder service入门系列：

  * Binder service入门–创建native binder service:   
    <a href="http://www.cloudchou.com/android/post-332.html" target="_blank">http://www.cloudchou.com/android/post-332.html</a>
  * Binder service入门—Framework binder service:   
    <a href="http://www.cloudchou.com/android/post-447.html" target="_blank">http://www.cloudchou.com/android/post-447.html</a>
  * Binder service入门—框架层、应用层调用native binder service:   
    <a href="http://www.cloudchou.com/android/post-468.html" target="_blank">http://www.cloudchou.com/android/post-468.html</a>

上一篇介绍了Framework Binder Service，本篇将介绍如何创建应用层的binder service。 实际上在应用层使用binder service时，并没有直接与ServiceManager交互(应用层不能直接使用ServiceManager 类)，一般是在Service子类里覆盖onBind方法，返回新创建的Binder实体对象。应用层使用Activity作为binder service的客户端，在Activity里创建ServiceConnecttion对象，并调用bindService方法绑定service，在ServiceConnection的onServiceConnected方法将接收到的IBinder对象转化为接口对象，然后再通过这个接口对象调用binder service的接口方法。

## 2.程序构成

程序在应用开发环境下编译。

整个工程可以在github上下载： <a href="https://github.com/cloudchou/AndroidBinderTest" target="_blank">https://github.com/cloudchou/AndroidBinderTest</a>

本示例使用remote service，声明service时，使用了android:process属性。

## 3.程序源码构成

源代码结构如下所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/app_f.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/app_f.png" alt="app_f" width="284" height="370" class="alignnone size-full wp-image-464" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/app_f.png 284w, http://www.cloudchou.com/wp-content/uploads/2014/04/app_f-230x300.png 230w, http://www.cloudchou.com/wp-content/uploads/2014/04/app_f-115x150.png 115w" sizes="(max-width: 284px) 100vw, 284px" /></a>

AndroidManifeset.xml：声明用到的activity，service组件

ICloudManager.aidl： binder service接口

CloudService: 创建binder service，并返回给客户端

TestAc: 测试binder service的客户端

### 实现应用层 binder service的步骤

  * 1) 使用aidl定义binder service接口ICloudManager
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
        <pre class="text" style="font-family:monospace;">package com.cloud.test;
interface ICloudManager{
    void print(String str) ;
    int add(int a, int b);
}</pre>
      </td>
    </tr>
  </table>
</div>

aidl全称是android interface definition language，用于定义binder service接口，语法与Java的接口非常类似，详情可参考：<a href="http://developer.android.com/guide/components/aidl.html" target="_blank">http://developer.android.com/guide/components/aidl.html</a>

使用eclipse开发时，它会被自动编译成ICloudManager.java，放在gen目录下。生成的ICloudManager.java源码如下所示：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//声明接口ICloudManager 继承自IInterface，这里和在Framework使用binder service类似</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">interface</span> ICloudManager <span style="color: #000000; font-weight: bold;">extends</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IInterface</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #008000; font-style: italic; font-weight: bold;">/**binder service实体类和framework的binder service实体类类似 */</span>
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">abstract</span> <span style="color: #000000; font-weight: bold;">class</span> <span style="color: #003399;">Stub</span> <span style="color: #000000; font-weight: bold;">extends</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Binder</span> <span style="color: #000000; font-weight: bold;">implements</span> com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> DESCRIPTOR <span style="color: #339933;">=</span> <span style="color: #0000ff;">"com.cloud.test.ICloudManager"</span><span style="color: #339933;">;</span>
&nbsp;
        <span style="color: #008000; font-style: italic; font-weight: bold;">/** Construct the stub at attach it to the interface. */</span>
        <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">Stub</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">this</span>.<span style="color: #006633;">attachInterface</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span>, DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        <span style="color: #008000; font-style: italic; font-weight: bold;">/**
         * Cast an IBinder object into an com.cloud.test.ICloudManager interface, generating a proxy if needed.
         */</span>
        <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span> asInterface<span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> obj<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>obj <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IInterface</span> iin <span style="color: #339933;">=</span> obj.<span style="color: #006633;">queryLocalInterface</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>iin <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>iin <span style="color: #000000; font-weight: bold;">instanceof</span> com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span><span style="color: #009900;">&#41;</span> iin<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000000; font-weight: bold;">new</span> com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span>.<span style="color: #003399;">Stub</span>.<span style="color: #003399;">Proxy</span><span style="color: #009900;">&#40;</span>obj<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        @Override
        <span style="color: #000000; font-weight: bold;">public</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> asBinder<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000000; font-weight: bold;">this</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        @Override
        <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">boolean</span> onTransact<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> code, android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> data, android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> reply, <span style="color: #000066; font-weight: bold;">int</span> flags<span style="color: #009900;">&#41;</span>
                <span style="color: #000000; font-weight: bold;">throws</span> android.<span style="color: #006633;">os</span>.<span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">switch</span> <span style="color: #009900;">&#40;</span>code<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">case</span> INTERFACE_TRANSACTION<span style="color: #339933;">:</span> <span style="color: #009900;">&#123;</span>
                reply.<span style="color: #006633;">writeString</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">case</span> TRANSACTION_print<span style="color: #339933;">:</span> <span style="color: #009900;">&#123;</span>
                data.<span style="color: #006633;">enforceInterface</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> _arg0<span style="color: #339933;">;</span>
                _arg0 <span style="color: #339933;">=</span> data.<span style="color: #006633;">readString</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">this</span>.<span style="color: #006633;">print</span><span style="color: #009900;">&#40;</span>_arg0<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                reply.<span style="color: #006633;">writeNoException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">case</span> TRANSACTION_add<span style="color: #339933;">:</span> <span style="color: #009900;">&#123;</span>
                data.<span style="color: #006633;">enforceInterface</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000066; font-weight: bold;">int</span> _arg0<span style="color: #339933;">;</span>
                _arg0 <span style="color: #339933;">=</span> data.<span style="color: #006633;">readInt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000066; font-weight: bold;">int</span> _arg1<span style="color: #339933;">;</span>
                _arg1 <span style="color: #339933;">=</span> data.<span style="color: #006633;">readInt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000066; font-weight: bold;">int</span> _result <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">this</span>.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span>_arg0, _arg1<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                reply.<span style="color: #006633;">writeNoException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                reply.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>_result<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onTransact</span><span style="color: #009900;">&#40;</span>code, data, reply, flags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        <span style="color: #666666; font-style: italic;">//binder service的引用类，或者说是代理，和framework使用binder service类似</span>
        <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">class</span> <span style="color: #003399;">Proxy</span> <span style="color: #000000; font-weight: bold;">implements</span> com.<span style="color: #006633;">cloud</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">ICloudManager</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">private</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> mRemote<span style="color: #339933;">;</span>
&nbsp;
            <span style="color: #003399;">Proxy</span><span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> remote<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                mRemote <span style="color: #339933;">=</span> remote<span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
&nbsp;
            @Override
            <span style="color: #000000; font-weight: bold;">public</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span> asBinder<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">return</span> mRemote<span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
&nbsp;
            <span style="color: #000000; font-weight: bold;">public</span> java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> getInterfaceDescriptor<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">return</span> DESCRIPTOR<span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
&nbsp;
            @Override
            <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span>java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> android.<span style="color: #006633;">os</span>.<span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
                android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _data <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _reply <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                    _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    _data.<span style="color: #006633;">writeString</span><span style="color: #009900;">&#40;</span>str<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Stub</span>.<span style="color: #006633;">TRANSACTION_print</span>, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
                    _reply.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    _data.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
&nbsp;
            @Override
            <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> android.<span style="color: #006633;">os</span>.<span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
                android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _data <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span> _reply <span style="color: #339933;">=</span> android.<span style="color: #006633;">os</span>.<span style="color: #006633;">Parcel</span>.<span style="color: #006633;">obtain</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000066; font-weight: bold;">int</span> _result<span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                    _data.<span style="color: #006633;">writeInterfaceToken</span><span style="color: #009900;">&#40;</span>DESCRIPTOR<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    _data.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>a<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    _data.<span style="color: #006633;">writeInt</span><span style="color: #009900;">&#40;</span>b<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    mRemote.<span style="color: #006633;">transact</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Stub</span>.<span style="color: #006633;">TRANSACTION_add</span>, _data, _reply, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    _reply.<span style="color: #006633;">readException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    _result <span style="color: #339933;">=</span> _reply.<span style="color: #006633;">readInt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
                    _reply.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    _data.<span style="color: #006633;">recycle</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #000000; font-weight: bold;">return</span> _result<span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_print <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> TRANSACTION_add <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">os</span>.<span style="color: #006633;">IBinder</span>.<span style="color: #006633;">FIRST_CALL_TRANSACTION</span> <span style="color: #339933;">+</span> <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span>java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> android.<span style="color: #006633;">os</span>.<span style="color: #003399;">RemoteException</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> android.<span style="color: #006633;">os</span>.<span style="color: #003399;">RemoteException</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

由此可见应用层使用binder service实际上和framework使用binder service是非常类似的，只是在应用层使用binder service时，只需编写aidl，开发工具可帮我们自动编译生成java源码文件，该源文件里包含接口，binder service实体类(抽象类，接口方法还未实现)，binder service引用类的源码。

  * 2) 实现Service
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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> CloudService <span style="color: #000000; font-weight: bold;">extends</span> Service <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> TAG <span style="color: #339933;">=</span> CloudService.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getSimpleName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
  <span style="color: #666666; font-style: italic;">//实现binder service实体类</span>
  <span style="color: #000000; font-weight: bold;">class</span> CloudMananger <span style="color: #000000; font-weight: bold;">extends</span> ICloudManager.<span style="color: #003399;">Stub</span> <span style="color: #009900;">&#123;</span>
&nbsp;
      @Override
      <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> print<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> str<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
          Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"[ThreadId "</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> 
                     <span style="color: #339933;">+</span> <span style="color: #0000ff;">"] [ProcessId"</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Process</span>.<span style="color: #006633;">myPid</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>
                     <span style="color: #339933;">+</span> <span style="color: #0000ff;">"]CloudService receive client print msg request: "</span> 
                     <span style="color: #339933;">+</span> str<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
&nbsp;
      @Override
      <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">int</span> add<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> a, <span style="color: #000066; font-weight: bold;">int</span> b<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
          Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"[ThreadId "</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> 
                      <span style="color: #339933;">+</span> <span style="color: #0000ff;">"] [ProcessId"</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Process</span>.<span style="color: #006633;">myPid</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>
                      <span style="color: #339933;">+</span> <span style="color: #0000ff;">"[CloudService receive client add request : "</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">return</span> a <span style="color: #339933;">+</span> b<span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
  @Override
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onCreate<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onCreate</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"[ThreadId "</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> 
                 <span style="color: #339933;">+</span> <span style="color: #0000ff;">"] [ProcessId"</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Process</span>.<span style="color: #006633;">myPid</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">"]  onCreate"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
 <span style="color: #666666; font-style: italic;">//定义binder service实体类对象</span>
  <span style="color: #000000; font-weight: bold;">private</span> CloudMananger manager <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> CloudMananger<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
 <span style="color: #666666; font-style: italic;">//覆盖onBind方法，返回binder service实体类对象</span>
  @Override
  <span style="color: #000000; font-weight: bold;">public</span> IBinder onBind<span style="color: #009900;">&#40;</span>Intent intent<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"[ThreadId "</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> 
                 <span style="color: #339933;">+</span> <span style="color: #0000ff;">"] [ProcessId"</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Process</span>.<span style="color: #006633;">myPid</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">"]  onBind"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">return</span> manager<span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 3) 实现Client
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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> TestAc <span style="color: #000000; font-weight: bold;">extends</span> Activity <span style="color: #009900;">&#123;</span>
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
                    Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"=========== Client call "</span>
                               <span style="color: #339933;">+</span><span style="color: #0000ff;">"CloudService print function"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #666666; font-style: italic;">//调用print方法</span>
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
                    Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"======Client call "</span>
                               <span style="color: #339933;">+</span><span style="color: #0000ff;">"CloudService add function"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #000066; font-weight: bold;">int</span> a <span style="color: #339933;">=</span> manager.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">3</span>, <span style="color: #cc66cc;">2</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"======Client add function reuslt : "</span> <span style="color: #339933;">+</span> a<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
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
        <span style="color: #666666; font-style: italic;">//绑定 remote service</span>
        Intent intent <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Intent<span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span>, CloudService.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        bindService<span style="color: #009900;">&#40;</span>intent, connection, BIND_AUTO_CREATE<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000066; font-weight: bold;">void</span> onStop<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">onStop</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        unbindService<span style="color: #009900;">&#40;</span>connection<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//和remote service绑定时用的ServiceConnection对象</span>
    <span style="color: #000000; font-weight: bold;">private</span> ServiceConnection connection <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ServiceConnection<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
&nbsp;
        @Override
        <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onServiceDisconnected<span style="color: #009900;">&#40;</span>ComponentName name<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"[ThreadId "</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> 
                       <span style="color: #339933;">+</span> <span style="color: #0000ff;">"] [ProcessId"</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Process</span>.<span style="color: #006633;">myPid</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>
                       <span style="color: #339933;">+</span> <span style="color: #0000ff;">"]  onServiceDisconnected"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        @Override
        <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onServiceConnected<span style="color: #009900;">&#40;</span>ComponentName name, IBinder service<span style="color: #009900;">&#41;</span>
        <span style="color: #009900;">&#123;</span>
            Log.<span style="color: #006633;">d</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"[ThreadId "</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> 
                       <span style="color: #339933;">+</span> <span style="color: #0000ff;">"] [ProcessId"</span> <span style="color: #339933;">+</span> <span style="color: #003399;">Process</span>.<span style="color: #006633;">myPid</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>
                       <span style="color: #339933;">+</span> <span style="color: #0000ff;">"]  onServiceConnected"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #666666; font-style: italic;">//将IBinder对象转为ICloudManager接口对象，实际上是创建了一个代理对象</span>
            manager <span style="color: #339933;">=</span> ICloudManager.<span style="color: #003399;">Stub</span>.<span style="color: #006633;">asInterface</span><span style="color: #009900;">&#40;</span>service<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            findViewById<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">id</span>.<span style="color: #006633;">btn_print</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setEnabled</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            findViewById<span style="color: #009900;">&#40;</span>R.<span style="color: #006633;">id</span>.<span style="color: #006633;">btn_add</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">setEnabled</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span><span style="color: #339933;">;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 4) AndroidManifest.xml，声明程序组件Activity和Service
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
</pre>
      </td>
      
      <td class="code">
        <pre class="xml" style="font-family:monospace;"><span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;manifest</span> <span style="color: #000066;">xmlns:android</span>=<span style="color: #ff0000;">"http://schemas.android.com/apk/res/android"</span></span>
<span style="color: #009900;">    <span style="color: #000066;">package</span>=<span style="color: #ff0000;">"com.cloud.test"</span></span>
<span style="color: #009900;">    <span style="color: #000066;">android:versionCode</span>=<span style="color: #ff0000;">"1"</span></span>
<span style="color: #009900;">    <span style="color: #000066;">android:versionName</span>=<span style="color: #ff0000;">"1.0"</span> <span style="color: #000000; font-weight: bold;">&gt;</span></span>
&nbsp;
    <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;uses-sdk</span></span>
<span style="color: #009900;">        <span style="color: #000066;">android:minSdkVersion</span>=<span style="color: #ff0000;">"15"</span></span>
<span style="color: #009900;">        <span style="color: #000066;">android:targetSdkVersion</span>=<span style="color: #ff0000;">"15"</span> <span style="color: #000000; font-weight: bold;">/&gt;</span></span>
&nbsp;
    <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;application</span></span>
<span style="color: #009900;">        <span style="color: #000066;">android:allowBackup</span>=<span style="color: #ff0000;">"true"</span></span>
<span style="color: #009900;">        <span style="color: #000066;">android:icon</span>=<span style="color: #ff0000;">"@drawable/ic_launcher"</span></span>
<span style="color: #009900;">        <span style="color: #000066;">android:label</span>=<span style="color: #ff0000;">"@string/app_name"</span></span>
<span style="color: #009900;">        <span style="color: #000066;">android:theme</span>=<span style="color: #ff0000;">"@style/AppTheme"</span> <span style="color: #000000; font-weight: bold;">&gt;</span></span>
        <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;activity</span> <span style="color: #000066;">android:name</span>=<span style="color: #ff0000;">".TestAc"</span> <span style="color: #000000; font-weight: bold;">&gt;</span></span>
            <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;intent-filter<span style="color: #000000; font-weight: bold;">&gt;</span></span></span>
                <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;action</span> <span style="color: #000066;">android:name</span>=<span style="color: #ff0000;">"android.intent.action.MAIN"</span> <span style="color: #000000; font-weight: bold;">/&gt;</span></span>
                <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;category</span> <span style="color: #000066;">android:name</span>=<span style="color: #ff0000;">"android.intent.category.LAUNCHER"</span><span style="color: #000000; font-weight: bold;">/&gt;</span></span>
            <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;/intent-filter<span style="color: #000000; font-weight: bold;">&gt;</span></span></span>
        <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;/activity<span style="color: #000000; font-weight: bold;">&gt;</span></span></span>
        <span style="color: #009900;">&lt;!—remote service--<span style="color: #000000; font-weight: bold;">&gt;</span></span>
        <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;service</span></span>
<span style="color: #009900;">            <span style="color: #000066;">android:name</span>=<span style="color: #ff0000;">".CloudService"</span></span>
<span style="color: #009900;">            <span style="color: #000066;">android:enabled</span>=<span style="color: #ff0000;">"true"</span></span>
<span style="color: #009900;">            <span style="color: #000066;">android:process</span>=<span style="color: #ff0000;">":remote"</span> <span style="color: #000000; font-weight: bold;">/&gt;</span></span>
    <span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;/application<span style="color: #000000; font-weight: bold;">&gt;</span></span></span>
&nbsp;
<span style="color: #009900;"><span style="color: #000000; font-weight: bold;">&lt;/manifest<span style="color: #000000; font-weight: bold;">&gt;</span></span></span></pre>
      </td>
    </tr>
  </table>
</div>

## 4.测试

  * 运行apk程序：
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/app_test.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/app_test-1024x229.png" alt="app_test" width="1024" height="229" class="alignnone size-large wp-image-465" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/app_test-1024x229.png 1024w, http://www.cloudchou.com/wp-content/uploads/2014/04/app_test-300x67.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/app_test-200x44.png 200w, http://www.cloudchou.com/wp-content/uploads/2014/04/app_test.png 1034w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>