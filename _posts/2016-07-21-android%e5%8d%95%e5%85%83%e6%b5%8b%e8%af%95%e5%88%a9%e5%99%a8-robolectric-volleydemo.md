---
id: 972
title: 'Android单元测试利器&#8211;Robolectric VolleyDemo'
date: 2016-07-21T08:51:59+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=972
permalink: /android/post-972.html
views:
  - 548
categories:
  - Android
  - 个人总结
tags:
  - Android 单元测试
  - Android 单元测试 Robolectric
  - Roblectric测试UI线程
  - Robolectric powermock
  - Robolectric测试主线程
---
Android单元测试系列文章的代码都可以在Github上找到: <a href='https://github.com/cloudchou/RobolectricDemo' target='_blank' >https://github.com/cloudchou/RobolectricDemo</a> 

## 使用Robolectric+Powermock测试UI线程逻辑

本节讲述如何使用Robolectric+PowerMock测试需要在UI线程执行的逻辑，比如Volley框架，在后台线程中请求网络，请求完成后在UI线程里通过Listener接口通知请求完成，并传递请求回来的数据。

在使用Robolectric框架测试需要在UI线程执行的逻辑时，需要注意的是在Android平台UI线程会轮询消息队列，然后从消息队列里取出消息，并将消息分发给Handler处理，UI线程执行的是轮询消息队列的死循环。但是在Robolectric框架中运行时，UI线程默认情况下并不会轮询消息队列，而需要在测试用例代码里主动驱动UI线程从消息队列里取出消息进行分发。测试用例执行时并不在UI线程，而是在单独的线程中，所以它可以主动驱动UI线程分发消息。

本节使用Volley请求来讲述如何针对这种情况进行测试，首先我们来看被测试的类VolleyRequest，它非常简单，使用了OkHttp作为传输层，请求<a href='http://www.mocky.io/v2/5597d86a6344715505576725' target='_blank' >http://www.mocky.io/v2/5597d86a6344715505576725</a>，然后将请求的数据保存下来。源代码如下所示:
 
{% highlight java linenos%}
public class VolleyRequester {
    private static final String TAG = VolleyRequester.class.getSimpleName();
    private RequestQueue mRequestQueue;
    private Context mContext;
    private volatile String mResponseStr;
 
    public void request(Context context) {
        mContext = context;
        RequestQueue volleyRequestQueue = getVolleyRequestQueue(mContext);
        //请求的url 请求该URL会返回一段json字符串
        //测试时 如果将其改成一个 无法访问的网址 就可以测试访问失败的情况
        String url = "http://www.mocky.io/v2/5597d86a6344715505576725";
        Response.Listener<String> dataListener = new Response.Listener<String>() {
            @Override
            public void onResponse(String response) {
                System.out.println("received response. ");
                mResponseStr = response;
            }
        };
        Response.ErrorListener errorListener = new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                //请求失败 会打印error日志
                SLog.e(TAG, "request failed");
            }
        };
        StringRequest request = new StringRequest(Request.Method.POST, url, dataListener, errorListener);
        volleyRequestQueue.add(request);
    }
 
    public String getResponseString() {
        return mResponseStr;
    }
 
    private RequestQueue getVolleyRequestQueue(Context ctx) {
        if (mRequestQueue == null) {
            // 使用OkHttp 作为传输层
            mRequestQueue = Volley.newRequestQueue(ctx, new OkHttpStack(new OkHttpClient()));
        }
        return mRequestQueue;
    }
 
    private static class OkHttpStack extends HurlStack {
        private OkHttpClient mOkHttpClient;
 
        public OkHttpStack(OkHttpClient okHttpClient) {
            mOkHttpClient = okHttpClient;
        }
 
        @Override
        protected HttpURLConnection createConnection(URL url) throws IOException {
            OkUrlFactory factory = new OkUrlFactory(mOkHttpClient);
            return factory.open(url);
        }
    }
}
{% endhighlight %}

接下来我们看看如何驱动主线程轮询消息队列，测试代码如下所示:


{% highlight java linenos %}
 /**
  * date 2016/7/3
  *
  * @author Cloud
  * @version 1.1
  * @since Ver 1.1
  */
 @RunWith(RobolectricGradleTestRunner.class)
 @Config(constants = BuildConfig.class, sdk = 21)
 //必须写如下代码 让PowerMock 忽略Robolectric的所有注入 这里因为要使用https 所以还需要忽略ssl
 @PowerMockIgnore({"org.mockito.*", "org.robolectric.*", "android.*", "javax.net.ssl.*"})
 //因为我们是针对类做静态函数的mock，所以必须使用PrepareForTest说明我们要mock的类
 @PrepareForTest({SLog.class})
 public class VolleyRequesterTest {
  
     //不可缺少的代码 表明使用Powermock执行单元测试，虽然我们使用的是RoblectricGradleTestRunner来执行单元测试
     //但是添加了如下代码后RoblectricGradleTestRunner会调用PowerMock的TestRunner去执行单元测试
     @Rule
     public PowerMockRule rule = new PowerMockRule();
  
     @Before
     public void setup() {
         PowerMockito.mockStatic(SLog.class);
     }
  
     @Test
     public void testRequest() throws Exception {
         PowerMockito.spy(SLog.class);
         VolleyRequester requester = new VolleyRequester();
         //调用请求方法后 volley 会开启后台线程去做真正的请求， 请求完毕后会在主线程上
         //调用Listener.onResponse方法通知请求完毕
         //但是主线程是一个有Handler的线程，Robolectric框架让主线程不轮询消息队列
         //必须在测试方法里主动驱动主线程轮询消息队列，针对消息进行处理
         //否则永远不会在UI线程上通知请求完毕
         requester.request(RuntimeEnvironment.application);
         //获取主线程的消息队列的调度者，通过它可以知道消息队列的情况
         //并驱动主线程主动轮询消息队列
         Scheduler scheduler = Robolectric.getForegroundThreadScheduler();
         //因为调用请求方法后 后台线程请求需要一段时间才能请求完毕，然后才会通知主线程
         // 所以在这里进行等待，直到消息队列里存在消息
         while (scheduler.size() == ) {
             Thread.sleep(500);
         }
         //轮询消息队列，这样就会在主线程进行通知
         scheduler.runOneTask();
         // 校验 请求是否失败
         PowerMockito.verifyStatic(times());
         SLog.e(VolleyRequester.class.getSimpleName(), "request failed");
         //如果没有失败 则打印请求回来的字符串
         String responseString = requester.getResponseString();
         System.out.println("response str:\n" + responseString);
     }
  
 }
 {% endhighlight %}


从上述代码可以看到我们可以通过获取Scheduler对象来判断消息队列中是否有消息，并调用Scheduler的runOneTask方法进行消息分发，这样就驱动了主线程进行消息轮询，执行结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-1024x318.png" alt="volley_demo" width="1024" height="318" class="aligncenter size-large wp-image-944" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-1024x318.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-300x93.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-768x239.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-200x62.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo.png 1255w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo.png)