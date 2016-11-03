---
id: 447
title: 'Binder service入门—Framework  binder service'
date: 2014-04-22T01:18:53+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=447
permalink: /android/post-447.html
views:
  - 5591
categories:
  - Android
tags:
  - android binder example
  - android binder framework example
  - android binder 使用
  - android binder 入门
  - android binder 实例
---

<h2>1.前言</h2>
<p>上一篇介绍了natvie binder Service，本篇将介绍如何创建框架层binder service，并交给ServiceManager管理，客户端通过ServiceManager获取binder service的引用，然后测试binder service。</p>

<p>Binder service入门系列：</p>  
<ul>
<li>Binder service入门–创建native binder service:<br/> <a href="http://www.cloudchou.com/android/post-332.html" target="_blank">http://www.cloudchou.com/android/post-332.html</a></li>
<li>Binder service入门—应用层binder service: <br/><a href="http://www.cloudchou.com/android/post-458.html" target="_blank">http://www.cloudchou.com/android/post-458.html</a></li>
<li>Binder service入门—框架层、应用层调用native binder service:<br/> <a href="http://www.cloudchou.com/android/post-468.html" target="_blank">http://www.cloudchou.com/android/post-468.html</a></li>
</ul>
 


<h2>2.程序构成</h2>
<p>Framework程序的开发必须要在源码开发环境下，本示例在vendor目录下建立了子目录shuame，然后把工程放在该目录下。</p>
<p>整个工程都可以在github上下载： <a href="https://github.com/cloudchou/FrameworkBinderTest" target="_blank">https://github.com/cloudchou/FrameworkBinderTest</a> </p>
<p>程序由服务端和客户端组成，服务端包括启动服务端的shell脚本bserver和放在framework目录的bserver.jar，客户端包括启动客户端的shell脚本bclient和放在framework目录的bclient.jar。</p> 
<p>服务端 Android.mk如下所示：</p>
```make
LOCAL_PATH:= $(call my-dir)
#生成framwork目录下的库bserver.jar
include $(CLEAR_VARS)
LOCAL_SRC_FILES := $(call all-subdir-java-files)
LOCAL_MODULE := bserver 
LOCAL_MODULE_TAGS := optional
include $(BUILD_JAVA_LIBRARY)
#生成system/bin目录下的shell脚本bserver 
include $(CLEAR_VARS)
LOCAL_MODULE := bserver
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_PATH := $(TARGET_OUT)/bin
LOCAL_MODULE_CLASS := UTILITY_EXECUTABLES
LOCAL_SRC_FILES := bserver
include $(BUILD_PREBUILT)
```
<p>客户端Android.mk如下所示：</p>
```make
LOCAL_PATH:= $(call my-dir)

#生成framwork目录下的库bclient.jar
include $(CLEAR_VARS)
LOCAL_SRC_FILES := $(call all-subdir-java-files)
LOCAL_MODULE := bclient 
LOCAL_MODULE_TAGS := optional
include $(BUILD_JAVA_LIBRARY)

#生成system/bin目录下的shell脚本bclient
include $(CLEAR_VARS)
LOCAL_MODULE := bclient
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_PATH := $(TARGET_OUT)/bin
LOCAL_MODULE_CLASS := UTILITY_EXECUTABLES
LOCAL_SRC_FILES := bclient
include $(BUILD_PREBUILT)
```

<h2>3.程序源码构成</h2>
<p>程序源码构成如下图所示：</p> 
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_fbs.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_fbs-1024x470.png" alt="framework_fbs" width="1024" height="470" class="alignnone size-large wp-image-452" /></a>
<p>整个程序由服务端和客户端两部分组成，分别放在bserver和bclient目录，顶层目录只有一个Android.mk，该Android.mk的内容如下所示：</p>
```make 
#包含所有子目录的makefiles，这样在顶层目录就可以编译所有模块
include $(call all-subdir-makefiles)
```
<p>ICloudManager:服务端和客户端共用同一个接口文件ICloudManager.java，这里通过软链接实现共用，该接口声明了binder service供外界调用的方法。</p>
<p>CloudManager:binder service实体类，接收客户端的调用，进行相关逻辑处理后返回结果给客户端</p>
<p>BServer: 创建CloudManage对象，并调用ServiceManager注册binder service</p>
<p>CloudManagerProxy: binder service引用类，其实是binder service在客户端的代理，客户端通过该类调用服务端的操作</p>
<p>BClient: 测试binder service的客户端，先通过ServiceManager获取binder对象，然后再利用它创建CloudManagerProxy对象，通过CloudManagerProxy对象调用服务端的操</p>

<h3>实现Framework binder service的步骤</h3>

1)   定义binder service接口ICloudManager以及binder service的描述字符串，并为接口里的每个方法声明对应的操作常量：
```java
public interface ICloudManager extends IInterface {
  //binder sevice的描述字符串
  static final java.lang.String DESCRIPTOR = "com.cloud.test.BServer";
  //操作
  public void print(String str) throws RemoteException ;
  public int add(int a, int b) throws RemoteException ;
  //操作常量
  static final int TRANSACTION_print = 
         (android.os.IBinder.FIRST_CALL_TRANSACTION + 0);
  static final int TRANSACTION_add = 
        (android.os.IBinder.FIRST_CALL_TRANSACTION + 1);
}
```
<p>声明binder service接口时必须从IInterface继承，IInterface接口如下所示：</p>
```java
public interface IInterface
{
    /**
     * Retrieve the Binder object associated with this interface.
     * You must use this instead of a plain cast, so that proxy objects
     * can return the correct result.
     */
    public IBinder asBinder();
}
```
<p>IInterface声明了asBinder方法，用于转为Binder对象。</p>
2)   实现binder service实体类CloudManager
```java
public class CloudManager extends Binder implements ICloudManager {  
   public CloudManager() {
      //保存 binder service描述字符串
      this.attachInterface(this, DESCRIPTOR);
   }

   @Override
   public IBinder asBinder() {
      return this;
   }

  //静态方法 转为ICloudManager接口对象
   public static com.cloud.test.ICloudManager asInterface(
         android.os.IBinder obj) {
      if ((obj == null)) {
         return null;
      }
      android.os.IInterface iin = obj.queryLocalInterface(DESCRIPTOR);
      if (((iin != null) && 
          (iin instanceof com.cloud.test.ICloudManager))) {
         return ((com.cloud.test.ICloudManager) iin);
      }
      return null;
   }

  //接收客户端的调用，根据不同的操作码进行不同的处理，然后返回结果给客户端
   @Override
   protected boolean onTransact(int code, Parcel data, 
                            Parcel reply, int flags)
         throws RemoteException {
      switch (code) {
      case INTERFACE_TRANSACTION: {
         reply.writeString(DESCRIPTOR);
         return true;
      }
      case TRANSACTION_print: {
         data.enforceInterface(DESCRIPTOR);
         String str = data.readString();
         print(str);
         reply.writeNoException();
         return true;
      }
      case TRANSACTION_add: {
         data.enforceInterface(DESCRIPTOR);
         int a = data.readInt();
         int b = data.readInt();
         int c = add(a, b);
         reply.writeNoException();
         reply.writeInt(c);
         return true;
      }
      }
      return super.onTransact(code, data, reply, flags);
   }

   @Override
   public void print(String str) {
      System.out.println(str);
   }

   @Override
   public int add(int a, int b) {
      return a + b;
   }
```
<p>注意必须从Binder继承，并实现ICloudManager接口</p>

3)   实现服务端 BServer，创建CloudManager对象，并通过ServiceManager注册服务
```java
public class BServer {
   public static void main(String[] args) {
      System.out.println("Cloud Manager Service Starts");
        //准备Looper
      Looper.prepareMainLooper();         
      android.os.Process.setThreadPriority(
                android.os.Process.THREAD_PRIORITY_FOREGROUND);
        //注册binder service
      ServiceManager.addService("CloudService", new CloudManager());
        //进入Looper死循环，
      Looper.loop();
   }

}
```

4)   实现服务端脚本bserver
```bash
base=/system
export CLASSPATH=$base/framework/bserver.jar
#调用app_process启动BServer
exec app_process $base/bin com.cloud.test.BServer "$@"
```

5)   实现binder service引用类CloudManagerProxy
```java
public class CloudManagerProxy implements ICloudManager {
   private android.os.IBinder mRemote;
    //保存通过ServiceManager查询服务得到的IBinder对象
   public CloudManagerProxy(android.os.IBinder remote) {
      mRemote = remote;
   }

   public java.lang.String getInterfaceDescriptor() {
      return DESCRIPTOR;
   }
 
   @Override
   public void print(String str) throws RemoteException {
      android.os.Parcel _data = android.os.Parcel.obtain();
      android.os.Parcel _reply = android.os.Parcel.obtain();
      try {
         _data.writeInterfaceToken(DESCRIPTOR);
         _data.writeString(str);
         mRemote.transact(TRANSACTION_print, _data, _reply, 0);
         _reply.readException();
      } finally {
         _reply.recycle();
         _data.recycle();
      }
   }

   @Override
   public int add(int a, int b) throws RemoteException {
      android.os.Parcel _data = android.os.Parcel.obtain();
      android.os.Parcel _reply = android.os.Parcel.obtain();
      int result=0;
      try {
         _data.writeInterfaceToken(DESCRIPTOR);
         _data.writeInt(a);
         _data.writeInt(b);
         mRemote.transact(TRANSACTION_add, _data, _reply, 0);
         _reply.readException();
         result=_reply.readInt();
      } finally {
         _reply.recycle();
         _data.recycle();
      }
      return result;
   }

   @Override
   public IBinder asBinder() {
      return mRemote;
   }

} 
```
<p>接口方法的实现实际上是通过调用IBinder对象的transact方法将调用参数传递给服务端，然后读取服务端返回的结果，再返回给接口方法的调用者。</p>

6)   实现客户端BClient
```java
public class BClient { 

   /** 
    * 
    * @param args
    *            The command-line arguments
    * @throws RemoteException
    */
   public static void main(String[] args) throws RemoteException {
      System.out.println("==========Client starts===========");
       //通过ServiceManager查询服务获得IBinder对象
      IBinder binder = ServiceManager.getService("CloudService");
        //创建CloudManagerProxy对象
      ICloudManager manager = new CloudManagerProxy(binder);
        //通过CloudManagerProxy对象调用接口的方法
      manager.print("Hello world");
      int result = manager.add(2, 3);
      System.out.println("manager.add(2, 3)=" + result);
   }
}
```

7)   实现客户端脚本bclient
```bash
base=/system
export CLASSPATH=$base/framework/bclient.jar
#调用app_process启动Bclient
exec app_process $base/bin com.cloud.test.BClient "$@"
```




<h2>4.测试</h2>
<p>编译时若提示错误，缺少framwork之类的jar，可先用mka framework编译framework，编译好之后再使用mm进行模块编译。</p>
<p>编译好之后将相关文件上传至手机并修改权限：</p>
<pre lang="text" line="1">
adb push bserver /system/bin
adb push bclient /system/bin
adb push bserver.jar /system/framework
adb push bclient.jar /system/framework
adb shell chmod 755 /system/bin/bserver
adb shell chmod 755 /system/bin/bclient
```
<p>测试：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_test.png" external_blank><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/framework_test-1024x229.png" alt="framework_test" width="1024" height="229" class="alignnone size-large wp-image-453" /></a>