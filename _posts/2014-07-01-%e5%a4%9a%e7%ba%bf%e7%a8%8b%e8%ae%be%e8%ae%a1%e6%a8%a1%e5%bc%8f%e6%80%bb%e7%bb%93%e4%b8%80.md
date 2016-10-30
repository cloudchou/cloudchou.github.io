---
id: 609
title: 多线程设计模式总结(一)
date: 2014-07-01T23:01:29+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=609
permalink: /softdesign/post-609.html
views:
  - 3382
categories:
  - 软件设计
tags:
  - 多线程编程
  - 多线程设计模式
  - 并发编程
  - 生产者消费者模式
  - 读写锁模式
---
并发程序的编程与设计是一个难点，也是程序员必须掌握的一个点。工作之后写的第一个软件里面也有<a href="http://www.cloudchou.com/tag/%e5%b9%b6%e5%8f%91%e7%bc%96%e7%a8%8b" title="View all posts in 并发编程" target="_blank" class="tags">并发编程</a>，当时在设计并发这块感觉好复杂，最后的实现感觉也有点乱。

当时就想好好学习一下并发编程的设计，但是一直没有时间。今年看了两本并发编程相关的书，《<a href="http://www.cloudchou.com/tag/%e5%a4%9a%e7%ba%bf%e7%a8%8b%e8%ae%be%e8%ae%a1%e6%a8%a1%e5%bc%8f" title="View all posts in 多线程设计模式" target="_blank" class="tags">多线程设计模式</a>》和《Java并发编程与实战》。本想着和设计模式一样，多线程设计模式也能提供很多模式可供套用，但是实际情况并不是如此，多线程设计模式讲的东西多为基础，并且内容也已经有点过时了，市面上《多线程设计模式》这本书也已经很难买到。而《Java并发编程与实战》这本书讲的东西比较深，也讲了Java5并发包的同步类的使用。个人感觉《多线程设计模式》讲的东西了解就可以了，但是《Java并发编程实战》值得细读。接下来我会写一些博客和读者分享我读这些书的心得与体会。

## 多线程程序的评量标准

多线程程序的评量标准：

  * ### 1) 安全性:不损坏对象 
    
    不安全是指，对象的状态处于非预期状态，比如账户余额变成了负值

  * ### 2) 生存性:进行必要的处理 
    
    生存性是指：程序能正常运行，可进行必要的处理，影响生存性的典型问题有出现死锁

  * ### 3) 复用性:可再利用类 
    
    复用性是指代码重用，若复用性好，可减少大量重复代码

  * ### 4) 性能:能快速，大量进行处理 
    
    性能有两个方面的考虑因素：吞吐量和响应性，客户端程序比较重视响应性，服务端程序更重视吞吐量，吞吐量是指单位时间内完成的任务，响应性是指提交任务后多长时间内能收到程序的反馈。比如说我们在QQ时，经常感觉QQ卡，这便是响应性问题。

其中安全性和生存性是必要的，如果安全性和生存性都没有保证，就无所谓别的考量了。复用性和性能决定了程序的质量



《多线程设计模式》一共讲了12个设计模式，列举如下。

## 1)Single Threaded Execution 

只允许单个线程执行对象的某个方法，以保护对象的多个状态。

实现时需用synchronized修饰引用受保护的状态的方法，这样就只能有单个线程访问该方法，其它线程由于不能获取锁而等待，因为只有一个线程去访问受保护状态变量，故此不需要担心该状态变量被别的线程修改。

也可以用synchronized修饰代码块来保护状态字段。

### 示例程序：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> Gate <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">String</span> _name <span style="color: #339933;">=</span> <span style="color: #0000ff;">"NoBody"</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">String</span> _where <span style="color: #339933;">=</span> <span style="color: #0000ff;">"NoBody"</span><span style="color: #339933;">;</span> 
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> pass<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> name, <span style="color: #003399;">String</span> where<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        _name <span style="color: #339933;">=</span> name<span style="color: #339933;">;</span>
        _where <span style="color: #339933;">=</span> where<span style="color: #339933;">;</span> 
        check<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> check<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>_name.<span style="color: #006633;">charAt</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> _where.<span style="color: #006633;">charAt</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
             <span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"*****************Broken**************"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

如果这里不用synchronized修饰pass方法，多线程环境下会有多个线程同时执行pass方法，容易造成状态不一致，引入安全性问题。

### 适用场景：

多线程环境下如果状态变量(可能有多个状态变量，并且它们之间是相关的)被多个线程访问，并且可能会发生变化，此时需要将状态变量封装起来(可以用类进行封装)，并将访问这些状态变量的方法用synchronized进行保护。可以用synchronized修饰方法，也可以修饰代码块。

### 注意事项：

一定要注意synchronized是通过获取哪个锁来保护状态变量，如果保护状态变量时使用不同的锁对象，那么多个线程仍然可以同时访问被保护的状态变量，尤其是保护多个相关状态变量时一定要记得用同一个锁对象。synchronized修饰方法时，获取的锁对象是synchronied方法所在类的实例，synchorized修饰this时，获取的锁对象也是当前类的实例。

synchronized修饰符不会被继承，也就是说我们覆盖父类的synchronized方法时，如果不添加synchronized修饰符，就不能保护状态变量，因此覆盖父类方法时，如果想保护某些状态变量，记得添加synchronized修饰符。 

## 2)Immutable

在single threaded executetion这个模式里我们使用了synchronized来保护需要保护的状态变量，因为这些状态可能会变化，如果不保护的话，可能会破坏对象。但是用synchronized保护变量也带来了性能问题，因为获取锁需要时间，并且如果多个线程竞争锁的话，会让某些线程进入这个锁的条件队列，暂停执行，这样会降低性能。

如果状态根本不会发生变化，就不需要用锁保护，这就是Immutable模式。

### 示例程序：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000000; font-weight: bold;">class</span> Person <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> _name<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> _address<span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> Person<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> name, <span style="color: #003399;">String</span> address<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        _name <span style="color: #339933;">=</span> name<span style="color: #339933;">;</span>
        _address <span style="color: #339933;">=</span> address<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">String</span> getName<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> _name<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">String</span> getAddress<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> _address<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    @Override
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">String</span> toString<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">return</span> <span style="color: #0000ff;">"Person [_name="</span> <span style="color: #339933;">+</span> _name <span style="color: #339933;">+</span> <span style="color: #0000ff;">", _address="</span> <span style="color: #339933;">+</span> _address <span style="color: #339933;">+</span> <span style="color: #0000ff;">"]"</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

Person类用final修饰，防止被继承。

\_name和\_address都用final修饰，防止被修改，只能在定义时初始化，或者在构造器里初始化，Person类也只提供了对这些状态字段的get方法，故此外界调用该类的实例时无法修改这些状态。

### 适用场景：

对于那些不会变化的状态可用Immutable类进行封装，这样可避免用锁同步，从而提高性能。

### 注意事项：

String就是一个Immutable类，与之相对应的StringBuilder或者StringBuffer是muttable类。我们在设计类时，针对那些需要共享并且访问很频繁的实例，可将其设置为Immutalbe类，如果在少数情况下它的状态也可能会变化，可为之设计相对应的muttable类，像String和StringBuffer的关系一样。

StringBuilder是非线程安全的，StringBuffer是线程安全的，String也是线程安全的，因为它是immutable类。

java里的包装器类全是immutable类。

## 3)Guarded Suspension

当我们调用对象某个的某个方法时，可能对象当前状态并不满足执行的条件，于是需要等待，这就是Guarded Suspension模式。只有当警戒条件满足时，才执行，否则等待，另外对象必须有改变其状态的方法。

### 示例程序：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> RequestQueue <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> LinkedList<span style="color: #339933;">&lt;</span>Request<span style="color: #339933;">&gt;</span> _queue <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> LinkedList<span style="color: #339933;">&lt;</span>Request<span style="color: #339933;">&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #003399;">Request</span> getRequest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>_queue.<span style="color: #006633;">size</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&lt;=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
                wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">InterruptedException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
&nbsp;
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #000000; font-weight: bold;">return</span> _queue.<span style="color: #006633;">removeFirst</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> putRequest<span style="color: #009900;">&#40;</span><span style="color: #003399;">Request</span> request<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        _queue.<span style="color: #006633;">add</span><span style="color: #009900;">&#40;</span>request<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

\_queue.size()>0 便是警戒条件，只有当\_queue.size()>0才能调用_queue.removeFirst()，当警戒条件不满足时，需要wait。

putRequest方法可以改变RequestQueue的状态，使getRequest方法里的警戒条件满足。

### 适用场景：

某个调用者的方法在执行时如果希望当状态不满足时等待状态满足后再执行，如果状态满足，则立即执行，可考虑使用Guarded Suspension模式。

### 注意事项：

Guarded Suspension里的警戒方法(等待状态成立才执行的方法)是同步阻塞的，状态不满足时，调用该方法的线程会阻塞。

Guarded Suspension里的状态变更方法里须记得在状态变更后，调用notifyAll，使得调用警戒方法的线程可恢复执行。

## 4)Balking

Balking模式与Guarded Suspension模式相似，都是在对象状态不符合要求时需要进行一些处理，不过Guared Suspension在状态不满足要求时，会等待并阻塞线程，而Balking模式是直接返回，并不等待。调用者可暂时先做别的工作，稍后再来调用该对象的方法。

### 示例程序：

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
28
29
30
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> Data <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> _file_name<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">String</span> _content<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">boolean</span> _changed<span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> Data<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> filename, <span style="color: #003399;">String</span> conetent<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        _file_name <span style="color: #339933;">=</span> filename<span style="color: #339933;">;</span>
        _content <span style="color: #339933;">=</span> conetent<span style="color: #339933;">;</span>
        _changed <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> change<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> newContent<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        _content <span style="color: #339933;">=</span> newContent<span style="color: #339933;">;</span>
        _changed <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> save<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">IOException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>_changed<span style="color: #009900;">&#41;</span>
            <span style="color: #000000; font-weight: bold;">return</span><span style="color: #339933;">;</span>
        doSave<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        _changed <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> doSave<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">IOException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #003399;">Writer</span> writer <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">FileWriter</span><span style="color: #009900;">&#40;</span>_file_name<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        writer.<span style="color: #006633;">write</span><span style="color: #009900;">&#40;</span>_content<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        writer.<span style="color: #006633;">close</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

save方法里首先检测字符串是否有变化，如果没有变化则立即返回，否则才保存字符串，这样可避免不必要的IO，提高性能。

上述实例中的警戒条件是_changed为true

### 适用场景：

不想等待警戒条件成立时，适合使用Balking模式。

警戒条件只有第一次成立时，适合使用Balking模式。

### 注意事项：

该模式并不会等待警戒条件成立，当警戒条件不成立时直接返回了，故此改变状态的方法也就不需要调用notifyAll方法。

另外注意不管是警戒条件方法还是改变状态的方法都需要用synchronized同步，因为这里封装了多个数据，一个用于判断警戒条件的状态，还有真实数据。

## 5)Producer-Consumer

生产者消费者问题是操作系统里非常经典的同步问题，生产者生产好数据后，放到缓冲区，消费者从缓冲区取出数据。但是当缓冲区满了的时候，生产者不可再将生产好的数据放到缓冲区，当缓冲区没有数据的时候消费者不可再从缓冲区里取出数据。

解决生产者消费者问题的方案称之为<a href="http://www.cloudchou.com/tag/%e7%94%9f%e4%ba%a7%e8%80%85%e6%b6%88%e8%b4%b9%e8%80%85%e6%a8%a1%e5%bc%8f" title="View all posts in 生产者消费者模式" target="_blank" class="tags">生产者消费者模式</a>，在该模式里可能有多个生产者，多个消费者，生产者和消费者都有独立的线程。其中最关键的是放置数据的缓冲区，生产者和消费者在操作缓冲区时都必须同步，生产者往缓冲区放置数据时，如果发现缓冲区已满则等待，消费者从缓冲区取数据时如果发现缓冲区没有数据，也必须等待。

### 示例程序：

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
28
29
30
31
32
33
34
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> Table <span style="color: #009900;">&#123;</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> _buffer<span style="color: #339933;">;</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> _tail<span style="color: #339933;">;</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> _head<span style="color: #339933;">;</span>
<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> _count<span style="color: #339933;">;</span>
&nbsp;
<span style="color: #000000; font-weight: bold;">public</span> Table<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> count<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
	_buffer <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">String</span><span style="color: #009900;">&#91;</span>count<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
	_head <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
	_tail <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
	_count <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> put<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> cake<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>_count <span style="color: #339933;">&gt;=</span> _buffer.<span style="color: #006633;">length</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
	_buffer<span style="color: #009900;">&#91;</span>_tail<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> cake<span style="color: #339933;">;</span>
	_tail <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>_tail <span style="color: #339933;">+</span> <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">%</span> _count<span style="color: #339933;">;</span>
	_count<span style="color: #339933;">++;</span>
	notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #003399;">String</span> take<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>_count <span style="color: #339933;">&lt;=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
	<span style="color: #003399;">String</span> cake <span style="color: #339933;">=</span> _buffer<span style="color: #009900;">&#91;</span>_head<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
	_head <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>_head <span style="color: #339933;">+</span> <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">%</span> _count<span style="color: #339933;">;</span>
	_count<span style="color: #339933;">--;</span>
	notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #000000; font-weight: bold;">return</span> cake<span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

这里table扮演的便是数据缓冲区的角色，当消费者调用take取数据时，如果发现数据数目少于0时，便会等待，当生产者调用put放数据时，如果发现数据数目大于缓冲区大小时，也会等待。

### 适用场景：

当程序里有多个生产者角色或者多个消费者角色操作同一个共享数据时，适合用生产者消费者模式。比如下载模块，通常会有多个下载任务线程(消费者角色)，用户点击下载按钮时产生下载任务(生产者角色)，它们会共享任务队列。

### 注意事项：

不管是生产方法还是消费方法，当警戒条件不满足时，一定要等待，警戒条件满足后执行完放置数据逻辑或者取出数据逻辑后一定要调用notifyAll方法，使得其它线程恢复运行。

## 6)Read-Write Lock

先前的几个多线程设计模式里，操作共享数据时，不管如何操作数据一律采取互斥的策略(除了Immutable模式)，即只允许一个线程执行同步方法，其它线程在共享数据的条件队列里等待，只有执行同步方法的线程执行完同步方法后被阻塞的线程才可在获得同步锁后继续执行。

这样效率其实有点低，因为读操作和读操作之间并不需要互斥，两个读线程可以同时操作共享数据，读线程和写线程同时操作共享数据会有冲突，两个写线程同时操作数据也会有冲突。

### 示例程序：

Data类

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
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> Data <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">char</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> _buffer<span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> ReadWriteLock _lock <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> ReadWriteLock<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> Data<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> size<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        _buffer <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #000066; font-weight: bold;">char</span><span style="color: #009900;">&#91;</span>size<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> i <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span> i <span style="color: #339933;">&lt;</span> size<span style="color: #339933;">;</span> i<span style="color: #339933;">++</span><span style="color: #009900;">&#41;</span>
            _buffer<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> <span style="color: #0000ff;">'*'</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">char</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> read<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
        _lock.<span style="color: #006633;">readLock</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">return</span> doRead<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _lock.<span style="color: #006633;">readUnlock</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> write<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">char</span> c<span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
        _lock.<span style="color: #006633;">writeLock</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            doWrite<span style="color: #009900;">&#40;</span>c<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _lock.<span style="color: #006633;">writeUnock</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">char</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> doRead<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000066; font-weight: bold;">char</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> newbuf <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #000066; font-weight: bold;">char</span><span style="color: #009900;">&#91;</span>_buffer.<span style="color: #006633;">length</span><span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> i <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span> i <span style="color: #339933;">&lt;</span> newbuf.<span style="color: #006633;">length</span><span style="color: #339933;">;</span> i<span style="color: #339933;">++</span><span style="color: #009900;">&#41;</span>
            newbuf<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> _buffer<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
        slowly<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> newbuf<span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> doWrite<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">char</span> c<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> i <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span> i <span style="color: #339933;">&lt;</span> _buffer.<span style="color: #006633;">length</span><span style="color: #339933;">;</span> i<span style="color: #339933;">++</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            _buffer<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> c<span style="color: #339933;">;</span>
            slowly<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> slowly<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #003399;">Thread</span>.<span style="color: #006633;">sleep</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">500</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">InterruptedException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

ReadWriteLock类

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
28
29
30
31
32
33
34
35
36
37
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> ReadWriteLock <span style="color: #009900;">&#123;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> _reading_readers <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> _waiting_writers <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> _writing_writers <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">boolean</span> _prefer_writer <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> readLock<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>_writing_writers <span style="color: #339933;">&gt;</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">||</span> <span style="color: #009900;">&#40;</span>_prefer_writer <span style="color: #339933;">&&</span> _waiting_writers <span style="color: #339933;">&gt;</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        _reading_readers<span style="color: #339933;">++;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> readUnlock<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        _reading_readers<span style="color: #339933;">--;</span>
        _prefer_writer <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
        notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> writeLock<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
        _waiting_writers<span style="color: #339933;">++;</span>
        <span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>_reading_readers <span style="color: #339933;">&gt;</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">||</span> _writing_writers <span style="color: #339933;">&gt;</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span>
                wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
            _waiting_writers<span style="color: #339933;">--;</span>
        <span style="color: #009900;">&#125;</span>
        _writing_writers<span style="color: #339933;">++;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> writeUnock<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        _writing_writers<span style="color: #339933;">--;</span>
        _prefer_writer <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
        notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

这里为读写锁设置了单独的类ReadWriteLock，ReadWriteLock提供了4个方法readLock，readUnlock，writeLock，writeUnlock。

读线程在读取共享数据时，先调用readLock方法获取读锁，然后使用try块读取共享数据并在finnally块中调用readUnlock释放读锁。写线程在写入共享数据时，先调用writeLock方法获取写锁，然后使用try块写入共享数据并在finnally块中调用writeUnlock方法释放写锁。

实现ReadWriteLock时使用了\_waiting\_writers和\_prefer\_writer，其实如果不采用这两个字段也能实现读写锁，但是使用了\_prefer\_writer后可以让读线程以及写线程不致于饥饿。每次读线程调用完readUnlock后设置\_prefer\_writer为true，此时如果有写线程等待写入，便可恢复执行，而不是由其它读线程继续执行。每次写线程调用完writeUnlock后，\_prefer\_writer为false，此时等待读取的线程可恢复执行。

### 适用场景：

操作共享数据的读线程明显多于写线程时可采用<a href="http://www.cloudchou.com/tag/%e8%af%bb%e5%86%99%e9%94%81%e6%a8%a1%e5%bc%8f" title="View all posts in 读写锁模式" target="_blank" class="tags">读写锁模式</a>提高程序性能。

### 注意事项：

Java 5的concurrent包里已经有ReadWriteLock接口，对应的类有ReentrantReadWriteLock，没必要自己实现ReadWriteLock类。并发库里的类都是经过测试的稳定的类，并且性能也会比自己写的类要高，因此我们应该优先选择并发库里的类。