---
     id: 388
     title: Handler Looper MessageQueue 详解
     date: 2014-04-16T01:15:54+08:00
     author: cloud
     layout: post
     guid: http://www.cloudchou.com/?p=388
     permalink: /android/post-388.html
     views:
       - 5084
     categories:
       - Android
     tags:
       - android handler message
       - android handler message queue
       - android handler message queue looper
       - android looper
       - android looper.prepare()
       - android looper用法
     ---
<h2>前言</h2>
 <p>一直对Android的Handler机制好奇，搞不清Handler,Looper,MessageQueue,Message之间的关系，近日对其做了一个深入研究，和大家分享一下。</p>
 
 <h2>类之间的关系</h2>
 <p>与Handler机制密切相关的类共5个，Handler，Looper，MessageQueue，Message，Messenger，Looper是最核心的类，它负责为线程建立Looper对象(通过静态方法)，还负责创建线程的消息队列MessageQueue对象，并负责处理MessageQueue的Message。MessageQueue负责管理Message。Handler会创建Message对象，同时将自己与Message对象关联，并压入MessageQueue，Looper会调用Handler分发Message。</p>
 <p><span style="color:red">注意:</span> 每个线程都至多只可以有一个Looper对象，也只可以有一个与该Looper对象关联的MessageQueue对象，但是可有多个Handler对象。Looper将Message取出来后，会调用与该Message关联的Handler的dispatchMessage方法。</p>
 <p>类之间的关系如下图所示：(看不清的话请看<a href="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图.png" target="_blank" style="text-decoration: underline">大图</a>：)</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler类图-979x1024.png" alt="Handler类图" width="979" height="1024" class="alignnone size-large wp-image-402" /></a>
 <h3>Looper</h3>
 <p>Looper的设计使用了多线程设计模式里的Thread Specifical Storage模式，属性sThreadLocal为每个线程存储Looper对象。</p>
 <p>sMainLooper是主线程使用的Looper对象。</p>
 <p>使用Looper对象时，会先调用静态的prepare方法或者prepareMainLooper方法来创建线程的Looper对象。如果是主线程会调用prepareMainLooper，如果是普通线程只需调用prepare方法，两者都会调用prepare(boolean quitAllowed)方法，该方法源码如下：</p>
 ```java
 private static void prepare(boolean quitAllowed) {
  if (sThreadLocal.get() != null) {
   throw new RuntimeException("Only one Looper may be created per thread");
  }
  sThreadLocal.set(new Looper(quitAllowed));
 }
 ```
 <p>这样便为线程建立了Looper对象，quitAllowed表示是否允许退出，如果是主线程则不能允许退出。</p>
 <p>prepareMainLooper创建好Looper对象之后，还会将sMainLooper引用新建立的Looper对象。</p>
 <p>myLooper方法会返回当前线程的Looper对象，myQueue方法则会返回当前线程Looper对象的MessageQueue对象。</p>
 <p>Looper的构造器方法里会创建当前线程的MessageQueue实例，并将mThread指向当前线程。源码如下所示：</p>
 ```java
 private Looper(boolean quitAllowed) {
         mQueue = new MessageQueue(quitAllowed);
         mRun = true;
         mThread = Thread.currentThread();
 }
 ```
 <p>使用Looper时，调用完Looper.prepare之后，还需要调用Looper.loop方法，该方法是一个死循环，会不断从MessageQueue里取出消息，并调用消息关联的Handler对象来处理该消息，Handler对象会分发该消息。loop的源码如下：</p>
 ```java
 public static void loop() {
   final Looper me = myLooper();
   if (me == null) {
       throw new RuntimeException("No Looper; Looper"
       +"prepare() wasn't called on this thread.");
   }
   final MessageQueue queue = me.mQueue;
 
   // Make sure the identity of this thread is that of the local process,
   // and keep track of what that identity token actually is.
   Binder.clearCallingIdentity();
   final long ident = Binder.clearCallingIdentity();
 
   for (;;) {
       //从消息队列MessageQueue上取下一个消息
       Message msg = queue.next(); // might block
       if (msg == null) {
           // No message indicates that the message queue is quitting.
           return;
       }
 
       // This must be in a local variable, 
       //in case a UI event sets the logger
       Printer logging = me.mLogging;
       if (logging != null) {
           logging.println(">>>>> Dispatching to " + msg.target + " " +
                   msg.callback + ": " + msg.what);
       }
      //调用message关联的Hander对象分发消息
       msg.target.dispatchMessage(msg);
 
       if (logging != null) {
           logging.println("<<<<< Finished to " + msg.target 
           + " " + msg.callback);
       }
 
       // Make sure that during the course of dispatching the
       // identity of the thread wasn't corrupted.
       final long newIdent = Binder.clearCallingIdentity();
       if (ident != newIdent) {
           Log.wtf(TAG, "Thread identity changed from 0x"
                   + Long.toHexString(ident) + " to 0x"
                   + Long.toHexString(newIdent) + " while dispatching to "
                   + msg.target.getClass().getName() + " "
                   + msg.callback + " what=" + msg.what);
       }
 
       msg.recycle();
   }
 }
 ```
 
 
 <h3>MessageQueue</h3>
 <p>负责管理消息队列，实际上Message类有一个next字段，会将Message对象串在一起成为一个消息队列，所以并不需要LinkedList之类的数据结构将Message对象组在一起成为队列。</p>
 <p>最重要的方法是next，用于获取下一个Message对象，如果没有需要处理的Message对象，该方法将阻塞。MessageQueue用本地方法做同步互斥，因为这样时间更精准。每个Message对象都有一个什么时刻处理该Message对象的属性when，没到时间都不会处理该Message对象，如果时间不精准的话，会导致系统消息不能及时处理。 源码如下：</p>
 ```java
 final Message next() {
   int pendingIdleHandlerCount = -1; // -1 only during first iteration
   int nextPollTimeoutMillis = 0;
 
   for (;;) {
       if (nextPollTimeoutMillis != 0) {
           Binder.flushPendingCommands();
       }
       nativePollOnce(mPtr, nextPollTimeoutMillis); 
       synchronized (this) {
           if (mQuiting) {
               return null;
           } 
           // Try to retrieve the next message.  Return if found.
           final long now = SystemClock.uptimeMillis();
           Message prevMsg = null;
           Message msg = mMessages;
           if (msg != null && msg.target == null) {
               // Stalled by a barrier. 
               // Find the next asynchronous message in the queue.
               do {
                   prevMsg = msg;
                   msg = msg.next;
               } while (msg != null && !msg.isAsynchronous());
           }
           if (msg != null) {
               if (now < msg.when) {
                 // Next message is not ready.  
                 //Set a timeout to wake up when it is ready.
                 nextPollTimeoutMillis = (int) Math.min(msg.when - now, 
                            Integer.MAX_VALUE);
               } else {
                   // 获得了一个Message对象，将其返回
                   mBlocked = false;
                   if (prevMsg != null) {
                       prevMsg.next = msg.next;
                   } else {
                       mMessages = msg.next;
                   }
                   msg.next = null;
                   if (false) Log.v("MessageQueue", "Returning message: "
                    + msg);
                   msg.markInUse();
                   return msg;
               }
           } else {
               // No more messages.
               nextPollTimeoutMillis = -1;
           }
 
           // If first time idle, then get the number of idlers to run.
           // Idle handles only run if the queue is empty or 
           // if the first message
           // in the queue (possibly a barrier) is due to 
           //be handled in the future.
           if (pendingIdleHandlerCount < 0
                   && (mMessages == null || now < mMessages.when)) {
               pendingIdleHandlerCount = mIdleHandlers.size();
           }
           if (pendingIdleHandlerCount <= 0) {
               // No idle handlers to run.  Loop and wait some more.
               mBlocked = true;
               continue;
           }
 
           if (mPendingIdleHandlers == null) {
               mPendingIdleHandlers = 
                 new IdleHandler[Math.max(pendingIdleHandlerCount, 4)];
           }
           mPendingIdleHandlers = 
             mIdleHandlers.toArray(mPendingIdleHandlers);
       }
 
       // Run the idle handlers.
       // We only ever reach this code block during the first iteration.
       for (int i = 0; i < pendingIdleHandlerCount; i++) {
           final IdleHandler idler = mPendingIdleHandlers[i];
           // release the reference to the handler
           mPendingIdleHandlers[i] = null; 
 
           boolean keep = false;
           try {
               keep = idler.queueIdle();
           } catch (Throwable t) {
               Log.wtf("MessageQueue", "IdleHandler threw exception", t);
           }
 
           if (!keep) {
               synchronized (this) {
                   mIdleHandlers.remove(idler);
               }
           }
       }
 
       // Reset the idle handler count to 0 so we do not run them again.
       pendingIdleHandlerCount = 0;
 
       // While calling an idle handler, a new message could have been delivered
       // so go back and look again for a pending message without waiting.
       nextPollTimeoutMillis = 0;
   }
 }
 ```
 <p>enqueueMessage用于将Message对象插入消息队列，消息队列的消息是按待处理时间排序的。该方法会被Hander对象调用。源码如下：</p>
 ```java
 final boolean enqueueMessage(Message msg, long when) {
   if (msg.isInUse()) {
       throw new AndroidRuntimeException(msg + 
       " This message is already in use.");
   }
   if (msg.target == null) {
       throw new AndroidRuntimeException("Message must have a target.");
   }
 
   boolean needWake;
   synchronized (this) {
       if (mQuiting) {
           RuntimeException e = new RuntimeException(
                   msg.target 
                   + " sending message to a Handler on a dead thread");
           Log.w("MessageQueue", e.getMessage(), e);
           return false;
       }
 
       msg.when = when;
       Message p = mMessages;
       if (p == null || when == 0 || when < p.when) {
           // New head, wake up the event queue if blocked.
           msg.next = p;
           mMessages = msg;
           needWake = mBlocked;
       } else {
           // Inserted within the middle of the queue.  
           //Usually we don't have to wake
           // up the event queue unless there is a barrier 
           //at the head of the queue
           // and the message is the earliest asynchronous 
           //message in the queue.
           needWake = mBlocked && p.target == null && msg.isAsynchronous();
           Message prev;
           for (;;) {
               prev = p;
               p = p.next;
               if (p == null || when < p.when) {
                   break;
               }
               if (needWake && p.isAsynchronous()) {
                   needWake = false;
               }
           }
           msg.next = p; // invariant: p == prev.next
           prev.next = msg;
       }
   }
   if (needWake) {
       nativeWake(mPtr);
   }
   return true;
 }
 ```
 <p>removeMessages系列的方法用于从消息队列里删除消息。</p>
 
 
 <h3>Message</h3>
 <p>Message表示消息，它的字段有：</p>
 <li>1)\t<span style="color:red">what</span> 用来区分不同消息，这个是用户自定义的，通常会用常量来区分</li>
 <li>2)\targ1  arg1 和 arg2 是一种轻量级的传递数据的方式</li>
 <li>3)\targ2 </li>
 <li>4)\tobj 任意对象，但是使用Messenger跨进程传递Message时不能为null</li>
 <li>5)\treplyTo 可选的Messenger对象，被谁接收</li>
 <li>6)\tflags 一些flag FLAG_IN_USE FLAG_ASYNCHRONOUS  FLAGS_TO_CLEAR_ON_COPY_FROM的组合</li>
 <li>7)\t<span style="color:red">when</span> 处理Message的时间</li>
 <li>8)\t<span style="color:red">data </span> 携带的bundle格式的数据</li>
 <li>9)\t<span style="color:red">target </span> 关联的Handler对象，处理Message时会调用它分发处理Message对象</li>
 <li>10)\tcallback 关联的Runnable对象，Handler分发处理Message时会优先执行callback的run方法</li>
 <li>11)\t<span style="color:red">next</span> Message队列里的下一个Message对象</li>
 <li>12)\tsPoolSync 消息池的同步锁</li>
 <li>13)\tsPool 消息池，创建好的Message对象用完了会放到消息池，下次再次创建Message对象时会从消息池里取出Message对象，只有当消息池没有任何Message对象时才会新建Message对象，这样节省了内存占用。</li>
 <li>14)\tsPoolSize 消息池当前消息个数</li>
 <p>管理Message对象时，Android采用了消息池，可以有效节省内存，有两个方法会操作消息池，obtain和recycle，源码如下：</p>
 ```java
 public static Message obtain() { //获得Message对象
     synchronized (sPoolSync) {
         if (sPool != null) { //只要消息池不空，则从消息池里取下一个消息
             Message m = sPool;
             sPool = m.next;
             m.next = null;
             sPoolSize--;
             return m;
         }
     }
     return new Message();//若消息池为空，则新建一个Message对象
 }
 public void recycle() {
     clearForRecycle();//将消息携带的所有数据清空
 
     synchronized (sPoolSync) {//将消息回收到消息池
         if (sPoolSize < MAX_POOL_SIZE) {
             next = sPool;
             sPool = this;
             sPoolSize++;
         }
     }
 }
 ```
 <p>Message的静态obtain系列方法都会调用上述的obtain方法来获取Message对象，而Handeler的obtainMessage系列方法都是调用Message的静态obtain系列方法来获得Message对象，故此可知Android会重复利用Message对象，从而节省了内存。</p>
 
 <h3>Handler</h3>
 <p>我们平常都不怎么接触Looper类和MessageQueue类，但是经常使用Handler。我们对Looper类和MessageQueue知之甚少，甚至不知道Handler如何和Looper对象以及MessageQueue对象关联的。这是因为使用了Thread Specifical Pattern的缘故，在某个线程里只需调用Looper.prepare或者Looper. prepareMainLooper方法即可为该线程建立Looper对象和MessageQueue对象，当前线程也只需要调用Looper.myLooper即可得到当前线程的Looper对象。</p>
 <p>创建Handler对象时，会先获得当前线程的Looper对象，以及looper对象关联的消息队列，并让自己对应的字段引用这些对象，源码如下所示：</p>
 ```java
 public Handler(Callback callback, boolean async) {
     if (FIND_POTENTIAL_LEAKS) {
         final Class<? extends Handler> klass = getClass();
         if ((klass.isAnonymousClass() || klass.isMemberClass() || klass.isLocalClass()) &&
                 (klass.getModifiers() & Modifier.STATIC) == 0) {
             Log.w(TAG, "The following Handler class should be static"
                 +" or leaks might occur: " +
                 klass.getCanonicalName());
         }
     } 
     mLooper = Looper.myLooper();
     if (mLooper == null) {
         throw new RuntimeException(
             "Can't create handler inside thread "
             +"that has not called Looper.prepare()");
     }
     mQueue = mLooper.mQueue;
     mCallback = callback;
     mAsynchronous = async;
 }
 ```
 我们通常会象下面这样使用Handler：
 ```java
 Handler h = new Handler() {
 \t@Override
 \tpublic void handleMessage(Message msg) {
 \t\tswitch (msg.what) {
 \t\tcase TEST:
 \t\t\t
 \t\t\tbreak;
 \t\t}
 \t}
 };
 h.sendEmptyMessage(h. obtainMessage(TEST));
 ```
 <p>调用Handler的sendMessage系列方法时，会调用MessageQueue的enqueueMessage方法将Message插入到消息队列，Looper的loop方法会从MessageQueue里取出Message对象，并调用与其关联的Handler对象的dispatchMessage方法分发处理该Message对象。dispatchMessage方法的源码如下所示：</p>
 ```java
 public void dispatchMessage(Message msg) {
     if (msg.callback != null) { //优先执行Message的callback回调
         handleCallback(msg);
     } else {
        //如果Handler有与其关联的callback，则调用callback的handleMessage方法
         if (mCallback != null) {z
             if (mCallback.handleMessage(msg)) {
                 return;
             }
         }
         //我们通常会覆盖handleMessage方法，在该方法里写处理消息的逻辑
         handleMessage(msg);
     }
 }
 ```
 <p>注意Handler类的obtainMessage系列方法其实是调用Message的静态obtain系列方法生成Message对象。</p>
 <h3>Messenger</h3>
 <p>引用了一个Handler对象，其它地方可以用Messenger来发送消息给这个Handler。利用这点可以实现跨进程的基于消息的通信，如果创建了一个 指向某个进程A的Handler对象 的Messenger对象，并把该Messenger对象传递给另外一个进程B，那么进程B就可以发送消息给进程A了。</p>
 
 <h2>时序图</h2>
 <p>Looper准备好并进入死循环的时序图如下图所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/04/loop-prepare-loop.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/loop-prepare-loop.png" alt="loop prepare loop" width="700" height="536" class="alignnone size-full wp-image-408" /></a>
 
 <p>Handler创建时的时序图如下图所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-create.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-create.png" alt="Handler create" width="427" height="342" class="alignnone size-full wp-image-407" /></a>
 
 <p>Handler创建消息并发送消息，然后Looper处理消息的时序图如下图所示：</p>
 <a href="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-send-message.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/04/Handler-send-message.png" alt="Handler  send message" width="862" height="758" class="alignnone size-full wp-image-410" /></a>
