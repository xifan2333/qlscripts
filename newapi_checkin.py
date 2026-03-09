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


def parse_accounts(items: Any) -> List[Dict[str, str]]:
    accounts: List[Dict[str, str]] = []
    if not isinstance(items, list):
        return accounts

    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or f"账号{idx}").strip() or f"账号{idx}"
        url = str(item.get("url") or "").strip()
        user_id = str(item.get("user_id") or "").strip()
        access_token = str(item.get("access_token") or "").strip()

        if not url or not user_id or not access_token:
            print(f"账号{idx} ({name}): 缺少 url/user_id/access_token，跳过")
            continue

        accounts.append({
            "name": name,
            "url": url,
            "user_id": user_id,
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

    accounts = parse_accounts(config.get("accounts"))

    if not accounts:
        print("NEWAPI_CONFIG 未配置有效 accounts（需要 url + user_id + access_token）")
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
