---
id: 815
title: '深入理解Activity启动流程(三)&#8211;Activity启动的详细流程2'
date: 2015-05-25T09:10:52+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=815
permalink: /android/post-815.html
views:
  - 4587
categories:
  - Android
  - 个人总结
tags:
  - activity启动流程
  - activity启动过程
  - android activity启动
  - android app 启动流程
  - android 启动activity
---
<p>本系列博客将详细阐述Activity的启动流程，这些博客基于Cm 10.1源码研究。</p>
<ul>
<li><a href="http://www.cloudchou.com/android/post-788.html" target="_blank">深入理解Activity启动流程(一)--Activity启动的概要流程</a></li>
<li><a href="http://www.cloudchou.com/android/post-793.html" target="_blank">深入理解Activity启动流程(二)--Activity启动相关类的类图</a></li>
<li><a href="http://www.cloudchou.com/android/post-805.html" target="_blank">深入理解Activity启动流程(三)--Activity启动的详细流程1</a></li>
<li><a href="http://www.cloudchou.com/android/post-858.html" target="_blank">深入理解Activity启动流程(四)--Activity Task的调度算法</a></li>
</ul>

<p>上篇博客介绍了Activity详细启动流程的前半部分:</p>
<ul>
    <li>1. Activity调用ActivityManagerService启动应用</li>
    <li>2. ActivityManagerService调用Zygote孵化应用进程</li>
    <li>3. Zygote孵化应用进程</li>
</ul>
<p>本篇博客主要介绍Activity详细启动流程的后半部分:</p>
<ul>
    <li>4. 新进程启动ActivityThread</li>
    <li>5. 应用进程绑定到ActivityManagerService</li>
    <li>6. ActivityThread的Handler处理启动Activity的消息</li>
</ul> 
<h2>4. 新进程启动ActivityThread</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote_activitythread-1024x359.png" alt="zygote_activitythread" width="1024" height="359" class="aligncenter size-large wp-image-812" /></a>
<p>Zygote进程孵化出新的应用进程后，会执行ActivityThread类的main方法。在该方法里会先准备好Looper和消息队列，然后调用attach方法将应用进程绑定到ActivityManagerService，然后进入loop循环，不断地读取消息队列里的消息，并分发消息。</p>
```java
//ActivityThread类
public static void main(String[] args) {
    //... 
    Looper.prepareMainLooper();
    ActivityThread thread = new ActivityThread();
    thread.attach(false);

    if (sMainThreadHandler == null) {
        sMainThreadHandler = thread.getHandler();
    }
    AsyncTask.init();
    //...
    Looper.loop();

    //...
}
```

<h2>5. 应用进程绑定到ActivityManagerService</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice.png"  target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/application_amservice-1024x983.png" alt="application_amservice" width="1024" height="983" class="aligncenter size-large wp-image-810" /></a>
<p>在ActivityThread的main方法里调用thread.attach(false);attach方法的主要代码如下所示:</p>
```java
//ActivityThread类
private void attach(boolean system) {
    sThreadLocal.set(this);
    mSystemThread = system;
    if (!system) {
        //...
        IActivityManager mgr = ActivityManagerNative.getDefault();
        try {
        //调用ActivityManagerService的attachApplication方法
        //将ApplicationThread对象绑定至ActivityManagerService，
        //这样ActivityManagerService就可以
        //通过ApplicationThread代理对象控制应用进程
            mgr.attachApplication(mAppThread);
        } catch (RemoteException ex) {
            // Ignore
        }
    } else {
        //...
    }
    //... 
}
```

<p>ActivityManagerService的attachApplication方法执行attachApplicationLocked(thread, callingPid)进行绑定。</p>
```java
//ActivityManagerService类
private final boolean attachApplicationLocked(IApplicationThread thread,
        int pid) { 
    ProcessRecord app;
    //...     
    app.thread = thread; 
    //...  
    try {
        //...
        thread.bindApplication(processName, appInfo, providers,
                app.instrumentationClass, profileFile, profileFd, profileAutoStop,
                app.instrumentationArguments, app.instrumentationWatcher, testMode,
                enableOpenGlTrace, isRestrictedBackupMode || !normalMode, app.persistent,
                new Configuration(mConfiguration), app.compat, getCommonServicesLocked(),
                mCoreSettingsObserver.getCoreSettingsLocked());
        //... 
    } catch (Exception e) {
       //...
    }
    //... 
    ActivityRecord hr = mMainStack.topRunningActivityLocked(null);
    if (hr != null && normalMode) {
        if (hr.app == null && app.uid == hr.info.applicationInfo.uid
                && processName.equals(hr.processName)) {
            try {
                if (mHeadless) {
                    Slog.e(TAG, "Starting activities not supported on headless device: " + hr);
                } else if (mMainStack.realStartActivityLocked(hr, app, true, true)) {
                //mMainStack.realStartActivityLocked真正启动activity
                    didSomething = true;
                }
            } catch (Exception e) {
                //...
            }
        } else {
            //...
        }
    }
    //... 
    return true;
}
```
<p>attachApplicationLocked方法有两个重要的函数调用thread.bindApplication和mMainStack.realStartActivityLocked。thread.bindApplication将应用进程的ApplicationThread对象绑定到ActivityManagerService，也就是说获得ApplicationThread对象的代理对象。mMainStack.realStartActivityLocked通知应用进程启动Activity。</p>
<h3>5.1 thread.bindApplication</h3>
<p>thread对象其实是ActivityThread里ApplicationThread对象在ActivityManagerService的代理对象，故此执行thread.bindApplication，最终会调用ApplicationThread的bindApplication方法，该方法的主要代码如下所示:</p>
```java
//ActivityThread类
public final void bindApplication(String processName,
        ApplicationInfo appInfo, List<ProviderInfo> providers,
        ComponentName instrumentationName, String profileFile,
        ParcelFileDescriptor profileFd, boolean autoStopProfiler,
        Bundle instrumentationArgs, IInstrumentationWatcher instrumentationWatcher,
        int debugMode, boolean enableOpenGlTrace, boolean isRestrictedBackupMode,
        boolean persistent, Configuration config, CompatibilityInfo compatInfo,
        Map<String, IBinder> services, Bundle coreSettings) {
    //...  
    AppBindData data = new AppBindData();
    data.processName = processName;
    data.appInfo = appInfo;
    data.providers = providers;
    data.instrumentationName = instrumentationName;
    data.instrumentationArgs = instrumentationArgs;
    data.instrumentationWatcher = instrumentationWatcher;
    data.debugMode = debugMode;
    data.enableOpenGlTrace = enableOpenGlTrace;
    data.restrictedBackupMode = isRestrictedBackupMode;
    data.persistent = persistent;
    data.config = config;
    data.compatInfo = compatInfo;
    data.initProfileFile = profileFile;
    data.initProfileFd = profileFd;
    data.initAutoStopProfiler = false;
    queueOrSendMessage(H.BIND_APPLICATION, data);
}
```

<p>这样调用queueOrSendMessage会往ActivityThread的消息队列发送消息，消息的用途是BIND_APPLICATION。</p>
<p>这样会在handler里处理BIND_APPLICATION消息，接着调用handleBindApplication方法处理绑定消息。</p>
```java
//ActivityThread类
private void handleBindApplication(AppBindData data) {
  //...  
  ApplicationInfo instrApp = new ApplicationInfo();
  instrApp.packageName = ii.packageName;
  instrApp.sourceDir = ii.sourceDir;
  instrApp.publicSourceDir = ii.publicSourceDir;
  instrApp.dataDir = ii.dataDir;
  instrApp.nativeLibraryDir = ii.nativeLibraryDir;
  LoadedApk pi = getPackageInfo(instrApp, data.compatInfo,
        appContext.getClassLoader(), false, true);
  ContextImpl instrContext = new ContextImpl();
  instrContext.init(pi, null, this);
    //... 
   
     

  if (data.instrumentationName != null) {
       //...
  } else {
       //注意Activity的所有生命周期方法都会被Instrumentation对象所监控，
       //也就说执行Activity的生命周期方法前后一定会调用Instrumentation对象的相关方法
       //并不是说只有跑单测用例才会建立Instrumentation对象，
       //即使不跑单测也会建立Instrumentation对象
       mInstrumentation = new Instrumentation();
  }
  //... 
  try {
     //...
     Application app = data.info.makeApplication(data.restrictedBackupMode, null);
     mInitialApplication = app;
     //...         
     try {
          mInstrumentation.onCreate(data.instrumentationArgs);
      }catch (Exception e) {
             //...
      }
      try {
           //这里会调用Application的onCreate方法
           //故此Applcation对象的onCreate方法会比ActivityThread的main方法后调用
           //但是会比这个应用的所有activity先调用
            mInstrumentation.callApplicationOnCreate(app);
        } catch (Exception e) {
           //...
        }
    } finally {
        StrictMode.setThreadPolicy(savedPolicy);
    }
}
```

<h3>5.2 mMainStack.realStartActivityLocked</h3>
<p>realStartActivity会调用scheduleLaunchActivity启动activity，主要代码:</p>
```java
//ActivityStack类
final boolean realStartActivityLocked(ActivityRecord r,
        ProcessRecord app, boolean andResume, boolean checkConfig)
        throws RemoteException {

    //...  
    try {
        //...
        app.thread.scheduleLaunchActivity(new Intent(r.intent), r.appToken,
                System.identityHashCode(r), r.info,
                new Configuration(mService.mConfiguration),
                r.compat, r.icicle, results, newIntents, !andResume,
                mService.isNextTransitionForward(), profileFile, profileFd,
                profileAutoStop);
        
        //...
        
    } catch (RemoteException e) {
        //...
    }
    //...    
    return true;
}
```
<p>同样app.thread也只是ApplicationThread对象在ActivityManagerService的一个代理对象而已，最终会调用ApplicationThread的scheduleLaunchActivity方法。</p>
```java
//ActivityThread类
public final void scheduleLaunchActivity(Intent intent, IBinder token, int ident,
        ActivityInfo info, Configuration curConfig, CompatibilityInfo compatInfo,
        Bundle state, List<ResultInfo> pendingResults,
        List<Intent> pendingNewIntents, boolean notResumed, boolean isForward,
        String profileName, ParcelFileDescriptor profileFd, boolean autoStopProfiler) {
    ActivityClientRecord r = new ActivityClientRecord();
    r.token = token;
    r.ident = ident;
    r.intent = intent;
    r.activityInfo = info;
    r.compatInfo = compatInfo;
    r.state = state;
    r.pendingResults = pendingResults;
    r.pendingIntents = pendingNewIntents;
    r.startsNotResumed = notResumed;
    r.isForward = isForward;
    r.profileFile = profileName;
    r.profileFd = profileFd;
    r.autoStopProfiler = autoStopProfiler;
    updatePendingConfiguration(curConfig);
    queueOrSendMessage(H.LAUNCH_ACTIVITY, r);
}
```
<p>这里调用了queueOrSendMessage往ActivityThread的消息队列发送了消息，消息的用途是启动Activity，接下来ActivityThread的handler便会处理该消息。</p>
<h2>6. ActivityThread的Handler处理启动Activity的消息</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/activitythread_activity-926x1024.png" alt="activitythread_activity" width="926" height="1024" class="aligncenter size-large wp-image-808" /></a>
<p>ActivityThread的handler调用handleLaunchActivity处理启动Activity的消息，handleLaunchActivity的主要代码如下所示:</p>
```java
//ActivityThread类
private void handleLaunchActivity(ActivityClientRecord r, Intent customIntent) {
    //... 
    Activity a = performLaunchActivity(r, customIntent);
    if (a != null) {
        //...
        handleResumeActivity(r.token, false, r.isForward,
                !r.activity.mFinished && !r.startsNotResumed);
        //...
    } else {
        //...
    }
}
```
<p>handleLaunchActivity方法里有有两个重要的函数调用,performLaunchActivity和handleResumeActivity,performLaunchActivity会调用Activity的onCreate,onStart,onResotreInstanceState方法,handleResumeActivity会调用Activity的onResume方法.</p>
<h3>6.1 performLaunchActivity</h3>
<p>performLaunchActivity的主要代码如下所示:</p>
```java
//ActivityThread类
private Activity performLaunchActivity(ActivityClientRecord r, Intent customIntent) {
    //...
    Activity activity = null;
    try {
        java.lang.ClassLoader cl = r.packageInfo.getClassLoader();
        activity = mInstrumentation.newActivity(
                cl, component.getClassName(), r.intent);
        //...
    } catch (Exception e) {
        //...
    }
    try {
        //r.packageInfo.makeApplication实际并未创建Application对象，
        //因为bindApplication过程已经创建了Application对象，
        //makeApplication方法会返回已创建的Application对象
        Application app = r.packageInfo.makeApplication(false, mInstrumentation);
        //...         
        if (activity != null) {
            //...
            //将application对象,appContext对象绑定到新建的activity对象
            activity.attach(appContext, this, getInstrumentation(), r.token,
                    r.ident, app, r.intent, r.activityInfo, title, r.parent,
                    r.embeddedID, r.lastNonConfigurationInstances, config);
            //... 
            //会调用Activity的onCreate方法             
            mInstrumentation.callActivityOnCreate(activity, r.state);
            //...
            //...
            //调用Activity的onStart方法
            if (!r.activity.mFinished) {
                activity.performStart();
                r.stopped = false;
            }              
            if (!r.activity.mFinished) {
                if (r.state != null) {
                    //会调用Activity的onRestoreInstanceState方法
                    mInstrumentation.callActivityOnRestoreInstanceState(activity, r.state);
                }
            }
            if (!r.activity.mFinished) {
                activity.mCalled = false;
                mInstrumentation.callActivityOnPostCreate(activity, r.state);
                //...
            }
        }
        //...
    } catch (SuperNotCalledException e) {
        throw e;

    } catch (Exception e) {
        //...
    }
    return activity;
}
```
<h3>6.2 handleResumeActivity</h3>
<p>handleResumeActivity的主要代码如下所示:</p>
```java
//ActivityThread类
final void handleResumeActivity(IBinder token, boolean clearHide, boolean isForward,
        boolean reallyResume) {
    //...
    //performResumeActivity最终会调用Activity的onResume方法 
    ActivityClientRecord r = performResumeActivity(token, clearHide);
    if (r != null) {
        final Activity a = r.activity;
        //... 
        //显示界面
        if (r.window == null && !a.mFinished && willBeVisible) {
            r.window = r.activity.getWindow();
            View decor = r.window.getDecorView();
            decor.setVisibility(View.INVISIBLE);
            ViewManager wm = a.getWindowManager();
            WindowManager.LayoutParams l = r.window.getAttributes();
            a.mDecor = decor;
            l.type = WindowManager.LayoutParams.TYPE_BASE_APPLICATION;
            l.softInputMode |= forwardBit;
            if (a.mVisibleFromClient) {
                a.mWindowAdded = true;
                wm.addView(decor, l);
            }
           //...         
        } else if (!willBeVisible) {
             //...
        }
        // Tell the activity manager we have resumed.
        if (reallyResume) {
            try {
                ActivityManagerNative.getDefault().activityResumed(token);
            } catch (RemoteException ex) {
            }
        }

    } else {
         //...
    }
}
```
<p>performResumeActivity的主要代码如下所示:</p>
```java
//ActivityThread类
public final ActivityClientRecord performResumeActivity(IBinder token,
        boolean clearHide) {
    ActivityClientRecord r = mActivities.get(token);
    //...
    if (r != null && !r.activity.mFinished) {
         //...
        try {
            //... 
            //会调用Activity的onResume方法 
            r.activity.performResume();
            //...
        } catch (Exception e) {
            //...
        }
    }
    return r;
}
```
<h2>总结</h2>
<p>Activity的概要启动流程:</p>
<p>用户在Launcher程序里点击应用图标时，会通知ActivityManagerService启动应用的入口Activity，ActivityManagerService发现这个应用还未启动，则会通知Zygote进程孵化出应用进程，然后在这个dalvik应用进程里执行ActivityThread的main方法。应用进程接下来通知ActivityManagerService应用进程已启动，ActivityManagerService保存应用进程的一个代理对象，这样ActivityManagerService可以通过这个代理对象控制应用进程，然后ActivityManagerService通知应用进程创建入口Activity的实例，并执行它的生命周期方法 </p>
<p>现在也可以理解: </p>
<p>如果应用的组件(包括所有组件Activity，Service，ContentProvider，Receiver) 被启动，肯定会先启动以应用包名为进程名的进程，这些组件都会运行在应用包名为进程名的进程里，并且是在主线程里。应用进程启动时会先创建Application对象，并执行Application对象的生命周期方法，然后才启动应用的组件。</p>
<p>有一种情况比较特殊，那就是为组件设置了特殊的进程名，也就是说通过android:process设置进程名的情况，此时组件运行在单独的进程内。</p>
<p>下篇博客将介绍Activity,Task的调度算法。</p>

