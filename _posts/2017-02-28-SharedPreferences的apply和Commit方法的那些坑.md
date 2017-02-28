---
id: 988
title: SharedPreferences的apply和Commit方法的那些坑
date: 2017-02-28T16:27:13+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=988
permalink: /android/post-988.html
categories:
  - Android
tags:
  - Android
---

大家都知道，使用SharedPreferences时，用apply方法比commit方法效率更高，但是apply方法其实有一个巨大的坑，容易引发ANR问题。

# 问题背景

我们做App时，发现一个很奇怪的ANR问题， ANR时主线程的堆栈是这样的:

```text
"main" prio=5 tid=1 WAIT
  | group="main" sCount=1 dsCount=0 obj=0x4155cc90 self=0x41496408
  | sysTid=13523 nice=0 sched=0/0 cgrp=apps handle=1074110804
  | state=S schedstat=( 2098661082 1582204811 6433 ) utm=165 stm=44 core=0
  at java.lang.Object.wait(Native Method)
  - waiting on <0x4155cd60> (a java.lang.VMThread) held by tid=1 (main)
  at java.lang.Thread.parkFor(Thread.java:1205)
  at sun.misc.Unsafe.park(Unsafe.java:325)
  at java.util.concurrent.locks.LockSupport.park(LockSupport.java:157)
  at java.util.concurrent.locks.AbstractQueuedSynchronizer.parkAndCheckInterrupt(AbstractQueuedSynchronizer.java:813)
  at java.util.concurrent.locks.AbstractQueuedSynchronizer.doAcquireSharedInterruptibly(AbstractQueuedSynchronizer.java:973)
  at java.util.concurrent.locks.AbstractQueuedSynchronizer.acquireSharedInterruptibly(AbstractQueuedSynchronizer.java:1281)
  at java.util.concurrent.CountDownLatch.await(CountDownLatch.java:202)
  at android.app.SharedPreferencesImpl$EditorImpl$1.run(SharedPreferencesImpl.java:364)
  at android.app.QueuedWork.waitToFinish(QueuedWork.java:88)
  at android.app.ActivityThread.handleServiceArgs(ActivityThread.java:2689)
  at android.app.ActivityThread.access$2000(ActivityThread.java:135)
  at android.app.ActivityThread$H.handleMessage(ActivityThread.java:1494)
  at android.os.Handler.dispatchMessage(Handler.java:102)
  at android.os.Looper.loop(Looper.java:137)
  at android.app.ActivityThread.main(ActivityThread.java:4998)
  at java.lang.reflect.Method.invokeNative(Native Method)
  at java.lang.reflect.Method.invoke(Method.java:515)
  at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:777)
  at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:593)
  at dalvik.system.NativeStart.main(Native Method)
```

可以看到QueuedWork.waitToFinish方法最终会等待SharedPreference类里的一个锁， 这个很奇怪， 我们没有直接在主线程里去调用SharedPreference的commit操作，但是居然因为SharedPreference导致ANR。

# 原因分析

我们先看源码中QueuedWork.waitToFinish方法的说明:

```
/**
     * Finishes or waits for async operations to complete.
     * (e.g. SharedPreferences$Editor#startCommit writes)
     *
     * Is called from the Activity base class's onPause(), after
     * BroadcastReceiver's onReceive, after Service command handling,
     * etc.  (so async work is never lost)
     */
    public static void waitToFinish() {
        Runnable toFinish;
        while ((toFinish = sPendingWorkFinishers.poll()) != null) {
            toFinish.run();
        }
    }
```

可以看到QueueWork.waitToFinish方法会在Activity暂停时或者BroadcastReceiver的onReceive方法调用后或者service的命令处理后被调用，并且调用这个方法的目的是为了确保异步任务被及时完成。

而在waitToFinish方法里会遍历sPendingWorkFinishers中所有等待完成的任务，并等待它们完成。

我们再看一下SharedPreference.Editor的apply方法的源码:

```
public void apply() {
            final MemoryCommitResult mcr = commitToMemory();
            final Runnable awaitCommit = new Runnable() {
                    public void run() {
                        try {
                            mcr.writtenToDiskLatch.await();
                        } catch (InterruptedException ignored) {
                        }
                    }
            };
			//在这里添加到QueuedWork的等待完成队列里
            QueuedWork.add(awaitCommit);
            // ...
            SharedPreferencesImpl.this.enqueueDiskWrite(mcr, postWriteRunnable);
 		    // ...
}
```

可以看到apply方法会将等待写入到文件系统的任务放在QueuedWork的等待完成队列里。

所以如果我们使用SharedPreference的apply方法, 虽然该方法可以很快返回， 并在其它线程里将键值对写入到文件系统， 但是当Activity的onPause等方法被调用时，会等待写入到文件系统的任务完成，所以如果写入比较慢，主线程就会出现ANR问题。

而commit方法的源码如下所示:

```
public boolean commit() {
           MemoryCommitResult mcr = commitToMemory();
           SharedPreferencesImpl.this.enqueueDiskWrite(
               mcr, null /* sync write on this thread okay */);
           try {
               mcr.writtenToDiskLatch.await();
           } catch (InterruptedException e) {
               return false;
           }
           notifyListeners(mcr);
           return mcr.writeToDiskResult;
}
```

它会在调用线程就等待写入任务完成，所以不会将等待的时间转嫁到主线程

# 总结

apply方法和commit方法对比:

1. apply没有返回值而commit返回boolean表明修改是否提交成功 

2. apply方法不会提示任何失败的提示

3. apply是将修改数据原子提交到内存, 而后异步真正提交到硬件磁盘, 而commit是同步的提交到硬件磁盘，因此，在多个并发的提交commit的时候，他们会等待正在处理的commit保存到磁盘后在操作，从而降低了效率。而apply只是原子的提交到内容，后面有调用apply的函数的将会直接覆盖前面的内存数据，这样从一定程度上提高了很多效率

4. 虽然apply方法不会阻塞调用线程， 但是会将等待时间转嫁到主线程(UI线程)，容易造成ANR问题

为了避免出现ANR问题，最好还是别使用apply操作，用commit方法最保险。如果担心在主线程调用commit方法会出现ANR，可以将所有的commit任务放到单线程池的线程里去执行。

