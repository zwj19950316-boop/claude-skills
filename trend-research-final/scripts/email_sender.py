#!/usr/bin/env python3
"""邮件发送脚本 — 通过SMTP发送热点报告"""

import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_manager import load_config


def markdown_to_html(markdown_text):
    """简单的Markdown转HTML（支持基本格式）"""
    html = markdown_text

    # 转义HTML特殊字符
    html = html.replace('&', '&amp;')
    html = html.replace('<', '&lt;')
    html = html.replace('>', '&gt;')

    # 标题
    html = html.replace('\n### ', '\n<h3>')
    html = html.replace('\n## ', '\n<h2>')
    html = html.replace('\n# ', '\n<h1>')
    html = html.replace('\n---', '\n<hr>')

    # 闭合标题（简单处理）
    lines = html.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('<h1>') and not line.endswith('</h1>'):
            line += '</h1>'
        elif line.startswith('<h2>') and not line.endswith('</h2>'):
            line += '</h2>'
        elif line.startswith('<h3>') and not line.endswith('</h3>'):
            line += '</h3>'
        new_lines.append(line)
    html = '\n'.join(new_lines)

    # 粗体
    import re
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # 列表项
    html = re.sub(r'^\s*-\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # 引用块
    html = re.sub(r'^\s*>\s*(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # 链接 [text](url)
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

    # 包裹在body中
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; }}
h1 {{ color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }}
h2 {{ color: #2c5aa0; margin-top: 30px; }}
h3 {{ color: #444; margin-top: 20px; }}
blockquote {{ background: #f0f7ff; border-left: 4px solid #1a73e8; margin: 0; padding: 10px 15px; }}
li {{ margin: 5px 0; }}
a {{ color: #1a73e8; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
strong {{ color: #d93025; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f5f5f5; }}
</style>
</head>
<body>
{html}
</body>
</html>"""

    return html


def send_email(subject, body_html, config):
    """发送邮件"""
    email_config = config.get('email', {})

    smtp_server = email_config.get('smtp_server', '')
    smtp_port = email_config.get('smtp_port', 587)
    username = email_config.get('username', '')
    password = email_config.get('password', '')
    to_address = email_config.get('to_address', '')
    from_address = email_config.get('from_address', username)

    if not all([smtp_server, username, to_address]):
        print("[错误] 邮件配置不完整，请检查SMTP设置")
        return False

    # 解析收件人（支持多邮箱，用逗号分隔）
    to_list = [addr.strip() for addr in to_address.split(',') if addr.strip()]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = ', '.join(to_list)

    # 添加HTML内容
    msg.attach(MIMEText(body_html, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls()
        server.login(username, password)
        server.sendmail(from_address, to_list, msg.as_string())
        server.quit()

        print(f"[成功] 邮件已发送到: {', '.join(to_list)}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[错误] SMTP认证失败，请检查邮箱账号和密码")
        print("提示: 如果使用Gmail，需要使用'应用专用密码'而非登录密码")
        return False
    except smtplib.SMTPConnectError:
        print(f"[错误] 无法连接到SMTP服务器: {smtp_server}:{smtp_port}")
        return False
    except Exception as e:
        print(f"[错误] 邮件发送失败: {e}")
        return False


def main():
    config = load_config()
    if not config:
        print("[错误] 配置文件不存在")
        sys.exit(1)

    if not config.get('report', {}).get('enable_email', False):
        print("[警告] 邮件功能未启用，请在配置中设置 enable_email: true")
        sys.exit(1)

    args = sys.argv[1:]
    report_path = None

    if "--report" in args:
        idx = args.index("--report")
        report_path = args[idx + 1] if idx + 1 < len(args) else None

    if not report_path or not os.path.exists(report_path):
        print("[错误] 请提供有效的报告文件路径: --report /path/to/report.md")
        sys.exit(1)

    # 读取报告内容
    with open(report_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # 转换为HTML
    html_content = markdown_to_html(markdown_content)

    # 生成邮件主题
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"[EaseUS热点日报] {today} — 话题调研报告"

    # 检查是否为周报（文件名含特定标记或周一）
    if datetime.now().weekday() == 0:  # 周一
        subject = f"[EaseUS热点周报] {today} — 话题调研报告"

    # 发送邮件
    success = send_email(subject, html_content, config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
