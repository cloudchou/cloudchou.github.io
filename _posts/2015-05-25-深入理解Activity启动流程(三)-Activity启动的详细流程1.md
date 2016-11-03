---
id: 805
title: '深入理解Activity启动流程(三)&#8211;Activity启动的详细流程1'
date: 2015-05-25T09:10:05+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=805
permalink: /android/post-805.html
views:
  - 3959
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
<li><a href="http://www.cloudchou.com/android/post-815.html" target="_blank">深入理解Activity启动流程(三)--Activity启动的详细流程2</a></li>
<li><a href="http://www.cloudchou.com/android/post-858.html" target="_blank">深入理解Activity启动流程(四)--Activity Task的调度算法</a></li>
</ul>

<p>本篇博客将开始介绍Activity启动的详细流程，由于详细启动流程非常复杂，故此分成两篇来介绍。</p>
<p>本篇主要介绍前半部分的启动流程:</p>
<ul>
    <li>1. Activity调用ActivityManagerService启动应用</li>
    <li>2. ActivityManagerService调用Zygote孵化应用进程</li>
    <li>3. Zygote孵化应用进程</li>
</ul>
<p>下篇介绍后半部分的启动流程:</p>
<ul>
    <li>4. 新进程启动ActivityThread</li>
    <li>5. 应用进程绑定到ActivityManagerService</li>
    <li>6. ActivityThread的Handler处理启动Activity的消息</li>
</ul>

<h2>1. Activity调用ActivityManagerService启动应用</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/activity_amservice.png" alt="activity_amservice" width="917" height="485" class="aligncenter size-full wp-image-807" /></a>
<p>在launcher应用程序里启动应用时，点击应用图标后，launcher程序会调用startActivity启动应用，传递的intent参数:</p>
```java
intent = new Intent(Intent.ACTION_MAIN);
   intent.addCategory(Intent.CATEGORY_LAUNCHER);
   intent.setComponent(className);
```
<p>activity最终调用Instrumentation的execStartActivity来启动应用:</p>
```java
//Activity类
public void startActivityForResult(Intent intent, int requestCode, Bundle options) {
 if (mParent == null) {
\tInstrumentation.ActivityResult ar =
\t                mInstrumentation.execStartActivity(
\t                    this, mMainThread.getApplicationThread(), mToken, this,
\t                    intent, requestCode, options);
\t   if (ar != null) {
\t                mMainThread.sendActivityResult(
\t                    mToken, mEmbeddedID, requestCode, ar.getResultCode(),
\t                    ar.getResultData());
\t   } 
\t//...   
 }else{
  //...
 } \t   
```
<p>Instrumentation调用ActivityManagerProxy对象的startActivity方法启动Activity，而ActivityManagerProxy只是ActivityManagerService对象在应用进程的一个代理对象，ActivityManagerProxy最终调用ActivityManagerService的startActvity方法启动Activity。</p>
```java
//Instrumentation类
public ActivityResult execStartActivity(
          Context who, IBinder contextThread, IBinder token, Activity target,
          Intent intent, int requestCode, Bundle options) {
//...
 try{          
   //...
   int result = ActivityManagerNative.getDefault()
                .startActivity(whoThread, intent,
                        intent.resolveTypeIfNeeded(who.getContentResolver()),
                        token, target != null ? target.mEmbeddedID : null,
                        requestCode, 0, null, null, options);
   } catch (RemoteException e) {
   }   
//...   
}                     
```


<h2>2. ActivityManagerService调用Zygote孵化应用进程</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/amservice_zygote.png" alt="amservice_zygote" width="1132" height="1048" class="aligncenter size-full wp-image-809" /></a>
<p>ActivityManagerProxy对象调用ActivityManagerService对象(运行在system_server进程)的startActivity方法以启动应用，startActivity方法接下来调用startActivityAsUser方法以启动应用。在startActivityAsUser方法里会调用ActivityStack的startActivityMayWait方法以启动应用，startActivityMayWait方法里启动应用时，需先根据intent在系统中找到合适的应用的activity，如果有多个activity可选择，则会弹出ResolverActivity让用户选择合适的应用。</p>
```java
//ActivityStack类
final int startActivityMayWait(IApplicationThread caller, int callingUid,
            Intent intent, String resolvedType, IBinder resultTo,
            String resultWho, int requestCode, int startFlags, String profileFile,
            ParcelFileDescriptor profileFd, WaitResult outResult, Configuration config,
            Bundle options, int userId) {
//…
//根据intent在系统中找到合适的应用的activity，如果有多个activity可选择，
//则会弹出ResolverActivity让用户选择合适的应用。
  ActivityInfo aInfo = resolveActivity(intent, resolvedType, startFlags,
                profileFile, profileFd, userId);
//…
int res = startActivityLocked(caller, intent, resolvedType,
                    aInfo, resultTo, resultWho, requestCode, callingPid, callingUid,
                    startFlags, options, componentSpecified, null);
//…
｝
```
<p>在startActivityLocked方法里，对传过来的参数做一些校验，然后创建ActivityRecord对象，再调用startActivityUncheckedLocked方法启动Activity。</p>
<p>startActivityUncheckedLocked方法负责调度ActivityRecord和Task，理解该方法是理解Actvity启动模式的关键。</p>
<p>startActivityUncheckedLocked方法调度task的算法非常复杂，和当前回退栈，要启动的acitivity的启动模式以及taskAffinity属性，启动activity时设置的intent的flag等诸多要素相关，intent的flag就有很多种情况，故此算法非常复杂，需要阅读源码并结合特定启动情况才能理解。</p>
<p>后续会介绍startActivityUncheckedLocked方法的实现，并结合特定场景分析调度算法。</p>
<p>接下来调用startActivityLocked将ActivityRecord加入到回退栈里:</p>
```java
//ActivityStack类
final int startActivityUncheckedLocked(ActivityRecord r,
          ActivityRecord sourceRecord, int startFlags, boolean doResume,
          Bundle options) {
//...          
startActivityLocked(r, newTask, doResume, keepCurTransition, options);
//...
}
```
<p>在startActivityLocked里调用resumeTopActivityLocked显示栈顶Activity:</p>
```java
//ActivityStack类
private final void startActivityLocked(ActivityRecord r, boolean newTask,
        boolean doResume, boolean keepCurTransition, Bundle options) {
 //...        
 if (doResume) {
   resumeTopActivityLocked(null);
 }  
}
```
<p>resumeTopActivityLocked(null)会调用另一个resumeTopActivityLocked方法显示栈顶的acitivity:</p>
```java
//ActivityStack类
final boolean resumeTopActivityLocked(ActivityRecord prev) {
    return resumeTopActivityLocked(prev, null);
}
```
<p>因为应用还未启动过，所以调用startSpecificActivityLocked启动应用，执行逻辑如下:</p>
```java
//ActivityStack类
final boolean resumeTopActivityLocked(ActivityRecord prev, Bundle options) {
  //...
  if (next.app != null && next.app.thread != null) {
    //…
  }else{
    //…
   startSpecificActivityLocked(next, true, true);
  }
 //... 
｝
```
<p>在startSpecificActivityLocked里调用mService.startProcessLocked启动应用:</p>
```java
//ActivityStack类
private final void startSpecificActivityLocked(ActivityRecord r,
            boolean andResume, boolean checkConfig) {
   ProcessRecord app = mService.getProcessRecordLocked(r.processName,
              r.info.applicationInfo.uid);
   //...
   mService.startProcessLocked(r.processName, r.info.applicationInfo, true, 0,
        "activity", r.intent.getComponent(), false, false);
}        
```        
<p>在ActivityManagerService的startProcessLocked方法里:</p>
```java
//ActivityManagerService类
final ProcessRecord startProcessLocked(String processName,
          ApplicationInfo info, boolean knownToBeDead, int intentFlags,
          String hostingType, ComponentName hostingName, boolean allowWhileBooting,
          boolean isolated) {
 ProcessRecord app;
 if (!isolated) {
     app = getProcessRecordLocked(processName, info.uid);
 } else {
     //...
 }
 //...
 if (app == null) {
    app = newProcessRecordLocked(null, info, processName, isolated);
    if (app == null) {
        Slog.w(TAG, "Failed making new process record for "
                + processName + "/" + info.uid + " isolated=" + isolated);
        return null;
    }
    mProcessNames.put(processName, app.uid, app);
    if (isolated) {
        mIsolatedProcesses.put(app.uid, app);
    }
  } else {
   //..
 }
 //...
 startProcessLocked(app, hostingType, hostingNameStr);
 //...
} 
```
<p>在startProcessLocked方法里:</p>
```java
//ActivityManagerService类
private final void startProcessLocked(ProcessRecord app,
        String hostingType, String hostingNameStr) {
  //...
  try {
      //...
      // Start the process.  It will either succeed and return a result containing
  // the PID of the new process, or else throw a RuntimeException.
  //Zygote孵化dalvik应用进程后，会执行android.app.ActivityThread类的main方法
      Process.ProcessStartResult startResult = Process.start("android.app.ActivityThread",
              app.processName, uid, uid, gids, debugFlags, mountExternal,
              app.info.targetSdkVersion, app.info.seinfo, null);
      //...    
  } catch (RuntimeException e) {
      //...
  }
}
```
<p>在Process类的start方法里:</p>
```java
//Process类
public static final ProcessStartResult start(final String processClass,
                              final String niceName,
                              int uid, int gid, int[] gids,
                              int debugFlags, int mountExternal,
                              int targetSdkVersion,
                              String seInfo,
                              String[] zygoteArgs) {
 try{                              
  startViaZygote(processClass, niceName, uid, gid, gids,
                    debugFlags, mountExternal, targetSdkVersion, seInfo, zygoteArgs);
  }catch (ZygoteStartFailedEx ex) {
    //...
  }                    
}                    
```
<p>在Process类的startViaZygote方法里，会计算启动应用进程用的各个参数，然后再调用zygoteSendArgsAndGetResult方法将这些参数通过socket发送给zygote进程，zygote进程会孵化出新的dalvik应用进程，然后告诉ActivityManagerService新启动的进程的pid。</p>

<h2>3. Zygote孵化应用进程</h2>
<p>点击图片可看<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote.png" target="_blank">大图</a></p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/zygote.png" alt="zygote" width="814" height="674" class="aligncenter size-full wp-image-811" /></a>
<p>zygote进程将ZygoteInit作为启动类，会执行它的main方法，先注册ZygoteSocket，然后调用runSelectLoop方法，runSelectLoop方法会调用方法在ZygoteSocket上监听请求，如果别的进程通过ZygoteSocket请求孵化进程，则孵化进程。</p>
<p>runSelectLoop方法的主要代码:</p>
```java
//ZygoteInit类
private static void runSelectLoopMode() throws MethodAndArgsCaller {
  //...
  while (true) {
     //...
      try {
          fdArray = fds.toArray(fdArray);
          index = selectReadable(fdArray);
      } catch (IOException ex) {
          throw new RuntimeException("Error in select()", ex);
      }
      if (index < 0) {
          throw new RuntimeException("Error in select()");
      } else if (index == 0) {
          //监听客户连接请求
          ZygoteConnection newPeer = acceptCommandPeer();
          peers.add(newPeer);
          fds.add(newPeer.getFileDesciptor());
      } else {
         //若客户发送孵化进程的请求过来，
         //此时便需要调用ZygoteConnection的runOnce方法孵化进程
          boolean done;
          done = peers.get(index).runOnce();
          if (done) {
              peers.remove(index);
              fds.remove(index);
          }
      }
  }
}  
```
<p>在runOnce方法里调用Zygote.forkAndSpecialize方法孵化进程，如果返回值为0表示是在孵化出来的应用进程里，此时会调用handleChildProc进行一些处理，并使用异常机制进行逃逸，会直接逃逸至ZygoteInit的main方法。</p>
```java
//ZygoteConnection类
boolean runOnce() throws ZygoteInit.MethodAndArgsCaller {
  //...
  try {
  //...
      pid = Zygote.forkAndSpecialize(parsedArgs.uid, parsedArgs.gid, parsedArgs.gids,
              parsedArgs.debugFlags, rlimits, parsedArgs.mountExternal, parsedArgs.seInfo,
              parsedArgs.niceName);
  } 
  //...
  try {
      if (pid == 0) {
          // in child
          IoUtils.closeQuietly(serverPipeFd);
          serverPipeFd = null;
          //handleChildProc是一个很重要的函数，在该函数里使用了异常进行逃逸
          handleChildProc(parsedArgs, descriptors, childPipeFd, newStderr);
          //...  
      } else {
         //... 
      }
  } finally {
       //...
  }
}
```
<h3>3.1 Zygote.forkAndSpecialize</h3>
<p>Zygote的forkAndSpecialize方法会调用nativeForkAndSpecialize方法孵化进程，nativeForkAndSpecialize是一个本地方法，它的实现在dalvik/vm/native/dalvik_system_Zygote.cpp里，在该cpp文件里与nativeForkAndSpecialize对应的C++方法是Dalvik_dalvik_system_Zygote_forkAndSpecialize，在该方法里会调用forkAndSpecializeCommon孵化进程,在forkAndSpecializeCommon方法里会调用fork系统调用创建进程，因为使用的是fork机制所以创建进程的效率比较高。</p>
<h3>3.2 handleChildProc</h3>
<p>handleChildProc方法主要代码:</p>
```java
//ZygoteConnection类
private void handleChildProc(Arguments parsedArgs,
            FileDescriptor[] descriptors, FileDescriptor pipeFd, PrintStream newStderr)
            throws ZygoteInit.MethodAndArgsCaller {
  //...
  if (parsedArgs.runtimeInit) {
  //...
  } else {
      String className;
      try {
          //这里得到的classname实际是android.app.ActivityThread
          className = parsedArgs.remainingArgs[0];
      } catch (ArrayIndexOutOfBoundsException ex) {
          logAndPrintError(newStderr,
                  "Missing required class name argument", null);
          return;
      }
      //...
      if (parsedArgs.invokeWith != null) {
      //...
      } else {
          ClassLoader cloader;
          if (parsedArgs.classpath != null) {
              cloader = new PathClassLoader(parsedArgs.classpath,
                      ClassLoader.getSystemClassLoader());
          } else {
              cloader = ClassLoader.getSystemClassLoader();
          }
          //调用ZygoteInit.invokeStaticMain执行android.app.ActivityThread的main方法        
          try {
              ZygoteInit.invokeStaticMain(cloader, className, mainArgs);
          } catch (RuntimeException ex) {
              logAndPrintError(newStderr, "Error starting.", ex);
          }
      }
  }
}
```
<p>ZygoteInit的invokeStaticMain方法并不会直接执行className的main方法，而是会构造一个 ZygoteInit.MethodAndArgsCaller异常，然后抛出来，通过异常机制会直接跳转到ZygoteInit的main方法, ZygoteInit.MethodAndArgsCaller类实现了Runnable方法，在run方法里会执行要求执行的main方法，故此跳转到ZygoteInit的main方法后，异常会被捕获，然后执行方法caller.run(),这样便会执行android.app.ActivityThread的main方法。</p>
<p>ZygoteInit的invokeStaticMain方法主要代码:</p>
```java
//ZygoteInit类
static void invokeStaticMain(ClassLoader loader,
        String className, String[] argv)
        throws ZygoteInit.MethodAndArgsCaller {
  //...        
  Method m;
  try {
      m = cl.getMethod("main", new Class[] { String[].class });
  } catch(//...){
  }
  //...
  throw new ZygoteInit.MethodAndArgsCaller(m, argv);
}
```
<p>ZygoteInit.MethodAndArgsCaller主要代码:</p>
```java
public static class MethodAndArgsCaller extends Exception
        implements Runnable {
    //...
    public void run() {
        try {
            mMethod.invoke(null, new Object[] { mArgs });
        }//...
    }
}
```

<p>ZygoteInit的main方法相关代码:</p>
```java
//ZygoteInit类
public static void main(String argv[]) {
  try {
      //...
  } catch (MethodAndArgsCaller caller) {
      caller.run();
  } catch (RuntimeException ex) {
      //...
  }
}
```
<p>下面博客将介绍Activity详细启动流程的后半部分。</p> 
