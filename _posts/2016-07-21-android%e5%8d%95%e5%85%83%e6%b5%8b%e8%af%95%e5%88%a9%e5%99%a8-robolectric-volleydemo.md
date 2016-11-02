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

`​`` html
<a href="#">Hello world</a>
`​``

```java
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
```

接下来我们看看如何驱动主线程轮询消息队列，测试代码如下所示:



从上述代码可以看到我们可以通过获取Scheduler对象来判断消息队列中是否有消息，并调用Scheduler的runOneTask方法进行消息分发，这样就驱动了主线程进行消息轮询，执行结果如下所示:

[<img src="http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-1024x318.png" alt="volley_demo" width="1024" height="318" class="aligncenter size-large wp-image-944" srcset="http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-1024x318.png 1024w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-300x93.png 300w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-768x239.png 768w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo-200x62.png 200w, http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo.png 1255w" sizes="(max-width: 1024px) 100vw, 1024px" />](http://www.cloudchou.com/wp-content/uploads/2016/07/volley_demo.png)