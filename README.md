# qlscripts

青龙面板自用脚本集合。

## 订阅

```bash
ql repo https://github.com/xifan2333/qlscripts.git "ql_" "backup|deprecated" "utils" "main" "js|ts|py|sh"
```

## 脚本列表

| 脚本 | 说明 | 定时 | 环境变量 |
|------|------|------|----------|
| ql_pool_maintainer.py | 账号池自动维护（清理401 + 补号） | `37 */4 * * *` | `POOL_MAINTAINER_CONFIG` |

## 环境变量说明

### ql_pool_maintainer.py

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `POOL_MAINTAINER_CONFIG` | 是 | JSON 配置字符串或配置文件路径 |
| `POOL_MIN_CANDIDATES` | 否 | 覆盖配置中的最小候选账号阈值 |
| `POOL_TIMEOUT` | 否 | 接口超时秒数，默认 15 |

`POOL_MAINTAINER_CONFIG` 示例值（JSON 字符串）：

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

## 依赖

Node.js 依赖会在订阅时自动安装（`package.json`）。Python 依赖需手动安装或通过面板依赖管理安装（`requirements.txt`）。
