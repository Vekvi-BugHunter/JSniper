import requests
from bs4 import BeautifulSoup
import os
import re
import subprocess
import sys
import json
import argparse
import random
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

banners = [
    """
     ██╗███████╗███╗   ██╗██╗██████╗ ███████╗██████╗ 
     ██║██╔════╝████╗  ██║██║██╔══██╗██╔════╝██╔══██╗
     ██║███████╗██╔██╗ ██║██║██████╔╝█████╗  ██████╔╝
██   ██║╚════██║██║╚██╗██║██║██╔═══╝ ██╔══╝  ██╔══██╗
╚█████╔╝███████║██║ ╚████║██║██║     ███████╗██║  ██║
 ╚════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ @vevki
    """
]

headers = {
    "User-Agent": "Mozilla/5.0"
    # Add "Cookie" header if needed for auth
}

# ---------------------------------------
def get_domain_folder(base_url):
    parsed = urlparse(base_url)
    domain = parsed.netloc.replace(":", "_")
    return f"output/{domain}"

# ---------------------------------------
def load_paths(path_file, base_url):
    paths = []
    try:
        with open(path_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    full_url = base_url.rstrip("/") + line if line.startswith("/") else base_url + "/" + line
                    paths.append(full_url)
    except Exception as e:
        print(f"[-] Error loading path file: {e}")
        sys.exit(1)
    return paths

# ---------------------------------------
def get_js_urls_from_pages(urls):
    js_urls = set()
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            scripts = soup.find_all("script")
            for tag in scripts:
                src = tag.get("src")
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        base = url.split("/")[0] + "//" + url.split("/")[2]
                        src = base + src
                    js_urls.add(src)
        except Exception as e:
            print(f"[-] Failed to parse {url}: {e}")
    return list(js_urls)

# ---------------------------------------
def download_single_file(url, out_dir):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        fname = url.split("/")[-1].split("?")[0]
        if not fname or "." not in fname:
            fname = url.replace("://", "_").replace("/", "_") + ".html"
        if not fname.endswith(".js") and not fname.endswith(".html"):
            fname += ".html"
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(r.text)
        return path
    except Exception as e:
        print(f"[-] Failed to download {url}: {e}")
        return None

def download_all_files(urls, out_dir):
    print(f"[+] Downloading files with multithreading...")
    downloaded_files = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_single_file, url, out_dir) for url in urls]
        for future in as_completed(futures):
            result = future.result()
            if result:
                downloaded_files.append(result)
    return downloaded_files

# ---------------------------------------
def extract_endpoints(js_dir, domain, out_file):
    pattern = r"(https?:\/\/[^\s'\"<>]+|\/[a-zA-Z0-9_\/\-\.]+(?:\.[a-z]{2,4})?)"
    endpoints = set()
    for fname in os.listdir(js_dir):
        try:
            with open(os.path.join(js_dir, fname), encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(pattern, content)
                for ep in matches:
                    if ep.startswith("http") and domain in ep:
                        endpoints.add(ep)
                    elif ep.startswith("/"):
                        endpoints.add(ep)
        except Exception as e:
            print(f"[-] Error in {fname}: {e}")
    with open(out_file, "w") as f:
        for ep in sorted(endpoints):
            f.write(ep + "\n")
    print(f"[+] In-scope endpoints saved: {out_file}")

# ---------------------------------------
def run_trufflehog(files, out_file):
    print("[+] Running TruffleHog...")
    seen = set()
    secrets = []

    for path in files:
        try:
            result = subprocess.run(
                ["trufflehog", "filesystem", "--json", path],
                capture_output=True, text=True
            )
            for line in result.stdout.strip().splitlines():
                try:
                    j = json.loads(line)
                    unique_key = json.dumps(j, sort_keys=True)
                    if unique_key not in seen:
                        secrets.append(j)
                        seen.add(unique_key)
                except:
                    continue
        except Exception as e:
            print(f"[-] TruffleHog failed on {path}: {e}")

    with open(out_file, "w") as f:
        json.dump(secrets, f, indent=2)
    print(f"[+] Unique secrets saved: {out_file}")

# ---------------------------------------
if __name__ == "__main__":
    print(random.choice(banners))
    parser = argparse.ArgumentParser(description="JS + HTML Analyzer for Internal PT")
    parser.add_argument("url", help="Base URL (e.g. https://uat.example.com)")
    parser.add_argument("-p", "--path", help="Path file (e.g. path.txt)", default="path.txt")
    args = parser.parse_args()

    base_url = args.url.strip().rstrip("/")
    parsed_url = urlparse(base_url)
    domain = parsed_url.netloc
    domain_folder = get_domain_folder(base_url)
    js_dir = os.path.join(domain_folder, "js")

    os.makedirs(js_dir, exist_ok=True)

    print(f"[+] Target: {base_url}")
    print(f"[+] Loading paths from: {args.path}")
    
    # Load paths & crawl for JS
    path_urls = load_paths(args.path, base_url)
    js_urls = get_js_urls_from_pages(path_urls)

    # Save JS URLs to file
    with open(os.path.join(domain_folder, "js-urls.txt"), "w") as f:
        f.write("\n".join(js_urls))

    print(f"[+] Found {len(js_urls)} JS URLs")

    all_urls_to_download = list(set(path_urls + js_urls))
    all_downloaded_files = download_all_files(all_urls_to_download, js_dir)

    extract_endpoints(js_dir, domain, os.path.join(domain_folder, "endpoints.txt"))

    run_trufflehog(all_downloaded_files, os.path.join(domain_folder, "secrets.json"))

    print(f"\n✅ DONE! Output in: {domain_folder}/")
