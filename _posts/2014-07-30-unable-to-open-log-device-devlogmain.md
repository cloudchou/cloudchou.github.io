---
id: 646
title: 'Unable to open log device &#8216;/dev/log/main&#8217;'
date: 2014-07-30T14:40:39+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=646
permalink: /android/post-646.html
views:
  - 2012
categories:
  - Android
tags:
  - android 无法查看日志
  - android 日志设备打不开
  - Unable to open log device
  - 无法查看日志
---
调试Android程序时，经常不能看到日志，而DDMS输出<a href="http://www.cloudchou.com/tag/unable-to-open-log-device" title="View all posts in Unable to open log device" target="_blank" class="tags">Unable to open log device</a> &#8216;/dev/log/main&#8217;: No such file or directory

解决这个问题，目前有3种办法：

  * 1.使用拨号键盘
1) 拨号盘中输入： \*#\*#2846579#\*#\* 

2) 然后 MMITEST_II ->->ProjectMenu -> 后台设置

3) Log 设置-> LOG开关 -> 开， Dump &#038;Log -> 勾上全部的 

4) 重启设备

  * 2.Speedmod 内核问题
Speedmod 内核默认不打开Android log功能，需要修改/system/etc/tweaks.conf文件，命令如下所示：

adb shell

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
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">$su</span>
<span style="color: #666666; font-style: italic;">#mount -o remount,rw /system</span>
<span style="color: #666666; font-style: italic;">#echo ANDROIDLOGGER &gt;&gt; /system/etc/tweaks.conf</span>
<span style="color: #666666; font-style: italic;">#mount -o remount,ro /system</span>
<span style="color: #666666; font-style: italic;">#reboot</span></pre>
      </td>
    </tr>
  </table>
</div>

  * 3./system/etc/init.d目录下的脚本删掉了日志设备
使用命令找到删除日志设备的脚本

adb shell

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">$su</span>
<span style="color: #666666; font-style: italic;"># cd /system/etc/init.d && grep -r "rm /dev/log/main" ./</span></pre>
      </td>
    </tr>
  </table>
</div>

找到该文件后

编辑该文件，可通过将该文件拷贝到电脑上，修改完成后再上传到手机，

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #666666;"># </span><span style="color: #c20cb9; font-weight: bold;">cp</span> <span style="color: #000000; font-weight: bold;">/</span>system<span style="color: #000000; font-weight: bold;">/</span>etc<span style="color: #000000; font-weight: bold;">/</span>init.d<span style="color: #000000; font-weight: bold;">/</span>S20bb <span style="color: #000000; font-weight: bold;">/</span>data<span style="color: #000000; font-weight: bold;">/</span>local<span style="color: #000000; font-weight: bold;">/</span>tmp</pre>
      </td>
    </tr>
  </table>
</div>

adb pull /system/etc/init.d/S20bb

使用文本编辑工具编辑S20bb，找到 “rm /dev/log/main” (不含引号)这一行，然后像下面一样注释该语句

\# rm /dev/log/main

然后再把S20bb上传至手机

adb push S20bb /data/local/tmp/S20bb

adb shell cp /data/local/tmp/S20bb /system/etc/init.d/S20bb

重启手机即可