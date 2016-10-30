---
id: 307
title: 使用gdb core分析Android程序的segment fault
date: 2014-03-02T17:01:03+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=307
permalink: /android/post-307.html
views:
  - 5796
categories:
  - Android
tags:
  - Android core dump 分析
  - android gdb core dump
  - android gdb 调试
  - android gdb 调试 core
  - android segmentation fault
---
我们开发Android本地可执行程序时，常常遇见segment fault错误，若程序比较复杂，使用打日志的方式很难查到出错的根本原因，若能让程序出core，然后用gdb 调试该core文件将能很快定位出错的代码位置，并能看到运行时出错代码的运行栈，这样能迅速定位。

## 1. core dump

那什么是core dump呢，core dump是指当程序运行崩溃的瞬间，内核会抛出当时该程序进程的内存详细情况，存储在一个core.xxx的文件中，Android默认设置情况下，程序运行出错后是不会出core的，需要进行以下设置：

  * ### 1) 设置core文件的存储位置
    
    echo &#8220;/data/coredump/core.%e.%p&#8221; > /proc/sys/kernel/core_pattern 
    
    表示存储在 /data/coredump 下，%e表示程序的名字，%p是指进程号， 示例：core.adbd.235
    
    若不设置core文件的存储位置，core文件将保存在程序运行时的工作目录下，文件名是core
    
    若想系统启动时自动设置core文件的存储位置(这样不用每次开机都需要重新设置),可以在根文件系统的init.rc里添加命令：
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="code">
            <pre class="txt" style="font-family:monospace;">on init
  ...
  write  /proc/sys/kernel/core_pattern /data/coredump/core.%e.%p
  ...</pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 2) 设置core文件大小限制
    
    默认情况下系统限制core文件大小为0，此时程序运行出错无法出core,若使用ulimit -c命令查看，可以看到结果是0，这时候可用ulimit -c unlimited 设置core文件大小无限制，此时运行程序出错后，便可以出Core了。但是请<span style="color:red">注意</span>使用ulimit命令修改core限制，<span style="color:red">只针对此次会话有效</span>，也就是说你使用adb shell 设置好后，在另外一个终端里运行adb shell后，再运行程序出错，还是不会出Core。
    
    若想对所有会话都有效，需要在系统启动时，就进行这样的设置。但是ulimit是一个shell内置命令，故此不能在init.rc里添加调用ulimit命令的服务来解决该问题，此时有三种解决方法，修改现有init.rc里的服务对应程序的源代码，或者修改init的源代码，或者编写一个本地程序，并在init.rc添加一个服务调用该程序，取消core文件大小限制的关键代码如下：
    
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
            <pre class="c" style="font-family:monospace;"><span style="color: #993333;">struct</span> rlimit lim<span style="color: #339933;">;</span>
lim.<span style="color: #202020;">rlim_cur</span><span style="color: #339933;">=</span>RLIM_INFINITY<span style="color: #339933;">;</span>
lim.<span style="color: #202020;">rlim_max</span><span style="color: #339933;">=</span>RLIM_INFINITY<span style="color: #339933;">;</span>	 
setrlimit<span style="color: #009900;">&#40;</span>RLIMIT_CORE<span style="color: #339933;">,&</span>lim<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> <span style="color: #666666; font-style: italic;">//出core</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    你可以将该段代码添加到你的本地程序里或者init源代码，或者服务程序源代码里。这样系统启动后，程序异常退出时，便会出core。此种方式对调试adbd程序非常有帮助。

## 2. 使用gdb调试出Core的程序

调试出现segment fault的本地程序时，别使用优化后的程序，这样使用gdb调试时不能看到源代码，都是一堆的二进制代码。Android源代码开发时，优化前的程序位于目录out/target/product/m7cdug/symbols下(m7cdwg是某个产品)，你可以在该目录下使用find 命令查找你要调试的程序: find -name &#8220;progname&#8221;。

程序出core后，使用adb pull将core文件从手机上拉下来，再将该文件放置到源代码开发主机的优化前程序所处目录下。如果你在编译Android源代码，并使用了source build/envsetup.sh，此时在编译源代码的终端可以运行arm-eabi-gdb命令来调试core文件，若找不到该命令，先将该命令所在目录添加到PATH目录。调试core文件的命令：arm-eabi-gdb 被调试程序 core，示例:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;">arm-eabi-gdb adbd core.adbd.235</pre>
      </td>
    </tr>
  </table>
</div>

<p style="color:red">
  注意:
</p>

使用该命令时，可能会出现问题：libpython2.6.so.1.0: cannot open shared object file，此时需要安装 python 2.6 

先下载python 2.6并解压，<a href="http://www.python.org/ftp/python/2.6/Python-2.6.tar.bz2" target="_blank">http://www.python.org/ftp/python/2.6/Python-2.6.tar.bz2</a>

编译并安装

<div class="wp_syntax">
  <table>
    <tr>
      <td class="code">
        <pre class="bash" style="font-family:monospace;">.<span style="color: #000000; font-weight: bold;">/</span>configure <span style="color: #660033;">--prefix</span>=<span style="color: #000000; font-weight: bold;">/</span>opt<span style="color: #000000; font-weight: bold;">/</span>python26 <span style="color: #660033;">--enable-shared</span> <span style="color: #660033;">--enable-unicode</span>=ucs4 <span style="color: #666666; font-style: italic;">#安装至/opt/python26</span>
<span style="color: #c20cb9; font-weight: bold;">make</span> <span style="color: #000000; font-weight: bold;">&&</span> <span style="color: #c20cb9; font-weight: bold;">sudo</span> <span style="color: #c20cb9; font-weight: bold;">make</span> <span style="color: #c20cb9; font-weight: bold;">install</span> 
<span style="color: #c20cb9; font-weight: bold;">sudo</span> <span style="color: #c20cb9; font-weight: bold;">ln</span> <span style="color: #660033;">-s</span>  <span style="color: #000000; font-weight: bold;">/</span>opt<span style="color: #000000; font-weight: bold;">/</span>python26<span style="color: #000000; font-weight: bold;">/</span>lib<span style="color: #000000; font-weight: bold;">/</span>libpython2.6.so.1.0   <span style="color: #000000; font-weight: bold;">/</span>usr<span style="color: #000000; font-weight: bold;">/</span>lib<span style="color: #000000; font-weight: bold;">/</span>libpython2.6.so.1.0 <span style="color: #666666; font-style: italic;">#软链接</span></pre>
      </td>
    </tr>
  </table>
</div>

调试时比较常用的命令：

bt：查看异常时的堆栈，使用gdb调试Core文件时，一般用该命令先查看出错的源代码位置 

list: 查看当前堆栈指针指向的源代码的前后共10行代码

up n: 堆栈指针往上移动n层

down n:堆栈指针往下移动n层

frame: 查看堆栈指针指向当前堆栈的位置

print: 查看某个变量 示例：print a