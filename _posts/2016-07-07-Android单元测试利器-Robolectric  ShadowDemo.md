---
id: 947
title: 'Android单元测试利器&#8211;Robolectric  ShadowDemo'
date: 2016-07-07T09:25:13+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=947
permalink: /android/post-947.html
views:
  - 521
categories:
  - Android
  - 个人总结
tags:
  - Android单元测试
  - Robolectric
  - Robolectric Shadow
---
<p>Android单元测试系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> </p>

<h2>Shadow测试Demo</h2>
<p>其实Robolectric对Android API的支持都是通过为各个API类建立Shadow类实现支持的，比如SystemProperties类，在Robolectric框架中有一个对应的ShadowSystemProperties，在Shadow类中只需要实现想mock的方法即可，不需要实现原始类的所有方法，这样当调用Android API类的方法时，实际上是调用Shadow类中的方法，所以通过这种方式实现了对Android系统API的mock。我们来看一下ShadowSystemProperties的实现:</p>
```java
/**
 * Shadow for {@link android.os.SystemProperties}.
 */
//下述注解表明是针对SystemProperties类的Shadow类，isInAndroidSdk表示原始类是否是在Android Sdk中暴露的,
//因为SystemProperities类实际上是一个隐藏类，所以这里isInAndroidSdk=false
@Implements(value = SystemProperties.class, isInAndroidSdk = false)
public class ShadowSystemProperties {
  private static final Map<String, Object> VALUES = new HashMap<>();
  private static final Set<String> alreadyWarned = new HashSet<>();

  static {
    VALUES.put("ro.build.version.release", "2.2");
    VALUES.put("ro.build.version.incremental", "0");
    VALUES.put("ro.build.version.sdk", 8);
    VALUES.put("ro.build.date.utc", 1277708400000L);  // Jun 28, 2010
    VALUES.put("ro.debuggable", 0);
    VALUES.put("ro.secure", 1);
    VALUES.put("ro.product.cpu.abilist", "armeabi-v7a");
    VALUES.put("ro.product.cpu.abilist32", "armeabi-v7a,armeabi");
    VALUES.put("ro.product.cpu.abilist64", "armeabi-v7a,armeabi");
    VALUES.put("ro.build.fingerprint", "robolectric");
    VALUES.put("ro.build.version.all_codenames", "REL");
    VALUES.put("log.closeguard.Animation", false);
    // disable vsync for Choreographer
    VALUES.put("debug.choreographer.vsync", false); 
  }

  /** 实现对get方法的mock
  */
  @Implementation
  public static String get(String key) {
    Object o = VALUES.get(key);
    if (o == null) {
      warnUnknown(key);
      return "";
    }
    return o.toString();
  }

  @Implementation
  public static String get(String key, String def) {
    Object value = VALUES.get(key);
    return value == null ? def : value.toString();
  }

  /** 实现对getInt方法的mock
  */
  @Implementation
  public static int getInt(String key, int def) {
    Object value = VALUES.get(key);
    return value == null ? def : (Integer) value;
  }

  /** 实现对getLong方法的mock
  */
  @Implementation
  public static long getLong(String key, long def) {
    Object value = VALUES.get(key);
    return value == null ? def : (Long) value;
  }

  /** 实现对getBoolean方法的mock
  */
  @Implementation
  public static boolean getBoolean(String key, boolean def) {
    Object value = VALUES.get(key);
    return value == null ? def : (Boolean) value;
  }

  synchronized private static void warnUnknown(String key) {
    if (alreadyWarned.add(key)) {
      System.err.println("WARNING: no system properties value for " + key);
    }
  }
}
```
<p>原始的SystemProperties类本来是从系统的属性服务里读取属性，Robolectric为了实现mock，将事先定义好的部分属性直接hardcode在代码里，应用获取系统属性时会调用到ShadowSystemProperties类的get方法，这时候就可以直接从内存里取值并返回给应用了。我们知道android.os.Build类的很多字段的值其实都是通过SystemProperties类的get方法获得的，比如Build.brand对应的属性key是ro.product.brand，而Build.MODEL对应的属性key是ro.product.model，但是在上述ShadowSystemProperties里并没有这些属性设置值，所以当我们读取Build.brand或者Build.model时得到的值都是unknown.</p>
<p>但是我们可以利用Roblectric创建自己的针对系统Api类的mock类，比如我们也创建一个CloudSystemProperties类，实现如下所示:</p>
```java
@Implements(value = SystemProperties.class, isInAndroidSdk = false)
public class CloudSystemProperties {
    private static final Map<String, Object> VALUES = new HashMap<>();
    private static final Set<String> alreadyWarned = new HashSet<>();

    static {
        VALUES.put("ro.build.version.release", "2.2");
        VALUES.put("ro.build.version.incremental", "0");
        VALUES.put("ro.build.version.sdk", 8);
        VALUES.put("ro.build.date.utc", 1277708400000L);  // Jun 28, 2010
        VALUES.put("ro.debuggable", 0);
        VALUES.put("ro.secure", 1);
        VALUES.put("ro.product.cpu.abilist", "armeabi-v7a");
        VALUES.put("ro.product.cpu.abilist32", "armeabi-v7a,armeabi");
        VALUES.put("ro.product.cpu.abilist64", "armeabi-v7a,armeabi");
        VALUES.put("ro.build.fingerprint", "robolectric");
        VALUES.put("ro.build.version.all_codenames", "REL");
        VALUES.put("log.closeguard.Animation", false);
        // disable vsync for Choreographer 
        VALUES.put("debug.choreographer.vsync", false); 
        //添加了如下属性
        VALUES.put("persist.radio.multisim.config", "DSDS"); 
        VALUES.put("ro.product.device", "GT-I9100G");
        VALUES.put("ro.product.board", "t1");
        VALUES.put("ro.build.product", "GT-I9100G");
        VALUES.put("ro.product.brand", "samsung");
        VALUES.put("ro.product.model", "GT-I9100G");
        VALUES.put("ro.build.fingerprint", 
        "samsung/GT-I9100G/GT-I9100G:4.1.2/JZO54K/I9100GXXLSR:user/release-keys");
    }

    @Implementation
    public static String get(String key) {
        Object o = VALUES.get(key);
        if (o == null) {
            warnUnknown(key);
            return "";
        }
        return o.toString();
    }

    @Implementation
    public static String get(String key, String def) {
        Object value = VALUES.get(key);
        return value == null ? def : value.toString();
    }

    @Implementation
    public static int getInt(String key, int def) {
        Object value = VALUES.get(key);
        return value == null ? def : (Integer) value;
    }

    @Implementation
    public static long getLong(String key, long def) {
        Object value = VALUES.get(key);
        return value == null ? def : (Long) value;
    }

    @Implementation
    public static boolean getBoolean(String key, boolean def) {
        Object value = VALUES.get(key);
        return value == null ? def : (Boolean) value;
    }

    synchronized private static void warnUnknown(String key) {
        if (alreadyWarned.add(key)) {
            System.err.println("WARNING: no system properties value for " + key);
        }
    }
}
```
<p>这样我们就可以获取Build.brand和Build.model的值了，在编写测试的时候指定Shadow类即可测试了:</p>
```java
@RunWith(RobolectricGradleTestRunner.class)
@Config(constants = BuildConfig.class, sdk = 21)
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"})
public class ShadowTest {

  //指定使用Roblectric框架的ShadowSystemProperties来对SystemProperties类mock
    @Config(shadows = {ShadowSystemProperties.class})
    @Test
    public void testEvn() throws IllegalAccessException, NoSuchFieldException {
        System.out.println(Build.VERSION.RELEASE);
        Context ctx = RuntimeEnvironment.application;
        System.out.println(Build.VERSION.SDK_INT);
        System.out.println(Build.DEVICE);
        System.out.println(Build.FINGERPRINT);
        System.out.println(Build.BRAND);
        System.out.println(Build.BOARD);
        System.out.println(Build.MODEL); 
    }

   //指定使用Roblectric框架的CloudSystemProperties来对SystemProperties类mock
    @Config(shadows = {CloudSystemProperties.class})
    @Test
    public void testEvn2() throws IllegalAccessException, NoSuchFieldException {
        System.out.println(Build.VERSION.RELEASE);
        Context ctx = RuntimeEnvironment.application;
        System.out.println(Build.VERSION.SDK_INT);
        System.out.println(Build.DEVICE);
        System.out.println(Build.FINGERPRINT);
        System.out.println(Build.BRAND);
        System.out.println(Build.BOARD);
        System.out.println(Build.MODEL); 
    }

}
```
<p>testEvn执行的测试结果如下所示:</p>
<p> <a href="http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp1.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp1.png" alt="ShadowSysProp1" width="1008" height="313" class="aligncenter size-full wp-image-940" /></a></p>
<p>testEvn2执行的测试结果如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/ShadowSysProp2-1024x261.png" alt="ShadowSysProp2" width="1024" height="261" class="aligncenter size-large wp-image-941" /></a></p>
<p>可以看出来CloudSystemProperties对SystemProperties类的mock是有效的.</p>
<h2>加载代码中的资源文件Demo</h2>
<p>我们还可以将某个机型的system/build.prop文件作为资源保存在代码里，然后实现SystemProperties的mock时，直接从该该资源文件里读取更加方便，这样可以实现对某个机型的属性的模拟。</p>
<p>测试代码如下所示,CloudSystemProperties2实现另一个对SystemProperites的Shadow</p>
```java
@Implements(value = SystemProperties.class, isInAndroidSdk = false)
public class CloudSystemProperties2 {

    @Implementation
    public static String get(String key) {
        Properties prop = new Properties();
        String name = "i9100g.properties";
        InputStream is = CloudSystemProperties2.class.getClassLoader().getResourceAsStream(name);
        try {
            prop.load(is);
            return prop.getProperty(key);
        } catch (IOException e) {
            return null;
        } finally {
            try {
                is.close();
            } catch (IOException e) {
            }
        }
    }

    @Implementation
    public static String get(String key, String def) {
        Object value = get(key);
        return value == null ? def : value.toString();
    }

    @Implementation
    public static int getInt(String key, int def) {
        String value = get(key);
        return value == null ? def : Integer.parseInt(value);
    }

    @Implementation
    public static long getLong(String key, long def) {
        String value = get(key);
        return value == null ? def : (Long) Long.parseLong(value);
    }

    @Implementation
    public static boolean getBoolean(String key, boolean def) {
        String value = get(key);
        return value == null ? def : Boolean.parseBoolean(value);
    }

}
```
<p>i9100g.properties内容如下所示:</p>
```java
ro.build.version.release=2.2
ro.build.version.incremental=0
ro.build.version.sdk=8
ro.build.date.utc=1277708400000
ro.debuggable=0
ro.secure=1
ro.product.cpu.abilist=armeabi-v7a
ro.product.cpu.abilist32=armeabi-v7a,armeabi
ro.product.cpu.abilist64=armeabi-v7a,armeabi
ro.build.fingerprint=robolectric
ro.build.version.all_codenames=REL
log.closeguard.Animation=false
debug.choreographer.vsync=false
debug.choreographer.vsync=false
persist.radio.multisim.config=DSDS
ro.product.device=GT-I9100G
ro.product.board=t1
ro.build.product=GT-I9100G
ro.product.brand=samsung
ro.product.model=GT-I9100G
ro.build.fingerprint=samsung/GT-I9100G/GT-I9100G:4.1.2/JZO54K/I9100GXXLSR:user/release-keys
```
<p>测试用例代码:</p>
```java
**
 * Created by Cloud on 2016/6/27.
 */
@RunWith(RobolectricGradleTestRunner.class)
@Config(constants = BuildConfig.class, sdk = 21)
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"})
public class ShadowTest {
    // ...
    @Config(shadows = {CloudSystemProperties2.class})
    @Test
    public void testShadow2() throws IllegalAccessException, NoSuchFieldException {
        System.out.println(Build.VERSION.RELEASE);
        System.out.println(Build.VERSION.SDK_INT);
        System.out.println(Build.DEVICE);
        System.out.println(Build.FINGERPRINT);
        System.out.println(Build.BRAND);
        System.out.println(Build.BOARD);
        System.out.println(Build.MODEL);
    }

}
```
<p>如果仅仅是这样做，是不够的，在AndroidStudio中执行这个单元测试，会在运行getClassLoader().getResourceAsStream(name)时因为找不到资源而抛出NullPointerException，如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/resource-exceptions-1024x345.png" alt="resource-exceptions" width="1024" height="345" class="aligncenter size-large wp-image-938" /></a></p>
<p>出现该问题的根本原因是getResourceAsStream函数在查找资源时，默认是在编译生成的类所在的文件夹里进行查找，而不是在源代码文件所在的文件夹查找，所以我们需要将i9100g.prop文件默认就拷贝到CloudSystemProperties生成的类文件所在的目录中，因此我们需要修改build.gradle，让它在执行测试前就将i9100g自动拷贝到它需要在的位置。 修改后的build.gradle如下所示:</p>
```groovy
android{
  //...
  testOptions {
        unitTests.all {
            beforeTest {
                def testClassDir = buildDir.getAbsolutePath() + "/intermediates/classes/test/debug"
                copy {
                    from(android.sourceSets.test.java.srcDirs) {
                        exclude "**/*.java"
                    }
                    into(testClassDir)
                }
            }
        }
    }	
  //...
}
```
<p>在代码文件里直接执行testShadow2之前，需先通过gralde执行testDebugUnitTest目标，否则也不会自动拷贝i9100g.prop文件到它需要的位置，执行这个命令之后就可以在代码中直接运行testShadow2测试了，通过gralde执行testDebugUnitTest目标可在命令行下执行如下命令:</p>
```java
gradlew.bat :app:testDebugUnitTest
```
<p>执行结果如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/resource_load_result-1024x270.png" alt="resource_load_result" width="1024" height="270" class="aligncenter size-large wp-image-937" /></a></p>

