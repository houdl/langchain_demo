# Email Alert: [Uber Skan New Singular Campaign Found]

## Overview
**Alert Type:** [mmp new campaign check]
**Sender:** [admin@feedmob.info]
**Recipients:** [Subscriber]
**Frequency:** [Daily]

## Sample Email
![邮件](../../assets/uber-skan-new-singular-campaign-found.png)

## What This Alert Means
 - 邮件的目的是检查是否有新的 uber Skan Campaigns 在我们系统中没有 campaign mapping, 可能会影响spend录入 和 event 显示

## Severity Level
- [x] P2 - Medium (Action required within 24 hours)

## How to Handle

### 1. Initial Assessment
- 有新的 uber Skan Campaign 没有 campaign mapping，不能保存到 singular report db 中，需要检查原因

### 2. Resolution Steps
1. 检查 click url 列表中 uber <> Amazon 中 click url 的 tracking url 中是否有pcn=CM2502613-display-amazon_1_-99_US-National_e_ios_acq_cpc_en_30-09-2024的(例子)
2. 同时检查一下 https://admin.feedmob.com/singular_campaign_mappings 页面是否有这个 campaign mapping
3. 后续需要和业务确认 这个 uber skan Campaign 对应的 click url
4. 后续确认了mapping 关系以后，需要及时更新 campaign mapping, 以及补录对应的 events 到 singular report db
5. 后续更新 singular report 数据到 agency dashboard

```
DownloadSingularReportUberSkanJob.perform_now(start_date: '2024-xx-xx', end_date: '2024-xx-xx')

(start_date..end_date).each do |date|
  RefreshAgencyRecordsJob.perform_now(refresh_date: date, daily_refresh: false)
end
```

## Related Resources
- uber skan 页面，为 uber 分享过来的链接 https://app.singular.net/react/anonymous2/?secret_id=2592a295c89d216525d224fce82160bb8d77a1dd9a9bbc3f8890810ff3ea62f4#/react/anonymous/2592a295c89d216525d224fce82160bb8d77a1dd9a9bbc3f8890810ff3ea62f4//

## Notes
- 拉取uber skan ticket https://github.com/feed-mob/feedmob/issues/10957
- 最近处理相关ticket https://github.com/feed-mob/tracking_admin/issues/18479

## Recent Updates
| Date | Change | Author |
|------|---------|--------|
| 2024-12-23 |检查Uber Skan New Singular Campaign Found邮件| [Jason] |