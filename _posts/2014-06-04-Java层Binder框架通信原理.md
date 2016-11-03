---
id: 573
title: Java层Binder框架通信原理
date: 2014-06-04T10:05:24+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=573
permalink: /android/post-573.html
views:
  - 6495
categories:
  - Android
tags:
  - android binder 分析
  - android binder设计与实现
  - Binder Java框架
  - Binder 机制详解
  - framework binder详解
---
<p>上一篇博客介绍了《<a href="http://www.cloudchou.com/android/post-558.html" target="_blank">Binder 机制详解—Binder Java框架</a>》，本篇博客将分析Java层Binder框架通信原理。</p>
<h2>Java层如何获得IServiceManager对象</h2>
<p>我们先看一下Java层的IServiceManager相关类的类图：(若看不清，请点击看大图)</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/06/IServiceManager_class_diagram.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/IServiceManager_class_diagram-1024x690.png" alt="IServiceManager_class_diagram" width="1024" height="690" class="aligncenter size-large wp-image-575" /></a>
<p>我们在Java层象下面一样使用ServiceManager：</p>
```java
//添加binder service
ServiceManager.addService("CloudService", new BServer()); 
//查询binder service
IBinder binder = ServiceManager.getService("CloudService");
```
<p>由类图也可以知道ServiceManager象一个工具类，提供了getServcie，addService，checkService，listService等一系列静态方法。实际上它缓存了一个IServiceManager对象，IServiceManager对象是利用私有的getIServiceManager方法获取的。</p>
<p>getIServiceManager的源码如下所示：</p>
```java
private static IServiceManager getIServiceManager() {
      if (sServiceManager != null) {
          return sServiceManager;
      }

      // Find the service manager
      sServiceManager = ServiceManagerNative.asInterface(
                         BinderInternal.getContextObject());
      return sServiceManager;
  }
```
<p>获得IServiceManager对象的流程图如下图所示(若看不清，请点击看大图)：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/06/getIServiceManager.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/getIServiceManager-1024x668.png" alt="getIServiceManager" width="1024" height="668" class="aligncenter size-large wp-image-577" /></a>
<p>BinderInternal的getContextObject方法是一个本地方法，对应android_util_Binder.cpp的android_os_BinderInternal_getContextObject方法，该方法调用了ProcessState:self()->getContextObject(NULL)，这个方法我们在《<a href="http://www.cloudchou.com/android/post-534.html" target="_blank">Binder 机制详解—重要函数调用流程分析</a>》已经分析过，它会返回一个IBinder指针，IBinder对象实际类型是BpBinder。然后它调用了javaObjectForIBinder方法，该方法我们在上一篇博客《<a href="http://www.cloudchou.com/android/post-558.html" target="_blank">Binder 机制详解—Binder Java框架</a>》已经分析过，主要作用是建立一个Java层的BinderProxy对象，并封装了一个本地的BpBinder指针。</p>
<p>getIServiceManager方法接下来调用ServiceManagerNative.asInterface方法将IBinder对象转为IServiceManager对象，ServiceManagerNative.asInterface方法源码如下所示：</p>
```java
static public IServiceManager asInterface(IBinder obj)
{
    if (obj == null) {
        return null;
    }
    IServiceManager in =
        (IServiceManager)obj.queryLocalInterface(descriptor);
    if (in != null) {
        return in;
    }
    
    return new ServiceManagerProxy(obj);
}
```
<p>我们已经知道IBinder对象的实际类型是BinderProxy，它的queryLocalInterface方法源码如下所示：</p>
```java
public IInterface queryLocalInterface(String descriptor) {
        return null;
}
```
<p>故此最终新建了一个ServiceManagerProxy对象，并封装了一个BinderProxy对象，而BinderProxy对象封装了一个本地的BpBinder对象指针。</p>
<p>这样我们知道getIServiceManager方法返回的IServiceManager对象的实际类型是ServiceManagerProxy。</p>

<h2>Java层如何获得IBinder接口对象</h2>
<p>我们在Java层象下面一样获得IBinder接口对象:</p>
<p>IBinder binder = ServiceManager.getService("CloudService");//查询binder service</p>
<p>Java层获得IBinder接口对象的流程：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/06/getIBinder.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/getIBinder-1024x690.png" alt="getIBinder" width="1024" height="690" class="aligncenter size-large wp-image-579" /></a>
<p>从上一节"Java层如何获得IServiceManager对象"，我们已经知道getIServiceManager方法返回的IServiceManager对象的实际类型其实是ServiceManangerProxy，该类会先调用mRemote.transact方法，而mRemote的实际类型其实是BinderProxy，它封装了一个本地层的BpBinder对象。BinderProxy的transact方法是一个本地方法，对应android_util_Binder.cpp的android_os_BinderProxy_transact方法，它会调用target的transact方法，target的类型是IBinder，实际类型是BpBinder，故此最终会调用BpBinder的transact方法，我们在《<a href="http://www.cloudchou.com/android/post-534.html" target="_blank">Binder 机制详解—重要函数调用流程分析</a>》已经深入分析过BpBinder的transact方法，这里不再赘述。</p>
<p>getSevcice方法调用完transact方法后，便收到了从binder service服务端发过来的数据，将这些数据保存在Parcel类型的reply对象里，然后调用Parcel的方法来解析这些数据。先调用Parcel的readStrongBinder方法，该方法会调用nativeReadStrongBinder，这是一个本地方法，对应android_util_binder.cpp的android_os_Parcel_readStrongBinder方法，该方法会先将nativePtr转为本地的Parcel指针，由此可知Java类型Parce其实封装了一个本地类型Parcel。然后再调用本地Parcel的readStrongBinder方法，我们已经在《<a href="http://www.cloudchou.com/android/post-507.html" target="_blank">Binder系统架构</a>》中分析过该方法，不再赘述。本地Parcel的readStrongBinder方法会返回一个本地IBinder指针，实际类型是BpBinder。接下来会调用javaObjectForBinder方法将本地IBinder指针转为javaobject，此时调用了env->NewObject(gBinderProxyOffsets.mClass, gBinderProxyOffsets.mConstructor)，由此可知其实是新建了一个BinderProxy对象。</p>
<p>通过上述介绍，我们知道Java层通过ServiceMananger的getService方法获得的IBinder接口对象实际类型是BinderProxy。</p>
 
<h2>Java层binder的数据流动</h2>
<p>首先我们先分析框架层如何启动binder service服务线程。</p>
<p>《<a href="http://www.cloudchou.com/android/post-447.html" target="_blank">Binder service入门—Framework binder service</a>》里binder service服务端启动脚本bserver如下所示：</p>
```bash
base=/system
export CLASSPATH=$base/framework/bserver.jar
#调用app_process启动BServer
exec app_process $base/bin com.cloud.test.BServer "$@"
```
<p>由此可知道其实是执行app_process程序 ，参数1为父目录/system/bin，参数2为要执行的java类，参数3为其它命令行参数。</p>
<p>app_process启动流程如下(若看不清，请点击看大图)：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/06/app_process1.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/app_process1.jpg" alt="app_process" width="655" height="942" class="aligncenter size-full wp-image-586" /></a>
<p>app_process程序源码是frameworks/base/cmds/app_process/app_main.cpp，main函数执行时会调用runtime.start启动java层的类RuntimeInit。runtime的类型是AndroidRuntime，实际类型是AndroidRuntime的子类AppRuntime。Java层RuntimeInit启动时也是先执行main函数，调用了commonInit函数和nativeFinishInit函数，而nativeFinishInit函数是一个本地函数，对应AndroidRuntime.cpp的jni函数com_android_internal_os_RuntimeInit_nativeFinishInit，该函数会调用gCurRuntime->onStarted，而gCurRuntime的实际类型便是AppRuntime，故此会执行AppRuntime的onStarted方法，在该方法里会调用proc->startThreadPool，在《<a href="http://www.cloudchou.com/android/post-507.html" target="_blank">Binder 机制详解—Binder 系统架构</a>》我们已经详细分析过ProcessState的startThreadPool方法，它会启动一个PoolThread线程，该线程会直接和binder驱动交互，等待客户端请求的到来，收到请求后再转发给binder service服务端实体对象，由它处理请求。</p>
<p>我们看一下Java层binder service的数据流动，示意图如下所示(若看不清，请点击看大图)：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder.jpg" alt="java_binder" width="1018" height="849" class="aligncenter size-full wp-image-587" /></a>
<p>在《<a href="http://www.cloudchou.com/android/post-447.html" target="_blank">Binder service入门—Framework binder service</a>》里我们已经看到客户端实现接口方法时都是通过调用mRemote.trasact向服务端提交请求来实现的，根据先前的分析我们知道mRemote的类型是IBinder，实际类型是BinderProxy。BinderProxy的transact方法其实是本地方法，对应android_util_Binder.cpp里的android_os_BinderProxy_transact方法，先前我们已经分析知道BinderProxy其实封装了一个BpBinder指针的字段，故此可通过该字段转为IBinder指针，然后调用它的transact方法，其实执行的是BpBinder.transact方法，在《<a href="http://www.cloudchou.com/android/post-534.html" target="_blank">Binder 机制详解—重要函数调用流程分析</a>》我们已经分析了该方法的执行流程，最终会通过ioctl与binder驱动交互，将请求转交给binder service的服务端。</p>
<p>我们在分析框架层如何启动binder service服务线程时已知道会调用ProcessState的startThreadPool方法，它会启动一个PoolThread线程，该线程会直接和binder驱动交互，等待客户端请求的到来，收到请求后会转发给binder service服务端实体对象。其实是转调BBinder的onTrasact方法，这里的实际类型是JavaBBinder，故此执行JavaBBinder的onTrasact方法，该方法会执行jboolean res = env->CallBooleanMethod(mObject, gBinderOffsets.mExecTransact, code, (int32_t)&data, (int32_t)reply, flags);这里的mExecTransact方法其实是Java层Binder的execTransact方法，execTransact方法又会调用Binder的onTransact方法，Binder的子类Binder服务实现类会覆盖onTransact方法，并在onTransact方法里根据不同的code调用不同的接口方法，然后将返回值写入返回数据对象里。</p>
<p>通过上述介绍我们便可清晰的认识Java层binder的数据流动。</p>
