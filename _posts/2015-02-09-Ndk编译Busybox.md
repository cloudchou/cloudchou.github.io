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
<h2>概述</h2>
 <p>本篇讲述如何在Linux下使用Ndk编译busybox源码，生成一个静态链接的兼容性好的可支持中文的busybox。busybox是静态链接的，所以busybox可以既在recovery模式下运行，也可以在系统模式下运行，解决busybox not found的问题。busybox兼容性好，使用ndk编译，可以在armv7和armv5的cpu上运行，解决了busybox illegal instruction的问题。另外busybox还支持中文，查看中文文件名的文件时，不会出现'?'。</p>   
 <p>接下来为大家介绍编译的步骤。</p>
 <h2>环境准备</h2>
 <ul>
 <li>
   <h3>1)\t准备源代码</h3>
   <p>使用CM 10.1源码目录下external/busybox的源代码即可，为了不影响其它代码的编译，可以将其拷贝至1个单独的目录，如~/work/busybox</p>
 </li>
 <li>
   <h3>2)\t准备编译环境</h3>
   <p>下载Ndk</p>
   <a href="http://developer.android.com/tools/sdk/ndk/index.html" target="_blank"> http://developer.android.com/tools/sdk/ndk/index.html </a>
   <p>解压Ndk包</p>
 ```bash
 $chmod 755 android-ndk-r10d-linux-x86_64.bin
 $./android-ndk-r10d-linux-x86_64.bin
 ```  
 </li>
 <li>
   <h3>3)\t将编译工具链目录添加至PATH环境变量</h3>
 ```bash
 export PATH=$PATH:/home/cloud/softwares/android-ndk-r10d/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin
 ```
 </li>
 </ul>
 <h2>准备config文件</h2>
 <p>拷贝 configs/android_ndk_defconfig 至busybox目录.config</p>
 <p>修改.config里的CONFIG_SYSROOT变量和CONFIG_EXTRA_CFLAGS变量</p>
 <ul>
 <li>
   <h3>1)\tCONFIG_SYSROOT变量</h3>
   <p>CONFIG_SYSROOT变量指定ndk系统目录，例如我们可以配制成:</p>
   <p>CONFIG_SYSROOT="/home/cloud/softwares/android-ndk-r10d/platforms/android-15/arch-arm"</p>
   <p>当然我们也可以指定成别的Android版本，比如android-14</p>
 </li>
 <li>
   <h3>2)\tCONFIG_EXTRA_CFLAGS变量</h3>
   <p>CONFIG_EXTRA_CFLAGS变量指定编译变量，原来.config文件的设置如下所示：</p>
 ```cpp
 CONFIG_EXTRA_CFLAGS="-DANDROID -D__ANDROID__ -DSK_RELEASE -nostdlib 
 -march=armv7-a -msoft-float -mfloat-abi=softfp -mfpu=neon -mthumb 
 -mthumb-interwork -fpic -fno-short-enums -fgcse-after-reload 
 -frename-registers"
 ```
   <p>-march=armv7-a 指定支持armv7-a指令架构，但这样编译出来的busybox必须在armv7-a以上架构的cpu执行，否则运行会出错，提示illegal instructions。因此我们必须去掉选项-march=armv7-a。更改后如下所示：</p>
 ```cpp
 CONFIG_EXTRA_CFLAGS="-DANDROID -D__ANDROID__ -DSK_RELEASE -nostdlib  
 -msoft-float   -mfloat-abi=softfp -mfpu=neon -mthumb -mthumb-interwork 
 -fpic -fno-short-enums -fgcse-after-reload -frename-registers"
 ```  
 </li>
 </ul>
 <p>为了让busybox运行时不依赖于任何动态库，这样在Recovery模式下运行busybox也无问题。只需将busybox设置为静态链接的即可，这时需在.config文件里设置CONFIG_STATIC变量，设置如下所示即可：</p>
 ```cpp
 CONFIG_STATIC=y
 ```
 <p>但是.config文件的初始设置时指定链接方式为动态链接，需将其改为静态链接，其原始的设置如下所示：</p>
 ```cpp
 CONFIG_EXTRA_LDFLAGS="-Xlinker -z -Xlinker muldefs -nostdlib -Bdynamic -Xlinker
 -dynamic-linker -Xlinker /system/bin/linker -Xlinker -z -Xlinker nocopyreloc 
 -Xlinker --no-undefined ${SYSROOT}/usr/lib/crtbegin_dynamic.o 
 ${SYSROOT}/usr/lib/crtend_android.o"
 ```
 <p>修改后如下所示：</p>
 ```cpp
 CONFIG_EXTRA_LDFLAGS="-Xlinker -z -Xlinker muldefs 
 -nostdlib -Xlinker -z -Xlinker nocopyreloc -Xlinker 
 --no-undefined ${SYSROOT}/usr/lib/crtbegin_dynamic.o 
 ${SYSROOT}/usr/lib/crtend_android.o"
 ```
 <p>去掉了-Bdynamic -Xlinker -dynamic-linker -Xlinker /system/bin/linker。</p>
 <p>此时如果编译还是会出错，提示找不到dl动态库，还需修改CONFIG_EXTRA_LDLIBS变量，去掉dl库。修改前如下所示：</p>
 ```cpp
 CONFIG_EXTRA_LDLIBS="dl m c gcc"
 ```
 <p>修改后如下所示：</p>
 ```cpp
 CONFIG_EXTRA_LDLIBS="m c gcc"
 ```
 <p>设置如下图所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/02/config.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/config-1024x209.png" alt="config" width="1024" height="209" class="aligncenter size-large wp-image-707" /></a>
 
 <h2>支持unicode</h2>
 <p>需要让busybox支持unicode编码，否则使用ls查看中文文件名的文件时会得到?,而不能正常显示中文文件名。</p>
 <p>使用make menuconfig命令调出选择界面，然后进行选择：</p>
 <p>Busybox Settting -> General Configuration -> Support Unicode</p>
 <p>按空格键勾选Support Unicode</p>
 <p>Charcter code to substitue unprintable characters with 填63，即0x3F</p>
 <p>Range of supported Unicode charaters 填1个较大数值，如200000</p>
 <p>勾选Allow wide Unicode characters on output</p>
 <p>勾选 Bidirectional character-aware line input</p>
 <p>勾选 Make it possible to enter sequences of chars wich are not unicode</p>
 <p>这样就可支持unicode了，可以解析utf8编码的中文文件名</p>
 <p>支持unicode的菜单设置如下图所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/02/unicode.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/unicode-1024x439.png" alt="unicode" width="1024" height="439" class="aligncenter size-large wp-image-711" /></a>
 
 
 <h2>选择busybox带的工具</h2>
 <p>make menuconfig调出勾选菜单，在Applets目录选择需要带的工具，</p>
 <p>   Archival Utilties 主要是 打包工具</p>
 <p>   Coreutils   主要是 核心工具，比如basename，cat，date</p>
 <p>   Console Utilities 主要是 控制台工具</p>
 <p>   Debian Utilities  是Debian系列Linux用的工具</p>
 <p>  Editors  文本编辑工具例如vi,awk,sed</p>
 <p>  Finding Utilties 查找工具</p>
 <p>  Init Utilities  Init相关工具</p>
 <p>  Networking Utilities 网络相关工具，如ping</p>
 <p>  如果选择了mount工具，在进行编译时可能会提示出错，</p>
 <p>  </p>
 <p>  此时需要修改文件libbb/Kbuild：</p>
 <p>  添加：</p>
 <p>    lib-$(CONFIG_MOUNT) += android.o</p>
 <p></p>
 <p>菜单选择如下图所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/02/coretools.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/coretools-1024x448.png" alt="coretools" width="1024" height="448" class="aligncenter size-large wp-image-708" /></a>
 
 <h2>编译</h2>
 <p>make –j8</p>
 <p>编译成功示意图如下图所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/02/make.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/make.png" alt="make" width="794" height="275" class="aligncenter size-full wp-image-710" /></a>
 
 <h2>测试并执行</h2>
 ```bash
 adb push busybox /data/local/tmp
 adb shell chmod 755 /data/local/tmp/busybox
 adb shell /data/local/tmp/busybox
 ```
 <p>成功输出如下图所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2015/02/execute.png" target="_blank" ><img src="http://www.cloudchou.com/wp-content/uploads/2015/02/execute.png" alt="execute" width="997" height="442" class="aligncenter size-full wp-image-709" /></a>
