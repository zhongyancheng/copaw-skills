# 湖州项目信息关键词爬虫
## 描述
爬取湖州项目平台（huzhou.bqpoint.com），支持多关键词检索、自动翻页、内容去重、关键词匹配、发布时间提取，输出结构化JSON结果。
## 入口函数
main
## 执行类型
function
## 输入参数
- keywords: 检索关键词列表（数组）
- max_page: 单关键词最大翻页数（数字）
- sleep_time: 请求间隔时间（数字，单位秒）
## 输出参数
- total_count: 爬取数据总条数
- keyword_stats: 关键词命中次数统计
- output_file: 结果文件保存路径