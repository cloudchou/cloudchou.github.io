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
本系列博客将详细阐述Activity的启动流程，这些博客基于Cm 10.1源码研究。

  * <a href="http://www.cloudchou.com/android/post-788.html" target="_blank">深入理解Activity启动流程(一)&#8211;Activity启动的概要流程</a>
  * <a href="http://www.cloudchou.com/android/post-793.html" target="_blank">深入理解Activity启动流程(二)&#8211;Activity启动相关类的类图</a>
  * <a href="http://www.cloudchou.com/android/post-805.html" target="_blank">深入理解Activity启动流程(三)&#8211;Activity启动的详细流程1</a>
  * <a href="http://www.cloudchou.com/android/post-815.html" target="_blank">深入理解Activity启动流程(三)&#8211;Activity启动的详细流程2</a>

前面两篇博客介绍了Activity的详细启动流程，提到ActivityStack类的startActivityUncheckedLocked方法负责调度ActivityRecord和Task，并且调度算法非常复杂，需结合实际场景分析调度算法。本篇博客将介绍startActivityUncheckedLocked方法的具体实现，本结合实际场景分析调度算法。

## startActivityUncheckedLocked方法的具体实现

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
230
231
232
233
234
235
236
237
238
239
240
241
242
243
244
245
246
247
248
249
250
251
252
253
254
255
256
257
258
259
260
261
262
263
264
265
266
267
268
269
270
271
272
273
274
275
276
277
278
279
280
281
282
283
284
285
286
287
288
289
290
291
292
293
294
295
296
297
298
299
300
301
302
303
304
305
306
307
308
309
310
311
312
313
314
315
316
317
318
319
320
321
322
323
324
325
326
327
328
329
330
331
332
333
334
335
336
337
338
339
340
341
342
343
344
345
346
347
348
349
350
351
352
353
354
355
356
357
358
359
360
361
362
363
364
365
366
367
368
369
370
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> startActivityUncheckedLocked<span style="color: #009900;">&#40;</span>ActivityRecord r,
        ActivityRecord sourceRecord, <span style="color: #000066; font-weight: bold;">int</span> startFlags, <span style="color: #000066; font-weight: bold;">boolean</span> doResume,
        Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #666666; font-style: italic;">//如果从Launcher程序启动应用，launchFlags为</span>
    <span style="color: #666666; font-style: italic;">//FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED </span>
    <span style="color: #666666; font-style: italic;">//否则一般情况下launcheFlags为0，除非启动Activity时设置了特殊的flag</span>
    <span style="color: #000066; font-weight: bold;">int</span> launchFlags <span style="color: #339933;">=</span> intent.<span style="color: #006633;">getFlags</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>      
    <span style="color: #666666; font-style: italic;">//启动Activity时默认不会设置FLAG_ACTIVITY_PREVIOUS_IS_TOP </span>
    <span style="color: #666666; font-style: italic;">//故此notTop默认情况下会是null</span>
    ActivityRecord notTop <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_PREVIOUS_IS_TOP</span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">?</span> r <span style="color: #339933;">:</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span> 
    <span style="color: #666666; font-style: italic;">//默认情况下startFlags不会设置START_FLAG_ONLY_IF_NEEDED</span>
    <span style="color: #666666; font-style: italic;">// If the onlyIfNeeded flag is set, then we can do this if the activity</span>
    <span style="color: #666666; font-style: italic;">// being launched is the same as the one making the call...  or, as</span>
    <span style="color: #666666; font-style: italic;">// a special case, if we do not know the caller then we count the</span>
    <span style="color: #666666; font-style: italic;">// current top activity as the caller.</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>startFlags<span style="color: #339933;">&</span>ActivityManager.<span style="color: #006633;">START_FLAG_ONLY_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//...默认情况下这里的代码不会执行</span>
    <span style="color: #009900;">&#125;</span>    
    <span style="color: #666666; font-style: italic;">//根据被启动的Activity和sourceRecord设置标志</span>
    <span style="color: #666666; font-style: italic;">//launchFlags |= Intent.FLAG_ACTIVITY_NEW_TASK</span>
    <span style="color: #666666; font-style: italic;">//如果从通知栏启动应用 sourceRecord == null</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">// This activity is not being started from another...  in this</span>
        <span style="color: #666666; font-style: italic;">// case we -always- start a new task.</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            Slog.<span style="color: #006633;">w</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"startActivity called from non-Activity context;"</span> 
                  <span style="color: #339933;">+</span><span style="color: #0000ff;">"forcing Intent.FLAG_ACTIVITY_NEW_TASK for: "</span>
                  <span style="color: #339933;">+</span> intent<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            launchFlags <span style="color: #339933;">|=</span> Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">// The original activity who is starting us is running as a single</span>
        <span style="color: #666666; font-style: italic;">// instance...  this new activity it is starting must go on its</span>
        <span style="color: #666666; font-style: italic;">// own task.</span>
        launchFlags <span style="color: #339933;">|=</span> Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">// The activity being started is a single instance...  it always</span>
        <span style="color: #666666; font-style: italic;">// gets launched into its own task.</span>
        launchFlags <span style="color: #339933;">|=</span> Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
  <span style="color: #666666; font-style: italic;">//一般情况下r.resultTo 不为null，它是启动该Activity的Activity，</span>
  <span style="color: #666666; font-style: italic;">//如果从通知栏启动Activity 则r.result为null</span>
  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//...</span>
      r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
  <span style="color: #009900;">&#125;</span>       
    <span style="color: #666666; font-style: italic;">//addingToTask 如果为true表示正在添加至某个task，</span>
    <span style="color: #666666; font-style: italic;">//  后续需要将r添加至sourceRecord所在的task</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//movedHome表示是否移动home task</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> movedHome <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//reuseTask 如果不为null,则表示已存在task，会重用这个task，</span>
    <span style="color: #666666; font-style: italic;">//                      但是这个Task里的所有Activity会被清除掉,</span>
    <span style="color: #666666; font-style: italic;">//                      需要将r加入这个task  </span>
    TaskRecord reuseTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>       
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">&&</span>
            <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_MULTIPLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//从通知栏启动时r.resultTo == null</span>
        <span style="color: #666666; font-style: italic;">//如果launchFlags设置了FLAG_ACTIVITY_NEW_TASK,r.resultTo也会为null</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//查找ActivityRecord栈，看要启动的activity是否已有相关task，</span>
            <span style="color: #666666; font-style: italic;">//如果已经有相关task，则不需要创建新的task，可以使用已有的task</span>
            <span style="color: #666666; font-style: italic;">//如果要启动的activity的启动模式是LAUNCH_SINGLE_INSTANCE，</span>
            <span style="color: #666666; font-style: italic;">//则使用快速查找方法findTaskLocked，否则使用慢速查找方法findActivityLocked</span>
            <span style="color: #666666; font-style: italic;">//因为如果启动模式是LAUNCH_SINGLE_INSTANCE,则这个activity只会在一个单独的Task里</span>
            <span style="color: #666666; font-style: italic;">//故此查找时，可以以task为单位进行查找和比较，这样比较快</span>
            <span style="color: #666666; font-style: italic;">//查找得到的结果taskTop是相关task的栈顶的ActivityRecord               </span>
            <span style="color: #666666; font-style: italic;">// See if there is a task to bring to the front.  If this is</span>
            <span style="color: #666666; font-style: italic;">// a SINGLE_INSTANCE activity, there can be one and only one</span>
            <span style="color: #666666; font-style: italic;">// instance of it in the history, and it is always in its own</span>
            <span style="color: #666666; font-style: italic;">// unique task, so we do a special search.</span>
            ActivityRecord taskTop <span style="color: #339933;">=</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">!=</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
                    <span style="color: #339933;">?</span> findTaskLocked<span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span>
                    <span style="color: #339933;">:</span> findActivityLocked<span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #666666; font-style: italic;">//找到了相关task        </span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>taskTop <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #666666; font-style: italic;">//重设task的intent</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">intent</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">// This task was started because of movement of</span>
                    <span style="color: #666666; font-style: italic;">// the activity based on affinity...  now that we</span>
                    <span style="color: #666666; font-style: italic;">// are actually launching it, we can assign the</span>
                    <span style="color: #666666; font-style: italic;">// base intent.</span>
                    taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">setIntent</span><span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">//如果目标task不在栈顶，</span>
                <span style="color: #666666; font-style: italic;">//则先将Home task移动到栈顶(实际上只有当启动Activity设置的Flag同时设置了</span>
                <span style="color: #666666; font-style: italic;">//FLAG_ACTIVITY_TASK_ON_HOME和FLAG_ACTIVITY_NEW_TASK才会移动home task，</span>
                <span style="color: #666666; font-style: italic;">//否则不会移动home task)，</span>
                <span style="color: #666666; font-style: italic;">//然后再将目标task移动到栈顶</span>
                <span style="color: #666666; font-style: italic;">// If the target task is not in the front, then we need</span>
                <span style="color: #666666; font-style: italic;">// to bring it to the front...  except...  well, with</span>
                <span style="color: #666666; font-style: italic;">// SINGLE_TASK_LAUNCH it's not entirely clear.  We'd like</span>
                <span style="color: #666666; font-style: italic;">// to have the same behavior as if a new instance was</span>
                <span style="color: #666666; font-style: italic;">// being started, which means not bringing it to the front</span>
                <span style="color: #666666; font-style: italic;">// if the caller is not itself in the front.</span>
                ActivityRecord curTop <span style="color: #339933;">=</span> topRunningNonDelayedActivityLocked<span style="color: #009900;">&#40;</span>notTop<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>curTop <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> curTop.<span style="color: #006633;">task</span> <span style="color: #339933;">!=</span> taskTop.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    r.<span style="color: #006633;">intent</span>.<span style="color: #006633;">addFlags</span><span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_BROUGHT_TO_FRONT</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #000066; font-weight: bold;">boolean</span> callerAtFront <span style="color: #339933;">=</span> sourceRecord <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span>
                            <span style="color: #339933;">||</span> curTop.<span style="color: #006633;">task</span> <span style="color: #339933;">==</span> sourceRecord.<span style="color: #006633;">task</span><span style="color: #339933;">;</span>
                    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>callerAtFront<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        <span style="color: #666666; font-style: italic;">// We really do want to push this one into the</span>
                        <span style="color: #666666; font-style: italic;">// user's face, right now.</span>
                        movedHome <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
                        moveHomeToFrontFromLaunchLocked<span style="color: #009900;">&#40;</span>launchFlags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        moveTaskToFrontLocked<span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>, r, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        options <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">//如果launchFlags设置了FLAG_ACTIVITY_RESET_TASK_IF_NEEDED，则会重置task </span>
                <span style="color: #666666; font-style: italic;">//从Launcher应用程序启动应用会设置FLAG_ACTIVITY_RESET_TASK_IF_NEEDED       </span>
                <span style="color: #666666; font-style: italic;">// If the caller has requested that the target task be</span>
                <span style="color: #666666; font-style: italic;">// reset, then do so.</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    taskTop <span style="color: #339933;">=</span> resetTaskIfNeededLocked<span style="color: #009900;">&#40;</span>taskTop, r<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">//... 一般情况下startFlags 不会设置 START_FLAG_ONLY_IF_NEEDED</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>startFlags<span style="color: #339933;">&</span>ActivityManager.<span style="color: #006633;">START_FLAG_ONLY_IF_NEEDED</span><span style="color: #009900;">&#41;</span>  <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">//...</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">// ==================================                                 </span>
                <span style="color: #666666; font-style: italic;">//默认情况下不会设置 Intent.FLAG_ACTIVITY_CLEAR_TASK</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags <span style="color: #339933;">&</span>
                        <span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">|</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TASK</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span>
                        <span style="color: #339933;">==</span> <span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">|</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TASK</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">// The caller has requested to completely replace any</span>
                    <span style="color: #666666; font-style: italic;">// existing task with its new activity.  Well that should</span>
                    <span style="color: #666666; font-style: italic;">// not be too hard...</span>
                    reuseTask <span style="color: #339933;">=</span> taskTop.<span style="color: #006633;">task</span><span style="color: #339933;">;</span>
                    performClearTaskLocked<span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">taskId</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    reuseTask.<span style="color: #006633;">setIntent</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">intent</span>, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TOP</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span>
                        <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span>
                        <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">//默认情况下launchFlags不会设置FLAG_ACTIVITY_CLEAR_TOP</span>
                    <span style="color: #666666; font-style: italic;">//但是如果被启动的activity的启动模式是singleTask或者singleInstance，</span>
                    <span style="color: #666666; font-style: italic;">//也会进入该分支</span>
                    <span style="color: #666666; font-style: italic;">// In this situation we want to remove all activities</span>
                    <span style="color: #666666; font-style: italic;">// from the task up to the one being started.  In most</span>
                    <span style="color: #666666; font-style: italic;">// cases this means we are resetting the task to its</span>
                    <span style="color: #666666; font-style: italic;">// initial state.</span>
                    <span style="color: #666666; font-style: italic;">//清除r所在的task 在r之上的所有activity, </span>
                    <span style="color: #666666; font-style: italic;">//该task里r和在r下的activity不会被清除</span>
                    ActivityRecord top <span style="color: #339933;">=</span> performClearTaskLocked<span style="color: #009900;">&#40;</span>
                            taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">taskId</span>, r, launchFlags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top.<span style="color: #006633;">frontOfTask</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                            <span style="color: #666666; font-style: italic;">// Activity aliases may mean we use different</span>
                            <span style="color: #666666; font-style: italic;">// intents for the top activity, so make sure</span>
                            <span style="color: #666666; font-style: italic;">// the task now has the identity of the new</span>
                            <span style="color: #666666; font-style: italic;">// intent.</span>
                            top.<span style="color: #006633;">task</span>.<span style="color: #006633;">setIntent</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">intent</span>, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        <span style="color: #009900;">&#125;</span>
                        logStartActivity<span style="color: #009900;">&#40;</span>EventLogTags.<span style="color: #006633;">AM_NEW_INTENT</span>, r, top.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        top.<span style="color: #006633;">deliverNewIntentLocked</span><span style="color: #009900;">&#40;</span>callingUid, r.<span style="color: #006633;">intent</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
                        <span style="color: #666666; font-style: italic;">// A special case: we need to</span>
                        <span style="color: #666666; font-style: italic;">// start the activity because it is not currently</span>
                        <span style="color: #666666; font-style: italic;">// running, and the caller has asked to clear the</span>
                        <span style="color: #666666; font-style: italic;">// current task to have this activity at the top.</span>
                        addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
                        <span style="color: #666666; font-style: italic;">// Now pretend like this activity is being started</span>
                        <span style="color: #666666; font-style: italic;">// by the top of its task, so it is put in the</span>
                        <span style="color: #666666; font-style: italic;">// right place.</span>
                        sourceRecord <span style="color: #339933;">=</span> taskTop<span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">realActivity</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">realActivity</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">// In this case the top activity on the task is the</span>
                    <span style="color: #666666; font-style: italic;">// same as the one being launched, so we take that</span>
                    <span style="color: #666666; font-style: italic;">// as a request to bring the task to the foreground.</span>
                    <span style="color: #666666; font-style: italic;">// If the top activity in the task is the root</span>
                    <span style="color: #666666; font-style: italic;">// activity, deliver this new intent to it if it</span>
                    <span style="color: #666666; font-style: italic;">// desires.</span>
                    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_SINGLE_TOP</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span>
                            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TOP</span><span style="color: #009900;">&#41;</span>
                            <span style="color: #339933;">&&</span> taskTop.<span style="color: #006633;">realActivity</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">realActivity</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        logStartActivity<span style="color: #009900;">&#40;</span>EventLogTags.<span style="color: #006633;">AM_NEW_INTENT</span>, r, taskTop.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">frontOfTask</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                            taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">setIntent</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">intent</span>, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        <span style="color: #009900;">&#125;</span>
                        taskTop.<span style="color: #006633;">deliverNewIntentLocked</span><span style="color: #009900;">&#40;</span>callingUid, r.<span style="color: #006633;">intent</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>r.<span style="color: #006633;">intent</span>.<span style="color: #006633;">filterEquals</span><span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">intent</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        <span style="color: #666666; font-style: italic;">// In this case we are launching the root activity</span>
                        <span style="color: #666666; font-style: italic;">// of the task, but with a different intent.  We</span>
                        <span style="color: #666666; font-style: italic;">// should start a new instance on top.</span>
                        addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
                        sourceRecord <span style="color: #339933;">=</span> taskTop<span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">// In this case an activity is being launched in to an</span>
                    <span style="color: #666666; font-style: italic;">// existing task, without resetting that task.  This</span>
                    <span style="color: #666666; font-style: italic;">// is typically the situation of launching an activity</span>
                    <span style="color: #666666; font-style: italic;">// from a notification or shortcut.  We want to place</span>
                    <span style="color: #666666; font-style: italic;">// the new activity on top of the current task.</span>
                    addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
                    sourceRecord <span style="color: #339933;">=</span> taskTop<span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">rootWasReset</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">//进入该分支的情况比较少</span>
                    <span style="color: #666666; font-style: italic;">// In this case we are launching in to an existing task</span>
                    <span style="color: #666666; font-style: italic;">// that has not yet been started from its front door.</span>
                    <span style="color: #666666; font-style: italic;">// The current task has been brought to the front.</span>
                    <span style="color: #666666; font-style: italic;">// Ideally, we'd probably like to place this new task</span>
                    <span style="color: #666666; font-style: italic;">// at the bottom of its stack, but that's a little hard</span>
                    <span style="color: #666666; font-style: italic;">// to do with the current organization of the code so</span>
                    <span style="color: #666666; font-style: italic;">// for now we'll just drop it.</span>
                    taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">setIntent</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">intent</span>, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>   
                <span style="color: #666666; font-style: italic;">// ================================== end</span>
                <span style="color: #666666; font-style: italic;">//如果没有正在添加至某个Task， 并且不用加入一个已清除所有Activity的Task</span>
                <span style="color: #666666; font-style: italic;">//此时只需要显示栈顶Activity即可              </span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span> reuseTask <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">// We didn't do anything...  but it was needed (a.k.a., client</span>
                    <span style="color: #666666; font-style: italic;">// don't use that intent!)  And for paranoia, make</span>
                    <span style="color: #666666; font-style: italic;">// sure we have correctly resumed the top activity.</span>
                    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>doResume<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        resumeTopActivityLocked<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span>, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
                        ActivityOptions.<span style="color: #006633;">abort</span><span style="color: #009900;">&#40;</span>options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span>
                    <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_TASK_TO_FRONT</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span> 
    <span style="color: #666666; font-style: italic;">//...  </span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">packageName</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">// If the activity being launched is the same as the one currently</span>
        <span style="color: #666666; font-style: italic;">// at the top, then we need to check if it should only be launched</span>
        <span style="color: #666666; font-style: italic;">// once.</span>
        ActivityRecord top <span style="color: #339933;">=</span> topRunningNonDelayedActivityLocked<span style="color: #009900;">&#40;</span>notTop<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top.<span style="color: #006633;">realActivity</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">realActivity</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&&</span> top.<span style="color: #006633;">userId</span> <span style="color: #339933;">==</span> r.<span style="color: #006633;">userId</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top.<span style="color: #006633;">app</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> top.<span style="color: #006633;">app</span>.<span style="color: #006633;">thread</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_SINGLE_TOP</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span>
                        <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TOP</span>
                        <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        <span style="color: #666666; font-style: italic;">//singleTop启动模式或者singleTask启动模式，</span>
                        <span style="color: #666666; font-style: italic;">//并且task栈顶的activity是要启动的activity，则先显示Activity</span>
                        <span style="color: #666666; font-style: italic;">//然后调用该Activity的onNewIntent方法</span>
                        logStartActivity<span style="color: #009900;">&#40;</span>EventLogTags.<span style="color: #006633;">AM_NEW_INTENT</span>, top, top.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        <span style="color: #666666; font-style: italic;">// For paranoia, make sure we have correctly</span>
                        <span style="color: #666666; font-style: italic;">// resumed the top activity.</span>
                        <span style="color: #666666; font-style: italic;">//先显示Activity</span>
                        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>doResume<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                            resumeTopActivityLocked<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        <span style="color: #009900;">&#125;</span>
                        ActivityOptions.<span style="color: #006633;">abort</span><span style="color: #009900;">&#40;</span>options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>startFlags<span style="color: #339933;">&</span>ActivityManager.<span style="color: #006633;">START_FLAG_ONLY_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                            <span style="color: #666666; font-style: italic;">// We don't need to start a new activity, and</span>
                            <span style="color: #666666; font-style: italic;">// the client said not to do anything if that</span>
                            <span style="color: #666666; font-style: italic;">// is the case, so this is it!</span>
                            <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_RETURN_INTENT_TO_CALLER</span><span style="color: #339933;">;</span>
                        <span style="color: #009900;">&#125;</span>
                        <span style="color: #666666; font-style: italic;">//然后调用已显示activity的onNewIntent方法</span>
                        top.<span style="color: #006633;">deliverNewIntentLocked</span><span style="color: #009900;">&#40;</span>callingUid, r.<span style="color: #006633;">intent</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_DELIVERED_TO_TOP</span><span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            sendActivityResultLocked<span style="color: #009900;">&#40;</span><span style="color: #339933;">-</span><span style="color: #cc66cc;">1</span>,
                    r.<span style="color: #006633;">resultTo</span>, r.<span style="color: #006633;">resultWho</span>, r.<span style="color: #006633;">requestCode</span>,
                Activity.<span style="color: #006633;">RESULT_CANCELED</span>, <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        ActivityOptions.<span style="color: #006633;">abort</span><span style="color: #009900;">&#40;</span>options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_CLASS_NOT_FOUND</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> newTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> keepCurTransition <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">// Should this be considered a new task?</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span>addingToTask
            <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>reuseTask <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
             <span style="color: #666666; font-style: italic;">//创建新的task</span>
            <span style="color: #666666; font-style: italic;">// todo: should do better management of integers.</span>
            mService.<span style="color: #006633;">mCurTask</span><span style="color: #339933;">++;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mService.<span style="color: #006633;">mCurTask</span> <span style="color: #339933;">&lt;=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                mService.<span style="color: #006633;">mCurTask</span> <span style="color: #339933;">=</span> <span style="color: #cc66cc;">1</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            r.<span style="color: #006633;">setTask</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> TaskRecord<span style="color: #009900;">&#40;</span>mService.<span style="color: #006633;">mCurTask</span>, r.<span style="color: #006633;">info</span>, intent<span style="color: #009900;">&#41;</span>, <span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>DEBUG_TASKS<span style="color: #009900;">&#41;</span> Slog.<span style="color: #006633;">v</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Starting new activity "</span> <span style="color: #339933;">+</span> r
                    <span style="color: #339933;">+</span> <span style="color: #0000ff;">" in new task "</span> <span style="color: #339933;">+</span> r.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
           <span style="color: #666666; font-style: italic;">//重复利用先前的task，该task里的所有acitivity已经被清空</span>
            r.<span style="color: #006633;">setTask</span><span style="color: #009900;">&#40;</span>reuseTask, reuseTask, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
        newTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>movedHome<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            moveHomeToFrontFromLaunchLocked<span style="color: #009900;">&#40;</span>launchFlags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> 
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span>
                <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TOP</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">// In this case, we are adding the activity to an existing</span>
            <span style="color: #666666; font-style: italic;">// task, but the caller has asked to clear that task if the</span>
            <span style="color: #666666; font-style: italic;">// activity is already running.</span>
            <span style="color: #666666; font-style: italic;">//清除r所在task在r之上的所有task，如果r不在task里，则返回的top为null</span>
            ActivityRecord top <span style="color: #339933;">=</span> performClearTaskLocked<span style="color: #009900;">&#40;</span>
                    sourceRecord.<span style="color: #006633;">task</span>.<span style="color: #006633;">taskId</span>, r, launchFlags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            keepCurTransition <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                logStartActivity<span style="color: #009900;">&#40;</span>EventLogTags.<span style="color: #006633;">AM_NEW_INTENT</span>, r, top.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #666666; font-style: italic;">//先调用onNewIntent方法 然后再显示</span>
                top.<span style="color: #006633;">deliverNewIntentLocked</span><span style="color: #009900;">&#40;</span>callingUid, r.<span style="color: #006633;">intent</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #666666; font-style: italic;">// For paranoia, make sure we have correctly</span>
                <span style="color: #666666; font-style: italic;">// resumed the top activity.</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>doResume<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    resumeTopActivityLocked<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                ActivityOptions.<span style="color: #006633;">abort</span><span style="color: #009900;">&#40;</span>options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_DELIVERED_TO_TOP</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span>
                <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_REORDER_TO_FRONT</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//将栈里已有的activity移到栈顶</span>
            <span style="color: #666666; font-style: italic;">// In this case, we are launching an activity in our own task</span>
            <span style="color: #666666; font-style: italic;">// that may already be running somewhere in the history, and</span>
            <span style="color: #666666; font-style: italic;">// we want to shuffle it to the front of the stack if so.</span>
            <span style="color: #000066; font-weight: bold;">int</span> where <span style="color: #339933;">=</span> findActivityInHistoryLocked<span style="color: #009900;">&#40;</span>r, sourceRecord.<span style="color: #006633;">task</span>.<span style="color: #006633;">taskId</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>where <span style="color: #339933;">&gt;=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                ActivityRecord top <span style="color: #339933;">=</span> moveActivityToFrontLocked<span style="color: #009900;">&#40;</span>where<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                logStartActivity<span style="color: #009900;">&#40;</span>EventLogTags.<span style="color: #006633;">AM_NEW_INTENT</span>, r, top.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                top.<span style="color: #006633;">updateOptionsLocked</span><span style="color: #009900;">&#40;</span>options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                top.<span style="color: #006633;">deliverNewIntentLocked</span><span style="color: #009900;">&#40;</span>callingUid, r.<span style="color: #006633;">intent</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>doResume<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    resumeTopActivityLocked<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_DELIVERED_TO_TOP</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #666666; font-style: italic;">// An existing activity is starting this new activity, so we want</span>
        <span style="color: #666666; font-style: italic;">// to keep the new one in the same task as the one that is starting</span>
        <span style="color: #666666; font-style: italic;">// it.</span>
        <span style="color: #666666; font-style: italic;">//同一个应用程序里的Activity A和Activity B，A可跳转至B，没有设置taskAffinity</span>
        <span style="color: #666666; font-style: italic;">//B的启动模式为singleTask，从A跳转至B时，B和A会在同一个task里</span>
        <span style="color: #666666; font-style: italic;">//该情况下会执行到这里的代码，将B的task设置为和A一样的task</span>
        r.<span style="color: #006633;">setTask</span><span style="color: #009900;">&#40;</span>sourceRecord.<span style="color: #006633;">task</span>, sourceRecord.<span style="color: #006633;">thumbHolder</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>DEBUG_TASKS<span style="color: #009900;">&#41;</span> Slog.<span style="color: #006633;">v</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Starting new activity "</span> <span style="color: #339933;">+</span> r
                <span style="color: #339933;">+</span> <span style="color: #0000ff;">" in existing task "</span> <span style="color: #339933;">+</span> r.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">// This not being started from an existing activity, and not part</span>
        <span style="color: #666666; font-style: italic;">// of a new task...  just put it in the top task, though these days</span>
        <span style="color: #666666; font-style: italic;">// this case should never happen.</span>
        <span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> N <span style="color: #339933;">=</span> mHistory.<span style="color: #006633;">size</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        ActivityRecord prev <span style="color: #339933;">=</span>
            N <span style="color: #339933;">&gt;</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">?</span> mHistory.<span style="color: #006633;">get</span><span style="color: #009900;">&#40;</span>N<span style="color: #339933;">-</span><span style="color: #cc66cc;">1</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">:</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
        r.<span style="color: #006633;">setTask</span><span style="color: #009900;">&#40;</span>prev <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span>
                <span style="color: #339933;">?</span> prev.<span style="color: #006633;">task</span>
                <span style="color: #339933;">:</span> <span style="color: #000000; font-weight: bold;">new</span> TaskRecord<span style="color: #009900;">&#40;</span>mService.<span style="color: #006633;">mCurTask</span>, r.<span style="color: #006633;">info</span>, intent<span style="color: #009900;">&#41;</span>, <span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>DEBUG_TASKS<span style="color: #009900;">&#41;</span> Slog.<span style="color: #006633;">v</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Starting new activity "</span> <span style="color: #339933;">+</span> r
                <span style="color: #339933;">+</span> <span style="color: #0000ff;">" in new guessed "</span> <span style="color: #339933;">+</span> r.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>  
    mService.<span style="color: #006633;">grantUriPermissionFromIntentLocked</span><span style="color: #009900;">&#40;</span>callingUid, r.<span style="color: #006633;">packageName</span>,
            intent, r.<span style="color: #006633;">getUriPermissionsLocked</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span> 
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>newTask<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        EventLog.<span style="color: #006633;">writeEvent</span><span style="color: #009900;">&#40;</span>EventLogTags.<span style="color: #006633;">AM_CREATE_TASK</span>, r.<span style="color: #006633;">userId</span>, r.<span style="color: #006633;">task</span>.<span style="color: #006633;">taskId</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
    logStartActivity<span style="color: #009900;">&#40;</span>EventLogTags.<span style="color: #006633;">AM_CREATE_ACTIVITY</span>, r, r.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    startActivityLocked<span style="color: #009900;">&#40;</span>r, newTask, doResume, keepCurTransition, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_SUCCESS</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 实际场景分析

实际场景1:

应用内有两个Activity,A和B,A为第应用入口Activity，从A可跳转至B，A和B的启动模式都为standard

1)从Launcher程序第1次启动应用时的任务调度情况:

任务调度时会创建新task并将新的ActivityRecord加入这个新的task

2)然后跳转至应用内Activity时的任务调度情况:

任务调度时会将新的ActivityRecord加入已有的task

3)然后按Home键，再打开应用程序时的调度情况:

任务调度时会先找到已有的相关task，并显示栈顶的Activity

1)从Launcher程序第1次启动应用时

会创建新task并将新的ActivityRecord加入这个新的task，任务调度执行如下所示:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> startActivityUncheckedLocked<span style="color: #009900;">&#40;</span>ActivityRecord r,
        ActivityRecord sourceRecord, <span style="color: #000066; font-weight: bold;">int</span> startFlags, <span style="color: #000066; font-weight: bold;">boolean</span> doResume,
        Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #666666; font-style: italic;">//launchFlags为FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span>
    <span style="color: #000066; font-weight: bold;">int</span> launchFlags <span style="color: #339933;">=</span> intent.<span style="color: #006633;">getFlags</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
   <span style="color: #666666; font-style: italic;">//... </span>
   <span style="color: #666666; font-style: italic;">//没设置FLAG_ACTIVITY_PREVIOUS_IS_TOP，故此notTop为null        </span>
    ActivityRecord notTop <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_PREVIOUS_IS_TOP</span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">?</span> r <span style="color: #339933;">:</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
   <span style="color: #666666; font-style: italic;">//startFlags未设置ActivityManager.START_FLAG_ONLY_IF_NEEDED</span>
   <span style="color: #666666; font-style: italic;">//...  </span>
   <span style="color: #666666; font-style: italic;">//sourceRecord为Launcher应用的Activity  launcher应用activity的启动模式为singleTask</span>
   <span style="color: #666666; font-style: italic;">// 故此下面的3个条件分支的内容都不会执行  </span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #666666; font-style: italic;">//r.resultTo不为null， launchFlags设置了FLAG_ACTIVITY_NEW_TASK，需要将r.resultTo置为null</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//... </span>
        r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>         
    <span style="color: #000066; font-weight: bold;">boolean</span> addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> movedHome <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    TaskRecord reuseTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//因为launchFlags为FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span>
    <span style="color: #666666; font-style: italic;">//故此下面的条件会满足， 也就是说只要从Launcher程序启动应用，下面这个条件肯定会满足</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">&&</span>
            <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_MULTIPLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//... </span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//因为应用被第一次启动，故此找不到相关task，taskTop则为null</span>
            ActivityRecord taskTop <span style="color: #339933;">=</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">!=</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
                    <span style="color: #339933;">?</span> findTaskLocked<span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span>
                    <span style="color: #339933;">:</span> findActivityLocked<span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>taskTop <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
              <span style="color: #666666; font-style: italic;">//... 这里面的内容不会执行</span>
            <span style="color: #009900;">&#125;</span>     
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
   <span style="color: #666666; font-style: italic;">//...</span>
   <span style="color: #666666; font-style: italic;">//r.packageName != null</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">packageName</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//如果被启动的Activity正好是栈顶的Activity，</span>
        <span style="color: #666666; font-style: italic;">//并且被启动的Activity启动模式是singleTop或者singleTask，</span>
        <span style="color: #666666; font-style: italic;">//则不用将新的ActivityRecord加入到栈里</span>
        <span style="color: #666666; font-style: italic;">//top Activity为Launcher应用的Activity </span>
        ActivityRecord top <span style="color: #339933;">=</span> topRunningNonDelayedActivityLocked<span style="color: #009900;">&#40;</span>notTop<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//top.realActivity.equals(r.realActivity)不满足</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top.<span style="color: #006633;">realActivity</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">realActivity</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&&</span> top.<span style="color: #006633;">userId</span> <span style="color: #339933;">==</span> r.<span style="color: #006633;">userId</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #666666; font-style: italic;">//... 这里的代码不会被执行 </span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #009900;">&#125;</span> 
    <span style="color: #000066; font-weight: bold;">boolean</span> newTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> keepCurTransition <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">// 此时 r.resultTo为null addingToTask为false  launchFlags设置了FLAG_ACTIVITY_NEW_TASK</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span>addingToTask
            <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>reuseTask <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">// todo: should do better management of integers.</span>
            mService.<span style="color: #006633;">mCurTask</span><span style="color: #339933;">++;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>mService.<span style="color: #006633;">mCurTask</span> <span style="color: #339933;">&lt;=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                mService.<span style="color: #006633;">mCurTask</span> <span style="color: #339933;">=</span> <span style="color: #cc66cc;">1</span><span style="color: #339933;">;</span>
            <span style="color: #009900;">&#125;</span>
            <span style="color: #666666; font-style: italic;">//创建新task</span>
            r.<span style="color: #006633;">setTask</span><span style="color: #009900;">&#40;</span><span style="color: #000000; font-weight: bold;">new</span> TaskRecord<span style="color: #009900;">&#40;</span>mService.<span style="color: #006633;">mCurTask</span>, r.<span style="color: #006633;">info</span>, intent<span style="color: #009900;">&#41;</span>, <span style="color: #000066; font-weight: bold;">null</span>, <span style="color: #000066; font-weight: bold;">true</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>DEBUG_TASKS<span style="color: #009900;">&#41;</span> Slog.<span style="color: #006633;">v</span><span style="color: #009900;">&#40;</span>TAG, <span style="color: #0000ff;">"Starting new activity "</span> <span style="color: #339933;">+</span> r
                    <span style="color: #339933;">+</span> <span style="color: #0000ff;">" in new task "</span> <span style="color: #339933;">+</span> r.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
           <span style="color: #666666; font-style: italic;">//...这里的代码会执行</span>
        <span style="color: #009900;">&#125;</span>
        newTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>movedHome<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            moveHomeToFrontFromLaunchLocked<span style="color: #009900;">&#40;</span>launchFlags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//... 这里的代码不会被执行</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//...这里的代码不会被执行</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//... </span>
    startActivityLocked<span style="color: #009900;">&#40;</span>r, newTask, doResume, keepCurTransition, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_SUCCESS</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

2)跳转至应用内Activity时

会将新的ActivityRecord加入已有的task，任务调度执行如下所示:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> startActivityUncheckedLocked<span style="color: #009900;">&#40;</span>ActivityRecord r,
        ActivityRecord sourceRecord, <span style="color: #000066; font-weight: bold;">int</span> startFlags, <span style="color: #000066; font-weight: bold;">boolean</span> doResume,
        Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//此时launchFlags为0 </span>
    <span style="color: #000066; font-weight: bold;">int</span> launchFlags <span style="color: #339933;">=</span> intent.<span style="color: #006633;">getFlags</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//notTop为null    </span>
    ActivityRecord notTop <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_PREVIOUS_IS_TOP</span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">?</span> r <span style="color: #339933;">:</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//startFlags未设置ActivityManager.START_FLAG_ONLY_IF_NEEDED</span>
    <span style="color: #666666; font-style: italic;">//...     </span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//...这里的代码不会被执行</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//...这里的代码不会被执行   </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
      <span style="color: #666666; font-style: italic;">//...这里的代码不会被执行     </span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//r.resultTo != null 但是launchFlags未设置FLAG_ACTIVITY_NEW_TASK</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//... 这里的代码不执行  </span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> movedHome <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    TaskRecord reuseTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//launchFlags为0 r的启动模式为standard 故此下面的逻辑都不会执行</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">&&</span>
            <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_MULTIPLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//... 这里的代码不执行</span>
    <span style="color: #009900;">&#125;</span>
   <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">packageName</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//top 是ActivityA 的ActivityRecord，</span>
        <span style="color: #666666; font-style: italic;">//但是被启动的Activity和top不是同一个Activity</span>
        ActivityRecord top <span style="color: #339933;">=</span> topRunningNonDelayedActivityLocked<span style="color: #009900;">&#40;</span>notTop<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top.<span style="color: #006633;">realActivity</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">realActivity</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&&</span> top.<span style="color: #006633;">userId</span> <span style="color: #339933;">==</span> r.<span style="color: #006633;">userId</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                 <span style="color: #666666; font-style: italic;">//...这里的代码不执行</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...这里的代码不执行</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> newTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> keepCurTransition <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//此时 r.resultTo !=null  sourceRecord != null addingToTask=false</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span>addingToTask
            <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...这里的代码不执行         </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span>
                <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TOP</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
             <span style="color: #666666; font-style: italic;">//... 这里的代码不执行</span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span>
                <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_REORDER_TO_FRONT</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
             <span style="color: #666666; font-style: italic;">//... 这里的代码不执行 </span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #666666; font-style: italic;">//添加到现有的task </span>
        r.<span style="color: #006633;">setTask</span><span style="color: #009900;">&#40;</span>sourceRecord.<span style="color: #006633;">task</span>, sourceRecord.<span style="color: #006633;">thumbHolder</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//... 这里的代码不执行 </span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_SUCCESS</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

3)然后按Home键，再打开应用程序

此时会先找到已有的相关task，并显示栈顶的Activity，任务调度执行如下所示:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> startActivityUncheckedLocked<span style="color: #009900;">&#40;</span>ActivityRecord r,
        ActivityRecord sourceRecord, <span style="color: #000066; font-weight: bold;">int</span> startFlags, <span style="color: #000066; font-weight: bold;">boolean</span> doResume,
        Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    <span style="color: #666666; font-style: italic;">//launchFlags为FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED </span>
    <span style="color: #000066; font-weight: bold;">int</span> launchFlags <span style="color: #339933;">=</span> intent.<span style="color: #006633;">getFlags</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//notTop为null    </span>
    ActivityRecord notTop <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_PREVIOUS_IS_TOP</span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">?</span> r <span style="color: #339933;">:</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//startFlags未设置ActivityManager.START_FLAG_ONLY_IF_NEEDED</span>
    <span style="color: #666666; font-style: italic;">//...         </span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//...这里的代码不会被执行</span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...这里的代码不会被执行  </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//...这里的代码不会被执行 </span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//此时 r.resultTo != null launchFlags设置了FLAG_ACTIVITY_NEW_TASK</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...</span>
        r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span> 
    <span style="color: #000066; font-weight: bold;">boolean</span> addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> movedHome <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    TaskRecord reuseTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//此时launchFlags设置了FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED </span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">&&</span>
            <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_MULTIPLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//此时 r.resultTo == null</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//此时已有相关task，并且task 栈的栈顶是Activity B的ActivityRecord</span>
            <span style="color: #666666; font-style: italic;">//故此taskTop为Activity B的ActivityRecord </span>
            ActivityRecord taskTop <span style="color: #339933;">=</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">!=</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
                    <span style="color: #339933;">?</span> findTaskLocked<span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span>
                    <span style="color: #339933;">:</span> findActivityLocked<span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>taskTop <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #666666; font-style: italic;">//... </span>
                <span style="color: #666666; font-style: italic;">// 此时curTop是Launcher应用的Activity的ActivityRecord  </span>
                ActivityRecord curTop <span style="color: #339933;">=</span> topRunningNonDelayedActivityLocked<span style="color: #009900;">&#40;</span>notTop<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>curTop <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> curTop.<span style="color: #006633;">task</span> <span style="color: #339933;">!=</span> taskTop.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    r.<span style="color: #006633;">intent</span>.<span style="color: #006633;">addFlags</span><span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_BROUGHT_TO_FRONT</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #666666; font-style: italic;">//此时Launcher应用的task在栈顶，故此callerAtFront为true，</span>
                    <span style="color: #666666; font-style: italic;">//此时会把被启动的应用的task移至栈顶</span>
                    <span style="color: #000066; font-weight: bold;">boolean</span> callerAtFront <span style="color: #339933;">=</span> sourceRecord <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span>
                            <span style="color: #339933;">||</span> curTop.<span style="color: #006633;">task</span> <span style="color: #339933;">==</span> sourceRecord.<span style="color: #006633;">task</span><span style="color: #339933;">;</span>
                    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>callerAtFront<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        <span style="color: #666666; font-style: italic;">// We really do want to push this one into the</span>
                        <span style="color: #666666; font-style: italic;">// user's face, right now.</span>
                        movedHome <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span>
                        moveHomeToFrontFromLaunchLocked<span style="color: #009900;">&#40;</span>launchFlags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        moveTaskToFrontLocked<span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>, r, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                        options <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">//此时launchFlags设置了FLAG_ACTIVITY_NEW_TASK|FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span>
                <span style="color: #666666; font-style: italic;">//此时需要重置task 重置完后 taskTop为ActivityB的ActivityRecord   </span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    taskTop <span style="color: #339933;">=</span> resetTaskIfNeededLocked<span style="color: #009900;">&#40;</span>taskTop, r<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">//startFlags为0</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>startFlags<span style="color: #339933;">&</span>ActivityManager.<span style="color: #006633;">START_FLAG_ONLY_IF_NEEDED</span><span style="color: #009900;">&#41;</span>  <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">//... 这些代码都不会被执行 </span>
                <span style="color: #009900;">&#125;</span> 
                <span style="color: #666666; font-style: italic;">//根据launchFlags和被启动的activity的信息 设置resueTask addingTask变量的值                  </span>
                <span style="color: #666666; font-style: italic;">//没设置 Intent.FLAG_ACTIVITY_CLEAR_TASK</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags <span style="color: #339933;">&</span>
                          <span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">|</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TASK</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span>
                          <span style="color: #339933;">==</span> <span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">|</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TASK</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                      <span style="color: #666666; font-style: italic;">//... 这些代码都不会被执行  </span>
                 <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TOP</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span>
                          <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span>
                          <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                      <span style="color: #666666; font-style: italic;">//... 这些代码都不会被执行  </span>
                 <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">realActivity</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">realActivity</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                      <span style="color: #666666; font-style: italic;">//... 这些代码都不会被执行   </span>
                 <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                       <span style="color: #666666; font-style: italic;">//因为从Launcher程序启动时launchFlags设置了FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span>
                       <span style="color: #666666; font-style: italic;">//所以不会进入该分支</span>
                       <span style="color: #666666; font-style: italic;">//... 这些代码都不会被执行   </span>
                  <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">rootWasReset</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                       <span style="color: #666666; font-style: italic;">//... 这些代码都不会被执行    </span>
                  <span style="color: #009900;">&#125;</span>  
                  <span style="color: #666666; font-style: italic;">//此时addingToTask为false，reuseTask为null，故此显示栈顶Actvity即可</span>
                  <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span> reuseTask <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                      <span style="color: #666666; font-style: italic;">// We didn't do anything...  but it was needed (a.k.a., client</span>
                      <span style="color: #666666; font-style: italic;">// don't use that intent!)  And for paranoia, make</span>
                      <span style="color: #666666; font-style: italic;">// sure we have correctly resumed the top activity.</span>
                      <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>doResume<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                          resumeTopActivityLocked<span style="color: #009900;">&#40;</span><span style="color: #000066; font-weight: bold;">null</span>, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                      <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
                          ActivityOptions.<span style="color: #006633;">abort</span><span style="color: #009900;">&#40;</span>options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                      <span style="color: #009900;">&#125;</span>
                      <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_TASK_TO_FRONT</span><span style="color: #339933;">;</span>
                  <span style="color: #009900;">&#125;</span> 
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span>
   <span style="color: #666666; font-style: italic;">//... 以下代码都不会被执行    </span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

实际场景2:

应用内有两个Activity,A和B,A为第应用入口Activity，从A可跳转至B，A的启动模式都为standard，B的启动模式为singleTop

此时已从Launchenr程序打开应用，启动了Actvity A,再从A跳转至B，此时的任务调度情况:

此时不会创建新的Task，而是将B的ActivityRecord加入到A所在的task里

任务调度执行如下所示:

<div class="wp_syntax">
  <table>
    <tr>
      <td class="line_numbers">
        <pre>1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
</pre>
      </td>
      
      <td class="code">
        <pre class="java" style="font-family:monospace;"><span style="color: #000000; font-weight: bold;">final</span> <span style="color: #000066; font-weight: bold;">int</span> startActivityUncheckedLocked<span style="color: #009900;">&#40;</span>ActivityRecord r,
        ActivityRecord sourceRecord, <span style="color: #000066; font-weight: bold;">int</span> startFlags, <span style="color: #000066; font-weight: bold;">boolean</span> doResume,
        Bundle options<span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
    <span style="color: #666666; font-style: italic;">//...  </span>
    <span style="color: #666666; font-style: italic;">//此时launcheFlags为0</span>
    <span style="color: #000066; font-weight: bold;">int</span> launchFlags <span style="color: #339933;">=</span> intent.<span style="color: #006633;">getFlags</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>      
    <span style="color: #666666; font-style: italic;">//notTop为null</span>
    ActivityRecord notTop <span style="color: #339933;">=</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_PREVIOUS_IS_TOP</span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">?</span> r <span style="color: #339933;">:</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//默认情况下startFlags不会设置START_FLAG_ONLY_IF_NEEDED    </span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>startFlags<span style="color: #339933;">&</span>ActivityManager.<span style="color: #006633;">START_FLAG_ONLY_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//...这里的代码不会执行</span>
    <span style="color: #009900;">&#125;</span>    
    <span style="color: #666666; font-style: italic;">//r.launchMode = ActivityInfo.LAUNCH_SINGLE_TASK </span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//这里的代码不会执行  </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//这里的代码不会执行    </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        launchFlags <span style="color: #339933;">|=</span> Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">//此时r.resultTo!=null launchFlags设置了Intent.FLAG_ACTIVITY_NEW_TASK</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
       <span style="color: #666666; font-style: italic;">//...</span>
        r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>
    <span style="color: #009900;">&#125;</span>       
    <span style="color: #666666; font-style: italic;">//addingToTask如果为true表示正在添加至某个task，后续需要将r添加至sourceRecord所在的task</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #666666; font-style: italic;">//movedHome表示是否移动home task</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> movedHome <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span> 
    TaskRecord reuseTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #339933;">;</span>       
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span> <span style="color: #339933;">&&</span>
            <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_MULTIPLE_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span>
            <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #666666; font-style: italic;">//此时 r.resultTo = null</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//此时找到的taskTop是Activity A的ActivityRecord，</span>
            <span style="color: #666666; font-style: italic;">//因为Actvity B和A的ActivityRecord所在的Task是相关的</span>
            ActivityRecord taskTop <span style="color: #339933;">=</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">!=</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span>
                    <span style="color: #339933;">?</span> findTaskLocked<span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span>
                    <span style="color: #339933;">:</span> findActivityLocked<span style="color: #009900;">&#40;</span>intent, r.<span style="color: #006633;">info</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
            <span style="color: #666666; font-style: italic;">//找到了相关task        </span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>taskTop <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                <span style="color: #666666; font-style: italic;">//重设task的intent</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">intent</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                     <span style="color: #666666; font-style: italic;">//...</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">//此时找到的task已在栈顶</span>
                ActivityRecord curTop <span style="color: #339933;">=</span> topRunningNonDelayedActivityLocked<span style="color: #009900;">&#40;</span>notTop<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>curTop <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> curTop.<span style="color: #006633;">task</span> <span style="color: #339933;">!=</span> taskTop.<span style="color: #006633;">task</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">//... 这里的代码不会执行 </span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">//launchFlags为0</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    taskTop <span style="color: #339933;">=</span> resetTaskIfNeededLocked<span style="color: #009900;">&#40;</span>taskTop, r<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">//... 一般情况下startFlags 不会设置 START_FLAG_ONLY_IF_NEEDED</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>startFlags<span style="color: #339933;">&</span>ActivityManager.<span style="color: #006633;">START_FLAG_ONLY_IF_NEEDED</span><span style="color: #009900;">&#41;</span>  <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">//...</span>
                <span style="color: #009900;">&#125;</span> 
&nbsp;
                <span style="color: #666666; font-style: italic;">// ==================== begin</span>
                <span style="color: #666666; font-style: italic;">// launchFlags此时为0</span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags <span style="color: #339933;">&</span>
                        <span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">|</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TASK</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span>
                        <span style="color: #339933;">==</span> <span style="color: #009900;">&#40;</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #339933;">|</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TASK</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                     <span style="color: #666666; font-style: italic;">//...这里的代码不执行</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TOP</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span>
                        <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_TASK</span>
                        <span style="color: #339933;">||</span> r.<span style="color: #006633;">launchMode</span> <span style="color: #339933;">==</span> ActivityInfo.<span style="color: #006633;">LAUNCH_SINGLE_INSTANCE</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                    <span style="color: #666666; font-style: italic;">// r.launchMode == ActivityInfo.LAUNCH_SINGLE_TASK</span>
                    <span style="color: #666666; font-style: italic;">// 故此会进入该分支</span>
                    <span style="color: #666666; font-style: italic;">//因为B还从未启动，故此得到的top为null</span>
                    ActivityRecord top <span style="color: #339933;">=</span> performClearTaskLocked<span style="color: #009900;">&#40;</span>
                            taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">taskId</span>, r, launchFlags<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
                    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                        <span style="color: #666666; font-style: italic;">//...这里的代码不执行 </span>
                    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span> 
                        addingToTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">true</span><span style="color: #339933;">;</span> 
                        sourceRecord <span style="color: #339933;">=</span> taskTop<span style="color: #339933;">;</span>
                    <span style="color: #009900;">&#125;</span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">realActivity</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">realActivity</span><span style="color: #009900;">&#41;</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                     <span style="color: #666666; font-style: italic;">//...这里的代码不执行 </span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_RESET_TASK_IF_NEEDED</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">==</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                     <span style="color: #666666; font-style: italic;">//...这里的代码不执行 </span>
                <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>taskTop.<span style="color: #006633;">task</span>.<span style="color: #006633;">rootWasReset</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                     <span style="color: #666666; font-style: italic;">//...这里的代码不执行 </span>
                <span style="color: #009900;">&#125;</span>
                <span style="color: #666666; font-style: italic;">// ==================== end     </span>
&nbsp;
                <span style="color: #666666; font-style: italic;">// 此时 addingToTask为true          </span>
                <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span> reuseTask <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                     <span style="color: #666666; font-style: italic;">//...这里的代码不执行 </span>
                <span style="color: #009900;">&#125;</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
    <span style="color: #009900;">&#125;</span> 
    <span style="color: #666666; font-style: italic;">//... </span>
&nbsp;
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">packageName</span> <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span> 
        ActivityRecord top <span style="color: #339933;">=</span> topRunningNonDelayedActivityLocked<span style="color: #009900;">&#40;</span>notTop<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
            <span style="color: #666666; font-style: italic;">//此时task还没有B的ActivityRecord，故此不会进入下述分支</span>
            <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>top.<span style="color: #006633;">realActivity</span>.<span style="color: #006633;">equals</span><span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">realActivity</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">&&</span> top.<span style="color: #006633;">userId</span> <span style="color: #339933;">==</span> r.<span style="color: #006633;">userId</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
                 <span style="color: #666666; font-style: italic;">//...这里的代码不执行</span>
            <span style="color: #009900;">&#125;</span>
        <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
           <span style="color: #666666; font-style: italic;">//...这里的代码不执行</span>
    <span style="color: #009900;">&#125;</span>
&nbsp;
    <span style="color: #000066; font-weight: bold;">boolean</span> newTask <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
    <span style="color: #000066; font-weight: bold;">boolean</span> keepCurTransition <span style="color: #339933;">=</span> <span style="color: #000066; font-weight: bold;">false</span><span style="color: #339933;">;</span>
&nbsp;
    <span style="color: #666666; font-style: italic;">// 此时 r.resultTo == null addingToTask为true sourceRecord != null</span>
    <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>r.<span style="color: #006633;">resultTo</span> <span style="color: #339933;">==</span> <span style="color: #000066; font-weight: bold;">null</span> <span style="color: #339933;">&&</span> <span style="color: #339933;">!</span>addingToTask
            <span style="color: #339933;">&&</span> <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_NEW_TASK</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//...这里的代码不执行 </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span>sourceRecord <span style="color: #339933;">!=</span> <span style="color: #000066; font-weight: bold;">null</span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
        <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span>
                <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_CLEAR_TOP</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
               <span style="color: #666666; font-style: italic;">//...这里的代码不执行 </span>
        <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #000000; font-weight: bold;">if</span> <span style="color: #009900;">&#40;</span><span style="color: #339933;">!</span>addingToTask <span style="color: #339933;">&&</span>
                <span style="color: #009900;">&#40;</span>launchFlags<span style="color: #339933;">&</span>Intent.<span style="color: #006633;">FLAG_ACTIVITY_REORDER_TO_FRONT</span><span style="color: #009900;">&#41;</span> <span style="color: #339933;">!=</span> <span style="color: #cc66cc;"></span><span style="color: #009900;">&#41;</span> <span style="color: #009900;">&#123;</span>
               <span style="color: #666666; font-style: italic;">//...这里的代码不执行 </span>
        <span style="color: #009900;">&#125;</span>
        <span style="color: #666666; font-style: italic;">//将B的ActivityRecord加入A的ActivityRecord所在的Task里 </span>
        r.<span style="color: #006633;">setTask</span><span style="color: #009900;">&#40;</span>sourceRecord.<span style="color: #006633;">task</span>, sourceRecord.<span style="color: #006633;">thumbHolder</span>, <span style="color: #000066; font-weight: bold;">false</span><span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
        <span style="color: #666666; font-style: italic;">//... </span>
    <span style="color: #009900;">&#125;</span> <span style="color: #000000; font-weight: bold;">else</span> <span style="color: #009900;">&#123;</span>
         <span style="color: #666666; font-style: italic;">//...这里的代码不执行</span>
    <span style="color: #009900;">&#125;</span>
    <span style="color: #666666; font-style: italic;">//...</span>
    startActivityLocked<span style="color: #009900;">&#40;</span>r, newTask, doResume, keepCurTransition, options<span style="color: #009900;">&#41;</span><span style="color: #339933;">;</span>
    <span style="color: #000000; font-weight: bold;">return</span> ActivityManager.<span style="color: #006633;">START_SUCCESS</span><span style="color: #339933;">;</span>
<span style="color: #009900;">&#125;</span></pre>
      </td>
    </tr>
  </table>
</div>

## 总结

从上面的分析可以看出来，Activity和Task的调度算法非常复杂，需结合实际场景才好分析，只有这样才知道是否需要新建Task,还是将新的ActivityRecord加入到已有的Task里，不过我们如果能理解启动模式的一些特点，对理解调度算法会有很大帮助。

大家可以结合下述场景分析调度算法:

1.从通知栏启动Activity:

假设应用有Activity A ，Activity A已启动，

此时发了一个通知，该通知用于启动Activity A，启动Activity A时不加任何特殊flag

点击通知，针对以下情况对任务调度情况进行分析:

1) Activity A的启动模式为standard

2) Activity A的启动模式为singleTop

3) Activity A的启动模式为singleTask

4) Activity A的启动模式为singleInstance

2.跨应用跳转Activity

假设应用app1有一个Activity A，另一个应用app2有一个Activity B

Activity A可跳转至Activity B

因为Activity A和Actiivty B在不同应用，所以Activity的taskffinity必然不同

现在Activity A已启动，跳转至Activity B，

针对以下4种情况分析跳转之后的Activity Task情况

1) Activity B的启动模式为standard

2) Activity B的启动模式为singleTop

3) Activity B的启动模式为singleTask

4) Activity B的启动模式为singleInstance

如果大家对上述场景分析有兴趣的话，可以在评论里一起探讨结果。