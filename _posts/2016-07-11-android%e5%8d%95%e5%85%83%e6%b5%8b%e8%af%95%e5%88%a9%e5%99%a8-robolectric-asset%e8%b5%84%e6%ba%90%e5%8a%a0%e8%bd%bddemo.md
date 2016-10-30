---
id: 952
title: 'Android单元测试利器&#8211;Robolectric asset资源加载demo'
date: 2016-07-11T09:32:41+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=952
permalink: /android/post-952.html
views:
  - 507
categories:
  - Android
  - 个人总结
tags:
  - Android单元测试
  - Robolectric
  - Robolectric asset资源加载
---
<a href="http://www.cloudchou.com/tag/android%e5%8d%95%e5%85%83%e6%b5%8b%e8%af%95" title="View all posts in Android单元测试" target="_blank" class="tags">Android单元测试</a>系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> 

## Android asset资源加载demo

先前有提到，本地单元测试里可以配置AndroidManifest, assests等目录，然而并没有什么卵用，读取的AndroidManifest还是主模块的AndroidManifest和assets，要想使用特殊的assets或者AndroidManifest必须自己写TestRunner,本节就讲解如何加载自定义的AndroidManifest和assets资源。

首先实现一个自定义的从<a href="http://www.cloudchou.com/tag/robolectric" title="View all posts in Robolectric" target="_blank" class="tags">Robolectric</a>GradleTestRunner集成的TestRunner:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//可以修改AndroidManifest和asset的TestRunner</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> RobolectricGradleTestRunner2 <span style="color: #000000; font-weight: bold;">extends</span> RobolectricGradleTestRunner <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> RobolectricGradleTestRunner2<span style="color: #009900;">&#40;</span>Class<span style="color: #339933;">&lt;?&gt;</span> klass<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> InitializationError <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">super</span><span style="color: #009900;">&#40;</span>klass<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">protected</span> AndroidManifest getAppManifest<span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">final</span> Config config<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//使用父类的方法创建AndroidManifest对象,</span>
        <span style="color: #666666; font-style: italic;">//因为我们只修改AndroidManifest对象的AndroidManifest文件的位置</span>
        <span style="color: #666666; font-style: italic;">// 和assets文件夹的位置</span>
        AndroidManifest appManifest <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">getAppManifest</span><span style="color: #009900;">&#40;</span>config<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//只有当我们在测试脚本里设置了manifest时，自定义TestRunner才处理</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>config.<span style="color: #006633;">manifest</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span><span style="color: #0000ff;">""</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>config.<span style="color: #006633;">manifest</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//使用反射修改AndroidManifest对象的androidManifestFile字段的值，</span>
            <span style="color: #666666; font-style: italic;">//使其指向我们设置的AndroidManifest文件的位置</span>
            FileFsFile manifestFile <span style="color: #339933;">=</span> FileFsFile.<span style="color: #006633;">from</span><span style="color: #009900;">&#40;</span>config.<span style="color: #006633;">manifest</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            Class<span style="color: #339933;">&lt;?</span> <span style="color: #000000; font-weight: bold;">extends</span> AndroidManifest<span style="color: #339933;">&gt;</span> appManifestClass <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                appManifestClass <span style="color: #339933;">=</span> appManifest.<span style="color: #006633;">getClass</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #003399;">Field</span> androidManifestFileField<span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                    androidManifestFileField <span style="color: #339933;">=</span> appManifestClass.<span style="color: #006633;">getDeclaredField</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"androidManifestFile"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">NoSuchFieldException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    androidManifestFileField <span style="color: #339933;">=</span> appManifestClass.<span style="color: #006633;">getSuperclass</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getDeclaredField</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"androidManifestFile"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                androidManifestFileField.<span style="color: #006633;">setAccessible</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                androidManifestFileField.<span style="color: #006633;">set</span><span style="color: #009900;">&#40;</span>appManifest, manifestFile<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">NoSuchFieldException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">IllegalAccessException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #666666; font-style: italic;">//使用反射修改AndroidManifest对象的assetsDirectory字段的值，</span>
            <span style="color: #666666; font-style: italic;">//使其指向我们设置的assets文件夹的位置</span>
            <span style="color: #003399;">String</span> parent <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">File</span><span style="color: #009900;">&#40;</span>config.<span style="color: #006633;">manifest</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getParent</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            FileFsFile assetFile <span style="color: #339933;">=</span> FileFsFile.<span style="color: #006633;">from</span><span style="color: #009900;">&#40;</span>parent, config.<span style="color: #006633;">assetDir</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #003399;">Field</span> assetsDirectoryField <span style="color: #339933;">=</span> appManifestClass.<span style="color: #006633;">getDeclaredField</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"assetsDirectory"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                assetsDirectoryField.<span style="color: #006633;">setAccessible</span><span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                assetsDirectoryField.<span style="color: #006633;">set</span><span style="color: #009900;">&#40;</span>appManifest, assetFile<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">NoSuchFieldException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">IllegalAccessException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #000000; font-weight: bold;">return</span> appManifest<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

然后再看如何在测试脚本里设置manifest进行测试:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">//必须指定使用自定义的TestRunner才能指定AndroidManifest文件的位置进行加载</span>
@RunWith<span style="color: #009900;">&#40;</span>RobolectricGradleTestRunner2.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span>
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> ManifestConfigTest <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//指定使用test目录下的AndroidManifest.xml 这时asse</span>
    @Test
    @Config<span style="color: #009900;">&#40;</span>manifest <span style="color: #339933;">=</span> <span style="color: #0000ff;">"src/test/AndroidManifest.xml"</span><span style="color: #009900;">&#41;</span>
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> testManifestConfig<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> PackageManager.<span style="color: #003399;">NameNotFoundException</span>, <span style="color: #003399;">IOException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">String</span> packageName <span style="color: #339933;">=</span> RuntimeEnvironment.<span style="color: #006633;">application</span>.<span style="color: #006633;">getPackageName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        PackageManager packageManager <span style="color: #339933;">=</span> RuntimeEnvironment.<span style="color: #006633;">application</span>.<span style="color: #006633;">getPackageManager</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        PackageInfo packageInfo <span style="color: #339933;">=</span> packageManager.<span style="color: #006633;">getPackageInfo</span><span style="color: #009900;">&#40;</span>packageName, PackageManager.<span style="color: #006633;">GET_ACTIVITIES</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>packageInfo.<span style="color: #006633;">activities</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>packageName<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>packageInfo.<span style="color: #006633;">versionCode</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>packageInfo.<span style="color: #006633;">versionName</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//从assets目录下加载test.prop文件</span>
        <span style="color: #003399;">InputStream</span> fileInputStream <span style="color: #339933;">=</span> RuntimeEnvironment.<span style="color: #006633;">application</span>.<span style="color: #006633;">getAssets</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">open</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"test.prop"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">Properties</span> props <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Properties</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        props.<span style="color: #006633;">load</span><span style="color: #009900;">&#40;</span>fileInputStream<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">String</span> property <span style="color: #339933;">=</span> props.<span style="color: #006633;">getProperty</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"ro.product.cpu.abilist"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>property<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

代码结构如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test.png" alt="manifest_test" width="695" height="350" class="aligncenter size-full wp-image-934" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test.png 695w, http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test-300x151.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test-200x101.png 200w" sizes="(max-width: 695px) 100vw, 695px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test.png)

执行结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test_result.png" alt="manifest_test_result" width="975" height="328" class="aligncenter size-full wp-image-935" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test_result.png 975w, http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test_result-300x101.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test_result-768x258.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test_result-200x67.png 200w" sizes="(max-width: 975px) 100vw, 975px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test_result.png)