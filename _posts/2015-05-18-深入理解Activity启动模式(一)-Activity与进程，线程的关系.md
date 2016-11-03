---
   id: 755
   title: '深入理解Activity启动模式(一)&#8211;Activity与进程，线程的关系'
   date: 2015-05-18T09:10:03+08:00
   author: cloud
   layout: post
   guid: http://www.cloudchou.com/?p=755
   permalink: /android/post-755.html
   views:
     - 5018
   categories:
     - Android
     - 个人总结
   tags:
     - activity 进程 关系
     - activity启动模式
     - android activity process thread
     - android activity启动模式
     - android application process
   ---
<h2>概述</h2>
 <p>Android官网介绍Activity的启动模式时比较含糊，介绍Application，Activity，Task，Process，Thread等概念以及它们之间的关系时，也没有说得清楚。大家看了Android官网对Activity启动模式的介绍后，可能会觉得很困惑。官网介绍singleTask启动模式时，说只要启动singleTask启动模式的Activity就会新建Task，但在实际操作中，如果同一个应用的两个Activity，如果其中一个Activity的启动模式为singleTask，一个Activity的启动模式为standard，从其中一个Activity跳转到另外一个Activity，并不会新建Task。</p>
 <p>为了解除这些困惑，对Activity启动模式做了深入研究，因此写了这一系列博客，详细阐述Application，Activity，Task，Process，Thread等概念概念之间的关系，以及启动模式各自的特点，希望能对大家理解这些概念有所帮助。</p> 
 <p>本系列文章共分3篇:</p>
 <ul>
 <li><a href="http://www.cloudchou.com/android/post-755.html" target="_blank">深入理解Activity启动模式(一)--Activity与进程，线程的关系</a></li>
 <li><a href="http://www.cloudchou.com/android/post-760.html" target="_blank">深入理解Activity启动模式(二)--Activity,回退栈,Task之间的关系</a></li>
 <li><a href="http://www.cloudchou.com/android/post-768.html" target="_blank">深入理解Activity启动模式(三)--Activity启动模式特点</a></li>
 </ul>
 <h2>Application,Activity, Process,Thread之间的关系</h2>
 <p></p>
 <p>我们知道在AndroidManifest.xml里可声明Application，它可以由4大组件组成:Activity，Service，ContentProvider，BroadcastReceiver。声明Application时可以用android:name声明本应用使用的Application类，如果没有声明，则会直接使用Android框架的Application类建立实例对象。</p>
 <p>应用第一次启动时，会启动一个新进程，该进程用应用的包名作为进程名。该进程会启动主线程ActivityThread，也叫做UI线程，UI的绘制都在该线程里完成。该进程里还有一些Binder服务线程，用于和系统进行通信。</p>
 <p>另外，我们知道Activity跳转时，可以跨应用跳转，也就说应用app1里的Activity A可以跳转到应用app2里的Activity B。如果Activity A和Activity B的启动模式为standard模式，从A跳转到B后，Activity A和Activity B对应的ActivityRecord会放在同一个task里(ActivityRecord，Task都由系统进程管理，下一篇博客会介绍这些概念)，但是Acitivity A和Activity B的实例对象会放在不同的进程里。假设app1的包名为com.cloud.app1，app2的包名为com.cloud.app2，那么Activity A的实例对象位于进程com.cloud.app1里，Activity B的实例对象位于进程com.cloud.app2里。</p>
 <p>也就是说，每个应用的组件都会运行在对应的应用进程里，该进程用应用的包名作为进程名。该进程里有一个主线程，也叫做UI线程，应用组件都运行在UI线程里。只有一种情况例外，如果声明组件时用android:process设置了进程名，该组件就会运行在一个新进程里，不是以应用的包名作为进程名，而是用包名+:+设置的值作为进程名</p>
 <p>所以一般情况下service，receiver也会运行在ui线程里，如果在service，receiver的生命周期方法里做一些耗时的操作，系统会提示ANR(Activity Not Responde)错误。</p>
 
 
 
 
