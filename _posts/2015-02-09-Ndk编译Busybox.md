---
id: 701
title: Ndk编译Busybox
date: 2015-02-09T10:48:42+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=701
permalink: /android/post-701.html
views:
  - 2708
categories:
  - Android
  - 个人总结
tags:
  - android busybox
  - busybox ?
  - busybox illegal instruction
  - ndk 编译 busybox
  - 编译busybox
---
## 概述

本篇讲述如何在Linux下使用Ndk<a href="http://www.cloudchou.com/tag/%e7%bc%96%e8%af%91busybox" title="View all posts in 编译busybox" target="_blank" class="tags">编译busybox</a>源码，生成一个静态链接的兼容性好的可支持中文的busybox。busybox是静态链接的，所以busybox可以既在recovery模式下运行，也可以在系统模式下运行，解决busybox not found的问题。busybox兼容性好，使用ndk编译，可以在armv7和armv5的cpu上运行，解决了<a href="http://www.cloudchou.com/tag/busybox-illegal-instruction" title="View all posts in busybox illegal instruction" target="_blank" class="tags">busybox illegal instruction</a>的问题。另外busybox还支持中文，查看中文文件名的文件时，不会出现&#8217;?&#8217;。

接下来为大家介绍编译的步骤。

## 环境准备

  * ### 1) 准备源代码
    
    使用CM 10.1源码目录下external/busybox的源代码即可，为了不影响其它代码的编译，可以将其拷贝至1个单独的目录，如~/work/busybox

  * ### 2) 准备编译环境
    
    下载Ndk
    
     <a href="http://developer.android.com/tools/sdk/ndk/index.html" target="_blank">http://developer.android.com/tools/sdk/ndk/index.html </a>
    
    解压Ndk包
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
2
</pre>
          </td>
          
          <td class="code">
            <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">$chmod</span> <span style="color: #000000;">755</span> android-ndk-r10d-linux-x86_64.bin
$.<span style="color: #000000; font-weight: bold;">/</span>android-ndk-r10d-linux-x86_64.bin</pre>
          </td>
        </tr>
      </table>
    </div>

  * ### 3) 将编译工具链目录添加至PATH环境变量
    
    <div class="wp_syntax">
      <table>
        <tr>
          <td class="line_numbers">
            <pre>1
</pre>
          </td>
          
          <td class="code">
            <pre class="bash" style="font-family:monospace;"><span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">PATH</span>=<span style="color: #007800;">$PATH</span>:<span style="color: #000000; font-weight: bold;">/</span>home<span style="color: #000000; font-weight: bold;">/</span>cloud<span style="color: #000000; font-weight: bold;">/</span>softwares<span style="color: #000000; font-weight: bold;">/</span>android-ndk-r10d<span style="color: #000000; font-weight: bold;">/</span>toolchains<span style="color: #000000; font-weight: bold;">/</span>arm-linux-androideabi-<span style="color: #000000;">4.9</span><span style="color: #000000; font-weight: bold;">/</span>prebuilt<span style="color: #000000; font-weight: bold;">/</span>linux-x86_64<span style="color: #000000; font-weight: bold;">/</span>bin</pre>
          </td>
        </tr>
      </table>
    </div>

## 准备config文件

拷贝 configs/android\_ndk\_defconfig 至busybox目录.config

修改.config里的CONFIG\_SYSROOT变量和CONFIG\_EXTRA_CFLAGS变量

  * ### 1) CONFIG_SYSROOT变量
    
    CONFIG_SYSROOT变量指定ndk系统目录，例如我们可以配制成:
    
    CONFIG_SYSROOT=&#8221;/home/cloud/softwares/android-ndk-r10d/platforms/android-15/arch-arm&#8221;
    
    当然我们也可以指定成别的Android版本，比如android-14

  * ### 2) CONFIG\_EXTRA\_CFLAGS变量
    
    CONFIG\_EXTRA\_CFLAGS变量指定编译变量，原来.config文件的设置如下所示：
    
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
            <pre class="cpp" style="font-family:monospace;">CONFIG_EXTRA_CFLAGS<span style="color: #000080;">=</span><span style="color: #FF0000;">"-DANDROID -D__ANDROID__ -DSK_RELEASE -nostdlib 
-march=armv7-a -msoft-float -mfloat-abi=softfp -mfpu=neon -mthumb 
-mthumb-interwork -fpic -fno-short-enums -fgcse-after-reload 
-frename-registers"</span></pre>
          </td>
        </tr>
      </table>
    </div>
    
    -march=armv7-a 指定支持armv7-a指令架构，但这样编译出来的busybox必须在armv7-a以上架构的cpu执行，否则运行会出错，提示illegal instructions。因此我们必须去掉选项-march=armv7-a。更改后如下所示：
    
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
            <pre class="cpp" style="font-family:monospace;">CONFIG_EXTRA_CFLAGS<span style="color: #000080;">=</span><span style="color: #FF0000;">"-DANDROID -D__ANDROID__ -DSK_RELEASE -nostdlib  
-msoft-float   -mfloat-abi=softfp -mfpu=neon -mthumb -mthumb-interwork 
-fpic -fno-short-enums -fgcse-after-reload -frename-registers"</span></pre>
          </td>
        </tr>
      </table>
    </div>

为了让busybox运行时不依赖于任何动态库，这样在Recovery模式下运行busybox也无问题。只需将busybox设置为静态链接的即可，这时需在.config文件里设置CONFIG_STATIC变量，设置如下所示即可：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;">CONFIG_STATIC<span style="color: #000080;">=</span>y</pre>
      </td>
    </tr>
  </table>
</div>

但是.config文件的初始设置时指定链接方式为动态链接，需将其改为静态链接，其原始的设置如下所示：

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
        <pre class="cpp" style="font-family:monospace;">CONFIG_EXTRA_LDFLAGS<span style="color: #000080;">=</span><span style="color: #FF0000;">"-Xlinker -z -Xlinker muldefs -nostdlib -Bdynamic -Xlinker
-dynamic-linker -Xlinker /system/bin/linker -Xlinker -z -Xlinker nocopyreloc 
-Xlinker --no-undefined ${SYSROOT}/usr/lib/crtbegin_dynamic.o 
${SYSROOT}/usr/lib/crtend_android.o"</span></pre>
      </td>
    </tr>
  </table>
</div>

修改后如下所示：

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
        <pre class="cpp" style="font-family:monospace;">CONFIG_EXTRA_LDFLAGS<span style="color: #000080;">=</span><span style="color: #FF0000;">"-Xlinker -z -Xlinker muldefs 
-nostdlib -Xlinker -z -Xlinker nocopyreloc -Xlinker 
--no-undefined ${SYSROOT}/usr/lib/crtbegin_dynamic.o 
${SYSROOT}/usr/lib/crtend_android.o"</span></pre>
      </td>
    </tr>
  </table>
</div>

去掉了-Bdynamic -Xlinker -dynamic-linker -Xlinker /system/bin/linker。

此时如果编译还是会出错，提示找不到dl动态库，还需修改CONFIG\_EXTRA\_LDLIBS变量，去掉dl库。修改前如下所示：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;">CONFIG_EXTRA_LDLIBS<span style="color: #000080;">=</span><span style="color: #FF0000;">"dl m c gcc"</span></pre>
      </td>
    </tr>
  </table>
</div>

修改后如下所示：

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
</pre>
      </td>
      
      <td class="code">
        <pre class="cpp" style="font-family:monospace;">CONFIG_EXTRA_LDLIBS<span style="color: #000080;">=</span><span style="color: #FF0000;">"m c gcc"</span></pre>
      </td>
    </tr>
  </table>
</div>

设置如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2015/02/config.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/config-1024x209.png" alt="config" width="1024" height="209" class="aligncenter size-large wp-image-707" srcset="http://www.cloudchou.com/wp-content/uploads/2015/02/config-1024x209.png 1024w, http://www.cloudchou.com/wp-content/uploads/2015/02/config-300x61.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/02/config-200x40.png 200w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

## 支持unicode

需要让busybox支持unicode编码，否则使用ls查看中文文件名的文件时会得到?,而不能正常显示中文文件名。

使用make menuconfig命令调出选择界面，然后进行选择：

Busybox Settting -> General Configuration -> Support Unicode

按空格键勾选Support Unicode

Charcter code to substitue unprintable characters with 填63，即0x3F

Range of supported Unicode charaters 填1个较大数值，如200000

勾选Allow wide Unicode characters on output

勾选 Bidirectional character-aware line input

勾选 Make it possible to enter sequences of chars wich are not unicode

这样就可支持unicode了，可以解析utf8编码的中文文件名

支持unicode的菜单设置如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2015/02/unicode.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/unicode-1024x439.png" alt="unicode" width="1024" height="439" class="aligncenter size-large wp-image-711" srcset="http://www.cloudchou.com/wp-content/uploads/2015/02/unicode-1024x439.png 1024w, http://www.cloudchou.com/wp-content/uploads/2015/02/unicode-300x128.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/02/unicode-200x85.png 200w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

## 选择busybox带的工具

make menuconfig调出勾选菜单，在Applets目录选择需要带的工具，

Archival Utilties 主要是 打包工具

Coreutils 主要是 核心工具，比如basename，cat，date

Console Utilities 主要是 控制台工具

Debian Utilities 是Debian系列Linux用的工具

Editors 文本编辑工具例如vi,awk,sed

Finding Utilties 查找工具

Init Utilities Init相关工具

Networking Utilities 网络相关工具，如ping

如果选择了mount工具，在进行编译时可能会提示出错，</p> 

此时需要修改文件libbb/Kbuild：

添加：

lib-$(CONFIG_MOUNT) += android.o</p> 

菜单选择如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2015/02/coretools.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/coretools-1024x448.png" alt="coretools" width="1024" height="448" class="aligncenter size-large wp-image-708" srcset="http://www.cloudchou.com/wp-content/uploads/2015/02/coretools-1024x448.png 1024w, http://www.cloudchou.com/wp-content/uploads/2015/02/coretools-300x131.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/02/coretools-200x87.png 200w" sizes="(max-width: 1024px) 100vw, 1024px" /></a>

## 编译

make –j8

编译成功示意图如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2015/02/make.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/make.png" alt="make" width="794" height="275" class="aligncenter size-full wp-image-710" srcset="http://www.cloudchou.com/wp-content/uploads/2015/02/make.png 794w, http://www.cloudchou.com/wp-content/uploads/2015/02/make-300x103.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/02/make-200x69.png 200w" sizes="(max-width: 794px) 100vw, 794px" /></a>

## 测试并执行

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
        <pre class="bash" style="font-family:monospace;">adb push busybox <span style="color: #000000; font-weight: bold;">/</span>data<span style="color: #000000; font-weight: bold;">/</span>local<span style="color: #000000; font-weight: bold;">/</span>tmp
adb shell <span style="color: #c20cb9; font-weight: bold;">chmod</span> <span style="color: #000000;">755</span> <span style="color: #000000; font-weight: bold;">/</span>data<span style="color: #000000; font-weight: bold;">/</span>local<span style="color: #000000; font-weight: bold;">/</span>tmp<span style="color: #000000; font-weight: bold;">/</span>busybox
adb shell <span style="color: #000000; font-weight: bold;">/</span>data<span style="color: #000000; font-weight: bold;">/</span>local<span style="color: #000000; font-weight: bold;">/</span>tmp<span style="color: #000000; font-weight: bold;">/</span>busybox</pre>
      </td>
    </tr>
  </table>
</div>

成功输出如下图所示：

<a href="http://www.cloudchou.com/wp-content/uploads/2015/02/execute.png" target="_blank" ><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/execute.png" alt="execute" width="997" height="442" class="aligncenter size-full wp-image-709" srcset="http://www.cloudchou.com/wp-content/uploads/2015/02/execute.png 997w, http://www.cloudchou.com/wp-content/uploads/2015/02/execute-300x132.png 300w, http://www.cloudchou.com/wp-content/uploads/2015/02/execute-200x88.png 200w" sizes="(max-width: 997px) 100vw, 997px" /></a>