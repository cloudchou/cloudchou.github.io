---
id: 276
title: Android编译系统详解(三)——编译流程详解
date: 2014-02-07T08:30:11+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=276
permalink: /android/post-276.html
views:
  - 18736
categories:
  - Android
tags:
  - Android droidcore
  - Android main.mk
  - Android 安装模块
  - Android编译系统详解
  - Android默认目标执行流程
---
## 1.概述

编译Android的第三步是使用mka命令进行编译，当然我们也可以使用make –j4，但是推荐使用mka命令。因为mka将自动计算-j选项的数字，让我们不用纠结这个数字到底是多少(这个数字其实就是所有cpu的核心数)。在编译时我们可以带上我们需要编译的目标，假设你想生成recovery，那么使用mka recoveryimage，如果想生成ota包，那么需要使用mka otapackage，后续会介绍所有可以使用的目标。另外注意有一些目标只是起到修饰的作用，也就是说需要和其它目标一起使用，共有4个用于修饰的伪目标:

  * 1) showcommands 显示编译过程中使用的命令
  * 2) incrementaljavac用于增量编译java代码
  * 3) checkbuild用于检验那些需要检验的模块
  * 4) all如果使用all修饰编译目标，会编译所有模块

研究Android编译系统时最头疼的可能是变量，成百个变量我们无法记住其含义，也不知道这些变量会是什么值，为此我专门做了一个编译变量的参考网站<a href="http://android.cloudchou.com" target="_blank">android.cloudchou.com</a>，你可以在该网站查找变量，它能告诉你变量的含义，也会给出你该变量的示例值，另外也详细解释了编译系统里每个Makefile的作用，这样你在看编译系统的代码时不至于一头雾水。

编译的核心文件是<a href="http://android.cloudchou.com/build/core/main.php" target="_blank">build/core/main.mk</a>和<a href="http://android.cloudchou.com/build/core/Makefile.php" target="_blank">build/core/makefile</a>，main.mk主要作用是检查编译环境是否符合要求，确定产品配置，决定产品需要使用的模块，并定义了许多目标供开发者使用，比如droid，sdk等目标，但是生成这些目标的规则主要在Makefile里定义，而内核的编译规则放在build/core/task/kernel.mk

我们将先整体介绍main.mk的执行流程，然后再针对在Linux上编译默认目标时使用的关键代码进行分析。Makefile主要定义了各个目标的生成规则，因此不再详细介绍它的执行流程，若有兴趣看每个目标的生成规则，可查看<a href="http://android.cloudchou.com/build/core/Makefile.php" target="_blank">http://android.cloudchou.com/build/core/Makefile.php</a>

## 2. main.mk执行流程

### 2.1 检验编译环境并建立产品配置

  * 1) 设置Shell变量为bash，不能使用其它shell
  * 2) 关闭make的suffix规则，rcs/sccs规则，并设置一个规则: 当某个规则失败了，就删除所有目标
  * 3) 检验make的版本，cygwin可使用任意版本make，但是linux或者mac只能使用3.81版本或者3.82版本
  * 4) 设置PWD,TOP,TOPDIR，BUILD_SYSTEM等变量，定义了默认目标变量，但是暂时并未定义默认目标的生成规则
  * 5) 包含<a href="http://android.cloudchou.com/build/core/help.php" target="_blank">build/core/help.mk</a>，该makefile定义了两个目标help和out, help用于显示帮助，out用于检验编译系统是否正确
  * 6) 包含<a href="http://android.cloudchou.com/build/core/config.php" target="_blank">build/core/config.mk</a>，config.mk作了很多配置，包括产品配置，包含该makefile后，会建立输出目录系列的变量，还会建立PRODUCT系列变量，后续介绍产品配置时，对此会有更多详细介绍
  * 7) 包含<a href="http://android.cloudchou.com/build/core/cleanbuild.php" target="_blank">build/core/cleanbuild.mk</a>，该makefile会包含所有工程的CleanSpec.mk，写了CleanSpec.mk的工程会定义每次编译前的特殊清理步骤，cleanbuild.mk会执行这些清除步骤
  * 8) 检验编译环境，先检测上次编译结果，如果上次检验的版本和此次检验的版本一致，则不再检测，然后进行检测并将此次编译结果写入

### 2.2 包含其它makefile及编译目标检测

  * 1) 如果目标里含有incrementaljavac， 那么编译目标时将用incremental javac进行增量编译
  * 2) 设置EMMA_INSTRUMENT变量的值，emma是用于测试代码覆盖率的库
  * 3) 包含<a href="http://android.cloudchou.com/build/core/definitions.php" target="_blank">build/core/definistions.mk</a>，该makefile定义了许多辅助函数
  * 4) 包含<a href="http://android.cloudchou.com/build/core/qcom_utils.php" target="_blank">build/core/qcom_utils.mk</a>，该makefile定义了高通板子的一些辅助函数及宏
  * 5) 包含<a href="http://android.cloudchou.com/build/core/dex_preopt.php" target="_blank">build/core/dex_preopt.mk</a>，该makefile定义了优化dex代码的一些宏
  * 6) 检测编译目标里是否有user,userdebug,eng，如果有则告诉用户放置在buildspec.mk或者使用lunch设置，检测TARGET\_BUILD\_VARIANT变量，看是否有效
  * 7) 包含<a href="http://android.cloudchou.com/build/core/pdk_config.php" target="_blank">build/core/pdk_config.mk</a>, PDK主要是能提高现有设备升级能力，帮助设备制造商能更快的适配新版本的android

### 2.3 根据TARGET\_BUILD\_VARIANT建立配置

  * 1) 如果编译目标里有sdk，win\_sdk或者sdk\_addon，那么设置is\_sdk\_build为true
  * 2) 如果定义了HAVE_SELINUX，那么编译时为build prop添加属性ro.build.selinux=1 
  * 3) 如果TARGET\_BUILD\_VARIANT是user或者userdebug，那么tags\_to\_install += debug 如果用户未定义DISABLE\_DEXPREOPT为true，并且是user模式，那么将设置WITH\_DEXPREOPT := true，该选项将开启apk的预优化，即将apk分成odex代码文件和apk资源文件
  * 4) 判断enable\_target\_debugging变量，默认是true，当build_variant是user时，则它是false。如果该变量值为true，则设置Rom的编译属性ro.debuggable为1，否则设置ro.debuggable为0
  * 5) 如果TARGET\_BUILD\_VARIANT是eng，那么tags\_to\_install为debug,eng， 并设置Rom的编译属性ro.setupwizard.mode为OPTIONAL，因为eng模式并不要安装向导
  * 6) 如果TARGET\_BUILD\_VARIANT是tests，那么tags\_to\_install := debug eng tests
  * 7) 设置sdk相关变量
  * 8) 添加一些额外的编译属性
  * 9) 定义should-install-to-system宏函数
  * 10) 若除了修饰目标，没定义任何目标，那么将使用默认目标编译

### 2.4 包含所有要编译的模块的Makefile

如果编译目标是clean clobber installclean dataclean，那么设置dont\_bother为true，若dont\_bother为false，则将所有要编译的模块包含进来 

1) 如果主机操作系统及体系结构为darwin-ppc(Mac电脑)，那么提示不支持编译Sdk，并将SDK_ONLY设置为true

2) 如果主机操作系统是windows，那么设置SDK_ONLY为true

3) 根据SDK\_ONLY是否为true，编译主机操作系统类型，BUILD\_TINY_ANDROID的值，设置sudbidrs变量

4) 将所有PRODUCT\_*相关变量存储至stash\_product_vars变量，稍后将验证它是否被修改

5) 根据ONE\_SHOT\_MAKEFILE的值是否为空，包含不同的makefile

6) 执行post_clean步骤，并确保产品相关变量没有变化

7) 检测是否有文件加入ALL_PREBUILT

8) 包含其它必须在所有Android.mk包含之后需要包含的makefile

9) 将known\_custom\_modules转化成安装路径得到变量CUSTOM_MODULES

10) 定义模块之间的依赖关系，$(ALL_MODULES.$(m).REQUIRED))变量指明了模块之间的依赖关系

11) 计算下述变量的值：product\_MODULES，debug\_MODULES，eng\_MODULES，tests\_MODULES，modules\_to\_install，overridden\_packages，target\_gnu\_MODULES，ALL\_DEFAULT\_INSTALLED\_MODULES

12) 包含build/core/Makefile

13) 定义变量modules\_to\_check

### 2.5 定义多个目标

这一节定义了众多目标，prebuilt，all\_copied\_headers，files，checkbuild，ramdisk，factory\_ramdisk，factory\_bundle，systemtarball，boottarball，userdataimage，userdatatarball，cacheimage，bootimage，droidcore，dist\_files，apps\_only，all_modules，docs，sdk，lintall，samplecode，findbugs，clean，modules，showcommands，nothing。

后续文章将列出所有可用的目标

## 3 编译默认目标时的执行流程

在介绍编译默认目标时的执行流程之前，先介绍一下ALL\_系列的变量，否则看代码时很难搞懂这些变量的出处，这些变量在包含所有模块后被建立，每个模块都有对应的用于编译的makefile，这些makefile会包含一个编译类型对应的makefile，比如package.mk，而这些makefile最终都会包含base\_rules.mk，在base_rules.mk里会为ALL系列变量添加值。所有这些变量及其来源均可在android.cloudchou.com查看详细解释：

  * 1) ALL\_DOCS所有文档的全路径，ALL\_DOCS的赋值在droiddoc.mk里, ALL\_DOCS += $(full\_target)
  * 2) ALL\_MODULES系统的所有模块的简单名字集合，编译系统还为每一个模块还定义了其它两个变量，ALL\_MODULES.$(LOCAL\_MODULE).BUILT 所有模块的生成路径ALL\_MODULES.$(LOCAL_MODULE).INSTALLED 所有模块的各自安装路径，详情请见<a href="http://android.cloudchou.com/build/core/definitions.php#ALL_MODULES" target="_blank">http://android.cloudchou.com/build/core/definitions.php#ALL_MODULES</a>
  * 3) ALL\_DEFAULT\_INSTALLED_MODULES 所有默认要安装的模块,在build/core/main.mk和build/core/makfile里设置
  * 4) ALL\_MODULE\_TAGS 使用LOCAL\_MODULE\_TAGS定义的所有tag集合，每一个tag对应一个ALL\_MODULE\_TAGS.变量，详情请见<a href="http://android.cloudchou.com/build/core/definitions.php#ALL_MODULE_TAGS" target="_blank">http://android.cloudchou.com/build/core/definitions.php#ALL_MODULE_TAGS</a>
  * 5) ALL\_MODULE\_NAME\_TAGS类似于ALL\_MODULE_TAGS，但是它的值是 某个tag的所有模块的名称 详情请见<a href="http://android.cloudchou.com/build/core/definitions.php#ALL_MODULE_NAME_TAGS" target="_blank">http://android.cloudchou.com/build/core/definitions.php#ALL_MODULE_NAME_TAGS</a>
  * 6) ALL\_HOST\_INSTALLED_FILES 安装在pc上的程序集合
  * 7) ALL_PREBUILT 将会被拷贝的预编译文件的安装全路径的集合
  * 8) ALL\_GENERATED\_SOURCES 某些工具生成的源代码文件的集合，比如aidl会生成java源代码文件
  * 9) ALL\_C\_CPP\_ETC\_OBJECTS 所有asm，c,c++,以及lex和yacc生成的c代码文件的全路径
  * 10) ALL\_ORIGINAL\_DYNAMIC_BINARIES 没有被优化，也没有被压缩的动态链接库
  * 11) ALL\_SDK\_FILES 将会放在sdk的文件 
  * 12) ALL\_FINDBUGS\_FILES 所有findbugs程序用的xml文件 
  * 13) ALL\_GPL\_MODULE\_LICENSE\_FILES GPL 模块的 许可文件
  * 14) ANDROID\_RESOURCE\_GENERATED_CLASSES Android 资源文件生成的java代码编译后的类的类型

### 3.1 关键代码

定义默认目标的代码位于main.mk：

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
        <pre class="make" style="font-family:monospace;"><span style="color: #990000;">.PHONY</span><span style="color: #004400;">:</span> droid
DEFAULT_GOAL <span style="color: #004400;">:=</span> droid
<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">DEFAULT_GOAL</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span></pre>
      </td>
    </tr>
  </table>
</div>

droid目标依赖的目标有：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="make" style="font-family:monospace;"><span style="color: #666622; font-weight: bold;">ifneq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_BUILD_APPS</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span><span style="color: #004400;">&#41;</span>
……
droid<span style="color: #004400;">:</span> apps_only <span style="color: #339900; font-style: italic;">#如果编译app，那么droid依赖apps_only目标</span>
<span style="color: #666622; font-weight: bold;">else</span>
……
droid<span style="color: #004400;">:</span> droidcore dist_files <span style="color: #339900; font-style: italic;">#默认依赖droidcore目标和dist_files目标</span>
<span style="color: #666622; font-weight: bold;">endif</span></pre>
      </td>
    </tr>
  </table>
</div>

dist_files目标依赖的目标主要是一些用于打包的工具，它们都是用dist-for-goals宏添加依赖关系的：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="make" style="font-family:monospace;"><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span> dist_files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">EMMA_META_ZIP</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
system<span style="color: #004400;">/</span>core<span style="color: #004400;">/</span>mkbootimg<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span> dist_files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span> LOCAL_BUILT_MODULE <span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
system<span style="color: #004400;">/</span>core<span style="color: #004400;">/</span>cpio<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">13</span><span style="color: #004400;">:$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span>dist_files<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">LOCAL_BUILT_MODULE</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
system<span style="color: #004400;">/</span>core<span style="color: #004400;">/</span>adb<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">88</span><span style="color: #004400;">:$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span>dist_files sdk<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">LOCAL_BUILT_MODULE</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
system<span style="color: #004400;">/</span>core<span style="color: #004400;">/</span>fastboot<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">68</span><span style="color: #004400;">:$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span>dist_files sdk<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">LOCAL_BUILT_MODULE</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
external<span style="color: #004400;">/</span>guava<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">26</span><span style="color: #004400;">:$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span> dist_files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">LOCAL_BUILT_MODULE</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span>guava<span style="color: #004400;">.</span>jar<span style="color: #004400;">&#41;</span>
external<span style="color: #004400;">/</span>yaffs2<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">28</span><span style="color: #004400;">:$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span> dist_files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">LOCAL_BUILT_MODULE</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
external<span style="color: #004400;">/</span>mp4parser<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">26</span><span style="color: #004400;">:$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span> dist_files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">LOCAL_BUILT_MODULE</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span>mp4parser<span style="color: #004400;">.</span>jar<span style="color: #004400;">&#41;</span>
external<span style="color: #004400;">/</span>jsr305<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">25</span><span style="color: #004400;">:$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span> dist_files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">LOCAL_BUILT_MODULE</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span>jsr305<span style="color: #004400;">.</span>jar<span style="color: #004400;">&#41;</span>
frameworks<span style="color: #004400;">/</span>support<span style="color: #004400;">/</span>renderscript<span style="color: #004400;">/</span>v8<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">29</span><span style="color: #004400;">:</span><span style="color: #339900; font-style: italic;">#$(call dist-for-goals, dist_files, $(LOCAL_BUILT_MODULE):volley.jar)</span>
frameworks<span style="color: #004400;">/</span>support<span style="color: #004400;">/</span>volley<span style="color: #004400;">/</span>Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">:</span><span style="color: #CC2200;">29</span><span style="color: #004400;">:</span><span style="color: #339900; font-style: italic;">#$(call dist-for-goals, dist_files, $(LOCAL_BUILT_MODULE):volley.jar)</span></pre>
      </td>
    </tr>
  </table>
</div>

我们再看droidcore目标依赖的目标有：

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
</pre>
      </td>
      
      <td class="code">
        <pre class="make" style="font-family:monospace;">droidcore<span style="color: #004400;">:</span> files \
	systemimage \ <span style="color: #339900; font-style: italic;">#system.img</span>
	<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_BOOTIMAGE_TARGET</span><span style="color: #004400;">&#41;</span> \ <span style="color: #339900; font-style: italic;">#boot.img</span>
	<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_RECOVERYIMAGE_TARGET</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;">#recovery.img</span>
	<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_USERDATAIMAGE_TARGET</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;">#data.img</span>
	<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_CACHEIMAGE_TARGET</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;">#cache.img</span>
	<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_FILES_FILE</span><span style="color: #004400;">&#41;</span><span style="color: #339900; font-style: italic;"># installed-files.txt</span>
<span style="color: #666622; font-weight: bold;">ifneq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_BUILD_APPS</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span><span style="color: #004400;">&#41;</span>
…<span style="color: #004400;">.</span>
<span style="color: #666622; font-weight: bold;">else</span>
<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> dist<span style="color: #004400;">-</span>for<span style="color: #004400;">-</span>goals<span style="color: #004400;">,</span> droidcore<span style="color: #004400;">,</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_UPDATE_PACKAGE_TARGET</span><span style="color: #004400;">&#41;</span> <span style="color: #339900; font-style: italic;">#cm_find5-img-eng.cloud.zip</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_OTA_PACKAGE_TARGET</span><span style="color: #004400;">&#41;</span> \ <span style="color: #339900; font-style: italic;"># cm_find5-ota-eng.cloud.zip</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">SYMBOLS_ZIP</span><span style="color: #004400;">&#41;</span> \ <span style="color: #339900; font-style: italic;"># cm_find5-symbols-eng.cloud.zip</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_FILES_FILE</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;"># installed-files.txt</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_BUILD_PROP_TARGET</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;"># system/build.prop</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILT_TARGET_FILES_PACKAGE</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;"># cm_find5-target_files-eng.cloud.zip</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_ANDROID_INFO_TXT_TARGET</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;"># android-info.txt</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_RAMDISK_TARGET</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;"># ramdisk.img</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_FACTORY_RAMDISK_TARGET</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;"># factory_ramdisk.gz</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_FACTORY_BUNDLE_TARGET</span><span style="color: #004400;">&#41;</span> \<span style="color: #339900; font-style: italic;"># cm_find5-factory_bundle- eng.cloud.zip</span>
   <span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">endif</span></pre>
      </td>
    </tr>
  </table>
</div>

system.img, boot.img, recovery.img, data.img,cache.img,installed_files.txt的生成规则在Makefile里定义, 在<a href="http://android.cloudchou.com/build/core/Makefile.php" target="_blank">http://android.cloudchou.com/build/core/Makefile.php</a>里可以看到详细的生成规则
  
再看一下files目标所依赖的目标：

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
        <pre class="make" style="font-family:monospace;">files<span style="color: #004400;">:</span> prebuilt \
        <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">modules_to_install</span><span style="color: #004400;">&#41;</span> \
        <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INSTALLED_ANDROID_INFO_TXT_TARGET</span><span style="color: #004400;">&#41;</span></pre>
      </td>
    </tr>
  </table>
</div>

prebuilt目标依赖$(ALL\_PREBUILT)，android-info.txt的生成规则在target/board/board.mk里定义，而$(modules\_to_install)目标是所有要安装的模块的集合，计算比较复杂，现在以在linux下编译默认目标为例，将涉及到的代码组织如下：

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
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
</pre>
      </td>
      
      <td class="code">
        <pre class="make" style="font-family:monospace;">……
tags_to_install <span style="color: #004400;">:=</span>
<span style="color: #666622; font-weight: bold;">ifneq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">user_variant</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
…<span style="color: #004400;">..</span>
  <span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">user_variant</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span>userdebug<span style="color: #004400;">&#41;</span>
  tags_to_install <span style="color: #004400;">+=</span> debug
  <span style="color: #666622; font-weight: bold;">else</span>
  …
  <span style="color: #666622; font-weight: bold;">endif</span>
<span style="color: #666622; font-weight: bold;">endif</span>
<span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_BUILD_VARIANT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span>eng<span style="color: #004400;">&#41;</span>
tags_to_install <span style="color: #004400;">:=</span> debug eng
…
<span style="color: #666622; font-weight: bold;">endif</span>
<span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_BUILD_VARIANT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span>tests<span style="color: #004400;">&#41;</span>
tags_to_install <span style="color: #004400;">:=</span> debug eng tests
<span style="color: #666622; font-weight: bold;">endif</span>
<span style="color: #666622; font-weight: bold;">ifdef</span> is_sdk_build
tags_to_install <span style="color: #004400;">:=</span> debug eng
<span style="color: #666622; font-weight: bold;">else</span> <span style="color: #339900; font-style: italic;"># !sdk</span>
<span style="color: #666622; font-weight: bold;">endif</span>
……
<span style="color: #339900; font-style: italic;"># ------------------------------------------------------------</span>
<span style="color: #339900; font-style: italic;"># Define a function that, given a list of module tags, returns</span>
<span style="color: #339900; font-style: italic;"># non-empty if that module should be installed in /system.</span>
&nbsp;
<span style="color: #339900; font-style: italic;"># For most goals, anything not tagged with the "tests" tag should</span>
<span style="color: #339900; font-style: italic;"># be installed in /system.</span>
define should<span style="color: #004400;">-</span>install<span style="color: #004400;">-</span>to<span style="color: #004400;">-</span>system
<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">if</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">filter</span> tests<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #CC2200;">1</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,,</span>true<span style="color: #004400;">&#41;</span>
endef
<span style="color: #666622; font-weight: bold;">ifdef</span> is_sdk_build
<span style="color: #339900; font-style: italic;"># For the sdk goal, anything with the "samples" tag should be</span>
<span style="color: #339900; font-style: italic;"># installed in /data even if that module also has "eng"/"debug"/"user".</span>
define should<span style="color: #004400;">-</span>install<span style="color: #004400;">-</span>to<span style="color: #004400;">-</span>system
<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">if</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">filter</span> samples tests<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #CC2200;">1</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,,</span>true<span style="color: #004400;">&#41;</span>
endef
<span style="color: #666622; font-weight: bold;">endif</span>
…
<span style="color: #339900; font-style: italic;">#接下来根据配置计算要查找的subdirs目录</span>
<span style="color: #666622; font-weight: bold;">ifneq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">dont_bother</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span>true<span style="color: #004400;">&#41;</span>
…
<span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">SDK_ONLY</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span>true<span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TOPDIR</span><span style="color: #004400;">&#41;</span>sdk<span style="color: #004400;">/</span>build<span style="color: #004400;">/</span>sdk_only_whitelist<span style="color: #004400;">.</span>mk
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TOPDIR</span><span style="color: #004400;">&#41;</span>development<span style="color: #004400;">/</span>build<span style="color: #004400;">/</span>sdk_only_whitelist<span style="color: #004400;">.</span>mk
<span style="color: #339900; font-style: italic;"># Exclude tools/acp when cross-compiling windows under linux</span>
<span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">findstring</span> Linux<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">UNAME</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span><span style="color: #004400;">&#41;</span>
subdirs <span style="color: #004400;">+=</span> build<span style="color: #004400;">/</span>tools<span style="color: #004400;">/</span>acp
<span style="color: #666622; font-weight: bold;">endif</span>
&nbsp;
<span style="color: #666622; font-weight: bold;">else</span>	<span style="color: #339900; font-style: italic;"># !SDK_ONLY</span>
<span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_TINY_ANDROID</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span> true<span style="color: #004400;">&#41;</span>
subdirs <span style="color: #004400;">:=</span> \
	bionic \
	system<span style="color: #004400;">/</span>core \
	system<span style="color: #004400;">/</span>extras<span style="color: #004400;">/</span>ext4_utils \
	system<span style="color: #004400;">/</span>extras<span style="color: #004400;">/</span>su \
	build<span style="color: #004400;">/</span>libs \
	build<span style="color: #004400;">/</span>target \
	build<span style="color: #004400;">/</span>tools<span style="color: #004400;">/</span>acp \
	external<span style="color: #004400;">/</span>gcc<span style="color: #004400;">-</span>demangle \
	external<span style="color: #004400;">/</span>mksh \
	external<span style="color: #004400;">/</span>openssl \
	external<span style="color: #004400;">/</span>yaffs2 \
	external<span style="color: #004400;">/</span>zlib
<span style="color: #666622; font-weight: bold;">else</span>	<span style="color: #339900; font-style: italic;"># !BUILD_TINY_ANDROID</span>
subdirs <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TOP</span><span style="color: #004400;">&#41;</span> 
FULL_BUILD <span style="color: #004400;">:=</span> true
<span style="color: #666622; font-weight: bold;">endif</span>	<span style="color: #339900; font-style: italic;"># !BUILD_TINY_ANDROID</span>
<span style="color: #666622; font-weight: bold;">endif</span>
<span style="color: #339900; font-style: italic;"># Before we go and include all of the module makefiles, stash away</span>
<span style="color: #339900; font-style: italic;"># the PRODUCT_* values so that later we can verify they are not modified.</span>
stash_product_vars<span style="color: #004400;">:=</span>true
<span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">stash_product_vars</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span>true<span style="color: #004400;">&#41;</span>
  <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> stash<span style="color: #004400;">-</span>product<span style="color: #004400;">-</span>vars<span style="color: #004400;">,</span> __STASHED<span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">endif</span>
…<span style="color: #004400;">.</span>
<span style="color: #666622; font-weight: bold;">ifneq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ONE_SHOT_MAKEFILE</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span><span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ONE_SHOT_MAKEFILE</span><span style="color: #004400;">&#41;</span>
CUSTOM_MODULES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> get<span style="color: #004400;">-</span>tagged<span style="color: #004400;">-</span>modules<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ALL_MODULE_TAGS</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
FULL_BUILD <span style="color: #004400;">:=</span>
…
<span style="color: #666622; font-weight: bold;">else</span> <span style="color: #339900; font-style: italic;"># ONE_SHOT_MAKEFILE</span>
<span style="color: #339900; font-style: italic;">#</span>
<span style="color: #339900; font-style: italic;"># Include all of the makefiles in the system</span>
<span style="color: #339900; font-style: italic;">#</span>
&nbsp;
<span style="color: #339900; font-style: italic;"># Can't use first-makefiles-under here because</span>
<span style="color: #339900; font-style: italic;"># --mindepth=2 makes the prunes not work.</span>
subdir_makefiles <span style="color: #004400;">:=</span> \
	<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">shell</span> build<span style="color: #004400;">/</span>tools<span style="color: #004400;">/</span>findleaves<span style="color: #004400;">.</span>py <span style="color: #004400;">--</span>prune<span style="color: #004400;">=</span>out <span style="color: #004400;">--</span>prune<span style="color: #004400;">=.</span>repo <span style="color: #004400;">--</span>prune<span style="color: #004400;">=.</span>git <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">subdirs</span><span style="color: #004400;">&#41;</span> Android<span style="color: #004400;">.</span>mk<span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">subdir_makefiles</span><span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #666622; font-weight: bold;">endif</span> <span style="color: #339900; font-style: italic;"># ONE_SHOT_MAKEFILE</span>
……
<span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">stash_product_vars</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span>true<span style="color: #004400;">&#41;</span>
  <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> assert<span style="color: #004400;">-</span>product<span style="color: #004400;">-</span>vars<span style="color: #004400;">,</span> __STASHED<span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">endif</span>
…
<span style="color: #339900; font-style: italic;"># -------------------------------------------------------------------</span>
<span style="color: #339900; font-style: italic;"># Fix up CUSTOM_MODULES to refer to installed files rather than</span>
<span style="color: #339900; font-style: italic;"># just bare module names.  Leave unknown modules alone in case</span>
<span style="color: #339900; font-style: italic;"># they're actually full paths to a particular file.</span>
known_custom_modules <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">filter</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ALL_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CUSTOM_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
unknown_custom_modules <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">filter-out</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ALL_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CUSTOM_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
CUSTOM_MODULES <span style="color: #004400;">:=</span> \
	<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> module<span style="color: #004400;">-</span>installed<span style="color: #004400;">-</span>files<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">known_custom_modules</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span> \
	<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>unknown_custom_modules
<span style="color: #339900; font-style: italic;"># -------------------------------------------------------------------</span>
<span style="color: #339900; font-style: italic;"># Figure out our module sets.</span>
<span style="color: #339900; font-style: italic;">#</span>
<span style="color: #339900; font-style: italic;"># Of the modules defined by the component makefiles,</span>
<span style="color: #339900; font-style: italic;"># determine what we actually want to build.</span>
&nbsp;
<span style="color: #666622; font-weight: bold;">ifdef</span> FULL_BUILD
  <span style="color: #339900; font-style: italic;"># The base list of modules to build for this product is specified</span>
  <span style="color: #339900; font-style: italic;"># by the appropriate product definition file, which was included</span>
  <span style="color: #339900; font-style: italic;"># by product_config.make.</span>
  product_MODULES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PRODUCTS<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>PRODUCT_PACKAGES<span style="color: #004400;">&#41;</span>
  <span style="color: #339900; font-style: italic;"># Filter out the overridden packages before doing expansion</span>
  product_MODULES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">filter-out</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> p<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">product_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span> \
      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PACKAGES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">p</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>OVERRIDES<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">product_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
  <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> expand<span style="color: #004400;">-</span>required<span style="color: #004400;">-</span>modules<span style="color: #004400;">,</span>product_MODULES<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">product_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
  product_FILES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> module<span style="color: #004400;">-</span>installed<span style="color: #004400;">-</span>files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">product_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
  <span style="color: #666622; font-weight: bold;">ifeq</span> <span style="color: #004400;">&#40;</span><span style="color: #CC2200;"></span><span style="color: #004400;">,</span><span style="color: #CC2200;">1</span><span style="color: #004400;">&#41;</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">info</span> product_FILES for <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_DEVICE</span><span style="color: #004400;">&#41;</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span><span style="color: #004400;">&#41;</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> p<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">product_FILES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">info</span> <span style="color: #004400;">:</span>   <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">p</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">error</span> done<span style="color: #004400;">&#41;</span>
  <span style="color: #666622; font-weight: bold;">endif</span>
<span style="color: #666622; font-weight: bold;">else</span>
  <span style="color: #339900; font-style: italic;"># We're not doing a full build, and are probably only including</span>
  <span style="color: #339900; font-style: italic;"># a subset of the module makefiles.  Don't try to build any modules</span>
  <span style="color: #339900; font-style: italic;"># requested by the product, because we probably won't have rules</span>
  <span style="color: #339900; font-style: italic;"># to build them.</span>
  product_FILES <span style="color: #004400;">:=</span>
<span style="color: #666622; font-weight: bold;">endif</span>
<span style="color: #339900; font-style: italic;"># When modules are tagged with debug eng or tests, they are installed</span>
<span style="color: #339900; font-style: italic;"># for those variants regardless of what the product spec says.</span>
debug_MODULES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> \
        <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> get<span style="color: #004400;">-</span>tagged<span style="color: #004400;">-</span>modules<span style="color: #004400;">,</span>debug<span style="color: #004400;">&#41;</span> \
        <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> module<span style="color: #004400;">-</span>installed<span style="color: #004400;">-</span>files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PRODUCTS<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>PRODUCT_PACKAGES_DEBUG<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span> \
    <span style="color: #004400;">&#41;</span>
eng_MODULES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> \
        <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> get<span style="color: #004400;">-</span>tagged<span style="color: #004400;">-</span>modules<span style="color: #004400;">,</span>eng<span style="color: #004400;">&#41;</span> \
        <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> module<span style="color: #004400;">-</span>installed<span style="color: #004400;">-</span>files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PRODUCTS<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>PRODUCT_PACKAGES_ENG<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span> \
    <span style="color: #004400;">&#41;</span>
tests_MODULES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> \
        <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> get<span style="color: #004400;">-</span>tagged<span style="color: #004400;">-</span>modules<span style="color: #004400;">,</span>tests<span style="color: #004400;">&#41;</span> \
        <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> module<span style="color: #004400;">-</span>installed<span style="color: #004400;">-</span>files<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PRODUCTS<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>PRODUCT_PACKAGES_TESTS<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span> \
<span style="color: #004400;">&#41;</span>
<span style="color: #339900; font-style: italic;"># TODO: Remove the 3 places in the tree that use ALL_DEFAULT_INSTALLED_MODULES</span>
<span style="color: #339900; font-style: italic;"># and get rid of it from this list.</span>
<span style="color: #339900; font-style: italic;"># TODO: The shell is chosen by magic.  Do we still need this?</span>
modules_to_install <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ALL_DEFAULT_INSTALLED_MODULES</span><span style="color: #004400;">&#41;</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">product_FILES</span><span style="color: #004400;">&#41;</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> tag<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">tags_to_install</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">tag</span><span style="color: #004400;">&#41;</span>_MODULES<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> get<span style="color: #004400;">-</span>tagged<span style="color: #004400;">-</span>modules<span style="color: #004400;">,</span> shell_<span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_SHELL</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">CUSTOM_MODULES</span><span style="color: #004400;">&#41;</span> \
  <span style="color: #004400;">&#41;</span>
<span style="color: #339900; font-style: italic;"># Some packages may override others using LOCAL_OVERRIDES_PACKAGES.</span>
<span style="color: #339900; font-style: italic;"># Filter out (do not install) any overridden packages.</span>
overridden_packages <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> get<span style="color: #004400;">-</span>package<span style="color: #004400;">-</span>overrides<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">modules_to_install</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">ifdef</span> overridden_packages
<span style="color: #339900; font-style: italic;">#  old_modules_to_install := $(modules_to_install)</span>
  modules_to_install <span style="color: #004400;">:=</span> \
      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">filter-out</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> p<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">overridden_packages</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">p</span><span style="color: #004400;">&#41;</span> <span style="color: #004400;">%/$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">p</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>apk<span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span> \
          <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">modules_to_install</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">endif</span>
<span style="color: #339900; font-style: italic;">#$(error filtered out</span>
<span style="color: #339900; font-style: italic;">#           $(filter-out $(modules_to_install),$(old_modules_to_install)))</span>
&nbsp;
<span style="color: #339900; font-style: italic;"># Don't include any GNU targets in the SDK.  It's ok (and necessary)</span>
<span style="color: #339900; font-style: italic;"># to build the host tools, but nothing that's going to be installed</span>
<span style="color: #339900; font-style: italic;"># on the target (including static libraries).</span>
<span style="color: #666622; font-weight: bold;">ifdef</span> is_sdk_build
  target_gnu_MODULES <span style="color: #004400;">:=</span> \
              <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">filter</span> \
                      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_OUT_INTERMEDIATES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">/%</span> \
                      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_OUT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">/%</span> \
                      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">TARGET_OUT_DATA</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">/%,</span> \
                              <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">call</span> get<span style="color: #004400;">-</span>tagged<span style="color: #004400;">-</span>modules<span style="color: #004400;">,</span>gnu<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
  <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">info</span> Removing from sdk<span style="color: #004400;">:</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> d<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">target_gnu_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">info</span> <span style="color: #004400;">:</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">d</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
  modules_to_install <span style="color: #004400;">:=</span> \
              <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">filter-out</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">target_gnu_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">modules_to_install</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
&nbsp;
  <span style="color: #339900; font-style: italic;"># Ensure every module listed in PRODUCT_PACKAGES* gets something installed</span>
  <span style="color: #339900; font-style: italic;"># TODO: Should we do this for all builds and not just the sdk?</span>
  <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> m<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PRODUCTS<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>PRODUCT_PACKAGES<span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">if</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">strip</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>INSTALLED<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,,</span>\
      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">warning</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>MAKEFILE<span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span> Module <span style="color: #CC2200;">'$(m)'</span> in PRODUCT_PACKAGES has nothing to install<span style="color: #004400;">!</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
  <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> m<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PRODUCTS<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>PRODUCT_PACKAGES_DEBUG<span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">if</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">strip</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>INSTALLED<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,,</span>\
      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">warning</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>MAKEFILE<span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span> Module <span style="color: #CC2200;">'$(m)'</span> in PRODUCT_PACKAGES_DEBUG has nothing to install<span style="color: #004400;">!</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
  <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> m<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PRODUCTS<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>PRODUCT_PACKAGES_ENG<span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">if</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">strip</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>INSTALLED<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,,</span>\
      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">warning</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>MAKEFILE<span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span> Module <span style="color: #CC2200;">'$(m)'</span> in PRODUCT_PACKAGES_ENG has nothing to install<span style="color: #004400;">!</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
  <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> m<span style="color: #004400;">,</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>PRODUCTS<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">INTERNAL_PRODUCT</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>PRODUCT_PACKAGES_TESTS<span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span> \
    <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">if</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">strip</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>INSTALLED<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,,</span>\
      <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #666622; font-weight: bold;">warning</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>MAKEFILE<span style="color: #004400;">&#41;</span><span style="color: #004400;">:</span> Module <span style="color: #CC2200;">'$(m)'</span> in PRODUCT_PACKAGES_TESTS has nothing to install<span style="color: #004400;">!</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">endif</span>
&nbsp;
<span style="color: #339900; font-style: italic;"># Install all of the host modules</span>
modules_to_install <span style="color: #004400;">+=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">modules_to_install</span><span style="color: #004400;">&#41;</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ALL_HOST_INSTALLED_FILES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #339900; font-style: italic;"># build/core/Makefile contains extra stuff that we don't want to pollute this</span>
<span style="color: #339900; font-style: italic;"># top-level makefile with.  It expects that ALL_DEFAULT_INSTALLED_MODULES</span>
<span style="color: #339900; font-style: italic;"># contains everything that's built during the current make, but it also further</span>
<span style="color: #339900; font-style: italic;"># extends ALL_DEFAULT_INSTALLED_MODULES.</span>
ALL_DEFAULT_INSTALLED_MODULES <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">modules_to_install</span><span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">include</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">BUILD_SYSTEM</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">/</span>Makefile
modules_to_install <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ALL_DEFAULT_INSTALLED_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
ALL_DEFAULT_INSTALLED_MODULES <span style="color: #004400;">:=</span>
&nbsp;
<span style="color: #666622; font-weight: bold;">endif</span> <span style="color: #339900; font-style: italic;"># dont_bother</span>
<span style="color: #339900; font-style: italic;"># These are additional goals that we build, in order to make sure that there</span>
<span style="color: #339900; font-style: italic;"># is as little code as possible in the tree that doesn't build.</span>
modules_to_check <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> m<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ALL_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>CHECKED<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
&nbsp;
<span style="color: #339900; font-style: italic;"># If you would like to build all goals, and not skip any intermediate</span>
<span style="color: #339900; font-style: italic;"># steps, you can pass the "all" modifier goal on the commandline.</span>
<span style="color: #666622; font-weight: bold;">ifneq</span> <span style="color: #004400;">&#40;</span><span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">filter</span> all<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">MAKECMDGOALS</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,</span><span style="color: #004400;">&#41;</span>
modules_to_check <span style="color: #004400;">+=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">foreach</span> m<span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">ALL_MODULES</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">,$</span><span style="color: #004400;">&#40;</span>ALL_MODULES<span style="color: #004400;">.$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">m</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">.</span>BUILT<span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
<span style="color: #666622; font-weight: bold;">endif</span>
&nbsp;
<span style="color: #339900; font-style: italic;"># for easier debugging</span>
modules_to_check <span style="color: #004400;">:=</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #0000CC; font-weight: bold;">sort</span> <span style="color: #004400;">$</span><span style="color: #004400;">&#40;</span><span style="color: #000088;">modules_to_check</span><span style="color: #004400;">&#41;</span><span style="color: #004400;">&#41;</span>
<span style="color: #339900; font-style: italic;">#$(error modules_to_check $(modules_to_check))</span></pre>
      </td>
    </tr>
  </table>
</div>