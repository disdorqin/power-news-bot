import requests
import datetime
import os

# --- 环境变量 ---
XP_TOKEN = os.environ.get("XP_TOKEN")
XP_UID = os.environ.get("XP_UID")

KEYWORDS = ["electricity forecasting", "load forecasting", "time series forecasting"]

def get_github_updates():
    print("正在搜索 GitHub...")
    results = []
    date_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    for keyword in KEYWORDS:
        url = f"https://api.github.com/search/repositories?q={keyword}+pushed:>{date_str}&sort=updated&order=desc"
        try:
            response = requests.get(url).json()
            if "items" in response:
                for item in response["items"][:3]:
                    repo_name = item['full_name']
                    repo_url = item['html_url']
                    desc = item['description']
                    stars = item['stargazers_count']
                    # HTML 格式优化
                    results.append(f"📦 <b>{repo_name}</b> (⭐{stars})<br>🔗 <a href='{repo_url}'>{repo_url}</a><br>📝 {desc}<br>")
        except Exception as e:
            print(f"GitHub Error: {e}")
    return results

def get_arxiv_updates():
    print("正在搜索 ArXiv...")
    results = []
    import urllib.request as libreq
    import xml.etree.ElementTree as ET
    for keyword in KEYWORDS:
        query = keyword.replace(" ", "+")
        url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending'
        try:
            with libreq.urlopen(url) as url_file:
                response = url_file.read()
            root = ET.fromstring(response)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.replace('\n', ' ')
                link = entry.find('atom:id', ns).text
                published = entry.find('atom:published', ns).text[:10]
                results.append(f"📄 <b>{title}</b><br>📅 {published}<br>🔗 <a href='{link}'>{link}</a><br>")
        except Exception as e:
            print(f"ArXiv Error: {e}")
    return list(set(results))

def send_wxpusher(content):
    if not XP_TOKEN or not XP_UID:
        print("❌ 未配置 WxPusher 密钥，跳过发送")
        return

    url = "https://wxpusher.zjiecode.com/api/send/message"
    
    # 构造请求数据
    data = {
        "appToken": XP_TOKEN,
        "content": content,
        "summary": f"⚡ 电力日报 ({datetime.datetime.now().strftime('%m-%d')})", # 消息摘要
        "contentType": 2, # 2表示HTML
        "uids": [XP_UID],
        "verifyPay": False
    }
    
    try:
        res = requests.post(url, json=data).json()
        if res['code'] == 1000:
            print("✅ 微信推送成功！")
        else:
            print(f"❌ 推送失败: {res['msg']}")
    except Exception as e:
        print(f"❌ 网络错误: {e}")

if __name__ == "__main__":
    github_data = get_github_updates()
    arxiv_data = get_arxiv_updates()
    
    html_msg = "<h2>🚀 今日 GitHub 更新</h2>" + ("<br>".join(github_data) if github_data else "暂无新项目")
    html_msg += "<br><hr><h2>📚 最新 ArXiv 论文</h2>" + ("<br>".join(arxiv_data) if arxiv_data else "暂无新论文")
    
    send_wxpusher(html_msg)
