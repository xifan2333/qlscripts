#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cron 0 9 * * *
# const $ = new Env('NewAPI自动签到')

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import requests

try:
    import notify
except ImportError:
    notify = None


def load_config() -> Dict[str, Any]:
    raw = os.getenv("NEWAPI_CONFIG", "").strip()
    if not raw:
        raise RuntimeError("未设置 NEWAPI_CONFIG 环境变量")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"NEWAPI_CONFIG JSON 解析失败: {e}")

    if not isinstance(data, dict):
        raise RuntimeError("NEWAPI_CONFIG 顶层必须是对象")
    return data


def parse_accounts(config: Dict[str, Any]) -> List[Dict[str, str]]:
    items = config.get("accounts", {}).get("accounts", [])
    accounts: List[Dict[str, str]] = []

    for item in items:
        if not isinstance(item, dict) or item.get("disabled"):
            continue
        if (item.get("site_type") or "").lower() != "new-api":
            continue
        health = item.get("health") or {}
        if "access token 无效" in str(health.get("reason") or ""):
            continue

        info = item.get("account_info") or {}
        url = str(item.get("site_url") or "").strip()
        user_id = info.get("id")
        access_token = str(info.get("access_token") or "").strip()
        name = str(item.get("site_name") or url).strip()

        if url and user_id and access_token:
            accounts.append({
                "name": name,
                "url": url,
                "user_id": str(user_id),
                "access_token": access_token,
            })
    return accounts


def checkin(sess: requests.Session, base_url: str, user_id: str, access_token: str) -> Tuple[bool, str, Optional[int]]:
    url = f"{base_url.rstrip('/')}/api/user/checkin"
    headers = {
        "new-api-user": user_id,
        "Authorization": f"Bearer {access_token}",
    }

    try:
        resp = sess.post(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        return False, f"请求异常: {e}", None

    try:
        data = resp.json()
    except Exception:
        return False, f"HTTP {resp.status_code} 响应非 JSON: {resp.text[:200]}", None

    success = data.get("success")
    message = str(data.get("message") or "").strip()

    if success is True:
        checkin_data = data.get("data") or {}
        quota = checkin_data.get("quota_awarded")
        return True, message or "签到成功", quota

    if "已签到" in message:
        return True, message, None

    return False, message or f"签到失败: {data}", None


def format_quota(quota: Optional[int]) -> str:
    if quota is None:
        return ""
    if quota >= 1000000:
        return f"${quota / 500000:.2f} ({quota:,} tokens)"
    if quota >= 1000:
        return f"${quota / 500000:.4f} ({quota:,} tokens)"
    return f"{quota:,} tokens"


def main() -> None:
    try:
        config = load_config()
    except RuntimeError as e:
        print(str(e))
        return

    accounts = parse_accounts(config)

    if not accounts:
        print("NEWAPI_CONFIG 未找到有效的 new-api 类型账号")
        return

    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    })

    ok_count = 0
    fail_count = 0
    lines: List[str] = []

    print(f"NewAPI 开始签到，账号数: {len(accounts)}")

    for i, account in enumerate(accounts, start=1):
        name = account["name"]
        ok, msg, quota = checkin(sess, account["url"], account["user_id"], account["access_token"])
        if ok:
            ok_count += 1
            quota_str = format_quota(quota)
            detail = f"{msg} +{quota_str}" if quota_str else msg
            line = f"[{i}/{len(accounts)}] {name}: 成功 - {detail}"
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
