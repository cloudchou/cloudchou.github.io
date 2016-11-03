---
id: 426
title: Android FutureTask
date: 2014-04-18T09:00:11+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=426
permalink: /android/post-426.html
views:
  - 3938
categories:
  - Android
tags:
  - android futuretask
  - callable future futuretask
  - futuretask future
  - futuretask future 区别
  - futuretask 用法
---
## 前言

研究AsyncTask的源码时遇到了FutureTask这个类，以前没用过，对它感觉很困惑，看FutureTask 的实现也不是很明白，于是重温了一遍Executor相关的类和接口，象Executor，ExecutorService，Callable接口，Runnable接口，Future接口，再研究了一下各个接口和类之间的关系，弄清楚了FutureTask的本意，现分享如下。

## Exector相关类

Executor相关类如下图所示:

<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/executor.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/executor.png" alt="executor" width="1008" height="614" class="alignnone size-full wp-image-429" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/executor.png 1008w, http://www.cloudchou.com/wp-content/uploads/2014/04/executor-300x182.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/executor-200x121.png 200w" sizes="(max-width: 1008px) 100vw, 1008px" /></a>

### 相关类介绍如下：

  * ### 1) Runnable
    
    通常我们实现线程时有两种方法，创建一个Runnable匿名对象，并在run方法里写逻辑，然后将Runnable对象传给Thread对象，然后调用Thread的start方法启动线程。另一种方法是直接继承Thread，覆盖run方法，然后创建Thread对象并调用Start方法启动线程。
    
    还可以使用Excecutor来建立线程，并执行Runnable。

  * ### 2) Executor
    
    执行Runnable对象，提供了execute方法，实现该接口的类通常会新建线程来执行Runnable，我们通常会在execute方法里对Runnable对象采取某种调度策略。当然实现者也可以直接执行Runnable的run方法，这样就和调用者运行在相同的线程。

  * ### 3) Callable
    
    执行Runnable不能返回数据，故此提供了Callable接口，调用者可以获取执行的结果。

  * ### 4) Future
    
    调用用ExecutorService提交Runnable或者Callable时可返回一个Future对象，ExecutorService并不一定立即执行Runnable或者Callable，但是会立即返回一个Future对象，client端可以调用Future的get方法获取Callable执行的结果，但是如果结果还没有准备好，那么get方法会阻塞，还可以用Future去取消要执行的Callable或者Runnable。

  * ### 5) ExecutorService
    
    从Executor接口继承，不仅能执行Runnable，还能执行Callable，并返回Future，它还能执行一批Runnable或者Callable。 

  * ### 6) ThreadPoolExecutor
    
    实现了ExecutorService接口的最常用的类，Executors的new系列方法大多是封装了一个ThreadPoolExecutor。

  * ### 7) Excecutors
    
    它是创建ExecutorService的简单工厂，另外还有一个将Runnable转成Callable的适配接口。new系列方法大多是封装了一个ThreadPoolExecutor。

```java
    public static ExecutorService newFixedThreadPool(int nThreads, 
                                ThreadFactory threadFactory) {
        return new ThreadPoolExecutor(nThreads, nThreads,
                                      0L, TimeUnit.MILLISECONDS,
                                      new LinkedBlockingQueue<Runnable>(),
                                      threadFactory);
    }

    public static ExecutorService newSingleThreadExecutor() {
        return new FinalizableDelegatedExecutorService
            (new ThreadPoolExecutor(1, 1,
                                    0L, TimeUnit.MILLISECONDS,
                                    new LinkedBlockingQueue<Runnable>()));
    }

    public static ExecutorService newCachedThreadPool(
                              ThreadFactory threadFactory) {
        return new ThreadPoolExecutor(0, Integer.MAX_VALUE,
                                      60L, TimeUnit.SECONDS,
                                      new SynchronousQueue<Runnable>(),
                                      threadFactory);
    }

    public static ScheduledExecutorService newScheduledThreadPool(
            int corePoolSize, ThreadFactory threadFactory) {
        return new ScheduledThreadPoolExecutor(corePoolSize, threadFactory);
    }
```

## FutureTask相关类

FutureTask相关类如下图所示：

[<img src="http://www.cloudchou.com/wp-content/uploads/2014/04/FutureTask.png" alt="FutureTask" width="724" height="597" class="alignnone size-full wp-image-431" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/FutureTask.png 724w, http://www.cloudchou.com/wp-content/uploads/2014/04/FutureTask-300x247.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/FutureTask-181x150.png 181w" sizes="(max-width: 724px) 100vw, 724px" />](http://www.cloudchou.com/wp-content/uploads/2014/04/FutureTask.png)

从上一节可知道Runnable是用来实现线程的，Future是用于获取线程执行结果的，但是这里有一个比较奇特的类RunnableFuture，它既继承了Runnable，也继承了Future，乍看起来觉得特奇怪，其实仔细想想，它们也就是接口而已，RunnableFuture既有了Runnable的特性，也有了Future的特性，也就是说它能提交给Exceutor或者ExecutorService执行，还能用来取消任务，获取任务执行结果。

FutureTask实现了RunnableFuture，自然有了RunnableFuture的所有方法，也就是说它能被Executor或者ExecutorService执行，并可以用来获取结果，以及取消自身对应的任务。

AsyncTask的实现使用了FutureTask。