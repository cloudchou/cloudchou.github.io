---
id: 957
title: 'Android单元测试利器&#8211;Robolectric 结合powermock测试'
date: 2016-07-14T08:34:14+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=957
permalink: /android/post-957.html
views:
  - 594
categories:
  - Android
  - 个人总结
tags:
  - Android单元测试
  - Android单元测试 Robolectric
  - Roblectric+powermock
  - Robolectric+powermock 实例
---
<a href="http://www.cloudchou.com/tag/android%e5%8d%95%e5%85%83%e6%b5%8b%e8%af%95" title="View all posts in Android单元测试" target="_blank" class="tags">Android单元测试</a>系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> 

## PowerMock测试Demo

前面的章节中有提到过Robolectric 3.0不能直接针对非Android Sdk的类做Shadow，必须使用PowerMock或者mockito处理，PowerMock支持静态函数的mock，还支持partialmock，也就是说mock某个类时，不需要为这个类的所有函数做mock处理，只需针对需要改变行为的函数进行mock就可以了，其它函数执行时还是mock之前的逻辑。这点非常有用，否则每次使用powermock或者mockito时需要针对某个类的所有函数都要处理，如果函数比较多，那会相当麻烦。

Robolectric 3.1已支持针对非AndroidSdk的类做Shadow，但是不支持Powermock。因为创建Shadow类的方式，需要写的代码比PowerMock方式多很多，所以我们建议使用PowerMock+Robolectric3.0+mockito做单元测试。

接下来我们看如何使用PowerMock做Partial Mock。

首先看一下要被mock的类的代码:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//被测试类只是简单返回一些字符串</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> HelloUtils2 <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> test1<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #0000ff;">"Hello Utils2 test1"</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #003399;">String</span> test2<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #0000ff;">"Hello Utils2 test2"</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

测试代码如下所示:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//必须写如下代码 让PowerMock 忽略Robolectric的所有注入</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类</span>
@PrepareForTest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> PartialPowerMockTest <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试</span>
    <span style="color: #666666; font-style: italic;">//但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试</span>
    @Rule
    <span style="color: #000000; font-weight: bold;">public</span> PowerMockRule rule <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> PowerMockRule<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须在所有测试用例执行之前</span>
    <span style="color: #666666; font-style: italic;">//使用PowerMockito.mockStatic开启对HelloUtils2的静态mock</span>
    @Before
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> setup<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        PowerMockito.<span style="color: #006633;">mockStatic</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testPartialmock<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">Exception</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//调用spy表明是partial mock</span>
        PowerMockito.<span style="color: #006633;">spy</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//当执行HelloUtils2.test1函数时，让它返回it's partial mocked</span>
        PowerMockito.<span style="color: #006633;">doReturn</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"it's partial mocked"</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">when</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span>, <span style="color: #0000ff;">"test1"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//test1 函数的行为已改变 会返回 it's partial mocked</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #006633;">test1</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #006633;">test2</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

执行代结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/partial_powermock.png" alt="partial_powermock" width="994" height="216" class="aligncenter size-full wp-image-936" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/partial_powermock.png 994w, http://www.cloudchou.com/wp-content/uploads/2016/07/partial_powermock-300x65.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/partial_powermock-768x167.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/partial_powermock-200x43.png 200w" sizes="(max-width: 994px) 100vw, 994px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/partial_powermock.png)

PowerMock还可以用于做校验，比如测试某个函数时，校验该函数调用的其它函数是否执行了指定的次数，或者校验这些函数是否执行超时。

Powermock进行校验时，和mockito做校验有比较大的区别,需要先执行测试的函数的逻辑, Powermock会收集执行时的数据，比如函数被调用多次，函数执行时间等信息，然后再对Powermock收集到的数据进行校验 , verifyStatic函数的参数是一个校验模型。times(3)表示执行了3次， 但是此时还不知道对哪个函数的执行次数校验3次，必须在后面调用 要校验的 函数， 执行后， Powermock就知道要校验谁了，Powermock此时会执行真正的校验逻辑。

示例代码如下所示:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//必须写如下代码 让PowerMock 忽略Robolectric的所有注入</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类</span>
@PrepareForTest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span>, SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> PowerMockVerifyTest <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试</span>
    <span style="color: #666666; font-style: italic;">//但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试</span>
    @Rule
    <span style="color: #000000; font-weight: bold;">public</span> PowerMockRule rule <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> PowerMockRule<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须在所有测试用例执行之前</span>
    <span style="color: #666666; font-style: italic;">//使用PowerMockito.mockStatic开启对HelloUtils2的静态mock</span>
    @Before
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> setup<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        PowerMockito.<span style="color: #006633;">mockStatic</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        PowerMockito.<span style="color: #006633;">mockStatic</span><span style="color: #009900;">&#40;</span>SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
     @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testVerify<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">Exception</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//先执行逻辑, Powermock会收集执行时的数据，比如函数被调用多次，函数执行时间等信息，</span>
        HelloUtils2.<span style="color: #006633;">test3</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloUtils2.<span style="color: #006633;">test3</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloUtils2.<span style="color: #006633;">test3</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//然后再对Powermock收集到的数据进行校验 , verifyStatic函数的参数是一个校验模型</span>
        <span style="color: #666666; font-style: italic;">// times(3)表示执行了3次， 但是此时还不知道对哪个函数的执行次数校验3次</span>
        <span style="color: #666666; font-style: italic;">// 必须在后面调用 要校验的 函数， 执行后， Powermock就知道要校验谁了，</span>
        <span style="color: #666666; font-style: italic;">//Powermock此时会执行真正的校验逻辑， 看test3函数是否真的执行了3次</span>
        PowerMockito.<span style="color: #006633;">verifyStatic</span><span style="color: #009900;">&#40;</span>times<span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">3</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloUtils2.<span style="color: #006633;">test3</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testVerifyFailed<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">Exception</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//先执行逻辑, Powermock会收集执行时的数据，比如函数被调用多次，函数执行时间等信息，</span>
        HelloUtils2.<span style="color: #006633;">test3</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloUtils2.<span style="color: #006633;">test3</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #666666; font-style: italic;">//        HelloUtils2.test3();</span>
        <span style="color: #666666; font-style: italic;">//然后再对Powermock收集到的数据进行校验 , verifyStatic函数的参数是一个校验模型</span>
        <span style="color: #666666; font-style: italic;">// times(3)表示执行了3次， 但是此时还不知道对哪个函数的执行次数校验3次</span>
        <span style="color: #666666; font-style: italic;">// 必须在后面调用 要校验的 函数， 执行后， Powermock就知道要校验谁了，</span>
        <span style="color: #666666; font-style: italic;">//Powermock此时会执行真正的校验逻辑， 看test3函数是否真的执行了3次</span>
        PowerMockito.<span style="color: #006633;">verifyStatic</span><span style="color: #009900;">&#40;</span>times<span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">3</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloUtils2.<span style="color: #006633;">test3</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

执行testVerifyFailed的结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified-1024x306.png" alt="test_verified" width="1024" height="306" class="aligncenter size-large wp-image-942" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified-1024x306.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified-300x90.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified-768x229.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified-200x60.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified.png 1148w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified.png)

我们不仅可以对函数调用次数进行校验， 还可以对函数的参数做限制，也就是说校验指定参数的函数校验调用次数，示例代码如下所示:

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
        <pre class="java" style="font-family:monospace;">@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//必须写如下代码 让PowerMock 忽略Robolectric的所有注入</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类</span>
@PrepareForTest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span>, SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> PowerMockVerifyTest <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">// ....   </span>
     @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testVerifyStringParam<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">Exception</span> <span style="color: #009900;">&#123;</span>
        HelloUtils2.<span style="color: #006633;">testStringParam</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"test"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">// 我们如果将下面对testStringParam函数调用的参数设置为其它值，则该测试用例会执行失败</span>
        HelloUtils2.<span style="color: #006633;">testStringParam</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"test"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        PowerMockito.<span style="color: #006633;">verifyStatic</span><span style="color: #009900;">&#40;</span>times<span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">2</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloUtils2.<span style="color: #006633;">testStringParam</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"test"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">// ... </span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

有了这个校验机制， 我们也就能针对Android平台的很多业务场景进行校验了，因为我们通常会在代码里打印Log，如果遇到异常场景，我们会打error日志，我们只需要校验是否打印了error日志就可以知道我们的业务逻辑是否符合预期。 

但是我们不能直接针对Log进行校验，Robolectric框架对Android sdk的类都做了替换，都设置了Shadow类，比如Log类对应的Shadow类是ShadowLog。所以我们需要对Log进行一层封装，不过在我们的业务逻辑里通常也会针对Log做一层封装，在我们的示例代码里使用了SLog对Log类进行了封装。

先看一下被测试的类的业务逻辑:

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
        <pre class="java" style="font-family:monospace;"> <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> HelloUtils2 <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> TAG <span style="color: #339933;">=</span> HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getSimpleName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> testLog<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        SLog.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Hello world"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
<span style="color: #009900;">&#125;</span> </pre>
      </td>
    </tr>
  </table>
</div>

我们在测试代码里，只需校验调用了SLog，传了指定的参数即可，测试代码如下所示:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;">@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//必须写如下代码 让PowerMock 忽略Robolectric的所有注入</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类</span>
@PrepareForTest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span>, SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> PowerMockVerifyTest <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试</span>
    <span style="color: #666666; font-style: italic;">//但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试</span>
    @Rule
    <span style="color: #000000; font-weight: bold;">public</span> PowerMockRule rule <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> PowerMockRule<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//因为我们是针对类做静态函数的mock，所以必须在所有测试用例执行之前</span>
    <span style="color: #666666; font-style: italic;">//使用PowerMockito.mockStatic开启对HelloUtils2的静态mock</span>
    <span style="color: #666666; font-style: italic;">//因为我们还要对SLog测试，所以还需针对SLog进行static mock</span>
    @Before
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> setup<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        PowerMockito.<span style="color: #006633;">mockStatic</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        PowerMockito.<span style="color: #006633;">mockStatic</span><span style="color: #009900;">&#40;</span>SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testVerifyLog<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">Exception</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//针对HelloUtils2类和SLog类做partial mock</span>
        PowerMockito.<span style="color: #006633;">spy</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        PowerMockito.<span style="color: #006633;">spy</span><span style="color: #009900;">&#40;</span>SLog.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        HelloUtils2.<span style="color: #006633;">testLog</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
      <span style="color: #666666; font-style: italic;">//因为testLog函数里调用了SLog, 而我们接下来校验时,不允许对SLog调用，所以校验会显示错误</span>
      <span style="color: #666666; font-style: italic;">//使用这种方式能很方便地校验业务逻辑</span>
        PowerMockito.<span style="color: #006633;">verifyStatic</span><span style="color: #009900;">&#40;</span>times<span style="color: #009900;">&#40;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        SLog.<span style="color: #006633;">e</span><span style="color: #009900;">&#40;</span>HelloUtils2.<span style="color: #000000; font-weight: bold;">class</span>.<span style="color: #006633;">getSimpleName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>, <span style="color: #0000ff;">"Hello world"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

执行结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log-1024x316.png" alt="test_verify_log" width="1024" height="316" class="aligncenter size-large wp-image-943" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log-1024x316.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log-300x93.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log-768x237.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log-200x62.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log.png 1083w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log.png)