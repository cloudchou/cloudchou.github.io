---
id: 1005
title: Sequelize使用总结
date: 2018-11-09T23:47:56+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=1005
permalink: /web/post-1005.html
categories:
- web
tags:
- web
---

sequelize是nodejs开发环境中的orm框架，基于promise，支持mysql,postgres,sqlite,Microsoft SQL Server.

以下记录使用的一些心得体会:

## 为什么使用orm框架

在java中如果不使用orm框架，我们会提前定义很多bean类(也叫Model类)，然后编写sql查询语句从数据库中查询得到结果集，然后需要自己手动转换成bean类，而编写bean类和转换成bean类需要花费不少时间，而这些工作都是很琐碎，繁杂的，如果能自动生成则最好。Java也有orm框架，能够自动生成这些bean类，比如jooq.

使用sequlize的orm框架的理由:

1. 减少在数据库中定义表的繁杂工作，可在代码中定义表结构及关联关系

2. 可为Model类添加自定义方法，以及校验方法，防止不符合规则得数据

3. 自动优化sql语句，可防注入

4. 若表之间有关联关系，使用对象操作方法即可轻松创建，更新，查询关联的对象

5. 在nodejs中查询数据，无须手动转换为bean类，也无需转换为json再发给客户端

## 如何优雅地使用sequelize

1.  建议用Sequelize接管数据库表的创建工作
   
    在模型类中定义好字段，以及类型，然后使用sequelize的同步方法，将表的定义同步到数据库中，可自动在数据库中建立好表结构，并设置表之间的关系

    如果直接在数据库中定义表，然后使用sequelize-auto-import的方式将表结构转换成Model类也可行，但是不方便给Model类添加自定义方法，校验方法，以及表之间的关系，所以更推荐使用Sequelize接管数据库表的创建工作

2.  自动添加常用字段 

    表字段可自动添加create_time, update_time,deleted 等常用字段， 当然也可不用这些字段，但是大部分表其实都需要这些字段，可以减少大量重复工作

3.  设置表之间的关联关系用处大

    若设置了表之间的关联关系 可很方便地创建，查询，更新关联数据

    只要设置了belongTo, hasOne, hasMany, belongsToMany关系，那么源对象就可拥有get,set方法来取关联关系的目标对象

    比如:

    ```
    GiftOrder.belongsTo(PayOrder, {
      foreignKey: 'order_no',
      as : 'payOrder'
    })
    ```
    
    那么GiftOrder的实例就有了getPayOrder，setPayOrder方法，甚至在创建GiftOrder对象时可跟一个PayOrder对象，写到数据库时可同时写入，另外查询GiftOrder时可使用`eager loading`的技术同时将关联的PayOrder对象拿到，非常方便


## 参考资料

[sequelize官方文档](http://docs.sequelizejs.com/manual/tutorial/associations.html)

    

