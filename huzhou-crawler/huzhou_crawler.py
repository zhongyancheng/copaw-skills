# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import json
import re
import hashlib
from collections import defaultdict
from datetime import datetime

BASE_URL = "https://huzhou.bqpoint.com"

KEYWORDS = [
    "可行性","可研","项建","项目建议书","风险评估","咨询评估",
    "资金平衡","投融资","投资决策","绿色建筑","节能评估",
    "专项债","项目申请","前期咨询","新能源","碳达峰",
    "碳排放","超低能耗","EOD","低空经济","近零","ESG","小额"
]

SLEEP = 0.3


# =========================
# 当前时间
# =========================
def now_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# =========================
# 初始化浏览器
# =========================
def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


# =========================
# 等待加载
# =========================
def wait_list(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.TAG_NAME, "body")
    )
    time.sleep(1)


# =========================
# 获取列表
# =========================
def get_links(driver):
    elements = driver.find_elements(By.XPATH, "//a")

    links = []
    for a in elements:
        try:
            text = a.text.strip()
            href = a.get_attribute("href")

            if not text or not href:
                continue
            if "javascript" in href:
                continue

            links.append((text, href))
        except:
            continue

    return links


# =========================
# 获取详情
# =========================
def get_detail(driver, url):
    try:
        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[-1])

        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: d.find_element(By.TAG_NAME, "body"))

        time.sleep(0.5)

        text = driver.find_element(By.TAG_NAME, "body").text

        # 👉 尝试提取时间（如果页面有）
        publish_time = None
        match = re.search(r"\d{4}-\d{2}-\d{2}", text)
        if match:
            publish_time = match.group()

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return text, publish_time

    except:
        try:
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return "", None


# =========================
# 关键词匹配
# =========================
def match_keywords(text):
    return list(set([kw for kw in KEYWORDS if re.search(kw, text)]))


# =========================
# 去重 hash
# =========================
def make_hash(title, url, content):
    return hashlib.md5(
        (title + url + content).encode("utf-8")
    ).hexdigest()


# =========================
# 翻页
# =========================
def click_page(driver, target):
    try:
        old = driver.page_source

        elements = driver.find_elements(By.XPATH, "//a | //span")

        for el in elements:
            if el.text.strip() == str(target):
                driver.execute_script("arguments[0].click();", el)

                WebDriverWait(driver, 10).until(
                    lambda d: d.page_source != old
                )
                return True

        return False

    except:
        return False


# =========================
# 主爬虫
# =========================
def crawl():
    driver = init_driver()

    results = []
    seen = set()
    stats = defaultdict(int)

    idx = 0

    for kw in KEYWORDS:
        print(f"\n🔍 关键词: {kw}")

        driver.get(f"{BASE_URL}/search.html?content={kw}")
        wait_list(driver)

        page = 1

        while page <= 10:
            print(f"📄 第 {page} 页")

            links = get_links(driver)

            if not links:
                break

            for i, (title, url) in enumerate(links):

                content, publish_time = get_detail(driver, url)

                h = make_hash(title, url, content)

                if h in seen:
                    continue
                seen.add(h)

                matched = match_keywords(title + content)

                for m in matched:
                    stats[m] += 1

                idx += 1

                results.append({
                    "index": idx,
                    "title": title,
                    "url": url,
                    "keywords": matched,
                    "search_keyword": kw,
                    "page": page,

                    # ✅ 新增时间
                    "crawl_time": now_time(),
                    "publish_time": publish_time
                })

                print(f"   ✔ {idx} {title[:30]}")

                time.sleep(SLEEP)

            print(f"   翻页 -> {page + 1}")

            if not click_page(driver, page + 1):
                break

            wait_list(driver)
            page += 1

    driver.quit()
    return results, stats


# =========================
# 主函数
# =========================
def main():
    data, stats = crawl()

    output = {
        "crawl_time": now_time(),
        "total": len(data),
        "keyword_stats": dict(stats),
        "data": data
    }

    print("\n📊 结果：")
    print(f"总数: {len(data)}")

    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n✅ 已保存 result.json")


if __name__ == "__main__":
    main()