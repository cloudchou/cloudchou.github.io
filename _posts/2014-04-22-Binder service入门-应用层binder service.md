---
     id: 458
     title: Binder service入门—应用层binder service
     date: 2014-04-22T01:20:12+08:00
     author: cloud
     layout: post
     guid: http://www.cloudchou.com/?p=458
     permalink: /android/post-458.html
     views:
       - 5165
     categories:
       - Android
     tags:
       - android binder example
       - android binder 使用
       - android binder 入门
       - android binder 实例
       - android 应用层 binder
     ---
<h2>1.前言</h2>
 <p>Binder service入门系列：</p>  
 <ul>
 <li>Binder service入门–创建native binder service:<br/> <a href="http://www.cloudchou.com/android/post-332.html" target="_blank">http://www.cloudchou.com/android/post-332.html</a></li>
 <li>Binder service入门—Framework binder service:<br/> <a href="http://www.cloudchou.com/android/post-447.html" target="_blank">http://www.cloudchou.com/android/post-447.html</a></li>
 <li>Binder service入门—框架层、应用层调用native binder service:<br/> <a href="http://www.cloudchou.com/android/post-468.html" target="_blank">http://www.cloudchou.com/android/post-468.html</a></li>
 </ul> 
 <p>上一篇介绍了Framework Binder Service，本篇将介绍如何创建应用层的binder service。 实际上在应用层使用binder service时，并没有直接与ServiceManager交互(应用层不能直接使用ServiceManager 类)，一般是在Service子类里覆盖onBind方法，返回新创建的Binder实体对象。应用层使用Activity作为binder service的客户端，在Activity里创建ServiceConnecttion对象，并调用bindService方法绑定service，在ServiceConnection的onServiceConnected方法将接收到的IBinder对象转化为接口对象，然后再通过这个接口对象调用binder service的接口方法。</p>
 
 <h2>2.程序构成</h2>
 <p>程序在应用开发环境下编译。</p>
 <p>整个工程可以在github上下载： <a href="https://github.com/cloudchou/AndroidBinderTest" target="_blank">https://github.com/cloudchou/AndroidBinderTest</a></p>
 <p>本示例使用remote service，声明service时，使用了android:process属性。</p>
 
 <h2>3.程序源码构成</h2>
 <p>源代码结构如下所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/04/app_f.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/app_f.png" alt="app_f" width="284" height="370" class="alignnone size-full wp-image-464" /></a>
 <p>AndroidManifeset.xml：声明用到的activity，service组件</p>
 <p>ICloudManager.aidl： binder service接口</p>
 <p>CloudService: 创建binder service，并返回给客户端</p>
 <p>TestAc: 测试binder service的客户端</p>
 
 <h3>实现应用层 binder service的步骤</h3>
 <ul>
 <li>1)    使用aidl定义binder service接口ICloudManager</li>
 ```text
 package com.cloud.test;
 interface ICloudManager{
     void print(String str) ;
     int add(int a, int b);
 }
 ```
 <p>aidl全称是android interface definition language，用于定义binder service接口，语法与Java的接口非常类似，详情可参考：<a href="http://developer.android.com/guide/components/aidl.html" target="_blank">http://developer.android.com/guide/components/aidl.html</a></p>
 <p>使用eclipse开发时，它会被自动编译成ICloudManager.java，放在gen目录下。生成的ICloudManager.java源码如下所示：</p>
 ```java
 //声明接口ICloudManager 继承自IInterface，这里和在Framework使用binder service类似
 public interface ICloudManager extends android.os.IInterface {
     /**binder service实体类和framework的binder service实体类类似 */
     public static abstract class Stub extends android.os.Binder implements com.cloud.test.ICloudManager {
         private static final java.lang.String DESCRIPTOR = "com.cloud.test.ICloudManager";
 
         /** Construct the stub at attach it to the interface. */
         public Stub() {
             this.attachInterface(this, DESCRIPTOR);
         }
 
         /**
          * Cast an IBinder object into an com.cloud.test.ICloudManager interface, generating a proxy if needed.
          */
         public static com.cloud.test.ICloudManager asInterface(android.os.IBinder obj) {
             if ((obj == null)) {
                 return null;
             }
             android.os.IInterface iin = obj.queryLocalInterface(DESCRIPTOR);
             if (((iin != null) && (iin instanceof com.cloud.test.ICloudManager))) {
                 return ((com.cloud.test.ICloudManager) iin);
             }
             return new com.cloud.test.ICloudManager.Stub.Proxy(obj);
         }
 
         @Override
         public android.os.IBinder asBinder() {
             return this;
         }
 
         @Override
         public boolean onTransact(int code, android.os.Parcel data, android.os.Parcel reply, int flags)
                 throws android.os.RemoteException {
             switch (code) {
             case INTERFACE_TRANSACTION: {
                 reply.writeString(DESCRIPTOR);
                 return true;
             }
             case TRANSACTION_print: {
                 data.enforceInterface(DESCRIPTOR);
                 java.lang.String _arg0;
                 _arg0 = data.readString();
                 this.print(_arg0);
                 reply.writeNoException();
                 return true;
             }
             case TRANSACTION_add: {
                 data.enforceInterface(DESCRIPTOR);
                 int _arg0;
                 _arg0 = data.readInt();
                 int _arg1;
                 _arg1 = data.readInt();
                 int _result = this.add(_arg0, _arg1);
                 reply.writeNoException();
                 reply.writeInt(_result);
                 return true;
             }
             }
             return super.onTransact(code, data, reply, flags);
         }
 
         //binder service的引用类，或者说是代理，和framework使用binder service类似
         private static class Proxy implements com.cloud.test.ICloudManager {
             private android.os.IBinder mRemote;
 
             Proxy(android.os.IBinder remote) {
                 mRemote = remote;
             }
 
             @Override
             public android.os.IBinder asBinder() {
                 return mRemote;
             }
 
             public java.lang.String getInterfaceDescriptor() {
                 return DESCRIPTOR;
             }
 
             @Override
             public void print(java.lang.String str) throws android.os.RemoteException {
                 android.os.Parcel _data = android.os.Parcel.obtain();
                 android.os.Parcel _reply = android.os.Parcel.obtain();
                 try {
                     _data.writeInterfaceToken(DESCRIPTOR);
                     _data.writeString(str);
                     mRemote.transact(Stub.TRANSACTION_print, _data, _reply, 0);
                     _reply.readException();
                 } finally {
                     _reply.recycle();
                     _data.recycle();
                 }
             }
 
             @Override
             public int add(int a, int b) throws android.os.RemoteException {
                 android.os.Parcel _data = android.os.Parcel.obtain();
                 android.os.Parcel _reply = android.os.Parcel.obtain();
                 int _result;
                 try {
                     _data.writeInterfaceToken(DESCRIPTOR);
                     _data.writeInt(a);
                     _data.writeInt(b);
                     mRemote.transact(Stub.TRANSACTION_add, _data, _reply, 0);
                     _reply.readException();
                     _result = _reply.readInt();
                 } finally {
                     _reply.recycle();
                     _data.recycle();
                 }
                 return _result;
             }
         }
 
         static final int TRANSACTION_print = (android.os.IBinder.FIRST_CALL_TRANSACTION + 0);
         static final int TRANSACTION_add = (android.os.IBinder.FIRST_CALL_TRANSACTION + 1);
     }
 
     public void print(java.lang.String str) throws android.os.RemoteException;
 
     public int add(int a, int b) throws android.os.RemoteException;
 }
 ```
 
 <p>由此可见应用层使用binder service实际上和framework使用binder service是非常类似的，只是在应用层使用binder service时，只需编写aidl，开发工具可帮我们自动编译生成java源码文件，该源文件里包含接口，binder service实体类(抽象类，接口方法还未实现)，binder service引用类的源码。</p>
 
 <li>2)    实现Service</li>
 ```java
 public class CloudService extends Service {
   private final static String TAG = CloudService.class.getSimpleName();
   
   //实现binder service实体类
   class CloudMananger extends ICloudManager.Stub {
 
       @Override
       public void print(String str) throws RemoteException {
           Log.d(TAG, "[ThreadId " + Thread.currentThread().getId() 
                      + "] [ProcessId" + Process.myPid()
                      + "]CloudService receive client print msg request: " 
                      + str);
       }
 
       @Override
       public int add(int a, int b) throws RemoteException {
           Log.d(TAG, "[ThreadId " + Thread.currentThread().getId() 
                       + "] [ProcessId" + Process.myPid()
                       + "[CloudService receive client add request : ");
           return a + b;
       }
   }
 
   @Override
   public void onCreate() {
       super.onCreate();
       Log.d(TAG, "[ThreadId " + Thread.currentThread().getId() 
                  + "] [ProcessId" + Process.myPid() + "]  onCreate");
   }
 
  //定义binder service实体类对象
   private CloudMananger manager = new CloudMananger();
   
  //覆盖onBind方法，返回binder service实体类对象
   @Override
   public IBinder onBind(Intent intent) {
       Log.d(TAG, "[ThreadId " + Thread.currentThread().getId() 
                  + "] [ProcessId" + Process.myPid() + "]  onBind");
       return manager;
   }
 
 }
 ```
 
 <li>3)    实现Client</li>
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
                     Log.d(TAG, "=========== Client call "
                                +"CloudService print function");
                     //调用print方法
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
                     Log.d(TAG, "======Client call "
                                +"CloudService add function");
                     int a = manager.add(3, 2);
                     Log.d(TAG, "======Client add function reuslt : " + a);
                 } catch (RemoteException e) {
                     e.printStackTrace();
                 }
             }
         });
     }
 
     @Override
     protected void onStart() {
         super.onStart();
         //绑定 remote service
         Intent intent = new Intent(this, CloudService.class);
         bindService(intent, connection, BIND_AUTO_CREATE);
     }
 
     @Override
     protected void onStop() {
         super.onStop();
         unbindService(connection);
     }
     
     //和remote service绑定时用的ServiceConnection对象
     private ServiceConnection connection = new ServiceConnection() {
 
         @Override
         public void onServiceDisconnected(ComponentName name) {
             Log.d(TAG, "[ThreadId " + Thread.currentThread().getId() 
                        + "] [ProcessId" + Process.myPid()
                        + "]  onServiceDisconnected");
         }
 
         @Override
         public void onServiceConnected(ComponentName name, IBinder service)
         {
             Log.d(TAG, "[ThreadId " + Thread.currentThread().getId() 
                        + "] [ProcessId" + Process.myPid()
                        + "]  onServiceConnected");
             //将IBinder对象转为ICloudManager接口对象，实际上是创建了一个代理对象
             manager = ICloudManager.Stub.asInterface(service);
             findViewById(R.id.btn_print).setEnabled(true);
             findViewById(R.id.btn_add).setEnabled(true);
         }
     };
 
 }
 ```
 
 <li>4)    AndroidManifest.xml，声明程序组件Activity和Service</li>
 ```xml
 <manifest xmlns:android="http://schemas.android.com/apk/res/android"
     package="com.cloud.test"
     android:versionCode="1"
     android:versionName="1.0" >
 
     <uses-sdk
         android:minSdkVersion="15"
         android:targetSdkVersion="15" />
 
     <application
         android:allowBackup="true"
         android:icon="@drawable/ic_launcher"
         android:label="@string/app_name"
         android:theme="@style/AppTheme" >
         <activity android:name=".TestAc" >
             <intent-filter>
                 <action android:name="android.intent.action.MAIN" />
                 <category android:name="android.intent.category.LAUNCHER"/>
             </intent-filter>
         </activity>
         <!—remote service-->
         <service
             android:name=".CloudService"
             android:enabled="true"
             android:process=":remote" />
     </application>
 
 </manifest>
 ```
 
 
 </ul>
 <h2>4.测试</h2>
 <li>运行apk程序：</li>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/04/app_test.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/app_test-1024x229.png" alt="app_test" width="1024" height="229" class="alignnone size-large wp-image-465" /></a>
 
 
  
