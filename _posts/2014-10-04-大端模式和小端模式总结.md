---
id: 659
title: 大端模式和小端模式总结
date: 2014-10-04T13:39:21+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=659
permalink: /%e4%b8%aa%e4%ba%ba%e6%80%bb%e7%bb%93/post-659.html
views:
  - 3942
categories:
  - 个人总结
tags:
  - 什么是大端和小端
  - 大端模式
  - 大端模式和小端模式 优缺点
  - 小端模式
  - 常见字节序
  - 端模式
---
## <a href="http://www.cloudchou.com/tag/%e4%bb%80%e4%b9%88%e6%98%af%e5%a4%a7%e7%ab%af%e5%92%8c%e5%b0%8f%e7%ab%af" title="View all posts in 什么是大端和小端" target="_blank" class="tags">什么是大端和小端</a>

我们平常谈论一个数字时，这个数字会有高位和地位之分，写在前面的为高位，写在后面的为地位，比如0x1234，那么高位字节为0x12，地位字节为0x34，而数字在计算机里的存储有两种方式，大端和小端：

  * 1) 大端就是将高位字节排放在内存的低地址端，低位字节排放在内存的高地址端
  * 2) 小端就是将低位字节排放在内存的低地址端，高位字节排放在内存的高地址端

举一个例子，比如数字0x12 34 56 78在内存中的表示形式为：

  * ### 1)<a href="http://www.cloudchou.com/tag/%e5%a4%a7%e7%ab%af%e6%a8%a1%e5%bc%8f" title="View all posts in 大端模式" target="_blank" class="tags">大端模式</a>：
    
    低地址 &#8212;&#8212;&#8212;&#8212;&#8212;&#8211;> 高地址
    
    0x12 | 0x34 | 0x56 | 0x78

  * ### 2)<a href="http://www.cloudchou.com/tag/%e5%b0%8f%e7%ab%af%e6%a8%a1%e5%bc%8f" title="View all posts in 小端模式" target="_blank" class="tags">小端模式</a>：
    
    低地址 &#8212;&#8212;&#8212;&#8212;&#8212;&#8212;> 高地址
    
    0x78 | 0x56 | 0x34 | 0x12

再举2个例子：

16bit宽的数0x1234在Little-endian模式（以及Big-endian模式）CPU内存中的存放方式（假设从地址0x4000开始存放）为：

<table class="dataintable">
  <tr>
    <th>
      内存地址
    </th>
    
    <th>
      小<a href="http://www.cloudchou.com/tag/%e7%ab%af%e6%a8%a1%e5%bc%8f" title="View all posts in 端模式" target="_blank" class="tags">端模式</a>
    </th>
    
    <th>
      大端模式
    </th>
  </tr>
  
  <tr>
    <td>
      0x4000
    </td>
    
    <td>
      0x34
    </td>
    
    <td>
      0x12
    </td>
  </tr>
  
  <tr>
    <td>
      0x4001
    </td>
    
    <td>
      0x12
    </td>
    
    <td>
      0x34
    </td>
  </tr>
</table>

32bit宽的数0x12345678在Little-endian模式以及Big-endian模式）CPU内存中的存放方式（假设从地址0x4000开始存放）为：

<table class="dataintable">
  <tr>
    <th>
      内存地址
    </th>
    
    <th>
      小端模式
    </th>
    
    <th>
      大端模式
    </th>
  </tr>
  
  <tr>
    <td>
      0x4000
    </td>
    
    <td>
      0x78
    </td>
    
    <td>
      0x12
    </td>
  </tr>
  
  <tr>
    <td>
      0x4001
    </td>
    
    <td>
      0x56
    </td>
    
    <td>
      0x34
    </td>
  </tr>
  
  <tr>
    <td>
      0x4002
    </td>
    
    <td>
      0x34
    </td>
    
    <td>
      0x56
    </td>
  </tr>
  
  <tr>
    <td>
      0x4003
    </td>
    
    <td>
      0x12
    </td>
    
    <td>
      0x78
    </td>
  </tr>
</table>

如果把数字存在文件里，而将文件看作一个大数组的话，数组从0排到文件长度，也就是说排在前面的是低地址区，后面的是高地址区，而常见的书写方式是把高位字节写在前面，地位字节写在后面，也就是说高位字节放在低地址区，地位字节放在高地址区， 故此书写方式可以看作是大端模式。

## 大端模式和小端模式各自的优缺点：

  * 1) 小端模式: 提取一个，两个，四个或者更长字节数据的汇编指令以与其他所有格式相同的方式进行：首先在偏移地址为0的地方提取最低位的字节，因为地址偏移和字节数是一对一的关系，多重精度的数学函数就相对地容易写了。如果你增加数字的值，你可能在左边增加数字（高位非指数函数需要更多的数字）。 因此， 经常需要增加两位数字并移动存储器里所有Big-endian顺序的数字，把所有数向右移，这会增加计算机的工作量。不过，使用Little- Endian的存储器中不重要的字节(地位字节)可以存在它原来的位置，新的数可以存在它的右边的高位地址里。这就意味着计算机中的某些计算可以变得更加简单和快速。
  * 
2) 大端模式：符号位的判定固定为第一个字节，容易判断正负。首先提取高位字节，你总是可以由看看在偏移位置为0的字节来确定这个数字是 正数还是负数。你不必知道这个数值有多长，或者你也不必过一些字节来看这个数值是否含有符号位。 </ul> 

## 数组在大端小端情况下的存储

以unsigned int value = 0x12345678为例，分别看看在两种字节序下其存储情况，我们可以用unsigned char buf[4]来表示value：

Big-Endian: 低地址存放高位，如下：

高地址

&#8212;&#8212;&#8212;&#8212;&#8212;

buf\[3\] (0x78) &#8212; 低位

buf\[2\] (0x56)

buf\[1\] (0x34)

buf\[0\] (0x12) &#8212; 高位

&#8212;&#8212;&#8212;&#8212;&#8212;

低地址

Little-Endian: 低地址存放低位，如下：

高地址

&#8212;&#8212;&#8212;&#8212;&#8212;

buf\[3\] (0x12) &#8212; 高位

buf\[2\] (0x34)

buf\[1\] (0x56)

buf\[0\] (0x78) &#8212; 低位

&#8212;&#8212;&#8212;&#8212;&#8211;

低地址

## 为什么会有大小端模式之分呢？

这是因为在计算机系统中，我们是以字节为单位的，每个地址单元都对应着一个字节，一个字节为8bit。但是在C语言中除了8bit的char之外，还有16bit的short型，32bit的long型（要看具体的编译器），另外，对于位数大于8位的处理器，例如16位或者32位的处理器，由于寄存器宽度大于一个字节，那么必然存在着一个如果将多个字节安排的问题。因此就导致了大端存储模式和小端存储模式。例如一个16bit的short型x，在内存中的地址为0x0010，x的值为0x1122，那么0x11为高字节，0x22为低字节。对于大端模式，就将0x11放在低地址中，即0x0010中，0x22放在高地址中，即0x0011中。小端模式，刚好相反。我们常用的X86结构是小端模式，而KEIL C51则为大端模式。很多的ARM，DSP都为小端模式。有些ARM处理器还可以由硬件来选择是大端模式还是小端模式。

## 常见的字节序

一般操作系统都是小端，而通讯协议是大端的。

常见CPU的字节序

大端模式：PowerPC、IBM、Sun

小端模式：X86，DEC

ARM既可以工作在大端模式，也可以工作在小端模式

常见文件的字节序：

Adobe PS – Big Endian

BMP – Little Endian

GIF – Little Endian

JPEG – Big Endian

Unicode: windows文本文件存储为unicode格式，默认为小端模式

Unicode 大端模式文本文件: windows 文本文件也可以存储为unicode 大端模式格式。

unicode文本文件，不论是大端模式还是小端模式，存储的第一个字符都是BOM，占两个字节，BOM的unicode码是0xFEFF，存储在大端模式unicode文件里是0xFEFF，存储在小端模式unicode文件里是0xFFFE。

不同端模式的处理器进行数据传递时必须要考虑端模式的不同。如进行网络数据传递时，必须要考虑端模式的转换。在Socket接口编程中，以下几个函数用于大小端字节序的转换。

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
        <pre class="cpp" style="font-family:monospace;"><span style="color: #339900;">#define ntohs(n)     //16位数据类型网络字节顺序到主机字节顺序的转换</span>
<span style="color: #339900;">#define htons(n)     //16位数据类型主机字节顺序到网络字节顺序的转换</span>
<span style="color: #339900;">#define ntohl(n)      //32位数据类型网络字节顺序到主机字节顺序的转换</span>
<span style="color: #339900;">#define htonl(n)      //32位数据类型主机字节顺序到网络字节顺序的转换</span></pre>
      </td>
    </tr>
  </table>
</div>

其中互联网使用的网络字节顺序采用大端模式进行编址，而主机字节顺序根据处理器的不同而不同，如PowerPC处理器使用大端模式，而Pentuim处理器使用小端模式。

大端模式处理器的字节序到网络字节序不需要转换，此时ntohs(n)=n，ntohl = n；而小端模式处理器的字节序到网络字节必须要进行转换，此时ntohs(n) = \_\_swab16(n)，ntohl = \_\_swab32(n)。

PowerPC处理器主导网络市场，可以说绝大多数的通信设备都使用PowerPC处理器进行协议处理和其他控制信息的处理，这也可能也是在网络上的绝大多数协议都采用大端编址方式的原因。而Pentium主导个人机市场，因此多数用于个人机的外设都采用小端模式，包括一些在网络设备中使用的PCI总线，Flash等设备，这也要求在硬件设计中注意端模式的转换。因此在有关网络协议的软件设计中，使用小端方式的处理器需要在软件中处理端模式的转变。对于通信协议来说，IP地址尤其要注意这种转换，因为主机一般都是小端模式，而网络设备一般是大端模式，故此需要转换为网络设备用的字节序，这样网络设备才可以使用ip地址进行路由。

## 参考材料

详解大端模式和小端模式

 <a href="http://blog.csdn.net/ce123_zhouwei/article/details/6971544" target="_blank">http://blog.csdn.net/ce123_zhouwei/article/details/6971544 </a>

大端模式和小端模式

 <a href="http://blog.csdn.net/hackbuteer1/article/details/7722667" target="_blank">http://blog.csdn.net/hackbuteer1/article/details/7722667 </a>