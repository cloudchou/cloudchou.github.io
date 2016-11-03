---
id: 805
title: '深入理解Activity启动流程(三)&#8211;Activity启动的详细流程1'
date: 2015-05-25T09:10:05+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=805
permalink: /android/post-805.html
views:
  - 3959
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
  * <a href="http://www.cloudchou.com/android/post-815.html" target="_blank">深入理解Activity启动流程(三)&#8211;Activity启动的详细流程2</a>
  * <a href="http://www.cloudchou.com/android/post-858.html" target="_blank">深入理解Activity启动流程(四)&#8211;Activity Task的调度算法</a>

本篇博客将开始介绍Activity启动的详细流程，由于详细启动流程非常复杂，故此分成两篇来介绍。

本篇主要介绍前半部分的启动流程:

  * 1. Activity调用ActivityManagerService启动应用
  * 2. ActivityManagerService调用Zygote孵化应用进程
  * 3. Zygote孵化应用进程

下篇介绍后半部分的启动流程:

  * 4. 新进程启动ActivityThread
  * 5. 应用进程绑定到ActivityManagerService
  * 6. ActivityThread的Handler处理启动Activity的消息

## 1. Activity调用ActivityManagerService启动应用

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice.png" alt="activity_amservice" width="917" height="485" class="aligncenter size-full wp-image-807" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice.png 917w, http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice-300x158.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice-200x105.png 200w" sizes="(max-width: 917px) 100vw, 917px" /></a>

在launcher应用程序里启动应用时，点击应用图标后，launcher程序会调用startActivity启动应用，传递的intent参数:

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
        <pre class="java" style="font-family:monospace;">intent <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Intent<span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">ACTION_MAIN</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   intent.<span style="color: #006633;">addCategory</span><span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">CATEGORY_LAUNCHER</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   intent.<span style="color: #006633;">setComponent</span><span style="color: #009900;">&#40;</span>className<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

activity最终调用Instrumentation的execStartActivity来启动应用:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//Activity类</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> startActivityForResult<span style="color: #009900;">&#40;</span>Intent intent, <span style="color: #000066; font-weight: bold;">int</span> requestCode, Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
 <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mParent <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
	Instrumentation.<span style="color: #006633;">ActivityResult</span> ar <span style="color: #339933;">=</span>
	                mInstrumentation.<span style="color: #006633;">execStartActivity</span><span style="color: #009900;">&#40;</span>
	                    <span style="color: #000000; font-weight: bold;">this</span>, mMainThread.<span style="color: #006633;">getApplicationThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, mToken, <span style="color: #000000; font-weight: bold;">this</span>,
	                    intent, requestCode, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	   <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>ar <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
	                mMainThread.<span style="color: #006633;">sendActivityResult</span><span style="color: #009900;">&#40;</span>
	                    mToken, mEmbeddedID, requestCode, ar.<span style="color: #006633;">getResultCode</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>,
	                    ar.<span style="color: #006633;">getResultData</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	   <span style="color: #009900;">&#125;</span> 
	<span style="color: #666666; font-style: italic;">//...   </span>
 <span style="color: #009900;">&#125;</span><span style="color: #000000; font-weight: bold;">else</span><span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
 <span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

Instrumentation调用ActivityManagerProxy对象的startActivity方法启动Activity，而ActivityManagerProxy只是ActivityManagerService对象在应用进程的一个代理对象，ActivityManagerProxy最终调用ActivityManagerService的startActvity方法启动Activity。

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//Instrumentation类</span>
<span style="color: #000000; font-weight: bold;">public</span> ActivityResult execStartActivity<span style="color: #009900;">&#40;</span>
          <span style="color: #003399;">Context</span> who, IBinder contextThread, IBinder token, Activity target,
          Intent intent, <span style="color: #000066; font-weight: bold;">int</span> requestCode, Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
<span style="color: #666666; font-style: italic;">//...</span>
 <span style="color: #000000; font-weight: bold;">try</span><span style="color: #009900;">&#123;</span>          
   <span style="color: #666666; font-style: italic;">//...</span>
   <span style="color: #000066; font-weight: bold;">int</span> result <span style="color: #339933;">=</span> ActivityManagerNative.<span style="color: #006633;">getDefault</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>
                .<span style="color: #006633;">startActivity</span><span style="color: #009900;">&#40;</span>whoThread, intent,
                        intent.<span style="color: #006633;">resolveTypeIfNeeded</span><span style="color: #009900;">&#40;</span>who.<span style="color: #006633;">getContentResolver</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span>,
                        token, target <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> target.<span style="color: #006633;">mEmbeddedID</span> <span style="color: #339933;">:</span> <span style="color: #000066; font-weight: bold;">null</span>,
                        requestCode, <span style="color: #cc66cc;"></span>, <span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #000066; font-weight: bold;">null</span>, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RemoteException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
   <span style="color: #009900;">&#125;</span>   
<span style="color: #666666; font-style: italic;">//...   </span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 2. ActivityManagerService调用Zygote孵化应用进程

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote.png" alt="amservice_zygote" width="1132" height="1048" class="aligncenter size-full wp-image-809" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote.png 1132w, http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote-300x277.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote-1024x948.png 1024w, http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote-162x150.png 162w" sizes="(max-width: 1132px) 100vw, 1132px" /></a>

ActivityManagerProxy对象调用ActivityManagerService对象(运行在system_server进程)的startActivity方法以启动应用，startActivity方法接下来调用startActivityAsUser方法以启动应用。在startActivityAsUser方法里会调用ActivityStack的startActivityMayWait方法以启动应用，startActivityMayWait方法里启动应用时，需先根据intent在系统中找到合适的应用的activity，如果有多个activity可选择，则会弹出ResolverActivity让用户选择合适的应用。

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityStack类</span>
<span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> startActivityMayWait<span style="color: #009900;">&#40;</span>IApplicationThread caller, <span style="color: #000066; font-weight: bold;">int</span> callingUid,
            Intent intent, <span style="color: #003399;">String</span> resolvedType, IBinder resultTo,
            <span style="color: #003399;">String</span> resultWho, <span style="color: #000066; font-weight: bold;">int</span> requestCode, <span style="color: #000066; font-weight: bold;">int</span> startFlags, <span style="color: #003399;">String</span> profileFile,
            ParcelFileDescriptor profileFd, WaitResult outResult, Configuration config,
            Bundle options, <span style="color: #000066; font-weight: bold;">int</span> userId<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
<span style="color: #666666; font-style: italic;">//…</span>
<span style="color: #666666; font-style: italic;">//根据intent在系统中找到合适的应用的activity，如果有多个activity可选择，</span>
<span style="color: #666666; font-style: italic;">//则会弹出ResolverActivity让用户选择合适的应用。</span>
  ActivityInfo aInfo <span style="color: #339933;">=</span> resolveActivity<span style="color: #009900;">&#40;</span>intent, resolvedType, startFlags,
                profileFile, profileFd, userId<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #666666; font-style: italic;">//…</span>
<span style="color: #000066; font-weight: bold;">int</span> res <span style="color: #339933;">=</span> startActivityLocked<span style="color: #009900;">&#40;</span>caller, intent, resolvedType,
                    aInfo, resultTo, resultWho, requestCode, callingPid, callingUid,
                    startFlags, options, componentSpecified, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #666666; font-style: italic;">//…</span>
｝</pre>
      </td>
    </tr>
  </table>
</div>

在startActivityLocked方法里，对传过来的参数做一些校验，然后创建ActivityRecord对象，再调用startActivityUncheckedLocked方法启动Activity。

startActivityUncheckedLocked方法负责调度ActivityRecord和Task，理解该方法是理解Actvity启动模式的关键。

startActivityUncheckedLocked方法调度task的算法非常复杂，和当前回退栈，要启动的acitivity的启动模式以及taskAffinity属性，启动activity时设置的intent的flag等诸多要素相关，intent的flag就有很多种情况，故此算法非常复杂，需要阅读源码并结合特定启动情况才能理解。

后续会介绍startActivityUncheckedLocked方法的实现，并结合特定场景分析调度算法。

接下来调用startActivityLocked将ActivityRecord加入到回退栈里:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityStack类</span>
<span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> startActivityUncheckedLocked<span style="color: #009900;">&#40;</span>ActivityRecord r,
          ActivityRecord sourceRecord, <span style="color: #000066; font-weight: bold;">int</span> startFlags, <span style="color: #000066; font-weight: bold;">boolean</span> doResume,
          Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
<span style="color: #666666; font-style: italic;">//...          </span>
startActivityLocked<span style="color: #009900;">&#40;</span>r, newTask, doResume, keepCurTransition, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

在startActivityLocked里调用resumeTopActivityLocked显示栈顶Activity:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityStack类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">void</span> startActivityLocked<span style="color: #009900;">&#40;</span>ActivityRecord r, <span style="color: #000066; font-weight: bold;">boolean</span> newTask,
        <span style="color: #000066; font-weight: bold;">boolean</span> doResume, <span style="color: #000066; font-weight: bold;">boolean</span> keepCurTransition, Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
 <span style="color: #666666; font-style: italic;">//...        </span>
 <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>doResume<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
   resumeTopActivityLocked<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
 <span style="color: #009900;">&#125;</span>  
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

resumeTopActivityLocked(null)会调用另一个resumeTopActivityLocked方法显示栈顶的acitivity:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityStack类</span>
<span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">boolean</span> resumeTopActivityLocked<span style="color: #009900;">&#40;</span>ActivityRecord prev<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">return</span> resumeTopActivityLocked<span style="color: #009900;">&#40;</span>prev, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

因为应用还未启动过，所以调用startSpecificActivityLocked启动应用，执行逻辑如下:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityStack类</span>
<span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">boolean</span> resumeTopActivityLocked<span style="color: #009900;">&#40;</span>ActivityRecord prev, Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>next.<span style="color: #006633;">app</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> next.<span style="color: #006633;">app</span>.<span style="color: #006633;">thread</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//…</span>
  <span style="color: #009900;">&#125;</span><span style="color: #000000; font-weight: bold;">else</span><span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//…</span>
   startSpecificActivityLocked<span style="color: #009900;">&#40;</span>next, <span style="color: #000066; font-weight: bold;">true</span>, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
 <span style="color: #666666; font-style: italic;">//... </span>
｝</pre>
      </td>
    </tr>
  </table>
</div>

在startSpecificActivityLocked里调用mService.startProcessLocked启动应用:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityStack类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">void</span> startSpecificActivityLocked<span style="color: #009900;">&#40;</span>ActivityRecord r,
            <span style="color: #000066; font-weight: bold;">boolean</span> andResume, <span style="color: #000066; font-weight: bold;">boolean</span> checkConfig<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
   ProcessRecord app <span style="color: #339933;">=</span> mService.<span style="color: #006633;">getProcessRecordLocked</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">processName</span>,
              r.<span style="color: #006633;">info</span>.<span style="color: #006633;">applicationInfo</span>.<span style="color: #006633;">uid</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #666666; font-style: italic;">//...</span>
   mService.<span style="color: #006633;">startProcessLocked</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">processName</span>, r.<span style="color: #006633;">info</span>.<span style="color: #006633;">applicationInfo</span>, <span style="color: #000066; font-weight: bold;">true</span>, <span style="color: #cc66cc;"></span>,
        <span style="color: #0000ff;">"activity"</span>, r.<span style="color: #006633;">intent</span>.<span style="color: #006633;">getComponent</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, <span style="color: #000066; font-weight: bold;">false</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

在ActivityManagerService的startProcessLocked方法里:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityManagerService类</span>
<span style="color: #000000; font-weight: bold;">final</span> ProcessRecord startProcessLocked<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> processName,
          ApplicationInfo info, <span style="color: #000066; font-weight: bold;">boolean</span> knownToBeDead, <span style="color: #000066; font-weight: bold;">int</span> intentFlags,
          <span style="color: #003399;">String</span> hostingType, ComponentName hostingName, <span style="color: #000066; font-weight: bold;">boolean</span> allowWhileBooting,
          <span style="color: #000066; font-weight: bold;">boolean</span> isolated<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
 ProcessRecord app<span style="color: #339933;">;</span>
 <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>isolated<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
     app <span style="color: #339933;">=</span> getProcessRecordLocked<span style="color: #009900;">&#40;</span>processName, info.<span style="color: #006633;">uid</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
 <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
     <span style="color: #666666; font-style: italic;">//...</span>
 <span style="color: #009900;">&#125;</span>
 <span style="color: #666666; font-style: italic;">//...</span>
 <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>app <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    app <span style="color: #339933;">=</span> newProcessRecordLocked<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span>, info, processName, isolated<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>app <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        Slog.<span style="color: #006633;">w</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Failed making new process record for "</span>
                <span style="color: #339933;">+</span> processName <span style="color: #339933;">+</span> <span style="color: #0000ff;">"/"</span> <span style="color: #339933;">+</span> info.<span style="color: #006633;">uid</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">" isolated="</span> <span style="color: #339933;">+</span> isolated<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    mProcessNames.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span>processName, app.<span style="color: #006633;">uid</span>, app<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>isolated<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        mIsolatedProcesses.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span>app.<span style="color: #006633;">uid</span>, app<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
   <span style="color: #666666; font-style: italic;">//..</span>
 <span style="color: #009900;">&#125;</span>
 <span style="color: #666666; font-style: italic;">//...</span>
 startProcessLocked<span style="color: #009900;">&#40;</span>app, hostingType, hostingNameStr<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
 <span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

在startProcessLocked方法里:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ActivityManagerService类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">void</span> startProcessLocked<span style="color: #009900;">&#40;</span>ProcessRecord app,
        <span style="color: #003399;">String</span> hostingType, <span style="color: #003399;">String</span> hostingNameStr<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//...</span>
      <span style="color: #666666; font-style: italic;">// Start the process.  It will either succeed and return a result containing</span>
  <span style="color: #666666; font-style: italic;">// the PID of the new process, or else throw a RuntimeException.</span>
  <span style="color: #666666; font-style: italic;">//Zygote孵化dalvik应用进程后，会执行android.app.ActivityThread类的main方法</span>
      <span style="color: #003399;">Process</span>.<span style="color: #006633;">ProcessStartResult</span> startResult <span style="color: #339933;">=</span> <span style="color: #003399;">Process</span>.<span style="color: #006633;">start</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"android.app.ActivityThread"</span>,
              app.<span style="color: #006633;">processName</span>, uid, uid, gids, debugFlags, mountExternal,
              app.<span style="color: #006633;">info</span>.<span style="color: #006633;">targetSdkVersion</span>, app.<span style="color: #006633;">info</span>.<span style="color: #006633;">seinfo</span>, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #666666; font-style: italic;">//...    </span>
  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RuntimeException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

在Process类的start方法里:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//Process类</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> ProcessStartResult start<span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> processClass,
                              <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> niceName,
                              <span style="color: #000066; font-weight: bold;">int</span> uid, <span style="color: #000066; font-weight: bold;">int</span> gid, <span style="color: #000066; font-weight: bold;">int</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> gids,
                              <span style="color: #000066; font-weight: bold;">int</span> debugFlags, <span style="color: #000066; font-weight: bold;">int</span> mountExternal,
                              <span style="color: #000066; font-weight: bold;">int</span> targetSdkVersion,
                              <span style="color: #003399;">String</span> seInfo,
                              <span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> zygoteArgs<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
 <span style="color: #000000; font-weight: bold;">try</span><span style="color: #009900;">&#123;</span>                              
  startViaZygote<span style="color: #009900;">&#40;</span>processClass, niceName, uid, gid, gids,
                    debugFlags, mountExternal, targetSdkVersion, seInfo, zygoteArgs<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span><span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span>ZygoteStartFailedEx ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #009900;">&#125;</span>                    
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

在Process类的startViaZygote方法里，会计算启动应用进程用的各个参数，然后再调用zygoteSendArgsAndGetResult方法将这些参数通过socket发送给zygote进程，zygote进程会孵化出新的dalvik应用进程，然后告诉ActivityManagerService新启动的进程的pid。

## 3. Zygote孵化应用进程

点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote.png" target="_blank">大图</a>

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote.png" alt="zygote" width="814" height="674" class="aligncenter size-full wp-image-811" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote.png 814w, http://www.cloudchou.com/wp-content/uploads/2015/05/zygote-300x248.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/05/zygote-181x150.png 181w" sizes="(max-width: 814px) 100vw, 814px" /></a>

zygote进程将ZygoteInit作为启动类，会执行它的main方法，先注册ZygoteSocket，然后调用runSelectLoop方法，runSelectLoop方法会调用方法在ZygoteSocket上监听请求，如果别的进程通过ZygoteSocket请求孵化进程，则孵化进程。

runSelectLoop方法的主要代码:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ZygoteInit类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> runSelectLoopMode<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> MethodAndArgsCaller <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
     <span style="color: #666666; font-style: italic;">//...</span>
      <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
          fdArray <span style="color: #339933;">=</span> fds.<span style="color: #006633;">toArray</span><span style="color: #009900;">&#40;</span>fdArray<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          index <span style="color: #339933;">=</span> selectReadable<span style="color: #009900;">&#40;</span>fdArray<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">IOException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Error in select()"</span>, ex<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>index <span style="color: #339933;">&lt;</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Error in select()"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>index <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #666666; font-style: italic;">//监听客户连接请求</span>
          ZygoteConnection newPeer <span style="color: #339933;">=</span> acceptCommandPeer<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          peers.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span>newPeer<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          fds.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span>newPeer.<span style="color: #006633;">getFileDesciptor</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//若客户发送孵化进程的请求过来，</span>
         <span style="color: #666666; font-style: italic;">//此时便需要调用ZygoteConnection的runOnce方法孵化进程</span>
          <span style="color: #000066; font-weight: bold;">boolean</span> done<span style="color: #339933;">;</span>
          done <span style="color: #339933;">=</span> peers.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>index<span style="color: #009900;">&#41;</span>.<span style="color: #006633;">runOnce</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>done<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              peers.<span style="color: #006633;">remove</span><span style="color: #009900;">&#40;</span>index<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
              fds.<span style="color: #006633;">remove</span><span style="color: #009900;">&#40;</span>index<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
      <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

在runOnce方法里调用Zygote.forkAndSpecialize方法孵化进程，如果返回值为0表示是在孵化出来的应用进程里，此时会调用handleChildProc进行一些处理，并使用异常机制进行逃逸，会直接逃逸至ZygoteInit的main方法。

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ZygoteConnection类</span>
<span style="color: #000066; font-weight: bold;">boolean</span> runOnce<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> ZygoteInit.<span style="color: #006633;">MethodAndArgsCaller</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
      pid <span style="color: #339933;">=</span> Zygote.<span style="color: #006633;">forkAndSpecialize</span><span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">uid</span>, parsedArgs.<span style="color: #006633;">gid</span>, parsedArgs.<span style="color: #006633;">gids</span>,
              parsedArgs.<span style="color: #006633;">debugFlags</span>, rlimits, parsedArgs.<span style="color: #006633;">mountExternal</span>, parsedArgs.<span style="color: #006633;">seInfo</span>,
              parsedArgs.<span style="color: #006633;">niceName</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span> 
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>pid <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #666666; font-style: italic;">// in child</span>
          IoUtils.<span style="color: #006633;">closeQuietly</span><span style="color: #009900;">&#40;</span>serverPipeFd<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          serverPipeFd <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
          <span style="color: #666666; font-style: italic;">//handleChildProc是一个很重要的函数，在该函数里使用了异常进行逃逸</span>
          handleChildProc<span style="color: #009900;">&#40;</span>parsedArgs, descriptors, childPipeFd, newStderr<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #666666; font-style: italic;">//...  </span>
      <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//... </span>
      <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

### 3.1 Zygote.forkAndSpecialize

Zygote的forkAndSpecialize方法会调用nativeForkAndSpecialize方法孵化进程，nativeForkAndSpecialize是一个本地方法，它的实现在dalvik/vm/native/dalvik\_system\_Zygote.cpp里，在该cpp文件里与nativeForkAndSpecialize对应的C++方法是Dalvik\_dalvik\_system\_Zygote\_forkAndSpecialize，在该方法里会调用forkAndSpecializeCommon孵化进程,在forkAndSpecializeCommon方法里会调用fork系统调用创建进程，因为使用的是fork机制所以创建进程的效率比较高。

### 3.2 handleChildProc

handleChildProc方法主要代码:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ZygoteConnection类</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> handleChildProc<span style="color: #009900;">&#40;</span>Arguments parsedArgs,
            <span style="color: #003399;">FileDescriptor</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> descriptors, <span style="color: #003399;">FileDescriptor</span> pipeFd, <span style="color: #003399;">PrintStream</span> newStderr<span style="color: #009900;">&#41;</span>
            <span style="color: #000000; font-weight: bold;">throws</span> ZygoteInit.<span style="color: #006633;">MethodAndArgsCaller</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">runtimeInit</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #003399;">String</span> className<span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #666666; font-style: italic;">//这里得到的classname实际是android.app.ActivityThread</span>
          className <span style="color: #339933;">=</span> parsedArgs.<span style="color: #006633;">remainingArgs</span><span style="color: #009900;">&#91;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">ArrayIndexOutOfBoundsException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
          logAndPrintError<span style="color: #009900;">&#40;</span>newStderr,
                  <span style="color: #0000ff;">"Missing required class name argument"</span>, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">return</span><span style="color: #339933;">;</span>
      <span style="color: #009900;">&#125;</span>
      <span style="color: #666666; font-style: italic;">//...</span>
      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">invokeWith</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//...</span>
      <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
          <span style="color: #003399;">ClassLoader</span> cloader<span style="color: #339933;">;</span>
          <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">classpath</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              cloader <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> PathClassLoader<span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">classpath</span>,
                      <span style="color: #003399;">ClassLoader</span>.<span style="color: #006633;">getSystemClassLoader</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
              cloader <span style="color: #339933;">=</span> <span style="color: #003399;">ClassLoader</span>.<span style="color: #006633;">getSystemClassLoader</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
          <span style="color: #666666; font-style: italic;">//调用ZygoteInit.invokeStaticMain执行android.app.ActivityThread的main方法        </span>
          <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
              ZygoteInit.<span style="color: #006633;">invokeStaticMain</span><span style="color: #009900;">&#40;</span>cloader, className, mainArgs<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RuntimeException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              logAndPrintError<span style="color: #009900;">&#40;</span>newStderr, <span style="color: #0000ff;">"Error starting."</span>, ex<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
          <span style="color: #009900;">&#125;</span>
      <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

ZygoteInit的invokeStaticMain方法并不会直接执行className的main方法，而是会构造一个 ZygoteInit.MethodAndArgsCaller异常，然后抛出来，通过异常机制会直接跳转到ZygoteInit的main方法, ZygoteInit.MethodAndArgsCaller类实现了Runnable方法，在run方法里会执行要求执行的main方法，故此跳转到ZygoteInit的main方法后，异常会被捕获，然后执行方法caller.run(),这样便会执行android.app.ActivityThread的main方法。

ZygoteInit的invokeStaticMain方法主要代码:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ZygoteInit类</span>
<span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> invokeStaticMain<span style="color: #009900;">&#40;</span><span style="color: #003399;">ClassLoader</span> loader,
        <span style="color: #003399;">String</span> className, <span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> argv<span style="color: #009900;">&#41;</span>
        <span style="color: #000000; font-weight: bold;">throws</span> ZygoteInit.<span style="color: #006633;">MethodAndArgsCaller</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...        </span>
  <span style="color: #003399;">Method</span> m<span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
      m <span style="color: #339933;">=</span> cl.<span style="color: #006633;">getMethod</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"main"</span>, <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #000000; font-weight: bold;">Class</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> <span style="color: #009900;">&#123;</span> <span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span>.<span style="color: #000000; font-weight: bold;">class</span> <span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span><span style="color: #009900;">&#40;</span><span style="color: #666666; font-style: italic;">//...){</span>
  <span style="color: #009900;">&#125;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> ZygoteInit.<span style="color: #006633;">MethodAndArgsCaller</span><span style="color: #009900;">&#40;</span>m, argv<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

ZygoteInit.MethodAndArgsCaller主要代码:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">class</span> MethodAndArgsCaller <span style="color: #000000; font-weight: bold;">extends</span> <span style="color: #003399;">Exception</span>
        <span style="color: #000000; font-weight: bold;">implements</span> <span style="color: #003399;">Runnable</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            mMethod.<span style="color: #006633;">invoke</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Object</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> <span style="color: #009900;">&#123;</span> mArgs <span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span><span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

ZygoteInit的main方法相关代码:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//ZygoteInit类</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> main<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> argv<span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span>MethodAndArgsCaller caller<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      caller.<span style="color: #006633;">run</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RuntimeException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//...</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

下面博客将介绍Activity详细启动流程的后半部分。