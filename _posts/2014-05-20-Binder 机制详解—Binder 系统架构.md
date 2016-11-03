---
id: 507
title: Binder 机制详解—Binder 系统架构
date: 2014-05-20T22:50:54+08:00
author: cloud
layout: post
guid: http://www.cloudchou.com/?p=507
permalink: /android/post-507.html
views:
  - 12990
categories:
  - Android
tags:
  - android service binder
  - binder service
  - binder机制
  - binder机制详解
  - binder系统架构
---
<p>前一篇博客介绍了Binder IPC程序结构，本篇将从架构角度分析binder, 介绍binder机制的层次划分,并着重分析驱动适配层和Binder核心框架层。</p>

<h2>Binder层次划分</h2>
<p>Binder层次划分如下图所示：</p> 
<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/binder-layer.jpg" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/binder-layer.jpg" alt="binder layer" width="330" height="290" class="aligncenter size-full wp-image-514" /></a>
<ul>
<li>
 <h3>(1)驱动层</h3>
<p>正如大家所知道的，Binder机制是需要Linux内核支持的，Android因此添加了binder驱动，binder 设备节点为/dev/binder，主设备号为10，binder 驱动程序在内核中的头文件和代码路径如下：</p>
<p>kernel/drivers/staging/binder.h</p>
<p>kernel/drivers/staging/binder.c</p>
<p>binder驱动程序的主要作用是完成实际的binder数据传输。</p>
<p>驱动实现时，主要通过binder_ioctl函数与用户空间的进程交换数据(用户进程与驱动交互时使用ioctl函数，对应驱动源码的binder_ioctl函数)。BINDDER_WRITE_READ命令字用来读写数据，数据包中有一个cmd域用于区分不同的请求。binder_thread_write函数用于发送请求，binder_thread_read函数用于读取结果。在binder_thread_write函数中调用binder_transaction函数来转发请求并返回结果。当收到请求时，binder_transaction函数会根据对象的handle找到对象所在的进程，如果handle为0，则认为对象是context_mgr，把请求发给context_mgr所在的进程。所有的binder请求对象全部放到一个RB树中，最后把请求放到目标进程的队列中，等待目标进程读取。</p>
<p>A进程如果要使用B进程的服务，B进程首先要注册此服务，A进程通过service mananger获取该服务的handle，通过这个handle，A进程就可以使用该服务了。A进程使用B进程的服务还意味着二者遵循相同的协议，这个协议反映在代码上就是二者要实现IBinder接口。</p>
<p>Binder的本质就是要把对象a从一个进程B映射到另一个进程A中，进程A中调用对象a的方法象调本地方法一样。但实际上进程B和进程A有不同的地址空间，对象a只有在进程B里有意义，但是驱动层可将进程B的对象a映射到进程A，得到对象a在进程A的表示，称之为handle，也叫句柄。这样，对象a在进程B的地址空间里有一个实际地址，在进程A里有对应的句柄，驱动会将这个句柄和对象a的实际地址映射起来。对象a对于进程B来说是本地对象，对象a对于进程A来说是远程对象，而handle对于进程A来说是对象a在进程A的引用。</p>
<p>适配层使用binder驱动时使用了内存映射技术，故此进程间传输数据时只需拷贝一次，传统的IPC需拷贝两次，因此使用binder可大大提高IPC通信效率。</p>
</li>
<li>
 <h3>(2)驱动适配层</h3>
 <p>主要是IPCThreadState.cpp和ProcessState.cpp,源码位于frameworks/native/libs/binder</p>
<p>这两个类都采用了单例模式，主要负责和驱动直接交互。</p>
<p>ProcessState负责打开binder设备，进行一些初始化设置并做内存映射</p>
<p>IPCThreadState负责直接和binder设备通信，使用ioctl读写binder驱动数据</p>
<p>后面将详细分析ProcessState和IPCThreadState。</p>

</li>
<li>
 <h3>(3)Binder核心框架层</h3>
<p>Binder核心框架主要是IBinder及它的两个子类，即BBinder和BpBinder，分别代表了最基本的服务端及客户端。</p>
<p>binder service服务端实体类会继承BnInterface，而BnInterface会继承自BBinder，服务端可将BBinder对象注册到servicemananger进程。</p>
<p>客户端程序和驱动交互时只能得到远程对象的句柄handle，它可以调用调用ProcessState的getStrongProxyForHandle函数，利用句柄handle建立BpBinder对象，然后将它转为IBinder指针返回给调用者。这样客户端每次调用IBinder指针的transact方法，其实是执行BpBinder的transact方法。</p>

</li>
<li>
 <h3>(4)Binder框架层</h3>
<p>本地Binder框架层包含以下类(frameworks/native/libs/binder)：</p>
<p>RefBase，IInterface，BnInterface，BpInterface，BpRefBase，Parcel 等等</p>
<p>Java框架层包含以下类(frameworks/base/core/java/android/os):</p>
<p>IBinder，Binder，IInterface，ServiceManagerNative，ServiceManager，BinderInternal，IServiceManager，ServiceManagerProxy</p>
<p>Java框架层的类的部分方法的实现在本地代码里(frameworks/base/core/jni)。</p>
<p>后续博客会详细分析本地binder框架和Java层 binder框架各自的类关系。</p>

</li>

<li>
 <h3>(5)Binder 服务和客户端实现</h3>
 <p>从Binder入门系列我们也知道，binder service服务端和binder 客户端都有native和Java之分，Java层服务端从Binder继承并实现服务接口，Java层客户端直接实现服务接口即可，而本地服务端需继承自BnInterface，本地客户端继承自BpInterface。</p>
 <p>后续博客分析本地binder框架和Java层 binder框架时会给出更详尽的类关系。</p>
</li>

</ul>


<h2>ProcessState</h2>
<p>ProcessState负责打开binder设备，进行一些初始化设置。</p>
<p>ProcessState的类图如下图所示：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/processstate.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/processstate.png" alt="processstate" width="511" height="636" class="aligncenter size-full wp-image-523" /></a>

<p>我们通常在binder service的服务端象下面一样使用ProcessState:</p>
```cpp
//初始化单例，其实不调用该语句也能正常运行
sp < ProcessState > proc(ProcessState::self());
//启动线程池
ProcessState::self()->startThreadPool();
``` 

<p>注意binder service服务端提供binder service时，是以线程池的形式提供服务，也就说可以同时启动多个线程来提供服务，可以通过如下方式来启动多个线程：</p>
```cpp
//设置线程池支持的最大线程个数
ProcessState::self()->setThreadPoolMaxThreadCount(4);
//启动一个服务线程
ProcessState::self()->spawnPooledThread(false);
//启动一个服务线程
ProcessState::self()->spawnPooledThread(false);
``` 

<p>接下来我们分析ProcessState的构造函数：</p>
```cpp
ProcessState::ProcessState()
    : mDriverFD(open_driver()) //打开binder设备，并将mDriverFD设置为打开的文件符
    , mVMStart(MAP_FAILED)
    , mManagesContexts(false)
    , mBinderContextCheckFunc(NULL)
    , mBinderContextUserData(NULL)
    , mThreadPoolStarted(false) //构造时，默认并未启动线程池
    , mThreadPoolSeq(1)
{
    if (mDriverFD >= 0) {
        // XXX Ideally, there should be a specific define for whether we
        // have mmap (or whether we could possibly have the kernel module
        // availabla).
#if !defined(HAVE_WIN32_IPC)
        // mmap the binder, providing a chunk of virtual address space 
        // to receive transactions.
        //内存映射 
        mVMStart = mmap(0, BINDER_VM_SIZE, PROT_READ, 
                        MAP_PRIVATE | MAP_NORESERVE, mDriverFD, 0);
        if (mVMStart == MAP_FAILED) {
            // *sigh*
            ALOGE("Using /dev/binder failed: unable to 
                     mmap transaction memory.\\n");
            close(mDriverFD);
            mDriverFD = -1;
        }
#else
        mDriverFD = -1;
#endif
    }

    LOG_ALWAYS_FATAL_IF(mDriverFD < 0, "Binder driver 
                               could not be opened.  Terminating.");
}
```

<p>open_driver的实现：</p>
```cpp
static int open_driver()
{
    int fd = open("/dev/binder", O_RDWR); //打开binder设备
    if (fd >= 0) {
        fcntl(fd, F_SETFD, FD_CLOEXEC);
        int vers;
        //检查版本
        status_t result = ioctl(fd, BINDER_VERSION, &vers);
        if (result == -1) {
            ALOGE("Binder ioctl to obtain version failed: %s", 
                            strerror(errno));
            close(fd);
            fd = -1;
        }
        if (result != 0 || vers != BINDER_CURRENT_PROTOCOL_VERSION) {
            ALOGE("Binder driver protocol does not match 
                              user space protocol!");
            close(fd);
            fd = -1;
        }
        //默认设置支持的线程数是15
        size_t maxThreads = 15;
        result = ioctl(fd, BINDER_SET_MAX_THREADS, &maxThreads);
        if (result == -1) {
            ALOGE("Binder ioctl to set max threads failed: %s",
                           strerror(errno));
        }
    } else {
        ALOGW("Opening '/dev/binder' failed: %s\\n", strerror(errno));
    }
    return fd;
}
```

<p>startThreadPool的实现(用于启动线程池)：</p>
```cpp
void ProcessState::startThreadPool()
{
    AutoMutex _l(mLock);
    if (!mThreadPoolStarted) {
        mThreadPoolStarted = true;
        spawnPooledThread(true);
    }
}
```

<p>spawnPooledThread的实现：</p>
```cpp
void ProcessState::spawnPooledThread(bool isMain)
{
    if (mThreadPoolStarted) {
        int32_t s = android_atomic_add(1, &mThreadPoolSeq);
        char buf[16];
        snprintf(buf, sizeof(buf), "Binder_%X", s);
        ALOGV("Spawning new pooled thread, name=%s\\n", buf);
        //PoolThread也在ProcessState里实现
        sp<Thread> t = new PoolThread(isMain);
        //启动线程,buf是新线程的名字
        t->run(buf);
    }
}
```

<p>PoolThread继承自Thread类，Thread类是框架层提供的一个类，和Java的Thread类相似，使用PoolThread类时需实现threadLoop函数(Java使用Thread类时需覆盖run方法)，新线程执行threadLoop函数，启动新线程需调用PoolThread对象的run方法(Java中调用start方法)。</p>
<p>PoolThread类的源码如下所示：</p>
```cpp
class PoolThread : public Thread
{
public:
    PoolThread(bool isMain)
        : mIsMain(isMain)
    {
    }
    
protected:
    virtual bool threadLoop()
{
    //加入线程池
        IPCThreadState::self()->joinThreadPool(mIsMain);
        return false;
    }
    
    const bool mIsMain;
};
```


<h2>IPCThreadState</h2>
<p>IPCThreadState负责直接和binder设备通信，从binder驱动读取数据，并向binder驱动写数据。</p>
<p>IPCThreadState也采用了单例模式。</p>
<p>IPCThreadState类图如下图所示：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/IPCThreadState.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/IPCThreadState.png" alt="IPCThreadState" width="607" height="704" class="aligncenter size-full wp-image-525" /></a>

<p>我们通常在binder service的服务端象下面一样使用IPCThreadState:</p>
<p>IPCThreadState::self()->joinThreadPool();</p>
<p>IPCThreadState joinThreadPool的函数原型：</p>
<p>void                joinThreadPool(bool isMain = true);</p>
<p>IPCThreadState的构造函数实现：</p>
```cpp
IPCThreadState::IPCThreadState()
    : mProcess(ProcessState::self()),
      mMyThreadId(androidGetTid()),
      mStrictModePolicy(0),
      mLastTransactionBinderFlags(0)
{
    pthread_setspecific(gTLS, this);
    clearCaller();
    mIn.setDataCapacity(256);
    mOut.setDataCapacity(256);
}
```

<p>joinThreadPool的函数实现如下所示：</p>
```cpp
void IPCThreadState::joinThreadPool(bool isMain)
{
    LOG_THREADPOOL("**** THREAD %p (PID %d) IS JOINING THE THREAD POOL\\n",
                       (void*)pthread_self(), getpid());

    mOut.writeInt32(isMain ? BC_ENTER_LOOPER : BC_REGISTER_LOOPER);
    
    // This thread may have been spawned by a thread that was 
    // in the background scheduling group, so first we will 
    //make sure it is in the foreground
    // one to avoid performing an initial transaction in the background.
    set_sched_policy(mMyThreadId, SP_FOREGROUND);
        
    status_t result;
    do {
        int32_t cmd;
        
        // When we've cleared the incoming command queue, 
        //process any pending derefs
        if (mIn.dataPosition() >= mIn.dataSize()) {
            size_t numPending = mPendingWeakDerefs.size();
            if (numPending > 0) {
                for (size_t i = 0; i < numPending; i++) {
                    RefBase::weakref_type* refs = mPendingWeakDerefs[i];
                    refs->decWeak(mProcess.get());
                }
                mPendingWeakDerefs.clear();
            }

            numPending = mPendingStrongDerefs.size();
            if (numPending > 0) {
                for (size_t i = 0; i < numPending; i++) {
                    BBinder* obj = mPendingStrongDerefs[i];
                    obj->decStrong(mProcess.get());
                }
                mPendingStrongDerefs.clear();
            }
        }

        // now get the next command to be processed, waiting if necessary
        //跟驱动交互 获取数据 或者写入数据
        result = talkWithDriver();
        if (result >= NO_ERROR) {
            size_t IN = mIn.dataAvail();
            if (IN < sizeof(int32_t)) continue;
            //获取命令
            cmd = mIn.readInt32();
            IF_LOG_COMMANDS() {
                alog << "Processing top-level Command: "
                    << getReturnString(cmd) << endl;
            }

            //执行命令
            result = executeCommand(cmd);
        }
        
  // After executing the command, ensure that the thread is returned to the
  // foreground cgroup before rejoining the pool.  The driver takes care of
  // restoring the priority, but doesn't do anything with cgroups so we
  // need to take care of that here in userspace.  Note that we do make
  // sure to go in the foreground after executing a transaction, but
  // there are other callbacks into user code that could have changed
  // our group so we want to make absolutely sure it is put back.
        set_sched_policy(mMyThreadId, SP_FOREGROUND);

        // Let this thread exit the thread pool if it is no longer
        // needed and it is not the main process thread.
        if(result == TIMED_OUT && !isMain) {
            break;
        }
    } while (result != -ECONNREFUSED && result != -EBADF);

    LOG_THREADPOOL("**** THREAD %p (PID %d) IS LEAVING THE THREAD POOL
                    err=%p\\n",
        (void*)pthread_self(), getpid(), (void*)result);
    
    mOut.writeInt32(BC_EXIT_LOOPER);
    talkWithDriver(false);
}
```
<p>talkWithDriver的实现：</p>
```cpp
status_t IPCThreadState::talkWithDriver(bool doReceive)
{
    if (mProcess->mDriverFD <= 0) {
        return -EBADF;
    }
    
    binder_write_read bwr; //和驱动交互时的数据结构
    
    // Is the read buffer empty?
    const bool needRead = mIn.dataPosition() >= mIn.dataSize();
    
    // We don't want to write anything if we are still reading
    // from data left in the input buffer and the caller
    // has requested to read the next data.
    const size_t outAvail = (!doReceive || needRead) ? mOut.dataSize() : 0;
    
    bwr.write_size = outAvail;
    bwr.write_buffer = (long unsigned int)mOut.data();

    // This is what we'll read.
    if (doReceive && needRead) {
        bwr.read_size = mIn.dataCapacity();
        bwr.read_buffer = (long unsigned int)mIn.data();
    } else {
        bwr.read_size = 0;
        bwr.read_buffer = 0;
    }

    IF_LOG_COMMANDS() {
        TextOutput::Bundle _b(alog);
        if (outAvail != 0) {
            alog << "Sending commands to driver: " << indent;
            const void* cmds = (const void*)bwr.write_buffer;
            const void* end = ((const uint8_t*)cmds)+bwr.write_size;
            alog << HexDump(cmds, bwr.write_size) << endl;
            while (cmds < end) cmds = printCommand(alog, cmds);
            alog << dedent;
        }
        alog << "Size of receive buffer: " << bwr.read_size
            << ", needRead: " << needRead << ", doReceive: " 
            << doReceive << endl;
    }
    
    // Return immediately if there is nothing to do.
    if ((bwr.write_size == 0) && (bwr.read_size == 0)) return NO_ERROR;

    bwr.write_consumed = 0;
    bwr.read_consumed = 0;
    status_t err;
    do {
        IF_LOG_COMMANDS() {
            alog << "About to read/write, write size = " 
                  << mOut.dataSize() << endl;
        }
#if defined(HAVE_ANDROID_OS)
        //使用ioctl与binder驱动交互，BINDER_WRITE_READ是最重要的命令字
        if (ioctl(mProcess->mDriverFD, BINDER_WRITE_READ, &bwr) >= 0)
            err = NO_ERROR;
        else
            err = -errno;
#else
        err = INVALID_OPERATION;
#endif
        if (mProcess->mDriverFD <= 0) {
            err = -EBADF;
        }
        IF_LOG_COMMANDS() {
            alog << "Finished read/write, write size = " 
                  << mOut.dataSize() << endl;
        }
    } while (err == -EINTR);

    IF_LOG_COMMANDS() {
        alog << "Our err: " << (void*)err << ", write consumed: "
            << bwr.write_consumed << " (of " << mOut.dataSize()
<< "), read consumed: " 
<< bwr.read_consumed << endl;
    }

    if (err >= NO_ERROR) {
        if (bwr.write_consumed > 0) {
            if (bwr.write_consumed < (ssize_t)mOut.dataSize())
                mOut.remove(0, bwr.write_consumed);
            else
                mOut.setDataSize(0);
        }
        if (bwr.read_consumed > 0) {
            mIn.setDataSize(bwr.read_consumed);
            mIn.setDataPosition(0);
        }
        IF_LOG_COMMANDS() {
            TextOutput::Bundle _b(alog);
            alog << "Remaining data size: " << mOut.dataSize() << endl;
            alog << "Received commands from driver: " << indent;
            const void* cmds = mIn.data();
            const void* end = mIn.data() + mIn.dataSize();
            alog << HexDump(cmds, mIn.dataSize()) << endl;
            while (cmds < end) cmds = printReturnCommand(alog, cmds);
            alog << dedent;
        }
        return NO_ERROR;
    }
    
    return err;
}
```

executeCommand的实现：
```cpp
status_t IPCThreadState::executeCommand(int32_t cmd)
{
    BBinder* obj;
    RefBase::weakref_type* refs;
    status_t result = NO_ERROR;
    
    switch (cmd) {
    case BR_ERROR:
        result = mIn.readInt32();
        break;
        
    case BR_OK:
        break;
        
    case BR_ACQUIRE:
        refs = (RefBase::weakref_type*)mIn.readInt32();
        obj = (BBinder*)mIn.readInt32();
        ALOG_ASSERT(refs->refBase() == obj,
                   "BR_ACQUIRE: object %p does not match cookie %p 
                     (expected %p)",
                   refs, obj, refs->refBase());
        obj->incStrong(mProcess.get());
        IF_LOG_REMOTEREFS() {
            LOG_REMOTEREFS("BR_ACQUIRE from driver on %p", obj);
            obj->printRefs();
        }
        mOut.writeInt32(BC_ACQUIRE_DONE);
        mOut.writeInt32((int32_t)refs);
        mOut.writeInt32((int32_t)obj);
        break;
        
    case BR_RELEASE:
        refs = (RefBase::weakref_type*)mIn.readInt32();
        obj = (BBinder*)mIn.readInt32();
        ALOG_ASSERT(refs->refBase() == obj,
                   "BR_RELEASE: object %p does not match 
                    cookie %p (expected %p)",
                   refs, obj, refs->refBase());
        IF_LOG_REMOTEREFS() {
            LOG_REMOTEREFS("BR_RELEASE from driver on %p", obj);
            obj->printRefs();
        }
        mPendingStrongDerefs.push(obj);
        break;
        
    case BR_INCREFS:
        refs = (RefBase::weakref_type*)mIn.readInt32();
        obj = (BBinder*)mIn.readInt32();
        refs->incWeak(mProcess.get());
        mOut.writeInt32(BC_INCREFS_DONE);
        mOut.writeInt32((int32_t)refs);
        mOut.writeInt32((int32_t)obj);
        break;
        
    case BR_DECREFS:
        refs = (RefBase::weakref_type*)mIn.readInt32();
        obj = (BBinder*)mIn.readInt32();
        // NOTE: This assertion is not valid, because the object may no
        // longer exist (thus the (BBinder*)cast 
        //above resulting in a different
        // memory address).
        //ALOG_ASSERT(refs->refBase() == obj,
        //           "BR_DECREFS: object %p does not match 
        //cookie %p (expected %p)",
        //           refs, obj, refs->refBase());
        mPendingWeakDerefs.push(refs);
        break;
        
    case BR_ATTEMPT_ACQUIRE:
        refs = (RefBase::weakref_type*)mIn.readInt32();
        obj = (BBinder*)mIn.readInt32();
         
        {
            const bool success = refs->attemptIncStrong(mProcess.get());
            ALOG_ASSERT(success && refs->refBase() == obj,
                       "BR_ATTEMPT_ACQUIRE: object %p does not 
                         match cookie %p (expected %p)",
                       refs, obj, refs->refBase());
            
            mOut.writeInt32(BC_ACQUIRE_RESULT);
            mOut.writeInt32((int32_t)success);
        }
        break;
    
    case BR_TRANSACTION: //最重要的分支
        {
            binder_transaction_data tr;
            result = mIn.read(&tr, sizeof(tr));
            ALOG_ASSERT(result == NO_ERROR,
                "Not enough command data for brTRANSACTION");
            if (result != NO_ERROR) break;
            
            Parcel buffer;
            buffer.ipcSetDataReference(
                reinterpret_cast<const uint8_t*>(tr.data.ptr.buffer),
                tr.data_size,
                reinterpret_cast<const size_t*>(tr.data.ptr.offsets),
                tr.offsets_size/sizeof(size_t), freeBuffer, this);
            
            const pid_t origPid = mCallingPid;
            const uid_t origUid = mCallingUid;
            
            mCallingPid = tr.sender_pid;
            mCallingUid = tr.sender_euid;
            
            int curPrio = getpriority(PRIO_PROCESS, mMyThreadId);
            if (gDisableBackgroundScheduling) {
                if (curPrio > ANDROID_PRIORITY_NORMAL) {
        // We have inherited a reduced priority from the caller, but do not
        // want to run in that state in this process.  The driver set our
        // priority already (though not our scheduling class), so bounce
        // it back to the default before invoking the transaction.
                    setpriority(PRIO_PROCESS, mMyThreadId, 
                       ANDROID_PRIORITY_NORMAL);
                }
            } else {
                if (curPrio >= ANDROID_PRIORITY_BACKGROUND) {
            // We want to use the inherited priority from the caller.
            // Ensure this thread is in the background scheduling class,
            // since the driver won't modify scheduling classes for us.
            // The scheduling group is reset to default by the caller
            // once this method returns after the transaction is complete.
                    set_sched_policy(mMyThreadId, SP_BACKGROUND);
                }
            }

            //ALOGI(">>>> TRANSACT from pid %d uid %d\\n",
            // mCallingPid, mCallingUid);
            
            Parcel reply;
            IF_LOG_TRANSACTIONS() {
                TextOutput::Bundle _b(alog);
                alog << "BR_TRANSACTION thr " << (void*)pthread_self()
                    << " / obj " << tr.target.ptr << " / code "
                    << TypeCode(tr.code) << ": " << indent << buffer
                    << dedent << endl
                    << "Data addr = "
                    << reinterpret_cast<const uint8_t*>(tr.data.ptr.buffer)
                    << ", offsets addr="
                    << reinterpret_cast<const size_t*>(tr.data.ptr.offsets)
                    << endl;
            }
            if (tr.target.ptr) {
                sp<BBinder> b((BBinder*)tr.cookie);
                //调用BBinder的transact方法 最终会调用服务类的onTransact方法
                const status_t error = b->transact(tr.code, buffer, 
                                        &reply, tr.flags);
                if (error < NO_ERROR) reply.setError(error);

            } else {
                const status_t error = the_context_object->transact(tr.code,
                                 buffer, &reply, tr.flags);
                if (error < NO_ERROR) reply.setError(error);
            }
            
            //ALOGI("<<<< TRANSACT from pid %d restore pid %d uid %d\\n",
            //     mCallingPid, origPid, origUid);
            
            if ((tr.flags & TF_ONE_WAY) == 0) {
                LOG_ONEWAY("Sending reply to %d!", mCallingPid);
                sendReply(reply, 0);
            } else {
                LOG_ONEWAY("NOT sending reply to %d!", mCallingPid);
            }
            
            mCallingPid = origPid;
            mCallingUid = origUid;

            IF_LOG_TRANSACTIONS() {
                TextOutput::Bundle _b(alog);
                alog << "BC_REPLY thr " << (void*)pthread_self() 
                     << " / obj "
                    << tr.target.ptr << ": " << indent << reply 
                    << dedent << endl;
            }
            
        }
        break;
    
    case BR_DEAD_BINDER:
        {
            BpBinder *proxy = (BpBinder*)mIn.readInt32();
            proxy->sendObituary();
            mOut.writeInt32(BC_DEAD_BINDER_DONE);
            mOut.writeInt32((int32_t)proxy);
        } break;
        
    case BR_CLEAR_DEATH_NOTIFICATION_DONE:
        {
            BpBinder *proxy = (BpBinder*)mIn.readInt32();
            proxy->getWeakRefs()->decWeak(proxy);
        } break;
        
    case BR_FINISHED:
        result = TIMED_OUT;
        break;
        
    case BR_NOOP:
        break;
        
    case BR_SPAWN_LOOPER:
        mProcess->spawnPooledThread(false);
        break;
        
    default:
        printf("*** BAD COMMAND %d received from Binder driver\\n", cmd);
        result = UNKNOWN_ERROR;
        break;
    }

    if (result != NO_ERROR) {
        mLastError = result;
    }
    
    return result;
}
```

 
<h2>Binder核心框架层</h2>
<p>Binder核心框架主要是IBinder及它的两个子类，即BBinder和BpBinder，分别代表了最基本的服务端及客户端。类图如下图所示：</p>
<a href="http://www.cloudchou.com/wp-content/uploads/2014/05/IBinder.png" target="_blank"><img src="http://www.cloudchou.com/wp-content/uploads/2014/05/IBinder-1024x514.png" alt="IBinder" width="1024" height="514" class="aligncenter size-large wp-image-531" /></a>
<ul>
<li>
 <h3>1)IBinder(frameworks/native/include/binder/IBinder.h)</h3>
 <p>IBinder有两个直接子类，代表服务端的BBinder和代表客户端的BpBinder。</p>
<p>重要方法说明(以下方法均是抽象方法)：</p>
<p>queryLocalInterface 用于检查IBinder是否实现了descriptor指定的接口，若实现了则会返回它的指针</p>
<p>getInterfaceDescriptor 用于返回IBinder提供的接口名字</p>
<p>transact 客户端用该方法向服务端提交数据，服务端实现该方法以处理客户端请求。</p>

</li>
<li>
 <h3>2)BBinder(frameworks/native/include/binder/Binder.h)</h3>
 <p>BBinder代表binder service服务端，最终声明的binder 服务类将间接从该类继承，它实现了IBinder声明的transact方法，转调留给子类实现onTrasact的方法。</p>
```cpp
 status_t BBinder::transact(
    uint32_t code, const Parcel& data, Parcel* reply, uint32_t flags)
{
    data.setDataPosition(0);

    status_t err = NO_ERROR;
    switch (code) {
        case PING_TRANSACTION:
            reply->writeInt32(pingBinder());
            break;
        default:
            err = onTransact(code, data, reply, flags);
            break;
    }

    if (reply != NULL) {
        reply->setDataPosition(0);
    }

    return err;
}
```
</li>
<li>
 <h3>3)BpBinder(frameworks/native/include/binder/BpBinder.h)</h3>
 <p>客户端使用servicemananger查询服务时实际上是先得到一个句柄handle，然后ProcessState的getStrongProxyForHandle函数里利用句柄handle建立BpBinder对象，再转为IBinder指针，代理类便是通过该指针向服务端请求。</p>
</li>
</ul>
 
<h2>参考资料</h2>
<p>书《Android系统原理及开发要点详解》 第4章Android的底层库和程序</p>
<p>书《Android技术内幕 系统卷》 第3章 Android的IPC机制―Binder</p>
