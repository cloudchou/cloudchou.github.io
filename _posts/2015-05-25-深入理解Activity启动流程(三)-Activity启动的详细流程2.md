---
id: 815
title: '深入理解Activity启动流程(三)&#8211;Activity启动的详细流程2'
date: 2015-05-25T09:10:52+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=815
permalink: /android/post-815.html
views:
  - 4587
categories:
  - Android
  - 个人总结
tags:
  - activity启动流程
  - activity启动过程
  - android activity启动
  - android app 启动流程
  - android 启动activity
---
本系列博客将详细阐述Activity的启动流程，这些博客基于Cm 10.1源码研究。

  * <a href="http://www.cloudchou.com/android/post-788.html" target="_blank">深入理解Activity启动流程(一)&#8211;Activity启动的概要流程</a>
  * <a href="http://www.cloudchou.com/android/post-793.html" target="_blank">深入理解Activity启动流程(二)&#8211;Activity启动相关类的类图</a>
  * <a href="http://www.cloudchou.com/android/post-805.html" target="_blank">深入理解Activity启动流程(三)&#8211;Activity启动的详细流程1</a>
  * <a href="http://www.cloudchou.com/android/post-858.html" target="_blank">深入理解Activity启动流程(四)&#8211;Activity Task的调度算法</a>

上篇博客介绍了Activity详细启动流程的前半部分:

  * 1. Activity调用ActivityManagerService启动应用
  * 2. ActivityManagerService调用Zygote孵化应用进程
  * 3. Zygote孵化应用进程

本篇博客主要介绍Activity详细启动流程的后半部分:

  * 4. 新进程启动ActivityThread
  * 5. 应用进程绑定到ActivityManagerService
  * 6. ActivityThread的Handler处理启动Activity的消息

## 4. 新进程启动ActivityThread

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread-1024x359.png" alt="zygote_activitythread" width="1024" height="359" class="aligncenter size-large wp-image-812" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread-1024x359.png 1024w, http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread-300x105.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread-200x70.png 200w, http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread.png 1164w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

Zygote进程孵化出新的应用进程后，会执行ActivityThread类的main方法。在该方法里会先准备好Looper和消息队列，然后调用attach方法将应用进程绑定到ActivityManagerService，然后进入loop循环，不断地读取消息队列里的消息，并分发消息。

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> main<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> args<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
    Looper.<span style="color: #006633;">prepareMainLooper</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    ActivityThread thread <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ActivityThread<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    thread.<span style="color: #006633;">attach</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sMainThreadHandler <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        sMainThreadHandler <span style="color: #339933;">=</span> thread.<span style="color: #006633;">getHandler</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    AsyncTask.<span style="color: #006633;">init</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    Looper.<span style="color: #006633;">loop</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 5. 应用进程绑定到ActivityManagerService

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice.png"  target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice-1024x983.png" alt="application_amservice" width="1024" height="983" class="aligncenter size-large wp-image-810" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice-1024x983.png 1024w, http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice-300x288.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice-156x150.png 156w, http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice.png 1036w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

在ActivityThread的main方法里调用thread.attach(false);attach方法的主要代码如下所示:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> attach<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">boolean</span> system<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    sThreadLocal.<span style="color: #006633;">set</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">this</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    mSystemThread <span style="color: #339933;">=</span> system<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>system<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
        IActivityManager mgr <span style="color: #339933;">=</span> ActivityManagerNative.<span style="color: #006633;">getDefault</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//调用ActivityManagerService的attachApplication方法</span>
        <span style="color: #666666; font-style: italic;">//将ApplicationThread对象绑定至ActivityManagerService，</span>
        <span style="color: #666666; font-style: italic;">//这样ActivityManagerService就可以</span>
        <span style="color: #666666; font-style: italic;">//通过ApplicationThread代理对象控制应用进程</span>
            mgr.<span style="color: #006633;">attachApplication</span><span style="color: #009900;">&#40;</span>mAppThread<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RemoteException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">// Ignore</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

ActivityManagerService的attachApplication方法执行attachApplicationLocked(thread, callingPid)进行绑定。

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityManagerService类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">boolean</span> attachApplicationLocked<span style="color: #009900;">&#40;</span>IApplicationThread thread,
        <span style="color: #000066; font-weight: bold;">int</span> pid<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span> 
    ProcessRecord app<span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//...     </span>
    app.<span style="color: #006633;">thread</span> <span style="color: #339933;">=</span> thread<span style="color: #339933;">;</span> 
    <span style="color: #666666; font-style: italic;">//...  </span>
    <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
        thread.<span style="color: #006633;">bindApplication</span><span style="color: #009900;">&#40;</span>processName, appInfo, providers,
                app.<span style="color: #006633;">instrumentationClass</span>, profileFile, profileFd, profileAutoStop,
                app.<span style="color: #006633;">instrumentationArguments</span>, app.<span style="color: #006633;">instrumentationWatcher</span>, testMode,
                enableOpenGlTrace, isRestrictedBackupMode <span style="color: #339933;">||</span> <span style="color: #339933;">!</span>normalMode, app.<span style="color: #006633;">persistent</span>,
                <span style="color: #000000; font-weight: bold;">new</span> Configuration<span style="color: #009900;">&#40;</span>mConfiguration<span style="color: #009900;">&#41;</span>, app.<span style="color: #006633;">compat</span>, getCommonServicesLocked<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>,
                mCoreSettingsObserver.<span style="color: #006633;">getCoreSettingsLocked</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Exception</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
    ActivityRecord hr <span style="color: #339933;">=</span> mMainStack.<span style="color: #006633;">topRunningActivityLocked</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>hr <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> normalMode<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>hr.<span style="color: #006633;">app</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> app.<span style="color: #006633;">uid</span> <span style="color: #339933;">==</span> hr.<span style="color: #006633;">info</span>.<span style="color: #006633;">applicationInfo</span>.<span style="color: #006633;">uid</span>
                <span style="color: #339933;">&&</span> processName.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>hr.<span style="color: #006633;">processName</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mHeadless<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    Slog.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Starting activities not supported on headless device: "</span> <span style="color: #339933;">+</span> hr<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mMainStack.<span style="color: #006633;">realStartActivityLocked</span><span style="color: #009900;">&#40;</span>hr, app, <span style="color: #000066; font-weight: bold;">true</span>, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #666666; font-style: italic;">//mMainStack.realStartActivityLocked真正启动activity</span>
                    didSomething <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Exception</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #666666; font-style: italic;">//...</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//...</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

attachApplicationLocked方法有两个重要的函数调用thread.bindApplication和mMainStack.realStartActivityLocked。thread.bindApplication将应用进程的ApplicationThread对象绑定到ActivityManagerService，也就是说获得ApplicationThread对象的代理对象。mMainStack.realStartActivityLocked通知应用进程启动Activity。

### 5.1 thread.bindApplication

thread对象其实是ActivityThread里ApplicationThread对象在ActivityManagerService的代理对象，故此执行thread.bindApplication，最终会调用ApplicationThread的bindApplication方法，该方法的主要代码如下所示:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">void</span> bindApplication<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> processName,
        ApplicationInfo appInfo, List<span style="color: #339933;">&lt;</span>ProviderInfo<span style="color: #339933;">&gt;</span> providers,
        ComponentName instrumentationName, <span style="color: #003399;">String</span> profileFile,
        ParcelFileDescriptor profileFd, <span style="color: #000066; font-weight: bold;">boolean</span> autoStopProfiler,
        Bundle instrumentationArgs, IInstrumentationWatcher instrumentationWatcher,
        <span style="color: #000066; font-weight: bold;">int</span> debugMode, <span style="color: #000066; font-weight: bold;">boolean</span> enableOpenGlTrace, <span style="color: #000066; font-weight: bold;">boolean</span> isRestrictedBackupMode,
        <span style="color: #000066; font-weight: bold;">boolean</span> persistent, Configuration config, CompatibilityInfo compatInfo,
        Map<span style="color: #339933;">&lt;</span><span style="color: #003399;">String</span>, IBinder<span style="color: #339933;">&gt;</span> services, Bundle coreSettings<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//...  </span>
    AppBindData data <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> AppBindData<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    data.<span style="color: #006633;">processName</span> <span style="color: #339933;">=</span> processName<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">appInfo</span> <span style="color: #339933;">=</span> appInfo<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">providers</span> <span style="color: #339933;">=</span> providers<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">instrumentationName</span> <span style="color: #339933;">=</span> instrumentationName<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">instrumentationArgs</span> <span style="color: #339933;">=</span> instrumentationArgs<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">instrumentationWatcher</span> <span style="color: #339933;">=</span> instrumentationWatcher<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">debugMode</span> <span style="color: #339933;">=</span> debugMode<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">enableOpenGlTrace</span> <span style="color: #339933;">=</span> enableOpenGlTrace<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">restrictedBackupMode</span> <span style="color: #339933;">=</span> isRestrictedBackupMode<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">persistent</span> <span style="color: #339933;">=</span> persistent<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">config</span> <span style="color: #339933;">=</span> config<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">compatInfo</span> <span style="color: #339933;">=</span> compatInfo<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">initProfileFile</span> <span style="color: #339933;">=</span> profileFile<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">initProfileFd</span> <span style="color: #339933;">=</span> profileFd<span style="color: #339933;">;</span>
    data.<span style="color: #006633;">initAutoStopProfiler</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    queueOrSendMessage<span style="color: #009900;">&#40;</span>H.<span style="color: #006633;">BIND_APPLICATION</span>, data<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

这样调用queueOrSendMessage会往ActivityThread的消息队列发送消息，消息的用途是BIND_APPLICATION。

这样会在handler里处理BIND_APPLICATION消息，接着调用handleBindApplication方法处理绑定消息。

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> handleBindApplication<span style="color: #009900;">&#40;</span>AppBindData data<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...  </span>
  ApplicationInfo instrApp <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ApplicationInfo<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  instrApp.<span style="color: #006633;">packageName</span> <span style="color: #339933;">=</span> ii.<span style="color: #006633;">packageName</span><span style="color: #339933;">;</span>
  instrApp.<span style="color: #006633;">sourceDir</span> <span style="color: #339933;">=</span> ii.<span style="color: #006633;">sourceDir</span><span style="color: #339933;">;</span>
  instrApp.<span style="color: #006633;">publicSourceDir</span> <span style="color: #339933;">=</span> ii.<span style="color: #006633;">publicSourceDir</span><span style="color: #339933;">;</span>
  instrApp.<span style="color: #006633;">dataDir</span> <span style="color: #339933;">=</span> ii.<span style="color: #006633;">dataDir</span><span style="color: #339933;">;</span>
  instrApp.<span style="color: #006633;">nativeLibraryDir</span> <span style="color: #339933;">=</span> ii.<span style="color: #006633;">nativeLibraryDir</span><span style="color: #339933;">;</span>
  LoadedApk pi <span style="color: #339933;">=</span> getPackageInfo<span style="color: #009900;">&#40;</span>instrApp, data.<span style="color: #006633;">compatInfo</span>,
        appContext.<span style="color: #006633;">getClassLoader</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, <span style="color: #000066; font-weight: bold;">false</span>, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  ContextImpl instrContext <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ContextImpl<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  instrContext.<span style="color: #006633;">init</span><span style="color: #009900;">&#40;</span>pi, <span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #000000; font-weight: bold;">this</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
&nbsp;
&nbsp;
&nbsp;
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>data.<span style="color: #006633;">instrumentationName</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//注意Activity的所有生命周期方法都会被Instrumentation对象所监控，</span>
       <span style="color: #666666; font-style: italic;">//也就说执行Activity的生命周期方法前后一定会调用Instrumentation对象的相关方法</span>
       <span style="color: #666666; font-style: italic;">//并不是说只有跑单测用例才会建立Instrumentation对象，</span>
       <span style="color: #666666; font-style: italic;">//即使不跑单测也会建立Instrumentation对象</span>
       mInstrumentation <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Instrumentation<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #666666; font-style: italic;">//... </span>
  <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
     <span style="color: #666666; font-style: italic;">//...</span>
     Application app <span style="color: #339933;">=</span> data.<span style="color: #006633;">info</span>.<span style="color: #006633;">makeApplication</span><span style="color: #009900;">&#40;</span>data.<span style="color: #006633;">restrictedBackupMode</span>, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
     mInitialApplication <span style="color: #339933;">=</span> app<span style="color: #339933;">;</span>
     <span style="color: #666666; font-style: italic;">//...         </span>
     <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
          mInstrumentation.<span style="color: #006633;">onCreate</span><span style="color: #009900;">&#40;</span>data.<span style="color: #006633;">instrumentationArgs</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span><span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Exception</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
             <span style="color: #666666; font-style: italic;">//...</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
           <span style="color: #666666; font-style: italic;">//这里会调用Application的onCreate方法</span>
           <span style="color: #666666; font-style: italic;">//故此Applcation对象的onCreate方法会比ActivityThread的main方法后调用</span>
           <span style="color: #666666; font-style: italic;">//但是会比这个应用的所有activity先调用</span>
            mInstrumentation.<span style="color: #006633;">callApplicationOnCreate</span><span style="color: #009900;">&#40;</span>app<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Exception</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
           <span style="color: #666666; font-style: italic;">//...</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
        StrictMode.<span style="color: #006633;">setThreadPolicy</span><span style="color: #009900;">&#40;</span>savedPolicy<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

### 5.2 mMainStack.realStartActivityLocked

realStartActivity会调用scheduleLaunchActivity启动activity，主要代码:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityStack类</span>
<span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">boolean</span> realStartActivityLocked<span style="color: #009900;">&#40;</span>ActivityRecord r,
        ProcessRecord app, <span style="color: #000066; font-weight: bold;">boolean</span> andResume, <span style="color: #000066; font-weight: bold;">boolean</span> checkConfig<span style="color: #009900;">&#41;</span>
        <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">RemoteException</span> <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//...  </span>
    <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
        app.<span style="color: #006633;">thread</span>.<span style="color: #006633;">scheduleLaunchActivity</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> Intent<span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">intent</span><span style="color: #009900;">&#41;</span>, r.<span style="color: #006633;">appToken</span>,
                <span style="color: #003399;">System</span>.<span style="color: #006633;">identityHashCode</span><span style="color: #009900;">&#40;</span>r<span style="color: #009900;">&#41;</span>, r.<span style="color: #006633;">info</span>,
                <span style="color: #000000; font-weight: bold;">new</span> Configuration<span style="color: #009900;">&#40;</span>mService.<span style="color: #006633;">mConfiguration</span><span style="color: #009900;">&#41;</span>,
                r.<span style="color: #006633;">compat</span>, r.<span style="color: #006633;">icicle</span>, results, newIntents, <span style="color: #339933;">!</span>andResume,
                mService.<span style="color: #006633;">isNextTransitionForward</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, profileFile, profileFd,
                profileAutoStop<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
        <span style="color: #666666; font-style: italic;">//...</span>
&nbsp;
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RemoteException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//...    </span>
    <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

同样app.thread也只是ApplicationThread对象在ActivityManagerService的一个代理对象而已，最终会调用ApplicationThread的scheduleLaunchActivity方法。

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">void</span> scheduleLaunchActivity<span style="color: #009900;">&#40;</span>Intent intent, IBinder token, <span style="color: #000066; font-weight: bold;">int</span> ident,
        ActivityInfo info, Configuration curConfig, CompatibilityInfo compatInfo,
        Bundle state, List<span style="color: #339933;">&lt;</span>ResultInfo<span style="color: #339933;">&gt;</span> pendingResults,
        List<span style="color: #339933;">&lt;</span>Intent<span style="color: #339933;">&gt;</span> pendingNewIntents, <span style="color: #000066; font-weight: bold;">boolean</span> notResumed, <span style="color: #000066; font-weight: bold;">boolean</span> isForward,
        <span style="color: #003399;">String</span> profileName, ParcelFileDescriptor profileFd, <span style="color: #000066; font-weight: bold;">boolean</span> autoStopProfiler<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    ActivityClientRecord r <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ActivityClientRecord<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    r.<span style="color: #006633;">token</span> <span style="color: #339933;">=</span> token<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">ident</span> <span style="color: #339933;">=</span> ident<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">intent</span> <span style="color: #339933;">=</span> intent<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">activityInfo</span> <span style="color: #339933;">=</span> info<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">compatInfo</span> <span style="color: #339933;">=</span> compatInfo<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">state</span> <span style="color: #339933;">=</span> state<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">pendingResults</span> <span style="color: #339933;">=</span> pendingResults<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">pendingIntents</span> <span style="color: #339933;">=</span> pendingNewIntents<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">startsNotResumed</span> <span style="color: #339933;">=</span> notResumed<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">isForward</span> <span style="color: #339933;">=</span> isForward<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">profileFile</span> <span style="color: #339933;">=</span> profileName<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">profileFd</span> <span style="color: #339933;">=</span> profileFd<span style="color: #339933;">;</span>
    r.<span style="color: #006633;">autoStopProfiler</span> <span style="color: #339933;">=</span> autoStopProfiler<span style="color: #339933;">;</span>
    updatePendingConfiguration<span style="color: #009900;">&#40;</span>curConfig<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    queueOrSendMessage<span style="color: #009900;">&#40;</span>H.<span style="color: #006633;">LAUNCH_ACTIVITY</span>, r<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

这里调用了queueOrSendMessage往ActivityThread的消息队列发送了消息，消息的用途是启动Activity，接下来ActivityThread的handler便会处理该消息。

## 6. ActivityThread的Handler处理启动Activity的消息

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity-926x1024.png" alt="activitythread_activity" width="926" height="1024" class="aligncenter size-large wp-image-808" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity-926x1024.png 926w, http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity-271x300.png 271w, http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity-135x150.png 135w, http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity.png 1231w" sizes="(max-width: 926px) 100vw, 926px" /></a>

ActivityThread的handler调用handleLaunchActivity处理启动Activity的消息，handleLaunchActivity的主要代码如下所示:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> handleLaunchActivity<span style="color: #009900;">&#40;</span>ActivityClientRecord r, Intent customIntent<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
    Activity a <span style="color: #339933;">=</span> performLaunchActivity<span style="color: #009900;">&#40;</span>r, customIntent<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>a <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
        handleResumeActivity<span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">token</span>, <span style="color: #000066; font-weight: bold;">false</span>, r.<span style="color: #006633;">isForward</span>,
                <span style="color: #339933;">!</span>r.<span style="color: #006633;">activity</span>.<span style="color: #006633;">mFinished</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span>r.<span style="color: #006633;">startsNotResumed</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

handleLaunchActivity方法里有有两个重要的函数调用,performLaunchActivity和handleResumeActivity,performLaunchActivity会调用Activity的onCreate,onStart,onResotreInstanceState方法,handleResumeActivity会调用Activity的onResume方法.

### 6.1 performLaunchActivity

performLaunchActivity的主要代码如下所示:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">private</span> Activity performLaunchActivity<span style="color: #009900;">&#40;</span>ActivityClientRecord r, Intent customIntent<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    Activity activity <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
        java.<span style="color: #006633;">lang</span>.<span style="color: #003399;">ClassLoader</span> cl <span style="color: #339933;">=</span> r.<span style="color: #006633;">packageInfo</span>.<span style="color: #006633;">getClassLoader</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        activity <span style="color: #339933;">=</span> mInstrumentation.<span style="color: #006633;">newActivity</span><span style="color: #009900;">&#40;</span>
                cl, component.<span style="color: #006633;">getClassName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, r.<span style="color: #006633;">intent</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Exception</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//r.packageInfo.makeApplication实际并未创建Application对象，</span>
        <span style="color: #666666; font-style: italic;">//因为bindApplication过程已经创建了Application对象，</span>
        <span style="color: #666666; font-style: italic;">//makeApplication方法会返回已创建的Application对象</span>
        Application app <span style="color: #339933;">=</span> r.<span style="color: #006633;">packageInfo</span>.<span style="color: #006633;">makeApplication</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">false</span>, mInstrumentation<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//...         </span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>activity <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//...</span>
            <span style="color: #666666; font-style: italic;">//将application对象,appContext对象绑定到新建的activity对象</span>
            activity.<span style="color: #006633;">attach</span><span style="color: #009900;">&#40;</span>appContext, <span style="color: #000000; font-weight: bold;">this</span>, getInstrumentation<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, r.<span style="color: #006633;">token</span>,
                    r.<span style="color: #006633;">ident</span>, app, r.<span style="color: #006633;">intent</span>, r.<span style="color: #006633;">activityInfo</span>, title, r.<span style="color: #006633;">parent</span>,
                    r.<span style="color: #006633;">embeddedID</span>, r.<span style="color: #006633;">lastNonConfigurationInstances</span>, config<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #666666; font-style: italic;">//... </span>
            <span style="color: #666666; font-style: italic;">//会调用Activity的onCreate方法             </span>
            mInstrumentation.<span style="color: #006633;">callActivityOnCreate</span><span style="color: #009900;">&#40;</span>activity, r.<span style="color: #006633;">state</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #666666; font-style: italic;">//...</span>
            <span style="color: #666666; font-style: italic;">//...</span>
            <span style="color: #666666; font-style: italic;">//调用Activity的onStart方法</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>r.<span style="color: #006633;">activity</span>.<span style="color: #006633;">mFinished</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                activity.<span style="color: #006633;">performStart</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                r.<span style="color: #006633;">stopped</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>              
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>r.<span style="color: #006633;">activity</span>.<span style="color: #006633;">mFinished</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">state</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">//会调用Activity的onRestoreInstanceState方法</span>
                    mInstrumentation.<span style="color: #006633;">callActivityOnRestoreInstanceState</span><span style="color: #009900;">&#40;</span>activity, r.<span style="color: #006633;">state</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>r.<span style="color: #006633;">activity</span>.<span style="color: #006633;">mFinished</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                activity.<span style="color: #006633;">mCalled</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
                mInstrumentation.<span style="color: #006633;">callActivityOnPostCreate</span><span style="color: #009900;">&#40;</span>activity, r.<span style="color: #006633;">state</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #666666; font-style: italic;">//...</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span>SuperNotCalledException e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">throw</span> e<span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Exception</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #000000; font-weight: bold;">return</span> activity<span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

### 6.2 handleResumeActivity

handleResumeActivity的主要代码如下所示:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">void</span> handleResumeActivity<span style="color: #009900;">&#40;</span>IBinder token, <span style="color: #000066; font-weight: bold;">boolean</span> clearHide, <span style="color: #000066; font-weight: bold;">boolean</span> isForward,
        <span style="color: #000066; font-weight: bold;">boolean</span> reallyResume<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #666666; font-style: italic;">//performResumeActivity最终会调用Activity的onResume方法 </span>
    ActivityClientRecord r <span style="color: #339933;">=</span> performResumeActivity<span style="color: #009900;">&#40;</span>token, clearHide<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">final</span> Activity a <span style="color: #339933;">=</span> r.<span style="color: #006633;">activity</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//... </span>
        <span style="color: #666666; font-style: italic;">//显示界面</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">window</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span>a.<span style="color: #006633;">mFinished</span> <span style="color: #339933;">&&</span> willBeVisible<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            r.<span style="color: #006633;">window</span> <span style="color: #339933;">=</span> r.<span style="color: #006633;">activity</span>.<span style="color: #006633;">getWindow</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #003399;">View</span> decor <span style="color: #339933;">=</span> r.<span style="color: #006633;">window</span>.<span style="color: #006633;">getDecorView</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            decor.<span style="color: #006633;">setVisibility</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">View</span>.<span style="color: #006633;">INVISIBLE</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            ViewManager wm <span style="color: #339933;">=</span> a.<span style="color: #006633;">getWindowManager</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            WindowManager.<span style="color: #006633;">LayoutParams</span> l <span style="color: #339933;">=</span> r.<span style="color: #006633;">window</span>.<span style="color: #006633;">getAttributes</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            a.<span style="color: #006633;">mDecor</span> <span style="color: #339933;">=</span> decor<span style="color: #339933;">;</span>
            l.<span style="color: #006633;">type</span> <span style="color: #339933;">=</span> WindowManager.<span style="color: #006633;">LayoutParams</span>.<span style="color: #006633;">TYPE_BASE_APPLICATION</span><span style="color: #339933;">;</span>
            l.<span style="color: #006633;">softInputMode</span> <span style="color: #339933;">|=</span> forwardBit<span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>a.<span style="color: #006633;">mVisibleFromClient</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                a.<span style="color: #006633;">mWindowAdded</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
                wm.<span style="color: #006633;">addView</span><span style="color: #009900;">&#40;</span>decor, l<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
           <span style="color: #666666; font-style: italic;">//...         </span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>willBeVisible<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
             <span style="color: #666666; font-style: italic;">//...</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #666666; font-style: italic;">// Tell the activity manager we have resumed.</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>reallyResume<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                ActivityManagerNative.<span style="color: #006633;">getDefault</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">activityResumed</span><span style="color: #009900;">&#40;</span>token<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RemoteException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

performResumeActivity的主要代码如下所示:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityThread类</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">final</span> ActivityClientRecord performResumeActivity<span style="color: #009900;">&#40;</span>IBinder token,
        <span style="color: #000066; font-weight: bold;">boolean</span> clearHide<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    ActivityClientRecord r <span style="color: #339933;">=</span> mActivities.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>token<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span>r.<span style="color: #006633;">activity</span>.<span style="color: #006633;">mFinished</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//...</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//... </span>
            <span style="color: #666666; font-style: italic;">//会调用Activity的onResume方法 </span>
            r.<span style="color: #006633;">activity</span>.<span style="color: #006633;">performResume</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #666666; font-style: italic;">//...</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Exception</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//...</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #000000; font-weight: bold;">return</span> r<span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 总结

Activity的概要启动流程:

用户在Launcher程序里点击应用图标时，会通知ActivityManagerService启动应用的入口Activity，ActivityManagerService发现这个应用还未启动，则会通知Zygote进程孵化出应用进程，然后在这个dalvik应用进程里执行ActivityThread的main方法。应用进程接下来通知ActivityManagerService应用进程已启动，ActivityManagerService保存应用进程的一个代理对象，这样ActivityManagerService可以通过这个代理对象控制应用进程，然后ActivityManagerService通知应用进程创建入口Activity的实例，并执行它的生命周期方法 

现在也可以理解: 

如果应用的组件(包括所有组件Activity，Service，ContentProvider，Receiver) 被启动，肯定会先启动以应用包名为进程名的进程，这些组件都会运行在应用包名为进程名的进程里，并且是在主线程里。应用进程启动时会先创建Application对象，并执行Application对象的生命周期方法，然后才启动应用的组件。

有一种情况比较特殊，那就是为组件设置了特殊的进程名，也就是说通过android:process设置进程名的情况，此时组件运行在单独的进程内。

下篇博客将介绍Activity,Task的调度算法。