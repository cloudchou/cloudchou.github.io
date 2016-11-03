---
id: 760
title: '深入理解Activity启动模式(二)&#8211;Activity,回退栈,Task之间的关系'
date: 2015-05-18T09:10:35+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=760
permalink: /android/post-760.html
views:
  - 3000
categories:
  - Android
  - 个人总结
tags:
  - Activity Task backstack之间的关系
  - Activity task 回退栈之间的关系
  - activity启动模式
  - android activity task
  - android activity启动模式
---
本系列文章共分3篇:

  * <a href="http://www.cloudchou.com/android/post-755.html" target="_blank">深入理解Activity启动模式(一)&#8211;Activity与进程，线程的关系</a>
  * <a href="http://www.cloudchou.com/android/post-760.html" target="_blank">深入理解Activity启动模式(二)&#8211;Activity,回退栈,Task之间的关系</a>
  * <a href="http://www.cloudchou.com/android/post-768.html" target="_blank">深入理解Activity启动模式(三)&#8211;Activity启动模式特点</a>

## Activity,回退栈,Task之间的关系

Activity启动时ActivityManagerService会为其生成对应的ActivityRecord记录，并将其加入到回退栈(back stack)中，另外也会将ActivityRecord记录加入到某个Task中。请记住，ActivityRecord，backstack，Task都是ActivityManagerService的对象，由system_server进程负责维护，而不是由应用进程维护。

在回退栈里属于同一个task的ActivityRecord会放在一起，也会形成栈的结构，也就是说后启动的Activity对应的ActivityRecord会放在task的栈顶。

假设Activity的跳转顺序:A&#8211;>B&#8211;>C，A,B,C对应的ActivityRecord属于同一个Task，此时从C跳转至D，再跳转至E，C和D不属于同一个Task，D和E属于同一个Task，那现在的back stack结构如下所示:

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_base.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_base.jpg" alt="backstack_base" width="215" height="268" class="aligncenter size-full wp-image-764" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_base.jpg 215w, http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_base-120x150.jpg 120w" sizes="(max-width: 215px) 100vw, 215px" /></a>

现在A,B,C属于task1,C在task1的栈顶，D,E属于task2，E在task2的栈顶。也可以看出来task2位于整个回退栈的栈顶，也就是说task2在task1的上面。如果此时不断按回退键，看到的Activity的顺序会是E&#8211;>D&#8211;>C&#8211;>B&#8211;>A。

另外需注意，ActivityManagerService不仅会往回退栈里添加新的ActivityRecord，还会移动回退栈里的ActivityRecord，移动时以task为单位进行移动，而不会移动单个AcitivityRecord。还是针对上面的例子，假设此时按了Home键，那么会将Home应用程序(也叫做Launcher应用程序)的task移动至栈顶，那么此时回退栈如下所示:

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_H.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_H.jpg" alt="backstack_H" width="212" height="312" class="aligncenter size-full wp-image-765" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_H.jpg 212w, http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_H-203x300.jpg 203w, http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_H-101x150.jpg 101w" sizes="(max-width: 212px) 100vw, 212px" /></a>

可以看到Home应用程序的Activity H对应的Activity Record移动到了回退栈的栈顶。Home应用程序的Activity H对回退按键的响应做了特殊处理，如果此时按回退键，是看不到Activity E的。

如果此时通过Launcher程序再打开Activity A所在的应用，那么会显示Activity C，因为会将Activity A对应的Activity Record所在的task移动至回退栈的栈顶，此时回退栈如下所示:

<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_move.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_move.jpg" alt="backstack_move" width="213" height="310" class="aligncenter size-full wp-image-763" srcset="http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_move.jpg 213w, http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_move-206x300.jpg 206w, http://www.cloudchou.com/wp-content/uploads/2015/05/backstack_move-103x150.jpg 103w" sizes="(max-width: 213px) 100vw, 213px" /></a>

现在task1移动到了栈顶，Home应用程序的task位于task1的下面，而task2位于Home应用程序的task之下，此时如果按返回键，那么Activity的显示顺序是:C&#8211;>B&#8211;>A&#8211;>H，不会显示E。

当然我们也可以在Launcher应用程序里打开D所在的应用，这样会将D,E所在的task2移动至栈顶。

现在应该对task有所理解了，task其实是由ActivityRecord组成的栈，多个task以栈的形式组成了回退栈，ActivityManagerService移动回退栈里的ActivityRecord时以task为单位移动。

我们知道跨应用跳转Activity时，两个Activity对应的ActivityRecord可属于同一个task，那什么情况下两个ActivityRecord会属于不同的task呢?或者说，Activity跳转时，什么情况下会产生新的task呢？

这个问题和Activity的启动模式，taskAffinity，启动Activity时为Intent设置的flag等因素相关。

先说一下taskAffinity，每个Activity的taskAffinity属性值默认为包名，也就是说如果Activity A所在的应用的包名为com.cloud.app1，那么Activity A的taskAffinity属性值为com.cloud.app1，我们可以在AndroidManifest.xml里通过android:taskAffinity属性为Activity设置特殊的taskAffinity，假设我们在AndroidManifest.xml里为Activity A设置了android:taskAffinity=”:test”，那么Activity A的taskAffinity值为com.cloud.app1:test。

那么我现在可以明白:不同应用的Activity的taskAffinity属性值会不一样。

假设Activity A和Activity B的启动模式都是standard，二者taskAffinity属性值不一样，从Activity A跳转至Activity B，那么它们对应的ActivityRecord会属于同一个task。

假设Activity A的启动模式是standard，Activity B的启动模式singleTask，二者taskAffinity属性值一样，此时从Activity A跳转至Activity B，那么它们对应的ActivityRecord会属于同一个task。因为只要两个Activity的taskAffinity属性一致，即使其中有一个Activity的启动模式为singleTask，它们对应的ActivityRecord会放在同一个task里，不管是从某个Activity跳转到singleTask类型的Activity，还是从singleTask类型的Activity跳转到其他Activity都是如此，除非跳转的其他Activity的启动模式是singleInstance。这里的描述和官方文档很不一样，稍后会为大家介绍singleTask启动模式的特点。

假设Activity A的启动模式是standard，Activity B的启动模式singleTask，二者taskAffinity属性值不 一样，此时从Activity A跳转至Activity B，那么它们对应的ActivityRecord会属于不同的Task。

还有其他很多情况会产生新的task，大家可以看接下来关于启动模式的特点的介绍。