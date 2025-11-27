# Polymarket套利机器人 - 快速开始指南

## 📋 目录
1. [系统要求](#系统要求)
2. [安装步骤](#安装步骤)
3. [配置](#配置)
4. [运行程序](#运行程序)
5. [常见问题](#常见问题)

## 系统要求

- Python 3.8 或更高版本
- pip 包管理器
- 互联网连接
- Polymarket账户和钱包

## 安装步骤

### 步骤 1: 克隆或下载项目

```bash
cd polymarket_arbitrage
```

### 步骤 2: 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 步骤 3: 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

### 1. 设置环境变量

复制模板文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```bash
# 使用你喜欢的编辑器打开 .env
# 例如：
nano .env
```

### 2. 获取你的私钥

**通过MetaMask:**
1. 打开MetaMask浏览器扩展
2. 点击菜单 → "账户详情" → "导出私钥"
3. 输入密码并复制私钥
4. 粘贴到 `.env` 文件中

**注意安全:**
- ⚠️ 永远不要分享你的私钥！
- ⚠️ 不要将私钥上传到公开的GitHub仓库
- ⚠️ `.env` 文件应该在 `.gitignore` 中

### 3. 配置 `.env` 文件

```env
# 复制你的私钥（不需要0x前缀）
POLYMARKET_PRIVATE_KEY=abc123def456...

# 你的钱包地址
POLYMARKET_WALLET_ADDRESS=0x...

# RPC端点（保持默认即可）
POLYGON_RPC_URL=https://polygon-rpc.com

# 测试模式：false（推荐先用这个）
ENABLE_TRADING=false

# 日志级别
LOG_LEVEL=INFO
```

## 运行程序

### 运行模式 1: 模拟模式（推荐）

```bash
python main.py
```

这会在模拟模式下运行，**不会执行真实交易**，但会：
- ✓ 连接到Polymarket API
- ✓ 扫描市场
- ✓ 检测套利机会
- ✓ 模拟交易执行
- ✓ 记录日志

### 运行模式 2: 测试脚本

```bash
python test.py
```

运行测试检查：
- API连接
- 套利检测逻辑
- 配置信息

### 运行模式 3: 实盘交易

**⚠️ 只有在完全理解风险后才启用！**

1. 确保模拟模式测试通过
2. 在 `.env` 中设置 `ENABLE_TRADING=true`
3. 确保钱包中有足够USDC资金
4. 运行程序：
```bash
python main.py
```

## 常见问题

### Q1: "Module not found" 错误

**A:** 确保你在项目根目录并激活了虚拟环境

```bash
# 检查当前目录
pwd

# 确认在 polymarket_arbitrage 目录中

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### Q2: "POLYGON_RPC_URL" 错误

**A:** 检查 `.env` 文件配置

```bash
# .env 应该包含
POLYGON_RPC_URL=https://polygon-rpc.com
```

### Q3: 无法连接到Polymarket API

**A:** 
- 检查网络连接
- 验证API端点是否可访问：
```bash
curl -I https://gamma-api.polymarket.com
```

### Q4: "私钥格式错误"

**A:** 私钥应该是：
- 64个十六进制字符（不带0x前缀）
- 或完整的128个字符（带0x前缀也可以）

### Q5: 未检测到套利机会

**A:** 这很正常，因为：
- 市场效率通常较高
- 套利机会比较罕见
- 可以降低 `MIN_PROFIT_PERCENTAGE` 来扩大搜索范围

在 `config/settings.py` 中修改：
```python
MIN_PROFIT_PERCENTAGE = 0.2  # 从0.5改为0.2
```

### Q6: 如何停止程序？

**A:** 按 `Ctrl+C` 中断程序

程序会：
- ✓ 平仓所有活跃交易
- ✓ 显示交易统计
- ✓ 保存日志

## 监控和日志

### 查看日志

```bash
# 查看最新的日志文件
tail -f logs/arbitrage_*.log

# 查看特定日期的日志
cat logs/arbitrage_20240101.log
```

### 查看交易历史

```bash
# SQLite数据库存储在 polymarket_trades.db
# 使用 sqlite3 命令行查看

# 查看最近的交易
sqlite3 polymarket_trades.db "SELECT * FROM trades ORDER BY executed_at DESC LIMIT 10;"
```

## 性能优化建议

1. **调整检查间隔**
   - 增加 `CHECK_INTERVAL` 以降低API调用频率
   - 减少 `CHECK_INTERVAL` 以增加检测频率

2. **调整头寸大小**
   - 在 `config/settings.py` 中修改 `MAX_POSITION_SIZE`

3. **并行处理**
   - 当前程序顺序处理，可以扩展为并发处理

## 风险管理

### 推荐做法

1. **从小额开始**
   ```python
   MAX_POSITION_SIZE = 10.0  # 先用$10测试
   ```

2. **监控交易**
   - 定期检查日志
   - 核查交易是否按预期执行

3. **定期统计**
   ```bash
   sqlite3 polymarket_trades.db "SELECT * FROM trades WHERE status='closed';"
   ```

## 获取帮助

### 有用的资源

1. **Polymarket API文档**
   - https://polymarket.com/api

2. **Polygon网络信息**
   - https://polygon.technology

3. **以太坊开发资源**
   - https://ethereum.org/developers

### 调试技巧

1. 增加日志级别：
   ```env
   LOG_LEVEL=DEBUG
   ```

2. 检查API响应：在 `src/polymarket_api.py` 中添加调试打印

3. 验证订单数据：检查日志中的订单详情

## 下一步

完成基本设置后，你可以：

1. ✓ 运行测试脚本验证环境
2. ✓ 以模拟模式运行几小时观察
3. ✓ 检查生成的日志和数据库
4. ✓ 根据结果调整参数
5. ✓ 选择性地启用实盘交易

祝你好运！🚀
