# Douyin Pet Monitor

本项目现在是一个 **Tauri v2 原生桌面应用**。界面使用 Vue 3 + TypeScript，数据处理继续使用 Python 3.12，SQLite 本地存储，支持 CSV/Excel 导入、重复导入更新、达人评分、筛选和 Excel 导出。

打包完成后，普通使用者只需要安装 Windows `.exe` 或 macOS `.dmg/.app`，不需要打开终端，也不需要自己安装 Python、Node.js 或 Rust。

## 功能

- CSV/Excel 导入达人数据
- 字段：`nickname`、`profile_url`、`fans`、`category`、`sales_30d`、`gmv_30d`、`product_count`、`live_count_7d`、`median_likes`
- 自动计算 `sales_per_fan = sales_30d / fans`
- 自动计算 `score`
- 相同 `profile_url` 再次导入时更新原数据
- Tauri 桌面页面展示榜单
- 支持筛选粉丝数、销量、类目
- 支持导出当前筛选结果为 Excel
- 使用 Playwright 做前端 smoke test

本项目不包含绕过平台风控、登录、验证码、加密接口或非公开接口的代码。

## 架构

- `app/`：Python 后端逻辑，负责 CSV/Excel 导入、SQLite、评分、Excel 导出
- `app/cli.py`：给 Tauri 调用的 JSON CLI
- `scripts/build_backend.py`：用 PyInstaller 构建 Python sidecar
- `desktop/`：Tauri + Vue 桌面应用
- `desktop/src-tauri/binaries/`：sidecar 输出目录，由构建脚本生成

## 评分规则

标准 CSV 各项指标先做 Min-Max 标准化，再按权重相加并转换为 `0-100` 分：

- `sales_per_fan`: 35%
- `sales_30d`: 25%
- `gmv_30d`: 15%
- `median_likes`: 10%
- `live_count_7d`: 10%
- `product_count`: 5%

达多多 Excel 会优先使用文件中的真实字段评分：

- `预估结算金额`: 30%
- `带货等级`: 20%
- `视频数`: 15%
- `平均赞粉比`: 15%
- `平均获赞数`: 10%
- `推广商品数`: 10%

## Windows 开发与打包步骤

1. 安装 Python 3.12，并勾选 `Add python.exe to PATH`。
2. 安装 Node.js LTS。
3. 安装 Rust。可使用 `rustup` 官方安装器。
4. 在项目根目录打开 PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts\build_backend.py
```

5. 安装桌面端依赖：

```powershell
cd desktop
npm install
```

6. 启动开发版：

```powershell
npm run tauri dev
```

7. 打包 Windows 安装包：

```powershell
npm run tauri build
```

打包产物在 `desktop/src-tauri/target/release/bundle/` 下。

## macOS 开发与打包步骤

1. 安装 Python 3.12、Node.js LTS、Rust：

```bash
brew install python@3.12 node rustup-init
rustup-init
```

2. 在项目根目录创建 Python 虚拟环境：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/build_backend.py
```

3. 安装桌面端依赖：

```bash
cd desktop
npm install
```

4. 启动开发版：

```bash
npm run tauri dev
```

5. 打包 macOS 应用：

```bash
npm run tauri build
```

打包产物在 `desktop/src-tauri/target/release/bundle/` 下。

## CI 自动打包

- 推送到 `main` 后，GitHub Actions 会自动构建 macOS 和 Windows 安装包，并保留为 artifact。
- 推送 `v*` 标签后，GitHub Actions 会自动创建 Release，并附上 macOS `.dmg` 和 Windows `.exe`。
- Windows 安装包在 `desktop/src-tauri/target/release/bundle/nsis/`。
- macOS 安装包在 `desktop/src-tauri/target/release/bundle/dmg/`。

如果构建时从 `crates.io` 下载 Rust 依赖超时，项目已内置 `.cargo/config.toml` 使用 `rsproxy` sparse 镜像。确认在项目根目录执行命令后，重新运行 `npm run tauri build` 即可。

## CSV/Excel 导入

CSV 必须包含这些列：

```text
nickname,profile_url,fans,category,sales_30d,gmv_30d,product_count,live_count_7d,median_likes
```

示例文件：

```text
data/sample_creators.csv
```

桌面应用里点击 `导入 CSV/Excel`，选择文件即可。每日重复导入时，相同 `profile_url` 会更新已有记录。

达多多 Excel 支持这些列：

```text
达人名称,达人抖音id,带货等级,视频数,粉丝总量,平均获赞数,平均赞粉比,推广商品数,预估结算金额
```

桌面应用里点击 `导入 CSV/Excel`，选择 `.xlsx` 文件即可。系统会保留抖音 ID、带货等级、视频数、赞粉比和预估结算金额，并支持按这些字段筛选和导出。

## Excel 导出

桌面应用里先设置筛选条件，再点击 `导出 Excel`。导出的 Excel 与当前筛选结果一致。

## Playwright Smoke Test

先启动前端开发服务：

```bash
cd desktop
npm run dev
```

再回到项目根目录运行：

```bash
python scripts/browser_check.py
```

脚本会访问 `http://localhost:1420` 并保存截图到 `exports/desktop_frontend.png`。

## 测试

Python 后端测试：

```bash
pytest -q
```

桌面前端构建测试：

```bash
cd desktop
npm run build
```
