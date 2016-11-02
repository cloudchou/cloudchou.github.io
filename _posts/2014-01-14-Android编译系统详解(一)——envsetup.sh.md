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
准备好编译环境后，编译Rom的第一步是 source build/<a href="http://www.cloudchou.com/tag/envsetup-sh" title="View all posts in envsetup.sh" target="_blank" class="tags">envsetup.sh</a>，该步骤把envsetup.sh里的函数声明为当前会话终端可用的命令。这些命令能让我们切换目录，提交代码，编译Rom更方便。如果记不住所有命令,只要你记住hmm就可以了，也可通过hmm命令看到支持的命令列表。

## 1. 命令分类:

### 1.1 编译用的命令

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
      <span class="emphasize">breakfast</span><br /> <br /> 别名bib<br />
    </td>
    
    <td>
      breakfast [product]<br /> <br /> 示例：<br /> <br /> breakfast i9100<br /> <br /> breakfast<br /> cm_i9100-userdebug<br />
    </td>
    
    <td>
      <b>选择产品</b><br /> product格式: device 或者 device-build_variant<br /> <br /> 先从网上下载cm支持的产品列表<br /> <br /> product是用户要编译的目标产品，例如find5或者i9100<br /> <br /> 如果选择device-build_variant，并且是cm支持的device，一般会以cm_开头，比如cm_i9100<br /> <br /> 如果未选择编译产品，那么会弹出许多product，让用户选择<br /> <br /> 这里的product列表仅包含从网上下载的产品，不包含只有本地支持的产品<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">lunch</span><br />
    </td>
    
    <td>
      lunch [product]<br /> <br /> 示例：<br /> <br /> lunch cm_i9100-userdebug<br />
    </td>
    
    <td>
      <b>选择产品</b><br /> <br /> product格式: build-build_variant<br /> <br /> <span style="color:red;font-weight: bold;">不再从</span>网上下载产品列表，<br /> <br /> 如果[product]为空，意味着未选择编译产品，也会弹出许多product，让用户选择，<br /> <br /> 这里的product列表是用户在执行source<br /> build/envsetup.sh时，including了一些shell脚本，从而添加至产品列表的<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">brunch</span><br />
    </td>
    
    <td>
      brunch [product]<br />
    </td>
    
    <td>
      <b>选择产品并编译</b><br /> product格式: device 或者 device-build_variant<br /> <br /> 调用breakfast选择编译产品<br /> <br /> 然后调用mka bacon编译<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">m</span><br />
    </td>
    
    <td>
      m [targetlist]<br />
    </td>
    
    <td>
      <b>编译选中目标</b><br /> 示例：m otatools bacon<br /> <br /> 并没有调用schedtool 充分利用所有核编译<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">mm</span><br />
    </td>
    
    <td>
      mm [mka]<br /> [targetlist]<br /> <br /> 示例：<br /> <br /> mm mka<br />
    </td>
    
    <td>
      <b>编译选中目标或者当前目录所在项目</b><br /> <br /> 若有mka，会调用mka进行编译<br /> <br /> 如果当前目录在顶层目录，会编译指定的所有目标<br /> <br /> 如果不在顶层目录，会编译当前目录所在的工程<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">mmm</span><br />
    </td>
    
    <td>
      mmm [directory:[modulist]]<br /> -arglist<br />
    </td>
    
    <td>
      <b>编译指定目录下的模块</b><br /> <br /> directory可以为以下特殊目标：<br /> <br /> snod dist mka<br /> showcommands<br /> <br /> 若指定了mka，将利用mka进行编译<br /> <br /> 示例：<br /> <br /> mmm<br /> bootable/recovery: recovery<br /> <br /> 或者<br /> <br /> mmm<br /> bootable/recovery<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">mka</span><br />
    </td>
    
    <td>
      mka [targetlist]<br />
    </td>
    
    <td>
      <b>编译指定目标列表</b><br /> <br /> 将利用SCHED_BATCH编译指定所有目标，这样能充分利用所有CPU<br />
    </td>
  </tr>
  
  <tr>
    <td>
      eat<br />
    </td>
    
    <td>
      eat<br />
    </td>
    
    <td>
      <b>刷机</b><br /> 在/cahce/recovery/command文件写上如下命令&#8211;sideload，重启设备至recovery，等待设备进入sideload状态，调用adb sideload进行刷机<br />
    </td>
  </tr>
  
  <tr>
    <td>
      omnom<br />
    </td>
    
    <td>
      omnmon [product]<br />
    </td>
    
    <td>
      <b>编译ROM并刷ROM至设备</b><br />
    </td>
  </tr>
  
  <tr>
    <td>
      tapas<br />
    </td>
    
    <td>
      tapas [<App1><br /> <App2> &#8230;] [arm|x86|mips] [eng|userdebug|user]<br />
    </td>
    
    <td>
      Configures the<br /> build to build unbundled apps<br />
    </td>
  </tr>
  
  <tr>
    <td>
      cmka<br />
    </td>
    
    <td>
      cmka [targetlist]<br />
    </td>
    
    <td>
      Cleans and builds<br /> using mka<br />
    </td>
  </tr>
  
  <tr>
    <td>
      installboot
    </td>
    
    <td>
      installboot<br />
    </td>
    
    <td>
      <b>安装boot</b><br /> <br /> 利用$OUT/recovery/root/etc/recovery.fstab找到boot所在分区以及分区类型，找到分区后，先将boot.img上传至/cache下，需要将内核需要加载的模块$OUT/system/lib/modules/*上传至/system/lib/modules/，然后如果是mtd分区就利用flash_image刷至相应的分区，否则利用dd刷至相应的分区<br />
    </td>
  </tr>
  
  <tr>
    <td>
      installrecovery<br />
    </td>
    
    <td>
      installrecovery<br />
    </td>
    
    <td>
      <b>安装recovery</b><br /> <br /> 与安装boot类似<br />
    </td>
  </tr>
</table>

### 1.2 查看代码时的辅助命令

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
      <span class="emphasize">cgrep</span><br />
    </td>
    
    <td>
      cgrep keyword<br />
    </td>
    
    <td>
      <b>在C，C++代码中搜索指定关键字</b><br /> <br /> 调用find查找C/C++代码文件(包括头文件)，并且排除了不用的文件夹，在找到的文件中用grep搜索关键字<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">jgrep</span><br />
    </td>
    
    <td>
      jgrep keyword<br />
    </td>
    
    <td>
      <b>在java代码中搜索指定关键字</b><br /> <br /> 调用find查找java代码文件，并且排除了不用的文件夹，在找到的文件中用grep搜索关键字<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">resgrep</span><br />
    </td>
    
    <td>
      resgrep<br /> keyword<br />
    </td>
    
    <td>
      <b>在资源xml文件中搜索指定关键字</b><br /> <br /> 调用find在当前文件夹查找下res子目录里找xml文件，并且排除了不用的文件夹，在找到的文件中用grep搜索关键字<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">croot</span><br />
    </td>
    
    <td>
      croot<br />
    </td>
    
    <td>
      <b>切换至Android根目录</b><br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">cout</span><br />
    </td>
    
    <td>
      cout<br />
    </td>
    
    <td>
      <b>切换至prodcut的out目录</b><br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">cproj</span><br />
    </td>
    
    <td>
      cproj<br />
    </td>
    
    <td>
      从某个工程的非常深的子目录，可迅速切换至工程的根目录<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">get_build_var</span><br />
    </td>
    
    <td>
      get_build_var<br /> build_var<br />
    </td>
    
    <td>
      获取某个编译变量的值，<br /> <br /> 一般是路径<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">get_abs_build_var</span><br />
    </td>
    
    <td>
      get_abs_build_var<br />
    </td>
    
    <td>
      获取某个编译变量的值，<br /> <br /> 是绝对路径<br />
    </td>
  </tr>
  
  <tr>
    <td>
      findmakefile<br />
    </td>
    
    <td>
    </td>
    
    <td>
      打印当前目录所在工程的Android.mk的文件路径<br />
    </td>
  </tr>
  
  <tr>
    <td>
      printconfig<br />
    </td>
    
    <td>
    </td>
    
    <td>
      打印各种编译变量的值<br />
    </td>
  </tr>
  
  <tr>
    <td>
      print_lunch_menu<br />
    </td>
    
    <td>
    </td>
    
    <td>
      打印lunch可选择的各种product<br />
    </td>
  </tr>
  
  <tr>
    <td>
      godir<br />
    </td>
    
    <td>
    </td>
    
    <td>
      切换至用户输入的文件所在的目录<br />
    </td>
  </tr>
  
  <tr>
    <td>
      repodiff<br />
    </td>
    
    <td>
    </td>
    
    <td>
      调用git进行diff，查看当前修改的东西<br />
    </td>
  </tr>
</table>

### 1.3 辅助函数

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
      <span class="emphasize">add_lunch_combo</span>
    </td>
    
    <td>
    </td>
    
    <td>
      增加调用lunch命令时的选择项<br /> <br /> 示例：<br /> <br /> add_lunch_combo<br /> full_galaxys2att-eng<br />
    </td>
  </tr>
  
  <tr>
    <td>
      check_product<br />
    </td>
    
    <td>
    </td>
    
    <td>
      检查产品看CM是否能支持编译<br />
    </td>
  </tr>
  
  <tr>
    <td>
      check_variant<br />
    </td>
    
    <td>
    </td>
    
    <td>
      检查TARGET_BUILD_VARIANT，看其值是否有效，可能的值只能为user,userdebug,eng<br />
    </td>
  </tr>
  
  <tr>
    <td>
      choosecombo<br />
    </td>
    
    <td>
    </td>
    
    <td>
      调用choosetype，chooseproduct，choosevariant等函数，确定TARGET_PRODUCT，TARGET_BUILD_TYPE，TARGET_BUILD_VARIANT<br />
    </td>
  </tr>
  
  <tr>
    <td>
      chooseproduct<br />
    </td>
    
    <td>
    </td>
    
    <td>
      让用户输入一个product的名字，默认为full，最终确定TARGET_PRODUCT，<br />
    </td>
  </tr>
  
  <tr>
    <td>
      choosetype<br />
    </td>
    
    <td>
    </td>
    
    <td>
      选择编译类型即TARGET_BUILD_TYPE，可能的值为debug,release<br />
    </td>
  </tr>
  
  <tr>
    <td>
      choosevariant<br />
    </td>
    
    <td>
    </td>
    
    <td>
      让用户选择编译变量TARGET_BUILD_VARIANT，可能的值为user,userdebug,eng<br />
    </td>
  </tr>
  
  <tr>
    <td>
      dopush<br />
    </td>
    
    <td>
    </td>
    
    <td>
      alias mmp=&#8217;dopush mm&#8217;<br /> <br /> alias mmmp=&#8217;dopush mmm&#8217;<br /> <br /> alias mkap=&#8217;dopush mka&#8217;<br /> <br /> alias cmkap=&#8217;dopush cmka&#8217;<br />
    </td>
  </tr>
  
  <tr>
    <td>
      fixup_common_out_dir<br />
    </td>
    
    <td>
    </td>
    
    <td>
      建立$(OUT_DIR)/target/common目录<br />
    </td>
  </tr>
  
  <tr>
    <td>
      getprebuilt<br />
    </td>
    
    <td>
    </td>
    
    <td>
      得到prebuilt的路径<br />
    </td>
  </tr>
  
  <tr>
    <td>
      getsdcardpath<br />
    </td>
    
    <td>
    </td>
    
    <td>
      获取Sd卡路径<br />
    </td>
  </tr>
  
  <tr>
    <td>
      gettargetarch<br />
    </td>
    
    <td>
    </td>
    
    <td>
      获取TARGET_ARCH的值<br />
    </td>
  </tr>
  
  <tr>
    <td>
      gettop<br />
    </td>
    
    <td>
    </td>
    
    <td>
      获取Android源码根目录<br />
    </td>
  </tr>
  
  <tr>
    <td>
      set_java_home<br />
    </td>
    
    <td>
    </td>
    
    <td>
      设置java的主目录<br />
    </td>
  </tr>
  
  <tr>
    <td>
      setpaths<br />
    </td>
    
    <td>
    </td>
    
    <td>
      将编译要用到的一些路径添加到环境变量PATH里<br />
    </td>
  </tr>
  
  <tr>
    <td>
      set_sequence_number<br />
    </td>
    
    <td>
    </td>
    
    <td>
      export BUILD_ENV_SEQUENCE_NUMBER=10<br />
    </td>
  </tr>
  
  <tr>
    <td>
      set_stuff_for_environment<br />
    </td>
    
    <td>
    </td>
    
    <td>
      设置PROMPT_COMMAND变量，java_home，PATH目录，set_sequence_number<br />
    </td>
  </tr>
  
  <tr>
    <td>
      settitle<br />
    </td>
    
    <td>
    </td>
    
    <td>
      如果STAY_OFF_MY_LAWN为空，设置PROMPT_COMMAND变量，会改变SecureCrt终端窗口显示的名字<br />
    </td>
  </tr>
</table>

### 1.4 调试相关

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
      <span class="emphasize">gdbclient</span></p>
    </td>
    
    <td>
      gdbclient<br /> exename (progname|pid)<br />
    </td>
    
    <td>
      gdb调试<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">pid</span></p>
    </td>
    
    <td>
      pid exename<br />
    </td>
    
    <td>
      查看某个可执行程序对应的进程id<br />
    </td>
  </tr>
  
  <tr>
    <td>
      getbugreports<br />
    </td>
    
    <td>
    </td>
    
    <td>
      将bug报告从设备上拉到本地，bug报告存放于目录/sdcard/bugreports，<br />
    </td>
  </tr>
  
  <tr>
    <td>
      getlastscreenshot<br />
    </td>
    
    <td>
    </td>
    
    <td>
      获取最后一张截图<br />
    </td>
  </tr>
  
  <tr>
    <td>
      getscreenshotpath<br />
    </td>
    
    <td>
    </td>
    
    <td>
      获取屏幕截图的路径<br />
    </td>
  </tr>
  
  <tr>
    <td>
      isviewserverstarted<br />
    </td>
    
    <td>
    </td>
    
    <td>
      判断viewserver是否已启动<br /> <br /> adb shell service call window 3<br />
    </td>
  </tr>
  
  <tr>
    <td>
      key_back<br />
    </td>
    
    <td>
    </td>
    
    <td>
      模拟按返回键<br />
    </td>
  </tr>
  
  <tr>
    <td>
      key_home<br />
    </td>
    
    <td>
    </td>
    
    <td>
      模拟按Home键<br />
    </td>
  </tr>
  
  <tr>
    <td>
      key_menu<br />
    </td>
    
    <td>
    </td>
    
    <td>
      模拟按菜单键<br />
    </td>
  </tr>
  
  <tr>
    <td>
      runtest<br />
    </td>
    
    <td>
    </td>
    
    <td>
      调用development/testrunner/runtest.py，进行测试<br />
    </td>
  </tr>
  
  <tr>
    <td>
      smoketest<br />
    </td>
    
    <td>
    </td>
    
    <td>
      利用SmokeTestApp.apk，SmokeTest.apk对系统进行一个smoke test<br />
    </td>
  </tr>
  
  <tr>
    <td>
      startviewserver<br />
    </td>
    
    <td>
    </td>
    
    <td>
      adb shell service call window 1 i32 $port<br />
    </td>
  </tr>
  
  <tr>
    <td>
      stopviewserver<br />
    </td>
    
    <td>
    </td>
    
    <td>
      adb shell<br /> service call window 2<br />
    </td>
  </tr>
  
  <tr>
    <td>
      systemstack<br />
    </td>
    
    <td>
    </td>
    
    <td>
      dump the current stack trace of all<br /> threads in the system process to the usual ANR traces file<br />
    </td>
  </tr>
  
  <tr>
    <td>
      tracedmdump<br />
    </td>
    
    <td>
    </td>
    
    <td>
      调用q2dm将系统堆栈导出来，并利用dmtracedump将其转为可读的html文件<br />
    </td>
  </tr>
</table>

### 1.5 提交代码相关命令

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
      aospremote<br />
    </td>
    
    <td>
    </td>
    
    <td>
      Add git remote<br /> for matching AOSP repository<br />
    </td>
  </tr>
  
  <tr>
    <td>
      cmgerrit<br />
    </td>
    
    <td>
    </td>
    
    <td>
      从CM拉源代码，或者将源代码提交到gerrit给比人审核，直接敲这个命令可得到该命令的使用帮助，最终调用Git完成命令功能<br />
    </td>
  </tr>
  
  <tr>
    <td>
      cmrebase<br />
    </td>
    
    <td>
    </td>
    
    <td>
      和git的rebase 衍合类似，我们不做代码提交，故此没必要<br />
    </td>
  </tr>
  
  <tr>
    <td>
      cmremote<br />
    </td>
    
    <td>
    </td>
    
    <td>
      Add git remote for CM Gerrit Review<br />
    </td>
  </tr>
  
  <tr>
    <td>
      makerecipe<br />
    </td>
    
    <td>
    </td>
    
    <td>
      将本地代码推送至git仓库<br />
    </td>
  </tr>
  
  <tr>
    <td>
      repopick<br />
    </td>
    
    <td>
    </td>
    
    <td>
      Utility to fetch changes from Gerrit，可选项有&#8211;ignore-missing，&#8211;start-branch，&#8211;abandon-first，&#8211;auto-branch<br />
    </td>
  </tr>
  
  <tr>
    <td>
      reposync<br />
    </td>
    
    <td>
    </td>
    
    <td>
      Parallel repo<br /> sync using ionice and SCHED_BATCH<br />
    </td>
  </tr>
</table>



## 2. source build/envsetup.sh 执行流程

envsetup.sh 定义了很多函数，除此之外还执行了其它操作，代码如下:

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
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">VARIANT_CHOICES</span>=<span style="color: #7a0874; font-weight: bold;">&#40;</span>user userdebug eng<span style="color: #7a0874; font-weight: bold;">&#41;</span>，<span style="color: #666666; font-style: italic;"># TARGET_BUILD_VARIANT变量的可能值</span>
<span style="color: #666666; font-style: italic;">#LUNCH_MENU_CHOICES是供用户选择的prodcut列表,</span>
<span style="color: #666666; font-style: italic;">#每次source build/envsetup.sh时需重置变量LUNCH_MENU_CHOICES</span>
<span style="color: #666666; font-style: italic;">#不然后续的include vendor/cm/vendorsetup.sh时会继续添加产品至变量LUNCH_MENU_CHOICES里，</span>
<span style="color: #666666; font-style: italic;">#导致出现很多重复产品</span>
<span style="color: #7a0874; font-weight: bold;">unset</span> LUNCH_MENU_CHOICES 
add_lunch_combo full-eng <span style="color: #666666; font-style: italic;">#默认添加full-eng，full_mips-eng等4个产品</span>
add_lunch_combo full_x86-eng
add_lunch_combo vbox_x86-eng
add_lunch_combo full_mips-eng
<span style="color: #7a0874; font-weight: bold;">alias</span> <span style="color: #007800;">bib</span>=breakfast<span style="color: #666666; font-style: italic;">#给breakfast起别名</span>
<span style="color: #7a0874; font-weight: bold;">complete</span> <span style="color: #660033;">-F</span> _lunch lunch <span style="color: #666666; font-style: italic;">#给lunch添加tab提示</span>
<span style="color: #000000; font-weight: bold;">case</span> <span style="color: #000000; font-weight: bold;">`</span><span style="color: #c20cb9; font-weight: bold;">uname</span> -s<span style="color: #000000; font-weight: bold;">`</span> <span style="color: #000000; font-weight: bold;">in</span> <span style="color: #666666; font-style: italic;">#定义sgrep函数 在所有工程类型代码里搜索</span>
    Darwin<span style="color: #7a0874; font-weight: bold;">&#41;</span>
        <span style="color: #000000; font-weight: bold;">function</span> sgrep<span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
        <span style="color: #7a0874; font-weight: bold;">&#123;</span>
            <span style="color: #c20cb9; font-weight: bold;">find</span> <span style="color: #660033;">-E</span> . <span style="color: #660033;">-name</span> .repo <span style="color: #660033;">-prune</span> <span style="color: #660033;">-o</span> <span style="color: #660033;">-name</span> .git <span style="color: #660033;">-prune</span> <span style="color: #660033;">-o</span>  <span style="color: #660033;">-type</span> f \
                 <span style="color: #660033;">-iregex</span> <span style="color: #ff0000;">'.*\.(c|h|cpp|S|java|xml|sh|mk)'</span> <span style="color: #660033;">-print0</span> \
                 <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">xargs</span> <span style="color: #660033;">-0</span> <span style="color: #c20cb9; font-weight: bold;">grep</span> <span style="color: #660033;">--color</span> <span style="color: #660033;">-n</span> <span style="color: #ff0000;">"$@"</span>
        <span style="color: #7a0874; font-weight: bold;">&#125;</span>
        <span style="color: #000000; font-weight: bold;">;;</span>
    <span style="color: #000000; font-weight: bold;">*</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
        <span style="color: #000000; font-weight: bold;">function</span> sgrep<span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
        <span style="color: #7a0874; font-weight: bold;">&#123;</span>
            <span style="color: #c20cb9; font-weight: bold;">find</span> . <span style="color: #660033;">-name</span> .repo <span style="color: #660033;">-prune</span> <span style="color: #660033;">-o</span> <span style="color: #660033;">-name</span> .git <span style="color: #660033;">-prune</span> <span style="color: #660033;">-o</span>  <span style="color: #660033;">-type</span> f \
                 <span style="color: #660033;">-iregex</span> <span style="color: #ff0000;">'.*\.\(c\|h\|cpp\|S\|java\|xml\|sh\|mk\)'</span> <span style="color: #660033;">-print0</span> \ 
                 <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">xargs</span> <span style="color: #660033;">-0</span> <span style="color: #c20cb9; font-weight: bold;">grep</span> <span style="color: #660033;">--color</span> <span style="color: #660033;">-n</span> <span style="color: #ff0000;">"$@"</span>
        <span style="color: #7a0874; font-weight: bold;">&#125;</span>
        <span style="color: #000000; font-weight: bold;">;;</span>
<span style="color: #000000; font-weight: bold;">esac</span>
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #660033;">-f</span> cmremote
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #660033;">-f</span> aospremote
<span style="color: #7a0874; font-weight: bold;">alias</span> <span style="color: #007800;">mmp</span>=<span style="color: #ff0000;">'dopush mm'</span> <span style="color: #666666; font-style: italic;">#定义更多编译后push到设备的函数的操作</span>
<span style="color: #7a0874; font-weight: bold;">alias</span> <span style="color: #007800;">mmmp</span>=<span style="color: #ff0000;">'dopush mmm'</span>
<span style="color: #7a0874; font-weight: bold;">alias</span> <span style="color: #007800;">mkap</span>=<span style="color: #ff0000;">'dopush mka'</span>
<span style="color: #7a0874; font-weight: bold;">alias</span> <span style="color: #007800;">cmkap</span>=<span style="color: #ff0000;">'dopush cmka'</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"x<span style="color: #007800;">$SHELL</span>"</span> <span style="color: #000000; font-weight: bold;">!</span>= <span style="color: #ff0000;">"x/bin/bash"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span> <span style="color: #666666; font-style: italic;">#只支持Bash终端</span>
    <span style="color: #000000; font-weight: bold;">case</span> <span style="color: #000000; font-weight: bold;">`</span><span style="color: #c20cb9; font-weight: bold;">ps</span> <span style="color: #660033;">-o</span> <span style="color: #7a0874; font-weight: bold;">command</span> <span style="color: #660033;">-p</span> <span style="color: #007800;">$$</span><span style="color: #000000; font-weight: bold;">`</span> <span style="color: #000000; font-weight: bold;">in</span>
        <span style="color: #000000; font-weight: bold;">*</span><span style="color: #c20cb9; font-weight: bold;">bash</span><span style="color: #000000; font-weight: bold;">*</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
            <span style="color: #000000; font-weight: bold;">;;</span>
        <span style="color: #000000; font-weight: bold;">*</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
            <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"WARNING: Only bash is supported,"</span>  \
                 <span style="color: #ff0000;">"use of other shell would lead to erroneous results"</span>
            <span style="color: #000000; font-weight: bold;">;;</span>
    <span style="color: #000000; font-weight: bold;">esac</span>
<span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #666666; font-style: italic;">#Execute the contents of any vendorsetup.sh files we can find.</span>
<span style="color: #666666; font-style: italic;">#source vendor和device下能找到的所有vendorsetup.sh</span>
<span style="color: #000000; font-weight: bold;">for</span> f <span style="color: #000000; font-weight: bold;">in</span> <span style="color: #000000; font-weight: bold;">`/</span>bin<span style="color: #000000; font-weight: bold;">/</span><span style="color: #c20cb9; font-weight: bold;">ls</span> vendor<span style="color: #000000; font-weight: bold;">/*/</span>vendorsetup.sh vendor<span style="color: #000000; font-weight: bold;">/*/*/</span>vendorsetup.sh device<span style="color: #000000; font-weight: bold;">/*/*/</span>vendorsetup.sh <span style="color: #000000;">2</span><span style="color: #000000; font-weight: bold;">&gt;</span> <span style="color: #000000; font-weight: bold;">/</span>dev<span style="color: #000000; font-weight: bold;">/</span>null<span style="color: #000000; font-weight: bold;">`</span>
<span style="color: #000000; font-weight: bold;">do</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"including <span style="color: #007800;">$f</span>"</span>
    . <span style="color: #007800;">$f</span>
<span style="color: #000000; font-weight: bold;">done</span>
<span style="color: #7a0874; font-weight: bold;">unset</span> f
<span style="color: #666666; font-style: italic;">#source目录 sdk/bash_completion vendor/cm/bash_completion下的bash脚本，</span>
<span style="color: #666666; font-style: italic;">#能提供tab提示</span>
addcompletions 
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">ANDROID_BUILD_TOP</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span>gettop<span style="color: #7a0874; font-weight: bold;">&#41;</span></pre>
      </td>
    </tr>
  </table>
</div>

### 2.1 执行的vendorsetup.sh有：

在envsetup.sh里将执行vendor和device目录及各自子目录下所有的vendorsetup.sh，这些vendorsetup.sh做的事情是调用add\_lunch\_combo将它们各自的产品添加到 LUNCH\_MENU\_CHOICES 变量里

#执行cm的vendorsetup.sh将从网上下载cm支持的产品列表，并添加至LUNCH\_MENU\_CHOICES

vendor/cm/vendorsetup.sh

#将添加mini\_armv7a\_neon产品 add\_lunch\_combo mini\_armv7a\_neon-userdebug

device/generic/armv7-a-neon/vendorsetup.sh

#add\_lunch\_combo mini_armv7a-userdebug

device/generic/armv7-a/vendorsetup.sh 

#add\_lunch\_combo mini_mips-userdebug

device/generic/mips/vendorsetup.sh

#add\_lunch\_combo mini_x86-userdebug 

device/generic/x86/vendorsetup.sh 

#add\_lunch\_combo cm_jflteatt-eng

device/samsung/jflteatt/vendorsetup.sh

\# add\_lunch\_combo full_panda-userdebug

device/ti/panda/vendorsetup.sh 

\# add\_lunch\_combo zte_blade-eng

#add\_lunch\_combo zte_blade-userdebug

device/zte/blade/vendorsetup.sh 

### 2.2 执行的completion bash有：

在envsetup.sh里将执行sdk/bash\_completion和vendor/cm/bash\_completion目录下的bash脚本，这些bash脚本主要是为命令提供tab支持，有了这些tab支持，输入命令后如果某个选项忘记了，只需要敲tab键，就能获得提示，使用命令更加方便

including sdk/bash_completion/adb.bash

including vendor/cm/bash_completion/git.bash

including vendor/cm/bash_completion/repo.bash

分别对应adb，git，repo的tab提示