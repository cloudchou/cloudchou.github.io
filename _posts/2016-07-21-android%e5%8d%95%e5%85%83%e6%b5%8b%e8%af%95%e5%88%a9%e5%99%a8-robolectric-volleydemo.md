---
id: 972
title: 'Android单元测试利器&#8211;Robolectric VolleyDemo'
date: 2016-07-21T08:51:59+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=972
permalink: /android/post-972.html
views:
  - 548
categories:
  - Android
  - 个人总结
tags:
  - Android 单元测试
  - Android 单元测试 Robolectric
  - Roblectric测试UI线程
  - Robolectric powermock
  - Robolectric测试主线程
---
Android单元测试系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> 

## 使用Robolectric+Powermock测试UI线程逻辑

本节讲述如何使用Robolectric+PowerMock测试需要在UI线程执行的逻辑，比如Volley框架，在后台线程中请求网络，请求完成后在UI线程里通过Listener接口通知请求完成，并传递请求回来的数据。

在使用Robolectric框架测试需要在UI线程执行的逻辑时，需要注意的是在Android平台UI线程会轮询消息队列，然后从消息队列里取出消息，并将消息分发给Handler处理，UI线程执行的是轮询消息队列的死循环。但是在Robolectric框架中运行时，UI线程默认情况下并不会轮询消息队列，而需要在测试用例代码里主动驱动UI线程从消息队列里取出消息进行分发。测试用例执行时并不在UI线程，而是在单独的线程中，所以它可以主动驱动UI线程分发消息。

本节使用Volley请求来讲述如何针对这种情况进行测试，首先我们来看被测试的类VolleyRequest，它非常简单，使用了OkHttp作为传输层，请求<a href='http://www.mocky.io/v2/5597d86a6344715505576725' target='_blank' >http://www.mocky.io/v2/5597d86a6344715505576725</a>，然后将请求的数据保存下来。源代码如下所示:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> VolleyRequester <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> TAG <span style="color: #339933;">=</span> VolleyRequester.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getSimpleName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> RequestQueue mRequestQueue<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">Context</span> mContext<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">volatile</span> <span style="color: #003399;">String</span> mResponseStr<span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> request<span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span> context<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        mContext <span style="color: #339933;">=</span> context<span style="color: #339933;">;</span>
        RequestQueue volleyRequestQueue <span style="color: #339933;">=</span> getVolleyRequestQueue<span style="color: #009900;">&#40;</span>mContext<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//请求的url 请求该URL会返回一段json字符串</span>
        <span style="color: #666666; font-style: italic;">//测试时 如果将其改成一个 无法访问的网址 就可以测试访问失败的情况</span>
        <span style="color: #003399;">String</span> url <span style="color: #339933;">=</span> <span style="color: #0000ff;">"http://www.mocky.io/v2/5597d86a6344715505576725"</span><span style="color: #339933;">;</span>
        Response.<span style="color: #006633;">Listener</span><span style="color: #339933;">&lt;</span>String<span style="color: #339933;">&gt;</span> dataListener <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Response.<span style="color: #006633;">Listener</span><span style="color: #339933;">&lt;</span>String<span style="color: #339933;">&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            @Override
            <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onResponse<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> response<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"received response. "</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                mResponseStr <span style="color: #339933;">=</span> response<span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span><span style="color: #339933;">;</span>
        Response.<span style="color: #006633;">ErrorListener</span> errorListener <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Response.<span style="color: #006633;">ErrorListener</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            @Override
            <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> onErrorResponse<span style="color: #009900;">&#40;</span>VolleyError error<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #666666; font-style: italic;">//请求失败 会打印error日志</span>
                SLog.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"request failed"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span><span style="color: #339933;">;</span>
        StringRequest request <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> StringRequest<span style="color: #009900;">&#40;</span><span style="color: #003399;">Request</span>.<span style="color: #003399;">Method</span>.<span style="color: #006633;">POST</span>, url, dataListener, errorListener<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        volleyRequestQueue.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span>request<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">String</span> getResponseString<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> mResponseStr<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> RequestQueue getVolleyRequestQueue<span style="color: #009900;">&#40;</span><span style="color: #003399;">Context</span> ctx<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mRequestQueue <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">// 使用OkHttp 作为传输层</span>
            mRequestQueue <span style="color: #339933;">=</span> Volley.<span style="color: #006633;">newRequestQueue</span><span style="color: #009900;">&#40;</span>ctx, <span style="color: #000000; font-weight: bold;">new</span> OkHttpStack<span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> OkHttpClient<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #000000; font-weight: bold;">return</span> mRequestQueue<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">class</span> OkHttpStack <span style="color: #000000; font-weight: bold;">extends</span> HurlStack <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">private</span> OkHttpClient mOkHttpClient<span style="color: #339933;">;</span>
&nbsp;
        <span style="color: #000000; font-weight: bold;">public</span> OkHttpStack<span style="color: #009900;">&#40;</span>OkHttpClient okHttpClient<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            mOkHttpClient <span style="color: #339933;">=</span> okHttpClient<span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        @Override
        <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #003399;">HttpURLConnection</span> createConnection<span style="color: #009900;">&#40;</span><span style="color: #003399;">URL</span> url<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">IOException</span> <span style="color: #009900;">&#123;</span>
            OkUrlFactory factory <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> OkUrlFactory<span style="color: #009900;">&#40;</span>mOkHttpClient<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">return</span> factory.<span style="color: #006633;">open</span><span style="color: #009900;">&#40;</span>url<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

接下来我们看看如何驱动主线程轮询消息队列，测试代码如下所示:

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
        <pre class="java" style="font-family:monospace;">&nbsp;
<span style="color: #008000; font-style: italic; font-weight: bold;">/**
 * date 2016/7/3
 *
 * @author Cloud
 * @version 1.1
 * @since Ver 1.1
 */</span>
@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//必须写如下代码 让PowerMock 忽略Robolectric的所有注入 这里因为要使用https 所以还需要忽略ssl</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span>, <span style="color: #0000ff;">"javax.net.ssl.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类</span>
@PrepareForTest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span>SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> VolleyRequesterTest <span style="color: #009900;">&#123;</span>
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
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testRequest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">Exception</span> <span style="color: #009900;">&#123;</span>
        PowerMockito.<span style="color: #006633;">spy</span><span style="color: #009900;">&#40;</span>SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        VolleyRequester requester <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> VolleyRequester<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//调用请求方法后 volley 会开启后台线程去做真正的请求， 请求完毕后会在主线程上</span>
        <span style="color: #666666; font-style: italic;">//调用Listener.onResponse方法通知请求完毕</span>
        <span style="color: #666666; font-style: italic;">//但是主线程是一个有Handler的线程，Robolectric框架让主线程不轮询消息队列</span>
        <span style="color: #666666; font-style: italic;">//必须在测试方法里主动驱动主线程轮询消息队列，针对消息进行处理</span>
        <span style="color: #666666; font-style: italic;">//否则永远不会在UI线程上通知请求完毕</span>
        requester.<span style="color: #006633;">request</span><span style="color: #009900;">&#40;</span>RuntimeEnvironment.<span style="color: #006633;">application</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//获取主线程的消息队列的调度者，通过它可以知道消息队列的情况</span>
        <span style="color: #666666; font-style: italic;">//并驱动主线程主动轮询消息队列</span>
        Scheduler scheduler <span style="color: #339933;">=</span> Robolectric.<span style="color: #006633;">getForegroundThreadScheduler</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//因为调用请求方法后 后台线程请求需要一段时间才能请求完毕，然后才会通知主线程</span>
        <span style="color: #666666; font-style: italic;">// 所以在这里进行等待，直到消息队列里存在消息</span>
        <span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>scheduler.<span style="color: #006633;">size</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #003399;">Thread</span>.<span style="color: #006633;">sleep</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">500</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #666666; font-style: italic;">//轮询消息队列，这样就会在主线程进行通知</span>
        scheduler.<span style="color: #006633;">runOneTask</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">// 校验 请求是否失败</span>
        PowerMockito.<span style="color: #006633;">verifyStatic</span><span style="color: #009900;">&#40;</span>times<span style="color: #009900;">&#40;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        SLog.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>VolleyRequester.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getSimpleName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, <span style="color: #0000ff;">"request failed"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//如果没有失败 则打印请求回来的字符串</span>
        <span style="color: #003399;">String</span> responseString <span style="color: #339933;">=</span> requester.<span style="color: #006633;">getResponseString</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"response str:<span style="color: #000099; font-weight: bold;">\n</span>"</span> <span style="color: #339933;">+</span> responseString<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

从上述代码可以看到我们可以通过获取Scheduler对象来判断消息队列中是否有消息，并调用Scheduler的runOneTask方法进行消息分发，这样就驱动了主线程进行消息轮询，执行结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-1024x318.png" alt="volley_demo" width="1024" height="318" class="aligncenter size-large wp-image-944" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-1024x318.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-300x93.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-768x239.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-200x62.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo.png 1255w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo.png)