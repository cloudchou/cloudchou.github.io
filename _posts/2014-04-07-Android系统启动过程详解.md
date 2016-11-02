---
id: 361
title: Android系统启动过程详解
date: 2014-04-07T01:29:04+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=361
permalink: /android/post-361.html
views:
  - 9807
categories:
  - Android
tags:
  - android 启动 home
  - android 系统启动
  - android启动过程
  - android启动过程 源代码分析
  - android启动过程分析
  - android启动过程详解
  - Android系统启动过程
---
## 前言

一直想研究Android完整的启动过程，网上看了不少资料，也看了书上的一些说明，对这些观点有些怀疑，于是自己分析了系统启动的完整过程。从内核启动第一个用户程序init开始说起，直到Home应用的启动，每一步都有源代码展示。希望能解除读者对<a href="http://www.cloudchou.com/tag/android%e7%b3%bb%e7%bb%9f%e5%90%af%e5%8a%a8%e8%bf%87%e7%a8%8b" title="View all posts in Android系统启动过程" target="_blank" class="tags">Android系统启动过程</a>中的困惑，若有什么疑问，欢迎留言交流。本研究基于CM10.1源码，读者若能对照源代码查看效果会更好。

## 1) init启动servicemanager和 zygote两个service

Android底层是Linux内核，和linux类似，内核初始化后启动的第一个用户进程是init，它会解析init.rc脚本，启动init.rc里声明的service，并执行一些action。在init.rc里有启动Andriod空间的一些关键服务，代码如下：

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
        <pre class="txt" style="font-family:monospace;">#…
service servicemanager /system/bin/servicemanager
    class core
    user system
    group system
    critical
    onrestart restart zygote
    onrestart restart media
    onrestart restart surfaceflinger
    onrestart restart drm
service zygote /system/bin/app_process -Xzygote /system/bin --zygote --start-system-server
    class main
    socket zygote stream 660 root system
    onrestart write /sys/android_power/request_state wake
    onrestart write /sys/power/state on
    onrestart restart media
    onrestart restart netd
#…</pre>
      </td>
    </tr>
  </table>
</div>

<span style="font-weight:bold">servicemanager</span>负责管理所有的binder service, 这些binder service有native的，也有java的。native的binder service有surfaceflinger，drm，media等，java的binder service就有我们平常熟悉的很多管理服务了，ActivityManagerService，WindowManagerService，BatteryService，PowerManagerService，InputManagerService等等。service manager并不负责这些binder service的创建，native的binder service大多由init启动init.rc里的service时创建并启动，java层的binder service大多由zygote创建并启动的，接下来会详细这些service是如何被启动的。

## 2) zygote service启动java层的ZygoteInit

zygote服务是java层所有程序进程的父进程，它是Android空间程序的孵化器，Android空间所有程序都是由zygote进程启动的。zygote service对应/system/bin/app\_process程序，源代码位于frameworks/base/cmds/app\_process/app_main.cpp，启动时的main函数代码如下：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">int</span> main<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">int</span> argc, <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">char</span><span style="color: #000040;">*</span> <span style="color: #0000ff;">const</span> argv<span style="color: #008000;">&#91;</span><span style="color: #008000;">&#93;</span><span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
<span style="color: #666666;">//...</span>
<span style="color: #ff0000; font-style: italic;">/*runtime就是dalvik虚拟机实例，启动Java层应用时，
 *会fork 一个子进程，复制虚拟机，许多书上将runtime看作一个进程，
 *然后再启动zygote进程，个人觉得这是错误的 
 */</span>		 
AppRuntime runtime<span style="color: #008080;">;</span>
<span style="color: #666666;">//... </span>
<span style="color: #0000ff;">while</span> <span style="color: #008000;">&#40;</span>i <span style="color: #000080;">&lt;</span> argc<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">const</span> <span style="color: #0000ff;">char</span><span style="color: #000040;">*</span> arg <span style="color: #000080;">=</span> argv<span style="color: #008000;">&#91;</span>i<span style="color: #000040;">++</span><span style="color: #008000;">&#93;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #000040;">!</span>parentDir<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        parentDir <span style="color: #000080;">=</span> arg<span style="color: #008080;">;</span>
  <span style="color: #ff0000; font-style: italic;">/*init.rc启动app_main会设置参数--zygote*/</span> 
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #0000dd;">strcmp</span><span style="color: #008000;">&#40;</span>arg, <span style="color: #FF0000;">"--zygote"</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        zygote <span style="color: #000080;">=</span> <span style="color: #0000ff;">true</span><span style="color: #008080;">;</span>
        niceName <span style="color: #000080;">=</span> <span style="color: #FF0000;">"zygote"</span><span style="color: #008080;">;</span> <span style="color: #666666;">//进程的名字</span>
  <span style="color: #ff0000; font-style: italic;">/*init.rc启动app_main会设置参数--start-system-server，
   *表示需启动systemserver
   */</span>
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #0000dd;">strcmp</span><span style="color: #008000;">&#40;</span>arg, <span style="color: #FF0000;">"--start-system-server"</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        startSystemServer <span style="color: #000080;">=</span> <span style="color: #0000ff;">true</span><span style="color: #008080;">;</span>
 <span style="color: #ff0000; font-style: italic;">/*启动应用时会使用--application参数*/</span>             
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #0000dd;">strcmp</span><span style="color: #008000;">&#40;</span>arg, <span style="color: #FF0000;">"--application"</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        application <span style="color: #000080;">=</span> <span style="color: #0000ff;">true</span><span style="color: #008080;">;</span>
<span style="color: #ff0000; font-style: italic;">/*--nice-name=参数表示要设置的进程名字*/</span>            
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #0000dd;">strncmp</span><span style="color: #008000;">&#40;</span>arg, <span style="color: #FF0000;">"--nice-name="</span>, <span style="color: #0000dd;">12</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        niceName <span style="color: #000080;">=</span> arg <span style="color: #000040;">+</span> <span style="color: #0000dd;">12</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #008000;">&#123;</span>
        className <span style="color: #000080;">=</span> arg<span style="color: #008080;">;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
<span style="color: #008000;">&#125;</span>    
<span style="color: #ff0000; font-style: italic;">/*设置进程名*/</span>
<span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>niceName <span style="color: #000040;">&&</span> <span style="color: #000040;">*</span>niceName<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    setArgv0<span style="color: #008000;">&#40;</span>argv0, niceName<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    set_process_name<span style="color: #008000;">&#40;</span>niceName<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span>
<span style="color: #ff0000; font-style: italic;">/*设置虚拟机运行环境的父目录*/</span>
runtime.<span style="color: #007788;">mParentDir</span> <span style="color: #000080;">=</span> parentDir<span style="color: #008080;">;</span>
<span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>zygote<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
<span style="color: #ff0000; font-style: italic;">/*虚拟机里启动com.android.internal.os.ZygoteInit，
 *并传递参数start-system-server
 */</span>
    runtime.<span style="color: #007788;">start</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"com.android.internal.os.ZygoteInit"</span>,
            startSystemServer <span style="color: #008080;">?</span> <span style="color: #FF0000;">"start-system-server"</span> <span style="color: #008080;">:</span> <span style="color: #FF0000;">""</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>className<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>        
    <span style="color: #ff0000; font-style: italic;">/*若不是zygote，则启动的第一个类是com.android.internal.os.RuntimeInit，
     *RumtimeInit初始化后会启动mClassName
     */</span>
    runtime.<span style="color: #007788;">mClassName</span> <span style="color: #000080;">=</span> className<span style="color: #008080;">;</span>
    runtime.<span style="color: #007788;">mArgC</span> <span style="color: #000080;">=</span> argc <span style="color: #000040;">-</span> i<span style="color: #008080;">;</span>
    runtime.<span style="color: #007788;">mArgV</span> <span style="color: #000080;">=</span> argv <span style="color: #000040;">+</span> i<span style="color: #008080;">;</span>
    runtime.<span style="color: #007788;">start</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"com.android.internal.os.RuntimeInit"</span>,
            application <span style="color: #008080;">?</span> <span style="color: #FF0000;">"application"</span> <span style="color: #008080;">:</span> <span style="color: #FF0000;">"tool"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span> <span style="color: #0000ff;">else</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000dd;">fprintf</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">stderr</span>, <span style="color: #FF0000;">"Error: no class name or --zygote supplied.<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    app_usage<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    LOG_ALWAYS_FATAL<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"app_process: no class name or --zygote supplied."</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">return</span> <span style="color: #0000dd;">10</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span>
<span style="color: #666666;">//...</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

通过上述代码可知道zygote service将运行dalvik虚拟机，并在虚拟机里执行com.android.internal.os.ZygoteInit，还给它传递了参数start-system-server

## 3) ZygoteInit启动SystemServer

ZygoteInit启动时的相关源代码：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> main<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> argv<span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
<span style="color: #009900;">&#123;</span>
<span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>   
   <span style="color: #666666; font-style: italic;">//...</span>
   <span style="color: #666666; font-style: italic;">//在某个描述符上监听连接请求，</span>
   <span style="color: #666666; font-style: italic;">//其它Android空间的程序的启动都是通过连接zygote才孵化出来的</span>
   registerZygoteSocket<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #666666; font-style: italic;">//... </span>
   <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>argv<span style="color: #009900;">&#91;</span><span style="color: #cc66cc;">1</span><span style="color: #009900;">&#93;</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"start-system-server"</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//启动SystemServer</span>
        startSystemServer<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>argv<span style="color: #009900;">&#91;</span><span style="color: #cc66cc;">1</span><span style="color: #009900;">&#93;</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">""</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span>argv<span style="color: #009900;">&#91;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#93;</span> <span style="color: #339933;">+</span> USAGE_STRING<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
   <span style="color: #666666; font-style: italic;">//...</span>
   <span style="color: #666666; font-style: italic;">/*ZYGOTE_FORK_MODE默认为false，如果为true的话，每收到一个连接请求，
    *就会建立一个新进程，然后再运行连接请求所要求执行的命令，此时会建立另一个新进程
    */</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>ZYGOTE_FORK_MODE<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        runForkMode<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//使用Select poll的方式来建立新进程，收到连接请求后，也会建立进程启动某个程序</span>
        runSelectLoopMode<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    closeServerSocket<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span>MethodAndArgsCaller caller<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    caller.<span style="color: #006633;">run</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">RuntimeException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    Log.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Zygote died with exception"</span>, ex<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    closeServerSocket<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">throw</span> ex<span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

从上述代码可知道会调用startSystemServer以启动SystemServer,相关源代码如下：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">boolean</span> startSystemServer<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>
<span style="color: #009900;">&#123;</span>
<span style="color: #666666; font-style: italic;">/* Hardcoded command line to start the system server */</span>
<span style="color: #666666; font-style: italic;">//启动SystemServer使用的参数</span>
<span style="color: #003399;">String</span> args<span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #0000ff;">"--setuid=1000"</span>,
    <span style="color: #0000ff;">"--setgid=1000"</span>,
    <span style="color: #0000ff;">"--setgroups=1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1018,1021,3001,3002,3003,3004,3006,3007,3009"</span>,
    <span style="color: #0000ff;">"--capabilities=130104352,130104352"</span>,
    <span style="color: #0000ff;">"--runtime-init"</span>,
    <span style="color: #0000ff;">"--nice-name=system_server"</span>,
    <span style="color: #666666; font-style: italic;">//注意：就是在这里设置要启动的SystemServer包名及类名，故此后续才能启动SystemServer</span>
    <span style="color: #0000ff;">"com.android.server.SystemServer"</span>,
<span style="color: #009900;">&#125;</span><span style="color: #339933;">;</span>
ZygoteConnection.<span style="color: #006633;">Arguments</span> parsedArgs <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
<span style="color: #000066; font-weight: bold;">int</span> pid<span style="color: #339933;">;</span>
<span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">/*将args参数传给ZygoteConnection进行转化，--形式的参数将全部被接收
     * 但是要启动的类的类名com.android.server.SystemServer会放在
     *ZygoteConnection.Arguments的remainingArgs里，后来调用handleSystemServerProcess时会用到
     */</span>
    parsedArgs <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ZygoteConnection.<span style="color: #006633;">Arguments</span><span style="color: #009900;">&#40;</span>args<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
    <span style="color: #666666; font-style: italic;">/*添加额外运行参数*/</span>
    ZygoteConnection.<span style="color: #006633;">applyDebuggerSystemProperty</span><span style="color: #009900;">&#40;</span>parsedArgs<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    ZygoteConnection.<span style="color: #006633;">applyInvokeWithSystemProperty</span><span style="color: #009900;">&#40;</span>parsedArgs<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
    <span style="color: #666666; font-style: italic;">/*开启新进程*/</span>
    pid <span style="color: #339933;">=</span> Zygote.<span style="color: #006633;">forkSystemServer</span><span style="color: #009900;">&#40;</span>
            parsedArgs.<span style="color: #006633;">uid</span>, parsedArgs.<span style="color: #006633;">gid</span>,
            parsedArgs.<span style="color: #006633;">gids</span>,
            parsedArgs.<span style="color: #006633;">debugFlags</span>,
            <span style="color: #000066; font-weight: bold;">null</span>,
            parsedArgs.<span style="color: #006633;">permittedCapabilities</span>,
            parsedArgs.<span style="color: #006633;">effectiveCapabilities</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">IllegalArgumentException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span>ex<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span> 
<span style="color: #666666; font-style: italic;">/* For child process */</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>pid <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
	  <span style="color: #666666; font-style: italic;">/*调用handleSystemServerProcess会执行ZygoteConnection.Arguments的remainingArgs参数
	   *所指定的类，即com.android.server.SystemServer	   
	   */</span>
    handleSystemServerProcess<span style="color: #009900;">&#40;</span>parsedArgs<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

ZygoteInit的startSystemServer会调用forkSystemServer，然后：

ZygoteInit.forkSystemServer -> Zygote.nativeForkSystemServer-> dalvik\_system\_Zygote.cpp 里的Dalvik\_dalvik\_system\_Zygote\_forkSystemServer-> forkAndSpecializeCommon->fork建立新进程

ZygoteInit的startSystemServer会调用handleSystemServerProcess来真正启动systemserver，相关源代码如下：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> handleSystemServerProcess<span style="color: #009900;">&#40;</span>
            ZygoteConnection.<span style="color: #006633;">Arguments</span> parsedArgs<span style="color: #009900;">&#41;</span>
            <span style="color: #000000; font-weight: bold;">throws</span> ZygoteInit.<span style="color: #006633;">MethodAndArgsCaller</span> <span style="color: #009900;">&#123;</span>
<span style="color: #666666; font-style: italic;">//... </span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">niceName</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #003399;">Process</span>.<span style="color: #006633;">setArgV0</span><span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">niceName</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #666666; font-style: italic;">//启动systemserver时invokeWith为null</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">invokeWith</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    WrapperInit.<span style="color: #006633;">execApplication</span><span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">invokeWith</span>,
            parsedArgs.<span style="color: #006633;">niceName</span>, parsedArgs.<span style="color: #006633;">targetSdkVersion</span>,
            <span style="color: #000066; font-weight: bold;">null</span>, parsedArgs.<span style="color: #006633;">remainingArgs</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">/*
     * 启动systemserver时，parsedArgs.remainingArgs为com.android.server.SystemServer.
     */</span>
    RuntimeInit.<span style="color: #006633;">zygoteInit</span><span style="color: #009900;">&#40;</span>parsedArgs.<span style="color: #006633;">targetSdkVersion</span>, parsedArgs.<span style="color: #006633;">remainingArgs</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

然后的流程是

RuntimeInit.zygoteInit-> applicationInit，applicationInit的代码如下所示：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> applicationInit<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> targetSdkVersion, <span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> argv<span style="color: #009900;">&#41;</span>
<span style="color: #009900;">&#123;</span>
<span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #000000; font-weight: bold;">final</span> Arguments args<span style="color: #339933;">;</span>
<span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//参数转换,系统启动时，argv里有一个参数是com.android.server.SystemServer</span>
    args <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Arguments<span style="color: #009900;">&#40;</span>argv<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">IllegalArgumentException</span> ex<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    Slog.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>TAG, ex.<span style="color: #006633;">getMessage</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">// let the process exit</span>
    <span style="color: #000000; font-weight: bold;">return</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #666666; font-style: italic;">//终于在此启动了SystemServer</span>
invokeStaticMain<span style="color: #009900;">&#40;</span>args.<span style="color: #006633;">startClass</span>, args.<span style="color: #006633;">startArgs</span><span style="color: #009900;">&#41;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 4) SystemServer 启动过程

执行com.android.server.SystemServer时，main函数里会调用init1函数，init1函数是一个本地函数，init1的实现放在frameworks/base/services/jni/com\_android\_server\_SystemServer.cpp里，对应的jni函数是android\_server\_SystemServer\_init1，在该函数里会调用system\_init，而system\_init的实现是在frameworks/base/cmds/system\_server/library/system\_init.cpp，该函数的实现代码如下所示：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">extern</span> <span style="color: #FF0000;">"C"</span> status_t system_init<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
<span style="color: #666666;">//... </span>
sp<span style="color: #000080;">&lt;</span>ProcessState<span style="color: #000080;">&gt;</span> proc<span style="color: #008000;">&#40;</span>ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
sp<span style="color: #000080;">&lt;</span>IServiceManager<span style="color: #000080;">&gt;</span> sm <span style="color: #000080;">=</span> defaultServiceManager<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
ALOGI<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"ServiceManager: %p<span style="color: #000099; font-weight: bold;">\n</span>"</span>, sm.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
sp<span style="color: #000080;">&lt;</span>GrimReaper<span style="color: #000080;">&gt;</span> grim <span style="color: #000080;">=</span> <span style="color: #0000dd;">new</span> GrimReaper<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
sm<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>asBinder<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>linkToDeath<span style="color: #008000;">&#40;</span>grim, grim.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span>, <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #0000ff;">char</span> propBuf<span style="color: #008000;">&#91;</span>PROPERTY_VALUE_MAX<span style="color: #008000;">&#93;</span><span style="color: #008080;">;</span>
property_get<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"system_init.startsurfaceflinger"</span>, propBuf, <span style="color: #FF0000;">"1"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #0000dd;">strcmp</span><span style="color: #008000;">&#40;</span>propBuf, <span style="color: #FF0000;">"1"</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #666666;">// Start the SurfaceFlinger</span>
    SurfaceFlinger<span style="color: #008080;">::</span><span style="color: #007788;">instantiate</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span>
property_get<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"system_init.startsensorservice"</span>, propBuf, <span style="color: #FF0000;">"1"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span><span style="color: #0000dd;">strcmp</span><span style="color: #008000;">&#40;</span>propBuf, <span style="color: #FF0000;">"1"</span><span style="color: #008000;">&#41;</span> <span style="color: #000080;">==</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #666666;">// Start the sensor service</span>
    SensorService<span style="color: #008080;">::</span><span style="color: #007788;">instantiate</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span>
<span style="color: #666666;">// And now start the Android runtime.  We have to do this bit</span>
<span style="color: #666666;">// of nastiness because the Android runtime initialization requires</span>
<span style="color: #666666;">// some of the core system services to already be started.</span>
<span style="color: #666666;">// All other servers should just start the Android runtime at</span>
<span style="color: #666666;">// the beginning of their processes's main(), before calling</span>
<span style="color: #666666;">// the init function.</span>
ALOGI<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"System server: starting Android runtime.<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
AndroidRuntime<span style="color: #000040;">*</span> runtime <span style="color: #000080;">=</span> AndroidRuntime<span style="color: #008080;">::</span><span style="color: #007788;">getRuntime</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
ALOGI<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"System server: starting Android services.<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
JNIEnv<span style="color: #000040;">*</span> env <span style="color: #000080;">=</span> runtime<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>getJNIEnv<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>env <span style="color: #000080;">==</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">return</span> UNKNOWN_ERROR<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span>
jclass clazz <span style="color: #000080;">=</span> env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>FindClass<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"com/android/server/SystemServer"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>clazz <span style="color: #000080;">==</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">return</span> UNKNOWN_ERROR<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span>
<span style="color: #666666;">//反过来调用Java里SystemServer的init2函数</span>
jmethodID methodId <span style="color: #000080;">=</span> env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>GetStaticMethodID<span style="color: #008000;">&#40;</span>clazz, <span style="color: #FF0000;">"init2"</span>, <span style="color: #FF0000;">"()V"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>methodId <span style="color: #000080;">==</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">return</span> UNKNOWN_ERROR<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span>
env<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>CallStaticVoidMethod<span style="color: #008000;">&#40;</span>clazz, methodId<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
ALOGI<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"System server: entering thread pool.<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>startThreadPool<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
IPCThreadState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>joinThreadPool<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
ALOGI<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"System server: exiting thread pool.<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 5) 启动Java层的各种binder service

调用SystemServer的init2函数后，会开启新线程android.server.ServerThread，在新线程里会启动各种Java层的binder service，并在service manager里注册，这些Service大多开启了新线程运行，故此都是systemserver的子线程，添加的Service列表如下所示：

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
        <pre class="java" style="font-family:monospace;">ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"entropy"</span>, <span style="color: #000000; font-weight: bold;">new</span> EntropyMixer<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">POWER_SERVICE</span>, power<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">DISPLAY_SERVICE</span>, display, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"telephony.registry"</span>, telephonyRegistry<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">SCHEDULING_POLICY_SERVICE</span>,
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">USER_SERVICE</span>,UserManagerService.<span style="color: #006633;">getInstance</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">ACCOUNT_SERVICE</span>, accountManager<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"battery"</span>, battery<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"vibrator"</span>, vibrator<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">ALARM_SERVICE</span>, alarm<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">WINDOW_SERVICE</span>, wm<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">INPUT_SERVICE</span>, inputManager<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span>BluetoothAdapter.<span style="color: #006633;">BLUETOOTH_MANAGER_SERVICE</span>, bluetooth<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">INPUT_METHOD_SERVICE</span>, imm<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">ACCESSIBILITY_SERVICE</span>,<span style="color: #000000; font-weight: bold;">new</span> AccessibilityManagerService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"mount"</span>, mountService<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"lock_settings"</span>, lockSettings<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">DEVICE_POLICY_SERVICE</span>, devicePolicy<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">STATUS_BAR_SERVICE</span>, statusBar<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">CLIPBOARD_SERVICE</span>,<span style="color: #000000; font-weight: bold;">new</span> ClipboardService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">NETWORKMANAGEMENT_SERVICE</span>, networkManagement<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">TEXT_SERVICES_MANAGER_SERVICE</span>, tsms<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">NETWORK_STATS_SERVICE</span>, networkStats<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">NETWORK_POLICY_SERVICE</span>, networkPolicy<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">WIFI_P2P_SERVICE</span>, wifiP2p<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">WIFI_SERVICE</span>, wifi<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">CONNECTIVITY_SERVICE</span>, connectivity<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">NSD_SERVICE</span>, serviceDiscovery<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">THROTTLE_SERVICE</span>, throttle<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"fm_receiver"</span>,<span style="color: #000000; font-weight: bold;">new</span> FmReceiverService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"fm_transmitter"</span>,<span style="color: #000000; font-weight: bold;">new</span> FmTransmitterService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">UPDATE_LOCK_SERVICE</span>,<span style="color: #000000; font-weight: bold;">new</span> UpdateLockService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">PROFILE_SERVICE</span>, profile<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">NOTIFICATION_SERVICE</span>, notification<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span>DeviceStorageMonitorService.<span style="color: #006633;">SERVICE</span>,
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">LOCATION_SERVICE</span>, location<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">COUNTRY_DETECTOR</span>, countryDetector<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">SEARCH_SERVICE</span>,<span style="color: #000000; font-weight: bold;">new</span> SearchManagerService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">DROPBOX_SERVICE</span>,<span style="color: #000000; font-weight: bold;">new</span> DropBoxManagerService<span style="color: #009900;">&#40;</span>context, <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">File</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"/data/system/dropbox"</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">WALLPAPER_SERVICE</span>, wallpaper<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">AUDIO_SERVICE</span>, <span style="color: #000000; font-weight: bold;">new</span> AudioService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">USB_SERVICE</span>, usb<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">SERIAL_SERVICE</span>, serial<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">BACKUP_SERVICE</span>,<span style="color: #000000; font-weight: bold;">new</span> BackupManagerService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span>.<span style="color: #006633;">APPWIDGET_SERVICE</span>, appWidget<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"diskstats"</span>, <span style="color: #000000; font-weight: bold;">new</span> DiskStatsService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"samplingprofiler"</span>, <span style="color: #000000; font-weight: bold;">new</span> SamplingProfilerService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"commontime_management"</span>, commonTimeMgmtService<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span>DreamService.<span style="color: #006633;">DREAM_SERVICE</span>, dreamy<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"assetredirection"</span>, <span style="color: #000000; font-weight: bold;">new</span> AssetRedirectionManagerService<span style="color: #009900;">&#40;</span>context<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"pieservice"</span>, pieService<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

上述并没有看到将ActivityManagerService添加到servicemanager管理，它的添加过程比较特别。在线程android.server.ServerThread里会调用ActivityManagerService.setSystemProcess();setSystemProcess函数的代码如下所示：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> setSystemProcess<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
<span style="color: #666666; font-style: italic;">//…</span>
ActivityManagerService m <span style="color: #339933;">=</span> mSelf<span style="color: #339933;">;</span>            
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"activity"</span>, m, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"meminfo"</span>, <span style="color: #000000; font-weight: bold;">new</span> MemBinder<span style="color: #009900;">&#40;</span>m<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"gfxinfo"</span>, <span style="color: #000000; font-weight: bold;">new</span> GraphicsBinder<span style="color: #009900;">&#40;</span>m<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"dbinfo"</span>, <span style="color: #000000; font-weight: bold;">new</span> DbBinder<span style="color: #009900;">&#40;</span>m<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>MONITOR_CPU_USAGE<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"cpuinfo"</span>, <span style="color: #000000; font-weight: bold;">new</span> CpuBinder<span style="color: #009900;">&#40;</span>m<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
ServiceManager.<span style="color: #006633;">addService</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"permission"</span>, <span style="color: #000000; font-weight: bold;">new</span> PermissionController<span style="color: #009900;">&#40;</span>m<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
ApplicationInfo info <span style="color: #339933;">=</span>
    mSelf.<span style="color: #006633;">mContext</span>.<span style="color: #006633;">getPackageManager</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getApplicationInfo</span><span style="color: #009900;">&#40;</span>
                <span style="color: #0000ff;">"android"</span>, STOCK_PM_FLAGS<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
mSystemThread.<span style="color: #006633;">installSystemApplicationInfo</span><span style="color: #009900;">&#40;</span>info<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #666666; font-style: italic;">//…</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

可以看到ActivityManagerService采用了单例模式，并调用ServiceManager.addService(&#8220;activity&#8221;, m, true);将ActivityManagerService交给servicemanager管理，在ActivityManagerService里还添加了别的binder service，像MemBinder，GraphicsBinder，DbBinder。

最后会调用Looper.loop();进入loop循环，等待和别的程序通信。

## 6) 启动系统界面

线程android.server.ServerThread里有如下代码：

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
        <pre class="java" style="font-family:monospace;">ActivityManagerService.<span style="color: #006633;">self</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">systemReady</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Runnable</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        Slog.<span style="color: #006633;">i</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Making services ready"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>headless<span style="color: #009900;">&#41;</span> startSystemUi<span style="color: #009900;">&#40;</span>contextF<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
     <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

startSystemUi就是用于启动系统界面的，代码如下：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">void</span> startSystemUi<span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span> context<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        Intent intent <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Intent<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        intent.<span style="color: #006633;">setComponent</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> ComponentName<span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"com.android.systemui"</span>,
                    <span style="color: #0000ff;">"com.android.systemui.SystemUIService"</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//Slog.d(TAG, "Starting service: " + intent);</span>
        context.<span style="color: #006633;">startServiceAsUser</span><span style="color: #009900;">&#40;</span>intent, UserHandle.<span style="color: #006633;">OWNER</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

这样便启动了com.android.systemui应用，该应用将启动PowerUI和RingtonePlayer两个线程。

## 7) 启动Home 程序

线程android.server.ServerThread里有如下代码：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//…</span>
ActivityManagerService.<span style="color: #006633;">self</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">systemReady</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Runnable</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                  <span style="color: #666666; font-style: italic;">//…</span>
                <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #666666; font-style: italic;">//…</span></pre>
      </td>
    </tr>
  </table>
</div>

ActivityManagerService.self().systemReady有如下代码：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//…</span>
mMainStack.<span style="color: #006633;">resumeTopActivityLocked</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #666666; font-style: italic;">//…</span></pre>
      </td>
    </tr>
  </table>
</div>

ActivityStack. resumeTopActivityLocked()有如下代码：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">resumeTopActivityLocked<span style="color: #009900;">&#40;</span>prev, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

resumeTopActivityLocked的实现有如下代码：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//…</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>next <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">// There are no more activities!  Let's just start up the</span>
    <span style="color: #666666; font-style: italic;">// Launcher...</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mMainStack<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        ActivityOptions.<span style="color: #006633;">abort</span><span style="color: #009900;">&#40;</span>options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
        <span style="color: #000000; font-weight: bold;">return</span> mService.<span style="color: #006633;">startHomeActivityLocked</span><span style="color: #009900;">&#40;</span>mCurrentUser<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #666666; font-style: italic;">//…</span></pre>
      </td>
    </tr>
  </table>
</div>

mService类型是ActivityManagerService，ActivityManagerService. startHomeActivityLocked的实现有如下代码：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000066; font-weight: bold;">boolean</span> startHomeActivityLocked<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> userId<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
<span style="color: #666666; font-style: italic;">//…</span>
Intent intent <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Intent<span style="color: #009900;">&#40;</span>
    mTopAction,
    mTopData <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> Uri.<span style="color: #006633;">parse</span><span style="color: #009900;">&#40;</span>mTopData<span style="color: #009900;">&#41;</span> <span style="color: #339933;">:</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
intent.<span style="color: #006633;">setComponent</span><span style="color: #009900;">&#40;</span>mTopComponent<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #666666; font-style: italic;">//这里便添加了Intent.CATEGORY_HOME，</span>
<span style="color: #666666; font-style: italic;">//所有的Home应用都会都带有该类型的Activity，只有这样才会被认为是Home应用</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mFactoryTest <span style="color: #339933;">!=</span> SystemServer.<span style="color: #006633;">FACTORY_TEST_LOW_LEVEL</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    intent.<span style="color: #006633;">addCategory</span><span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">CATEGORY_HOME</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
ActivityInfo aInfo <span style="color: #339933;">=</span>
    resolveActivityInfo<span style="color: #009900;">&#40;</span>intent, STOCK_PM_FLAGS, userId<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>aInfo <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    intent.<span style="color: #006633;">setComponent</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> ComponentName<span style="color: #009900;">&#40;</span>
            aInfo.<span style="color: #006633;">applicationInfo</span>.<span style="color: #006633;">packageName</span>, aInfo.<span style="color: #006633;">name</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">// Don't do this if the home app is currently being</span>
    <span style="color: #666666; font-style: italic;">// instrumented.</span>
    aInfo <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ActivityInfo<span style="color: #009900;">&#40;</span>aInfo<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    aInfo.<span style="color: #006633;">applicationInfo</span> <span style="color: #339933;">=</span> getAppInfoForUser<span style="color: #009900;">&#40;</span>aInfo.<span style="color: #006633;">applicationInfo</span>, userId<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    ProcessRecord app <span style="color: #339933;">=</span> getProcessRecordLocked<span style="color: #009900;">&#40;</span>aInfo.<span style="color: #006633;">processName</span>,
            aInfo.<span style="color: #006633;">applicationInfo</span>.<span style="color: #006633;">uid</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>app <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">||</span> app.<span style="color: #006633;">instrumentationClass</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        intent.<span style="color: #006633;">setFlags</span><span style="color: #009900;">&#40;</span>intent.<span style="color: #006633;">getFlags</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">|</span> Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        mMainStack.<span style="color: #006633;">startActivityLocked</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span>, intent, <span style="color: #000066; font-weight: bold;">null</span>, aInfo,
                <span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #cc66cc;"></span>, <span style="color: #cc66cc;"></span>, <span style="color: #cc66cc;"></span>, <span style="color: #cc66cc;"></span>, <span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #000066; font-weight: bold;">false</span>, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

这样先找到使用Intent.CATEGORY_HOME声明的Activity组件，然后再调用mMainStack.startActivityLocked启动该Activity。

system server启动Home程序总结：

android.server.ServerThread->ActivityManagerService.self().systemReady->mMainStack.resumeTopActivityLocked->resumeTopActivityLocked-> mService.startHomeActivityLocked-> intent.addCategory(Intent.CATEGORY_HOME);mMainStack.startActivityLocked

## 总结

内核初始化好后，运行的第一个用户程序是init，init将启动init.rc里声明的多个service，跟Android空间相关的有servicemanager和zygote，servicemanager负责管理所有的binder service，zygote负责孵化所有Android空间的程序。zygote service对应的程序是app_process，不过加了一些启动参数，所以它会启动Java层的ZygoteInit，在ZygoteInit里会启动SystemServer，SystemServer分为两个阶段：本地的init1和Java层的init2，init2里会启动线程android.server.ServerThread。在android.server.ServerThread线程里会启动Java层的各种binder service，比如ActivityManagerService，PackageManagerService，WindowManagerService。然后调用ActivityManagerService的systemReady方法，在该方法里会启动系统界面以及Home程序。