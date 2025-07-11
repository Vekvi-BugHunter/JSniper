# JSniper

```
     ██╗███████╗███╗   ██╗██╗██████╗ ███████╗██████╗ 
     ██║██╔════╝████╗  ██║██║██╔══██╗██╔════╝██╔══██╗
     ██║███████╗██╔██╗ ██║██║██████╔╝█████╗  ██████╔╝
██   ██║╚════██║██║╚██╗██║██║██╔═══╝ ██╔══╝  ██╔══██╗
╚█████╔╝███████║██║ ╚████║██║██║     ███████╗██║  ██║
 ╚════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ @vevki
```

**JSniper** is a Python-based tool to automate JavaScript endpoint discovery and secret leakage analysis in web apps.

## 🔥 Features
- Custom path file support via `--path`
- Multi-threaded JS + HTML downloader
- TruffleHog integration with deduplicated secret results
- In-scope endpoint extraction from downloaded files
- Output neatly organized under `output/<domain>/`

## 🛠️ Installation
```bash
# Clone the repo
git clone https://github.com/Vekvi-BugHunter/JSniper.git
cd JSniper

# Install Python requirements
pip install -r requirements.txt

# Install TruffleHog (ensure it's in PATH)
sudo apt install trufflehog  # or use: pip install trufflehog
```

## 🚀 Usage
```bash
python3 main.py https://example.com -p path.txt
```

### Optional:
- If you don't provide `-p`, it will use `path.txt` by default.
- You can include authenticated routes in `path.txt` if using cookies (add in `headers`).

## 📂 Output Example
```
output/example.com/
├── js/               # Downloaded JS + HTML files
├── js-urls.txt       # All <script src=...> links found
├── endpoints.txt     # Extracted in-scope API endpoints
└── secrets.json      # Unique TruffleHog findings
```

## 🧪 Sample `path.txt`
```
/
/login
/dashboard
/static/
/js/main.js
```

## ⚠️ Disclaimer
This tool is intended for internal pentesting & educational purposes only. Do not use it on unauthorized systems.

## 📧 Contact
Made with 💗 by [Vekvi-BugHunter] - [demotivator2001@gmail.com] (or GitHub handle)

---
MIT License | Star ⭐ if helpful!
