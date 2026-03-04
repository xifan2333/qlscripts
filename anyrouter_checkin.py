#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cron 0 8 * * *
# const $ = new Env('AnyRouter自动签到')

import json
import os
from typing import Any, Dict, List, Tuple

import requests

try:
    import notify
except ImportError:
    notify = None

DEFAULT_BASE_URL = "https://blog.zhx47.top/anyrouter"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def load_config() -> Dict[str, Any]:
    raw = os.getenv("ANYROUTER_CONFIG", "").strip()
    if not raw:
        raise RuntimeError("未设置 ANYROUTER_CONFIG 环境变量")

    if not raw.startswith("{"):
        raise RuntimeError("ANYROUTER_CONFIG 必须为 JSON 字符串")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"ANYROUTER_CONFIG JSON 解析失败: {e}")

    if not isinstance(data, dict):
        raise RuntimeError("ANYROUTER_CONFIG 顶层必须是对象")
    return data


def parse_accounts(items: Any) -> List[Tuple[str, str]]:
    accounts: List[Tuple[str, str]] = []
    if not isinstance(items, list):
        return accounts

    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or f"账号{idx}").strip() or f"账号{idx}"
        cookie = str(item.get("cookie") or "").strip()
        if cookie:
            accounts.append((name, cookie))
    return accounts


def sign_in(session: requests.Session, base_url: str, cookie: str) -> Tuple[bool, str]:
    url = f"{base_url.rstrip('/')}/api/user/sign_in"
    try:
        resp = session.post(url, headers={"Cookie": cookie}, timeout=30)
    except requests.RequestException as e:
        return False, f"请求异常: {e}"

    if resp.status_code == 401:
        return False, "Cookie 无效(401)，请更新"
    if resp.status_code != 200:
        return False, f"签到失败 HTTP {resp.status_code}: {resp.text[:200]}"

    try:
        data = resp.json()
    except Exception:
        return False, f"响应非 JSON: {resp.text[:200]}"

    if isinstance(data, dict):
        success = data.get("success")
        message = str(data.get("message") or "").strip()

        if success is True:
            return True, message or "今日已签到"
        if success is False:
            return False, message or f"签到失败: {data}"

    return True, f"返回: {data}"


def main() -> None:
    try:
        config = load_config()
    except RuntimeError as e:
        print(str(e))
        return

    base_url = str(config.get("base_url") or DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    accounts = parse_accounts(config.get("accounts"))

    if not accounts:
        print("ANYROUTER_CONFIG 未配置有效 accounts")
        return

    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    ok_count = 0
    fail_count = 0
    lines: List[str] = []

    print(f"AnyRouter 开始签到，账号数: {len(accounts)}")
    print(f"签到地址: {base_url}")

    for i, (name, cookie) in enumerate(accounts, start=1):
        ok, msg = sign_in(session, base_url, cookie)
        if ok:
            ok_count += 1
            line = f"[{i}/{len(accounts)}] {name}: 成功 - {msg}"
            print(line)
            lines.append(line)
        else:
            fail_count += 1
            line = f"[{i}/{len(accounts)}] {name}: 失败 - {msg}"
            print(line)
            lines.append(line)

    summary = f"AnyRouter 签到完成: 成功 {ok_count}, 失败 {fail_count}"
    print(summary)

    if notify:
        notify.send("AnyRouter签到", summary + "\n\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
