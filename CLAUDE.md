# qlscripts - 青龙面板脚本仓库

## 项目概述

青龙 (QingLong) 面板自用定时任务脚本集合，支持 JavaScript/TypeScript/Python/Shell。

## 仓库结构

```
qlscripts/
├── ql_*.js / ql_*.ts / ql_*.py / ql_*.sh   # 脚本（根目录，ql_ 前缀）
├── utils/                                     # 共享工具模块（非任务文件）
├── package.json                               # Node.js 依赖
├── requirements.txt                           # Python 依赖
└── README.md                                  # 订阅说明与脚本列表
```

## 脚本规范

### 命名

- 所有脚本使用 `ql_` 前缀：`ql_<平台>_<功能>.js`
- 示例：`ql_bilibili_signin.js`、`ql_alipan_checkin.py`

### 头部元数据（必须）

青龙面板通过解析头部注释自动创建定时任务：

**JavaScript/TypeScript:**
```javascript
/*
 * cron 30 8 * * *
 * new Env('脚本显示名称')
 */
```

**Python:**
```python
# cron 0 9 * * *
# const $ = new Env('脚本显示名称')
```

**Shell:**
```bash
# cron 0 10 * * *
# const $ = new Env('脚本显示名称')
```

### JavaScript 脚本模板

```javascript
/*
 * cron 30 8 * * *
 * new Env('示例脚本')
 */

const axios = require('axios');
const notify = require('./sendNotify');

const TOKEN = process.env.EXAMPLE_TOKEN || '';

!(async () => {
  if (!TOKEN) {
    console.log('未设置 EXAMPLE_TOKEN 环境变量');
    return;
  }
  // 业务逻辑
  let message = '';
  // ...
  if (message) {
    await notify.sendNotify('示例脚本', message);
  }
})().catch(e => console.error(e));
```

### Python 脚本模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cron 0 9 * * *
# const $ = new Env('示例脚本')

import os
import requests

try:
    import notify
except ImportError:
    notify = None

TOKEN = os.getenv("EXAMPLE_TOKEN", "")

def main():
    if not TOKEN:
        print("未设置 EXAMPLE_TOKEN 环境变量")
        return
    # 业务逻辑
    msg = ""
    # ...
    if msg and notify:
        notify.send("示例脚本", msg)

if __name__ == "__main__":
    main()
```

## 关键约定

1. **环境变量**：所有敏感信息（cookie、token）通过青龙面板环境变量管理，脚本中通过 `process.env` / `os.getenv` 读取，禁止硬编码
2. **通知**：使用青龙内置的 `sendNotify.js`（JS）或 `notify.py`（Python）
3. **多账号**：环境变量中多账号用换行符 `\n` 分隔
4. **定时**：避免整点集中，使用随机偏移（如 `:15`、`:37`）
5. **依赖**：Node.js 依赖写入 `package.json`，Python 依赖写入 `requirements.txt`
6. **工具模块**：放入 `utils/` 目录，通过订阅命令的 dependence 参数同步
