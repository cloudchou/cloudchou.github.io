---
id: 616
title: 多线程设计模式总结(二)
date: 2014-07-03T09:30:41+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=616
permalink: /softdesign/post-616.html
views:
  - 2228
categories:
  - 软件设计
tags:
  - Thread-Specific Storage
  - Worker Thread
  - 多线程设计模式
  - 并发编程
  - 软件设计
---
接上一篇《<a href="http://www.cloudchou.com/tag/%e5%a4%9a%e7%ba%bf%e7%a8%8b%e8%ae%be%e8%ae%a1%e6%a8%a1%e5%bc%8f" title="View all posts in 多线程设计模式" target="_blank" class="tags">多线程设计模式</a>总结(一)》，这篇博客再介绍5个多线程设计模式

## 7)Thread-Per-Message

实现某个方法时创建新线程去完成任务，而不是在本方法里完成任务，这样可提高响应性，因为有些任务比较耗时。

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> Host <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> Handler _handler<span style="color: #339933;">=</span><span style="color: #000000; font-weight: bold;">new</span> Handler<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> request<span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> count, <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">char</span> c<span style="color: #009900;">&#41;</span><span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Thread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#123;</span>
			<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#123;</span>
				_handler.<span style="color: #006633;">handle</span><span style="color: #009900;">&#40;</span>count, c<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
			<span style="color: #009900;">&#125;</span>
		<span style="color: #009900;">&#125;</span>.<span style="color: #006633;">start</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

实现Host类的方法时，新建了一个线程调用Handler对象处理request请求。

每次调用Host对象的request方法时都会创建并启动新线程，这些新线程的启动顺序不是确定的。

### 适用场景：

适合在操作顺序无所谓时使用，因为请求的方法里新建的线程的启动顺序不是确定的。

在不需要返回值的时候才能使用，因为request方法不会等待线程结束才返回，而是会立即返回，这样得不到请求处理后的结果。

### 注意事项：

每次调用都会创建并启动一个新线程，对新建线程没有控制权，实际应用中只有很简单的请求才会用Thread-Per-Message这个模式，因为通常我们会关注返回结果，也会控制创建的线程数量，否则系统会吃不消。

## 8)<a href="http://www.cloudchou.com/tag/worker-thread" title="View all posts in Worker Thread" target="_blank" class="tags">Worker Thread</a>

在Thread-Per-Message模式里，每次函数调用都会启动一个新线程，但是启动新线程的操作其实是比较繁重的，需要比较多时间，系统对创建的线程数量也会有限制。我们可以预先启动一定数量的线程，组成线程池，每次函数调用时新建一个任务放到任务池，预先启动的线程从任务池里取出任务并执行。这样便可以控制线程的数量，也避免了每次启动新线程的高昂代价，实现了资源重复利用。

### 示例程序：

Channel类:

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> Channel <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> MAX_REQUEST <span style="color: #339933;">=</span> <span style="color: #cc66cc;">100</span><span style="color: #339933;">;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">Request</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> _request_queue<span style="color: #339933;">;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> tail<span style="color: #339933;">;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> head<span style="color: #339933;">;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">int</span> count<span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">private</span> WorkerThread<span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> _thread_pool<span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> Channel<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> threads<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		_request_queue <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Request</span><span style="color: #009900;">&#91;</span>MAX_REQUEST<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
		tail <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
		head <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
		count <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
		_thread_pool <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> WorkerThread<span style="color: #009900;">&#91;</span>threads<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
		<span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> i <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span> i <span style="color: #339933;">&lt;</span> threads<span style="color: #339933;">;</span> i<span style="color: #339933;">++</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			_thread_pool<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> 
			   <span style="color: #000000; font-weight: bold;">new</span> WorkerThread<span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Worker-"</span> <span style="color: #339933;">+</span> i, <span style="color: #000000; font-weight: bold;">this</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> startWorkers<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> i <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span> i <span style="color: #339933;">&lt;</span> _thread_pool.<span style="color: #006633;">length</span><span style="color: #339933;">;</span> i<span style="color: #339933;">++</span><span style="color: #009900;">&#41;</span>
			_thread_pool<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span>.<span style="color: #006633;">start</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #003399;">Request</span> takeRequest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> 
	             <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>count <span style="color: #339933;">&lt;=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span>
		<span style="color: #003399;">Request</span> request <span style="color: #339933;">=</span> _request_queue<span style="color: #009900;">&#91;</span>head<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
		head <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>head <span style="color: #339933;">+</span> <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">%</span> _request_queue.<span style="color: #006633;">length</span><span style="color: #339933;">;</span>
		count<span style="color: #339933;">--;</span>
		notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #000000; font-weight: bold;">return</span> request<span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> putRequest<span style="color: #009900;">&#40;</span><span style="color: #003399;">Request</span> request<span style="color: #009900;">&#41;</span>
			<span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span>count <span style="color: #339933;">&gt;=</span> _request_queue.<span style="color: #006633;">length</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span>
		_request_queue<span style="color: #009900;">&#91;</span>tail<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> request<span style="color: #339933;">;</span>
		tail <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>tail <span style="color: #339933;">+</span> <span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">%</span> _request_queue.<span style="color: #006633;">length</span><span style="color: #339933;">;</span>
		count<span style="color: #339933;">++;</span>
		notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

WorkerThread类:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> WorkerThread <span style="color: #000000; font-weight: bold;">extends</span> <span style="color: #003399;">Thread</span> <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> Channel _channel<span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> WorkerThread<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> name, Channel channel<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">super</span><span style="color: #009900;">&#40;</span>name<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		_channel <span style="color: #339933;">=</span> channel<span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	@Override
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			<span style="color: #003399;">Request</span> request<span style="color: #339933;">;</span>
			<span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
				request <span style="color: #339933;">=</span> _channel.<span style="color: #006633;">takeRequest</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
				request.<span style="color: #006633;">execute</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
			<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">InterruptedException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
				<span style="color: #666666; font-style: italic;">// TODO Auto-generated catch block</span>
				e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
			<span style="color: #009900;">&#125;</span> 
		<span style="color: #009900;">&#125;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

channel类集成了线程池和任务池，对外提供了startWorkers方法，外界可调用该方法启动所有工作线程，然后通过putRequest方法向任务池添加任务，工作者线程会自动从任务池里取出任务并执行。

### 适用场景：

和Thread-Per-Message模式一样，Worker Thread模式实现了invocation和exectution的分离，即调用和执行分离，调用者调用方法运行在一个线程，任务的执行在另一个线程。调用者调用方法后可立即返回，提高了程序的响应性。另外也正是因为调用和执行分离了，我们可以控制任务的执行顺序，还可以取消任务，还能分散处理，将任务交给不同的机器执行，如果没有将调用和执行分离，这些特性是无法实现的。

适合有大量任务并且还需要将任务执行分离的程序，比如象应用分发类App，需要经常和服务器通信获取数据，并且通信消息可能还有优先级。

### 注意事项：

注意控制工作者线程的数量，如果过多，那么会有不少工作者线程并没有工作，会浪费系统资源，如果过少会使得任务池里塞满，导致其它线程长期阻塞。可根据实际工作调整线程数量，和任务池里的最大任务池数。

如果worker thread只有一条，工人线程处理的范围就变成单线程了，可以省去共享互斥的必要。通常GUI框架都是这么实现的，操作界面的线程只有一个，界面元素的方法不需要进行共享互斥。如果操作界面的线程有多个，那么必须进行共享互斥，我们还会经常设计界面元素的子类，子类实现覆盖方法时也必须使用synchronized进行共享互斥，引入共享互斥后会引入锁同步的开销，使程序性能降低，并且如果有不恰当的获取锁的顺序，很容易造成死锁，这使得GUI程序设计非常复杂，故此GUI框架一般都采用单线程。

Java 5的并发包里已经有线程池相关的类，无需自己实现线程池。可使用Executors的方法启动线程池，这些方法包括newFixedThreadPool，newSingleThreadExecutor，newCachedThreadPool，newScheduledThreadPool等等。

## 9)Future

在Thread-Per-Message模式和Worker Thread模式里，我们实现了调用和执行分离。但是通常我们调用一个函数是可以获得返回值的，在上述两种模式里，虽然实现了调用和执行相分离，但是并不能获取调用执行的返回结果。Future模式则可以获得执行结果，在调用时返回一个Future，可以通过Future获得真正的执行结果。

### 示例程序：

Host类

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> Host <span style="color: #009900;">&#123;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> Data request<span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> count, <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">char</span> c<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">" request ("</span> <span style="color: #339933;">+</span> count 
		                 <span style="color: #339933;">+</span> <span style="color: #0000ff;">", "</span> <span style="color: #339933;">+</span> c <span style="color: #339933;">+</span> <span style="color: #0000ff;">" ) BEGIN"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #000000; font-weight: bold;">final</span> FutureData future <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> FutureData<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">Thread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			@Override
			<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
				RealData realData <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> RealData<span style="color: #009900;">&#40;</span>count, c<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
				future.<span style="color: #006633;">setRealData</span><span style="color: #009900;">&#40;</span>realData<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
			<span style="color: #009900;">&#125;</span>
&nbsp;
		<span style="color: #009900;">&#125;</span>.<span style="color: #006633;">start</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #000000; font-weight: bold;">return</span> future<span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

Data接口

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">interface</span> Data <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">String</span> getContent<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

FutureData类

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> FutureData <span style="color: #000000; font-weight: bold;">implements</span> Data <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">boolean</span> _ready <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
	<span style="color: #000000; font-weight: bold;">private</span> RealData _real_data <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #000066; font-weight: bold;">void</span> setRealData<span style="color: #009900;">&#40;</span>RealData realData<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>_ready<span style="color: #009900;">&#41;</span>
			<span style="color: #000000; font-weight: bold;">return</span><span style="color: #339933;">;</span>
		_real_data <span style="color: #339933;">=</span> realData<span style="color: #339933;">;</span>
		_ready <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
		notifyAll<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	@Override
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">synchronized</span> <span style="color: #003399;">String</span> getContent<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>_ready<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			<span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
				wait<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
			<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">InterruptedException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			<span style="color: #009900;">&#125;</span>
		<span style="color: #009900;">&#125;</span>
		<span style="color: #000000; font-weight: bold;">return</span> _real_data.<span style="color: #006633;">getContent</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

RealData类

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> RealData <span style="color: #000000; font-weight: bold;">implements</span> Data <span style="color: #009900;">&#123;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #003399;">String</span> _content<span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> RealData<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> count, <span style="color: #000066; font-weight: bold;">char</span> c<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"Making  Realdata("</span> 
		          <span style="color: #339933;">+</span> count <span style="color: #339933;">+</span> <span style="color: #0000ff;">","</span> <span style="color: #339933;">+</span> c <span style="color: #339933;">+</span> <span style="color: #0000ff;">") BEGIN"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #000066; font-weight: bold;">char</span><span style="color: #009900;">&#91;</span><span style="color: #009900;">&#93;</span> buffer <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #000066; font-weight: bold;">char</span><span style="color: #009900;">&#91;</span>count<span style="color: #009900;">&#93;</span><span style="color: #339933;">;</span>
		<span style="color: #000000; font-weight: bold;">for</span> <span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">int</span> i <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span> i <span style="color: #339933;">&lt;</span> count<span style="color: #339933;">;</span> i<span style="color: #339933;">++</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			buffer<span style="color: #009900;">&#91;</span>i<span style="color: #009900;">&#93;</span> <span style="color: #339933;">=</span> c<span style="color: #339933;">;</span>
			<span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
				<span style="color: #003399;">Thread</span>.<span style="color: #006633;">sleep</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">100</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
			<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">Exception</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			<span style="color: #009900;">&#125;</span>
		<span style="color: #009900;">&#125;</span>
		<span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">" making Real Data("</span> 
		          <span style="color: #339933;">+</span> count <span style="color: #339933;">+</span> <span style="color: #0000ff;">","</span> <span style="color: #339933;">+</span> c <span style="color: #339933;">+</span> <span style="color: #0000ff;">") END"</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		_content <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">String</span><span style="color: #009900;">&#40;</span>buffer<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	@Override
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #003399;">String</span> getContent<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">return</span> _content<span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

### 适用场景：

如果既想实现调用和执行分离，又想获取执行结果，适合使用Future模式。

Future模式可以获得异步方法调用的”返回值”，分离了”准备返回值”和”使用返回值”这两个过程。

### 注意事项：

Java 5并发包里已经有Future接口，不仅能获得返回结果，还能取消任务执行。当调用ExecutorService对象的submit方法向任务池提交一个Callable任务后，可获得一个Future对象，用于获取任务执行结果，并可取消任务执行。

## 10)Two-Phase Termination

这一节介绍如何停止线程，我们刚开始学习线程时，可能很容易犯的错就是调用Thread的stop方法停止线程，该方法确实能迅速停止线程，并会让线程抛出异常。但是调用stop方法是不安全的，如果该线程正获取了某个对象的锁，那么这个锁是不会被释放的，其他线程将继续被阻塞在该锁的条件队列里，并且也许线程正在做的工作是不能被打断的，这样可能会造成系统破坏。从线程角度看，只有执行任务的线程本身知道该何时恰当的停止执行任务，故此我们需要用Two-Phase Termination模式来停止线程，在该模式里如果想停止某个线程，先设置请求线程停止的标志为true，然后调用Thread的interrupt方法，在该线程里每完成一定工作会检查请求线程停止的标志，如果为true，则安全地结束线程。

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
35
36
37
38
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> CountupThread <span style="color: #000000; font-weight: bold;">extends</span> <span style="color: #003399;">Thread</span> <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">long</span> counter <span style="color: #339933;">=</span> <span style="color: #cc66cc;"></span><span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">volatile</span> <span style="color: #000066; font-weight: bold;">boolean</span> _shutdown_requested <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> shutdownRequest<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		_shutdown_requested <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
		interrupt<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">boolean</span> isShutdownRequested<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">return</span> _shutdown_requested<span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	@Override
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
			<span style="color: #000000; font-weight: bold;">while</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>_shutdown_requested<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
				doWork<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
			<span style="color: #009900;">&#125;</span>
		<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">InterruptedException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">finally</span> <span style="color: #009900;">&#123;</span>
			doShutdown<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> doWork<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #000000; font-weight: bold;">throws</span> <span style="color: #003399;">InterruptedException</span> <span style="color: #009900;">&#123;</span>
		counter<span style="color: #339933;">++;</span>
		<span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"doWork: counter = "</span> <span style="color: #339933;">+</span> counter<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #003399;">Thread</span>.<span style="color: #006633;">sleep</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">500</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000066; font-weight: bold;">void</span> doShutdown<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #003399;">System</span>.<span style="color: #006633;">out</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span><span style="color: #0000ff;">"doShutDown: counter = "</span> <span style="color: #339933;">+</span> counter<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

外界可调用shutdownRequest来停止线程。

### 适用场景：

需要停止线程时，可考虑使用Two-Phase Termination模式

### 注意事项：

我们在请求线程停止时，若只设置请求停止标志，是不够的，因为如果线程正在执行sleep操作，那么会等sleep操作执行完后，再执行到检查停止标志的语句才会退出，这样程序响应性不好。

响应停止请求的线程如果只检查中断状态(不是说我们设置的停止标志)也是不够的，如果线程正在sleep或者wait，则会抛出InterruptedException异常，就算没有抛出异常，线程也会变成中断状态，似乎我们没必要设置停止标志，只需检查InterruptedException或者用isInterrupted方法检查当前线程的中断状态就可以了，但是这样做会引入潜在的危险，如果该线程调用的方法忽略了InterruptedException，或者该线程使用的对象的某个方法忽略了InterruptedException，而这样的情况是很常见的，尤其是如果我们使用某些类库代码时，又不知其实现，即使忽略了InterruptedException，我们也不知道，在这种情况下，我们无法检查到是否有其它线程正在请求本线程退出，故此说设置终端标志是有必要的，除非能保证线程所引用的所有对象(包括间接引用的)不会忽略InterruptedException，或者能保存中断状态。

中断状态和InterruptedException可以互转:

1) 中断状态 -> InterruptedException

  * 1) 中断状态 -> InterruptedException
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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">if</span><span style="color: #009900;">&#40;</span><span style="color: #003399;">Thread</span>.<span style="color: #006633;">interrupted</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#123;</span>
<span style="color: #000000; font-weight: bold;">throw</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">InterruptedException</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 2) InterruptedException -> 中断状态
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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">try</span><span style="color: #009900;">&#123;</span>
	<span style="color: #003399;">Thread</span>.<span style="color: #006633;">sleep</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">1000</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span><span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">InterruptedException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
	<span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">interrupt</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 3) InterruptedException -> InterruptedException
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
        <pre class="java" style="font-family:monospace;"><span style="color: #003399;">InterruptedException</span> savedInterruptException <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
...
<span style="color: #000000; font-weight: bold;">try</span><span style="color: #009900;">&#123;</span>
	<span style="color: #003399;">Thread</span>.<span style="color: #006633;">sleep</span><span style="color: #009900;">&#40;</span><span style="color: #cc66cc;">1000</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span><span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">InterruptedException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
	savedInterruptException<span style="color: #339933;">=</span>e<span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span>
...
<span style="color: #000000; font-weight: bold;">if</span><span style="color: #009900;">&#40;</span>savedInterruptException <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #009900;">&#41;</span>
	<span style="color: #000000; font-weight: bold;">throw</span> savedInterruptException<span style="color: #339933;">;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 11)<a href="http://www.cloudchou.com/tag/thread-specific-storage" title="View all posts in Thread-Specific Storage" target="_blank" class="tags">Thread-Specific Storage</a>

我们知道，如果一个对象不会被多个线程访问，那么就不存在线程安全问题。Thread-Specific Storage模式就是这样一种设计模式，为每个线程生成单独的对象，解决线程安全问题。不过为线程生成单独的对象这些细节对于使用者来说是隐藏的，使用者只需简单使用即可。需要用到ThreadLocal类，它是线程保管箱，为每个线程保存单独的对象。

### 示例程序：

Log类

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
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> Log <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> ThreadLocal<span style="color: #339933;">&lt;</span>TSLog<span style="color: #339933;">&gt;</span> _ts_log_collection <span style="color: #339933;">=</span> 
	                      <span style="color: #000000; font-weight: bold;">new</span> ThreadLocal<span style="color: #339933;">&lt;</span>TSLog<span style="color: #339933;">&gt;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> println<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> s<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		getTSLog<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">println</span><span style="color: #009900;">&#40;</span>s<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">static</span> <span style="color: #000066; font-weight: bold;">void</span> close<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		getTSLog<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">close</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #000000; font-weight: bold;">static</span> TSLog getTSLog<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		TSLog tsLog <span style="color: #339933;">=</span> _ts_log_collection.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>tsLog <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			tsLog <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> TSLog<span style="color: #009900;">&#40;</span>
			 <span style="color: #003399;">Thread</span>.<span style="color: #006633;">currentThread</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span>.<span style="color: #006633;">getName</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">+</span> <span style="color: #0000ff;">"-log.txt"</span>
			 <span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
			_ts_log_collection.<span style="color: #006633;">set</span><span style="color: #009900;">&#40;</span>tsLog<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span>
		<span style="color: #000000; font-weight: bold;">return</span> tsLog<span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

TSLog类

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000000; font-weight: bold;">class</span> TSLog <span style="color: #009900;">&#123;</span>
	<span style="color: #000000; font-weight: bold;">private</span> <span style="color: #003399;">PrintWriter</span> _writer <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> TSLog<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> fileName<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		<span style="color: #000000; font-weight: bold;">try</span> <span style="color: #009900;">&#123;</span>
			_writer <span style="color: #339933;">=</span> <span style="color: #000000; font-weight: bold;">new</span> <span style="color: #003399;">PrintWriter</span><span style="color: #009900;">&#40;</span>fileName<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">catch</span> <span style="color: #009900;">&#40;</span><span style="color: #003399;">FileNotFoundException</span> e<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
			e.<span style="color: #006633;">printStackTrace</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
		<span style="color: #009900;">&#125;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> println<span style="color: #009900;">&#40;</span><span style="color: #003399;">String</span> s<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		_writer.<span style="color: #006633;">write</span><span style="color: #009900;">&#40;</span>s<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
&nbsp;
	<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> close<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
		_writer.<span style="color: #006633;">close</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
	<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

### 适用场景：

使用Thread-Specific Storgae模式可很好的解决多线程安全问题，每个线程都有单独的对象，如果从ThreadLocal类里获取线程独有对象的时间远小于调用对象方法的执行时间，可提高程序性能。因此在日志系统里如果可以为每个线程建立日志文件，那么特别适合使用Thread-Specific Storage模式。

### 注意事项：

采用Thread-Specific Storage模式意味着将线程特有信息放在线程外部，在示例程序里，我们将线程特有的TSLog放在了ThreadLocal的实例里。通常我们一般将线程特有的信息放在线程内部，比如建立一个Thread类的子类MyThread，我们声明的MyThread的字段，就是线程特有的信息。因为把线程特有信息放在线程外部，每个线程访问线程独有信息时，会取出自己独有信息，但是调试时会困难一些，因为有隐藏的context(当前线程环境)， 程序以前的行为，也可能会使context出现异常，而是造成现在的bug的真正原因，我们比较难找到线程先前的什么行为导致context出现异常。

设计多线程程序，主体是指主动操作的对象，一般指线程，客体指线程调用的对象，一般指的是任务对象，会因为重点放在“主体”与“客体”的不同，有两种开发方式：

  * 1) Actor-based 注重主体
  * 2) Task-based 注重客体

Actor-based 注重主体，偏重于线程，由线程维护状态，将工作相关的信息都放到线程类的字段，类似这样

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">class</span> Actor <span style="color: #000000; font-weight: bold;">extends</span> <span style="color: #003399;">Thread</span><span style="color: #009900;">&#123;</span>
操作者内部的状态
<span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#123;</span>
 从外部取得任务，改变自己内部状态的循环
<span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

Task-based注重客体，将状态封装到任务对象里，在线程之间传递这些任务对象，这些任务对象被称为消息，请求或者命令。使用这种开发方式的最典型的例子是Worker Thread 模式，生产者消费者模式。任务类似这样:

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
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">class</span> Task <span style="color: #000000; font-weight: bold;">implements</span> <span style="color: #003399;">Runnable</span><span style="color: #009900;">&#123;</span>
 执行任务所需的信息
 <span style="color: #000000; font-weight: bold;">public</span> <span style="color: #000066; font-weight: bold;">void</span> run<span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#123;</span> 
   执行任务所需的处理内容
 <span style="color: #009900;">&#125;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

实际上这两个开发方式是混用的，本人刚设计多线程程序时，总是基于Actor-based的思维方式，甚至在解决生产者消费者问题时也使用Actor-based思维方式，造成程序结构混乱，因此最好按实际场景来，适合使用Actor-based开发方式的就使用Actor-based，适合Task-based开发方式的就使用Task-based。