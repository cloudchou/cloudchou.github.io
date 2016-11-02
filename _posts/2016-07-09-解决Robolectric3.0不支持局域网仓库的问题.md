---
id: 978
title: 解决Robolectric3.0不支持局域网仓库的问题
date: 2016-07-09T17:28:36+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=978
permalink: /android/post-978.html
views:
  - 348
categories:
  - Android
  - 个人总结
tags:
  - Robolectric
  - Robolectric 3.0
  - robolectric.dependency.repo.url
  - Robolectric3.0 not support local net
---
<a href="http://www.cloudchou.com/tag/robolectric" title="View all posts in Robolectric" target="_blank" class="tags">Robolectric</a>官网在介绍它的配置时，指出可以在build.gradle里配置robolectric的依赖仓库，也就是说在脚本里可以声明Robolectric相关jar包的下载地址，比如android-all-5.0.0_r2-robolectric-1.jar，利用这个特性，我们可以将下载地址设置为局域网的组件仓库，这样可以缓存这些jar包，否则如果每次都从sonatype仓库下的话会非常慢。

设置的脚本如下所示:

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
        <pre class="java" style="font-family:monospace;">android <span style="color: #009900;">&#123;</span>
  testOptions <span style="color: #009900;">&#123;</span>
    unitTests.<span style="color: #006633;">all</span> <span style="color: #009900;">&#123;</span>
      systemProperty <span style="color: #0000ff;">'robolectric.dependency.repo.url'</span>, <span style="color: #0000ff;">'https://local-mirror/repo'</span>
      systemProperty <span style="color: #0000ff;">'robolectric.dependency.repo.id'</span>, <span style="color: #0000ff;">'local'</span>
    <span style="color: #009900;">&#125;</span>
  <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

但实际上如果依赖robolectric3.0， 上面的依赖是无效的，如果我们使用./gradlew -d test命令执行测试，可以发现还是会从sonatype仓库下载，并且会非常慢。如果搜索robolectric 3.0的源码会发现根本找不到&#8221;<a href="http://www.cloudchou.com/tag/robolectric-dependency-repo-url" title="View all posts in robolectric.dependency.repo.url" target="_blank" class="tags">robolectric.dependency.repo.url</a>&#8220;字符串。 

我们需要对RobolectricGradleTestRunner进行定制才可解决这个问题，代码如下所示:

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
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> BaseRobolectricGradleTestRunner <span style="color: #000000; font-weight: bold;">extends</span> RobolectricGradleTestRunner <span style="color: #009900;">&#123;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> BaseRobolectricGradleTestRunner<span style="color: #009900;">&#40;</span>Class<span style="color: #339933;">&lt;?&gt;</span> klass<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> InitializationError <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">super</span><span style="color: #009900;">&#40;</span>klass<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//覆盖该方法 可以定制DependencyResolver</span>
    @Override
    <span style="color: #000000; font-weight: bold;">protected</span> DependencyResolver getJarResolver<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">String</span> repoUrl <span style="color: #339933;">=</span> <span style="color: #003399;">System</span>.<span style="color: #006633;">getProperty</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"robolectric.dependency.repo.url"</span>, <span style="color: #0000ff;">"."</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #003399;">String</span> repoId <span style="color: #339933;">=</span> <span style="color: #003399;">System</span>.<span style="color: #006633;">getProperty</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"robolectric.dependency.repo.id"</span>, <span style="color: #0000ff;">"."</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>StringUtils.<span style="color: #006633;">isNotEmpty</span><span style="color: #009900;">&#40;</span>repoUrl<span style="color: #009900;">&#41;</span> <span style="color: #339933;">&&</span> StringUtils.<span style="color: #006633;">isNotEmpty</span><span style="color: #009900;">&#40;</span>repoId<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #003399;">File</span> cacheDir <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">File</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">File</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">System</span>.<span style="color: #006633;">getProperty</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"java.io.tmpdir"</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span>, <span style="color: #0000ff;">"robolectric"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            cacheDir.<span style="color: #006633;">mkdir</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            DependencyResolver dependencyResolver<span style="color: #339933;">;</span>
            <span style="color: #666666; font-style: italic;">//如果设置了robolectric.dependency.repo.url属性，则利用LocalNetDependencyResolver来解决依赖</span>
            <span style="color: #666666; font-style: italic;">//这样便可以调整仓库地址</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>cacheDir.<span style="color: #006633;">exists</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                Logger.<span style="color: #006633;">info</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Dependency cache location: %s"</span>, cacheDir.<span style="color: #006633;">getAbsolutePath</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                dependencyResolver <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> CachedDependencyResolver<span style="color: #009900;">&#40;</span>
                <span style="color: #000000; font-weight: bold;">new</span> LocalNetDependencyResolver<span style="color: #009900;">&#40;</span>repoUrl, repoId<span style="color: #009900;">&#41;</span>, cacheDir, <span style="color: #cc66cc;">60</span> <span style="color: #339933;">*</span> <span style="color: #cc66cc;">60</span> <span style="color: #339933;">*</span> <span style="color: #cc66cc;">24</span> <span style="color: #339933;">*</span> <span style="color: #cc66cc;">1000</span>
                <span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
                dependencyResolver <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> LocalNetDependencyResolver<span style="color: #009900;">&#40;</span>repoUrl, repoId<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">return</span> dependencyResolver<span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000000; font-weight: bold;">super</span>.<span style="color: #006633;">getJarResolver</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">class</span> LocalNetDependencyResolver <span style="color: #000000; font-weight: bold;">implements</span> DependencyResolver <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">String</span> mRepoUrl<span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">String</span> mRepoId<span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> Project project <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Project<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
        <span style="color: #000000; font-weight: bold;">public</span> LocalNetDependencyResolver<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> repoUrl, <span style="color: #003399;">String</span> repoId<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            mRepoId <span style="color: #339933;">=</span> repoId<span style="color: #339933;">;</span>
            mRepoUrl <span style="color: #339933;">=</span> repoUrl<span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        @Override
        <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">URL</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> getLocalArtifactUrls<span style="color: #009900;">&#40;</span>DependencyJar... <span style="color: #006633;">dependencies</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            DependenciesTask dependenciesTask <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> DependenciesTask<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            configureMaven<span style="color: #009900;">&#40;</span>dependenciesTask<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            RemoteRepository sonatypeRepository <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> RemoteRepository<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            sonatypeRepository.<span style="color: #006633;">setUrl</span><span style="color: #009900;">&#40;</span>mRepoUrl<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            sonatypeRepository.<span style="color: #006633;">setId</span><span style="color: #009900;">&#40;</span>mRepoId<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            dependenciesTask.<span style="color: #006633;">addConfiguredRemoteRepository</span><span style="color: #009900;">&#40;</span>sonatypeRepository<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            dependenciesTask.<span style="color: #006633;">setProject</span><span style="color: #009900;">&#40;</span>project<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span>DependencyJar dependencyJar <span style="color: #339933;">:</span> dependencies<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                Dependency dependency <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> Dependency<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                dependency.<span style="color: #006633;">setArtifactId</span><span style="color: #009900;">&#40;</span>dependencyJar.<span style="color: #006633;">getArtifactId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                dependency.<span style="color: #006633;">setGroupId</span><span style="color: #009900;">&#40;</span>dependencyJar.<span style="color: #006633;">getGroupId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                dependency.<span style="color: #006633;">setType</span><span style="color: #009900;">&#40;</span>dependencyJar.<span style="color: #006633;">getType</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                dependency.<span style="color: #006633;">setVersion</span><span style="color: #009900;">&#40;</span>dependencyJar.<span style="color: #006633;">getVersion</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>dependencyJar.<span style="color: #006633;">getClassifier</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    dependency.<span style="color: #006633;">setClassifier</span><span style="color: #009900;">&#40;</span>dependencyJar.<span style="color: #006633;">getClassifier</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                dependenciesTask.<span style="color: #006633;">addDependency</span><span style="color: #009900;">&#40;</span>dependency<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            dependenciesTask.<span style="color: #006633;">execute</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
            @SuppressWarnings<span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"unchecked"</span><span style="color: #009900;">&#41;</span>
            Hashtable<span style="color: #339933;">&lt;</span><span style="color: #003399;">String</span>, String<span style="color: #339933;">&gt;</span> artifacts <span style="color: #339933;">=</span> project.<span style="color: #006633;">getProperties</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #003399;">URL</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> urls <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">URL</span><span style="color: #009900;">&#91;</span>dependencies.<span style="color: #006633;">length</span><span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> i <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span> i <span style="color: #339933;">&lt;</span> urls.<span style="color: #006633;">length</span><span style="color: #339933;">;</span> i<span style="color: #339933;">++</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                    urls<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> <span style="color: #003399;">Util</span>.<span style="color: #006633;">url</span><span style="color: #009900;">&#40;</span>artifacts.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>key<span style="color: #009900;">&#40;</span>dependencies<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">MalformedURLException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">RuntimeException</span><span style="color: #009900;">&#40;</span>e<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">return</span> urls<span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        @Override
        <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">URL</span> getLocalArtifactUrl<span style="color: #009900;">&#40;</span>DependencyJar dependency<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #003399;">URL</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> urls <span style="color: #339933;">=</span> getLocalArtifactUrls<span style="color: #009900;">&#40;</span>dependency<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>urls.<span style="color: #006633;">length</span> <span style="color: #339933;">&gt;</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">return</span> urls<span style="color: #009900;">&#91;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">String</span> key<span style="color: #009900;">&#40;</span>DependencyJar dependency<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #003399;">String</span> key <span style="color: #339933;">=</span> dependency.<span style="color: #006633;">getGroupId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">":"</span> <span style="color: #339933;">+</span> dependency.<span style="color: #006633;">getArtifactId</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">":"</span> 
            <span style="color: #339933;">+</span> dependency.<span style="color: #006633;">getType</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>dependency.<span style="color: #006633;">getClassifier</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                key <span style="color: #339933;">+=</span> <span style="color: #0000ff;">":"</span> <span style="color: #339933;">+</span> dependency.<span style="color: #006633;">getClassifier</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #000000; font-weight: bold;">return</span> key<span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
        <span style="color: #000000; font-weight: bold;">protected</span> <span style="color: #000066; font-weight: bold;">void</span> configureMaven<span style="color: #009900;">&#40;</span>DependenciesTask dependenciesTask<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">// maybe you want to override this method and some settings?</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
&nbsp;
    <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

可以象下面这样使用这个TestRunner:

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
        <pre class="java" style="font-family:monospace;">@RunWith<span style="color: #009900;">&#40;</span>BaseRobolectricGradleTestRunner.<span style="color: #000000; font-weight: bold;">class</span><span style="color: #009900;">&#41;</span> <span style="color: #666666; font-style: italic;">//指定使用RobolectricGradleTestRunner作为单元测试执行者</span>
<span style="color: #666666; font-style: italic;">//配置常量,执行时所使用的AndroidSdk，还可以在这里配置Application类，AndroidManifest文件的路径，Shadow类</span>
@Config<span style="color: #009900;">&#40;</span>constants <span style="color: #339933;">=</span> BuildConfig.<span style="color: #000000; font-weight: bold;">class</span>, sdk <span style="color: #339933;">=</span> <span style="color: #cc66cc;">21</span><span style="color: #009900;">&#41;</span>
@PowerMockIgnore<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#123;</span><span style="color: #0000ff;">"org.mockito.*"</span>, <span style="color: #0000ff;">"org.robolectric.*"</span>, <span style="color: #0000ff;">"android.*"</span><span style="color: #009900;">&#125;</span><span style="color: #009900;">&#41;</span> <span style="color: #666666; font-style: italic;">//使得Powermock忽略这些包的注入类</span>
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