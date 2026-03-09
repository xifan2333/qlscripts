# qlscripts

青龙面板自用脚本集合。

## 订阅

```bash
ql repo https://github.com/xifan2333/qlscripts.git "" "backup|deprecated" "utils" "main" "js|ts|py|sh"
```

## 脚本列表

| 脚本 | 说明 | 定时 | 环境变量 |
|------|------|------|----------|
| gpt_autopool.py | 账号池自动维护（清理401 + 补号） | `0 2 * * *` | `GPT_POOL_CONFIG`、`POOL_MIN_CANDIDATES`、`POOL_TIMEOUT` |
| anyrouter_checkin.py | AnyRouter 自动签到（支持多账号） | `0 8 * * *` | `ANYROUTER_CONFIG` |
| newapi_checkin.py | NewAPI 自动签到（支持多账号） | `0 9 * * *` | `NEWAPI_CONFIG` |

## 环境变量说明

### gpt_autopool.py

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `GPT_POOL_CONFIG` | 是 | JSON 配置字符串（仅支持 JSON 字符串，不支持文件路径） |
| `POOL_MIN_CANDIDATES` | 否 | 覆盖配置中的最小候选账号阈值 |
| `POOL_TIMEOUT` | 否 | 接口超时秒数，默认 15 |

`GPT_POOL_CONFIG` 示例值（JSON 字符串）：

```json
{
  "clean": {
    "base_url": "http://your-api:8317",
    "token": "your-token",
    "target_type": "codex",
    "workers": 20,
    "delete_workers": 20,
    "timeout": 10,
    "retries": 1
  },
  "email": {
    "worker_domain": "mail.example.com",
    "email_domains": ["example.com"],
    "admin_password": "your-password"
  },
  "maintainer": {
    "min_candidates": 100
  },
  "run": {
    "workers": 8,
    "proxy": ""
  },
  "oauth": {
    "issuer": "https://auth.openai.com",
    "client_id": "app_EMoamEEZ73f0CkXaXp7hrann",
    "redirect_uri": "http://localhost:1455/auth/callback"
  },
  "output": {
    "save_local": false
  }
}
```

### anyrouter_checkin.py

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `ANYROUTER_CONFIG` | 是 | JSON 配置字符串，包含 `base_url` 与 `accounts` |

`ANYROUTER_CONFIG` 示例：

```json
{
  "base_url": "https://blog.zhx47.top/anyrouter",
  "accounts": [
    {
      "name": "xifan",
      "cookie": "session=xxxx;"
    }
  ]
}
```

### newapi_checkin.py

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `NEWAPI_CONFIG` | 是 | JSON 配置字符串，包含 `accounts` 列表 |

`NEWAPI_CONFIG` 示例：

```json
{
  "accounts": [
    {
      "name": "主账号",
      "url": "https://api.example.com",
      "session": "your_session_cookie_here"
    },
    {
      "name": "备用账号",
      "url": "https://api2.example.com",
      "session": "another_session_cookie"
    }
  ]
}
```

Node.js 依赖会在订阅时自动安装（`package.json`）。Python 依赖需手动安装或通过面板依赖管理安装（`requirements.txt`）。
