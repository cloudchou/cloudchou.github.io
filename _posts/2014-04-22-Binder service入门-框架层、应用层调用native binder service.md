---
id: 468
title: Binder service入门—框架层、应用层调用native binder service
date: 2014-04-22T01:21:15+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=468
permalink: /android/post-468.html
views:
  - 8608
categories:
  - Android
tags:
  - android binder example
  - android binder 使用
  - android binder 入门
  - android binder 实例
  - android 框架层调用底层binder service
---
<h2>1.前言</h2>
<p>上一篇介绍了如何创建应用层binder service，本篇将综合先前介绍的native binder service，framework binder service，应用层binder service等知识，讲述如何使用native 的client，framework层的client，应用层的client测试native binder service。</p>

<p>Binder service入门系列：</p>  
<ul>
<li>Binder service入门–创建native binder service:<br/> <a href="http://www.cloudchou.com/android/post-332.html" target="_blank">http://www.cloudchou.com/android/post-332.html</a></li>
<li>Binder service入门—Framework binder service:<br/> <a href="http://www.cloudchou.com/android/post-447.html" target="_blank">http://www.cloudchou.com/android/post-447.html</a></li>
<li>Binder service入门—应用层binder service: <br/><a href="http://www.cloudchou.com/android/post-458.html" target="_blank">http://www.cloudchou.com/android/post-458.html</a></li>
</ul>   


<h2>2.程序构成</h2>
<p>因为编译native的binder service，framework层的client都需要在源码环境下编译，故此本篇讲述的工程需要在源码环境下编译。</p>
<p>整个工程可以在github上下载： </p>
<p><a href="https://github.com/cloudchou/NativeBinderJavaClientDemo" target="_blank">https://github.com/cloudchou/NativeBinderJavaClientDemo</a></p>
<p>程序由4个部分组成：</p>

1)    native_bserver 创建并注册native binder service的本地服务端
2)    native_bclient 测试native binder service的本地客户端
3)    fclient和fclient.jar测试native binder service的框架层客户端
4)    NativeBinderServiceTest 测试native  binder service的应用层客户端


<h2>3.程序源码构成</h2>
<p>源程序目录结构如下所示：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest_f.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest_f.png" alt="nativetest_f" width="451" height="708" class="alignnone size-full wp-image-472" /></a>
<p>顶层Android.mk只是简单包含各个子目录的Android.mk，BServer目录存放本地服务端和本地客户端源码，FClient存放框架层客户端源码，NatviveBinderServiceTest存放应用层客户端源码。</p>

<h3>本地服务端和本地客户端</h3>


 <h3>1)    BServer的Android.mk源码如下所示：</h3>
```make
LOCAL_PATH := $(call my-dir)
 
#生成binder service的本地服务端
include $(CLEAR_VARS)
LOCAL_SHARED_LIBRARIES := \\
    libcutils \\
    libutils \\
    libbinder       
LOCAL_MODULE    := native_bserver
LOCAL_SRC_FILES := \\
    ICloudManager.cpp \\
    TestServer.cpp   
LOCAL_MODULE_TAGS := optional
include $(BUILD_EXECUTABLE)
 
#生成binder service的本地客户端
include $(CLEAR_VARS)
LOCAL_SHARED_LIBRARIES := \\
    libcutils \\
    libutils \\
    libbinder
LOCAL_MODULE    := native_bclient
LOCAL_SRC_FILES := \\
    ICloudManager.cpp \\
    TestClient.cpp
LOCAL_MODULE_TAGS := optional
include $(BUILD_EXECUTABLE)
 ```
  


 <h3>2)    binder service接口ICloudManager(ICloudManager.h)： </h3>
```cpp
namespace android
{
    class ICloudManager : public IInterface
    {
    public:
        DECLARE_META_INTERFACE(CloudManager); // declare macro
        virtual void test()=0;
        virtual void print(const char* str)=0;
        virtual int add(int a, int b)=0;
    };

    enum
    {
        TEST = IBinder::FIRST_CALL_TRANSACTION+1,
        PRINT = IBinder::FIRST_CALL_TRANSACTION+2,
        ADD = IBinder::FIRST_CALL_TRANSACTION+3,
    };

    class BpCloudManager: public BpInterface<ICloudManager> {
    public:
        BpCloudManager(const sp<IBinder>& impl);
        virtual void test();
        virtual void print(const char* str);
        virtual int add(int a, int b);
    };
}
```
  


 <h3>3)    实现实现ICloudManager接口的方法(ICloudManager.cpp)</h3>
```cpp
namespace android
{
    IMPLEMENT_META_INTERFACE(CloudManager, "com.cloud.test.ICloudManager");
}
```
 


 <h3>4)    实现服务端(TestServer.cpp)</h3>
```cpp
 namespace android
{
     //binder service 实体类
    class BnCloudManager : public BnInterface<ICloudManager>
    {
    public:
        virtual status_t
        onTransact(uint32_t code, const Parcel& data, Parcel* reply, uint32_t flags = 0);
        virtual void   test();
        virtual void   print(const char* str);
        virtual int   add(int a, int b);
    };

    status_t
    BnCloudManager::onTransact(uint_t code, const Parcel& data, Parcel* reply, uint32_t flags) {
        switch (code)
            {
        case TEST:
            {
                CHECK_INTERFACE(ICloudManager, data, reply);
                test();
                reply->writeInt32(0);
                return NO_ERROR;
            }
            break;
        case PRINT:
            {
                CHECK_INTERFACE(ICloudManager, data, reply);
                String16 str = data.readString16();
                String8 str8 = String8(str);
                print(str8.string());
                reply->writeInt32(0);
                return NO_ERROR;
            }
            break;
        case ADD:
            {
                CHECK_INTERFACE(ITest, data, reply);
                int a;
                int b;
                data.readInt32(&a);
                data.readInt32(&b);
                int c = add(a,b);
                reply->writeInt32(0);
                reply->writeInt32(c);
                return NO_ERROR;
            }
            break;
        default:
            break;
            }
        return NO_ERROR;
    }

    void
    BnCloudManager::test() {
        printf("Now server receive requset from client: [call test]\\n");
    }

    void
    BnCloudManager::print(const char* str) {
        printf("Now server receive requset from client: [call print %s]\\n", str);
    }

    int
    BnCloudManager::add(int a, int b) {
        printf("Now server receive requset from client: [call add %d %d]\\n", a, b);
        return a + b;
    }

}
int
main() {
    sp<ProcessState> proc(ProcessState::self());
sp<IServiceManager> sm = defaultServiceManager();
//注册binder service
    sm->addService(String16("cloudservice"), new BnCloudManager());
    printf("Native binder server starts to work\\n");
    ProcessState::self()->startThreadPool();
    IPCThreadState::self()->joinThreadPool();
    return 0;
}
```
 


 <h3>5)    实现客户端(TestClient.cpp)</h3>
```cpp
namespace android
{
    BpCloudManager::BpCloudManager(const sp<IBinder>& impl) :
            BpInterface<ICloudManager>(impl) {
    }
    void
    BpCloudManager::test() {
        printf("Client call server test method\\n");
        Parcel data, reply;
        data.writeInterfaceToken(ICloudManager::getInterfaceDescriptor());
        remote()->transact(TEST, data, &reply);
        int code = reply.readExceptionCode();
        printf("Server exepction code: %d\\n", code);
    }

    void
    BpCloudManager::print(const char* str) {
        printf("Client call server print method\\n");
        Parcel data, reply;
        data.writeInterfaceToken(ICloudManager::getInterfaceDescriptor());
        data.writeString16(String16(str));
        remote()->transact(PRINT, data, &reply);
        int code = reply.readExceptionCode();
        printf("Server exepction code: %d\\n", code);
    }

    int
    BpCloudManager::add(int a, int b) {
        printf("Client call server add method\\n");
        Parcel data, reply;
        data.writeInterfaceToken(ICloudManager::getInterfaceDescriptor());
        data.writeInt32(a);
        data.writeInt32(b);
        remote()->transact(ADD, data, &reply);
        int code = reply.readExceptionCode();
        int result;
        reply.readInt32(&result);
        printf("Server exepction code: %d\\n", code);
        return result;
    }

}

int
main() {
sp<IServiceManager> sm = defaultServiceManager();
//查询服务
sp<IBinder> binder = sm->getService(String16("cloudservice"));
//转换接口
sp<ICloudManager> cs = interface_cast<ICloudManager>(binder);
//测试接口方法
    cs->test();
    cs->print("Hello world");
    int result=cs->add(2,3);
    printf("client receive add result from server : %d\\n",result);
    return 0;
}
```
 

 

<h3>框架层客户端</h3>


 <h3>1)    Android.mk</h3>
```make
LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)
#生成fclient.jar
LOCAL_SRC_FILES := $(call all-subdir-java-files)
LOCAL_MODULE := fclient 
LOCAL_MODULE_TAGS := optional
include $(BUILD_JAVA_LIBRARY)
#生成fclient
include $(CLEAR_VARS)
LOCAL_MODULE := fclient
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_PATH := $(TARGET_OUT)/bin
LOCAL_MODULE_CLASS := UTILITY_EXECUTABLES
LOCAL_SRC_FILES := fclient
include $(BUILD_PREBUILT)
```


 <h3>2)    定义接口类(ICloudManager.java)</h3>
```java
public interface ICloudManager extends IInterface {
    //接口描述字符串
    static final java.lang.String DESCRIPTOR = "com.cloud.test.ICloudManager";

    void test() throws RemoteException;

    void print(String str) throws RemoteException;

    int add(int a, int b) throws RemoteException;

    static final int TRANSACTION_test = (android.os.IBinder.FIRST_CALL_TRANSACTION + 1);
    static final int TRANSACTION_print = (android.os.IBinder.FIRST_CALL_TRANSACTION + 2);
    static final int TRANSACTION_add = (android.os.IBinder.FIRST_CALL_TRANSACTION + 3);
}
```


 <h3>3)    定义接口代理类(CloudManagerProxy.java)</h3>
```java
public class CloudManagerProxy implements ICloudManager {
    private android.os.IBinder mRemote;

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
        int result = 0;
        try {
            _data.writeInterfaceToken(DESCRIPTOR);
            _data.writeInt(a);
            _data.writeInt(b);
            mRemote.transact(TRANSACTION_add, _data, _reply, 0);
            _reply.readException();
            result = _reply.readInt();
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

    @Override
    public void test() throws RemoteException {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain(); 
        try {
            _data.writeInterfaceToken(DESCRIPTOR); 
            mRemote.transact(TRANSACTION_test, _data, _reply, 0);
            _reply.readException(); 
        } finally {
            _reply.recycle();
            _data.recycle();
        }

    }
}
```


 <h3>4)    客户端(FClient.java)</h3>
```java
public class FClient { 

    /**
     * Command-line entry point.
     * 
     * @param args
     *            The command-line arguments
     * @throws RemoteException
     */
    public static void main(String[] args) throws RemoteException {
        System.out.println("==========Client starts===========");
        IBinder binder = ServiceManager.getService("cloudservice");
        ICloudManager manager = new CloudManagerProxy(binder);
        System.out.println("========== client call server  test ===========");
        manager.test();
        System.out.println("========== client call server print ===========");
        manager.print("Hello world");
        System.out.println("========== client call server add ===========");
        int result = manager.add(2, 3);
        System.out.println("manager.add(2, 3)=" + result);
    }
}
```


 <h3>5)    客户端脚本fclient</h3>
```bash
# Script to start "am" on the device, which has a very rudimentary
# shell.
#
base=/system
export CLASSPATH=$base/framework/fclient.jar
exec app_process $base/bin com.cloud.test.FClient "$@"
```



<h3>应用层客户端</h3>
<p>先前我们有讲到在应用层是不能直接使用ServiceManager这个类的，因为Sdk并未包含该类，应用层只能通过bind service去使用binder service，但是我们的native service并不是使用应用层的Service子类创建的，这样看来貌似应用层不能使用native的binder service。</p>
<p>这里介绍一个技巧，其实我们的应用在运行时可以使用系统隐藏的类，比如ServiceManager，SystemProperties，只是编译时Sdk并未提供这些类，我们若使用这些类就无法编译。但是我们可以创建这些类所在的包，并创建这些类，在类里定义我们要使用的那些方法，我们就可以通过编译了。比如ServiceManager这个类，我们就可以为之创建android.os这个package，并在这个package下创建ServiceManager类，定义我们需要的方法getService。也许读者会担心运行时使用的ServiceManger类就是我们创建的ServiceManager类，但实际上运行时使用的ServiceManager类是framework.jar里的ServiceManager类，这是因为classloader在查找类时优先使用系统的类。</p>


<h3>1)    Android.mk</h3>
```make
LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE_TAGS := optional

LOCAL_STATIC_JAVA_LIBRARIES := android-support-v13
LOCAL_STATIC_JAVA_LIBRARIES += android-support-v4

LOCAL_SRC_FILES := $(call all-java-files-under, src)

LOCAL_PACKAGE_NAME := NativeBinderServiceTest  
#LOCAL_PROGUARD_FLAG_FILES := proguard.flags

include $(BUILD_PACKAGE)

# Use the following include to make our test apk.
include $(call all-makefiles-under,$(LOCAL_PATH)) 
```


<h3>2)    我们创建的ServiceManager源码</h3>
```java
public class ServiceManager {

    public static IBinder getService(String name) {
        return null;
    }

} 
```


<h3>3)    定义接口ICloudManager</h3>
```java
public interface ICloudManager extends IInterface {
    static final java.lang.String DESCRIPTOR = "com.cloud.test.ICloudManager";

    void test() throws RemoteException;

    void print(String str) throws RemoteException;

    int add(int a, int b) throws RemoteException;

    static final int TRANSACTION_test = (android.os.IBinder.FIRST_CALL_TRANSACTION + 1);
    static final int TRANSACTION_print = (android.os.IBinder.FIRST_CALL_TRANSACTION + 2);
    static final int TRANSACTION_add = (android.os.IBinder.FIRST_CALL_TRANSACTION + 3);
} 
```


<h3>4)    定义代理类CloudManagerProxy</h3>
```java
public class CloudManagerProxy implements ICloudManager {
    private android.os.IBinder mRemote;

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
        int result = 0;
        try {
            _data.writeInterfaceToken(DESCRIPTOR);
            _data.writeInt(a);
            _data.writeInt(b);
            mRemote.transact(TRANSACTION_add, _data, _reply, 0);
            _reply.readException();
            result = _reply.readInt();
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

    @Override
    public void test() throws RemoteException {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain(); 
        try {
            _data.writeInterfaceToken(DESCRIPTOR); 
            mRemote.transact(TRANSACTION_test, _data, _reply, 0);
            _reply.readException(); 
        } finally {
            _reply.recycle();
            _data.recycle();
        }

    }

} 
```


<h3>5)    测试用的Activity(TestAc.java)</h3>
```java
public class TestAc extends Activity {

    private static final String TAG = TestAc.class.getSimpleName();
    private ICloudManager manager = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        Log.d(TAG, "[ThreadId " + Thread.currentThread().getId() 
                  + "] [ProcessId" + Process.myPid() + "]  onCreate");
        findViewById(R.id.btn_print).setOnClickListener(
          new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    Log.d(TAG, "=========== Client call CloudService"
                               +" print function");
                    manager.print("Hello world");
                } catch (RemoteException e) {
                    e.printStackTrace();
                }
            }
        });
        findViewById(R.id.btn_add).setOnClickListener(
        new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    Log.d(TAG, "======Client call CloudService"
                               +" add function");
                    int a = manager.add(3, 2);
                    Log.d(TAG, "======Client add function reuslt : "
                                + a);
                } catch (RemoteException e) {
                    e.printStackTrace();
                }
            }
        });
        findViewById(R.id.btn_test).setOnClickListener(
          new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try {
                    Log.d(TAG, "======Client call CloudService"
                               +" test function");
                    manager.test();
                } catch (RemoteException e) {
                    e.printStackTrace();
                }
            }
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
        IBinder binder = ServiceManager.getService("cloudservice");
        manager = new CloudManagerProxy(binder);
        findViewById(R.id.btn_print).setEnabled(true);
        findViewById(R.id.btn_add).setEnabled(true);
        findViewById(R.id.btn_test).setEnabled(true);
    }

    @Override
    protected void onStop() {
        super.onStop();
    }

    @Override
    protected void onDestroy() {

        super.onDestroy();

    }
} 
```



<h2>4.测试</h2>
<p>上传程序：</p> 
```text
adb push native_bclient /system/bin
adb push native_bserver /system/bin
adb push fclient /system/bin
adb push fclient.jar /system/framework
adb shell chmod 755 /system/bin/native_bserver
adb shell chmod 755 /system/bin/native_bclient
adb shell chmod 755 /system/bin/fclient
```
<p>使用native_client测试：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest.png"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/nativetest.png" alt="nativetest" width="873" height="246" class="alignnone size-full wp-image-480" /></a>
<p>使用框架层的client测试：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/frameworktest.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/frameworktest.png" alt="frameworktest" width="989" height="204" class="alignnone size-full wp-image-476" /></a>
<p>使用应用层的client测试：</p> 
<p>服务端： </p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_server.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_server.png" alt="apptest_server" width="621" height="213" class="alignnone size-full wp-image-478" /></a>
<p>客户端：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_client.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/apptest_client.png" alt="apptest_client" width="781" height="165" class="alignnone size-full wp-image-477" /></a>
