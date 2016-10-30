---
id: 687
title: linux共享挂载和从属挂载
date: 2014-12-09T12:11:21+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=687
permalink: /%e4%b8%aa%e4%ba%ba%e6%80%bb%e7%bb%93/post-687.html
views:
  - 1600
categories:
  - 个人总结
tags:
  - linux从属挂载
  - linux共享挂载
  - 从属挂载
  - 共享挂载
  - 挂载分类
---
<a href="http://www.cloudchou.com/tag/%e6%8c%82%e8%bd%bd%e5%88%86%e7%b1%bb" title="View all posts in 挂载分类" target="_blank" class="tags">挂载分类</a>：

  * ### 1)<a href="http://www.cloudchou.com/tag/%e5%85%b1%e4%ba%ab%e6%8c%82%e8%bd%bd" title="View all posts in 共享挂载" target="_blank" class="tags">共享挂载</a> 
    
    某个目录已经是挂载点了，可以通过下述命令将该目录变成共享的挂载目录：
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
</pre>
          </td>
          
          <td class="code">
            <pre class="bash" style="font-family:monospace;"><span style="color: #c20cb9; font-weight: bold;">mount</span> <span style="color: #660033;">--make-shared</span> <span style="color: #000000; font-weight: bold;">/</span>mnt</pre>
          </td>
        </tr>
      </table>
    </div>
    
    再通过bind选项将挂载点绑定到另一个目录，
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
</pre>
          </td>
          
          <td class="code">
            <pre class="bash" style="font-family:monospace;"><span style="color: #c20cb9; font-weight: bold;">mount</span> <span style="color: #660033;">--bind</span> <span style="color: #000000; font-weight: bold;">/</span>mnt <span style="color: #000000; font-weight: bold;">/</span>tmp</pre>
          </td>
        </tr>
      </table>
    </div>
    
    这样在mnt下的任何文件变化都会反应到tmp目录下，tmp目录下的任何变化也会反映到mnt目录
    
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
            <pre class="bash" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">#ls /mnt</span>
a b c
<span style="color: #666666; font-style: italic;">#ls /tmp</span>
a b c</pre>
          </td>
        </tr>
      </table>
    </div>
    
    甚至在mnt目录的某个子目录挂载新的文件系统，也会反应在tmp子目录下，在tmp某个子目录下挂载新的文件系统也会反应到mnt目录
    
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
            <pre class="bash" style="font-family:monospace;"><span style="color: #666666; font-style: italic;">#mount /dev/sd0  /tmp/a</span>
<span style="color: #666666; font-style: italic;">#ls /tmp/a</span>
t1 t2 t3
<span style="color: #666666; font-style: italic;">#ls /mnt/a</span>
t1 t2 t3</pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 2)<a href="http://www.cloudchou.com/tag/%e4%bb%8e%e5%b1%9e%e6%8c%82%e8%bd%bd" title="View all posts in 从属挂载" target="_blank" class="tags">从属挂载</a>
    
    从属挂载和共享挂载是类似的，只是mount和umount事件知会从主挂载传递到从属挂载，从属挂载的mount事件并不会通知到主挂载。
    
    另外注意从属挂载是基于共享挂载的，从属挂载的主挂载肯定是一个共享挂载。Android就是利用了从属挂载这个特性，隐藏某些挂载来为不同用户挂载不同的挂载点。
    
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
            <pre class="bash" style="font-family:monospace;"><span style="color: #666666; font-style: italic;"># mount --make-shared /mnt</span>
<span style="color: #666666; font-style: italic;"># mount --bind /mnt /tmp</span>
<span style="color: #666666; font-style: italic;"># mount --make-slave /tmp</span>
<span style="color: #666666; font-style: italic;"># mount /dev/sd0 /mnt/a</span>
<span style="color: #666666; font-style: italic;"># ls /mnt/a</span>
  t1 t2 t3
<span style="color: #666666; font-style: italic;"># mount /dev/sd1 /tmp/b</span>
<span style="color: #666666; font-style: italic;">#ls /tmp/b</span>
   s1 s2 s3   
<span style="color: #666666; font-style: italic;">#ls /mnt/b</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    由上可知挂载点/mnt的mount事件通知到了挂载点/tmp，但是挂载点/tmp的挂载事件并未通知到/mnt

  * ### 3)私有挂载
    
    这是我们平常熟悉的挂载方式，是默认类型

  * ### 4)不能绑定的挂载是不可绑定的私有挂载
    
    假设我们一个挂载/mnt，我们将它设置为不可绑定
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
</pre>
          </td>
          
          <td class="code">
            <pre class="bash" style="font-family:monospace;"><span style="color: #666666;"># </span><span style="color: #c20cb9; font-weight: bold;">mount</span> <span style="color: #660033;">--make-unbindable</span> <span style="color: #000000; font-weight: bold;">/</span>mnt</pre>
          </td>
        </tr>
      </table>
    </div>
    
    我们此时如果再去将它绑定给另一个目录
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
</pre>
          </td>
          
          <td class="code">
            <pre class="bash" style="font-family:monospace;"><span style="color: #666666;">#</span><span style="color: #c20cb9; font-weight: bold;">mount</span> <span style="color: #660033;">--bind</span> <span style="color: #000000; font-weight: bold;">/</span>mnt <span style="color: #000000; font-weight: bold;">/</span>tmp</pre>
          </td>
        </tr>
      </table>
    </div>
    
    此时便会出错，提示：
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
</pre>
          </td>
          
          <td class="code">
            <pre class="bash" style="font-family:monospace;">mount: wrong fs <span style="color: #7a0874; font-weight: bold;">type</span>, bad option, bad superblock on <span style="color: #000000; font-weight: bold;">/</span>mnt,or too many mounted <span style="color: #c20cb9; font-weight: bold;">file</span> systems</pre>
          </td>
        </tr>
      </table>
    </div>