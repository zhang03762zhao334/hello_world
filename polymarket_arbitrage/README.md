# Polymarket套利程序

这是一个完整的Polymarket预测市场套利机器人，能够自动检测和执行套利交易。

## 功能特性

- 🔍 **自动检测套利机会** - 监控Polymarket市场中的互补对价格
- 📊 **实时市场数据** - 从Polymarket API获取最新的订单簿和价格
- 🤖 **自动交易执行** - 自动下单和管理头寸（支持模拟和实盘模式）
- 💰 **利润计算** - 精确计算套利利润和风险
- 📈 **性能追踪** - 数据库记录所有交易历史和统计
- 🛡️ **风险管理** - 头寸大小限制、损失控制

## 项目结构

```
polymarket_arbitrage/
├── config/
│   ├── settings.py          # 配置设置
│   └── logger.py            # 日志配置
├── src/
│   ├── models.py            # 数据模型
│   ├── polymarket_api.py    # Polymarket API客户端
│   ├── arbitrage_detector.py # 套利检测引擎
│   ├── trade_executor.py    # 交易执行引擎
│   ├── database.py          # 交易数据库
│   └── arbitrage_bot.py     # 主机器人类
├── main.py                  # 程序入口
├── requirements.txt         # Python依赖
├── .env.example             # 环境变量模板
└── README.md               # 说明文档
```

## 安装

### 前置要求
- Python 3.8+
- pip包管理器

### 安装步骤

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
```

编辑 `.env` 文件并填入你的配置：
```
POLYMARKET_PRIVATE_KEY=你的私钥
POLYMARKET_WALLET_ADDRESS=你的钱包地址
POLYGON_RPC_URL=https://polygon-rpc.com
ENABLE_TRADING=false  # 设置为true以启用真实交易
```

## 使用方法

### 运行模拟模式（推荐先用这个测试）

```bash
python main.py
```

这会在模拟模式下运行，不会执行真实交易。

### 启用真实交易

1. 确保你的私钥和钱包地址正确配置在 `.env` 文件中
2. 在 `.env` 中设置 `ENABLE_TRADING=true`
3. 确保钱包中有足够的USDC资金
4. 运行程序：

```bash
python main.py
```

## 核心模块说明

### 1. Polymarket API客户端 (`polymarket_api.py`)
- 获取市场列表和详情
- 获取订单簿数据
- 创建和取消订单
- 查询用户头寸

### 2. 套利检测引擎 (`arbitrage_detector.py`)
- 扫描所有市场寻找互补对
- 计算互补对价格之和
- 识别价格不一致的套利机会
- 计算利润率和最大交易大小

**套利逻辑说明：**
- 在二元市场中，YES和NO的价格之和应该等于1.0
- 如果价格之和 < 1.0，则存在套利机会
- 套利方式：同时买入YES和NO，等待平仓获利

### 3. 交易执行引擎 (`trade_executor.py`)
- 订单签名（支持EIP-191标准）
- 创建买入和卖出订单
- 头寸管理和平仓
- 支持模拟和实盘两种模式

### 4. 数据库 (`database.py`)
- SQLite数据库用于存储交易历史
- 查询和统计交易数据
- 性能监控

### 5. 主机器人 (`arbitrage_bot.py`)
- 协调所有组件
- 定期扫描市场
- 执行套利交易
- 显示统计信息

## 配置说明

在 `config/settings.py` 中可以调整以下参数：

```python
MIN_PROFIT_PERCENTAGE = 0.5      # 最小利润率 (%)，小于此值的机会会被忽略
MAX_POSITION_SIZE = 100.0         # 最大头寸大小 (USDC)
CHECK_INTERVAL = 5                # 市场扫描间隔 (秒)
ENABLE_TRADING = False            # 启用真实交易
```

## 安全建议

1. **私钥管理**
   - 永远不要将私钥提交到版本控制系统
   - 使用环境变量或 `.env` 文件存储敏感信息
   - 定期轮换密钥

2. **资金管理**
   - 从小额测试开始
   - 设置合理的头寸大小限制
   - 定期监控交易历史

3. **市场风险**
   - 虽然套利应该是无风险的，但执行延迟可能导致风险
   - 市场流动性可能不足，影响订单填充
   - 定期检查交易统计以发现问题

## 监控和日志

程序会在 `logs/` 目录下生成每日日志文件：
```
logs/arbitrage_20240101.log
```

日志包含：
- 检测到的套利机会
- 执行的交易
- API错误和异常
- 性能统计

## 性能统计

运行完毕后或通过数据库可以查看：
- 总交易数
- 已平仓的交易数
- 总利润
- 平均利润率
- 单笔最大利润

## 故障排除

### 问题：未检测到套利机会
- 检查网络连接
- 验证Polymarket API是否可访问
- 检查市场流动性是否充足
- 降低最小利润率阈值

### 问题：订单创建失败
- 验证私钥格式是否正确
- 检查钱包是否有足够余额
- 查看API返回的具体错误信息

### 问题：交易利润计算不准确
- 注意gas费用（当前代码未计入）
- 注意Maker/Taker费用
- 检查是否有滑点

## 未来改进方向

- [ ] 集成多个市场平台（Manifold Markets等）
- [ ] 跨平台套利检测
- [ ] 高级风险管理（止损、获利了结）
- [ ] 机器学习预测市场走向
- [ ] Web UI仪表板
- [ ] 实时警报通知（Discord、Telegram）
- [ ] 高级交易策略（market-making等）

## 许可证

MIT License

## 免责声明

本程序用于教育和研究目的。使用本程序进行交易时请自担风险。不对任何交易损失负责。

## 联系方式

如有问题或建议，欢迎提交Issue或PR。
