---
id: 261
title: Android编译系统详解(二)——命令执行流程
date: 2014-01-20T08:00:20+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=261
permalink: /android/post-261.html
views:
  - 9666
categories:
  - Android
tags:
  - android编译系统分析
  - Android编译系统详解
  - breafast command
  - breakfast lunch 命令执行流程
  - breakfast命令 lunch命令
  - lunch command
---
编译Rom的第一步是source build/envsetup.sh,该步骤将envsetup.sh里的函数声明为当前终端可用的命令，并将所有产品添加至变量LUNCH\_MENU\_CHOICES里。

编译Rom的第二步是让用户选择他想编译的产品，用户可以使用在source build/envsetup.sh后设置的breakfast或者lunch命令进行选择，接下来我们将详细分析这些命令的执行流程以及执行完breakfast命令或者lunch命令后在会话终端设置的变量

## 1. 命令执行流程

### 1.1 breakfast执行流程

流程：

  * 1) 从github上下载cm支持的产品，并添加至产品列表
  * 2) 如果命令参数为空，那么调用lunch函数，让用户选择产品
  * 3) 如果命令参数为1个且$target格式为$product-$build_variant，那么调用lunch $target，这样不需要用户选择产品
  * 4) 如果命令参数为1个且$target格式为$product，那么将其扩展为带build\_variant格式的产品，然后调用lunch cm\_$target-userdebug，这样不需要用户选择产品

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
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">target</span>=<span style="color: #007800;">$1</span>
<span style="color: #007800;">CM_DEVICES_ONLY</span>=<span style="color: #ff0000;">"true"</span> <span style="color: #666666; font-style: italic;">#只编译CM支持的设备</span>
<span style="color: #7a0874; font-weight: bold;">unset</span> LUNCH_MENU_CHOICES
add_lunch_combo full-eng
<span style="color: #666666; font-style: italic;">#vendor/cm/vendorsetup.sh 该脚本会从github上下载cm支持的产品，</span>
<span style="color: #666666; font-style: italic;">#并添加至LUNCH_MENU_CHOICES变量 ，该变量表示产品列表</span>
<span style="color: #000000; font-weight: bold;">for</span> f <span style="color: #000000; font-weight: bold;">in</span> <span style="color: #000000; font-weight: bold;">`/</span>bin<span style="color: #000000; font-weight: bold;">/</span><span style="color: #c20cb9; font-weight: bold;">ls</span> vendor<span style="color: #000000; font-weight: bold;">/</span>cm<span style="color: #000000; font-weight: bold;">/</span>vendorsetup.sh <span style="color: #000000;">2</span><span style="color: #000000; font-weight: bold;">&gt;</span> <span style="color: #000000; font-weight: bold;">/</span>dev<span style="color: #000000; font-weight: bold;">/</span>null<span style="color: #000000; font-weight: bold;">`</span> 
    <span style="color: #000000; font-weight: bold;">do</span>
        <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"including <span style="color: #007800;">$f</span>"</span>
        . <span style="color: #007800;">$f</span>  
    <span style="color: #000000; font-weight: bold;">done</span>
<span style="color: #7a0874; font-weight: bold;">unset</span> f
&nbsp;
 <span style="color: #666666; font-style: italic;">#如果没有带任何参数，那么调用lunch函数，让用户选择产品</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #007800;">$#</span> <span style="color: #660033;">-eq</span> <span style="color: #000000;"></span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>     
    lunch
<span style="color: #000000; font-weight: bold;">else</span>
<span style="color: #666666; font-style: italic;">#target格式：$product-$build_variant 或者 $product </span>
<span style="color: #666666; font-style: italic;">#  示例 cm_i9100-userdebug 或 i9100</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"z<span style="color: #007800;">$target</span>"</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">grep</span> <span style="color: #660033;">-q</span> <span style="color: #ff0000;">"-"</span>
    <span style="color: #666666; font-style: italic;">#如果用户输入的产品格式是$product-$build_variant 那么直接调用lunch</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #007800;">$?</span> <span style="color: #660033;">-eq</span> <span style="color: #000000;"></span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span> 
        <span style="color: #666666; font-style: italic;"># A buildtype was specified, assume a full device name</span>
        lunch <span style="color: #007800;">$target</span>
    <span style="color: #000000; font-weight: bold;">else</span>  
       <span style="color: #666666; font-style: italic;">#如果用户输入的产品格式是$product， </span>
       <span style="color: #666666; font-style: italic;">#那么扩展该变量为cm_$target-userdebug格式</span>
       <span style="color: #666666; font-style: italic;"># This is probably just the CM model name</span>
        lunch cm_<span style="color: #007800;">$target</span>-userdebug
    <span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #7a0874; font-weight: bold;">return</span> <span style="color: #007800;">$?</span></pre>
      </td>
    </tr>
  </table>
</div>

### 1.2 lunch执行流程

流程：

  * 1) 获取用户指定的产品或者让用户选择产品，并提取$product和$variant
  * 2) 检查是否支持产品
  * 3) 若不支持该产品，从网上下载该产品的相关配置到本地device目录，并再次检查是否支持该产品
  * 4) 若支持该产品，下载产品的最新配置到本地device目录
  * 5) 若还是不支持，告诉用户不支持并退出
  * 6) 设置环境变量export TARGET\_PRODUCT，TARGET\_BUILD\_VARIANT，TARGET\_BUILD_TYPE
  * 7) 建立$(OUT_DIR)/target/common目录
  * 8) 设置PROMPT\_COMMAND变量，java\_home，PATH目录，set\_sequence\_number
  * 9) 打印选择产品后对应的一些编译配置变量

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
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #7a0874; font-weight: bold;">local</span> answer
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"$1"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span> ; <span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #007800;">answer</span>=<span style="color: #007800;">$1</span>
<span style="color: #000000; font-weight: bold;">else</span> 
   <span style="color: #666666; font-style: italic;">#若调用者没有指定产品，那么打印产品列表，让用户选择</span>
    print_lunch_menu
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #660033;">-n</span> <span style="color: #ff0000;">"Which would you like? [full-eng] "</span>
    <span style="color: #c20cb9; font-weight: bold;">read</span> answer
<span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">selection</span>=
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #660033;">-z</span> <span style="color: #ff0000;">"<span style="color: #007800;">$answer</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span> <span style="color: #666666; font-style: italic;">#默认产品为full-eng</span>
<span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #007800;">selection</span>=full-eng
<span style="color: #000000; font-weight: bold;">elif</span> <span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #660033;">-n</span> <span style="color: #007800;">$answer</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">grep</span> <span style="color: #660033;">-q</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">"^[0-9][0-9]*$"</span><span style="color: #7a0874; font-weight: bold;">&#41;</span><span style="color: #666666; font-style: italic;">#用户如输入的是数字</span>
<span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #007800;">$answer</span> <span style="color: #660033;">-le</span> <span style="color: #800000;">${#LUNCH_MENU_CHOICES[@]}</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>
    <span style="color: #000000; font-weight: bold;">then</span>
        <span style="color: #007800;">selection</span>=<span style="color: #800000;">${LUNCH_MENU_CHOICES[$(($answer-1))]}</span>
    <span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #666666; font-style: italic;">#选择的产品为$product-$build_variant格式    </span>
<span style="color: #000000; font-weight: bold;">elif</span> <span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #660033;">-n</span> <span style="color: #007800;">$answer</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">grep</span> <span style="color: #660033;">-q</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">"^[^\-][^\-]*-[^\-][^\-]*$"</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
<span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #007800;">selection</span>=<span style="color: #007800;">$answer</span>
<span style="color: #000000; font-weight: bold;">fi</span>
&nbsp;
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #660033;">-z</span> <span style="color: #ff0000;">"<span style="color: #007800;">$selection</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span><span style="color: #666666; font-style: italic;">#selection格式为$product-$build_variant</span>
<span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"Invalid lunch combo: <span style="color: #007800;">$answer</span>"</span>
    <span style="color: #7a0874; font-weight: bold;">return</span> <span style="color: #000000;">1</span>
<span style="color: #000000; font-weight: bold;">fi</span>
&nbsp;
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">TARGET_BUILD_APPS</span>=
&nbsp;
 <span style="color: #666666; font-style: italic;">#提取product变量 product示例cm_i9100</span>
<span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">product</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #660033;">-n</span> <span style="color: #007800;">$selection</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">sed</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">"s/-.*$//"</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
check_product <span style="color: #007800;">$product</span> <span style="color: #666666; font-style: italic;">#检查产品是否支持</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #007800;">$?</span> <span style="color: #660033;">-ne</span> <span style="color: #000000;"></span> <span style="color: #7a0874; font-weight: bold;">&#93;</span><span style="color: #666666; font-style: italic;">#若产品不支持</span>
<span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #666666; font-style: italic;">#if we can't find a product, try to grab it off the CM github</span>
    <span style="color: #007800;">T</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span>gettop<span style="color: #7a0874; font-weight: bold;">&#41;</span>
    <span style="color: #7a0874; font-weight: bold;">pushd</span> <span style="color: #007800;">$T</span> <span style="color: #000000; font-weight: bold;">&gt;</span> <span style="color: #000000; font-weight: bold;">/</span>dev<span style="color: #000000; font-weight: bold;">/</span>null
    <span style="color: #666666; font-style: italic;">#下载prouct的配置 放在device/$vendor/$product目录</span>
    build<span style="color: #000000; font-weight: bold;">/</span>tools<span style="color: #000000; font-weight: bold;">/</span>roomservice.py <span style="color: #007800;">$product</span> 
    <span style="color: #7a0874; font-weight: bold;">popd</span> <span style="color: #000000; font-weight: bold;">&gt;</span> <span style="color: #000000; font-weight: bold;">/</span>dev<span style="color: #000000; font-weight: bold;">/</span>null
    check_product <span style="color: #007800;">$product</span> <span style="color: #666666; font-style: italic;">#再次检查产品是否支持</span>
<span style="color: #000000; font-weight: bold;">else</span>
    <span style="color: #666666; font-style: italic;">#获取最新配置 更新device/$vendor/$product</span>
    build<span style="color: #000000; font-weight: bold;">/</span>tools<span style="color: #000000; font-weight: bold;">/</span>roomservice.py <span style="color: #007800;">$product</span> <span style="color: #c20cb9; font-weight: bold;">true</span>
<span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #007800;">$?</span> <span style="color: #660033;">-ne</span> <span style="color: #000000;"></span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>
<span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"** Don't have a product spec for: '<span style="color: #007800;">$product</span>'"</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"** Do you have the right repo manifest?"</span>
    <span style="color: #007800;">product</span>=
<span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #666666; font-style: italic;">#从$product-$build_variant里提取$variant</span>
<span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">variant</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #660033;">-n</span> <span style="color: #007800;">$selection</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">sed</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">"s/^[^\-]*-//"</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
check_variant <span style="color: #007800;">$variant</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #007800;">$?</span> <span style="color: #660033;">-ne</span> <span style="color: #000000;"></span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>
<span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"** Invalid variant: '<span style="color: #007800;">$variant</span>'"</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"** Must be one of <span style="color: #007800;">${VARIANT_CHOICES[@]}</span>"</span>
    <span style="color: #007800;">variant</span>=
<span style="color: #000000; font-weight: bold;">fi</span>
&nbsp;
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #660033;">-z</span> <span style="color: #ff0000;">"<span style="color: #007800;">$product</span>"</span> <span style="color: #660033;">-o</span> <span style="color: #660033;">-z</span> <span style="color: #ff0000;">"<span style="color: #007800;">$variant</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>
<span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span>
    <span style="color: #7a0874; font-weight: bold;">return</span> <span style="color: #000000;">1</span>
<span style="color: #000000; font-weight: bold;">fi</span>
&nbsp;
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">TARGET_PRODUCT</span>=<span style="color: #007800;">$product</span>
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">TARGET_BUILD_VARIANT</span>=<span style="color: #007800;">$variant</span>
<span style="color: #7a0874; font-weight: bold;">export</span> <span style="color: #007800;">TARGET_BUILD_TYPE</span>=release
&nbsp;
fixup_common_out_dir <span style="color: #666666; font-style: italic;">#建立$(OUT_DIR)/target/common目录</span>
&nbsp;
<span style="color: #666666; font-style: italic;">#设置PROMPT_COMMAND变量，java_home，PATH目录，set_sequence_number</span>
set_stuff_for_environment
<span style="color: #666666; font-style: italic;"># 打印选择产品后的重要环境变量</span>
printconfig</pre>
      </td>
    </tr>
  </table>
</div>

### 1.3 check_product执行流程

流程：

  * 1) export CM\_BUILD CM\_BUILD示例：若$1是cm\_i9100，则CM\_BUILD是i9100
  * 2) 调用get\_build\_var TARGET_DEVICE

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
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">T</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span>gettop<span style="color: #7a0874; font-weight: bold;">&#41;</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #000000; font-weight: bold;">!</span> <span style="color: #ff0000;">"<span style="color: #007800;">$T</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"Couldn't locate the top of the tree.  Try setting TOP."</span> <span style="color: #000000; font-weight: bold;">&gt;&</span><span style="color: #000000;">2</span>
    <span style="color: #7a0874; font-weight: bold;">return</span>
<span style="color: #000000; font-weight: bold;">fi</span>
&nbsp;
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #660033;">-n</span> <span style="color: #007800;">$1</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">grep</span> <span style="color: #660033;">-q</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">"^cm_"</span><span style="color: #7a0874; font-weight: bold;">&#41;</span> ; <span style="color: #000000; font-weight: bold;">then</span>
   <span style="color: #007800;">CM_BUILD</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #660033;">-n</span> <span style="color: #007800;">$1</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">sed</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">'s/^cm_//g'</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
<span style="color: #000000; font-weight: bold;">else</span>
   <span style="color: #007800;">CM_BUILD</span>=
<span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #7a0874; font-weight: bold;">export</span> CM_BUILD
<span style="color: #007800;">CALLED_FROM_SETUP</span>=<span style="color: #c20cb9; font-weight: bold;">true</span> <span style="color: #007800;">BUILD_SYSTEM</span>=build<span style="color: #000000; font-weight: bold;">/</span>core \
    <span style="color: #007800;">TARGET_PRODUCT</span>=<span style="color: #007800;">$1</span> \
    <span style="color: #007800;">TARGET_BUILD_VARIANT</span>= \
    <span style="color: #007800;">TARGET_BUILD_TYPE</span>= \
    <span style="color: #007800;">TARGET_BUILD_APPS</span>= \
    get_build_var TARGET_DEVICE <span style="color: #000000; font-weight: bold;">&gt;</span> <span style="color: #000000; font-weight: bold;">/</span>dev<span style="color: #000000; font-weight: bold;">/</span>null</pre>
      </td>
    </tr>
  </table>
</div>

### 1.4 get\_build\_var执行流程

调用流程：lunch->check\_product->get\_build\_var TARGET\_DEVICE

此时的环境变量有

1)TARGET\_PRODUCT:cm\_i9100 

2)CALLED\_FROM\_SETUP:true 

3)BUILD_SYSTEM:build/core

4)export CM_BUILD=i9100

最终调用build/core/config.mk来完成检测是否支持产品$TARGET_PRODUCT

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
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">T</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span>gettop<span style="color: #7a0874; font-weight: bold;">&#41;</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #000000; font-weight: bold;">!</span> <span style="color: #ff0000;">"<span style="color: #007800;">$T</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"Couldn't locate the top of the tree.  Try setting TOP."</span> <span style="color: #000000; font-weight: bold;">&gt;&</span><span style="color: #000000;">2</span>
    <span style="color: #7a0874; font-weight: bold;">return</span>
<span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #007800;">CALLED_FROM_SETUP</span>=<span style="color: #c20cb9; font-weight: bold;">true</span> <span style="color: #007800;">BUILD_SYSTEM</span>=build<span style="color: #000000; font-weight: bold;">/</span>core \
 <span style="color: #666666; font-style: italic;">#$1的值可能为TARGET_DEVICE</span>
  <span style="color: #c20cb9; font-weight: bold;">make</span> <span style="color: #660033;">--no-print-directory</span> <span style="color: #660033;">-C</span> <span style="color: #ff0000;">"<span style="color: #007800;">$T</span>"</span> <span style="color: #660033;">-f</span> build<span style="color: #000000; font-weight: bold;">/</span>core<span style="color: #000000; font-weight: bold;">/</span>config.mk dumpvar-<span style="color: #007800;">$1</span></pre>
      </td>
    </tr>
  </table>
</div>

选择好产品后，可用get\_build\_var查看产品对应的编译变量，它依赖于以下环境变量

export TARGET\_PRODUCT=cm\_i9100 

export TARGET\_BUILD\_VARIANT=userdebug

export TARGET\_BUILD\_TYPE=release

export CM_BUILD=i9100

因此makefile里定义的变量并未添加至环境变量，每次调用get\_build\_var时，其实是调用config.mk依赖的dumpvar.mk实时计算出编译变量的值

比如说LEX变量 HOST_ARCH变量

### 1.5 printconfig执行流程

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
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #007800;">T</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span>gettop<span style="color: #7a0874; font-weight: bold;">&#41;</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #000000; font-weight: bold;">!</span> <span style="color: #ff0000;">"<span style="color: #007800;">$T</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"Couldn't locate the top of the tree.  Try setting TOP."</span> <span style="color: #000000; font-weight: bold;">&gt;&</span><span style="color: #000000;">2</span>
    <span style="color: #7a0874; font-weight: bold;">return</span>
<span style="color: #000000; font-weight: bold;">fi</span>
get_build_var report_config</pre>
      </td>
    </tr>
  </table>
</div>

最终调用build/core/dumpvar.mk来完成变量的打印

示例：

PLATFORM\_VERSION\_CODENAME=REL

PLATFORM_VERSION=4.2.2

CM_VERSION=10.1-20130822-UNOFFICIAL-i9100

TARGET\_PRODUCT=cm\_i9100

TARGET\_BUILD\_VARIANT=userdebug

TARGET\_BUILD\_TYPE=release

TARGET\_BUILD\_APPS=

TARGET_ARCH=arm

TARGET\_ARCH\_VARIANT=armv7-a-neon

HOST_ARCH=x86

HOST_OS=linux

HOST\_OS\_EXTRA=Linux-2.6.32-33-generic-x86_64-with-Ubuntu-10.04-lucid

HOST\_BUILD\_TYPE=release

BUILD_ID=JDQ39E

OUT\_DIR=/home/android/tmp/android\_out/CyanogenMod

### 1.5 mm执行流程

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
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">MM_MAKE</span>=<span style="color: #c20cb9; font-weight: bold;">make</span>
<span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">ARG</span>=
<span style="color: #000000; font-weight: bold;">for</span> ARG <span style="color: #000000; font-weight: bold;">in</span> $<span style="color: #000000; font-weight: bold;">@</span> ; <span style="color: #000000; font-weight: bold;">do</span> <span style="color: #666666; font-style: italic;">#如果参数中有mka，那么利用mka进行编译</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$ARG</span>"</span> = mka <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
        <span style="color: #007800;">MM_MAKE</span>=mka
    <span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #000000; font-weight: bold;">done</span>
<span style="color: #666666; font-style: italic;">#如果处在根目录 利用Android根目录的makefile编译选中目标</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #660033;">-f</span> build<span style="color: #000000; font-weight: bold;">/</span>core<span style="color: #000000; font-weight: bold;">/</span>envsetup.mk <span style="color: #660033;">-a</span> <span style="color: #660033;">-f</span> Makefile <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span> 
    <span style="color: #007800;">$MM_MAKE</span> $<span style="color: #000000; font-weight: bold;">@</span> 
<span style="color: #000000; font-weight: bold;">else</span>    
    <span style="color: #007800;">T</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span>gettop<span style="color: #7a0874; font-weight: bold;">&#41;</span>
    <span style="color: #666666; font-style: italic;">#找到最近的makfile，即当前目录所在工程的makefile</span>
    <span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">M</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span>findmakefile<span style="color: #7a0874; font-weight: bold;">&#41;</span> 
    <span style="color: #666666; font-style: italic;"># Remove the path to top as the makefilepath needs to be relative</span>
    <span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">M</span>=<span style="color: #000000; font-weight: bold;">`</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #007800;">$M</span><span style="color: #000000; font-weight: bold;">|</span><span style="color: #c20cb9; font-weight: bold;">sed</span> <span style="color: #ff0000;">'s:'</span><span style="color: #007800;">$T</span><span style="color: #ff0000;">'/::'</span><span style="color: #000000; font-weight: bold;">`</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #000000; font-weight: bold;">!</span> <span style="color: #ff0000;">"<span style="color: #007800;">$T</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
        <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"Couldn't locate the top of the tree.  Try setting TOP."</span>
    <span style="color: #000000; font-weight: bold;">elif</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #000000; font-weight: bold;">!</span> <span style="color: #ff0000;">"<span style="color: #007800;">$M</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
        <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"Couldn't locate a makefile from the current directory."</span>
    <span style="color: #000000; font-weight: bold;">else</span>
        <span style="color: #666666; font-style: italic;">#使用ONE_SHOT_MAKEFILE关键字确定工程所用的makefile，</span>
        <span style="color: #666666; font-style: italic;">#并利用Android根目录的makefile进行编译</span>
        <span style="color: #007800;">ONE_SHOT_MAKEFILE</span>=<span style="color: #007800;">$M</span> <span style="color: #007800;">$MM_MAKE</span> <span style="color: #660033;">-C</span> <span style="color: #007800;">$T</span> all_modules $<span style="color: #000000; font-weight: bold;">@</span> 
    <span style="color: #000000; font-weight: bold;">fi</span>
<span style="color: #000000; font-weight: bold;">fi</span></pre>
      </td>
    </tr>
  </table>
</div>

### 1.5 mmm执行流程

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
</pre>
      </td>
      
      <td class="code">
        <pre class="bash" style="font-family:monospace;"><span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">MMM_MAKE</span>=<span style="color: #c20cb9; font-weight: bold;">make</span>
<span style="color: #007800;">T</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span>gettop<span style="color: #7a0874; font-weight: bold;">&#41;</span>
<span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$T</span>"</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
    <span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">MAKEFILE</span>=
    <span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">MODULES</span>=
    <span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">ARGS</span>=
    <span style="color: #7a0874; font-weight: bold;">local</span> DIR TO_CHOP
    <span style="color: #666666; font-style: italic;">#提取编译选项(用-指定编译参数)</span>
    <span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">DASH_ARGS</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"$@"</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">awk</span> <span style="color: #660033;">-v</span> <span style="color: #007800;">RS</span>=<span style="color: #ff0000;">" "</span> <span style="color: #660033;">-v</span> <span style="color: #007800;">ORS</span>=<span style="color: #ff0000;">" "</span> <span style="color: #ff0000;">'/^-.*$/'</span><span style="color: #7a0874; font-weight: bold;">&#41;</span> 
    <span style="color: #666666; font-style: italic;">#提取编译目录</span>
    <span style="color: #7a0874; font-weight: bold;">local</span> <span style="color: #007800;">DIRS</span>=$<span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"$@"</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">awk</span> <span style="color: #660033;">-v</span> <span style="color: #007800;">RS</span>=<span style="color: #ff0000;">" "</span> <span style="color: #660033;">-v</span> <span style="color: #007800;">ORS</span>=<span style="color: #ff0000;">" "</span> <span style="color: #ff0000;">'/^[^-].*$/'</span><span style="color: #7a0874; font-weight: bold;">&#41;</span>
    <span style="color: #000000; font-weight: bold;">for</span> DIR <span style="color: #000000; font-weight: bold;">in</span> <span style="color: #007800;">$DIRS</span> ; <span style="color: #000000; font-weight: bold;">do</span>
        <span style="color: #007800;">MODULES</span>=<span style="color: #000000; font-weight: bold;">`</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #007800;">$DIR</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">sed</span> <span style="color: #660033;">-n</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">'s/.*:\(.*$\)/\1/p'</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">sed</span> <span style="color: #ff0000;">'s/,/ /'</span><span style="color: #000000; font-weight: bold;">`</span>
        <span style="color: #666666; font-style: italic;">#提取模块 dir格式:dirname:modulename</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$MODULES</span>"</span> = <span style="color: #ff0000;">""</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
            <span style="color: #007800;">MODULES</span>=all_modules
        <span style="color: #000000; font-weight: bold;">fi</span>
        <span style="color: #007800;">DIR</span>=<span style="color: #000000; font-weight: bold;">`</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #007800;">$DIR</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">sed</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">'s/:.*//'</span> <span style="color: #660033;">-e</span> <span style="color: #ff0000;">'s:/$::'</span><span style="color: #000000; font-weight: bold;">`</span>
        <span style="color: #666666; font-style: italic;">#如果指定目录有Android.mk，计算出MAKEFILE变量的值</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #660033;">-f</span> <span style="color: #007800;">$DIR</span><span style="color: #000000; font-weight: bold;">/</span>Android.mk <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span> 
            <span style="color: #007800;">TO_CHOP</span>=<span style="color: #000000; font-weight: bold;">`</span><span style="color: #7a0874; font-weight: bold;">&#40;</span><span style="color: #7a0874; font-weight: bold;">cd</span> <span style="color: #660033;">-P</span> <span style="color: #660033;">--</span> <span style="color: #007800;">$T</span> <span style="color: #000000; font-weight: bold;">&&</span> <span style="color: #7a0874; font-weight: bold;">pwd</span> -P<span style="color: #7a0874; font-weight: bold;">&#41;</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">wc</span> <span style="color: #660033;">-c</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">tr</span> <span style="color: #660033;">-d</span> <span style="color: #ff0000;">' '</span><span style="color: #000000; font-weight: bold;">`</span>
            <span style="color: #007800;">TO_CHOP</span>=<span style="color: #000000; font-weight: bold;">`</span><span style="color: #c20cb9; font-weight: bold;">expr</span> <span style="color: #007800;">$TO_CHOP</span> + <span style="color: #000000;">1</span><span style="color: #000000; font-weight: bold;">`</span>
            <span style="color: #007800;">START</span>=<span style="color: #000000; font-weight: bold;">`</span><span style="color: #007800;">PWD</span>= <span style="color: #000000; font-weight: bold;">/</span>bin<span style="color: #000000; font-weight: bold;">/</span><span style="color: #7a0874; font-weight: bold;">pwd</span><span style="color: #000000; font-weight: bold;">`</span>
            <span style="color: #007800;">MFILE</span>=<span style="color: #000000; font-weight: bold;">`</span><span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #007800;">$START</span> <span style="color: #000000; font-weight: bold;">|</span> <span style="color: #c20cb9; font-weight: bold;">cut</span> <span style="color: #660033;">-c</span><span style="color: #800000;">${TO_CHOP}</span>-<span style="color: #000000; font-weight: bold;">`</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$MFILE</span>"</span> = <span style="color: #ff0000;">""</span> <span style="color: #7a0874; font-weight: bold;">&#93;</span> ; <span style="color: #000000; font-weight: bold;">then</span>
                <span style="color: #007800;">MFILE</span>=<span style="color: #007800;">$DIR</span><span style="color: #000000; font-weight: bold;">/</span>Android.mk
            <span style="color: #000000; font-weight: bold;">else</span>
                <span style="color: #007800;">MFILE</span>=<span style="color: #007800;">$MFILE</span><span style="color: #000000; font-weight: bold;">/</span><span style="color: #007800;">$DIR</span><span style="color: #000000; font-weight: bold;">/</span>Android.mk
            <span style="color: #000000; font-weight: bold;">fi</span>
            <span style="color: #007800;">MAKEFILE</span>=<span style="color: #ff0000;">"<span style="color: #007800;">$MAKEFILE</span> <span style="color: #007800;">$MFILE</span>"</span> 
        <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #666666; font-style: italic;">#特殊目标 其实是做编译参数</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$DIR</span>"</span> = snod <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
                <span style="color: #007800;">ARGS</span>=<span style="color: #ff0000;">"<span style="color: #007800;">$ARGS</span> snod"</span>
            <span style="color: #000000; font-weight: bold;">elif</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$DIR</span>"</span> = showcommands <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
                <span style="color: #007800;">ARGS</span>=<span style="color: #ff0000;">"<span style="color: #007800;">$ARGS</span> showcommands"</span>
            <span style="color: #000000; font-weight: bold;">elif</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$DIR</span>"</span> = dist <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
                <span style="color: #007800;">ARGS</span>=<span style="color: #ff0000;">"<span style="color: #007800;">$ARGS</span> dist"</span>
            <span style="color: #000000; font-weight: bold;">elif</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$DIR</span>"</span> = incrementaljavac <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
                <span style="color: #007800;">ARGS</span>=<span style="color: #ff0000;">"<span style="color: #007800;">$ARGS</span> incrementaljavac"</span>
            <span style="color: #000000; font-weight: bold;">elif</span> <span style="color: #7a0874; font-weight: bold;">&#91;</span> <span style="color: #ff0000;">"<span style="color: #007800;">$DIR</span>"</span> = mka <span style="color: #7a0874; font-weight: bold;">&#93;</span>; <span style="color: #000000; font-weight: bold;">then</span>
                <span style="color: #007800;">MMM_MAKE</span>=mka
            <span style="color: #000000; font-weight: bold;">else</span>
                <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"No Android.mk in <span style="color: #007800;">$DIR</span>."</span>
                <span style="color: #7a0874; font-weight: bold;">return</span> <span style="color: #000000;">1</span>
            <span style="color: #000000; font-weight: bold;">fi</span>
        <span style="color: #000000; font-weight: bold;">fi</span>
    <span style="color: #000000; font-weight: bold;">done</span>
    <span style="color: #666666; font-style: italic;">#使用ONE_SHOT_MAKEFILE关键字确定工程所用的makefile，</span>
    <span style="color: #666666; font-style: italic;">#并利用Android根目录的makefile进行编译</span>
    <span style="color: #007800;">ONE_SHOT_MAKEFILE</span>=<span style="color: #ff0000;">"<span style="color: #007800;">$MAKEFILE</span>"</span> <span style="color: #007800;">$MMM_MAKE</span> <span style="color: #660033;">-C</span> <span style="color: #007800;">$T</span> <span style="color: #007800;">$DASH_ARGS</span> <span style="color: #007800;">$MODULES</span> <span style="color: #007800;">$ARGS</span>
<span style="color: #000000; font-weight: bold;">else</span>
    <span style="color: #7a0874; font-weight: bold;">echo</span> <span style="color: #ff0000;">"Couldn't locate the top of the tree.  Try setting TOP."</span>
<span style="color: #000000; font-weight: bold;">fi</span></pre>
      </td>
    </tr>
  </table>
</div>



## 2. breakfast或者lunch命令执行后在会话终端定义的变量

在执行完breakfast或者lunch命令后，会在当前终端设置许多变量，这些变量有些只能在当前shell里使用，有些能继续在子shell里使用(用sh执行某个shell脚本即在子shell里)。根据变量定义位置，将变量分为3类：

  * 1) 函数：是在函数定义的变量，但并未用export显示指出，在子shell里不可用，当前shell可用
  * 2) export:导出的环境变量，子Shell也可用
  * 3) 文件：文件里定义的变量

<table class="dataintable">
  <tr>
    <th width="245px">
      变量
    </th>
    
    <th width="60px">
      类型
    </th>
    
    <th>
      说明
    </th>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">T</span><br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      根目录<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">TARGET_BUILD_TYPE</span><br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      release或者debug<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">TARGET_PRODUCT</span><br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      示例：cm_find5<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">TARGET_BUILD_VARIANT</span><br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      可能的值为user,userdebug,eng<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">TARGET_BUILD_APPS</span><br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      需要编译的App集合<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">CM_BUILD</span><br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      示例find5<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">VARIANT_CHOICES</span><br />
    </td>
    
    <td>
      文件<br />
    </td>
    
    <td>
      (user userdebug<br /> eng)<br />
    </td>
  </tr>
  
  <tr>
    <td>
      <span class="emphasize">LUNCH_MENU_CHOICES</span><br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      产品列表<br />
    </td>
  </tr>
  
  <tr>
    <td>
      prebuiltdir<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      $(getprebuilt)<br />
    </td>
  </tr>
  
  <tr>
    <td>
      gccprebuiltdir<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      $(get_abs_build_var<br /> ANDROID_GCC_PREBUILTS)<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_EABI_TOOLCHAIN<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      工具链所在目录：以下选项之一<br /> <br /> $ gccprebuiltdir<br /> /x86/i686-linux-android-4.6/bin<br /> <br /> $ gccprebuiltdir<br /> /arm/arm-linux-androideabi-4.6/bin<br /> <br /> $ gccprebuiltdir<br /> /mips/mipsel-linux-android-4.6/bin<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_TOOLCHAIN<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $ANDROID_EABI_TOOLCHAIN<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_QTOOLS<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $T/development/emulator/qtools<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_DEV_SCRIPTS<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $T/development/scripts<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_BUILD_PATHS<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $(get_build_var<br /> ANDROID_BUILD_PATHS):<br /> <br /> $ANDROID_QTOOLS:<br /> <br /> $ANDROID_TOOLCHAIN:<br /> <br /> $ARM_EABI_TOOLCHAIN_PATH:<br /> <br /> $CODE_REVIEWS:$ANDROID_DEV_SCRIPTS:<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ARM_EABI_TOOLCHAIN<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $gccprebuiltdir/ arm/arm-eabi-4.6/bin<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ARM_EABI_TOOLCHAIN_PATH<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      $gccprebuiltdir/<br /> arm/arm-eabi-4.6/bin<br />
    </td>
  </tr>
  
  <tr>
    <td>
      toolchaindir<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      以下三个选项之一<br /> <br /> x86/i686-linux-android-4.6/bin<br /> <br /> arm/arm-linux-androideabi-4.6/bin<br /> <br /> mips/mipsel-linux-android-4.6/bin<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_JAVA_TOOLCHAIN<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $JAVA_HOME/bin<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_PRE_BUILD_PATHS<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $ANDROID_JAVA_TOOLCHAIN<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_PRODUCT_OUT<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $(get_abs_build_var<br /> PRODUCT_OUT)<br />
    </td>
  </tr>
  
  <tr>
    <td>
      OUT<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $ANDROID_PRODUCT_OUT<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ANDROID_HOST_OUT<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $(get_abs_build_var<br /> HOST_OUT)<br />
    </td>
  </tr>
  
  <tr>
    <td>
      OPROFILE_EVENTS_DIR<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      $T/external/oprofile/events<br />
    </td>
  </tr>
  
  <tr>
    <td>
      BUILD_ENV_SEQUENCE_NUMBER<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      export<br /> BUILD_ENV_SEQUENCE_NUMBER=10<br />
    </td>
  </tr>
  
  <tr>
    <td>
      PROMPT_COMMAND<br />
    </td>
    
    <td>
      export<br />
    </td>
    
    <td>
      命令提示符<br />
    </td>
  </tr>
  
  <tr>
    <td>
      CM_DEVICES_ONLY<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      true 表示只支持CM的设备，如果使用breakfast命令会将改变量设置为true<br />
    </td>
  </tr>
  
  <tr>
    <td>
      MODVERSION<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      $(get_build_var CM_VERSION)<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ZIPFILE<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      cm-$MODVERSION.zip<br />
    </td>
  </tr>
  
  <tr>
    <td>
      ZIPPATH<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      $OUT/$ZIPFILE<br />
    </td>
  </tr>
  
  <tr>
    <td>
      TOPFILE<br />
    </td>
    
    <td>
      函数<br />
    </td>
    
    <td>
      build/core/envsetup.mk<br />
    </td>
  </tr>
</table>

用户下一步将使用mka进行编译，会利用这前两步设置的变量和函数命令，虽然breakfast命令和lunch命令有利用到一些makefile检查选择的产品是否符合要求，但是makefile里的变量都引入到当前shell,仅仅用于检查产品是否符合要求而已。

我们现在了解到breakfast命令会从网上下载产品列表，而lunch命令会下载产品的最新配置，所以我们在使用breakfast命令或者lunch命令时，会觉得时间比较长，如果是本地产品，你可以注释那些检查的代码，这样会很快。