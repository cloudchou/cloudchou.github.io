---
id: 134
title: Android编译系统详解(一)——build/envsetup.sh
date: 2014-01-14T00:04:23+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=134
permalink: /android/post-134.html
views:
  - 16259
categories:
  - Android
tags:
  - android build/envsetup.sh
  - android 查看源码 常用命令
  - Android编译系统详解
  - envsetup.sh
  - envsetup.sh分析
  - envsetup.sh执行流程
---

<p>准备好编译环境后，编译Rom的第一步是 source build/envsetup.sh，该步骤把envsetup.sh里的函数声明为当前会话终端可用的命令。这些命令能让我们切换目录，提交代码，编译Rom更方便。如果记不住所有命令,只要你记住hmm就可以了，也可通过hmm命令看到支持的命令列表。</p>
<h2>1. 命令分类:</h2> 
<h3>1.1 编译用的命令</h3>
<table class="dataintable">
 <tr>
  <th width="80px">
   命令名称
  </th>
  <th width="150px">
   使用方式
  </th>
  <th>
   说明
  </th>
 </tr>
 <tr>
  <td>
   <span class="emphasize">breakfast</span>
   <br/>
   别名bib
   <br/>
  </td>
  <td>
   breakfast [product]
   <br/>
   示例：
   <br/>
   breakfast i9100
   <br/>
   breakfast
  cm_i9100-userdebug
   <br/>
  </td>
  <td>
   <b>选择产品</b><br/>
   product格式: device 或者 device-build_variant
   <br/>
   先从网上下载cm支持的产品列表
   <br/>
   product是用户要编译的目标产品，例如find5或者i9100
   <br/>
   如果选择device-build_variant，并且是cm支持的device，一般会以cm_开头，比如cm_i9100
   <br/>
   如果未选择编译产品，那么会弹出许多product，让用户选择
   <br/>
   这里的product列表仅包含从网上下载的产品，不包含只有本地支持的产品
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   <span class="emphasize">lunch</span>
   <br/>
  </td>
  <td>
   lunch [product]
   <br/>
   示例：
   <br/>
   lunch cm_i9100-userdebug
   <br/>
  </td>
  <td>
   <b>选择产品</b><br/> 
   product格式: build-build_variant
   <br/>
   <span style="color:red;font-weight: bold;">不再从</span>网上下载产品列表，
   <br/>
   如果[product]为空，意味着未选择编译产品，也会弹出许多product，让用户选择，
   <br/>
   这里的product列表是用户在执行source
  build/envsetup.sh时，including了一些shell脚本，从而添加至产品列表的
   <br/>
  </td>
 </tr>
 <tr>
  <td>
    <span class="emphasize">brunch</span>
   <br/>
  </td>
  <td>
   brunch [product]
   <br/>
  </td>
  <td>
   <b>选择产品并编译</b><br/>
   product格式: device 或者 device-build_variant
   <br/>
   调用breakfast选择编译产品
   <br/>
   然后调用mka bacon编译
   <br/>
  </td>
 </tr>
 <tr>
  <td>
    <span class="emphasize">m</span>
   <br/>
  </td>
  <td>
   m [targetlist]
   <br/>
  </td>
  <td>
   <b>编译选中目标</b><br/>
   示例：m otatools bacon
   <br/>
   并没有调用schedtool 充分利用所有核编译
   <br/>
  </td>
 </tr>
 <tr>
  <td>
    <span class="emphasize">mm</span>
   <br/>
  </td>
  <td>
   mm [mka]
  [targetlist]
   <br/>
   示例：
   <br/>
   mm mka
   <br/>
  </td>
  <td>
   <b>编译选中目标或者当前目录所在项目</b><br/>   
   若有mka，会调用mka进行编译
   <br/>
   如果当前目录在顶层目录，会编译指定的所有目标
   <br/>
   如果不在顶层目录，会编译当前目录所在的工程
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   <span class="emphasize">mmm</span>
   <br/>
  </td>
  <td>
   mmm [directory:[modulist]]
  -arglist
   <br/>
  </td>
  <td>
   <b>编译指定目录下的模块</b><br/> 
   directory可以为以下特殊目标：
   <br/>
   snod dist mka
  showcommands
   <br/>
   若指定了mka，将利用mka进行编译
   <br/>
   示例：
   <br/>
   mmm
  bootable/recovery: recovery
   <br/>
   或者
   <br/>
   mmm
  bootable/recovery
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   <span class="emphasize">mka</span>
   <br/>
  </td>
  <td>
   mka [targetlist]
   <br/>
  </td>
  <td>
   <b>编译指定目标列表</b><br/>  
   将利用SCHED_BATCH编译指定所有目标，这样能充分利用所有CPU
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   eat
   <br/>
  </td>
  <td>
   eat
   <br/>
  </td>
  <td>
   <b>刷机</b><br/>
   在/cahce/recovery/command文件写上如下命令--sideload，重启设备至recovery，等待设备进入sideload状态，调用adb sideload进行刷机
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   omnom
   <br/>
  </td>
  <td>
   omnmon [product]
   <br/>
  </td>
  <td>
    <b>编译ROM并刷ROM至设备</b><br/>  
  </td>
 </tr>
 <tr>
  <td>
   tapas
   <br/>
  </td>
  <td>
   tapas [&lt;App1&gt;
  &lt;App2&gt; ...] [arm|x86|mips] [eng|userdebug|user]
   <br/>
  </td>
  <td>
   Configures the
  build to build unbundled apps
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   cmka
   <br/>
  </td>
  <td>
   cmka [targetlist]
   <br/>
  </td>
  <td>
   Cleans and builds
  using mka
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   installboot
  </td>
  <td>
   installboot
   <br/>
  </td>
  <td>
   <b>安装boot</b><br/> 
   利用$OUT/recovery/root/etc/recovery.fstab找到boot所在分区以及分区类型，找到分区后，先将boot.img上传至/cache下，需要将内核需要加载的模块$OUT/system/lib/modules/*上传至/system/lib/modules/，然后如果是mtd分区就利用flash_image刷至相应的分区，否则利用dd刷至相应的分区
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   installrecovery
   <br/>
  </td>
  <td>
   installrecovery
   <br/>
  </td>
  <td>
  <b>安装recovery</b><br/>    
   与安装boot类似
   <br/>
  </td>
 </tr>
</table>

<h3>1.2 查看代码时的辅助命令</h3>
<table class="dataintable">
 <tr>
  <th width="80px">
   命令名称
  </th>
  <th width="150px">
   使用方式
  </th>
  <th>
   说明
  </th>
 </tr>
 <tr>
  <td>
    <span class="emphasize">cgrep</span>
   <br/>
  </td>
  <td>
   cgrep keyword
   <br/>
  </td>
  <td>
    <b>在C，C++代码中搜索指定关键字</b>
   <br/>
    调用find查找C/C++代码文件(包括头文件)，并且排除了不用的文件夹，在找到的文件中用grep搜索关键字
   <br/>
  </td>
 </tr>
 <tr>
  <td>
       <span class="emphasize">jgrep</span>
   <br/>
  </td>
  <td>
   jgrep keyword
   <br/>
  </td>
  <td>
   <b>在java代码中搜索指定关键字</b>   
   <br/>
   调用find查找java代码文件，并且排除了不用的文件夹，在找到的文件中用grep搜索关键字
   <br/>
  </td>
 </tr>
 <tr>
  <td>
     <span class="emphasize">resgrep</span>
   <br/>
  </td>
  <td>
   resgrep
  keyword
   <br/>
  </td>
  <td>
    <b>在资源xml文件中搜索指定关键字</b>      
   <br/>
   调用find在当前文件夹查找下res子目录里找xml文件，并且排除了不用的文件夹，在找到的文件中用grep搜索关键字    
   <br/>
  </td>
 </tr>
 <tr>
  <td>
    <span class="emphasize">croot</span>
   <br/>
  </td>
  <td>
   croot
   <br/>
  </td>
  <td>
    <b>切换至Android根目录</b>
   <br/>
  </td>
 </tr>
 <tr>
  <td>
       <span class="emphasize">cout</span>
   <br/>
  </td>
  <td>
   cout
   <br/>
  </td>
  <td>
    <b>切换至prodcut的out目录</b>
   <br/>
  </td>
 </tr>
 <tr>
  <td>
    <span class="emphasize">cproj</span>
   <br/>
  </td>
  <td>
   cproj
   <br/>
  </td>
  <td>
   从某个工程的非常深的子目录，可迅速切换至工程的根目录
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   <span class="emphasize">get_build_var</span>
   <br/>
  </td>
  <td>
   get_build_var
  build_var
   <br/>
  </td>
  <td>
   获取某个编译变量的值，
   <br/>
   一般是路径
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   <span class="emphasize">get_abs_build_var</span>
   <br/>
  </td>
  <td>
   get_abs_build_var
   <br/>
  </td>
  <td>
   获取某个编译变量的值，
   <br/>
   是绝对路径
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   findmakefile
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   打印当前目录所在工程的Android.mk的文件路径
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   printconfig
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   打印各种编译变量的值
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   print_lunch_menu
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   打印lunch可选择的各种product
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   godir
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   切换至用户输入的文件所在的目录
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   repodiff
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   调用git进行diff，查看当前修改的东西
   <br/>
  </td>
 </tr>
</table>

<h3>1.3 辅助函数</h3>
<table class="dataintable">
 <tr>
  <th width="80px">
   命令名称
  </th>
  <th width="150px">
   使用方式
  </th>
  <th>
   说明
  </th>
 </tr>
 <tr>
  <td>
   <span class="emphasize">add_lunch_combo</span><br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   增加调用lunch命令时的选择项
   <br/>
   示例：
   <br/>
   add_lunch_combo
  full_galaxys2att-eng
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   check_product
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   检查产品看CM是否能支持编译
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   check_variant
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   检查TARGET_BUILD_VARIANT，看其值是否有效，可能的值只能为user,userdebug,eng
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   choosecombo
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   调用choosetype，chooseproduct，choosevariant等函数，确定TARGET_PRODUCT，TARGET_BUILD_TYPE，TARGET_BUILD_VARIANT
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   chooseproduct
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   让用户输入一个product的名字，默认为full，最终确定TARGET_PRODUCT，
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   choosetype
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   选择编译类型即TARGET_BUILD_TYPE，可能的值为debug,release
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   choosevariant
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   让用户选择编译变量TARGET_BUILD_VARIANT，可能的值为user,userdebug,eng
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   dopush
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   alias mmp='dopush mm'
   <br/>
   alias mmmp='dopush mmm'
   <br/>
   alias mkap='dopush mka'
   <br/>
   alias cmkap='dopush cmka'
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   fixup_common_out_dir
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   建立$(OUT_DIR)/target/common目录
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   getprebuilt
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   得到prebuilt的路径
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   getsdcardpath
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   获取Sd卡路径
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   gettargetarch
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   获取TARGET_ARCH的值
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   gettop
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   获取Android源码根目录
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   set_java_home
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   设置java的主目录
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   setpaths
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   将编译要用到的一些路径添加到环境变量PATH里
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   set_sequence_number
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   export BUILD_ENV_SEQUENCE_NUMBER=10
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   set_stuff_for_environment
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   设置PROMPT_COMMAND变量，java_home，PATH目录，set_sequence_number
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   settitle
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   如果STAY_OFF_MY_LAWN为空，设置PROMPT_COMMAND变量，会改变SecureCrt终端窗口显示的名字
   <br/>
  </td>
 </tr>
</table>

<h3>1.4 调试相关</h3>
<table class="dataintable">
 <tr>
  <th width="80px">
   命令名称
  </th>
  <th width="150px">
   使用方式
  </th>
  <th>
   说明
  </th>
 </tr>
 <tr>
  <td>
    <span class="emphasize">gdbclient</span><br/>   
   <br/>
  </td>
  <td>
   gdbclient
  exename (progname|pid)
   <br/>
  </td>
  <td>
   gdb调试
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   <span class="emphasize">pid</span><br/>   
   <br/>
  </td>
  <td>   
   pid exename
   <br/>
  </td>
  <td>
   查看某个可执行程序对应的进程id
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   getbugreports
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   将bug报告从设备上拉到本地，bug报告存放于目录/sdcard/bugreports，
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   getlastscreenshot
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   获取最后一张截图
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   getscreenshotpath
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   获取屏幕截图的路径
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   isviewserverstarted
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   判断viewserver是否已启动
   <br/>
   adb shell service call window 3
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   key_back
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   模拟按返回键
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   key_home
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   模拟按Home键
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   key_menu
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   模拟按菜单键
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   runtest
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   调用development/testrunner/runtest.py，进行测试
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   smoketest
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   利用SmokeTestApp.apk，SmokeTest.apk对系统进行一个smoke test
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   startviewserver
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   adb shell service call window 1 i32 $port
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   stopviewserver
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   adb shell
  service call window 2
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   systemstack
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   dump the current stack trace of all
  threads in the system process to the usual ANR traces file
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   tracedmdump
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   调用q2dm将系统堆栈导出来，并利用dmtracedump将其转为可读的html文件
   <br/>
  </td>
 </tr>
</table>

<h3>1.5 提交代码相关命令</h3>
<table class="dataintable">
 <tr>
  <th width="80px">
   命令名称
  </th>
  <th width="150px">
   使用方式
  </th>
  <th>
   说明
  </th>
 </tr>
 <tr>
  <td>
   aospremote
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   Add git remote
  for matching AOSP repository
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   cmgerrit
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   从CM拉源代码，或者将源代码提交到gerrit给比人审核，直接敲这个命令可得到该命令的使用帮助，最终调用Git完成命令功能
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   cmrebase
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   和git的rebase 衍合类似，我们不做代码提交，故此没必要
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   cmremote
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   Add git remote for CM Gerrit Review
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   makerecipe
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   将本地代码推送至git仓库
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   repopick
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   Utility to fetch changes from Gerrit，可选项有--ignore-missing，--start-branch，--abandon-first，--auto-branch
   <br/>
  </td>
 </tr>
 <tr>
  <td>
   reposync
   <br/>
  </td>
  <td>
   <br/>
  </td>
  <td>
   Parallel repo
  sync using ionice and SCHED_BATCH
   <br/>
  </td>
 </tr>
</table>

<br/>
<h2>2. source build/envsetup.sh 执行流程</h2>
<p>envsetup.sh 定义了很多函数，除此之外还执行了其它操作，代码如下:</p>
```bash
VARIANT_CHOICES=(user userdebug eng)，# TARGET_BUILD_VARIANT变量的可能值
#LUNCH_MENU_CHOICES是供用户选择的prodcut列表,
#每次source build/envsetup.sh时需重置变量LUNCH_MENU_CHOICES
#不然后续的include vendor/cm/vendorsetup.sh时会继续添加产品至变量LUNCH_MENU_CHOICES里，
#导致出现很多重复产品
unset LUNCH_MENU_CHOICES 
add_lunch_combo full-eng #默认添加full-eng，full_mips-eng等4个产品
add_lunch_combo full_x86-eng
add_lunch_combo vbox_x86-eng
add_lunch_combo full_mips-eng
alias bib=breakfast#给breakfast起别名
complete -F _lunch lunch #给lunch添加tab提示
case `uname -s` in #定义sgrep函数 在所有工程类型代码里搜索
    Darwin)
        function sgrep()
        {
            find -E . -name .repo -prune -o -name .git -prune -o  -type f \
                 -iregex '.*\.(c|h|cpp|S|java|xml|sh|mk)' -print0 \
                 | xargs -0 grep --color -n "$@"
        }
        ;;
    *)
        function sgrep()
        {
            find . -name .repo -prune -o -name .git -prune -o  -type f \
                 -iregex '.*\.\(c\|h\|cpp\|S\|java\|xml\|sh\|mk\)' -print0 \ 
                 | xargs -0 grep --color -n "$@"
        }
        ;;
esac
export -f cmremote
export -f aospremote
alias mmp='dopush mm' #定义更多编译后push到设备的函数的操作
alias mmmp='dopush mmm'
alias mkap='dopush mka'
alias cmkap='dopush cmka'
if [ "x$SHELL" != "x/bin/bash" ]; then #只支持Bash终端
    case `ps -o command -p $$` in
        *bash*)
            ;;
        *)
            echo "WARNING: Only bash is supported,"  \
                 "use of other shell would lead to erroneous results"
            ;;
    esac
fi
#Execute the contents of any vendorsetup.sh files we can find.
#source vendor和device下能找到的所有vendorsetup.sh
for f in `/bin/ls vendor/*/vendorsetup.sh vendor/*/*/vendorsetup.sh device/*/*/vendorsetup.sh 2> /dev/null`
do
    echo "including $f"
    . $f
done
unset f
#source目录 sdk/bash_completion vendor/cm/bash_completion下的bash脚本，
#能提供tab提示
addcompletions 
export ANDROID_BUILD_TOP=$(gettop)
```
<h3>2.1 执行的vendorsetup.sh有：</h3>
<p>在envsetup.sh里将执行vendor和device目录及各自子目录下所有的vendorsetup.sh，这些vendorsetup.sh做的事情是调用add_lunch_combo将它们各自的产品添加到 LUNCH_MENU_CHOICES 变量里</p>
<p>#执行cm的vendorsetup.sh将从网上下载cm支持的产品列表，并添加至LUNCH_MENU_CHOICES</p>
<p>vendor/cm/vendorsetup.sh</p>
<p>#将添加mini_armv7a_neon产品 add_lunch_combo mini_armv7a_neon-userdebug</p>
<p>device/generic/armv7-a-neon/vendorsetup.sh</p>
<p>#add_lunch_combo mini_armv7a-userdebug</p>
<p>device/generic/armv7-a/vendorsetup.sh </p>
<p>#add_lunch_combo mini_mips-userdebug</p>
<p>device/generic/mips/vendorsetup.sh</p>
<p>#add_lunch_combo mini_x86-userdebug </p>
<p>device/generic/x86/vendorsetup.sh </p>
<p>#add_lunch_combo cm_jflteatt-eng</p>
<p>device/samsung/jflteatt/vendorsetup.sh</p>
<p># add_lunch_combo full_panda-userdebug</p>
<p>device/ti/panda/vendorsetup.sh </p>
<p># add_lunch_combo zte_blade-eng</p>
<p>#add_lunch_combo zte_blade-userdebug</p>
<p>device/zte/blade/vendorsetup.sh </p>

<h3>2.2 执行的completion bash有：</h3>
<p>在envsetup.sh里将执行sdk/bash_completion和vendor/cm/bash_completion目录下的bash脚本，这些bash脚本主要是为命令提供tab支持，有了这些tab支持，输入命令后如果某个选项忘记了，只需要敲tab键，就能获得提示，使用命令更加方便</p>
<p>including sdk/bash_completion/adb.bash</p>
<p>including vendor/cm/bash_completion/git.bash</p>
<p>including vendor/cm/bash_completion/repo.bash</p>
<p>分别对应adb，git，repo的tab提示</p>
