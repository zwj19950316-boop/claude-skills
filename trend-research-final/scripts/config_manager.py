#!/usr/bin/env python3
"""配置管理脚本 — 热点调研skill的配置初始化与管理"""

import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "trend-research"
CONFIG_FILE = CONFIG_DIR / "config.json"
REPORTS_DIR = Path.home() / ".config" / "trend-reports"

DEFAULT_CONFIG = {
    "brand": {
        "name": "EaseUS",
        "youtube": "@Easeus-official",
        "tiktok": "@easeus_official",
        "products": ["EaseUS Data Recovery Wizard", "EaseUS Partition Master"]
    },
    "domains": {
        "windows-system": {
            "description": "Windows系统更新、故障、优化",
            "keywords": [
                "Windows 11 update problems",
                "Windows 10 update stuck",
                "Windows blue screen",
                "Windows not booting",
                "Windows storage full",
                "C drive full Windows",
                "Windows system repair",
                "Windows partition resize",
                "Windows 24H2 issues",
                "KB update problems"
            ]
        },
        "data-recovery": {
            "description": "数据恢复场景和需求",
            "keywords": [
                "recover deleted files",
                "hard drive data recovery",
                "SD card recovery",
                "USB drive not showing files",
                "formatted drive recovery",
                "recycle bin recovery",
                "SSD data recovery",
                "external hard drive corrupted",
                "photo recovery",
                "document recovery"
            ]
        },
        "storage-device": {
            "description": "存储设备和分区管理",
            "keywords": [
                "partition manager",
                "resize partition",
                "merge partitions",
                "SSD vs HDD",
                "external SSD review",
                "NAS setup",
                "USB flash drive repair",
                "disk full solution",
                "move space from D to C",
                "extend C drive"
            ]
        }
    },
    "competitors": {
        "youtube": [
            "@Britec09", "@Jayztwocents", "@UFDTech", "@METAPCs",
            "@cleverfiles", "@ThioJoe", "@ZachsTechTurf", "@TheGrumpySysadmin",
            "@RecoveritDataRecoverySoftware", "@Tenorshare4DDiGDataRecovery",
            "@BrenTech", "@WCT", "@CyberCPU", "@AskYourComputerGuy",
            "@CrownGEEK", "@BrettInTech"
        ],
        "twitter": ["Windows"],
        "facebook": []
    },
    "email": {
        "smtp_server": "",
        "smtp_port": 587,
        "username": "",
        "password": "",
        "to_address": "zhousibo@info.easeus.com.cn, zhouweijiao@info.easeus.com.cn",
        "from_address": "EaseUS TrendBot <trend@easeus.com>"
    },
    "report": {
        "language": "zh",
        "max_hot_topics": 15,
        "competitor_video_limit": 5,
        "enable_email": False
    }
}


def ensure_dirs():
    """确保配置目录和报告目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    """加载配置文件，如不存在返回None"""
    if not CONFIG_FILE.exists():
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[错误] 配置文件读取失败: {e}")
        return None


def save_config(config):
    """保存配置到文件"""
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"[成功] 配置已保存到: {CONFIG_FILE}")


def check_config():
    """检查配置完整性，返回(bool, message)"""
    config = load_config()
    if config is None:
        return False, "配置文件不存在，请先运行初始化"

    missing = []
    if not config.get("email", {}).get("smtp_server"):
        missing.append("SMTP服务器地址")
    if not config.get("email", {}).get("username"):
        missing.append("发件邮箱账号")
    if not config.get("email", {}).get("to_address"):
        missing.append("收件邮箱地址")

    if missing:
        return False, f"配置不完整，缺少: {', '.join(missing)}"

    return True, "配置完整"


def interactive_init():
    """交互式初始化配置"""
    ensure_dirs()
    print("=== EaseUS 热点调研 — 配置初始化 ===\n")

    config = DEFAULT_CONFIG.copy()

    # 品牌信息
    print("[品牌信息]")
    brand_name = input(f"品牌名称 [{config['brand']['name']}]: ").strip()
    if brand_name:
        config["brand"]["name"] = brand_name

    # 邮箱配置
    print("\n[邮件推送配置] (留空则禁用邮件功能)")
    smtp_server = input("SMTP服务器 [例如: smtp.gmail.com]: ").strip()
    if smtp_server:
        config["email"]["smtp_server"] = smtp_server

        smtp_port = input("SMTP端口 [587]: ").strip()
        config["email"]["smtp_port"] = int(smtp_port) if smtp_port else 587

        username = input("发件邮箱账号: ").strip()
        if username:
            config["email"]["username"] = username

        password = input("邮箱密码/应用专用密码: ").strip()
        if password:
            config["email"]["password"] = password

        to_address = input(
            f"收件邮箱 [{config['email']['to_address']}]: ").strip()
        if to_address:
            config["email"]["to_address"] = to_address

        config["report"]["enable_email"] = bool(
            config["email"]["smtp_server"] and config["email"]["username"]
        )

    # 竞争对手
    print("\n[竞争对手账号]")
    print("已预设以下YouTube竞品频道，可直接使用或修改:")
    for ch in config["competitors"]["youtube"]:
        print(f"  - {ch}")

    add_more = input("\n是否添加更多竞争对手? (y/n) [n]: ").strip().lower()
    if add_more == "y":
        while True:
            new_ch = input("输入YouTube频道handle (带@，或空行结束): ").strip()
            if not new_ch:
                break
            if new_ch not in config["competitors"]["youtube"]:
                config["competitors"]["youtube"].append(new_ch)

    # 关键词
    print("\n[搜索关键词]")
    print("已预设各领域关键词，如需修改请直接编辑配置文件")

    # 保存
    save_config(config)
    print("\n=== 初始化完成 ===")
    print(f"配置文件路径: {CONFIG_FILE}")
    print("后续可用以下命令管理配置:")
    print("  python config_manager.py check  # 检查配置")
    print("  python config_manager.py show   # 查看配置(脱敏)")


def show_config():
    """显示当前配置（脱敏）"""
    config = load_config()
    if not config:
        print("[错误] 配置文件不存在")
        return

    safe_config = json.loads(json.dumps(config))
    if "password" in safe_config.get("email", {}):
        safe_config["email"]["password"] = "********"

    print(json.dumps(safe_config, indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print("用法: python config_manager.py [init|check|show]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        interactive_init()
    elif cmd == "check":
        ok, msg = check_config()
        print(f"[{'通过' if ok else '失败'}] {msg}")
        sys.exit(0 if ok else 1)
    elif cmd == "show":
        show_config()
    else:
        print(f"[错误] 未知命令: {cmd}")
        print("用法: python config_manager.py [init|check|show]")
        sys.exit(1)


if __name__ == "__main__":
    main()
