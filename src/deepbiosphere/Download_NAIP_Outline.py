import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://naipeuwest.blob.core.windows.net/naip/v002/mi/2012/mi_shpfl_2012/index.html"
LOCAL_ROOT = "D:/deepbiosphere_mi/PATHS/SHPFILES/mi_shpfl_2012/"

def get_links_from_url(url):
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return [a["href"] for a in soup.find_all("a") if "href" in a.attrs]
    except Exception as e:
        print(f"[ERROR] Failed to load {url}: {e}")
        return []

def crawl_and_download(url, relative_path=""):
    print(f"🔍 正在访问: {url}")
    links = get_links_from_url(url)

    for href in links:
        full_url = urljoin(url, href)
        local_path = os.path.join(LOCAL_ROOT, relative_path)
        os.makedirs(local_path, exist_ok=True)
        filename = os.path.basename(urlparse(href).path)
        save_path = os.path.join(local_path, filename)

        # 递归：如果是 index.html 说明可能还有下级目录
        if href.endswith("index.html") and href not in ("index.html", "../index.html"):
            sub_url = urljoin(url, href)
            sub_relative_path = os.path.join(relative_path, os.path.dirname(href))
            crawl_and_download(sub_url, sub_relative_path)
        # 下载所有文件类型
        elif "." in filename:
            if os.path.exists(save_path):
                print(f"  ⏩ 已存在: {save_path}")
                continue
            try:
                print(f"  📥 Downloading: {full_url} → {save_path}")
                with requests.get(full_url, stream=True, timeout=120) as r:
                    r.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            except Exception as e:
                print(f"  [ERROR] Failed to download {filename}: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting download from: {BASE_URL}")
    print(f"📁 Saving to: {LOCAL_ROOT}")
    crawl_and_download(BASE_URL)
    print("✅ Done.")