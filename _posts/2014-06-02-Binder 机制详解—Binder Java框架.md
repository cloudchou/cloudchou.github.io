---
id: 558
title: Binder 机制详解—Binder Java框架
date: 2014-06-02T23:29:14+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=558
permalink: /android/post-558.html
views:
  - 9500
categories:
  - Android
tags:
  - android binder机制
  - android binder设计与实现
  - android service binder
  - Binder Java框架
  - Binder 机制详解
---
<p>上一篇博客介绍了 Binder本地框架层，本篇博客将介绍Binder的java层框架。</p>

<h2>Binder的java层框架</h2>
<p>Binder的Java框架层包含以下类(frameworks/base/core/java/android/os):IBinder，Binder，IInterface，ServiceManagerNative，ServiceManager，BinderInternal，IServiceManager，ServiceManagerProxy。</p>
<p>Binder的Java框架层部分方法的实现在本地代码里，源码位于frameworks/base/core/jni。</p>
<p>先前博客《<a href="http://www.cloudchou.com/android/post-447.html" target="_blank">Binder service入门—Framework binder service</a>》中ICloudMananger与Binder Java 框架层的类图如下图所示(若看不清，请点击看大图):</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder_framework.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/java_binder_framework-1024x702.png" alt="java_binder_framework" width="1024" height="702" class="aligncenter size-large wp-image-560" /></a>
<p>与Binder本地框架类似，声明的binder service接口必须继承自IInterface，这里ICloudManager继承自IInterface。与Binder 本地框架层不相同的是，Java层的IBinder接口直接继承自IInterface，而本地的IBinder类继承自RefBase。本地的IBinder有两个子类，BBinder和BpBinder，Java层的IBinder接口也有两个子类，Binder和BinderProxy。Java层服务端的CloudManager (binder service实体类) 直接继承自Binder类，并实现了binder service接口ICloudManager，而客户端的CloudManagerProxy类只需实现binder service接口ICloudManager即可。</p>
<h2>Binder java层框架相关 Jni源码</h2>
<p>Binder Java层框架类有不少方法是native的，意味着这些native方法是jni方法。Java层框架中的类Binder，BinderProxy，BinderInternal的native方法的实现是在源码frameworks/base/core/jni/android_util_Binder.cpp里，Java层框架中Parcel类native方法的实现是在frameworks/base/core/jni/android_os_Parcel.cpp里。接下来我们将详细分析android_util_Binder.cpp。</p>
<h3>重要数据结构</h3>
<ul>
<li>
 <h3>1)gBinderOffsets，代表android.os.Binder 类</h3>
```cpp
static struct bindernative_offsets_t
{
    // 指向class对象android.os.Binder 
    jclass mClass;
    //指向 android.os.Binder的execTransact方法
    jmethodID mExecTransact;

    //指向android.os.Binder的mObject字段，
    //将用于保存指向JavaBBinderHolder对象的指针
    jfieldID mObject;

} gBinderOffsets;
``` 
</li>
<li>
 <h3>2)gBinderInternalOffsets，代表com.android.internal.os.BinderInternal类</h3>
```cpp
static struct binderinternal_offsets_t
{
    //指向 class对象com.android.internal.os.BinderInternal
    jclass mClass;
    //指向BinderInternal的forceGc方法
    jmethodID mForceGc;

} gBinderInternalOffsets; 
```

</li>
<li>
 <h3>3)binderproxy_offsets_t，代表android.os.BinderProxy类</h3>
```cpp
static struct binderproxy_offsets_t
{
    //指向 class对象android.os.BinderProxy
    jclass mClass;
    //指向 BinderProxy的构造方法
    jmethodID mConstructor;
    //指向 BinderProxy的sendDeathNotice方法
    jmethodID mSendDeathNotice;

    //指向 BinderProxy的mObject字段
    jfieldID mObject;
    //指向 BinderProxy的mSelf字段
    jfieldID mSelf;
    //指向 BinderProxy的mOrgue字段
    jfieldID mOrgue;

} gBinderProxyOffsets;
``` 
</li>
<li>
 <h3>4)JavaBBinder和JavaBBinderHolder</h3>
<p>JavaBBinder和JavaBBinderHolder相关类类图如下所示(若看不清，请点击看大图)，JavaBBinder继承自本地框架的BBinder，代表binder service服务端实体，而JavaBBinderHolder保存JavaBBinder指针，Java层Binder的mObject保存的是JavaBBinderHolder指针的值，故此这里用聚合关系表示。BinderProxy的mObject保存的是BpBinder对象指针的值，故此这里用聚合关系表示。</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/06/binder_java_jni.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/binder_java_jni-1024x687.png" alt="binder_java_jni" width="1024" height="687" class="aligncenter size-large wp-image-561" /></a>
</li>
</ul>

<h3>重要函数</h3>
<ul>
<li>
 <h3>1)javaObjectForIBinder 将本地IBinder对象转为Java层的IBinder对象，实际类型是BinderProxy</h3>
```cpp
jobject javaObjectForIBinder(JNIEnv* env, const sp<IBinder>& val)
{
    if (val == NULL) return NULL;

    //如果是 binder 服务端进程调用javaObjectForIBinder 
    //将调用JavaBBinder的object方法返回jobject，
    //这里jobject的实际Java类型是Binder
    if (val->checkSubclass(&gBinderOffsets)) {
        // One of our own!
        jobject object = static_cast<JavaBBinder*>(val.get())->object();
        LOGDEATH("objectForBinder %p: it's our own %p!\\n", val.get(),
                 object);
        return object;
    }
    //如果是binder客户端进程，则需要返回Java层的BinderProxy对象
    
    // For the rest of the function we will hold this lock, to serialize
    // looking/creation of Java proxies for native Binder proxies.
    AutoMutex _l(mProxyLock);

    // 如果已有用Java层WeakReference保存的BinderProxy对象，则返回该对象
    jobject object = (jobject)val->findObject(&gBinderProxyOffsets);
    if (object != NULL) {
        jobject res = env->CallObjectMethod(object, 
                          gWeakReferenceOffsets.mGet);
        if (res != NULL) {
            ALOGV("objectForBinder %p: found existing %p!\\n", val.get(),
                   res);
            return res;
        }
        LOGDEATH("Proxy object %p of IBinder %p no longer 
                  in working set!!!", object, val.get());
        android_atomic_dec(&gNumProxyRefs);
        val->detachObject(&gBinderProxyOffsets);
        env->DeleteGlobalRef(object);
    }

    //创建BinderProxy对象
    object = env->NewObject(gBinderProxyOffsets.mClass, 
                 gBinderProxyOffsets.mConstructor);
    if (object != NULL) {
        LOGDEATH("objectForBinder %p: created new proxy %p !\\n",
            val.get(), object);
        // The proxy holds a reference to the native object.
        //设置BinderProxy对象的mObject字段为本地IBinder对象指针，
        //本地IBinder对象的实际类型是BpBinder
        env->SetIntField(object, gBinderProxyOffsets.mObject, 
               (int)val.get());
        val->incStrong(object);

        // The native object needs to hold a weak reference back to the
        // proxy, so we can retrieve 
        //the same proxy if it is still active.
        jobject refObject = env->NewGlobalRef(
                env->GetObjectField(object, gBinderProxyOffsets.mSelf));
        //关联gBinderProxyOffsets，故此第20行代码用findObject才能找到      
        val->attachObject(&gBinderProxyOffsets, refObject,
                jnienv_to_javavm(env), proxy_cleanup);

        // Also remember the death recipients registered on this proxy
        sp<DeathRecipientList> drl = new DeathRecipientList;
        drl->incStrong((void*)javaObjectForIBinder);
        env->SetIntField(object, gBinderProxyOffsets.mOrgue, 
                    reinterpret_cast<jint>(drl.get()));

        // Note that a new object reference has been created.
        android_atomic_inc(&gNumProxyRefs);
        incRefsCreated(env);
    }

    return object;
}
``` 
 
</li>
<li>
 <h3>2)ibinderForJavaObject 将Java层的IBinder对象转为本地IBinder对象</h3>
```cpp
sp<IBinder> ibinderForJavaObject(JNIEnv* env, jobject obj)
{
    if (obj == NULL) return NULL;

    //如果是Java层Binder对象 
    //则将Binder对象的mObject字段转为JavaBBinderHolder指针
    //然后调用它的get方法即可转为本地IBinder对象，实际类型是JavaBBinder
    if (env->IsInstanceOf(obj, gBinderOffsets.mClass)) {
        JavaBBinderHolder* jbh = (JavaBBinderHolder*)
            env->GetIntField(obj, gBinderOffsets.mObject);
        return jbh != NULL ? jbh->get(env, obj) : NULL;
    }

    //如果是Java层的BinderProxy对象，
    //则将BinderProxy对象的mObject字段直接转为本地的IBinder对象指针
    //实际类型是本地框架里的BpBinder
    if (env->IsInstanceOf(obj, gBinderProxyOffsets.mClass)) {
        return (IBinder*)
            env->GetIntField(obj, gBinderProxyOffsets.mObject);
    }

    ALOGW("ibinderForJavaObject: %p is not a Binder object", obj);
    return NULL;
}
```  
</li>
</ul>

<h3>初始化流程</h3>
<p>Java虚拟机启动时会调用jni方法来注册Java层binder框架的本地方法，流程如下图所示(若看不清请点击看大图)：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/06/jni_funitioons1.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/06/jni_funitioons1-1024x516.jpg" alt="jni_funitioons" width="1024" height="516" class="aligncenter size-large wp-image-571" /></a>
 
