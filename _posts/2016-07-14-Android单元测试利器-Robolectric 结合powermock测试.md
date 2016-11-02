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
<p>Android单元测试系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> </p>
<h2>PowerMock测试Demo</h2>
<p>前面的章节中有提到过Robolectric 3.0不能直接针对非Android Sdk的类做Shadow，必须使用PowerMock或者mockito处理，PowerMock支持静态函数的mock，还支持partialmock，也就是说mock某个类时，不需要为这个类的所有函数做mock处理，只需针对需要改变行为的函数进行mock就可以了，其它函数执行时还是mock之前的逻辑。这点非常有用，否则每次使用powermock或者mockito时需要针对某个类的所有函数都要处理，如果函数比较多，那会相当麻烦。</p>
<p>Robolectric 3.1已支持针对非AndroidSdk的类做Shadow，但是不支持Powermock。因为创建Shadow类的方式，需要写的代码比PowerMock方式多很多，所以我们建议使用PowerMock+Robolectric3.0+mockito做单元测试。</p>
<p>接下来我们看如何使用PowerMock做Partial Mock。</p>
<p>首先看一下要被mock的类的代码:</p>
```java
//被测试类只是简单返回一些字符串
public class HelloUtils2 {
    public static String test1() {
        return "Hello Utils2 test1";
    }

    public static String test2() {
        return "Hello Utils2 test2";
    }

}
```
<p>测试代码如下所示:</p>
```java
@RunWith(RobolectricGradleTestRunner.class)
@Config(constants = BuildConfig.class, sdk = 21)
//必须写如下代码 让PowerMock 忽略Robolectric的所有注入
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"})
//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类
@PrepareForTest({HelloUtils2.class})
public class PartialPowerMockTest {

    //不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试
    //但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试
    @Rule
    public PowerMockRule rule = new PowerMockRule();

    //因为我们是针对类做静态函数的mock，所以必须在所有测试用例执行之前
    //使用PowerMockito.mockStatic开启对HelloUtils2的静态mock
    @Before
    public void setup() {
        PowerMockito.mockStatic(HelloUtils2.class);
    }

    @Test
    public void testPartialmock() throws Exception {
        //调用spy表明是partial mock
        PowerMockito.spy(HelloUtils2.class);
        //当执行HelloUtils2.test1函数时，让它返回it's partial mocked
        PowerMockito.doReturn("it's partial mocked").when(HelloUtils2.class, "test1");
        //test1 函数的行为已改变 会返回 it's partial mocked
        System.out.println(HelloUtils2.test1());
        System.out.println(HelloUtils2.test2());
    }

}
```
<p>执行代结果如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/partial_powermock.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/partial_powermock.png" alt="partial_powermock" width="994" height="216" class="aligncenter size-full wp-image-936" /></a></p>
<p>PowerMock还可以用于做校验，比如测试某个函数时，校验该函数调用的其它函数是否执行了指定的次数，或者校验这些函数是否执行超时。</p>
<p>Powermock进行校验时，和mockito做校验有比较大的区别,需要先执行测试的函数的逻辑, Powermock会收集执行时的数据，比如函数被调用多次，函数执行时间等信息，然后再对Powermock收集到的数据进行校验 , verifyStatic函数的参数是一个校验模型。times(3)表示执行了3次， 但是此时还不知道对哪个函数的执行次数校验3次，必须在后面调用 要校验的 函数， 执行后， Powermock就知道要校验谁了，Powermock此时会执行真正的校验逻辑。</p>
<p>示例代码如下所示:</p>
```java
@RunWith(RobolectricGradleTestRunner.class)
@Config(constants = BuildConfig.class, sdk = 21)
//必须写如下代码 让PowerMock 忽略Robolectric的所有注入
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"})
//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类
@PrepareForTest({HelloUtils2.class, SLog.class})
public class PowerMockVerifyTest {

    //不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试
    //但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试
    @Rule
    public PowerMockRule rule = new PowerMockRule();

    //因为我们是针对类做静态函数的mock，所以必须在所有测试用例执行之前
    //使用PowerMockito.mockStatic开启对HelloUtils2的静态mock
    @Before
    public void setup() {
        PowerMockito.mockStatic(HelloUtils2.class);
        PowerMockito.mockStatic(SLog.class);
    }
  
     @Test
    public void testVerify() throws Exception {
        //先执行逻辑, Powermock会收集执行时的数据，比如函数被调用多次，函数执行时间等信息，
        HelloUtils2.test3();
        HelloUtils2.test3();
        HelloUtils2.test3();
        //然后再对Powermock收集到的数据进行校验 , verifyStatic函数的参数是一个校验模型
        // times(3)表示执行了3次， 但是此时还不知道对哪个函数的执行次数校验3次
        // 必须在后面调用 要校验的 函数， 执行后， Powermock就知道要校验谁了，
        //Powermock此时会执行真正的校验逻辑， 看test3函数是否真的执行了3次
        PowerMockito.verifyStatic(times(3));
        HelloUtils2.test3();
    }
  
    @Test
    public void testVerifyFailed() throws Exception {
        //先执行逻辑, Powermock会收集执行时的数据，比如函数被调用多次，函数执行时间等信息，
        HelloUtils2.test3();
        HelloUtils2.test3();
//        HelloUtils2.test3();
        //然后再对Powermock收集到的数据进行校验 , verifyStatic函数的参数是一个校验模型
        // times(3)表示执行了3次， 但是此时还不知道对哪个函数的执行次数校验3次
        // 必须在后面调用 要校验的 函数， 执行后， Powermock就知道要校验谁了，
        //Powermock此时会执行真正的校验逻辑， 看test3函数是否真的执行了3次
        PowerMockito.verifyStatic(times(3));
        HelloUtils2.test3();
    }
    //...
}  
```
<p>执行testVerifyFailed的结果如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/test_verified-1024x306.png" alt="test_verified" width="1024" height="306" class="aligncenter size-large wp-image-942" /></a></p>
<p>我们不仅可以对函数调用次数进行校验， 还可以对函数的参数做限制，也就是说校验指定参数的函数校验调用次数，示例代码如下所示:</p>
```java
@RunWith(RobolectricGradleTestRunner.class)
@Config(constants = BuildConfig.class, sdk = 21)
//必须写如下代码 让PowerMock 忽略Robolectric的所有注入
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"})
//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类
@PrepareForTest({HelloUtils2.class, SLog.class})
public class PowerMockVerifyTest {
    // ....   
     @Test
    public void testVerifyStringParam() throws Exception {
        HelloUtils2.testStringParam("test");
        // 我们如果将下面对testStringParam函数调用的参数设置为其它值，则该测试用例会执行失败
        HelloUtils2.testStringParam("test");
        PowerMockito.verifyStatic(times(2));
        HelloUtils2.testStringParam("test");
    }
    // ... 
}  
```
<p>有了这个校验机制， 我们也就能针对Android平台的很多业务场景进行校验了，因为我们通常会在代码里打印Log，如果遇到异常场景，我们会打error日志，我们只需要校验是否打印了error日志就可以知道我们的业务逻辑是否符合预期。 </p>
<p>但是我们不能直接针对Log进行校验，Robolectric框架对Android sdk的类都做了替换，都设置了Shadow类，比如Log类对应的Shadow类是ShadowLog。所以我们需要对Log进行一层封装，不过在我们的业务逻辑里通常也会针对Log做一层封装，在我们的示例代码里使用了SLog对Log类进行了封装。</p>
<p>先看一下被测试的类的业务逻辑:</p>
```java
 public class HelloUtils2 {
    private static final String TAG = HelloUtils2.class.getSimpleName();
    //... 
    public static void testLog() {
        SLog.e(TAG, "Hello world");
    }
    //...
} 
```
<p>我们在测试代码里，只需校验调用了SLog，传了指定的参数即可，测试代码如下所示:</p>
```java
@RunWith(RobolectricGradleTestRunner.class)
@Config(constants = BuildConfig.class, sdk = 21)
//必须写如下代码 让PowerMock 忽略Robolectric的所有注入
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"})
//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类
@PrepareForTest({HelloUtils2.class, SLog.class})
public class PowerMockVerifyTest {

    //不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试
    //但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试
    @Rule
    public PowerMockRule rule = new PowerMockRule();

    //因为我们是针对类做静态函数的mock，所以必须在所有测试用例执行之前
    //使用PowerMockito.mockStatic开启对HelloUtils2的静态mock
    //因为我们还要对SLog测试，所以还需针对SLog进行static mock
    @Before
    public void setup() {
        PowerMockito.mockStatic(HelloUtils2.class);
        PowerMockito.mockStatic(SLog.class);
    }
    //...
    @Test
    public void testVerifyLog() throws Exception {
       //针对HelloUtils2类和SLog类做partial mock
        PowerMockito.spy(HelloUtils2.class);
        PowerMockito.spy(SLog.class);
        HelloUtils2.testLog();
      //因为testLog函数里调用了SLog, 而我们接下来校验时,不允许对SLog调用，所以校验会显示错误
      //使用这种方式能很方便地校验业务逻辑
        PowerMockito.verifyStatic(times(0));
        SLog.e(HelloUtils2.class.getSimpleName(), "Hello world");
    }

}
```
<p>执行结果如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/test_verify_log-1024x316.png" alt="test_verify_log" width="1024" height="316" class="aligncenter size-large wp-image-943" /></a></p> 