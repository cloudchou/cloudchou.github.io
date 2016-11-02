---
id: 947
title: 'Android单元测试利器&#8211;Robolectric  ShadowDemo'
date: 2016-07-07T09:25:13+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=947
permalink: /android/post-947.html
views:
  - 521
categories:
  - Android
  - 个人总结
tags:
  - Android单元测试
  - Robolectric
  - Robolectric Shadow
---
<a href="http://www.cloudchou.com/tag/android%e5%8d%95%e5%85%83%e6%b5%8b%e8%af%95" title="View all posts in Android单元测试" target="_blank" class="tags">Android单元测试</a>系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> 

## Shadow测试Demo

其实<a href="http://www.cloudchou.com/tag/robolectric" title="View all posts in Robolectric" target="_blank" class="tags">Robolectric</a>对Android API的支持都是通过为各个API类建立Shadow类实现支持的，比如SystemProperties类，在Robolectric框架中有一个对应的ShadowSystemProperties，在Shadow类中只需要实现想mock的方法即可，不需要实现原始类的所有方法，这样当调用Android API类的方法时，实际上是调用Shadow类中的方法，所以通过这种方式实现了对Android系统API的mock。我们来看一下ShadowSystemProperties的实现:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #008000; font-style: italic; font-weight: bold;">/**
 * Shadow for {@link android.os.SystemProperties}.
 */</span>
<span style="color: #666666; font-style: italic;">//下述注解表明是针对SystemProperties类的Shadow类，isInAndroidSdk表示原始类是否是在Android Sdk中暴露的,</span>
<span style="color: #666666; font-style: italic;">//因为SystemProperities类实际上是一个隐藏类，所以这里isInAndroidSdk=false</span>
@<span style="color: #000000; font-weight: bold;">Implements</span><span style="color: #009900;">&#40;</span>value <span style="color: #339933;">=</span> SystemProperties.<span style="color: #000000; font-weight: bold;">class</span>, isInAndroidSdk <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> ShadowSystemProperties <span style="color: #009900;">&#123;</span>
  <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> Map<span style="color: #339933;">&lt;</span><span style="color: #003399;">String</span>, Object<span style="color: #339933;">&gt;</span> VALUES <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> HashMap<span style="color: #339933;">&lt;&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> Set<span style="color: #339933;">&lt;</span>String<span style="color: #339933;">&gt;</span> alreadyWarned <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> HashSet<span style="color: #339933;">&lt;&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
  <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #009900;">&#123;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.version.release"</span>, <span style="color: #0000ff;">"2.2"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.version.incremental"</span>, <span style="color: #0000ff;">"0"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.version.sdk"</span>, <span style="color: #cc66cc;">8</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.date.utc"</span>, 1277708400000L<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>  <span style="color: #666666; font-style: italic;">// Jun 28, 2010</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.debuggable"</span>, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.secure"</span>, <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.cpu.abilist"</span>, <span style="color: #0000ff;">"armeabi-v7a"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.cpu.abilist32"</span>, <span style="color: #0000ff;">"armeabi-v7a,armeabi"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.cpu.abilist64"</span>, <span style="color: #0000ff;">"armeabi-v7a,armeabi"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.fingerprint"</span>, <span style="color: #0000ff;">"robolectric"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.version.all_codenames"</span>, <span style="color: #0000ff;">"REL"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"log.closeguard.Animation"</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">// disable vsync for Choreographer</span>
    VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"debug.choreographer.vsync"</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
  <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #008000; font-style: italic; font-weight: bold;">/** 实现对get方法的mock
  */</span>
  @Implementation
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> get<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #003399;">Object</span> o <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>o <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      warnUnknown<span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #0000ff;">""</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #000000; font-weight: bold;">return</span> o.<span style="color: #006633;">toString</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
  @Implementation
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> get<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #003399;">String</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> value.<span style="color: #006633;">toString</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #008000; font-style: italic; font-weight: bold;">/** 实现对getInt方法的mock
  */</span>
  @Implementation
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">int</span> getInt<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">int</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Integer</span><span style="color: #009900;">&#41;</span> value<span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #008000; font-style: italic; font-weight: bold;">/** 实现对getLong方法的mock
  */</span>
  @Implementation
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">long</span> getLong<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">long</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Long</span><span style="color: #009900;">&#41;</span> value<span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #008000; font-style: italic; font-weight: bold;">/** 实现对getBoolean方法的mock
  */</span>
  @Implementation
  <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">boolean</span> getBoolean<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">boolean</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Boolean</span><span style="color: #009900;">&#41;</span> value<span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> warnUnknown<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>alreadyWarned.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #003399;">System</span>.<span style="color: #006633;">err</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"WARNING: no system properties value for "</span> <span style="color: #339933;">+</span> key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

原始的SystemProperties类本来是从系统的属性服务里读取属性，Robolectric为了实现mock，将事先定义好的部分属性直接hardcode在代码里，应用获取系统属性时会调用到ShadowSystemProperties类的get方法，这时候就可以直接从内存里取值并返回给应用了。我们知道android.os.Build类的很多字段的值其实都是通过SystemProperties类的get方法获得的，比如Build.brand对应的属性key是ro.product.brand，而Build.MODEL对应的属性key是ro.product.model，但是在上述ShadowSystemProperties里并没有这些属性设置值，所以当我们读取Build.brand或者Build.model时得到的值都是unknown.

但是我们可以利用Roblectric创建自己的针对系统Api类的mock类，比如我们也创建一个CloudSystemProperties类，实现如下所示:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">@<span style="color: #000000; font-weight: bold;">Implements</span><span style="color: #009900;">&#40;</span>value <span style="color: #339933;">=</span> SystemProperties.<span style="color: #000000; font-weight: bold;">class</span>, isInAndroidSdk <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> CloudSystemProperties <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> Map<span style="color: #339933;">&lt;</span><span style="color: #003399;">String</span>, Object<span style="color: #339933;">&gt;</span> VALUES <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> HashMap<span style="color: #339933;">&lt;&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> Set<span style="color: #339933;">&lt;</span>String<span style="color: #339933;">&gt;</span> alreadyWarned <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> HashSet<span style="color: #339933;">&lt;&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #009900;">&#123;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.version.release"</span>, <span style="color: #0000ff;">"2.2"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.version.incremental"</span>, <span style="color: #0000ff;">"0"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.version.sdk"</span>, <span style="color: #cc66cc;">8</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.date.utc"</span>, 1277708400000L<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>  <span style="color: #666666; font-style: italic;">// Jun 28, 2010</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.debuggable"</span>, <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.secure"</span>, <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.cpu.abilist"</span>, <span style="color: #0000ff;">"armeabi-v7a"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.cpu.abilist32"</span>, <span style="color: #0000ff;">"armeabi-v7a,armeabi"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.cpu.abilist64"</span>, <span style="color: #0000ff;">"armeabi-v7a,armeabi"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.fingerprint"</span>, <span style="color: #0000ff;">"robolectric"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.version.all_codenames"</span>, <span style="color: #0000ff;">"REL"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"log.closeguard.Animation"</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">// disable vsync for Choreographer </span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"debug.choreographer.vsync"</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
        <span style="color: #666666; font-style: italic;">//添加了如下属性</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"persist.radio.multisim.config"</span>, <span style="color: #0000ff;">"DSDS"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.device"</span>, <span style="color: #0000ff;">"GT-I9100G"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.board"</span>, <span style="color: #0000ff;">"t1"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.product"</span>, <span style="color: #0000ff;">"GT-I9100G"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.brand"</span>, <span style="color: #0000ff;">"samsung"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.model"</span>, <span style="color: #0000ff;">"GT-I9100G"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VALUES.<span style="color: #006633;">put</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.build.fingerprint"</span>, 
        <span style="color: #0000ff;">"samsung/GT-I9100G/GT-I9100G:4.1.2/JZO54K/I9100GXXLSR:user/release-keys"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> get<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Object</span> o <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>o <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            warnUnknown<span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #0000ff;">""</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #000000; font-weight: bold;">return</span> o.<span style="color: #006633;">toString</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> get<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #003399;">String</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> value.<span style="color: #006633;">toString</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">int</span> getInt<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">int</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Integer</span><span style="color: #009900;">&#41;</span> value<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">long</span> getLong<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">long</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Long</span><span style="color: #009900;">&#41;</span> value<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">boolean</span> getBoolean<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">boolean</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> VALUES.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Boolean</span><span style="color: #009900;">&#41;</span> value<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> warnUnknown<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>alreadyWarned.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #003399;">System</span>.<span style="color: #006633;">err</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"WARNING: no system properties value for "</span> <span style="color: #339933;">+</span> key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

这样我们就可以获取Build.brand和Build.model的值了，在编写测试的时候指定Shadow类即可测试了:

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
        <pre class="java" style="font-family:monospace;">@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> ShadowTest <span style="color: #009900;">&#123;</span>
&nbsp;
  <span style="color: #666666; font-style: italic;">//指定使用Roblectric框架的ShadowSystemProperties来对SystemProperties类mock</span>
    @Config<span style="color: #009900;">&#40;</span>shadows <span style="color: #339933;">=</span> <span style="color: #009900;">&#123;</span>ShadowSystemProperties.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
    @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testEvn<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">IllegalAccessException</span>, <span style="color: #003399;">NoSuchFieldException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">VERSION</span>.<span style="color: #006633;">RELEASE</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">Context</span> ctx <span style="color: #339933;">=</span> RuntimeEnvironment.<span style="color: #006633;">application</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">VERSION</span>.<span style="color: #006633;">SDK_INT</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">DEVICE</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">FINGERPRINT</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">BRAND</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">BOARD</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">MODEL</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
    <span style="color: #009900;">&#125;</span>
&nbsp;
   <span style="color: #666666; font-style: italic;">//指定使用Roblectric框架的CloudSystemProperties来对SystemProperties类mock</span>
    @Config<span style="color: #009900;">&#40;</span>shadows <span style="color: #339933;">=</span> <span style="color: #009900;">&#123;</span>CloudSystemProperties.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
    @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testEvn2<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">IllegalAccessException</span>, <span style="color: #003399;">NoSuchFieldException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">VERSION</span>.<span style="color: #006633;">RELEASE</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">Context</span> ctx <span style="color: #339933;">=</span> RuntimeEnvironment.<span style="color: #006633;">application</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">VERSION</span>.<span style="color: #006633;">SDK_INT</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">DEVICE</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">FINGERPRINT</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">BRAND</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">BOARD</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">MODEL</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

testEvn执行的测试结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp1.png" alt="ShadowSysProp1" width="1008" height="313" class="aligncenter size-full wp-image-940" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp1.png 1008w, http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp1-300x93.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp1-768x238.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp1-200x62.png 200w" sizes="(max-width: 1008px) 100vw, 1008px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp1.png)

testEvn2执行的测试结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2-1024x261.png" alt="ShadowSysProp2" width="1024" height="261" class="aligncenter size-large wp-image-941" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2-1024x261.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2-300x77.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2-768x196.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2-200x51.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2.png 1042w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2.png)

可以看出来CloudSystemProperties对SystemProperties类的mock是有效的.

## 加载代码中的资源文件Demo

我们还可以将某个机型的system/build.prop文件作为资源保存在代码里，然后实现SystemProperties的mock时，直接从该该资源文件里读取更加方便，这样可以实现对某个机型的属性的模拟。

测试代码如下所示,CloudSystemProperties2实现另一个对SystemProperites的Shadow

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">@<span style="color: #000000; font-weight: bold;">Implements</span><span style="color: #009900;">&#40;</span>value <span style="color: #339933;">=</span> SystemProperties.<span style="color: #000000; font-weight: bold;">class</span>, isInAndroidSdk <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> CloudSystemProperties2 <span style="color: #009900;">&#123;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> get<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Properties</span> prop <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Properties</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">String</span> name <span style="color: #339933;">=</span> <span style="color: #0000ff;">"i9100g.properties"</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">InputStream</span> is <span style="color: #339933;">=</span> CloudSystemProperties2.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getClassLoader</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getResourceAsStream</span><span style="color: #009900;">&#40;</span>name<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            prop.<span style="color: #006633;">load</span><span style="color: #009900;">&#40;</span>is<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">return</span> prop.<span style="color: #006633;">getProperty</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">IOException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                is.<span style="color: #006633;">close</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">IOException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> get<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #003399;">String</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Object</span> value <span style="color: #339933;">=</span> get<span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> value.<span style="color: #006633;">toString</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">int</span> getInt<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">int</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">String</span> value <span style="color: #339933;">=</span> get<span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #003399;">Integer</span>.<span style="color: #006633;">parseInt</span><span style="color: #009900;">&#40;</span>value<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">long</span> getLong<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">long</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">String</span> value <span style="color: #339933;">=</span> get<span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Long</span><span style="color: #009900;">&#41;</span> <span style="color: #003399;">Long</span>.<span style="color: #006633;">parseLong</span><span style="color: #009900;">&#40;</span>value<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Implementation
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">boolean</span> getBoolean<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> key, <span style="color: #000066; font-weight: bold;">boolean</span> def<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">String</span> value <span style="color: #339933;">=</span> get<span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> value <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">?</span> def <span style="color: #339933;">:</span> <span style="color: #003399;">Boolean</span>.<span style="color: #006633;">parseBoolean</span><span style="color: #009900;">&#40;</span>value<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

i9100g.properties内容如下所示:

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
        <pre class="java" style="font-family:monospace;">ro.<span style="color: #006633;">build</span>.<span style="color: #006633;">version</span>.<span style="color: #006633;">release</span><span style="color: #339933;">=</span><span style="color: #cc66cc;">2.2</span>
ro.<span style="color: #006633;">build</span>.<span style="color: #006633;">version</span>.<span style="color: #006633;">incremental</span><span style="color: #339933;">=</span><span style="color: #cc66cc;"></span>
ro.<span style="color: #006633;">build</span>.<span style="color: #006633;">version</span>.<span style="color: #006633;">sdk</span><span style="color: #339933;">=</span><span style="color: #cc66cc;">8</span>
ro.<span style="color: #006633;">build</span>.<span style="color: #006633;">date</span>.<span style="color: #006633;">utc</span><span style="color: #339933;">=</span><span style="color: #cc66cc;">1277708400000</span>
ro.<span style="color: #006633;">debuggable</span><span style="color: #339933;">=</span><span style="color: #cc66cc;"></span>
ro.<span style="color: #006633;">secure</span><span style="color: #339933;">=</span><span style="color: #cc66cc;">1</span>
ro.<span style="color: #006633;">product</span>.<span style="color: #006633;">cpu</span>.<span style="color: #006633;">abilist</span><span style="color: #339933;">=</span>armeabi<span style="color: #339933;">-</span>v7a
ro.<span style="color: #006633;">product</span>.<span style="color: #006633;">cpu</span>.<span style="color: #006633;">abilist32</span><span style="color: #339933;">=</span>armeabi<span style="color: #339933;">-</span>v7a,armeabi
ro.<span style="color: #006633;">product</span>.<span style="color: #006633;">cpu</span>.<span style="color: #006633;">abilist64</span><span style="color: #339933;">=</span>armeabi<span style="color: #339933;">-</span>v7a,armeabi
ro.<span style="color: #006633;">build</span>.<span style="color: #006633;">fingerprint</span><span style="color: #339933;">=</span>robolectric
ro.<span style="color: #006633;">build</span>.<span style="color: #006633;">version</span>.<span style="color: #006633;">all_codenames</span><span style="color: #339933;">=</span>REL
log.<span style="color: #006633;">closeguard</span>.<span style="color: #006633;">Animation</span><span style="color: #339933;">=</span><span style="color: #000066; font-weight: bold;">false</span>
debug.<span style="color: #006633;">choreographer</span>.<span style="color: #006633;">vsync</span><span style="color: #339933;">=</span><span style="color: #000066; font-weight: bold;">false</span>
debug.<span style="color: #006633;">choreographer</span>.<span style="color: #006633;">vsync</span><span style="color: #339933;">=</span><span style="color: #000066; font-weight: bold;">false</span>
persist.<span style="color: #006633;">radio</span>.<span style="color: #006633;">multisim</span>.<span style="color: #006633;">config</span><span style="color: #339933;">=</span>DSDS
ro.<span style="color: #006633;">product</span>.<span style="color: #006633;">device</span><span style="color: #339933;">=</span>GT<span style="color: #339933;">-</span>I9100G
ro.<span style="color: #006633;">product</span>.<span style="color: #006633;">board</span><span style="color: #339933;">=</span>t1
ro.<span style="color: #006633;">build</span>.<span style="color: #006633;">product</span><span style="color: #339933;">=</span>GT<span style="color: #339933;">-</span>I9100G
ro.<span style="color: #006633;">product</span>.<span style="color: #006633;">brand</span><span style="color: #339933;">=</span>samsung
ro.<span style="color: #006633;">product</span>.<span style="color: #006633;">model</span><span style="color: #339933;">=</span>GT<span style="color: #339933;">-</span>I9100G
ro.<span style="color: #006633;">build</span>.<span style="color: #006633;">fingerprint</span><span style="color: #339933;">=</span>samsung<span style="color: #339933;">/</span>GT<span style="color: #339933;">-</span>I9100G<span style="color: #339933;">/</span>GT<span style="color: #339933;">-</span>I9100G<span style="color: #339933;">:</span>4.1.2<span style="color: #339933;">/</span>JZO54K<span style="color: #339933;">/</span>I9100GXXLSR<span style="color: #339933;">:</span>user<span style="color: #339933;">/</span>release<span style="color: #339933;">-</span>keys</pre>
      </td>
    </tr>
  </table>
</div>

测试用例代码:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #339933;">**</span>
 <span style="color: #339933;">*</span> Created by Cloud on <span style="color: #cc66cc;">2016</span><span style="color: #339933;">/</span><span style="color: #cc66cc;">6</span><span style="color: #339933;">/</span><span style="color: #cc66cc;">27</span>.
 <span style="color: #339933;">*/</span>
@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> ShadowTest <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">// ...</span>
    @Config<span style="color: #009900;">&#40;</span>shadows <span style="color: #339933;">=</span> <span style="color: #009900;">&#123;</span>CloudSystemProperties2.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
    @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testShadow2<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">IllegalAccessException</span>, <span style="color: #003399;">NoSuchFieldException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">VERSION</span>.<span style="color: #006633;">RELEASE</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">VERSION</span>.<span style="color: #006633;">SDK_INT</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">DEVICE</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">FINGERPRINT</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">BRAND</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">BOARD</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>Build.<span style="color: #006633;">MODEL</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

如果仅仅是这样做，是不够的，在AndroidStudio中执行这个单元测试，会在运行getClassLoader().getResourceAsStream(name)时因为找不到资源而抛出NullPointerException，如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions-1024x345.png" alt="resource-exceptions" width="1024" height="345" class="aligncenter size-large wp-image-938" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions-1024x345.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions-300x101.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions-768x258.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions-200x67.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions.png 1061w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions.png)

出现该问题的根本原因是getResourceAsStream函数在查找资源时，默认是在编译生成的类所在的文件夹里进行查找，而不是在源代码文件所在的文件夹查找，所以我们需要将i9100g.prop文件默认就拷贝到CloudSystemProperties生成的类文件所在的目录中，因此我们需要修改build.gradle，让它在执行测试前就将i9100g自动拷贝到它需要在的位置。 修改后的build.gradle如下所示:

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
        <pre class="java" style="font-family:monospace;">android<span style="color: #009900;">&#123;</span>
  <span style="color: #666666; font-style: italic;">//...</span>
  testOptions <span style="color: #009900;">&#123;</span>
        unitTests.<span style="color: #006633;">all</span> <span style="color: #009900;">&#123;</span>
            beforeTest <span style="color: #009900;">&#123;</span>
                def testClassDir <span style="color: #339933;">=</span> buildDir.<span style="color: #006633;">getAbsolutePath</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">"/intermediates/classes/test/debug"</span>
                copy <span style="color: #009900;">&#123;</span>
                    from<span style="color: #009900;">&#40;</span>android.<span style="color: #006633;">sourceSets</span>.<span style="color: #006633;">test</span>.<span style="color: #006633;">java</span>.<span style="color: #006633;">srcDirs</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        exclude <span style="color: #0000ff;">"**/*.java"</span>
                    <span style="color: #009900;">&#125;</span>
                    into<span style="color: #009900;">&#40;</span>testClassDir<span style="color: #009900;">&#41;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>	
  <span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

在代码文件里直接执行testShadow2之前，需先通过gralde执行testDebugUnitTest目标，否则也不会自动拷贝i9100g.prop文件到它需要的位置，执行这个命令之后就可以在代码中直接运行testShadow2测试了，通过gralde执行testDebugUnitTest目标可在命令行下执行如下命令:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">gradlew.<span style="color: #006633;">bat</span> <span style="color: #339933;">:</span>app<span style="color: #339933;">:</span>testDebugUnitTest</pre>
      </td>
    </tr>
  </table>
</div>

执行结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result-1024x270.png" alt="resource_load_result" width="1024" height="270" class="aligncenter size-large wp-image-937" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result-1024x270.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result-300x79.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result-768x202.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result-200x53.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result.png 1200w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result.png)