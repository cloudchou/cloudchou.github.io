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
<h2>Robolectric简介</h2>
<p>​       以前为Android写单元测试时，只能编写基于Instrumentation Test的单元测试，也就是说只能编写在手机上执行的单元测试。只有为普通的Java工程编写的单元测试才能脱离手机单独执行，但是Android平台有很多平台专有的Api，如果实现lib，基本都会选择Android的lib工程，而不会选择普通的Java库工程。这样只好编写基于Instrumentation Test的单元测试。</p>
<p>​     这种单元测试在执行时需要连接手机，测试时间长，还不能和持续集成服务相结合，因为持续集成服务通常在服务器上执行单元测试，不方便连接手机，或者创建模拟器。</p>
<p>     此外，我们知道做单元测试，经常需要借助mock测试，mock测试就是在测试过程中，对于某些不容易构造或者不容易获取的对象，用一个虚拟的对象来创建以便测试的测试方法。常用的mock框架有mockito,easymock(mockito比easymock更好用，接口更简洁),而这两种框架只支持对象级的mock,也就是说只能构建虚拟的对象，不能支持静态方法,private方法的mock, 而我们写的代码里，不可避免的会有静态工具类，很多系统类也是静态工具类。于是我们很需要象Powermock这样的mock框架，它能支持静态方法的mock。但是Powermock无法支持Android平台，因为实现静态方法的mock的原理，是替换系统的ClassLoader，并将加载的类换成mock的类，而在Android平台出于安全考虑，不允许替换系统的ClassLoader，否则会抛安全异常。所以如果使用Instrumentation test，就不能使用Powermock。</p>
<p>​      后来Android支持了在PC上执行的单元测试，可以使用mockito,powermock等框架，但是几乎所有Android的API都需要自己去做mock，非常麻烦，比如，Context都需要自己去创建mock对象。如果有一个框架能帮我们实现Android Api的mock，我们只需要在测试时mock几个比较特殊的对象或者类，那该多好。</p>
<p>​     Robolectric就是这样一个强大的框架，有了它，编写在PC上执行的本地单元测试就方便多了。Robolectric将Android的Api在PC上做了重新实现，它有以下特点:</p>
<ol><li>
<p>有mock的context,不需要自己在创建mock context，只需使用即可</p>
</li>
<li>
<p>支持SharedPreference,所以在应用代码里写的SharedPreference相关代码在PC上一样可以执行，不用在测试代码里专门添加逻辑来支持SharedPreference</p>
</li>
<li>
<p>支持Sqlite数据库, 所以不用应用代码里操作数据库的逻辑做任何特殊支持</p>
</li>
<li>
<p>支持Environment，所以在应用代码里用Envrionment获取Sd卡路径，也能得到正确的Sd卡路径，在PC上执行时实际获得的Sd卡路径是一个PC上的文件夹路径，也可以在里面创建文件</p>
</li>
<li>
<p>它还支持资源文件的加载，所以在代码中编写的显示界面的逻辑都可以在PC上运行，这就使得在PC上能执行在真实设备上执行的大多数逻辑。我们还可以针对Sdk的API做自己的特殊实现，这样可以模拟错误条件，或者真实场景里的传感器行为</p>
</li>
<li>
<p>它不需要Mockito,Powermock等框架的支持，当然，我们也可以选择和Powermock相结合</p>
<p>​有了这么强大的本地单元测试框架，我们可以和持续集成服务相结合，更新代码时，持续集成服务在服务器上自动执行本地单元测试，确保更新的代码不会引入新Bug，或者使得旧Bug又出现。   <br/></p>
</li>
</ol>
<h2>Robolectric的不足</h2>
<ol><li>
<p>在代码包里的资源文件(比如test.prop)不能直接用getResourceAsStream加载，必须在gradle脚本里添加处理，在执行测试用例前将非代码资源拷贝到编译好的class文件所在目录</p>
</li>
<li>
<p>本地单元测试里可以配置AndroidManifest, assests等目录，然而并没有什么卵用，读取的AndroidManifest还是主模块的AndroidManifest和assets，要想使用特殊的assets或者AndroidManifest必须自己写TestRunner,我们写TestRunner时，可以从RobolectricGradleTestRunner继承，然后覆盖getAppManifest方法，构建自己想要的特殊的AndroidManifest对象来实现对AndroidManifest,assets,res资源的控制</p>
</li>
<li>
<p>Robolectric 3.0不能直接针对非Android Sdk的类做Shadow，必须使用Powermock或者mockito来处理这种情况，Powermock支持partial mock，也就是说mock某个类时，不需要为这个类的所有函数做mock处理，只需针对需要改变行为的函数进行mock就可以了，但是不能对Android sdk的类做mock，因为Robolectric框架已经将这些类都替换成了Shadow类</p>
<p>Robolectric 3.1 已支持针对非AndroidSdk的类做Shadow，但是不支持Powermock</p>
<p>总的来说如果为每个要hack的类都创建Shadow类，然后为每个要hack的函数都创建shadow函数还是非常麻烦的事情，相对来说，使用PowerMock需要添加的代码就少很多，所以建议使用Robolectric 3.0+power mock+mockito来做单元测试，就已经足够。</p>
<p>接下来我们看使用Robolectric做单元测试的一些demo，所有代码都可以在Github上下载:</p>
<p><a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> </p>
</li>
</ol>
<h2>环境测试Demo</h2>
<p>   我们首先来看使用Roblectric测试SharedPreference和Environment的demo。</p>
<p>​    首先需要在build.gradle里添加对Robolectric的依赖:</p>
<pre  lang="groovy" line="1">
dependencies {
    compile fileTree(dir: "libs", include: ["*.jar"])
    testCompile "junit:junit:4.12"
    testCompile "org.powermock:powermock-module-junit4:1.6.4"
    testCompile "org.powermock:powermock-module-junit4-rule:1.6.4"
    testCompile "org.powermock:powermock-api-mockito:1.6.4"
    testCompile "org.powermock:powermock-classloading-xstream:1.6.4"
    testCompile "org.robolectric:robolectric:3.0"
    compile "com.android.support:appcompat-v7:24.0.0"
}
```
<p>​    然后建立单元测试类EvnTest, 必须指定使用RobolectricGradleTestRunner作为单元测试执行者，然后配置constants常量，因为我们使用了Powermock，powermock的许多注入类必须被忽略，代码如下所示：</p>
```java
/**
 * Created by Cloud on 2016/6/22.
 */
@RunWith(RobolectricGradleTestRunner.class) //指定使用RobolectricGradleTestRunner作为单元测试执行者
//配置常量,执行时所使用的AndroidSdk，还可以在这里配置Application类，AndroidManifest文件的路径，Shadow类
@Config(constants = BuildConfig.class, sdk = 21)
//使得Powermock忽略这些包的注入类
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"}) 
public class EvnTest {

    @Test
    public void testEvn() {
        String absolutePath = Environment.getExternalStorageDirectory().getAbsolutePath();
        Assert.assertNotNull(absolutePath);
        System.out.println("absolute path: " + absolutePath);
        Context application = RuntimeEnvironment.application;
        SharedPreferences sSp = PreferenceManager.getDefaultSharedPreferences(application);
        SharedPreferences.Editor edit = sSp.edit();
        edit.putBoolean("halo", true);
        edit.commit();
        boolean halo = sSp.getBoolean("halo", false);
        Assert.assertTrue(halo);
    }

}
```
<p>执行结果如下所示:</p>
<p><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/EvnTest-1024x152.png" alt="EvnTest" width="1024" height="152" class="aligncenter size-large wp-image-933" /></p>
<p>可以看出来Roblectric对context, SharedPreference,Environment的支持都是非常好的。</p>
<p>Android单元测试系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> </p>
