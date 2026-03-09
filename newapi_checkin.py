#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cron 0 9 * * *
# const $ = new Env('NewAPI自动签到')

import json
import os
from typing import Any, Dict, List, Optional

import requests

try:
    import notify
except ImportError:
    notify = None


def load_config() -> Dict[str, Any]:
    """加载 JSON 配置"""
    raw = os.getenv("NEWAPI_CONFIG", "").strip()
    if not raw:
        raise RuntimeError("未设置 NEWAPI_CONFIG 环境变量")

    if not raw.startswith("{"):
        raise RuntimeError("NEWAPI_CONFIG 必须为 JSON 字符串")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"NEWAPI_CONFIG JSON 解析失败: {e}")

    if not isinstance(data, dict):
        raise RuntimeError("NEWAPI_CONFIG 顶层必须是对象")
    return data


def parse_accounts(items: Any) -> List[Dict[str, str]]:
    """解析账号列表"""
    accounts: List[Dict[str, str]] = []
    if not isinstance(items, list):
        return accounts

    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or f"账号{idx}").strip() or f"账号{idx}"
        url = str(item.get("url") or "").strip()
        session = str(item.get("session") or "").strip()

        if url and session:
            accounts.append({"name": name, "url": url, "session": session})
    return accounts


def checkin(session: requests.Session, base_url: str, session_cookie: str) -> tuple[bool, str, Optional[int]]:
    """执行签到"""
    url = f"{base_url.rstrip('/')}/api/user/checkin"
    cookies = {"session": session_cookie}

    try:
        resp = session.post(url, cookies=cookies, timeout=30)
    except requests.RequestException as e:
        return False, f"请求异常: {e}", None

    if resp.status_code == 401:
        return False, "Session 已过期(401)，请更新", None
    if resp.status_code != 200:
        return False, f"签到失败 HTTP {resp.status_code}: {resp.text[:200]}", None

    try:
        data = resp.json()
    except Exception:
        return False, f"响应非 JSON: {resp.text[:200]}", None

    if isinstance(data, dict):
        success = data.get("success")
        message = str(data.get("message") or "").strip()
        quota = None

        if success is True:
            checkin_data = data.get("data", {})
            quota = checkin_data.get("quota_awarded")
            return True, message or "签到成功", quota
        if success is False:
            return False, message or f"签到失败: {data}", None

    return False, f"未知响应: {data}", None


def format_quota(quota: Optional[int]) -> str:
    """格式化额度显示"""
    if quota is None:
        return ""
    if quota >= 1000000:
        return f"{quota / 1000000:.2f}M ({quota:,} tokens)"
    if quota >= 1000:
        return f"{quota / 1000:.2f}K ({quota:,} tokens)"
    return f"{quota:,} tokens"


def main() -> None:
    try:
        config = load_config()
    except RuntimeError as e:
        print(str(e))
        return

    accounts = parse_accounts(config.get("accounts"))

    if not accounts:
        print("NEWAPI_CONFIG 未配置有效 accounts")
        return

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    })

    ok_count = 0
    fail_count = 0
    lines: List[str] = []

    print(f"NewAPI 开始签到，账号数: {len(accounts)}")

    for i, account in enumerate(accounts, start=1):
        name = account["name"]
        url = account["url"]
        session_cookie = account["session"]

        ok, msg, quota = checkin(session, url, session_cookie)
        if ok:
            ok_count += 1
            quota_str = format_quota(quota)
            detail = f"{msg} +{quota_str}" if quota_str else msg
            line = f"[{i}/{len(accounts)}] {name}: 成功 - {detail}"
            print(line)
            lines.append(line)
        else:
            fail_count += 1
            line = f"[{i}/{len(accounts)}] {name}: 失败 - {msg}"
            print(line)
            lines.append(line)

    summary = f"NewAPI 签到完成: 成功 {ok_count}, 失败 {fail_count}"
    print(summary)

    if notify:
        notify.send("NewAPI签到", summary + "\n\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
