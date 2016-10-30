---
id: 966
title: 'Android单元测试利器&#8211;Robolectric 多线程Demo'
date: 2016-07-18T08:46:45+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=966
permalink: /android/post-966.html
views:
  - 499
categories:
  - Android
  - 个人总结
tags:
  - Android单元测试
  - Android单元测试 Robolectric
  - Android单元测试 多线程
  - Powermock 多线程
  - Robolectric 多线程
---
<a href="http://www.cloudchou.com/tag/android%e5%8d%95%e5%85%83%e6%b5%8b%e8%af%95" title="View all posts in Android单元测试" target="_blank" class="tags">Android单元测试</a>系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> 

## 多线程测试Demo

本节使用Robolectric+powermock测试多线程的场景。

首先，我们看一下，被测试的类的源码，HelloThread的init方法主要功能是启动一个线程，然后在新线程内部做实际初始化，实际初始化完毕后将初始化状态标志为成功或者失败，在本场景里将状态标志为失败。在非多线程的场景中，我们进行单元测试时，通常直接对被测试函数的返回值做校验，而多线程场景中，因为实际功能在另外一条线程里完成，所以对函数的返回值做校验并没有实际价值，但是我们可以通过校验日志来看执行效果。

被测试的类的源码如下所示:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> HelloThread <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> InitStatus mInitStatus <span style="color: #339933;">=</span> InitStatus.<span style="color: #006633;">INIT</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> TAG <span style="color: #339933;">=</span> HelloThread.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getSimpleName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">enum</span> InitStatus <span style="color: #009900;">&#123;</span>
        INIT,
        INITING,
        OK,
        FAILED
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> HelloThread<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">class</span> HelloThreadHolder <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> HelloThread sInstance <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> HelloThread<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> HelloThread getInstance<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> HelloThreadHolder.<span style="color: #006633;">sInstance</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> init<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mInitStatus <span style="color: #339933;">==</span> InitStatus.<span style="color: #006633;">INIT</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            mInitStatus <span style="color: #339933;">=</span> InitStatus.<span style="color: #006633;">INITING</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Thread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                @Override
                <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    internalInit<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>.<span style="color: #006633;">start</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> internalInit<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"========&lt; start init ===&gt;&gt;&gt;"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            doSomething<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            setInitStatus<span style="color: #009900;">&#40;</span>InitStatus.<span style="color: #006633;">OK</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Throwable</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>          
            <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"========&lt; init failed ===&gt;&gt;&gt;"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #666666; font-style: italic;">//初始化失败后打印日志，这也是我们写程序时时常见的一种做法，</span>
            <span style="color: #666666; font-style: italic;">//通过日志能帮助程序员更好地定位问题</span>
            SLog.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"init failed"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            setInitStatus<span style="color: #009900;">&#40;</span>InitStatus.<span style="color: #006633;">FAILED</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"========&lt; finish init ===&gt;&gt;&gt;"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> setInitStatus<span style="color: #009900;">&#40;</span>InitStatus status<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        mInitStatus <span style="color: #339933;">=</span> status<span style="color: #339933;">;</span>
        notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> waitForInitFinished<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>mInitStatus <span style="color: #339933;">==</span> InitStatus.<span style="color: #006633;">INITING</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> doSomething<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Thread</span>.<span style="color: #006633;">sleep</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">3500</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//假设初始化失败</span>
        <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"som exception"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

从代码中可以看到我们在初始化失败时，会打印error日志，这也让我们的校验有了可行性。通过前述章节，我们知道可以对SLog做静态partial mock， 然后在测试init时，收集执行数据，最后对SLog进行校验，看其是否打印了指定的error日志即可。 测试代码如下所示:

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
        <pre class="java" style="font-family:monospace;">@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//必须写如下代码 让PowerMock 忽略Robolectric的所有注入</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类</span>
@PrepareForTest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span>SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> HelloThreadTest <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试</span>
    <span style="color: #666666; font-style: italic;">//但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试</span>
    @Rule
    <span style="color: #000000; font-weight: bold;">public</span> PowerMockRule rule <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> PowerMockRule<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    @Before
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> setup<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        PowerMockito.<span style="color: #006633;">mockStatic</span><span style="color: #009900;">&#40;</span>SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testInit<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">Exception</span> <span style="color: #009900;">&#123;</span>
        PowerMockito.<span style="color: #006633;">spy</span><span style="color: #009900;">&#40;</span>SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloThread.<span style="color: #006633;">getInstance</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">init</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloThread.<span style="color: #006633;">getInstance</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">waitForInitFinished</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #666666; font-style: italic;">//因为我们在被测试代码里调用了SLog.e 日志， 所以verifyStatic  必然失败</span>
        PowerMockito.<span style="color: #006633;">verifyStatic</span><span style="color: #009900;">&#40;</span>times<span style="color: #009900;">&#40;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        SLog.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>HelloThread.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getSimpleName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, <span style="color: #0000ff;">"init failed"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

执行结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/robolectr_thread_demo.png" alt="robolectr_thread_demo" width="941" height="349" class="aligncenter size-full wp-image-939" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/robolectr_thread_demo.png 941w, http://www.cloudchou.com/wp-content/uploads/2016/07/robolectr_thread_demo-300x111.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/robolectr_thread_demo-768x285.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/robolectr_thread_demo-200x74.png 200w" sizes="(max-width: 941px) 100vw, 941px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/robolectr_thread_demo.png)

可以看到使用PowerMock 对 多线程程序做校验是非常方便的