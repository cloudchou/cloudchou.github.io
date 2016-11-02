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
上一篇博客介绍了Binder系统架构，其中说到Binder框架，本地层和Java层各自有一套实现。本篇博客将介绍Binder本地框架。

## Binder本地框架

本地Binder框架包含以下类(frameworks/native/libs/binder)：

RefBase， IInterface，BnInterface，BpInterface，BpRefBase，Parcel 等等

下图描述了实例《<a href="http://www.cloudchou.com/android/post-332.html" target="_blank">Binder service入门–创建native binder service</a>》使用的ITestService与本地Binder框架类库的关系：(若看不清，请点击看大图)

<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binde_framework.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binde_framework.png" alt="native_binde_framework" width="987" height="851" class="aligncenter size-full wp-image-549" srcset="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binde_framework.png 987w, http://www.cloudchou.com/wp-content/uploads/2014/05/native_binde_framework-300x258.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/05/native_binde_framework-173x150.png 173w" sizes="(max-width: 987px) 100vw, 987px" /></a>

  * ### 1) RefBase类(frameworks/native/include/utils/RefBase.h)
    
    引用的基类，android本地代码里采用了智能指针，有强指针，也有弱指针。不过不用纠结于这些细节。

  * ### 2) IInterface(frameworks/native/include/binder/IInterface.h)
    
    自定义的binder service接口必须继承自IInterface(如ITestService)，它的onAsBinder方法为抽象方法，该方法的实现在BpInterface和BnInterface模版类里。

  * ### 3) BpRefBase(frameworks/native/include/binder/Binder.h)
    
    客户端间接用到该类，用于保存IBinder指针，remote()方法即返回IBinder指针。

  * ### 4) ITestService
    
    声明的binder service接口，在该接口里会声明所有提供的服务方法(使用纯虚函数)，并用宏DECLARE\_META\_INTERFACE进行声明，这样会添加静态字段descriptor，静态方法asInterface，虚方法getInterfaceDescriptor，以及构造函数和析构函数。另外只需要使用IMPLEMENT\_META\_INTERFACE(INTERFACE, NAME)来即可定义用宏DECLARE\_META\_INTERFACE声明的这些方法和字段。
    
    DECLARE\_META\_INTERFACE宏的源码如下所示：
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
2
3
4
5
6
7
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"><span style="color: #339900;">#define DECLARE_META_INTERFACE(INTERFACE)                           \
    static const android::String16 descriptor;                      \
    static android::sp&lt;I##INTERFACE&gt; asInterface(                   \
            const android::sp&lt;android::IBinder&gt;& obj);              \
    virtual const android::String16& getInterfaceDescriptor() const;\
    I##INTERFACE();                                                 \
    virtual ~I##INTERFACE();</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    若使用DECLARE\_META\_INTERFACE(TestService); 则会扩展为:
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
2
3
4
5
6
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">static</span> <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">String16</span> descriptor<span style="color: #008080;">;</span>                       \
<span style="color: #0000ff;">static</span> android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span> asInterface<span style="color: #008000;">&#40;</span>                    \
            <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>android<span style="color: #008080;">::</span><span style="color: #007788;">IBinder</span><span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>           \
<span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">String16</span><span style="color: #000040;">&</span> getInterfaceDescriptor<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">const</span><span style="color: #008080;">;</span> \
ITestService<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>                                                  \
<span style="color: #0000ff;">virtual</span> ~ITestService<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    宏函数IMPLEMENT\_META\_INTERFACE(INTERFACE, NAME)的源码如下所示：
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"><span style="color: #339900;">#define IMPLEMENT_META_INTERFACE(INTERFACE, NAME)              \
    const android::String16 I##INTERFACE::descriptor(NAME);    \
    const android::String16&                                   \
            I##INTERFACE::getInterfaceDescriptor() const {     \
        return I##INTERFACE::descriptor;                       \
    }                                                          \
    android::sp&lt;I##INTERFACE&gt; I##INTERFACE::asInterface(       \
            const android::sp&lt;android::IBinder&gt;& obj)          \
    {                                                          \
        android::sp&lt;I##INTERFACE&gt; intr;                        \
        if (obj != NULL) {                                     \
            intr = static_cast&lt;I##INTERFACE*&gt;(                 \
                obj-&gt;queryLocalInterface(                      \
                        I##INTERFACE::descriptor).get());      \
            if (intr == NULL) {                                \
                intr = new Bp##INTERFACE(obj);                 \
            }                                                  \
        }                                                      \
        return intr;                                           \
    }                                                          \
    I##INTERFACE::I##INTERFACE() { }                           \
    I##INTERFACE::~I##INTERFACE() { }                          \</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    若使用IMPLEMENT\_META\_INTERFACE(TestService, &#8220;android.TestServer.ITestService&#8221;)则会被替换成:
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">String16</span> 
    ITestService<span style="color: #008080;">::</span><span style="color: #007788;">descriptor</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"android.TestServer.ITestService"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span> \
    <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">String16</span><span style="color: #000040;">&</span>                                     \
            ITestService<span style="color: #008080;">::</span><span style="color: #007788;">getInterfaceDescriptor</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">const</span> <span style="color: #008000;">&#123;</span>       \
        <span style="color: #0000ff;">return</span> ITestService<span style="color: #008080;">::</span><span style="color: #007788;">descriptor</span><span style="color: #008080;">;</span>                         \
    <span style="color: #008000;">&#125;</span>                                                            \
    android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span> ITestService<span style="color: #008080;">::</span><span style="color: #007788;">asInterface</span><span style="color: #008000;">&#40;</span>         \
            <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>android<span style="color: #008080;">::</span><span style="color: #007788;">IBinder</span><span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> obj<span style="color: #008000;">&#41;</span>            \
    <span style="color: #008000;">&#123;</span>                                                            \
        android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span> intr<span style="color: #008080;">;</span>                          \
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>obj <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>                                       \
            intr <span style="color: #000080;">=</span> <span style="color: #0000ff;">static_cast</span><span style="color: #000080;">&lt;</span>ITestService<span style="color: #000040;">*</span><span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>                   \
                obj<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>queryLocalInterface<span style="color: #008000;">&#40;</span>                        \
                        ITestService<span style="color: #008080;">::</span><span style="color: #007788;">descriptor</span><span style="color: #008000;">&#41;</span>.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>        \
            <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>intr <span style="color: #000080;">==</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>                                  \
                intr <span style="color: #000080;">=</span> <span style="color: #0000dd;">new</span> BpTestService<span style="color: #008000;">&#40;</span>obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>                   \
            <span style="color: #008000;">&#125;</span>                                                    \
        <span style="color: #008000;">&#125;</span>                                                        \
        <span style="color: #0000ff;">return</span> intr<span style="color: #008080;">;</span>                                             \
    <span style="color: #008000;">&#125;</span>                                                            \
    ITestService<span style="color: #008080;">::</span><span style="color: #007788;">ITestService</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span> <span style="color: #008000;">&#125;</span>                             \
    ITestService<span style="color: #008080;">::</span>~ITestService<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span> <span style="color: #008000;">&#125;</span>                            \</pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 5) BpInterface(frameworks/native/include/binder/Binder.h)
    
    该类是一个模版类，需和某个继承自IIterface的类结合使用。
    
    它的声明如下所示：
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
2
3
4
5
6
7
8
9
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"> <span style="color: #0000ff;">template</span><span style="color: #000080;">&lt;</span><span style="color: #0000ff;">typename</span> INTERFACE<span style="color: #000080;">&gt;</span>
<span style="color: #0000ff;">class</span> BpInterface <span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> INTERFACE, <span style="color: #0000ff;">public</span> BpRefBase
<span style="color: #008000;">&#123;</span>
<span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
                                BpInterface<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> remote<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
&nbsp;
<span style="color: #0000ff;">protected</span><span style="color: #008080;">:</span>
    <span style="color: #0000ff;">virtual</span> IBinder<span style="color: #000040;">*</span>            onAsBinder<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    因此BpInterface会继承两个类，一个父类是继承自IInterface的类，一个是BpRefbase，我们通常声明的客户端代理类会继承自BpInterface

  * ### 6) BnInterface(frameworks/native/include/binder/IInterface.h)
    
    该类也是一个模版类，需和某个继承自IIterface的类结合使用。
    
    它的声明如下所示：
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
2
3
4
5
6
7
8
9
10
11
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"> <span style="color: #0000ff;">template</span><span style="color: #000080;">&lt;</span><span style="color: #0000ff;">typename</span> INTERFACE<span style="color: #000080;">&gt;</span>
<span style="color: #0000ff;">class</span> BnInterface <span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> INTERFACE, <span style="color: #0000ff;">public</span> BBinder
<span style="color: #008000;">&#123;</span>
<span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
    <span style="color: #0000ff;">virtual</span> sp<span style="color: #000080;">&lt;</span>IInterface<span style="color: #000080;">&gt;</span>      
        queryLocalInterface<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> String16<span style="color: #000040;">&</span> _descriptor<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">const</span> String16<span style="color: #000040;">&</span>     getInterfaceDescriptor<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">const</span><span style="color: #008080;">;</span>
&nbsp;
<span style="color: #0000ff;">protected</span><span style="color: #008080;">:</span>
    <span style="color: #0000ff;">virtual</span> IBinder<span style="color: #000040;">*</span>            onAsBinder<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    因此BnInterface也会继承两个类，一个父类是继承自IInterface的binder service接口类，一个是代表Binder service服务端的BBinder类，我们通常声明的服务端类会直接继承自BnInterface。
    
    该类实现了IBinder声明的另外两个方法，queryLocalInterface和getInterfaceDescriptor。

再介绍一个重要的宏函数interface_cast，它的源码如下所示：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">template</span><span style="color: #000080;">&lt;</span><span style="color: #0000ff;">typename</span> INTERFACE<span style="color: #000080;">&gt;</span>
<span style="color: #0000ff;">inline</span> sp<span style="color: #000080;">&lt;</span>INTERFACE<span style="color: #000080;">&gt;</span> interface_cast<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> obj<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">return</span> INTERFACE<span style="color: #008080;">::</span><span style="color: #007788;">asInterface</span><span style="color: #008000;">&#40;</span>obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

若使用interface_cast < ITestService > (binder)，会被扩展为：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">inline</span> sp<span style="color: #000080;">&lt;</span> ITestService <span style="color: #000080;">&gt;</span> interface_cast<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> obj<span style="color: #008000;">&#41;</span>
<span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">return</span> ITestService<span style="color: #008080;">::</span><span style="color: #007788;">asInterface</span><span style="color: #008000;">&#40;</span>obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

而ITestService::asInterface方法是ITestService接口声明时使用DECLARE\_META\_INTERFACE(TestService)声明的函数

## IServiceManager类图

从先前的博客《<a href="http://www.cloudchou.com/android/post-497.html" target="_blank">Binder IPC程序结构</a>》可知，servicemanager其实是init.rc里声明的本地服务，由init进程启动它作为一个单独的进程运行。不管是提供binder service的服务端还是使用binder service的客户端，都是在单独的进程，他们都需要首先获得servicemananger的IBinder指针，然后利用IBinder指针建立IServiceManager接口对象。通过《<a href="http://www.cloudchou.com/android/post-534.html" target="_blank">Binder 机制详解—重要函数调用流程分析</a>》我们已经知道如何获得servicemananger的IBinder指针，并利用该IBinder指针建立IServiceMananger接口对象。

IServiceManager相关类如下图所示：(若看不清，请点击看大图)

<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binder_framework_servicemananger.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binder_framework_servicemananger-1024x378.png" alt="native_binder_framework_servicemananger" width="1024" height="378" class="aligncenter size-large wp-image-550" srcset="http://www.cloudchou.com/wp-content/uploads/2014/05/native_binder_framework_servicemananger-1024x378.png 1024w, http://www.cloudchou.com/wp-content/uploads/2014/05/native_binder_framework_servicemananger-300x110.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/05/native_binder_framework_servicemananger-200x73.png 200w, http://www.cloudchou.com/wp-content/uploads/2014/05/native_binder_framework_servicemananger.png 1438w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

IServiceManager是表示servicemanager的接口，有如下方法：

1) getService获得binder service引用，

2) checkService获得binder service引用，

3) addService添加binder service，

4) listServices 列举所有binder service。

servicemanager的binder service服务端其实是在frameworks/base/cmds/servicemanager 里实现，BnServiceMananger实际上并未使用。BpServiceMananger就是利用获得的IBinder指针建立的IServiceMananger对象的实际类型。