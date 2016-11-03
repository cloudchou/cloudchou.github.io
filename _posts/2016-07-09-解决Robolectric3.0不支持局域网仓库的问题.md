---
id: 978
title: 解决Robolectric3.0不支持局域网仓库的问题
date: 2016-07-09T17:28:36+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=978
permalink: /android/post-978.html
views:
  - 348
categories:
  - Android
  - 个人总结
tags:
  - Robolectric
  - Robolectric 3.0
  - robolectric.dependency.repo.url
  - Robolectric3.0 not support local net
---
<p>Robolectric官网在介绍它的配置时，指出可以在build.gradle里配置robolectric的依赖仓库，也就是说在脚本里可以声明Robolectric相关jar包的下载地址，比如android-all-5.0.0_r2-robolectric-1.jar，利用这个特性，我们可以将下载地址设置为局域网的组件仓库，这样可以缓存这些jar包，否则如果每次都从sonatype仓库下的话会非常慢。</p>

<p>设置的脚本如下所示:</p>
```groovy
android {
  testOptions {
    unitTests.all {
      systemProperty 'robolectric.dependency.repo.url', 'https://local-mirror/repo'
      systemProperty 'robolectric.dependency.repo.id', 'local'
    }
  }
}
```
<p>但实际上如果依赖robolectric3.0， 上面的依赖是无效的，如果我们使用./gradlew -d test命令执行测试，可以发现还是会从sonatype仓库下载，并且会非常慢。如果搜索robolectric 3.0的源码会发现根本找不到"robolectric.dependency.repo.url"字符串。 </p>
<p>我们需要对RobolectricGradleTestRunner进行定制才可解决这个问题，代码如下所示:</p>
```java
public class BaseRobolectricGradleTestRunner extends RobolectricGradleTestRunner {

    public BaseRobolectricGradleTestRunner(Class<?> klass) throws InitializationError {
        super(klass);
    }

    //覆盖该方法 可以定制DependencyResolver
    @Override
    protected DependencyResolver getJarResolver() {
        String repoUrl = System.getProperty("robolectric.dependency.repo.url", ".");
        String repoId = System.getProperty("robolectric.dependency.repo.id", ".");
        if (StringUtils.isNotEmpty(repoUrl) && StringUtils.isNotEmpty(repoId)) {
            File cacheDir = new File(new File(System.getProperty("java.io.tmpdir")), "robolectric");
            cacheDir.mkdir();
            DependencyResolver dependencyResolver;
            //如果设置了robolectric.dependency.repo.url属性，则利用LocalNetDependencyResolver来解决依赖
            //这样便可以调整仓库地址
            if (cacheDir.exists()) {
                Logger.info("Dependency cache location: %s", cacheDir.getAbsolutePath());
                dependencyResolver = new CachedDependencyResolver(
                new LocalNetDependencyResolver(repoUrl, repoId), cacheDir, 60 * 60 * 24 * 1000
                );
            } else {
                dependencyResolver = new LocalNetDependencyResolver(repoUrl, repoId);
            }
            return dependencyResolver;
        } else {
            return super.getJarResolver();
        }
    }

    private static class LocalNetDependencyResolver implements DependencyResolver {
        private String mRepoUrl;
        private String mRepoId;
        private final Project project = new Project();

        public LocalNetDependencyResolver(String repoUrl, String repoId) {
            mRepoId = repoId;
            mRepoUrl = repoUrl;
        }

        @Override
        public URL[] getLocalArtifactUrls(DependencyJar... dependencies) {
            DependenciesTask dependenciesTask = new DependenciesTask();
            configureMaven(dependenciesTask);
            RemoteRepository sonatypeRepository = new RemoteRepository();
            sonatypeRepository.setUrl(mRepoUrl);
            sonatypeRepository.setId(mRepoId);
            dependenciesTask.addConfiguredRemoteRepository(sonatypeRepository);
            dependenciesTask.setProject(project);
            for (DependencyJar dependencyJar : dependencies) {
                Dependency dependency = new Dependency();
                dependency.setArtifactId(dependencyJar.getArtifactId());
                dependency.setGroupId(dependencyJar.getGroupId());
                dependency.setType(dependencyJar.getType());
                dependency.setVersion(dependencyJar.getVersion());
                if (dependencyJar.getClassifier() != null) {
                    dependency.setClassifier(dependencyJar.getClassifier());
                }
                dependenciesTask.addDependency(dependency);
            }
            dependenciesTask.execute();

            @SuppressWarnings("unchecked")
            Hashtable<String, String> artifacts = project.getProperties();
            URL[] urls = new URL[dependencies.length];
            for (int i = 0; i < urls.length; i++) {
                try {
                    urls[i] = Util.url(artifacts.get(key(dependencies[i])));
                } catch (MalformedURLException e) {
                    throw new RuntimeException(e);
                }
            }
            return urls;
        }

        @Override
        public URL getLocalArtifactUrl(DependencyJar dependency) {
            URL[] urls = getLocalArtifactUrls(dependency);
            if (urls.length > 0) {
                return urls[0];
            }
            return null;
        }

        private String key(DependencyJar dependency) {
            String key = dependency.getGroupId() + ":" + dependency.getArtifactId() + ":" 
            + dependency.getType();
            if (dependency.getClassifier() != null) {
                key += ":" + dependency.getClassifier();
            }
            return key;
        }

        protected void configureMaven(DependenciesTask dependenciesTask) {
            // maybe you want to override this method and some settings?
        }


    }
}

```
<p>可以象下面这样使用这个TestRunner:</p>
```java
@RunWith(BaseRobolectricGradleTestRunner.class) //指定使用RobolectricGradleTestRunner作为单元测试执行者
//配置常量,执行时所使用的AndroidSdk，还可以在这里配置Application类，AndroidManifest文件的路径，Shadow类
@Config(constants = BuildConfig.class, sdk = 21)
@PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*"}) //使得Powermock忽略这些包的注入类
public class EvnTest {

    @Test
    public void testEvn() {
        String absolutePath = Environment.getExternalStorageDirectory().getAbsolutePath();
        Assert.assertNotNull(absolutePath);
        System.out.println("absolute path: " + absolutePath);
        Context application = RuntimeEnvironment.application;
        SharedPreferences sSp = PreferenceManager.getDefaultSharedPreferences(application);
        SharedPreferences.Editor edit = sSp.edit();
        edit.putBoolean("halo", true);
        edit.commit();
        boolean halo = sSp.getBoolean("halo", false);
        Assert.assertTrue(halo);
    }

}
```

