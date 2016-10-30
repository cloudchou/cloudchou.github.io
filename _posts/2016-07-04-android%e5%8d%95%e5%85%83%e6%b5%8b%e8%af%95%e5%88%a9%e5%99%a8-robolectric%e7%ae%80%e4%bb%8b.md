---
id: 925
title: 'Android单元测试利器&#8211;Robolectric简介'
date: 2016-07-04T09:03:03+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=925
permalink: /android/post-925.html
views:
  - 593
categories:
  - Android
  - 个人总结
tags:
  - Android单元测试
  - Robolectric
  - Robolectric不足
  - Robolectric优点
---
## <a href="http://www.cloudchou.com/tag/robolectric" title="View all posts in Robolectric" target="_blank" class="tags">Robolectric</a>简介

​ 以前为Android写单元测试时，只能编写基于Instrumentation Test的单元测试，也就是说只能编写在手机上执行的单元测试。只有为普通的Java工程编写的单元测试才能脱离手机单独执行，但是Android平台有很多平台专有的Api，如果实现lib，基本都会选择Android的lib工程，而不会选择普通的Java库工程。这样只好编写基于Instrumentation Test的单元测试。

​ 这种单元测试在执行时需要连接手机，测试时间长，还不能和持续集成服务相结合，因为持续集成服务通常在服务器上执行单元测试，不方便连接手机，或者创建模拟器。

此外，我们知道做单元测试，经常需要借助mock测试，mock测试就是在测试过程中，对于某些不容易构造或者不容易获取的对象，用一个虚拟的对象来创建以便测试的测试方法。常用的mock框架有mockito,easymock(mockito比easymock更好用，接口更简洁),而这两种框架只支持对象级的mock,也就是说只能构建虚拟的对象，不能支持静态方法,private方法的mock, 而我们写的代码里，不可避免的会有静态工具类，很多系统类也是静态工具类。于是我们很需要象Powermock这样的mock框架，它能支持静态方法的mock。但是Powermock无法支持Android平台，因为实现静态方法的mock的原理，是替换系统的ClassLoader，并将加载的类换成mock的类，而在Android平台出于安全考虑，不允许替换系统的ClassLoader，否则会抛安全异常。所以如果使用Instrumentation test，就不能使用Powermock。

​ 后来Android支持了在PC上执行的单元测试，可以使用mockito,powermock等框架，但是几乎所有Android的API都需要自己去做mock，非常麻烦，比如，Context都需要自己去创建mock对象。如果有一个框架能帮我们实现Android Api的mock，我们只需要在测试时mock几个比较特殊的对象或者类，那该多好。

​ Robolectric就是这样一个强大的框架，有了它，编写在PC上执行的本地单元测试就方便多了。Robolectric将Android的Api在PC上做了重新实现，它有以下特点:

  1. 有mock的context,不需要自己在创建mock context，只需使用即可

  2. 支持SharedPreference,所以在应用代码里写的SharedPreference相关代码在PC上一样可以执行，不用在测试代码里专门添加逻辑来支持SharedPreference

  3. 支持Sqlite数据库, 所以不用应用代码里操作数据库的逻辑做任何特殊支持

  4. 支持Environment，所以在应用代码里用Envrionment获取Sd卡路径，也能得到正确的Sd卡路径，在PC上执行时实际获得的Sd卡路径是一个PC上的文件夹路径，也可以在里面创建文件

  5. 它还支持资源文件的加载，所以在代码中编写的显示界面的逻辑都可以在PC上运行，这就使得在PC上能执行在真实设备上执行的大多数逻辑。我们还可以针对Sdk的API做自己的特殊实现，这样可以模拟错误条件，或者真实场景里的传感器行为

  6. 它不需要Mockito,Powermock等框架的支持，当然，我们也可以选择和Powermock相结合
    
    ​有了这么强大的本地单元测试框架，我们可以和持续集成服务相结合，更新代码时，持续集成服务在服务器上自动执行本地单元测试，确保更新的代码不会引入新Bug，或者使得旧Bug又出现。 

## Robolectric的不足

  1. 在代码包里的资源文件(比如test.prop)不能直接用getResourceAsStream加载，必须在gradle脚本里添加处理，在执行测试用例前将非代码资源拷贝到编译好的class文件所在目录

  2. 本地单元测试里可以配置AndroidManifest, assests等目录，然而并没有什么卵用，读取的AndroidManifest还是主模块的AndroidManifest和assets，要想使用特殊的assets或者AndroidManifest必须自己写TestRunner,我们写TestRunner时，可以从RobolectricGradleTestRunner继承，然后覆盖getAppManifest方法，构建自己想要的特殊的AndroidManifest对象来实现对AndroidManifest,assets,res资源的控制

  3. Robolectric 3.0不能直接针对非Android Sdk的类做Shadow，必须使用Powermock或者mockito来处理这种情况，Powermock支持partial mock，也就是说mock某个类时，不需要为这个类的所有函数做mock处理，只需针对需要改变行为的函数进行mock就可以了，但是不能对Android sdk的类做mock，因为Robolectric框架已经将这些类都替换成了Shadow类
    
    Robolectric 3.1 已支持针对非AndroidSdk的类做Shadow，但是不支持Powermock
    
    总的来说如果为每个要hack的类都创建Shadow类，然后为每个要hack的函数都创建shadow函数还是非常麻烦的事情，相对来说，使用PowerMock需要添加的代码就少很多，所以建议使用Robolectric 3.0+power mock+mockito来做单元测试，就已经足够。
    
    接下来我们看使用Robolectric做单元测试的一些demo，所有代码都可以在Github上下载:
    
    <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> 

## 环境测试Demo

我们首先来看使用Roblectric测试SharedPreference和Environment的demo。

​ 首先需要在build.gradle里添加对Robolectric的依赖:

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
        <pre class="groovy" style="font-family:monospace;">dependencies <span style="color: #66cc66;">&#123;</span>
    compile fileTree<span style="color: #66cc66;">&#40;</span>dir: <span style="color: #ff0000;">"libs"</span>, include: <span style="color: #66cc66;">&#91;</span><span style="color: #ff0000;">"*.jar"</span><span style="color: #66cc66;">&#93;</span><span style="color: #66cc66;">&#41;</span>
    testCompile <span style="color: #ff0000;">"junit:junit:4.12"</span>
    testCompile <span style="color: #ff0000;">"org.powermock:powermock-module-junit4:1.6.4"</span>
    testCompile <span style="color: #ff0000;">"org.powermock:powermock-module-junit4-rule:1.6.4"</span>
    testCompile <span style="color: #ff0000;">"org.powermock:powermock-api-mockito:1.6.4"</span>
    testCompile <span style="color: #ff0000;">"org.powermock:powermock-classloading-xstream:1.6.4"</span>
    testCompile <span style="color: #ff0000;">"org.robolectric:robolectric:3.0"</span>
    compile <span style="color: #ff0000;">"com.android.support:appcompat-v7:24.0.0"</span>
<span style="color: #66cc66;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

​ 然后建立单元测试类EvnTest, 必须指定使用RobolectricGradleTestRunner作为单元测试执行者，然后配置constants常量，因为我们使用了Powermock，powermock的许多注入类必须被忽略，代码如下所示：

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
        <pre class="java" style="font-family:monospace;"><span style="color: #008000; font-style: italic; font-weight: bold;">/**
 * Created by Cloud on 2016/6/22.
 */</span>
@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span> <span style="color: #666666; font-style: italic;">//指定使用RobolectricGradleTestRunner作为单元测试执行者</span>
<span style="color: #666666; font-style: italic;">//配置常量,执行时所使用的AndroidSdk，还可以在这里配置Application类，AndroidManifest文件的路径，Shadow类</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
<span style="color: #666666; font-style: italic;">//使得Powermock忽略这些包的注入类</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span> 
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> EvnTest <span style="color: #009900;">&#123;</span>
&nbsp;
    @Test
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testEvn<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">String</span> absolutePath <span style="color: #339933;">=</span> <span style="color: #003399;">Environment</span>.<span style="color: #006633;">getExternalStorageDirectory</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getAbsolutePath</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">Assert</span>.<span style="color: #006633;">assertNotNull</span><span style="color: #009900;">&#40;</span>absolutePath<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"absolute path: "</span> <span style="color: #339933;">+</span> absolutePath<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">Context</span> application <span style="color: #339933;">=</span> RuntimeEnvironment.<span style="color: #006633;">application</span><span style="color: #339933;">;</span>
        SharedPreferences sSp <span style="color: #339933;">=</span> PreferenceManager.<span style="color: #006633;">getDefaultSharedPreferences</span><span style="color: #009900;">&#40;</span>application<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        SharedPreferences.<span style="color: #006633;">Editor</span> edit <span style="color: #339933;">=</span> sSp.<span style="color: #006633;">edit</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        edit.<span style="color: #006633;">putBoolean</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"halo"</span>, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        edit.<span style="color: #006633;">commit</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000066; font-weight: bold;">boolean</span> halo <span style="color: #339933;">=</span> sSp.<span style="color: #006633;">getBoolean</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"halo"</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">Assert</span>.<span style="color: #006633;">assertTrue</span><span style="color: #009900;">&#40;</span>halo<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

执行结果如下所示:

<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/EvnTest-1024x152.png" alt="EvnTest" width="1024" height="152" class="aligncenter size-large wp-image-933" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/EvnTest-1024x152.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/EvnTest-300x45.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/EvnTest-768x114.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/EvnTest-200x30.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/EvnTest.png 1306w" sizes="(max-width: 1024px) 100vw, 1024px" />

可以看出来Roblectric对context, SharedPreference,Environment的支持都是非常好的。

<a href="http://www.cloudchou.com/tag/android%e5%8d%95%e5%85%83%e6%b5%8b%e8%af%95" title="View all posts in Android单元测试" target="_blank" class="tags">Android单元测试</a>系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a>