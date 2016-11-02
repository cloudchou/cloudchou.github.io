---
id: 332
title: 'Binder service入门&#8211;创建native  binder service'
date: 2014-04-21T23:13:18+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=332
permalink: /android/post-332.html
views:
  - 9362
categories:
  - Android
tags:
  - android binder example
  - android binder native example
  - android binder 使用
  - android binder 入门
  - android binder 实例
---
## 1.前言

Binder service入门系列：

  * Binder service入门—Framework binder service:   
    <a href="http://www.cloudchou.com/android/post-447.html" target="_blank">http://www.cloudchou.com/android/post-447.html</a>
  * Binder service入门—应用层binder service:   
    <a href="http://www.cloudchou.com/android/post-458.html" target="_blank">http://www.cloudchou.com/android/post-458.html</a>
  * Binder service入门—框架层、应用层调用native binder service:   
    <a href="http://www.cloudchou.com/android/post-468.html" target="_blank">http://www.cloudchou.com/android/post-468.html</a>

这些天原计划研究Android启动过程，虽然先前研究过，但是有些机制还是没弄清楚，主要卡在binder service这块，不知道SystemServer调用init1后如何反过来调用init2的，也不知道框架层的那些service和service manager的关系，还有本地service和service manager的关系。网上看了不少资料，感觉很乱，有很多都介绍了binder的详细实现，但大多都只详细介绍各个数据结构的作用，各个数据结构之间的关系都弄不清，也有很多将驱动层和系统层混在一起介绍的，感觉一点都理不清。我觉得学习一样东西，最好自顶向下，并且能有简单的实例入门最好。

接下来我将以实例说明如何编写native的binder service，本实例将向service manager注册一个native的binder service，并用本地程序测试该binder service,整个工程都可以在github上下载：

<a href="https://github.com/cloudchou/NativeBinderTest" target="_blank">https://github.com/cloudchou/NativeBinderTest</a>

建议读者将源码下载下来在本地看，否则难理解。

## 2.程序构成

编译binder程序需要链接binder动态链接库，应用开发环境下使用ndk编程是不能链接binder动态链接库的，故此需要在源码开发环境下。本实例在vendor目录下建立了子目录shuame，然后把工程目录放在该目录下。

程序由2个部分组成，一个实现binder service的服务端程序，一个测试binder service的client程序，对应的Android.mk如下所示：

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
23
24
25
26
</pre>
      </td>
      
      <td class="code">
        <pre class="make" style="font-family:monospace;">LOCAL_PATH <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> my<span style="color: #004400;">-</span>dir<span style="color: #004400;">&#41;</span>
<span style="color: #339900; font-style: italic;">#生成binder service的服务端</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_SHARED_LIBRARIES <span style="color: #004400;">:=</span> \
    libcutils \
    libutils \
    libbinder 
LOCAL_MODULE    <span style="color: #004400;">:=</span> TestServer
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> \
    TestServer<span style="color: #004400;">.</span>cpp \
    ITestService<span style="color: #004400;">.</span>cpp
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_EXECUTABLE</span><span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #339900; font-style: italic;">#生成binder service的测试client端</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CLEAR_VARS</span><span style="color: #004400;">&#41;</span>
LOCAL_SHARED_LIBRARIES <span style="color: #004400;">:=</span> \
    libcutils \
    libutils \
    libbinder 
LOCAL_MODULE    <span style="color: #004400;">:=</span> TestClient
LOCAL_SRC_FILES <span style="color: #004400;">:=</span> \
    TestClient<span style="color: #004400;">.</span>cpp \
    ITestService<span style="color: #004400;">.</span>cpp
LOCAL_MODULE_TAGS <span style="color: #004400;">:=</span> optional
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_EXECUTABLE</span><span style="color: #004400;">&#41;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 3.程序源码构成

Test.h ：包含需要用到的头文件，声明接口，定义操作枚举，声明binder引用类 

ITestService.cpp： 接口类方法的实现

TestServer.cpp: 声明并实现binder实体类 ，启动binder服务，并在service manager里注册

TestClient.cpp： 声明并实现binder 引用类， 测试binder服务的client

### 实现binder service的步骤：

  * ### 1) 声明service 接口ITestService(Test.h)
    
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
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">class</span> ITestService <span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> Iinterface 
<span style="color: #008000;">&#123;</span>
     <span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
        <span style="color: #ff0000; font-style: italic;">/*使用该宏，相当于添加了一些代码，后面会有详细分析*/</span>     
        DECLARE_META_INTERFACE<span style="color: #008000;">&#40;</span>TestService<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span> 
        <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span> test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000080;">=</span><span style="color: #0000dd;"></span><span style="color: #008080;">;</span> <span style="color: #666666;">//该服务对外提供的操作接口</span>
<span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    使用DECLARE\_META\_INTERFACE(TestService);相当于添加了下述代码：
    
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
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">static</span> <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">String16</span> descriptor<span style="color: #008080;">;</span>
<span style="color: #0000ff;">static</span> android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span> asInterface<span style="color: #008000;">&#40;</span>  
        <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>android<span style="color: #008080;">::</span><span style="color: #007788;">IBinder</span><span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">String16</span><span style="color: #000040;">&</span> getInterfaceDescriptor<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">const</span><span style="color: #008080;">;</span>
ITestService <span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #0000ff;">virtual</span> ~ITestService<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    也就说添加了字段descriptor，也添加了两个成员函数asInterface，getInterfaceDescriptor, 还添加了构造器和析构器

  * ### 2)为ITestService接口的所有方法声明枚举，一个枚举值对应ITestService接口的一个方法(Test.h) 
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
2
3
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">enum</span><span style="color: #008000;">&#123;</span>
   TEST <span style="color: #000080;">=</span> IBinder<span style="color: #008080;">::</span><span style="color: #007788;">FIRST_CALL_TRANSACTION</span>,
<span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    TEST相当于ITestService接口里的test方法，后续会为该枚举值调用test方法(Test.h)

  * ### 3)声明binder引用类BpTestService(Test.h) 
    
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
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">class</span> BpTestService<span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> BpInterface<span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
    	BpTestService<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> impl<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    	<span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span> test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    因为实现ITestService接口的方法时，必须使用binder 引用类，所以binder引用类需要在Test.h里声明。但是实际上binder引用类的实现将放在TestClient.cpp里，而不是ITestService.cpp里。

  * ### 4)实现ITestService接口的方法(ITestService.cpp)
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;">IMPLEMENT_META_INTERFACE<span style="color: #008000;">&#40;</span>TestService, <span style="color: #FF0000;">"android.TestServer.ITestService"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    使用IMPLEMENT\_META\_INTERFACE(TestService, &#8220;android.TestServer.ITestService&#8221;);相当于添加了下述代码：
    
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
23
24
25
26
27
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"> <span style="color: #ff0000; font-style: italic;">/*初始化用宏DECLARE_META_INTERFACE声明的静态字段descriptor*/</span>
<span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">String16</span> ITestService<span style="color: #008080;">::</span><span style="color: #007788;">descriptor</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"android.TestServer.ITestService"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #ff0000; font-style: italic;">/*实现用宏DECLARE_META_INTERFACE声明的方法getInterfaceDescriptor */</span>
<span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">String16</span><span style="color: #000040;">&</span>                                          
        ITestService<span style="color: #008080;">::</span><span style="color: #007788;">getInterfaceDescriptor</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #0000ff;">const</span> <span style="color: #008000;">&#123;</span> 
    <span style="color: #0000ff;">return</span> ITestService<span style="color: #008080;">::</span><span style="color: #007788;">descriptor</span><span style="color: #008080;">;</span>                   
<span style="color: #008000;">&#125;</span>                                                                   
<span style="color: #ff0000; font-style: italic;">/*实现用宏DECLARE_META_INTERFACE声明的方法asInterface */</span>
android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span> ITestService<span style="color: #008080;">::</span><span style="color: #007788;">asInterface</span><span style="color: #008000;">&#40;</span>   
        <span style="color: #0000ff;">const</span> android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>android<span style="color: #008080;">::</span><span style="color: #007788;">IBinder</span><span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> obj<span style="color: #008000;">&#41;</span>      
<span style="color: #008000;">&#123;</span>                                                      
    android<span style="color: #008080;">::</span><span style="color: #007788;">sp</span><span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span> intr<span style="color: #008080;">;</span>                    
    <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>obj <span style="color: #000040;">!</span><span style="color: #000080;">=</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>           
        <span style="color: #ff0000; font-style: italic;">/*在binder实体类BnInterface里会执行queryLocalInterface*/</span>                      
        intr <span style="color: #000080;">=</span> <span style="color: #0000ff;">static_cast</span><span style="color: #000080;">&lt;</span>ITestService<span style="color: #000040;">*</span><span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>             
            obj<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>queryLocalInterface<span style="color: #008000;">&#40;</span>                  
                    ITestService<span style="color: #008080;">::</span><span style="color: #007788;">descriptor</span><span style="color: #008000;">&#41;</span>.<span style="color: #007788;">get</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>  
        <span style="color: #ff0000; font-style: italic;">/*在binder引用类BpInterface里会创建BpInterface的子类对象*/</span>            
        <span style="color: #0000ff;">if</span> <span style="color: #008000;">&#40;</span>intr <span style="color: #000080;">==</span> <span style="color: #0000ff;">NULL</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>                            
            intr <span style="color: #000080;">=</span> <span style="color: #0000dd;">new</span> BpTestService<span style="color: #008000;">&#40;</span>obj<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>             
        <span style="color: #008000;">&#125;</span>                                              
    <span style="color: #008000;">&#125;</span>                                                  
    <span style="color: #0000ff;">return</span> intr<span style="color: #008080;">;</span>                                       
<span style="color: #008000;">&#125;</span>                                                      
<span style="color: #ff0000; font-style: italic;">/*实现用宏DECLARE_META_INTERFACE声明的构造器和析构器 */</span>
ITestService<span style="color: #008080;">::</span><span style="color: #007788;">ITestService</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span> <span style="color: #008000;">&#125;</span>                     
ITestService<span style="color: #008080;">::</span>~ITestService<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span> <span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 5) 实现binder引用类BpTestService(TestClient.cpp)
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;">BpTestService<span style="color: #008080;">::</span><span style="color: #007788;">BpTestService</span><span style="color: #008000;">&#40;</span><span style="color: #0000ff;">const</span> sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span><span style="color: #000040;">&</span> impl<span style="color: #008000;">&#41;</span> <span style="color: #008080;">:</span>
  BpInterface<span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>impl<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
<span style="color: #008000;">&#125;</span>
<span style="color: #0000ff;">void</span> BpTestService<span style="color: #008080;">::</span><span style="color: #007788;">test</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
   <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"in the get Test<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
   Parcel data, reply<span style="color: #008080;">;</span>
   data.<span style="color: #007788;">writeInterfaceToken</span><span style="color: #008000;">&#40;</span>ITestService<span style="color: #008080;">::</span><span style="color: #007788;">getInterfaceDescriptor</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
   remote<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>transact<span style="color: #008000;">&#40;</span>TEST, data, <span style="color: #000040;">&</span>reply<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
   <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"send Print %d<span style="color: #000099; font-weight: bold;">\n</span>"</span>, reply.<span style="color: #007788;">readInt32</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    service 的 client端通过service manager拿到的ITestService接口对象其实就是一个binder引用，也就是说其实是一个BpTestService对象，它也会实现ITestService接口的test方法，但是它并没有实现test的功能，而是跨进程调用Binder实体对象BnInterface的test方法。因为涉及到跨进程调用，所以并没有直接调用，而是通过binder驱动转交给服务进程一些参数，然后就阻塞住。服务进程收到这些参数后，知道client端调用test方法，此时服务端再调用test方法，执行完后把执行结果通过binder驱动再返回给client所在进程，此时client的test方法收到结果后再返回。
    
    我们实际编程的时候并没有直接与binder驱动交互，而是通过Android为binder专门设计的一些核心库和框架来交互，这样简化了代码编写复杂度。像BpInterface便是核心库和框架提供的一个类，我们在实现时，只需要调用BpInterface的构造器，并实现ITestService接口的test方法即可，实现test方法时，通过remote()调用transact方法就能把数据提交至service端，servcie的返回结果会放在reply里。

  * ### 6) 实现client端(TestClient.cpp)
    
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
            <pre class="cpp" style="font-family:monospace;"> <span style="color: #0000ff;">int</span> main<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #ff0000; font-style: italic;">/*获取service manager引用*/</span>
sp<span style="color: #000080;">&lt;</span>IServiceManager<span style="color: #000080;">&gt;</span> sm <span style="color: #000080;">=</span> defaultServiceManager<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #ff0000; font-style: italic;">/*获取test service的binder接口对象*/</span>
sp<span style="color: #000080;">&lt;</span>IBinder<span style="color: #000080;">&gt;</span> binder <span style="color: #000080;">=</span> sm<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>getService<span style="color: #008000;">&#40;</span>String16<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"service.testservice"</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #ff0000; font-style: italic;">/*转为sp&lt;ITestService&gt;*/</span>
sp<span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span> cs <span style="color: #000080;">=</span> interface_cast<span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span><span style="color: #008000;">&#40;</span>binder<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
<span style="color: #ff0000; font-style: italic;">/*通过binder引用调用test方法*/</span>
    cs<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">return</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    interface_cast<ITestService>(binder); 实际上调用的方法是用宏DECLARE\_META\_INTERFACE声明的方法ITestService::asInterface，这里用了内联函数模版。
    
    ProcessState和IPCThreadState是真正直接和binder驱动交互的类，核心库和框架层都是通过和这两个类交互才能和驱动间接交互。它们通过ioctl和binder驱动交互，ProcessState主要负责管理所有的binder引用，IPCThreadState则和binder传输数据。以后如果有时间再详细介绍这两个类。

  * ### 7) 声明并实现binder实体类BnInterface(TestServer.cpp)
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"><span style="color: #0000ff;">class</span> BnTestService <span style="color: #008080;">:</span> <span style="color: #0000ff;">public</span> BnInterface<span style="color: #000080;">&lt;</span>ITestService<span style="color: #000080;">&gt;</span>
<span style="color: #008000;">&#123;</span>
 <span style="color: #0000ff;">public</span><span style="color: #008080;">:</span>
    <span style="color: #0000ff;">virtual</span> status_t
    onTransact<span style="color: #008000;">&#40;</span><span style="color: #0000ff;">uint32_t</span> code, <span style="color: #0000ff;">const</span> Parcel<span style="color: #000040;">&</span> data, Parcel<span style="color: #000040;">*</span> reply, <span style="color: #0000ff;">uint32_t</span> flags <span style="color: #000080;">=</span> <span style="color: #0000dd;"></span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">virtual</span> <span style="color: #0000ff;">void</span>
    test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
        <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"Now get test<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    <span style="color: #008000;">&#125;</span>
<span style="color: #008000;">&#125;</span><span style="color: #008080;">;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    BnInterface也是binder核心库和框架中的类，表示binder实体类，在onTransact函数里，会根据客户端提交的操作代码调用不同的函数，而操作代码就是2)里声明的枚举值，在本实例里是TEST,我们收到test后会调用test方法。本实例里将onTransact的实现放在第5步。

  * ### 8) 实现binder实体类的onTransact方法(TestServer.cpp)
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;">IMPLEMENT_META_INTERFACE<span style="color: #008000;">&#40;</span>TestService, <span style="color: #FF0000;">"android.TestServer.ITestService"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
status_t
BnTestService<span style="color: #008080;">::</span><span style="color: #007788;">onTransact</span><span style="color: #008000;">&#40;</span>uint_t code, <span style="color: #0000ff;">const</span> Parcel<span style="color: #000040;">&</span> data, Parcel<span style="color: #000040;">*</span> reply, <span style="color: #0000ff;">uint32_t</span> flags<span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">switch</span> <span style="color: #008000;">&#40;</span>code<span style="color: #008000;">&#41;</span>
        <span style="color: #008000;">&#123;</span>
    <span style="color: #0000ff;">case</span> TEST<span style="color: #008080;">:</span>
        <span style="color: #008000;">&#123;</span>
            <span style="color: #0000dd;">printf</span><span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"got the client msg<span style="color: #000099; font-weight: bold;">\n</span>"</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            CHECK_INTERFACE<span style="color: #008000;">&#40;</span>ITest, data, reply<span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            test<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            reply<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>writeInt32<span style="color: #008000;">&#40;</span><span style="color: #0000dd;">100</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
            <span style="color: #0000ff;">return</span> NO_ERROR<span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
    <span style="color: #0000ff;">default</span><span style="color: #008080;">:</span>
        <span style="color: #0000ff;">break</span><span style="color: #008080;">;</span>
        <span style="color: #008000;">&#125;</span>
    <span style="color: #0000ff;">return</span> NO_ERROR<span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    在onTransact里转调test方法即可。

  * ### 9) 实现server端(TestServer.cpp)
    
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
</pre>
          </td>
          
          <td class="code">
            <pre class="cpp" style="font-family:monospace;"> <span style="color: #0000ff;">int</span> main<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span> <span style="color: #008000;">&#123;</span>
    ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>  <span style="color: #666666;">//初始化单例</span>
    <span style="color: #ff0000; font-style: italic;">/*获取service manager的binder引用*/</span>
    sp<span style="color: #000080;">&lt;</span>IServiceManager<span style="color: #000080;">&gt;</span> sm <span style="color: #000080;">=</span> defaultServiceManager<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span> 
    <span style="color: #ff0000; font-style: italic;">/*添加服务 注意字符串必须用String16类型*/</span>
    sm<span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>addService<span style="color: #008000;">&#40;</span>String16<span style="color: #008000;">&#40;</span><span style="color: #FF0000;">"service.testservice"</span><span style="color: #008000;">&#41;</span>, <span style="color: #0000dd;">new</span> BnTestService<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span>
    ProcessState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>startThreadPool<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span> <span style="color: #666666;">//启动线程池</span>
    IPCThreadState<span style="color: #008080;">::</span><span style="color: #007788;">self</span><span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #000040;">-</span><span style="color: #000080;">&gt;</span>joinThreadPool<span style="color: #008000;">&#40;</span><span style="color: #008000;">&#41;</span><span style="color: #008080;">;</span><span style="color: #666666;">//等待线程结束</span>
    <span style="color: #0000ff;">return</span> <span style="color: #0000dd;"></span><span style="color: #008080;">;</span>
<span style="color: #008000;">&#125;</span></pre>
          </td>
        </tr>
      </table>
    </div>

## 4.测试

将TestServer和TestClient推到/data/local/tmp，并修改权限

adb push TestServer /data/local/tmp

adb push TestClient /data/local/tmp

adb shell chmod 755 /data/local/tmp/*

然后开两个cmd窗口测试：

[<img src="http://www.cloudchou.com/wp-content/uploads/2014/04/binder_test-1024x238.png" alt="binder_test" width="1024" height="238" class="alignnone size-large wp-image-344" srcset="http://www.cloudchou.com/wp-content/uploads/2014/04/binder_test-1024x238.png 1024w, http://www.cloudchou.com/wp-content/uploads/2014/04/binder_test-300x69.png 300w, http://www.cloudchou.com/wp-content/uploads/2014/04/binder_test-200x46.png 200w, http://www.cloudchou.com/wp-content/uploads/2014/04/binder_test.png 1087w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2014/04/binder_test.png)