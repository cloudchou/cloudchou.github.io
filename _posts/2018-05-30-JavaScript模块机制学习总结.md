---
id: 997
title: JavaScript模块机制学习总结
date: 2018-05-30T23:44:29+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=997
permalink: /web/post-997.html
published: false
categories:
- web
tags:
- web
---

先前被JavaScript的模块机制弄得晕头转向，于是彻底研究了JS的模块机制，总结分享如下，希望对你有帮助。在下一篇文章再对我自己先前遇到的JS模块相关的问题进行梳理总结

# JavaScript模块化规范学习总结

## JavaScript模块化规范简单对比

|模块化规范|如何定义模块对外接口|如何引入其他模块|简介|
|------|-------------|-----------|------|
|CommonJS|`module.exports={//...}`|`var math = require('./math')`|Node.js采用CommonJS规范，主要用于服务器端编程|
|AMD|<code>define(['xxx'], function(x){<br> return {xxx2 : <br>function(){}};}<br>)</code>|<code>require(['xxx1', 'xxx2'],<br> function( xxx1, xxx2)<br> {//...}<br> );</code>|AMD规范采用异步方式加载模块，主要用于浏览器端，require.js是该规范的实现者，因此网页中必须引用require.js才可正常工作|
|CMD|<code>define(function(require, exports, module)<br>{<br>exports.add=function(){}<br> );</code>|<code>define(function(require, exports, module)<br>{<br>var a = require('./a'); <br>if(false)<br>{<br>var b = require('./b');<br>}<br>}<br>);</code>|CMD规范也采用异步方式加载模块，主要用于浏览器端，sea.js是该规范的实现者，页面中必须引用sea.js才可正常工作,CMD规范比AMD规范更先进|
|ES6|`export { basicNum, add };`|`import { basicNum, add } from './math'`|ES6在语言标准的层面上实现了模块功能，而其它规范都是靠第三方库，export规定模块对外的接口,import用于输入其他模块提供的功能|

### AMD VS CMD

AMD规范和CMD规范都是浏览器端的异步加载规范，不同点在于:

|规范|区别|
|---|----|
|AMD|1.AMD 推崇依赖前置，提前执行，也就是说在声明时就会初始化使用到的所有模块|
|CMD|1.CMD 推崇依赖就近，延迟执行，也就是说在运行时只有逻辑成立的加载模块的指令才会执行|
|AMD|2.AMD使用返回的对象来定义模块对外输出的变量|
|CMD|2.CMD使用define参数函数的export变量定义模块对外输出的变量|
|AMD|3.AMD使用define的第1个参数来加载依赖的模块|
|CMD|3.CMD使用require来加载依赖的模块|


```javascript
/** AMD写法 **/ 
/** define函数的第一个参数所指的依赖模块在define执行时就会加载     不会管第2个函数中是否会真正用到这个模块，都会初始化**/
define(["a", "b", "c", "d", "e", "f"], function(a, b, c, d, e, f) { 
     // 等于在最前面声明并初始化了要用到的所有模块
    a.doSomething();
    if (false) {
        // 即便没用到某个模块 b，但 b 还是提前执行了
        b.doSomething()
    } 
});

/** CMD写法 **/
define(function(require, exports, module) {
    var a = require('./a'); //在需要时申明 a模块会被加载
    a.doSomething();
    if (false) {
        var b = require('./b'); // b模块不会被加载，因为不会执行
        b.doSomething();
    }
});


/** CMD 中 使用 sea.js 定义当前模块对外接口**/
// 定义模块 math.js
define(function(require, exports, module) {
    var $ = require('jquery.js');
    var add = function(a,b){
        return a+b;
    }
    exports.add = add; // 使用 exports定义模块对外接口
});
// 加载模块
seajs.use(['math.js'], function(math){
    var sum = math.add(1+2);
});

```

### CommonJS VS ES6

1.  CommonJS 模块输出的是一个值的拷贝，ES6模块输出的是值的引用

    *  CommonJS 模块输出的是值的拷贝，也就是说，一旦输出一个值，模块内部的变化就影响不到这个值

    *  而在ES6中， JS引擎对脚本静态分析的时候，遇到模块加载命令import，只会生成一个只读引用。等到脚本真正执行时，再根据这个只读引用，到被加载的那个模块里面去取值

2.  CommonJS 模块是运行时加载， ES6模块是编译时输出接口

    *  运行时加载: CommonJS 模块就是对象；即在输入时是先加载整个模块，生成一个对象，然后再从这个对象上面读取方法，这种加载称为“运行时加载”

    *  编译时加载: ES6 模块不是对象，而是通过 export 命令显式指定输出的代码，import时采用静态命令的形式。即在import时可以指定加载某个输出值，而不是加载整个模块，这种加载称为“编译时加载” 

    *  CommonJS 加载的是一个对象（即module.exports属性），该对象只有在脚本运行完才会生成。而 ES6 模块不是对象，它的对外接口只是一种静态定义，在代码静态解析阶段就会生成 

3.  ES6规范可在浏览器端使用，也可已在服务器端使用

    *  新版本的Node.js已支持ES6规范，因为ES6是将来的趋势，所以新项目可直接采用ES6规范，而放弃CommonJS
    
    *  浏览器端有很多老浏览器不支持ES6规范，因此需要预编译器babel，将ES6规范的代码转成ES5的代码，编译后的代码就可以在浏览器端使用了

## Webpack采用的模块规范

Webpack的配置文件采用CommonJS规范，但是Webpack项目的源代码可采用AMD, CMD, CommonJS, es6等几乎所有规范，因为webpack本身维护了一套模块系统

现实中有大量的老项目采用的是CommonJS规范，而我们的项目一般会使用ES6规范，有时ES6规范的模块需要引用CommonJS规范的模块

若使用Webpack打包工具，我们就可以在代码中使用ES6规范的import去加载CommonJS规范的模块

实际上Webpack在构建时，会将ES6,AMD,CMD,CommonJS等规范的模块化方案都转成它自己的模块化方案，达到统一，所以我们使用ES6规范的import可以加载CommonJS规范的模块

实际上使用Webpack构建的npm第3方公共组件，比如element-ui，会将webpack的配置属性output.libraryTarget设置为commonjs2，导出的组件的js最后都会赋值给module.exports，所以我们可以使用import的方式去使用第3方组件

通常我们使用webpack时还会使用babel，babel专门用于将es6转换成es5，babel将es6转换成es5语法时，同时也会将es6的模块化语法，转化成es5的模块化语法，babel的转换方式和weppack思路是差不多的，不过babel会将es6的import,export等关键字转换成commonjs的require,module.exports等关键字。

在构建流程中babel将es6转为es5的步骤在webpack的模块化方案转换之前，所以babel预先已经将import,export等关键字变成了commonjs的require,module.exports等关键字，然后webpack的模块化方案转化工作时，只需将require关键字修改成webpack运行时定义的_webpack_require__就可以了

### babel如何将es6的模块语法转换为CommonJS

#### 导出模块的转换

babel 转换 es6 的模块输出逻辑非常简单，即将所有输出都赋值给 exports，并带上一个标志 __esModule 表明这是个由 es6 转换来的 commonjs 输出

es6的导出模块的写法有

```javascript
export default 123;
export const a = 123;
const b = 3;
const c = 4;
export { b, c };
```
babel 会将这些统统转换成 commonjs 的 exports

```javascript
exports.default = 123;
exports.a = 123;
exports.b = 3;
exports.c = 4;
exports.__esModule = true;
```

#### 导入模块的转换
babel 也会将引入 import 也转换为 commonjs 规范。即采用 require 去引用模块，再加以一定的处理，符合es6的使用意图

##### 引入default

```javascript
import a from './a.js';
```

在es6中 import a from './a.js' 的本意是想去引入一个 es6 a模块中的 default 输出。

如果上述语句转换成`var a = require(./a.js)`，得到的会是整个对象，也就是说exports这整个对象，而不是exports.default对象，所以需要添加一些新逻辑

> CommonJS中exports和module.exports是等价的

我们在导出提到，es6的default输出会赋值给导出对象的default属性，也就是说exports.default属性, 为了能让import的转换可引用这个exports.default属性，babel添加了一个help函数_interopRequireDefault函数，转换的逻辑如下所示:

```javascript
function _interopRequireDefault(obj) {
    return obj && obj.__esModule
        ? obj
        : { 'default': obj };
}

var _a = require('a.js');
//如果被导入的模块是es6模块，则该模块对象有属性__esModule，所以_interopRequireDefault会直接返回这个对象
//如果被导入的模块是CommonJS模块，则该模块对象没有属性__esModule，则会返回新对象{'default':obj}
var _a2 = _interopRequireDefault(_a);  
var a = _a2['default']; 
```

如果被导入的模块是es6模块，`import a from './a.js';`得到的会是a.js模块的default输出
如果被导入的模块是CommonJs模块，`import a from './a.js';`得到的会直接是该模块对象，和CommonJS的`var a=require('./a.js')`是等价的

##### 引入 * 通配符

```javascript
import * as a from './a.js'
```

上述语句的本意是想将es6模块的所有命名输出以及default输出打包成一个对象赋值给a变量

假设导出变量的es6模块经过babel转换后得到如下代码:

```javascript
exports.default = 123;
exports.a = 123;
exports.b = 3;
exports.__esModule = true;
```

那么`import * as a from './a.js'`， 如果转换成 `var a = require('./a.js')`，则已符合意图

假设导出变量的模块是CommonJS模块，导出时不会有default属性，因此还需要添加一个default属性,这个default属性的值就是整个模块对象，这个转换逻辑如下所示:

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

通过这种转换，使用*导入模块，比如:`import * as a from './a.js'`，如果a.js是es6模块，那么a变量不一定有default属性，而如果a.js是CommonJS模块，则a就会有default属性

##### import { a } from './a.js'

直接转换成 require('./a.js').a 即可。


## 自己使用es6的模块化经常犯的错

最容易误解import指令:

```javascript
//以前的理解:    相当于CommonJS的 var a = require './a.js'
//             或者等价于es6的 import * as a from './a.js'
//有时还误解为:  等价于 import {a} from './a.js'
//实际上:       这里只import default输出, 和 import * as a from './a.js' 相差特别大
//             虽然a.js中的输出的default变量未必叫a，有可能叫b，但这里可随意命名为a,或者b，或者c都可以
//             import a from './a.js' 和 import {a} from './a.js'差别很大
import a from './a.js'

// 引入a模块中的导出变量b, a.js中必须导出一个变量名为b的变量
import {b} from './a.js'

// 引入a模块的所有导出变量  等价的CommonJS代码: var a = require './a.js' 
import * as a from './a.js'

// 下面的指令也是合法的 这样a1是a中的default输出 而是a模块的有输出变量组成的对象
import a1, * as a from './a.js'

// 下面的指令也是合法的， 这样b是a中的单个导出变量， 而a是所有导出变量组成的对象
import {b}, * as a from './a.js'

```

## 总结

JavaScript的模块化规范发展经历了多个阶段，从服务端的CommonJS规范，然后再到浏览器端依赖第3方库实现的AMD规范,CMD规范，再到在语言层面就直接支持的ES6模块化规范，越来越完善，使用也越来越方便

为了兼容旧的规范，Webpack, babel有模块化转换机制将ES6,AMD,CMD等规范的模块化方案转换成CommonJS的模块化方案，然后CommonJS用它自己运行时支持的_webpack_require__来替换CommonJS的require，这样在浏览器端也可以使用原来在服务端才能使用的模块化机制了，得益于此，我们才能构建大型复杂的前端应用

babel转换es6的export指令是非常简单的，但是在转换import指令却非常复杂，共有3种场景，每种场景都需要考虑import的模块如果是commonjs，应该如何处理，这3种场景分别是:

1. import default

2. import * as a from './a.js'

3. import { a } from './b.js' 

其中第3种情况最简单，第1种场景最复杂，先前在import default时，理解有很多错误，或者和第2种场景等价，或者和第3种场景等价，实际上它非常特殊，它不管export的变量的名字的，相当于重命名了

## 参考资料

[「前端」import、require、export、module.exports 混合详解](https://github.com/ShowJoy-com/showjoy-blog/issues/39)

[前端模块化：CommonJS,AMD,CMD,ES6](https://juejin.im/post/5aaa37c8f265da23945f365c)



