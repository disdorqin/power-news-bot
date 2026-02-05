import requests
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# --- 环境变量获取 ---
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
MAIL_RECEIVER = os.environ.get("MAIL_RECEIVER")

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
                    results.append(f"<p>📦 <b>{repo_name}</b> (⭐{stars})<br>🔗 <a href='{repo_url}'>{repo_url}</a><br>📝 {desc}</p>")
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
                results.append(f"<p>📄 <b>{title}</b><br>📅 {published}<br>🔗 <a href='{link}'>{link}</a></p>")
        except Exception as e:
            print(f"ArXiv Error: {e}")
    return list(set(results))

def send_email(content):
    if not MAIL_USER or not MAIL_PASS:
        print("❌ 未配置邮箱密钥，跳过发送")
        return

    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header("电力情报Bot", 'utf-8')
    message['To'] = Header("未来的大牛", 'utf-8')
    message['Subject'] = Header(f"⚡ 电力预测日报 ({datetime.datetime.now().strftime('%m-%d')})", 'utf-8')

    # --- 自动判断邮箱服务器 ---
    smtp_server = 'smtp.qq.com'
    if '@163.com' in MAIL_USER:
        smtp_server = 'smtp.163.com'
    
    print(f"正在连接邮箱服务器: {smtp_server} ...")

    try:
        # 【修改点】改用 587 端口 + starttls，这在 GitHub Actions 上更稳定
        smtp_obj = smtplib.SMTP(smtp_server, 587)
        smtp_obj.ehlo()
        smtp_obj.starttls() # 启动加密传输
        smtp_obj.login(MAIL_USER, MAIL_PASS)
        smtp_obj.sendmail(MAIL_USER, [MAIL_RECEIVER], message.as_string())
        smtp_obj.quit()
        print("✅ 邮件发送成功！快去查收！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

if __name__ == "__main__":
    github_data = get_github_updates()
    arxiv_data = get_arxiv_updates()
    
    html_msg = "<h2>🚀 今日 GitHub 更新</h2>" + ("".join(github_data) if github_data else "<p>暂无新项目</p>")
    html_msg += "<hr><h2>📚 最新 ArXiv 论文</h2>" + ("".join(arxiv_data) if arxiv_data else "<p>暂无新论文</p>")
    
    send_email(html_msg)
