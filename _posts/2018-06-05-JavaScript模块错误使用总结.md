---
id: 998
title: JavaScript模块错误使用总结
date: 2018-06-05T23:29:31+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=998
permalink: /web/post-998.html
published: false
categories:
- Web
tags:
- JavaScript模块
---

在使用 JavaScript 的模块化时遇到了不少问题，主要是 Webpack 项目加载第三方模块遇到的问题，本篇主要梳理总结自己曾经遇到的问题

## JavaScript 模块错误使用总结

### Webpack 项目如何引用 Weixin Sdk:weixin-js-sdk

在 Webpack 项目中，我们可以使用命令`npm install i weixin-js-sdk`安装 Weixin Sdk 模块。我们先分析 weixin-js-sdk 的源码，然后便可知如何在源代码中使用 es6 的模块化方案加载该模块。weixin-js-sdk 的 index.js 源码简化后如下所示:

```javascript
! function (e, n) {
    module.exports = n(e)
}(window, function (e, n) {
    //...
    if (!e.jWeixin) {
         // ....
        var E = !1,
            O = [],
            N = {
                config: function (e) {
                    //...
                },
                // ...
                miniProgram: {
                    navigateBack: function (e) {
                       //...
                    },
                    //...
                }
            },
            //...
        return /** ...*/ n && (e.wx = e.jWeixin = N), N
    }
});
```

上面的代码其实相当于如下代码:

```javascript
function Xxx(){
if (!window.jWeixin) {
         // ....
        var /*...*/
            N = {
                config: function (e) {
                    //...
                },
                // ...
                miniProgram: {
                    navigateBack: function (e) {
                       //...
                    },
                    //...
                }
            },
            //...
        window.wx = window.jWeixin = N
        return N
}
}
module.exports=Xxx()
```

从上面的代码我们可以知道weixin-js-sdk将WeixinSdk对象赋值给了window的jWexin属性，也赋值给了window的wx属性，同时它还将这个对象作为模块的导出对象

从上一篇[JavaScript模块机制学习总结](./2018-05-30-JavaScript模块机制学习总结)我们可知，如果我们想使用es6的语法引用该weixin-js-sdk导出的对象，只需像下面的代码一样:

```javascript
import WeixinSdk from 'weixin-js-sdk'
```

原因是如果我们使用es6模块规范的import default去引用CommonJS模块规范使用module.exports导出的对象时，经过babel对import指令的处理，这个default变量会被直接赋值为CommonJS模块规范使用module.exports导出的对象。这个转换代码大概如下所示:

```javascript
function _interopRequireDefault(obj) {
    return obj && obj.__esModule
        ? obj
        : { 'default': obj };
}

var _weixin-js-sdk = require('weixin-js-sdk');
//如果被导入的模块是es6模块，则该模块对象有属性__esModule，所以_interopRequireDefault会直接返回这个对象
//如果被导入的模块是CommonJS模块，则该模块对象没有属性__esModule，则会返回新对象{'default':obj}
var _weixin2 = _interopRequireDefault(weixin-js-sdk);  
var WeixinSdk = _weixin2['default']; 
```

从上面可知指令`import WeixinSdk from 'weixin-js-sdk'`中的WeixinSdk可以随意命名，都可以正常工作，和ES6规范import default指令是一致的，ES6规范中import default时变量名都可以随意命名

其实我们还有另一种方法引用该weixin-js-sdk导出的对象，只需象下面的代码一样:

```javascript
import * as WeixinJSSDK from 'weixin-js-sdk'
```

原因是如果我们使用es6模块规范的import *去引用CommonJS规范使用module.exports导出的对象时，经过babel对import指令的处理，这个as变量会被赋值为CommonJS模块规范使用module.exports导出的对象的所有属性组成的一个新对象，并且这个新对象还有一个default属性指向原来的对象，这个转换过程大概如下所示:

```javascript
function _interopRequireWildcard(obj) {
    if (obj && obj.__esModule) {
        return obj;
    }
    else {
        var newObj = {}; // (A)
        if (obj != null) {
            for (var key in obj) {
                if (Object.prototype.hasOwnProperty.call(obj, key))
                    newObj[key] = obj[key];
            }
        }
        newObj.default = obj;
        return newObj;
    }
}
```

从上述转换代码可知，这个as变量其实是一个新生成的对象，它有一个default属性指向CommonJS规范使用module.exports导出的对象，并且它还克隆了module.exports导出对象的所有属性，所以我们可以使用这个as变量引用module.exports导出对象的所有属性

**总结**

从上述分析可知，在ES6的代码中，我们有两种方式引用CommonJS规范使用module.exports导出的变量

1. 使用 import default 指令， 类似如此: `import WeixinSdk from weixin-js-sdk`

2. 使用 import * as 指令， 类似如此:  `import * as WeixinJSSDK from 'weixin-js-sdk'` 


### Webpack项目如何利用微信官方cdn分发的weixin-js-sdk

项目中如果利用微信官方cdn分发的weixin-js-sdk,可以加速weixin-js-sdk在客户端的加载速度，那么如何实现呢?

我们可以利用webpack的externals配置来实现上述需求

webpack的exgternals配置可以: 
> 防止将某些 import 的包(package)打包到 bundle 中，而是在运行时(runtime)再去从外部获取这些扩展依赖(external dependencies)

例如，从 CDN 引入 jQuery，而不是把它打包：

**index.html**

```javascript
<script
  src="https://code.jquery.com/jquery-3.1.0.js"
  integrity="sha256-slogkvB1K3VOkzAI8QITxV3VzpOnkeNVsKvtkYLMjfk="
  crossorigin="anonymous">
</script>
```
**webpack.config.js**

```javascript
module.exports = {
  /* ...*/
  externals: {
    jquery: 'jQuery'
  }
}
```

改成这样后，下面的代码还可以正常工作:

```javascript
import $ from 'jquery';
$('.my-element').animate(...);
```

这个externals配置工作的原理是: 

> 在解析import指令遇到from时，会看from所指的库，如果在externals配置里,比如这里的jquery在externals中有一个配置项jquery, 那么webpack在将import指令转化成require指令时会用配置项的值jQuery，也就是说import $ from 'jquery';经过webpack转化后，得到的javascript类似下面的代码:

类似于: 存在jquery文件:
```javascript
module.exports = jWeixin;
```

然后import的地方变成了:
```javascript
var $=require(jquery)
```

这就要求我们在index.html中引入的jQuery必须给window.jQuery赋值，否则无法正常工作

利用微信官方cdn分发的weixin-js-sdk,可以加速weixin-js-sdk在客户端的加载速度, 具体步骤如下所示:

1. 在项目根目录下的index.html中添加weixin-js-sdk的官方cdn链接，

```html
<!DOCTYPE html>
<html>
<head>
  <!-- ... -->
  <script src="//res.wx.qq.com/open/js/jweixin-1.3.2.js"></script>
</head>
<body>
  <div id="app"></div>
  <!-- built files will be auto injected -->
</body>
</html>
```

2. 修改webpack.base.conf.js的externals配置

```javascript
module.exports = {
  /* ...*/
  externals: {
    /*...*/  
    'weixin-js-sdk': 'jWeixin'
  }
}
```

因为加载`weixin-js-sdk`时，会为`window.jWeixin`赋值，所以externals配置中`weixin-js-sdk`配置项的值是`jWexin`，其实将jWeixin改成wx也是可以正常工作的，因为weixin-js-sdk也为window.wx赋了值


### webpack项目调试时import的变量不可evaluate

前端代码调试时 import的名字不可以直接用于evaluate 表达式

比如有代码:
import moment from 'moment'
let dateStr = moment(endTime).format('YYYY-MM-DD')
我们调试时，如果在上一句代码处打断点, 然后运行到此处时，如果evaluate表达式moment，会得到undefined的结果

![javascript_debug](/assets/blogimgs/javascript_debug.png)

但实际上上述代码可以正常执行

![javascript_normal_execute](/assets/blogimgs/javascript_normal_execute.png)

通过观察闭包的变量，moment对应的执行时的函数__WEBPACK_IMPORTED_MODULE_3_moment___default

所以下次遇到这样的问题时，不要再怀疑代码有问题了

## 参考资料

1. [webpack externals 深入理解](https://www.tangshuang.net/3343.html)