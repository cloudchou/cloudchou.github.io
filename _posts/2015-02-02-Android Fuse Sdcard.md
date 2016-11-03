---
id: 697
title: Android Fuse Sdcard
date: 2015-02-02T11:58:42+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=697
permalink: /android/post-697.html
views:
  - 0
categories:
  - Android
  - 个人总结
tags:
  - /dev/fuse
  - Android fuse
  - Android fuse sdcard
  - 用户空间文件系统
---
<h2>什么是fuse</h2>
<p>用户空间文件系统（Filesystem in Userspace，简称FUSE）是操作系统中的概念，指完全在用户态实现的文件系统。Linux通过内核模块对此进行支持。文件系统是一个通用操作系统重要的组成部分。传统上操作系统在内核层面上对文件系统提供支持。而通常内核态的代码难以调试，生产率较低。Linux从2.6.14版本开始通过FUSE模块支持在用户空间实现文件系统。在用户空间实现文件系统能够大幅提高生产率，简化了为操作系统提供新的文件系统的工作量，特别适用于各种虚拟文件系统和网络文件系统。但是，在用户态实现文件系统必然会引入额外的内核态/用户态切换带来的开销，对性能会产生一定影响。</p>

<p>Android利用fuse技术实现虚拟的Sd卡。</p>
<h2>如何获取fuse设备对应的真实设备</h2>
<p>可通过如下命令查看是否有fuse设备：</p>
```bash
$mount | grep fuse
$/dev/fuse /storage/sdcard0 fuse rw,nosuid,nodev,relatime,user_id=1023,group_id=1 023,default_permissions,allow_other 0 0
```
<p>可看到该系统上使用了fuse设备，Android上fuse的实现必定使用sdcard daemon服务，它们会添加在init.rc里，格式如下所示：</p>
```bash
service fuse_sdcard0 /system/bin/sdcard -u 1023 -g 1023 -d /mnt/media_rw/sdcard0 /storage/sdcard0
   class late_start
   disabled
```
<p>因此我们可以通过获取sdcard daemon执行时的命令行参数得到被映射的路径,命令：</p>
```bash
$ps | grep /system/bin/sdcard
$ media_rw  1106  1     4080   944   ffffffff b6fa87c0 S /system/bin/sdcard
$cat /proc/1106/cmdline
/system/bin/sdcard  -u 1023 -g 1023 -d /mnt/media_rw/sdcard0 /storage/sdcard0
```
<p>由此可以知道，其实是将目录/mnt/media_rw/sdcard0 映射到了 /storage/sdcard0目录，我们再看是哪个目录挂载至/mnt/media_rw/scard0</p>
```bash
$mount | grep media_rw
/dev/block/vold/179:29 /mnt/media_rw/sdcard0 vfat rw,dirsync,nosuid,nodev,noexec,relatime,uid=1023,gid=1023,fmask=0007,dmask=0007,allow_utime=0020,codepage=cp437,iocharset=iso8859-1,shortname=mixed,utf8,errors=remount-ro 0 0
```
<p>因此我们可知道是/dev/block/vold/179:29 这个设备，179是主设备号，29是次设备号，再读取/proc/partitions</p>
```bash
179       18      10240 mmcblk0p18
 179       19    1048576 mmcblk0p19
 179       20    2097152 mmcblk0p20
 179       21       8192 mmcblk0p21
 179       22     524288 mmcblk0p22
 179       23       1024 mmcblk0p23
 179       24      10240 mmcblk0p24
 179       25      32768 mmcblk0p25
 179       26       8192 mmcblk0p26
 179       27       8192 mmcblk0p27
 179       28      32768 mmcblk0p28
 179       29   11358191 mmcblk0p29
```
<p>我们可知道真实设备其实是/dev/block/mmcblk0p29</p>
<p>故此知道/dev/fuse 挂载至/storage/sdcard0目录，使用的真实设备是/dev/block/mmcblk0p29</p>

<h2>sdcard程序变更历史</h2>
```bash
1. sdcard <path> <uid> <gid>
2. sdcard [-l] [-f]<path> <uid> <gid>
3. sdcard [-t<threads>] <source_path> <dest_path> <uid> <gid>
4. sdcard [OPTIONS] <source_path> <dest_path>
 -u: specify UID to run as
 -g: specify GID to run as
 -t: specify number of threads to use (default %d)
 -d: derive file permissions based on path
5. usage: sdcard [OPTIONS] <source_path> <dest_path>
   -u: specify UID to run as
   -g: specify GID to run as
   -G: specify default GID for files (default sdcard_r, requires -d or -l)
   -t: specify number of threads to use (default %d)
   -d: derive file permissions based on path
   -l: derive file permissions based on legacy internal layout
   -s: split derived permissions for pics, av
6. sdcard [OPTIONS] <source_path> <dest_path>
   -u: specify UID to run as
   -g: specify GID to run as
   -w: specify GID required to write (default sdcard_rw)
   -t: specify number of threads to use (default %d)
   -d: derive file permissions based on path
   -l: derive file permissions based on legacy internal layout
   -s: split derived permissions for pics, av (requires -d or -l)  
```
