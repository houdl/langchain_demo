# all ping 项目介绍

### 项目背景

* <https://github.com/feed-mob/feedmob/issues/10810> 调研：FeedMob ALL PINGS on Singular
* 背景：Singular在问能否把 uber all pings 发到一个端口，再通过 FEEDMOB_REFERRAL (attributed, nonattributed) 来区分，因为 Singular 只能全部发送全部数据到一个端口，或只发attributed数据。
* 讨论方案：所有数据发到 uber-eats.feedmob.com，FEEDMOB_REFERRAL=attributed 则转发到 conversion api 进行正常处理，如果不是， 则由 ubereats 的 api 处理后， 发到 ua api进行处理

  \

### 第一步实现数据分发：

相关逻辑：

* FEEDMOB_REFERRAL=attributed 则转发到 conversion api 进行正常处理
* FEEDMOB_REFERRAL=notattributed 转发到 all ping api 进行正常处理

 ![](/api/attachments.redirect?id=8a180389-0606-4692-a8c1-630ccb11b53b)


相关lb 规则：

 ![](/api/attachments.redirect?id=fbd65949-e2cb-4fbc-8d94-1da2d606a8dd)


\
### 第二步实现all ping api数据存储：

* 相关ticket: <https://github.com/feed-mob/feedmob/issues/10896>
* 对于请求 partner api的数据结果进行存储：ourl， target_url，postback_time，code，message，post_body
* 需要一个页面， 能够看到这些数据 

  \


 ![](/api/attachments.redirect?id=79811565-9a52-4359-9f5f-cc7af0ef0a45)


\
### 第三步：实现对于shareit 的 event mapping 需求，以及all ping数据发送给shareit

* 相关ticket <https://github.com/feed-mob/feedmob/issues/10900>

  \

1  shareit 需要哪些类数据：根据FEEDMOB_REFERRAL 分为三类:

attributed 数据：

* ourl 中 FEEDMOB_REFERRAL=attributed 的为 attributed数据
* 回发给shareit api的参数中包含 channel=shareit
* 只转发数据 open 和 level 的数据给shareit

notattributed数据：

* ourl 中 FEEDMOB_REFERRAL=notattributed 的为 attributed数据
* 回发给shareit api的参数中包含 channel=''
* 转发数据 所有event数据给shareit, 包含：install, open, level, purchase, registration, retained

organic数据：

* ourl 中 FEEDMOB_REFERRAL=organic 的为 attributed数据
* 回发给shareit api的参数中包含 channel=organic
* 转发数据 所有event数据给shareit, 包含：install, open, level, purchase, registration, retained


 2  shareit 相关的event mapping 

 ![](/api/attachments.redirect?id=7048d818-5422-4406-b079-b74bcb8fb397)


3 相关 lb 重新配置

* FEEDMOB_REFERRAL=attributed 并且 ACTION=L或ACTION=O的转发到 ua conversion api
* FEEDMOB_REFERRAL=attributed 的其他 events 的转发到 tracking conversion api
* 其他数据，FEEDMOB_REFERRAL=notattributed 或 FEEDMOB_REFERRAL=organic 会转发到 ua conversion api

 ![](/api/attachments.redirect?id=f0df3012-d8db-49e6-ac64-ec5bf1cb1513)


4 相关数据流程图


 ![](/api/attachments.redirect?id=484420de-6d29-45b9-a651-a5d596230076)


### 第四步：增加 all ping 的 lambda 备用方案

* 相关ticket <https://github.com/feed-mob/tracking_admin/issues/16549>
* 解决的当 all ping worker 处理不过来的时候可以有 lambda 方案来做支撑

相关方案：

* lambda_logs_divider代码中直接调用S3，读取解析ELB logs并将参数以CSV格式写到S3 ua-conversion-divided中
* lambda_ua_conversion被ua-conversion-divided S3文件触发，读取CSV文件，向vendor发送postback，随机存一部分ua_conversion_postbacks到redshift中


数据分发 lambda 处理 redshift 正常：

 ![](/api/attachments.redirect?id=de3be933-783e-4c2e-b9ba-93279a7d9e67)

 lambda all ping conversion  优化：

*   <https://github.com/feed-mob/tracking_admin/issues/16609> 
* 使用多线程的方式，充分利用 lambda 服务，增加处理速度
* lambda上限100个线程，改为使用线程池


 ![](/api/attachments.redirect?id=d9881e6e-e687-4353-82c7-e9a8ca7071e3)


\
### 第五步：统一把 uber eat lb 数据转发到 all ping api 

* 相关ticket: <https://github.com/feed-mob/feedmob/issues/11007>
* 原因： 之前对于 attributed 的 非 open 和 level 的数据（从lb 那边切给 tracking api 了），不会发送 给 all ping api ，所以不会发送给shareit  , 需要把所有数据都发送给 shareit 
* 方案： 把 uber eat lb 数据转发到 all ping api ，分成两个job: 一个job将所有数据都发给shareit， 一个job 将 attributed 的 非open 和 level 的数据发给 tracking api 实现 conversion records 数据的保存
* 遇到问题： all ping worker 主机到 不在 mmp  ip 白名单, 所以从 all ping worker 发送到 tracking 的数据，status 会被判定为 invalid_mip  ，处理方案： 把 all ping worker ip 添加到 mmp ip 上处理


 ![](/api/attachments.redirect?id=523e3bf3-d519-42ef-bc21-81367cf0f099)


相关 lb 切换：全部切换为 all ping api 

 ![](/api/attachments.redirect?id=f228512b-eb7f-4989-b007-b95a2cc55998)


相关数据流程图：

 ![](/api/attachments.redirect?id=4d2ddb4b-d678-4316-b69f-1b19fea075e4)


\
### 第六步： 后续的一些优化

1 all ping job 处理中的tracking api的部分进行独立queue 和 服务器

* ticket  <https://github.com/feed-mob/tracking_admin/issues/16711>
* 解决：如果当 all ping这边的数据堵塞， tracking  api 那边数据请求不受到影响
* 所以对于 tracking api 的job 使用单独的队列和服务器隔离


 ![](/api/attachments.redirect?id=ea58fa84-0dbd-484c-b594-fc2dc506cc2e)

 2 对于 invalid_mip 的判断使用真实的 mmp ip 进行判断

* ticket <https://github.com/feed-mob/tracking_admin/issues/16694>
* 原因： 在处理all ping worker 主机到 不在 mmp  ip 白名单的时候，把 all ping worker 服务器添加到白名单，并不能是使用 mmp ip 进行的 invalid_mip 判断，存在漏洞
* 方案： 在 all ping worker 把真实的 mmp ip 发送给 tracking api ，从而 sidekiq conversion worker 项目 根据 MMP_REMOTE_IP 进行 判断是否是 IP 白名单


 ![](/api/attachments.redirect?id=5a6dc74b-d76d-44bb-aa7f-593883e49ce0)


\

\
### 停止转发

* 停止all ping 转发给 tracking api https://github.com/feed-mob/feedmob/issues/11693


