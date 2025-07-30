import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://naipeuwest.blob.core.windows.net/naip/v002/mi/2014/index.html"
LOCAL_ROOT = "E:/SCRATCH/naip/"
EXTENSION_FILTER = [".tif"]

def is_valid_file(href):
    return any(href.lower().endswith(ext) for ext in EXTENSION_FILTER)

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
    # 标记本目录下是否发现.tif文件
    tif_found = False

    for href in links:
        if is_valid_file(href):
            tif_found = True
            # 下载.tif文件
            local_path = os.path.join(LOCAL_ROOT, relative_path)
            os.makedirs(local_path, exist_ok=True)
            filename = os.path.basename(urlparse(href).path)
            save_path = os.path.join(local_path, filename)
            file_url = urljoin(url, href)
            if os.path.exists(save_path):
                print(f"  ⏩ 已存在: {save_path}")
                continue
            try:
                print(f"  📥 Downloading: {file_url} → {save_path}")
                with requests.get(file_url, stream=True, timeout=120) as r:
                    r.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            except Exception as e:
                print(f"  [ERROR] Failed to download {filename}: {e}")

    # 只要不是.tif文件就递归找index.html
    for href in links:
        # 只递归目录型链接（index.html），且不递归当前目录与上级目录
        if href.endswith("index.html") and href not in ("index.html", "../index.html"):
            sub_url = urljoin(url, href)
            sub_relative_path = os.path.join(relative_path, os.path.dirname(href))
            crawl_and_download(sub_url, sub_relative_path)

if __name__ == "__main__":
    print(f"🚀 Starting download from: {BASE_URL}")
    print(f"📁 Saving to: {LOCAL_ROOT}")
    crawl_and_download(BASE_URL)
    print("✅ Done.")

