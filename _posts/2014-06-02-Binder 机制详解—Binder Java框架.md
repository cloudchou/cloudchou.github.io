---
id: 558
title: Binder 机制详解—Binder Java框架
date: 2014-06-02T23:29:14+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=558
permalink: /android/post-558.html
views:
  - 9500
categories:
  - Android
tags:
  - android binder机制
  - android binder设计与实现
  - android service binder
  - Binder Java框架
  - Binder 机制详解
---
上一篇博客介绍了 Binder本地框架层，本篇博客将介绍Binder的java层框架。

## Binder的java层框架

Binder的Java框架层包含以下类(frameworks/base/core/java/android/os):IBinder，Binder，IInterface，ServiceManagerNative，ServiceManager，BinderInternal，IServiceManager，ServiceManagerProxy。

Binder的Java框架层部分方法的实现在本地代码里，源码位于frameworks/base/core/jni。

先前博客《<a href="http://www.cloudchou.com/android/post-447.html" target="_blank">Binder service入门—Framework binder service</a>》中ICloudMananger与Binder Java 框架层的类图如下图所示(若看不清，请点击看大图):

<a href="http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder_framework.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder_framework-1024x702.png" alt="java_binder_framework" width="1024" height="702" class="aligncenter size-large wp-image-560" srcset="http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder_framework-1024x702.png 1024w, http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder_framework-300x205.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder_framework-200x137.png 200w, http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder_framework.png 1234w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

与Binder本地框架类似，声明的binder service接口必须继承自IInterface，这里ICloudManager继承自IInterface。与Binder 本地框架层不相同的是，Java层的IBinder接口直接继承自IInterface，而本地的IBinder类继承自RefBase。本地的IBinder有两个子类，BBinder和BpBinder，Java层的IBinder接口也有两个子类，Binder和BinderProxy。Java层服务端的CloudManager (binder service实体类) 直接继承自Binder类，并实现了binder service接口ICloudManager，而客户端的CloudManagerProxy类只需实现binder service接口ICloudManager即可。

## Binder java层框架相关 Jni源码

Binder Java层框架类有不少方法是native的，意味着这些native方法是jni方法。Java层框架中的类Binder，BinderProxy，BinderInternal的native方法的实现是在源码frameworks/base/core/jni/android\_util\_Binder.cpp里，Java层框架中Parcel类native方法的实现是在frameworks/base/core/jni/android\_os\_Parcel.cpp里。接下来我们将详细分析android\_util\_Binder.cpp。

### 重要数据结构

  * ### 1) gBinderOffsets，代表android.os.Binder 类
    
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
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">static</span> <span style="color: #0000ff;">struct</span> bindernative_offsets_t
<span style="color: #008000;">&#123;</span>
    <span style="color: #666666;">// 指向class对象android.os.Binder </span>
    jclass mClass<span style="color: #008080;">;</span>
    <span style="color: #666666;">//指向 android.os.Binder的execTransact方法</span>
    jmethodID mExecTransact<span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #666666;">//指向android.os.Binder的mObject字段，</span>
    <span style="color: #666666;">//将用于保存指向JavaBBinderHolder对象的指针</span>
    jfieldID mObject<span style="color: #008080;">;</span>
&nbsp;
<span style="color: #008000;">&#125;</span> gBinderOffsets<span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 2) gBinderInternalOffsets，代表com.android.internal.os.BinderInternal类
    
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
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">static</span> <span style="color: #0000ff;">struct</span> binderinternal_offsets_t
<span style="color: #008000;">&#123;</span>
    <span style="color: #666666;">//指向 class对象com.android.internal.os.BinderInternal</span>
    jclass mClass<span style="color: #008080;">;</span>
    <span style="color: #666666;">//指向BinderInternal的forceGc方法</span>
    jmethodID mForceGc<span style="color: #008080;">;</span>
&nbsp;
<span style="color: #008000;">&#125;</span> gBinderInternalOffsets<span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 3) binderproxy\_offsets\_t，代表android.os.BinderProxy类
    
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
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">static</span> <span style="color: #0000ff;">struct</span> binderproxy_offsets_t
<span style="color: #008000;">&#123;</span>
    <span style="color: #666666;">//指向 class对象android.os.BinderProxy</span>
    jclass mClass<span style="color: #008080;">;</span>
    <span style="color: #666666;">//指向 BinderProxy的构造方法</span>
    jmethodID mConstructor<span style="color: #008080;">;</span>
    <span style="color: #666666;">//指向 BinderProxy的sendDeathNotice方法</span>
    jmethodID mSendDeathNotice<span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #666666;">//指向 BinderProxy的mObject字段</span>
    jfieldID mObject<span style="color: #008080;">;</span>
    <span style="color: #666666;">//指向 BinderProxy的mSelf字段</span>
    jfieldID mSelf<span style="color: #008080;">;</span>
    <span style="color: #666666;">//指向 BinderProxy的mOrgue字段</span>
    jfieldID mOrgue<span style="color: #008080;">;</span>
&nbsp;
<span style="color: #008000;">&#125;</span> gBinderProxyOffsets<span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 4) JavaBBinder和JavaBBinderHolder
    
    JavaBBinder和JavaBBinderHolder相关类类图如下所示(若看不清，请点击看大图)，JavaBBinder继承自本地框架的BBinder，代表binder service服务端实体，而JavaBBinderHolder保存JavaBBinder指针，Java层Binder的mObject保存的是JavaBBinderHolder指针的值，故此这里用聚合关系表示。BinderProxy的mObject保存的是BpBinder对象指针的值，故此这里用聚合关系表示。
    
    <a href="http://www.cloudchou.com/wp-content/uploads/2014/06/binder_java_jni.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/binder_java_jni-1024x687.png" alt="binder_java_jni" width="1024" height="687" class="aligncenter size-large wp-image-561" srcset="http://www.cloudchou.com/wp-content/uploads/2014/06/binder_java_jni-1024x687.png 1024w, http://www.cloudchou.com/wp-content/uploads/2014/06/binder_java_jni-300x201.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/06/binder_java_jni-200x134.png 200w, http://www.cloudchou.com/wp-content/uploads/2014/06/binder_java_jni.png 1471w" sizes="(max-width: 1024px) 100vw, 1024px" /></a> </li> </ul> 
    
    ### 重要函数
    
      * ### 1) javaObjectForIBinder 将本地IBinder对象转为Java层的IBinder对象，实际类型是BinderProxy
        
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
</pre>
              </td>
              
              <td class="code">
                <pre class="cpp" style="font-family:monospace;">jobject javaObjectForIBinder<span style="color: #008000;">&#40;</span>JNIEnv<span style="color: #000040;">*</span> env, <span style="color: #0000ff;">const</span> sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> val<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>val <span style="color: #000080;">==</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">return</span> <span style="color: #0000ff;">NULL</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #666666;">//如果是 binder 服务端进程调用javaObjectForIBinder </span>
    <span style="color: #666666;">//将调用JavaBBinder的object方法返回jobject，</span>
    <span style="color: #666666;">//这里jobject的实际Java类型是Binder</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>val<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>checkSubclass<span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>gBinderOffsets<span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #666666;">// One of our own!</span>
        jobject object <span style="color: #000080;">=</span> <span style="color: #0000ff;">static_cast</span><span style="color: #000080;">&lt;</span>JavaBBinder<span style="color: #000040;">*</span><span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>val.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>object<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        LOGDEATH<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"objectForBinder %p: it's our own %p!<span style="color: #000099; font-weight: bold;">\n</span>"</span>, val.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>,
                 object<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">return</span> object<span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
    <span style="color: #666666;">//如果是binder客户端进程，则需要返回Java层的BinderProxy对象</span>
&nbsp;
    <span style="color: #666666;">// For the rest of the function we will hold this lock, to serialize</span>
    <span style="color: #666666;">// looking/creation of Java proxies for native Binder proxies.</span>
    AutoMutex _l<span style="color: #008000;">&#40;</span>mProxyLock<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #666666;">// 如果已有用Java层WeakReference保存的BinderProxy对象，则返回该对象</span>
    jobject object <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>jobject<span style="color: #008000;">&#41;</span>val<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>findObject<span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>gBinderProxyOffsets<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>object <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        jobject res <span style="color: #000080;">=</span> env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>CallObjectMethod<span style="color: #008000;">&#40;</span>object, 
                          gWeakReferenceOffsets.<span style="color: #007788;">mGet</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>res <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
            ALOGV<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"objectForBinder %p: found existing %p!<span style="color: #000099; font-weight: bold;">\n</span>"</span>, val.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>,
                   res<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">return</span> res<span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        LOGDEATH<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Proxy object %p of IBinder %p no longer 
                  in working set!!!"</span>, object, val.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        android_atomic_dec<span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>gNumProxyRefs<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        val<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>detachObject<span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>gBinderProxyOffsets<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>DeleteGlobalRef<span style="color: #008000;">&#40;</span>object<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #666666;">//创建BinderProxy对象</span>
    object <span style="color: #000080;">=</span> env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>NewObject<span style="color: #008000;">&#40;</span>gBinderProxyOffsets.<span style="color: #007788;">mClass</span>, 
                 gBinderProxyOffsets.<span style="color: #007788;">mConstructor</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>object <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        LOGDEATH<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"objectForBinder %p: created new proxy %p !<span style="color: #000099; font-weight: bold;">\n</span>"</span>,
            val.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>, object<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #666666;">// The proxy holds a reference to the native object.</span>
        <span style="color: #666666;">//设置BinderProxy对象的mObject字段为本地IBinder对象指针，</span>
        <span style="color: #666666;">//本地IBinder对象的实际类型是BpBinder</span>
        env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>SetIntField<span style="color: #008000;">&#40;</span>object, gBinderProxyOffsets.<span style="color: #007788;">mObject</span>, 
               <span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int</span><span style="color: #008000;">&#41;</span>val.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        val<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>incStrong<span style="color: #008000;">&#40;</span>object<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
        <span style="color: #666666;">// The native object needs to hold a weak reference back to the</span>
        <span style="color: #666666;">// proxy, so we can retrieve </span>
        <span style="color: #666666;">//the same proxy if it is still active.</span>
        jobject refObject <span style="color: #000080;">=</span> env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>NewGlobalRef<span style="color: #008000;">&#40;</span>
                env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>GetObjectField<span style="color: #008000;">&#40;</span>object, gBinderProxyOffsets.<span style="color: #007788;">mSelf</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #666666;">//关联gBinderProxyOffsets，故此第20行代码用findObject才能找到      </span>
        val<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>attachObject<span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>gBinderProxyOffsets, refObject,
                jnienv_to_javavm<span style="color: #008000;">&#40;</span>env<span style="color: #008000;">&#41;</span>, proxy_cleanup<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
        <span style="color: #666666;">// Also remember the death recipients registered on this proxy</span>
        sp<span style="color: #000080;">&lt;</span>DeathRecipientList<span style="color: #000080;">&gt;</span> drl <span style="color: #000080;">=</span> <span style="color: #0000dd;">new</span> DeathRecipientList<span style="color: #008080;">;</span>
        drl<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>incStrong<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">void</span><span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>javaObjectForIBinder<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>SetIntField<span style="color: #008000;">&#40;</span>object, gBinderProxyOffsets.<span style="color: #007788;">mOrgue</span>, 
                    <span style="color: #0000ff;">reinterpret_cast</span><span style="color: #000080;">&lt;</span>jint<span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>drl.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
        <span style="color: #666666;">// Note that a new object reference has been created.</span>
        android_atomic_inc<span style="color: #008000;">&#40;</span><span style="color: #000040;">&</span>gNumProxyRefs<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        incRefsCreated<span style="color: #008000;">&#40;</span>env<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #0000ff;">return</span> object<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
              </td>
            </tr>
          </table>
        </div>
    
      * ### 2) ibinderForJavaObject 将Java层的IBinder对象转为本地IBinder对象
        
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
</pre>
              </td>
              
              <td class="code">
                <pre class="cpp" style="font-family:monospace;">sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span> ibinderForJavaObject<span style="color: #008000;">&#40;</span>JNIEnv<span style="color: #000040;">*</span> env, jobject obj<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>obj <span style="color: #000080;">==</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">return</span> <span style="color: #0000ff;">NULL</span><span style="color: #008080;">;</span>
&nbsp;
    <span style="color: #666666;">//如果是Java层Binder对象 </span>
    <span style="color: #666666;">//则将Binder对象的mObject字段转为JavaBBinderHolder指针</span>
    <span style="color: #666666;">//然后调用它的get方法即可转为本地IBinder对象，实际类型是JavaBBinder</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>IsInstanceOf<span style="color: #008000;">&#40;</span>obj, gBinderOffsets.<span style="color: #007788;">mClass</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        JavaBBinderHolder<span style="color: #000040;">*</span> jbh <span style="color: #000080;">=</span> <span style="color: #008000;">&#40;</span>JavaBBinderHolder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>
            env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>GetIntField<span style="color: #008000;">&#40;</span>obj, gBinderOffsets.<span style="color: #007788;">mObject</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
        <span style="color: #0000ff;">return</span> jbh <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000ff;">NULL</span> <span style="color: #008080;">?</span> jbh<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>get<span style="color: #008000;">&#40;</span>env, obj<span style="color: #008000;">&#41;</span> <span style="color: #008080;">:</span> <span style="color: #0000ff;">NULL</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    <span style="color: #666666;">//如果是Java层的BinderProxy对象，</span>
    <span style="color: #666666;">//则将BinderProxy对象的mObject字段直接转为本地的IBinder对象指针</span>
    <span style="color: #666666;">//实际类型是本地框架里的BpBinder</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>IsInstanceOf<span style="color: #008000;">&#40;</span>obj, gBinderProxyOffsets.<span style="color: #007788;">mClass</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000ff;">return</span> <span style="color: #008000;">&#40;</span>IBinder<span style="color: #000040;">*</span><span style="color: #008000;">&#41;</span>
            env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>GetIntField<span style="color: #008000;">&#40;</span>obj, gBinderProxyOffsets.<span style="color: #007788;">mObject</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
&nbsp;
    ALOGW<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"ibinderForJavaObject: %p is not a Binder object"</span>, obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">return</span> <span style="color: #0000ff;">NULL</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
              </td>
            </tr>
          </table>
        </div>
    
    ### 初始化流程
    
    Java虚拟机启动时会调用jni方法来注册Java层binder框架的本地方法，流程如下图所示(若看不清请点击看大图)：
    
    <a href="http://www.cloudchou.com/wp-content/uploads/2014/06/jni_funitioons1.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/jni_funitioons1-1024x516.jpg" alt="jni_funitioons" width="1024" height="516" class="aligncenter size-large wp-image-571" srcset="http://www.cloudchou.com/wp-content/uploads/2014/06/jni_funitioons1-1024x516.jpg 1024w, http://www.cloudchou.com/wp-content/uploads/2014/06/jni_funitioons1-300x151.jpg 300w, http://www.cloudchou.com/wp-content/uploads/2014/06/jni_funitioons1-200x100.jpg 200w, http://www.cloudchou.com/wp-content/uploads/2014/06/jni_funitioons1.jpg 1099w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>