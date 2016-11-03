---
  id: 858
  title: '深入理解Activity启动流程(四)&#8211;Activity Task的调度算法'
  date: 2015-05-25T09:12:26+08:00
  author: cloud
  layout: post
  guid: http://www.cloudchou.com/?p=858
  permalink: /android/post-858.html
  views:
    - 3367
  categories:
    - Android
    - 个人总结
  tags:
    - activity 启动分析
    - activity 启动流程
    - activity启动过程
    - android activity task
    - android actvity启动
  ---
<p>本系列博客将详细阐述Activity的启动流程，这些博客基于Cm 10.1源码研究。</p>
 <ul>
 <li><a href="http://www.cloudchou.com/android/post-788.html" target="_blank">深入理解Activity启动流程(一)--Activity启动的概要流程</a></li>
 <li><a href="http://www.cloudchou.com/android/post-793.html" target="_blank">深入理解Activity启动流程(二)--Activity启动相关类的类图</a></li>
 <li><a href="http://www.cloudchou.com/android/post-805.html" target="_blank">深入理解Activity启动流程(三)--Activity启动的详细流程1</a></li>
 <li><a href="http://www.cloudchou.com/android/post-815.html" target="_blank">深入理解Activity启动流程(三)--Activity启动的详细流程2</a></li>
 </ul>
 
 <p>前面两篇博客介绍了Activity的详细启动流程，提到ActivityStack类的startActivityUncheckedLocked方法负责调度ActivityRecord和Task，并且调度算法非常复杂，需结合实际场景分析调度算法。本篇博客将介绍startActivityUncheckedLocked方法的具体实现，本结合实际场景分析调度算法。</p>
 <h2>startActivityUncheckedLocked方法的具体实现</h2>
 ```java
 final int startActivityUncheckedLocked(ActivityRecord r,
         ActivityRecord sourceRecord, int startFlags, boolean doResume,
         Bundle options) {
     //... 
     //如果从Launcher程序启动应用，launchFlags为
     //FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED 
     //否则一般情况下launcheFlags为0，除非启动Activity时设置了特殊的flag
     int launchFlags = intent.getFlags();      
     //启动Activity时默认不会设置FLAG_ACTIVITY_PREVIOUS_IS_TOP 
     //故此notTop默认情况下会是null
     ActivityRecord notTop = (launchFlags&Intent.FLAG_ACTIVITY_PREVIOUS_IS_TOP)
             != 0 ? r : null; 
     //默认情况下startFlags不会设置START_FLAG_ONLY_IF_NEEDED
     // If the onlyIfNeeded flag is set, then we can do this if the activity
     // being launched is the same as the one making the call...  or, as
     // a special case, if we do not know the caller then we count the
     // current top activity as the caller.
     if ((startFlags&ActivityManager.START_FLAG_ONLY_IF_NEEDED) != 0) {
          //...默认情况下这里的代码不会执行
     }    
     //根据被启动的Activity和sourceRecord设置标志
     //launchFlags |= Intent.FLAG_ACTIVITY_NEW_TASK
     //如果从通知栏启动应用 sourceRecord == null
     if (sourceRecord == null) {
         // This activity is not being started from another...  in this
         // case we -always- start a new task.
         if ((launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) == 0) {
             Slog.w(TAG, "startActivity called from non-Activity context;" 
                   +"forcing Intent.FLAG_ACTIVITY_NEW_TASK for: "
                   + intent);
             launchFlags |= Intent.FLAG_ACTIVITY_NEW_TASK;
         }
     } else if (sourceRecord.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
         // The original activity who is starting us is running as a single
         // instance...  this new activity it is starting must go on its
         // own task.
         launchFlags |= Intent.FLAG_ACTIVITY_NEW_TASK;
     } else if (r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK) {
         // The activity being started is a single instance...  it always
         // gets launched into its own task.
         launchFlags |= Intent.FLAG_ACTIVITY_NEW_TASK;
     }
     
   //一般情况下r.resultTo 不为null，它是启动该Activity的Activity，
   //如果从通知栏启动Activity 则r.result为null
   if (r.resultTo != null && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
       //...
       r.resultTo = null;
   }       
     //addingToTask 如果为true表示正在添加至某个task，
     //  后续需要将r添加至sourceRecord所在的task
     boolean addingToTask = false;
     //movedHome表示是否移动home task
     boolean movedHome = false;
     //reuseTask 如果不为null,则表示已存在task，会重用这个task，
     //                      但是这个Task里的所有Activity会被清除掉,
     //                      需要将r加入这个task  
     TaskRecord reuseTask = null;       
     if (((launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0 &&
             (launchFlags&Intent.FLAG_ACTIVITY_MULTIPLE_TASK) == 0)
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
         //从通知栏启动时r.resultTo == null
         //如果launchFlags设置了FLAG_ACTIVITY_NEW_TASK,r.resultTo也会为null
         if (r.resultTo == null) {
             //查找ActivityRecord栈，看要启动的activity是否已有相关task，
             //如果已经有相关task，则不需要创建新的task，可以使用已有的task
             //如果要启动的activity的启动模式是LAUNCH_SINGLE_INSTANCE，
             //则使用快速查找方法findTaskLocked，否则使用慢速查找方法findActivityLocked
             //因为如果启动模式是LAUNCH_SINGLE_INSTANCE,则这个activity只会在一个单独的Task里
             //故此查找时，可以以task为单位进行查找和比较，这样比较快
             //查找得到的结果taskTop是相关task的栈顶的ActivityRecord               
             // See if there is a task to bring to the front.  If this is
             // a SINGLE_INSTANCE activity, there can be one and only one
             // instance of it in the history, and it is always in its own
             // unique task, so we do a special search.
             ActivityRecord taskTop = r.launchMode != ActivityInfo.LAUNCH_SINGLE_INSTANCE
                     ? findTaskLocked(intent, r.info)
                     : findActivityLocked(intent, r.info);
             //找到了相关task        
             if (taskTop != null) {
                 //重设task的intent
                 if (taskTop.task.intent == null) {
                     // This task was started because of movement of
                     // the activity based on affinity...  now that we
                     // are actually launching it, we can assign the
                     // base intent.
                     taskTop.task.setIntent(intent, r.info);
                 }
                 //如果目标task不在栈顶，
                 //则先将Home task移动到栈顶(实际上只有当启动Activity设置的Flag同时设置了
                 //FLAG_ACTIVITY_TASK_ON_HOME和FLAG_ACTIVITY_NEW_TASK才会移动home task，
                 //否则不会移动home task)，
                 //然后再将目标task移动到栈顶
                 // If the target task is not in the front, then we need
                 // to bring it to the front...  except...  well, with
                 // SINGLE_TASK_LAUNCH it's not entirely clear.  We'd like
                 // to have the same behavior as if a new instance was
                 // being started, which means not bringing it to the front
                 // if the caller is not itself in the front.
                 ActivityRecord curTop = topRunningNonDelayedActivityLocked(notTop);
                 if (curTop != null && curTop.task != taskTop.task) {
                     r.intent.addFlags(Intent.FLAG_ACTIVITY_BROUGHT_TO_FRONT);
                     boolean callerAtFront = sourceRecord == null
                             || curTop.task == sourceRecord.task;
                     if (callerAtFront) {
                         // We really do want to push this one into the
                         // user's face, right now.
                         movedHome = true;
                         moveHomeToFrontFromLaunchLocked(launchFlags);
                         moveTaskToFrontLocked(taskTop.task, r, options);
                         options = null;
                     }
                 }
                 //如果launchFlags设置了FLAG_ACTIVITY_RESET_TASK_IF_NEEDED，则会重置task 
                 //从Launcher应用程序启动应用会设置FLAG_ACTIVITY_RESET_TASK_IF_NEEDED       
                 // If the caller has requested that the target task be
                 // reset, then do so.
                 if ((launchFlags&Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED) != 0) {
                     taskTop = resetTaskIfNeededLocked(taskTop, r);
                 }
                 //... 一般情况下startFlags 不会设置 START_FLAG_ONLY_IF_NEEDED
                 if ((startFlags&ActivityManager.START_FLAG_ONLY_IF_NEEDED)  != 0) {
                     //...
                 }
                 // ==================================                                 
                 //默认情况下不会设置 Intent.FLAG_ACTIVITY_CLEAR_TASK
                 if ((launchFlags &
                         (Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK))
                         == (Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK)) {
                     // The caller has requested to completely replace any
                     // existing task with its new activity.  Well that should
                     // not be too hard...
                     reuseTask = taskTop.task;
                     performClearTaskLocked(taskTop.task.taskId);
                     reuseTask.setIntent(r.intent, r.info);
                 } else if ((launchFlags&Intent.FLAG_ACTIVITY_CLEAR_TOP) != 0
                         || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
                         || r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
                     //默认情况下launchFlags不会设置FLAG_ACTIVITY_CLEAR_TOP
                     //但是如果被启动的activity的启动模式是singleTask或者singleInstance，
                     //也会进入该分支
                     // In this situation we want to remove all activities
                     // from the task up to the one being started.  In most
                     // cases this means we are resetting the task to its
                     // initial state.
                     //清除r所在的task 在r之上的所有activity, 
                     //该task里r和在r下的activity不会被清除
                     ActivityRecord top = performClearTaskLocked(
                             taskTop.task.taskId, r, launchFlags);
                     if (top != null) {
                         if (top.frontOfTask) {
                             // Activity aliases may mean we use different
                             // intents for the top activity, so make sure
                             // the task now has the identity of the new
                             // intent.
                             top.task.setIntent(r.intent, r.info);
                         }
                         logStartActivity(EventLogTags.AM_NEW_INTENT, r, top.task);
                         top.deliverNewIntentLocked(callingUid, r.intent);
                     } else {
                         // A special case: we need to
                         // start the activity because it is not currently
                         // running, and the caller has asked to clear the
                         // current task to have this activity at the top.
                         addingToTask = true;
                         // Now pretend like this activity is being started
                         // by the top of its task, so it is put in the
                         // right place.
                         sourceRecord = taskTop;
                     }
                 } else if (r.realActivity.equals(taskTop.task.realActivity)) {
                     // In this case the top activity on the task is the
                     // same as the one being launched, so we take that
                     // as a request to bring the task to the foreground.
                     // If the top activity in the task is the root
                     // activity, deliver this new intent to it if it
                     // desires.
                     if (((launchFlags&Intent.FLAG_ACTIVITY_SINGLE_TOP) != 0
                             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TOP)
                             && taskTop.realActivity.equals(r.realActivity)) {
                         logStartActivity(EventLogTags.AM_NEW_INTENT, r, taskTop.task);
                         if (taskTop.frontOfTask) {
                             taskTop.task.setIntent(r.intent, r.info);
                         }
                         taskTop.deliverNewIntentLocked(callingUid, r.intent);
                     } else if (!r.intent.filterEquals(taskTop.task.intent)) {
                         // In this case we are launching the root activity
                         // of the task, but with a different intent.  We
                         // should start a new instance on top.
                         addingToTask = true;
                         sourceRecord = taskTop;
                     }
                 } else if ((launchFlags&Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED) == 0) {
                     // In this case an activity is being launched in to an
                     // existing task, without resetting that task.  This
                     // is typically the situation of launching an activity
                     // from a notification or shortcut.  We want to place
                     // the new activity on top of the current task.
                     addingToTask = true;
                     sourceRecord = taskTop;
                 } else if (!taskTop.task.rootWasReset) {
                     //进入该分支的情况比较少
                     // In this case we are launching in to an existing task
                     // that has not yet been started from its front door.
                     // The current task has been brought to the front.
                     // Ideally, we'd probably like to place this new task
                     // at the bottom of its stack, but that's a little hard
                     // to do with the current organization of the code so
                     // for now we'll just drop it.
                     taskTop.task.setIntent(r.intent, r.info);
                 }   
                 // ================================== end
                 //如果没有正在添加至某个Task， 并且不用加入一个已清除所有Activity的Task
                 //此时只需要显示栈顶Activity即可              
                 if (!addingToTask && reuseTask == null) {
                     // We didn't do anything...  but it was needed (a.k.a., client
                     // don't use that intent!)  And for paranoia, make
                     // sure we have correctly resumed the top activity.
                     if (doResume) {
                         resumeTopActivityLocked(null, options);
                     } else {
                         ActivityOptions.abort(options);
                     }
                     return ActivityManager.START_TASK_TO_FRONT;
                 }
             }
         }
     } 
     //...  
     if (r.packageName != null) {
         // If the activity being launched is the same as the one currently
         // at the top, then we need to check if it should only be launched
         // once.
         ActivityRecord top = topRunningNonDelayedActivityLocked(notTop);
         if (top != null && r.resultTo == null) {
             if (top.realActivity.equals(r.realActivity) && top.userId == r.userId) {
                 if (top.app != null && top.app.thread != null) {
                     if ((launchFlags&Intent.FLAG_ACTIVITY_SINGLE_TOP) != 0
                         || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TOP
                         || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK) {
                         //singleTop启动模式或者singleTask启动模式，
                         //并且task栈顶的activity是要启动的activity，则先显示Activity
                         //然后调用该Activity的onNewIntent方法
                         logStartActivity(EventLogTags.AM_NEW_INTENT, top, top.task);
                         // For paranoia, make sure we have correctly
                         // resumed the top activity.
                         //先显示Activity
                         if (doResume) {
                             resumeTopActivityLocked(null);
                         }
                         ActivityOptions.abort(options);
                         if ((startFlags&ActivityManager.START_FLAG_ONLY_IF_NEEDED) != 0) {
                             // We don't need to start a new activity, and
                             // the client said not to do anything if that
                             // is the case, so this is it!
                             return ActivityManager.START_RETURN_INTENT_TO_CALLER;
                         }
                         //然后调用已显示activity的onNewIntent方法
                         top.deliverNewIntentLocked(callingUid, r.intent);
                         return ActivityManager.START_DELIVERED_TO_TOP;
                     }
                 }
             }
         }
 
     } else {
         if (r.resultTo != null) {
             sendActivityResultLocked(-1,
                     r.resultTo, r.resultWho, r.requestCode,
                 Activity.RESULT_CANCELED, null);
         }
         ActivityOptions.abort(options);
         return ActivityManager.START_CLASS_NOT_FOUND;
     }
     boolean newTask = false;
     boolean keepCurTransition = false;
     // Should this be considered a new task?
     if (r.resultTo == null && !addingToTask
             && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
         if (reuseTask == null) {
              //创建新的task
             // todo: should do better management of integers.
             mService.mCurTask++;
             if (mService.mCurTask <= 0) {
                 mService.mCurTask = 1;
             }
             r.setTask(new TaskRecord(mService.mCurTask, r.info, intent), null, true);
             if (DEBUG_TASKS) Slog.v(TAG, "Starting new activity " + r
                     + " in new task " + r.task);
         } else {
            //重复利用先前的task，该task里的所有acitivity已经被清空
             r.setTask(reuseTask, reuseTask, true);
         }
         newTask = true;
         if (!movedHome) {
             moveHomeToFrontFromLaunchLocked(launchFlags);
         } 
     } else if (sourceRecord != null) {
         if (!addingToTask &&
                 (launchFlags&Intent.FLAG_ACTIVITY_CLEAR_TOP) != 0) {
             // In this case, we are adding the activity to an existing
             // task, but the caller has asked to clear that task if the
             // activity is already running.
             //清除r所在task在r之上的所有task，如果r不在task里，则返回的top为null
             ActivityRecord top = performClearTaskLocked(
                     sourceRecord.task.taskId, r, launchFlags);
             keepCurTransition = true;
             if (top != null) {
                 logStartActivity(EventLogTags.AM_NEW_INTENT, r, top.task);
                 //先调用onNewIntent方法 然后再显示
                 top.deliverNewIntentLocked(callingUid, r.intent);
                 // For paranoia, make sure we have correctly
                 // resumed the top activity.
                 if (doResume) {
                     resumeTopActivityLocked(null);
                 }
                 ActivityOptions.abort(options);
                 return ActivityManager.START_DELIVERED_TO_TOP;
             }
         } else if (!addingToTask &&
                 (launchFlags&Intent.FLAG_ACTIVITY_REORDER_TO_FRONT) != 0) {
             //将栈里已有的activity移到栈顶
             // In this case, we are launching an activity in our own task
             // that may already be running somewhere in the history, and
             // we want to shuffle it to the front of the stack if so.
             int where = findActivityInHistoryLocked(r, sourceRecord.task.taskId);
             if (where >= 0) {
                 ActivityRecord top = moveActivityToFrontLocked(where);
                 logStartActivity(EventLogTags.AM_NEW_INTENT, r, top.task);
                 top.updateOptionsLocked(options);
                 top.deliverNewIntentLocked(callingUid, r.intent);
                 if (doResume) {
                     resumeTopActivityLocked(null);
                 }
                 return ActivityManager.START_DELIVERED_TO_TOP;
             }
         }
         // An existing activity is starting this new activity, so we want
         // to keep the new one in the same task as the one that is starting
         // it.
         //同一个应用程序里的Activity A和Activity B，A可跳转至B，没有设置taskAffinity
         //B的启动模式为singleTask，从A跳转至B时，B和A会在同一个task里
         //该情况下会执行到这里的代码，将B的task设置为和A一样的task
         r.setTask(sourceRecord.task, sourceRecord.thumbHolder, false);
         if (DEBUG_TASKS) Slog.v(TAG, "Starting new activity " + r
                 + " in existing task " + r.task); 
     } else {
         // This not being started from an existing activity, and not part
         // of a new task...  just put it in the top task, though these days
         // this case should never happen.
         final int N = mHistory.size();
         ActivityRecord prev =
             N > 0 ? mHistory.get(N-1) : null;
         r.setTask(prev != null
                 ? prev.task
                 : new TaskRecord(mService.mCurTask, r.info, intent), null, true);
         if (DEBUG_TASKS) Slog.v(TAG, "Starting new activity " + r
                 + " in new guessed " + r.task);
     }  
     mService.grantUriPermissionFromIntentLocked(callingUid, r.packageName,
             intent, r.getUriPermissionsLocked()); 
     if (newTask) {
         EventLog.writeEvent(EventLogTags.AM_CREATE_TASK, r.userId, r.task.taskId);
     }
     logStartActivity(EventLogTags.AM_CREATE_ACTIVITY, r, r.task);
     startActivityLocked(r, newTask, doResume, keepCurTransition, options);
     return ActivityManager.START_SUCCESS;
 }
 ```
 
 <h2>实际场景分析</h2>
 <p>实际场景1:</p>
 <p>应用内有两个Activity,A和B,A为第应用入口Activity，从A可跳转至B，A和B的启动模式都为standard</p>
 <p>1)从Launcher程序第1次启动应用时的任务调度情况:</p>
 <p>  任务调度时会创建新task并将新的ActivityRecord加入这个新的task</p>
 <p>2)然后跳转至应用内Activity时的任务调度情况:</p>
 <p>  任务调度时会将新的ActivityRecord加入已有的task</p>
 <p>3)然后按Home键，再打开应用程序时的调度情况:</p>
 <p>  任务调度时会先找到已有的相关task，并显示栈顶的Activity</p>
 <p>1)从Launcher程序第1次启动应用时</p>
 <p>会创建新task并将新的ActivityRecord加入这个新的task，任务调度执行如下所示:</p>
 ```java
 final int startActivityUncheckedLocked(ActivityRecord r,
         ActivityRecord sourceRecord, int startFlags, boolean doResume,
         Bundle options) {
     //...
     //launchFlags为FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED
     int launchFlags = intent.getFlags();
    //... 
    //没设置FLAG_ACTIVITY_PREVIOUS_IS_TOP，故此notTop为null        
     ActivityRecord notTop = (launchFlags&Intent.FLAG_ACTIVITY_PREVIOUS_IS_TOP)
             != 0 ? r : null;
    //startFlags未设置ActivityManager.START_FLAG_ONLY_IF_NEEDED
    //...  
    //sourceRecord为Launcher应用的Activity  launcher应用activity的启动模式为singleTask
    // 故此下面的3个条件分支的内容都不会执行  
     if (sourceRecord == null) {
         //... 
     } else if (sourceRecord.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
          //...
     } else if (r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK) {
         //... 
     }
     //... 
     //r.resultTo不为null， launchFlags设置了FLAG_ACTIVITY_NEW_TASK，需要将r.resultTo置为null
     if (r.resultTo != null && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
         //... 
         r.resultTo = null;
     }         
     boolean addingToTask = false;
     boolean movedHome = false;
     TaskRecord reuseTask = null;
     //因为launchFlags为FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED
     //故此下面的条件会满足， 也就是说只要从Launcher程序启动应用，下面这个条件肯定会满足
     if (((launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0 &&
             (launchFlags&Intent.FLAG_ACTIVITY_MULTIPLE_TASK) == 0)
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
         //... 
         if (r.resultTo == null) {
             //因为应用被第一次启动，故此找不到相关task，taskTop则为null
             ActivityRecord taskTop = r.launchMode != ActivityInfo.LAUNCH_SINGLE_INSTANCE
                     ? findTaskLocked(intent, r.info)
                     : findActivityLocked(intent, r.info);
             if (taskTop != null) {
               //... 这里面的内容不会执行
             }     
         }
     }
    //...
    //r.packageName != null
     if (r.packageName != null) {
         //如果被启动的Activity正好是栈顶的Activity，
         //并且被启动的Activity启动模式是singleTop或者singleTask，
         //则不用将新的ActivityRecord加入到栈里
         //top Activity为Launcher应用的Activity 
         ActivityRecord top = topRunningNonDelayedActivityLocked(notTop);
         if (top != null && r.resultTo == null) {
             //top.realActivity.equals(r.realActivity)不满足
             if (top.realActivity.equals(r.realActivity) && top.userId == r.userId) {
                 //... 这里的代码不会被执行 
             }
         }
 
     } else {
         //...
     } 
     boolean newTask = false;
     boolean keepCurTransition = false;
     // 此时 r.resultTo为null addingToTask为false  launchFlags设置了FLAG_ACTIVITY_NEW_TASK
     if (r.resultTo == null && !addingToTask
             && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
         if (reuseTask == null) {
             // todo: should do better management of integers.
             mService.mCurTask++;
             if (mService.mCurTask <= 0) {
                 mService.mCurTask = 1;
             }
             //创建新task
             r.setTask(new TaskRecord(mService.mCurTask, r.info, intent), null, true);
             if (DEBUG_TASKS) Slog.v(TAG, "Starting new activity " + r
                     + " in new task " + r.task);
         } else {
            //...这里的代码会执行
         }
         newTask = true;
         if (!movedHome) {
             moveHomeToFrontFromLaunchLocked(launchFlags);
         }
         
     } else if (sourceRecord != null) {
          //... 这里的代码不会被执行
     } else {
        //...这里的代码不会被执行
     }
     //... 
     startActivityLocked(r, newTask, doResume, keepCurTransition, options);
     return ActivityManager.START_SUCCESS;
 }
 ```
 
 <p>2)跳转至应用内Activity时</p>
 <p>会将新的ActivityRecord加入已有的task，任务调度执行如下所示:</p>
 ```java
 final int startActivityUncheckedLocked(ActivityRecord r,
         ActivityRecord sourceRecord, int startFlags, boolean doResume,
         Bundle options) {
     //此时launchFlags为0 
     int launchFlags = intent.getFlags();
     //notTop为null    
     ActivityRecord notTop = (launchFlags&Intent.FLAG_ACTIVITY_PREVIOUS_IS_TOP)
             != 0 ? r : null;
     //startFlags未设置ActivityManager.START_FLAG_ONLY_IF_NEEDED
     //...     
     if (sourceRecord == null) {
        //...这里的代码不会被执行
     } else if (sourceRecord.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
       //...这里的代码不会被执行   
     } else if (r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK) {
       //...这里的代码不会被执行     
     }
     //r.resultTo != null 但是launchFlags未设置FLAG_ACTIVITY_NEW_TASK
     if (r.resultTo != null && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
        //... 这里的代码不执行  
     }
     boolean addingToTask = false;
     boolean movedHome = false;
     TaskRecord reuseTask = null;
     //launchFlags为0 r的启动模式为standard 故此下面的逻辑都不会执行
     if (((launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0 &&
             (launchFlags&Intent.FLAG_ACTIVITY_MULTIPLE_TASK) == 0)
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
         //... 这里的代码不执行
     }
    //...
     if (r.packageName != null) {
         //top 是ActivityA 的ActivityRecord，
         //但是被启动的Activity和top不是同一个Activity
         ActivityRecord top = topRunningNonDelayedActivityLocked(notTop);
         if (top != null && r.resultTo == null) {
             if (top.realActivity.equals(r.realActivity) && top.userId == r.userId) {
                  //...这里的代码不执行
             }
         }
 
     } else {
         //...这里的代码不执行
     }
     boolean newTask = false;
     boolean keepCurTransition = false;
     //此时 r.resultTo !=null  sourceRecord != null addingToTask=false
     if (r.resultTo == null && !addingToTask
             && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
         //...这里的代码不执行         
     } else if (sourceRecord != null) {
         if (!addingToTask &&
                 (launchFlags&Intent.FLAG_ACTIVITY_CLEAR_TOP) != 0) {
              //... 这里的代码不执行
         } else if (!addingToTask &&
                 (launchFlags&Intent.FLAG_ACTIVITY_REORDER_TO_FRONT) != 0) {
              //... 这里的代码不执行 
         }
         //添加到现有的task 
         r.setTask(sourceRecord.task, sourceRecord.thumbHolder, false);
         //... 
     } else {
         //... 这里的代码不执行 
     }
     //...
     return ActivityManager.START_SUCCESS;
 }
 ```
 <p>3)然后按Home键，再打开应用程序</p>
 <p>此时会先找到已有的相关task，并显示栈顶的Activity，任务调度执行如下所示:</p>
 ```java
 final int startActivityUncheckedLocked(ActivityRecord r,
         ActivityRecord sourceRecord, int startFlags, boolean doResume,
         Bundle options) {
     //...
     //launchFlags为FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED 
     int launchFlags = intent.getFlags();
     //notTop为null    
     ActivityRecord notTop = (launchFlags&Intent.FLAG_ACTIVITY_PREVIOUS_IS_TOP)
             != 0 ? r : null;
     //startFlags未设置ActivityManager.START_FLAG_ONLY_IF_NEEDED
     //...         
     if (sourceRecord == null) {
        //...这里的代码不会被执行
     } else if (sourceRecord.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
         //...这里的代码不会被执行  
     } else if (r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK) {
        //...这里的代码不会被执行 
     }
     //此时 r.resultTo != null launchFlags设置了FLAG_ACTIVITY_NEW_TASK
     if (r.resultTo != null && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
         //...
         r.resultTo = null;
     } 
     boolean addingToTask = false;
     boolean movedHome = false;
     TaskRecord reuseTask = null;
     //此时launchFlags设置了FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED 
     if (((launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0 &&
             (launchFlags&Intent.FLAG_ACTIVITY_MULTIPLE_TASK) == 0)
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
         //此时 r.resultTo == null
         if (r.resultTo == null) {
             //此时已有相关task，并且task 栈的栈顶是Activity B的ActivityRecord
             //故此taskTop为Activity B的ActivityRecord 
             ActivityRecord taskTop = r.launchMode != ActivityInfo.LAUNCH_SINGLE_INSTANCE
                     ? findTaskLocked(intent, r.info)
                     : findActivityLocked(intent, r.info);
             if (taskTop != null) {
                 //... 
                 // 此时curTop是Launcher应用的Activity的ActivityRecord  
                 ActivityRecord curTop = topRunningNonDelayedActivityLocked(notTop);
                 if (curTop != null && curTop.task != taskTop.task) {
                     r.intent.addFlags(Intent.FLAG_ACTIVITY_BROUGHT_TO_FRONT);
                     //此时Launcher应用的task在栈顶，故此callerAtFront为true，
                     //此时会把被启动的应用的task移至栈顶
                     boolean callerAtFront = sourceRecord == null
                             || curTop.task == sourceRecord.task;
                     if (callerAtFront) {
                         // We really do want to push this one into the
                         // user's face, right now.
                         movedHome = true;
                         moveHomeToFrontFromLaunchLocked(launchFlags);
                         moveTaskToFrontLocked(taskTop.task, r, options);
                         options = null;
                     }
                 }
                 //此时launchFlags设置了FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED
                 //此时需要重置task 重置完后 taskTop为ActivityB的ActivityRecord   
                 if ((launchFlags&Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED) != 0) {
                     taskTop = resetTaskIfNeededLocked(taskTop, r);
                 }
                 //startFlags为0
                 if ((startFlags&ActivityManager.START_FLAG_ONLY_IF_NEEDED)  != 0) {
                     //... 这些代码都不会被执行 
                 } 
                 //根据launchFlags和被启动的activity的信息 设置resueTask addingTask变量的值                  
                 //没设置 Intent.FLAG_ACTIVITY_CLEAR_TASK
                 if ((launchFlags &
                           (Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK))
                           == (Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK)) {
                       //... 这些代码都不会被执行  
                  } else if ((launchFlags&Intent.FLAG_ACTIVITY_CLEAR_TOP) != 0
                           || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
                           || r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
                       //... 这些代码都不会被执行  
                  } else if (r.realActivity.equals(taskTop.task.realActivity)) {
                       //... 这些代码都不会被执行   
                  } else if ((launchFlags&Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED) == 0) {
                        //因为从Launcher程序启动时launchFlags设置了FLAG_ACTIVITY_RESET_TASK_IF_NEEDED
                        //所以不会进入该分支
                        //... 这些代码都不会被执行   
                   } else if (!taskTop.task.rootWasReset) {
                        //... 这些代码都不会被执行    
                   }  
                   //此时addingToTask为false，reuseTask为null，故此显示栈顶Actvity即可
                   if (!addingToTask && reuseTask == null) {
                       // We didn't do anything...  but it was needed (a.k.a., client
                       // don't use that intent!)  And for paranoia, make
                       // sure we have correctly resumed the top activity.
                       if (doResume) {
                           resumeTopActivityLocked(null, options);
                       } else {
                           ActivityOptions.abort(options);
                       }
                       return ActivityManager.START_TASK_TO_FRONT;
                   } 
             }
         }
     }
    //... 以下代码都不会被执行    
 }
 ``` 
 
 
 <p>实际场景2:</p>
 <p>应用内有两个Activity,A和B,A为第应用入口Activity，从A可跳转至B，A的启动模式都为standard，B的启动模式为singleTop</p>
 <p>此时已从Launchenr程序打开应用，启动了Actvity A,再从A跳转至B，此时的任务调度情况:</p>
 <p>此时不会创建新的Task，而是将B的ActivityRecord加入到A所在的task里</p>
 <p>任务调度执行如下所示:</p>
 ```java
 final int startActivityUncheckedLocked(ActivityRecord r,
         ActivityRecord sourceRecord, int startFlags, boolean doResume,
         Bundle options) {
     //...  
     //此时launcheFlags为0
     int launchFlags = intent.getFlags();      
     //notTop为null
     ActivityRecord notTop = (launchFlags&Intent.FLAG_ACTIVITY_PREVIOUS_IS_TOP)
             != 0 ? r : null;
     //默认情况下startFlags不会设置START_FLAG_ONLY_IF_NEEDED    
     if ((startFlags&ActivityManager.START_FLAG_ONLY_IF_NEEDED) != 0) {
         //...这里的代码不会执行
     }    
     //r.launchMode = ActivityInfo.LAUNCH_SINGLE_TASK 
     if (sourceRecord == null) {
        //这里的代码不会执行  
     } else if (sourceRecord.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
         //这里的代码不会执行    
     } else if (r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK) {
         launchFlags |= Intent.FLAG_ACTIVITY_NEW_TASK;
     }
     
     //此时r.resultTo!=null launchFlags设置了Intent.FLAG_ACTIVITY_NEW_TASK
     if (r.resultTo != null && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
        //...
         r.resultTo = null;
     }       
     //addingToTask如果为true表示正在添加至某个task，后续需要将r添加至sourceRecord所在的task
     boolean addingToTask = false;
     //movedHome表示是否移动home task
     boolean movedHome = false; 
     TaskRecord reuseTask = null;       
     if (((launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0 &&
             (launchFlags&Intent.FLAG_ACTIVITY_MULTIPLE_TASK) == 0)
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
             || r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
         //此时 r.resultTo = null
         if (r.resultTo == null) {
             //此时找到的taskTop是Activity A的ActivityRecord，
             //因为Actvity B和A的ActivityRecord所在的Task是相关的
             ActivityRecord taskTop = r.launchMode != ActivityInfo.LAUNCH_SINGLE_INSTANCE
                     ? findTaskLocked(intent, r.info)
                     : findActivityLocked(intent, r.info);
             //找到了相关task        
             if (taskTop != null) {
                 //重设task的intent
                 if (taskTop.task.intent == null) {
                      //...
                 }
                 //此时找到的task已在栈顶
                 ActivityRecord curTop = topRunningNonDelayedActivityLocked(notTop);
                 if (curTop != null && curTop.task != taskTop.task) {
                     //... 这里的代码不会执行 
                 }
                 //launchFlags为0
                 if ((launchFlags&Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED) != 0) {
                     taskTop = resetTaskIfNeededLocked(taskTop, r);
                 }
                 //... 一般情况下startFlags 不会设置 START_FLAG_ONLY_IF_NEEDED
                 if ((startFlags&ActivityManager.START_FLAG_ONLY_IF_NEEDED)  != 0) {
                     //...
                 } 
                 
                 // ==================== begin
                 // launchFlags此时为0
                 if ((launchFlags &
                         (Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK))
                         == (Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK)) {
                      //...这里的代码不执行
                 } else if ((launchFlags&Intent.FLAG_ACTIVITY_CLEAR_TOP) != 0
                         || r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
                         || r.launchMode == ActivityInfo.LAUNCH_SINGLE_INSTANCE) {
                     // r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK
                     // 故此会进入该分支
                     //因为B还从未启动，故此得到的top为null
                     ActivityRecord top = performClearTaskLocked(
                             taskTop.task.taskId, r, launchFlags);
                     if (top != null) {
                         //...这里的代码不执行 
                     } else { 
                         addingToTask = true; 
                         sourceRecord = taskTop;
                     }
                 } else if (r.realActivity.equals(taskTop.task.realActivity)) {
                      //...这里的代码不执行 
                 } else if ((launchFlags&Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED) == 0) {
                      //...这里的代码不执行 
                 } else if (!taskTop.task.rootWasReset) {
                      //...这里的代码不执行 
                 }
                 // ==================== end     
                 
                 // 此时 addingToTask为true          
                 if (!addingToTask && reuseTask == null) {
                      //...这里的代码不执行 
                 }
             }
         }
     } 
     //... 
 
     if (r.packageName != null) { 
         ActivityRecord top = topRunningNonDelayedActivityLocked(notTop);
         if (top != null && r.resultTo == null) {
             //此时task还没有B的ActivityRecord，故此不会进入下述分支
             if (top.realActivity.equals(r.realActivity) && top.userId == r.userId) {
                  //...这里的代码不执行
             }
         }
 
     } else {
            //...这里的代码不执行
     }
 
     boolean newTask = false;
     boolean keepCurTransition = false;
 
     // 此时 r.resultTo == null addingToTask为true sourceRecord != null
     if (r.resultTo == null && !addingToTask
             && (launchFlags&Intent.FLAG_ACTIVITY_NEW_TASK) != 0) {
          //...这里的代码不执行 
     } else if (sourceRecord != null) {
         if (!addingToTask &&
                 (launchFlags&Intent.FLAG_ACTIVITY_CLEAR_TOP) != 0) {
                //...这里的代码不执行 
         } else if (!addingToTask &&
                 (launchFlags&Intent.FLAG_ACTIVITY_REORDER_TO_FRONT) != 0) {
                //...这里的代码不执行 
         }
         //将B的ActivityRecord加入A的ActivityRecord所在的Task里 
         r.setTask(sourceRecord.task, sourceRecord.thumbHolder, false);
         //... 
     } else {
          //...这里的代码不执行
     }
     //...
     startActivityLocked(r, newTask, doResume, keepCurTransition, options);
     return ActivityManager.START_SUCCESS;
 }
 ```
 <h2>总结</h2>
 <p>从上面的分析可以看出来，Activity和Task的调度算法非常复杂，需结合实际场景才好分析，只有这样才知道是否需要新建Task,还是将新的ActivityRecord加入到已有的Task里，不过我们如果能理解启动模式的一些特点，对理解调度算法会有很大帮助。</p>
 <p>大家可以结合下述场景分析调度算法:</p>
 <p>1.从通知栏启动Activity:</p>
 <p>假设应用有Activity A ，Activity A已启动，</p>
 <p>此时发了一个通知，该通知用于启动Activity A，启动Activity A时不加任何特殊flag</p>
 <p>点击通知，针对以下情况对任务调度情况进行分析:</p>
 <p> 1) Activity A的启动模式为standard</p> 
 <p> 2) Activity A的启动模式为singleTop</p> 
 <p> 3) Activity A的启动模式为singleTask</p> 
 <p> 4) Activity A的启动模式为singleInstance</p> 
 <p>2.跨应用跳转Activity</p>
 <p>假设应用app1有一个Activity A，另一个应用app2有一个Activity B</p>
 <p>Activity A可跳转至Activity B</p>
 <p>因为Activity A和Actiivty B在不同应用，所以Activity的taskffinity必然不同</p>
 <p>现在Activity A已启动，跳转至Activity B，</p>
 <p>针对以下4种情况分析跳转之后的Activity Task情况</p>
 <p> 1) Activity B的启动模式为standard</p> 
 <p> 2) Activity B的启动模式为singleTop</p> 
 <p> 3) Activity B的启动模式为singleTask</p> 
 <p> 4) Activity B的启动模式为singleInstance</p>
 <p>如果大家对上述场景分析有兴趣的话，可以在评论里一起探讨结果。</p>
