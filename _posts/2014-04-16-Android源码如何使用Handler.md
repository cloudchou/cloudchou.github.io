---
id: 414
title: Android源码如何使用Handler
date: 2014-04-16T23:03:14+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=414
permalink: /android/post-414.html
views:
  - 3360
categories:
  - Android
tags:
  - ActivityThread
  - android handler and asynctask
  - android handler thread
  - android handler 使用
  - android handler 用法
  - HandlerThread
  - IntentService
---
<h2>前言</h2>
<p><a href="http://www.cloudchou.com/android/post-388.html" target="_blank">前一篇</a>文章我们详细分析了Handler机制的实现，这一篇会给大家介绍Android源码里如何使用Handler。这里会介绍以下4个例子：</p>
<li>
 <h3>1)ActivityThread</h3>
 <p>Activity运行在ActivityThread里，ActivityThread就是Android应用开发时所说的UI线程，或者说是主线程，它使用了Handler机制。</p>
</li>
<li>
 <h3>2)AsyncTask</h3>
 <p>AsyncTask的实现也用到了Handler机制。</p>
</li>
<li>
 <h3>3)HandlerThread</h3>
 <p>HandlerThread继承自Thread，它的run方法里会创建Looper，并调用Looper.loop方法进入死循环，我们可以用HandlerThread实现worker thread。</p>
</li>
<li>
 <h3>4)IntentService</h3>
 <p>IntentService的实现使用了HandlerThread，将客户端的请求交给了HanderThread，这样不会阻塞主线程，也就不会产生ANR问题。</p>
</li>

<h2>1. ActivityThread使用Handler</h2>
<p>ActivityThread源码位于：frameworks/base/core/java/android/app/ActivityThread.java</p>
<li>1)准备Looper </li>
```java
public static void main(String[] args) {
  //...
  //创建主线程的Looper实例和MessageQueue实例
  Looper.prepareMainLooper();
  //创建ActivityThread
  ActivityThread thread = new ActivityThread();
  //交给ActivityManagerService管理
  thread.attach(false);
  //设置mainHandler
  if (sMainThreadHandler == null) {
      sMainThreadHandler = thread.getHandler();
  }
  //初始化AsyncTask，设置它的Handler，这样在Activity里使用AsyncTask才可正常使用
  AsyncTask.init();
  if (false) {
      Looper.myLooper().setMessageLogging(new
              LogPrinter(Log.DEBUG, "ActivityThread"));
  }
  //进入loop循环，会不断从MessageQueue里取出Message，并分发Message
  Looper.loop();
  throw new RuntimeException("Main thread loop unexpectedly exited");
}
```
<li>2)创建Handler</li>
```java
final H mH = new H();
private class H extends Handler {
  public static final int LAUNCH_ACTIVITY         = 100;
  public static final int PAUSE_ACTIVITY          = 101;
  //...
  String codeToString(int code) {
      if (DEBUG_MESSAGES) {
          switch (code) {
              case LAUNCH_ACTIVITY: return "LAUNCH_ACTIVITY";
              case PAUSE_ACTIVITY: return "PAUSE_ACTIVITY";
          //...
          }
      }
      return Integer.toString(code);
  }
  //覆盖Handler的handleMessage方法，针对不同的消息类型进行不同的处理
  public void handleMessage(Message msg) {
      if (DEBUG_MESSAGES) Slog.v(TAG, ">>> handling: " + 
                                   codeToString(msg.what));
      switch (msg.what) {
          case LAUNCH_ACTIVITY: {
              Trace.traceBegin(Trace.TRACE_TAG_ACTIVITY_MANAGER,
               "activityStart");
              ActivityClientRecord r = (ActivityClientRecord)msg.obj;

              r.packageInfo = getPackageInfoNoCheck(
                      r.activityInfo.applicationInfo, r.compatInfo);
              handleLaunchActivity(r, null);
              Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);
          } break;
          case RELAUNCH_ACTIVITY: {
              Trace.traceBegin(Trace.TRACE_TAG_ACTIVITY_MANAGER, 
              "activityRestart");
              ActivityClientRecord r = (ActivityClientRecord)msg.obj;
              handleRelaunchActivity(r);
              Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);
          } break;
         //...
      }
      if (DEBUG_MESSAGES) Slog.v(TAG, "<<< done: " + 
                           codeToString(msg.what));
  }
 //...
}
```
<li>3)使用Handler发送消息</li>
```java
private void queueOrSendMessage(int what, Object obj, int arg1, int arg2) {
  synchronized (this) {
      if (DEBUG_MESSAGES) Slog.v(
          TAG, "SCHEDULE " + what + " " + mH.codeToString(what)
          + ": " + arg1 + " / " + obj);
      Message msg = Message.obtain();
      msg.what = what;
      msg.obj = obj;
      msg.arg1 = arg1;
      msg.arg2 = arg2;
      mH.sendMessage(msg);
  }
}
```
<p>ActivityThread里的Schedule系列方法都是调用queueOrSendMessage发送Message，然后在Handler里处理消息</p>

<h2>2. AsyncTask使用Handler</h2>
<li>1)Handler子类</li>
```java
private static class InternalHandler extends Handler {
  @SuppressWarnings({"unchecked", "RawUseOfParameterizedType"})
  @Override
  public void handleMessage(Message msg) {
      AsyncTaskResult result = (AsyncTaskResult) msg.obj;
      switch (msg.what) {
          case MESSAGE_POST_RESULT://告知结果，会回调onPostExecute方法
              // There is only one result
              result.mTask.finish(result.mData[0]);
              break;
          case MESSAGE_POST_PROGRESS://汇报进度，会回调onProgressUpdate
              result.mTask.onProgressUpdate(result.mData);
              break;
      }
  }
}
private static final InternalHandler sHandler = new InternalHandler();
```


<li>2)初始化</li>
<p>关联loope和MessageQueue</p>
```java
public static void init() {
  sHandler.getLooper();
}
```
<p>实际上不执行sHandler.getLooper()也可以正常关联looper和MessageQueue，在ui线程里创建AsyncTask时，就会初始化好sHandler。</p>

<li>3)发送消息</li>
```java
private Result postResult(Result result) {
  @SuppressWarnings("unchecked")
  Message message = sHandler.obtainMessage(MESSAGE_POST_RESULT,
          new AsyncTaskResult<Result>(this, result));
  message.sendToTarget();
  return result;
}
protected final void publishProgress(Progress... values) {
  if (!isCancelled()) {
      sHandler.obtainMessage(MESSAGE_POST_PROGRESS,
              new AsyncTaskResult<Progress>(this, values)).sendToTarget();
  }
}
```
<h2>3. HandlerThread</h2>
<p>HandlerThread从Thread类继承，run方法里会创建Looper，并调用Looper.prepare和Looper.loop方法，这样HandlerThread有了自己的Looper对象和MessageQueue对象。</p>
<p>使用HandlerThread时，必须调用start方法，这样便启动了一个带有Looper的新线程。</p>
<p>HandlerThread使用示例：</p>
```java
private static Handler sAsyncHandler
static{
HandlerThread thr = new HandlerThread("Open browser download async");
thr.start();
sAsyncHandler = new Handler(thr.getLooper());
} 
@Override
public void onReceive(final Context context, Intent intent) {
  //...
  Runnable worker = new Runnable() {
      @Override
      public void run() {
          onReceiveAsync(context, id);
          result.finish();
      }
  };
  //worker会在HandlerThread里运行，而不会在调用onReceive的线程里执行
  sAsyncHandler.post(worker);
}
```

<h2>4. IntentService</h2>
<p>IntentService继承于Service，用于处理异步请求。Client通过startService(Intent)发送请求给IntentService，这样便启动了service，它会使用worker thread处理每个Intent请求，处理完所有请求后，它就会停止。</p>
<p>IntentService使用了work queue processor模式将任务从主线程剥离，IntentService的子类不用关心这些事情，只需关注自己的逻辑即可，不用担心ANR异常，因为所有的任务都会在非主线程里按序执行。使用IntentService时只需从IntentService继承，并实现onHandleIntent(Intent)方法，注意onHandleIntent是运行在非主线程里的。IntentService接收Intent后，会启动一个worker thread，并在适当的时候停止。</p>
<p>所有的请求都会在同一个worker thread里处理，不用担心他们运行时间非常长，它们也不会阻塞程序的main loop。这些请求会形成队列，每次处理一个，处理完一个后再从队列里取出下一个进行处理。</p>
```java
public abstract class IntentService extends Service {
    private volatile Looper mServiceLooper;
    private volatile ServiceHandler mServiceHandler;
    private String mName;
    private boolean mRedelivery;

   /**
    *ServiceHandler使用HandlerThread的Looper
    *没有使用主线程的Looper
    *故此它的handleMessage方法在HandlerThread里执行，而非主线程
*/
    private final class ServiceHandler extends Handler {
        public ServiceHandler(Looper looper) {
            super(looper);
        }

        @Override
        public void handleMessage(Message msg) {
            onHandleIntent((Intent)msg.obj);
            stopSelf(msg.arg1);
        }
    }

    //name用于给worker thread命名，方便调试 
    public IntentService(String name) {
        super();
        mName = name;
    }

   /**
    *设置intent redelivery偏好 
    *如果enabled设置为true， 
    *那么当进程在onHandleIntent(Intent)返回之前被杀死了， 
    *onStartCommand(Intent, int, int)会返回Service.START_REDELIVER_INTENT
    *进程会被重启，intent会被重新发送
    *如果多个Intent被发送了，那么只有最新的那个会被保证重新发送
    *如果enabled设置为false，
    *那么当进程在onHandleIntent(Intent)返回之前被杀死了
    *onStartCommand(Intent, int, int)会返回Service.START_NOT_STICKY
    *Intent也不会被重新发送     
    */
    public void setIntentRedelivery(boolean enabled) {
        mRedelivery = enabled;
    }

    @Override
    public void onCreate() { 
        super.onCreate();
        //在HandlerThread里处理请求，而非UI线程
        HandlerThread thread = new HandlerThread
                            ("IntentService[" + mName + "]");
        thread.start();
        //mServiceHandler使用HandlerThread的looper对象，而非主线程的
        mServiceLooper = thread.getLooper();
        mServiceHandler = new ServiceHandler(mServiceLooper);
    }

   /**
    *收到Intent后，让HandlerThread处理，
    *然后mServiceHandler的handleMessage会调用
    *留给子类实现的onHandleIntent方法
    */
    @Override
    public void onStart(Intent intent, int startId) {
        Message msg = mServiceHandler.obtainMessage();
        msg.arg1 = startId;
        msg.obj = intent;
        mServiceHandler.sendMessage(msg);
    }
 
    //不要覆盖该方法，而是要覆盖onHandleIntent方法
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        onStart(intent, startId);
        return mRedelivery ? START_REDELIVER_INTENT : START_NOT_STICKY;
    }

//退出
    @Override
    public void onDestroy() {
        mServiceLooper.quit();
    }

    /**
     *  不需要覆盖onBind方法，在IntentService里不用这个方法     
     */
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
 
    /**
     *这个方法会在worker thread线程执行，即HandlerThread，
     *一次只处理一个Intent请求，
     *处理请求时会和程序的其它逻辑完全独立
     *因此如果处理请求需要一段时间的话，发送给IntentService的Intent请求会被排队
     *所有请求都被处理完毕后，IntentService会干掉自己，
     *子类实现该方法时不需要调用stopSelf。
     */
    protected abstract void onHandleIntent(Intent intent);
} 
```
