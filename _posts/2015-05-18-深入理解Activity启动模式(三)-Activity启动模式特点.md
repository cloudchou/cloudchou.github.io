---
id: 768
title: '深入理解Activity启动模式(三)&#8211;Activity启动模式特点'
date: 2015-05-18T09:10:46+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=768
permalink: /android/post-768.html
views:
  - 2729
categories:
  - Android
  - 个人总结
tags:
  - activity启动模式特点
  - activity启动模式详解
  - android activity launchmode
  - android activity启动模式
---
<p>本系列文章共分3篇:</p>
<ul>
<li><a href="http://www.cloudchou.com/android/post-755.html" target="_blank">深入理解Activity启动模式(一)--Activity与进程，线程的关系</a></li>
<li><a href="http://www.cloudchou.com/android/post-760.html" target="_blank">深入理解Activity启动模式(二)--Activity,回退栈,Task之间的关系</a></li>
<li><a href="http://www.cloudchou.com/android/post-768.html" target="_blank">深入理解Activity启动模式(三)--Activity启动模式特点</a></li>
</ul>
<h2>Activity 启动模式特点</h2>
 
<p>Activity的启动模式共有4种，默认为standard，其它还有singleTop，singleTask，singleInstance，下面就这4种启动模式分别介绍它们的特点。</p>
<ul>
<li>
 <h3>1)\tstandard模式</h3>
 <p>standard模式的Activity可以有多个ActivityRecord加入不同的task，同一个task也可存在多个ActivityRecord，并且ActivityRecord还可相邻。</p>
 <p>假设Activity A的启动模式为standard，那么可能存在如下图所示的回退栈:</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/standard.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/standard.png" alt="standard" width="194" height="279" class="aligncenter size-full wp-image-778" /></a>
 <p>假设Activity A启动Activity B，B的启动模式为standard模式</p>
 <p>B的ActivityRecord默认会放在A的ActivityRecord所在的task里，即使B和A的taskAffinity不同也会如此，这也意味着如果B和A属于不同的应用，B的ActivityRecord也会放在A的ActivityRecord所在的task里。</p>
 <p>但是下面两种情况不会将A和B的ActivityRecord放在同一个task里:</p>
 <p>如果Activity A的启动模式为singleInstance，则会查找整个回退栈，直到找到和B相关的task，然后把B的ActivityRecord放到该task里，如果没有找到相关的task，则新建task，将B的ActivityRecord放到新task里。后面会介绍如何判断Activity和某个task相关。</p>
 <p>如果Activity A的启动模式为singleTask，并且Activity A和Activity B的taskAffinity不一样，那么也会查找整个回退栈，直到找到和B相关的task，然后把B的ActivityRecord放到该task里。</p>

</li>
<li>
 <h3>2)\tsingleTop模式</h3>
 <p>singleTop模式与standard模式比较相似，singleTop模式的Activity可以有多个ActivityRecord加入不同的task，同一个task也可存在多个ActivityRecord,但是同一个task的ActivityRecord不可以相邻。</p>
 <p>假设Activity A的启动模式为singleTop，那么如下图所示的回退栈就是不合理的:</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/05/singleTop_bad.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/singleTop_bad.png" alt="singleTop_bad" width="213" height="310" class="aligncenter size-full wp-image-776" /></a>
 <p>但是可存在如下图所示的回退栈:</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/05/singleTop_good.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/singleTop_good.png" alt="singleTop_good" width="176" height="255" class="aligncenter size-full wp-image-777" /></a>
 <p>假设Activity A启动了Activity B， 这时B在task的栈顶，B的启动模式为singleTop模式。此时从其它Activity也跳转至Activity B，并且启动的task也是已启动的A和B所在的task，或者A和 B所在的task本身就回退栈的栈顶，那么不会新建B的ActivityRecord，而是会将启动Activity B的Intent传递给栈顶Activity B的ActivityRecrod对应的在应用进程的实例对象，调用它的onNewIntent方法。</p>
 <p>可以这样模拟此种情况:</p>
 <p>假设Activity A和Activity B在同一个应用app1里，A是入口Activity，A可跳转至Activity B，B的启动模式为singleTop。此时已从A跳转至B，通知栏有一个启动B的通知，点击通知后，就出现上述情况。</p>
</li>
<li>
 <h3>3)\tsingleTask模式</h3>
 <p>singleTask模式和standard模式，singleTop模式区别很大，singleTask模式的Activity在整个回退栈只可以有一个ActivityRecord，也就是说它只能属于某一个task，不可在多个task里存在ActivityRecord。但是在这个task里可以有其它Activity的ActivityRecord。</p>
 <p>假设Activity A的启动模式为singleTask，那么如下图所示的回退栈就是不合理的:</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/05/singleTask_bad.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/singleTask_bad.png" alt="singleTask_bad" width="172" height="249" class="aligncenter size-full wp-image-774" /></a>
 <p>假设Activity A的启动模式为singleTask，那么如下图所示的回退栈就是合理的:</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/singleTask_good.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/singleTask_good.png" alt="singleTask_good" width="179" height="261" class="aligncenter size-full wp-image-775" /></a>
 <p>假设Activity A的启动模式为singleTask，那么和Activity A的ActivityRecord放在同一个task里的ActivityRecord所对应的Activity，必须与Activity A的taskAffinity相同。也就是说，Activity A的ActivityRecord只会和同一应用的其它Activity的ActivityRecord放在同一个task里，并且这些同一应用的其它Activity不能设置特殊的taskAffinity。</p>
 <p>singleTask模式的Activity还有另一个特点:</p>
 <p>假设Activity A的启动模式是singleTask，A所在的task里，A并没有处于栈顶，此时若从别的Activity跳转至Activity A，那么A所在的task里位于A之上的所有ActivityRecord都会被清除掉。</p>
 
 <p>跳转之前回退栈的示意图如下所示:</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/singeleTask_before.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/singeleTask_before.png" alt="singeleTask_before" width="174" height="251" class="aligncenter size-full wp-image-770" /></a>
 <p>此时从E跳转至A之后，回退栈的示意图如下图所示:</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/05/afterjump.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/afterjump.png" alt="afterjump" width="204" height="292" class="aligncenter size-full wp-image-885" /></a>
 <p>也就是说位A所在的task里的C被清除了。</p>
 <p>另外需注意:</p>
 <p>只要两个Activity的taskAffinity属性一致，即使其中有一个Activity的启动模式为singleTask，它们对应的ActivityRecord会放在同一个task里，不管是从某个Activity跳转到singleTask类型的Activity，还是从singleTask类型的Activity跳转到其他Activity都是如此，除非跳转的其他Activity的启动模式是singleInstance。Android官方文档对singleTask启动模式的描述不准确。</p>
 <p>举例如下:</p>
 <p>假设某个应用有两个Activity A和Activity B，Activity A已启动，Activity B的启动模式为singleTask，Activity B还从未启动过，在AndroidManifest.xml里没有给这两个Activity设置特殊的taskAffinity。此时从Activity A跳转至Activity B，那么Activity B的ActivityRecord会放在Activity A的ActivityRecord所在的task里。</p>
</li>
<li>
 <h3>4)\tsingleInstance模式</h3>
 <p>该启动模式和singleTask类似，singleInstance模式的Activity在整个回退栈只可以有一个ActivityRecord，也就是说它只能属于某一个task，不可在多个task里存在ActivityRecord，并且它所在的task不可再有其它Activity的ActivityRecord，即使是同一个应用内的其它Activity，也不可有它们的AcvitityRecord。</p>
 <p>假设Activity A的启动模式为singleInstance，那么如下图所示的回退栈就是不合理的:</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/05/singleInstance_bad.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/singleInstance_bad.png" alt="singleInstance_bad" width="197" height="283" class="aligncenter size-full wp-image-771" /></a>
 <p>假设Activity A的启动模式为singleInstance，那么如下图所示的回退栈就是合理的:</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2015/05/singleInstance_good.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/05/singleInstance_good.png" alt="singleInstance_good" width="209" height="303" class="aligncenter size-full wp-image-772" /></a>
</li>
</ul>
 
<p>启动Activity时，有时需要查看回退栈，看是否有和这个Activity相关的task。Activity和某个task相关，有两种情况(假设Activity为A，相关的task为task1):</p>
<ul>
<li>1)\t如果A的启动模式为singleInstance，那么task1只能包含1个ActivityRecord，并且ActivityRecord对应的Activity必须是A </li>
<li>2)\tA的启动模式不是singleInstance，A的taskAffinity属性和task1的taskAffinity属性必须一样。Task的taskAffinity属性由它包含的第1个ActivityRecord的taskAffinity属性决定。</li>
</ul>

<h2>注意</h2>
<ul>
<li>1)\t从Launcher程序启动应用时，会先查找所有task，看是否有相关task，如果已有相关task，则会将相关task移动到回退栈的栈顶，然后显示栈顶Activity。查找相关task时，需看task是否和应用的入口Activity相关，入口Activity是指在AndroidManifest.xml里声明IntentFilter时，注明category为android.intent.category.LAUNCHER的Activity。如果入口Activity的启动模式为singleTask，不仅会将相关task移动到回退栈的栈顶，还会将该task里位于入口Activity之上的其它ActivityRecord全部清除掉</li>
<li>2)\t通过最近应用程序，切换应用时，会直接将应用图标对应的task移动到回退栈的栈顶，这样即使task里有singleTask类型的ActivityRecord，在它之上的ActivityRecord也不会被清除</li>
<li>3)\t可以通过adb shell dumpsys activity activties查看系统task情况</li>
</ul>

<h2>思考问题</h2>
<p>相信大家看了这3篇博客以后，可以回答如下关于哪些情况下会产生新task的问题了</p>
<ul>
<li>1) 首次启动应用，是否会产生新的task?</li>
<li>2) 假设应用app1的入口Activity(Activity A)启动模式为standard,从A可跳转至Acitivity B，Activity B的启动模式为singleTask，那么启动应用后，从ActivityA跳转到ActivityB是否会产生新的task?</li>
<li>3) 假设应用app1的入口Activity是A,从A可跳转至B，从B可跳转至C,B的启动模式为singleTask，A和C的启动模式为standard，Activity的跳转顺序为A->B->C是否会产生新的task? 如果C的启动模式也为singleTask呢？ 如果C的启动模式为singleInstance呢?</li>
<li>4) 假设应用app1的入口Activity是A,从A可跳转至B, B的启动模式为singleTask，A的启动模式为standard,另一个应用app2有一个Activity C，C的启动模式为stanard，C也可跳转至B,目前已从A跳转到B，此时再打开应用app2，从C跳转至B,是否会产生新的task呢？ 如果应用app1没启动，是否会产生新的task呢?</li>
<li>5) 假设应用app1的入口Activity是A,从A可跳转至B,从B可跳转至C， B的启动模式为singleTask，A,C的启动模式为standard，从A跳转至B后，A会finish，假设此时A已跳转至B，B已跳转至C，此时通知栏有一个通知，可启动Activity B，那么点击通知后，会出现什么情况呢?</li>
</ul>
