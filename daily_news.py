import requests
import datetime
import os

# --- 配置区 ---
KEYWORDS = ["electricity forecasting", "load forecasting", "time series forecasting"]
# 你的 PushPlus Token (本地测试时填这里，传到 GitHub 后我们会用环境变量覆盖)
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN") 

def get_github_updates():
    print("正在搜索 GitHub...")
    results = []
    # 搜索最近 24 小时更新的项目
    date_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    for keyword in KEYWORDS:
        url = f"https://api.github.com/search/repositories?q={keyword}+pushed:>{date_str}&sort=updated&order=desc"
        try:
            response = requests.get(url).json()
            if "items" in response:
                for item in response["items"][:3]: # 每个关键词只取前3个，防止太长
                    repo_name = item['full_name']
                    repo_url = item['html_url']
                    desc = item['description']
                    stars = item['stargazers_count']
                    results.append(f"📦 **{repo_name}** (⭐{stars})\n🔗 {repo_url}\n📝 {desc}\n")
        except Exception as e:
            print(f"GitHub 搜索出错: {e}")
    return results

def get_arxiv_updates():
    print("正在搜索 ArXiv 论文...")
    results = []
    # 使用 arXiv API
    import urllib.request as libreq
    import xml.etree.ElementTree as ET
    
    for keyword in KEYWORDS:
        # 将空格替换为 +
        query = keyword.replace(" ", "+")
        url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending'
        try:
            with libreq.urlopen(url) as url_file:
                response = url_file.read()
            root = ET.fromstring(response)
            # 解析 XML (ArXiv 返回的是 XML)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.replace('\n', ' ')
                link = entry.find('atom:id', ns).text
                published = entry.find('atom:published', ns).text[:10]
                # 简单过滤最近两天的（简化逻辑）
                results.append(f"📄 **{title}**\n📅 {published}\n🔗 {link}\n")
        except Exception as e:
            print(f"ArXiv 搜索出错: {e}")
    return list(set(results)) # 去重

def send_wechat(content):
    if not PUSHPLUS_TOKEN:
        print("没有 Token，跳过推送")
        print(content) # 本地打印代替
        return
    
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": f"⚡ 电力预测日报 ({datetime.datetime.now().strftime('%m-%d')})",
        "content": content,
        "template": "markdown"
    }
    requests.post(url, json=data)
    print("微信推送成功！")

if __name__ == "__main__":
    github_data = get_github_updates()
    arxiv_data = get_arxiv_updates()
    
    msg = "## 🚀 今日 GitHub 更新\n" + ("\n".join(github_data) if github_data else "暂无新项目")
    msg += "\n\n## 📚 最新 ArXiv 论文\n" + ("\n".join(arxiv_data) if arxiv_data else "暂无新论文")
    
    send_wechat(msg)