---
id: 952
title: 'Android单元测试利器&#8211;Robolectric asset资源加载demo'
date: 2016-07-11T09:32:41+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=952
permalink: /android/post-952.html
views:
  - 507
categories:
  - Android
  - 个人总结
tags:
  - Android单元测试
  - Robolectric
  - Robolectric asset资源加载
---
<p>Android单元测试系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> </p>
<h2>Android asset资源加载demo</h2>
<p>先前有提到，本地单元测试里可以配置AndroidManifest, assests等目录，然而并没有什么卵用，读取的AndroidManifest还是主模块的AndroidManifest和assets，要想使用特殊的assets或者AndroidManifest必须自己写TestRunner,本节就讲解如何加载自定义的AndroidManifest和assets资源。</p>
<p>首先实现一个自定义的从RobolectricGradleTestRunner集成的TestRunner:</p>
```java
//可以修改AndroidManifest和asset的TestRunner
public class RobolectricGradleTestRunner2 extends RobolectricGradleTestRunner {

    public RobolectricGradleTestRunner2(Class<?> klass) throws InitializationError {
        super(klass);
    }

    @Override
    protected AndroidManifest getAppManifest(final Config config) {
        //使用父类的方法创建AndroidManifest对象,
        //因为我们只修改AndroidManifest对象的AndroidManifest文件的位置
        // 和assets文件夹的位置
        AndroidManifest appManifest = super.getAppManifest(config);
        //只有当我们在测试脚本里设置了manifest时，自定义TestRunner才处理
        if (config.manifest() != null && !"".equals(config.manifest())) {
            //使用反射修改AndroidManifest对象的androidManifestFile字段的值，
            //使其指向我们设置的AndroidManifest文件的位置
            FileFsFile manifestFile = FileFsFile.from(config.manifest());
            Class<? extends AndroidManifest> appManifestClass = null;
            try {
                appManifestClass = appManifest.getClass();
                Field androidManifestFileField;
                try {
                    androidManifestFileField = appManifestClass.getDeclaredField("androidManifestFile");
                } catch (NoSuchFieldException e) {
                    androidManifestFileField = appManifestClass.getSuperclass().getDeclaredField("androidManifestFile");
                }
                androidManifestFileField.setAccessible(true);
                androidManifestFileField.set(appManifest, manifestFile);
            } catch (NoSuchFieldException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
            //使用反射修改AndroidManifest对象的assetsDirectory字段的值，
            //使其指向我们设置的assets文件夹的位置
            String parent = new File(config.manifest()).getParent();
            FileFsFile assetFile = FileFsFile.from(parent, config.assetDir());
            try {
                Field assetsDirectoryField = appManifestClass.getDeclaredField("assetsDirectory");
                assetsDirectoryField.setAccessible(true);
                assetsDirectoryField.set(appManifest, assetFile);
            } catch (NoSuchFieldException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        }
        return appManifest;
    }

}
```
<p>然后再看如何在测试脚本里设置manifest进行测试:</p>
```java
//必须指定使用自定义的TestRunner才能指定AndroidManifest文件的位置进行加载
@RunWith(RobolectricGradleTestRunner2.class)
@Config(constants = BuildConfig.class, sdk = 21)
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"})
public class ManifestConfigTest {

    //指定使用test目录下的AndroidManifest.xml 这时asse
    @Test
    @Config(manifest = "src/test/AndroidManifest.xml")
    public void testManifestConfig() throws PackageManager.NameNotFoundException, IOException {
        String packageName = RuntimeEnvironment.application.getPackageName();
        PackageManager packageManager = RuntimeEnvironment.application.getPackageManager();
        PackageInfo packageInfo = packageManager.getPackageInfo(packageName, PackageManager.GET_ACTIVITIES);
        System.out.println(packageInfo.activities);
        System.out.println(packageName);
        System.out.println(packageInfo.versionCode);
        System.out.println(packageInfo.versionName);
        //从assets目录下加载test.prop文件
        InputStream fileInputStream = RuntimeEnvironment.application.getAssets().open("test.prop");
        Properties props = new Properties();
        props.load(fileInputStream);
        String property = props.getProperty("ro.product.cpu.abilist");
        System.out.println(property);
    }
}
```
<p>代码结构如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test.png" alt="manifest_test" width="695" height="350" class="aligncenter size-full wp-image-934" /></a></p>
<p>执行结果如下所示:</p>
<p><a href="http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test_result.png"><img src="http://www.cloudchou.com/wp-content/uploads/2016/07/manifest_test_result.png" alt="manifest_test_result" width="975" height="328" class="aligncenter size-full wp-image-935" /></a></p>