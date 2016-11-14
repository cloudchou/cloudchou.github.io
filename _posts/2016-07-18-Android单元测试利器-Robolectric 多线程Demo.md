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
<h2>多线程测试Demo</h2>
<p>本节使用Robolectric+powermock测试多线程的场景。</p>

<p>Android单元测试系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> </p>

<p>首先，我们看一下，被测试的类的源码，HelloThread的init方法主要功能是启动一个线程，然后在新线程内部做实际初始化，实际初始化完毕后将初始化状态标志为成功或者失败，在本场景里将状态标志为失败。在非多线程的场景中，我们进行单元测试时，通常直接对被测试函数的返回值做校验，而多线程场景中，因为实际功能在另外一条线程里完成，所以对函数的返回值做校验并没有实际价值，但是我们可以通过校验日志来看执行效果。</p>
<p>被测试的类的源码如下所示:</p>
```java
public class HelloThread {

    private InitStatus mInitStatus = InitStatus.INIT;
    private static final String TAG = HelloThread.class.getSimpleName();

    public enum InitStatus {
        INIT,
        INITING,
        OK,
        FAILED
    }

    private HelloThread() {
    }

    private static class HelloThreadHolder {
        private static HelloThread sInstance = new HelloThread();
    }

    public static HelloThread getInstance() {
        return HelloThreadHolder.sInstance;
    }

    public synchronized void init() {
        if (mInitStatus == InitStatus.INIT) {
            mInitStatus = InitStatus.INITING;
            new Thread() {
                @Override
                public void run() {
                    internalInit();
                }
            }.start();
        }
    }

    private void internalInit() {
        System.out.println("========< start init ===>>>");
        try {
            doSomething();
            setInitStatus(InitStatus.OK);
        } catch (Throwable e) {          
            System.out.println("========< init failed ===>>>");
            //初始化失败后打印日志，这也是我们写程序时时常见的一种做法，
            //通过日志能帮助程序员更好地定位问题
            SLog.e(TAG, "init failed");
            setInitStatus(InitStatus.FAILED);
        }
        System.out.println("========< finish init ===>>>");
    }

    private synchronized void setInitStatus(InitStatus status) {
        mInitStatus = status;
        notifyAll();
    }

    public synchronized void waitForInitFinished() throws InterruptedException {
        while (mInitStatus == InitStatus.INITING) {
            wait();
        }
    }

    private void doSomething() throws InterruptedException {
        Thread.sleep(3500);
        //假设初始化失败
        throw new RuntimeException("som exception");
    }

}
```
<p>从代码中可以看到我们在初始化失败时，会打印error日志，这也让我们的校验有了可行性。通过前述章节，我们知道可以对SLog做静态partial mock， 然后在测试init时，收集执行数据，最后对SLog进行校验，看其是否打印了指定的error日志即可。 测试代码如下所示:</p>
```java
@RunWith(RobolectricGradleTestRunner.class)
@Config(constants = BuildConfig.class, sdk = 21)
//必须写如下代码 让PowerMock 忽略Robolectric的所有注入
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"})
//因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类
@PrepareForTest({SLog.class})
public class HelloThreadTest {

    //不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试
    //但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试
    @Rule
    public PowerMockRule rule = new PowerMockRule();

    @Before
    public void setup() {
        PowerMockito.mockStatic(SLog.class);
    }

    @Test
    public void testInit() throws Exception {
        PowerMockito.spy(SLog.class);
        HelloThread.getInstance().init();
        HelloThread.getInstance().waitForInitFinished();
      //因为我们在被测试代码里调用了SLog.e 日志， 所以verifyStatic  必然失败
        PowerMockito.verifyStatic(times(0));
        SLog.e(HelloThread.class.getSimpleName(), "init failed");
    }

}
```
<p>执行结果如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/robolectr_thread_demo.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/robolectr_thread_demo.png" alt="robolectr_thread_demo" width="941" height="349" class="aligncenter size-full wp-image-939" /></a></p>
<p> 可以看到使用PowerMock 对 多线程程序做校验是非常方便的</p> 
