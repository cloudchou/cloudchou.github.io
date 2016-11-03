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
<p>调试Android程序时，经常不能看到日志，而DDMS输出Unable to open log device '/dev/log/main': No such file or directory</p>
<p>解决这个问题，目前有3种办法：</p>

1.使用拨号键盘
<p>1) 拨号盘中输入：   *#*#2846579#*#* </p>
<p>2) 然后         MMITEST_II ->->ProjectMenu -> 后台设置</p>
<p>3) Log 设置-> LOG开关 -> 开， Dump &Log -> 勾上全部的 </p>
<p>4) 重启设备</p>
2.Speedmod 内核问题
<p>Speedmod 内核默认不打开Android log功能，需要修改/system/etc/tweaks.conf文件，命令如下所示：</p>
<p>adb shell</p>
```bash
$su
#mount -o remount,rw /system
#echo ANDROIDLOGGER >> /system/etc/tweaks.conf
#mount -o remount,ro /system
#reboot
```
3./system/etc/init.d目录下的脚本删掉了日志设备
<p>使用命令找到删除日志设备的脚本</p>
<p>adb shell</p>
```bash
$su
# cd /system/etc/init.d && grep -r "rm /dev/log/main" ./
```
<p>找到该文件后</p>
<p>编辑该文件，可通过将该文件拷贝到电脑上，修改完成后再上传到手机，</p>
```bash
# cp /system/etc/init.d/S20bb /data/local/tmp
```
<p>adb pull /system/etc/init.d/S20bb</p>
<p>使用文本编辑工具编辑S20bb，找到 “rm /dev/log/main” (不含引号)这一行，然后像下面一样注释该语句</p>
<p># rm /dev/log/main</p>
<p>然后再把S20bb上传至手机</p>
<p>adb push S20bb /data/local/tmp/S20bb</p>
<p>adb shell cp /data/local/tmp/S20bb /system/etc/init.d/S20bb</p>
<p>重启手机即可</p>

