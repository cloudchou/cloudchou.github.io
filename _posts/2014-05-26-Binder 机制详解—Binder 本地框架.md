---
     id: 547
     title: Binder 机制详解—Binder 本地框架
     date: 2014-05-26T22:48:35+08:00
     author: cloud
     layout: post
     guid: http://www.cloudchou.com/?p=547
     permalink: /android/post-547.html
     views:
       - 11145
     categories:
       - Android
     tags:
       - android binder机制
       - android binder设计与实现
       - android service binder
       - Binder 本地框架
       - Binder 机制详解
     ---
<p>上一篇博客介绍了Binder系统架构，其中说到Binder框架，本地层和Java层各自有一套实现。本篇博客将介绍Binder本地框架。</p> 
 <h2>Binder本地框架</h2>
 <p>本地Binder框架包含以下类(frameworks/native/libs/binder)：</p>
 <p>RefBase， IInterface，BnInterface，BpInterface，BpRefBase，Parcel 等等</p>
 <p>下图描述了实例《<a href="http://www.cloudchou.com/android/post-332.html" target="_blank">Binder service入门–创建native binder service</a>》使用的ITestService与本地Binder框架类库的关系：(若看不清，请点击看大图)</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binde_framework.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binde_framework.png" alt="native_binde_framework" width="987" height="851" class="aligncenter size-full wp-image-549" /></a>
 <ul>
 <li>
  <h3>1)\tRefBase类(frameworks/native/include/utils/RefBase.h)</h3>
  <p>引用的基类，android本地代码里采用了智能指针，有强指针，也有弱指针。不过不用纠结于这些细节。</p>
 </li>
 <li>
  <h3>2)\tIInterface(frameworks/native/include/binder/IInterface.h)</h3>
  <p>自定义的binder service接口必须继承自IInterface(如ITestService)，它的onAsBinder方法为抽象方法，该方法的实现在BpInterface和BnInterface模版类里。</p>
 </li>
 <li>
  <h3>3)\tBpRefBase(frameworks/native/include/binder/Binder.h)</h3>
  <p>客户端间接用到该类，用于保存IBinder指针，remote()方法即返回IBinder指针。</p>
 </li>
 <li>
  <h3>4)\tITestService</h3>
  <p>声明的binder service接口，在该接口里会声明所有提供的服务方法(使用纯虚函数)，并用宏DECLARE_META_INTERFACE进行声明，这样会添加静态字段descriptor，静态方法asInterface，虚方法getInterfaceDescriptor，以及构造函数和析构函数。另外只需要使用IMPLEMENT_META_INTERFACE(INTERFACE, NAME)来即可定义用宏DECLARE_META_INTERFACE声明的这些方法和字段。</p>
  <p>DECLARE_META_INTERFACE宏的源码如下所示：</p>
 ```cpp
 #define DECLARE_META_INTERFACE(INTERFACE)                           \\
     static const android::String16 descriptor;                      \\
     static android::sp<I##INTERFACE> asInterface(                   \\
             const android::sp<android::IBinder>& obj);              \\
     virtual const android::String16& getInterfaceDescriptor() const;\\
     I##INTERFACE();                                                 \\
     virtual ~I##INTERFACE(); 
 ``` 
 <p>若使用DECLARE_META_INTERFACE(TestService); 则会扩展为:</p> 
 ```cpp
 static const android::String16 descriptor;                       \\
 static android::sp<ITestService> asInterface(                    \\
             const android::sp<android::IBinder>& obj);           \\
 virtual const android::String16& getInterfaceDescriptor() const; \\
 ITestService();                                                  \\
 virtual ~ITestService();
 ```
 <p>宏函数IMPLEMENT_META_INTERFACE(INTERFACE, NAME)的源码如下所示：</p>
 
 ```cpp
 #define IMPLEMENT_META_INTERFACE(INTERFACE, NAME)              \\
     const android::String16 I##INTERFACE::descriptor(NAME);    \\
     const android::String16&                                   \\
             I##INTERFACE::getInterfaceDescriptor() const {     \\
         return I##INTERFACE::descriptor;                       \\
     }                                                          \\
     android::sp<I##INTERFACE> I##INTERFACE::asInterface(       \\
             const android::sp<android::IBinder>& obj)          \\
     {                                                          \\
         android::sp<I##INTERFACE> intr;                        \\
         if (obj != NULL) {                                     \\
             intr = static_cast<I##INTERFACE*>(                 \\
                 obj->queryLocalInterface(                      \\
                         I##INTERFACE::descriptor).get());      \\
             if (intr == NULL) {                                \\
                 intr = new Bp##INTERFACE(obj);                 \\
             }                                                  \\
         }                                                      \\
         return intr;                                           \\
     }                                                          \\
     I##INTERFACE::I##INTERFACE() { }                           \\
     I##INTERFACE::~I##INTERFACE() { }                          \\
 ```
 <p>若使用IMPLEMENT_META_INTERFACE(TestService, "android.TestServer.ITestService")则会被替换成:</p>
 ```cpp
 const android::String16 
     ITestService::descriptor("android.TestServer.ITestService"); \\
     const android::String16&                                     \\
             ITestService::getInterfaceDescriptor() const {       \\
         return ITestService::descriptor;                         \\
     }                                                            \\
     android::sp<ITestService> ITestService::asInterface(         \\
             const android::sp<android::IBinder>& obj)            \\
     {                                                            \\
         android::sp<ITestService> intr;                          \\
         if (obj != NULL) {                                       \\
             intr = static_cast<ITestService*>(                   \\
                 obj->queryLocalInterface(                        \\
                         ITestService::descriptor).get());        \\
             if (intr == NULL) {                                  \\
                 intr = new BpTestService(obj);                   \\
             }                                                    \\
         }                                                        \\
         return intr;                                             \\
     }                                                            \\
     ITestService::ITestService() { }                             \\
     ITestService::~ITestService() { }                            \\
 ```
 </li>
 <li>
  <h3>5)\tBpInterface(frameworks/native/include/binder/Binder.h)</h3>
  <p>该类是一个模版类，需和某个继承自IIterface的类结合使用。</p>
  <p>它的声明如下所示：</p> 
 ```cpp
  template<typename INTERFACE>
 class BpInterface : public INTERFACE, public BpRefBase
 {
 public:
                                 BpInterface(const sp<IBinder>& remote);
 
 protected:
     virtual IBinder*            onAsBinder();
 };
 ```
 <p>因此BpInterface会继承两个类，一个父类是继承自IInterface的类，一个是BpRefbase，我们通常声明的客户端代理类会继承自BpInterface</p>
  
 </li>
 <li>
  <h3>6)\tBnInterface(frameworks/native/include/binder/IInterface.h)</h3>
  <p>该类也是一个模版类，需和某个继承自IIterface的类结合使用。</p>
  <p>它的声明如下所示：</p>
 ```cpp
  template<typename INTERFACE>
 class BnInterface : public INTERFACE, public BBinder
 {
 public:
     virtual sp<IInterface>      
         queryLocalInterface(const String16& _descriptor);
     virtual const String16&     getInterfaceDescriptor() const;
 
 protected:
     virtual IBinder*            onAsBinder();
 };
 ```
 <p>因此BnInterface也会继承两个类，一个父类是继承自IInterface的binder service接口类，一个是代表Binder service服务端的BBinder类，我们通常声明的服务端类会直接继承自BnInterface。</p>
 <p>该类实现了IBinder声明的另外两个方法，queryLocalInterface和getInterfaceDescriptor。</p> 
 </li>
 </ul>
 <p>再介绍一个重要的宏函数interface_cast，它的源码如下所示：</p>
 ```cpp
 template<typename INTERFACE>
 inline sp<INTERFACE> interface_cast(const sp<IBinder>& obj)
 {
     return INTERFACE::asInterface(obj);
 }
 ```
 <p>若使用interface_cast < ITestService > (binder)，会被扩展为：</p>
 ```cpp
 inline sp< ITestService > interface_cast(const sp<IBinder>& obj)
 {
     return ITestService::asInterface(obj);
 }
 ```
 <p>而ITestService::asInterface方法是ITestService接口声明时使用DECLARE_META_INTERFACE(TestService)声明的函数</p>
 <h2>IServiceManager类图</h2>
 <p>从先前的博客《<a href="http://www.cloudchou.com/android/post-497.html" target="_blank">Binder IPC程序结构</a>》可知，servicemanager其实是init.rc里声明的本地服务，由init进程启动它作为一个单独的进程运行。不管是提供binder service的服务端还是使用binder service的客户端，都是在单独的进程，他们都需要首先获得servicemananger的IBinder指针，然后利用IBinder指针建立IServiceManager接口对象。通过《<a href="http://www.cloudchou.com/android/post-534.html" target="_blank">Binder 机制详解—重要函数调用流程分析</a>》我们已经知道如何获得servicemananger的IBinder指针，并利用该IBinder指针建立IServiceMananger接口对象。</p>
 <p>IServiceManager相关类如下图所示：(若看不清，请点击看大图)</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binder_framework_servicemananger.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binder_framework_servicemananger-1024x378.png" alt="native_binder_framework_servicemananger" width="1024" height="378" class="aligncenter size-large wp-image-550" /></a>
 <p>IServiceManager是表示servicemanager的接口，有如下方法：</p>
 <p>1) getService获得binder service引用，</p>
 <p>2) checkService获得binder service引用，</p>
 <p>3) addService添加binder service，</p>
 <p>4) listServices 列举所有binder service。</p>
 <p>servicemanager的binder service服务端其实是在frameworks/base/cmds/servicemanager 里实现，BnServiceMananger实际上并未使用。BpServiceMananger就是利用获得的IBinder指针建立的IServiceMananger对象的实际类型。</p>
