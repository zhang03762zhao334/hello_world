# Polymarket套利机器人 - 高级配置指南

## 📊 高级参数调优

### 1. 利润率阈值调整

在 `config/settings.py` 中：

```python
# 保守策略（利润率高、但机会少）
MIN_PROFIT_PERCENTAGE = 2.0  # 只做利润≥2%的交易

# 积极策略（机会多、但利润较小）
MIN_PROFIT_PERCENTAGE = 0.2  # 做利润≥0.2%的交易

# 平衡策略（推荐）
MIN_PROFIT_PERCENTAGE = 0.5  # 做利润≥0.5%的交易
```

**如何选择：**
- 市场流动性好→可以降低阈值
- 初期测试→使用较高的阈值（1-2%）
- 成熟运营→可降低阈值到0.3-0.5%

### 2. 头寸大小管理

```python
# 小额测试
MAX_POSITION_SIZE = 10.0   # $10

# 中额操作
MAX_POSITION_SIZE = 100.0  # $100

# 大额操作
MAX_POSITION_SIZE = 1000.0 # $1000
```

**风险计算：**
```python
# 考虑执行风险和滑点
# 实际可用资金 = MAX_POSITION_SIZE × 0.8
```

### 3. 市场扫描频率

```python
# 快速扫描（高CPU，更容易检测到机会）
CHECK_INTERVAL = 2  # 每2秒检查一次

# 平衡扫描
CHECK_INTERVAL = 5  # 每5秒检查一次（推荐）

# 低频扫描（低CPU，可能错过机会）
CHECK_INTERVAL = 15 # 每15秒检查一次
```

## 🎯 套利策略

### 策略1: 互补对套利（当前实现）

**原理：**
在二元市场（YES/NO）中，两个结果的价格应该总和为1.0

```
价格 = {YES: 0.45, NO: 0.48}
价格和 = 0.93 < 1.0 
→ 存在套利机会（利润7%）

执行：
- 同时买入YES和NO
- 持有至到期（赚取利差）
```

**优点：** 
- 理论上无风险
- 实现相对简单

**缺点：**
- 机会罕见
- 需要持有头寸到期

### 策略2: 市场间套利（可扩展）

在不同交易对之间发现价格差异

```python
# 示例代码框架
class CrossExchangeArbitrager:
    def __init__(self):
        self.polymarket_api = PolymarketAPI()
        self.manifold_api = ManifoldAPI()
    
    def find_opportunities(self):
        # 在两个交易所寻找同一市场的价格差异
        pass
```

### 策略3: 流动性提供套利（高级）

通过在不同价格点提供流动性获利

```python
class LiquidityMakerBot:
    def __init__(self):
        self.target_spread = 0.02  # 目标2%的价差
    
    def provide_liquidity(self, market_id):
        # 在最佳买卖价差附近提供流动性
        pass
```

## 📈 性能优化

### 1. API优化

```python
# 批量请求而不是单个请求
class OptimizedPolymarketAPI(PolymarketAPI):
    def get_multiple_markets(self, market_ids):
        """批量获取多个市场数据"""
        # 实现批量API调用
        pass
    
    def cache_market_data(self, ttl=60):
        """缓存市场数据以减少API调用"""
        pass
```

### 2. 数据库优化

```python
# 定期清理旧数据
def cleanup_old_trades(days_old=30):
    """删除30天前的交易数据"""
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM trades 
            WHERE executed_at < datetime('now', '-30 days')
        """)
        conn.commit()
```

### 3. 多线程优化

```python
import threading
from concurrent.futures import ThreadPoolExecutor

class AsyncArbitrageBot:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def scan_markets_async(self):
        """异步扫描多个市场"""
        futures = [
            self.executor.submit(self._scan_market, market)
            for market in self.markets
        ]
```

## 🛡️ 风险管理

### 1. 头寸限制

```python
class RiskManager:
    def __init__(self):
        self.max_total_exposure = 1000.0  # 最大总敞口
        self.max_single_position = 100.0  # 单个头寸最大值
        self.max_daily_loss = 50.0        # 每日最大损失
    
    def can_open_trade(self, trade_size):
        """检查是否可以开新头寸"""
        current_exposure = self.calculate_exposure()
        return current_exposure + trade_size <= self.max_total_exposure
```

### 2. 损失控制

```python
class StopLossManager:
    def __init__(self):
        self.stop_loss_pct = 1.0  # 1%止损
    
    def check_stop_loss(self, trade):
        """检查是否需要止损"""
        if trade.current_loss_pct >= self.stop_loss_pct:
            self.close_trade(trade)
```

### 3. 执行延迟风险

```python
# 在execute_arbitrage中添加超时保护
def execute_arbitrage_safe(self, opportunity, max_delay_ms=1000):
    """
    带超时保护的套利执行
    如果执行超过max_delay_ms，自动取消订单
    """
    start_time = time.time()
    
    try:
        trade = self._execute_arbitrage(opportunity, size)
        elapsed = (time.time() - start_time) * 1000
        
        if elapsed > max_delay_ms:
            logger.warning(f"执行延迟过大: {elapsed}ms")
            self.executor.close_trade(trade.trade_id)
            return None
        
        return trade
    except TimeoutError:
        logger.error("交易执行超时")
        return None
```

## 📊 监控和告警

### 1. 实时监控仪表板

```python
class MonitoringDashboard:
    def display_status(self):
        """显示实时交易状态"""
        stats = self.db.get_statistics()
        print(f"总利润: ${stats['total_profit']:.2f}")
        print(f"成功率: {stats['closed_trades']}/{stats['total_trades']}")
        print(f"今日交易: {self.get_today_trades()}")
```

### 2. 告警系统

```python
class AlertSystem:
    def send_alert(self, level, message):
        """发送告警（Discord/Telegram）"""
        if level == "critical":
            self._send_discord_alert(message)
        elif level == "warning":
            self._send_telegram_alert(message)
```

## 🔧 调试和故障排除

### 启用详细日志

```bash
# 设置环境变量
export LOG_LEVEL=DEBUG

# 运行程序
python main.py
```

### 添加调试点

```python
# 在 arbitrage_detector.py 中
def detect_opportunities(self, markets):
    logger.debug(f"扫描 {len(markets)} 个市场")
    
    for market in markets:
        logger.debug(f"分析市场: {market.get('id')}")
        opportunities = self._detect_market_opportunities(...)
        logger.debug(f"找到 {len(opportunities)} 个机会")
```

### 性能分析

```python
import cProfile

def profile_arbitrage_detection():
    """性能分析"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 运行检测
    opportunities = detector.detect_opportunities(markets)
    
    profiler.disable()
    profiler.print_stats(sort='cumulative')
```

## 📝 参数优化检查清单

- [ ] 根据市场流动性调整 `MIN_PROFIT_PERCENTAGE`
- [ ] 根据钱包资金调整 `MAX_POSITION_SIZE`
- [ ] 根据CPU使用调整 `CHECK_INTERVAL`
- [ ] 配置日志级别
- [ ] 测试数据库性能
- [ ] 验证API速率限制
- [ ] 设置监控告警
- [ ] 定期检查交易统计
- [ ] 月度性能审计

## 🚀 生产部署

### Docker部署

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

运行：
```bash
docker build -t polymarket-arbitrage .
docker run -e POLYMARKET_PRIVATE_KEY=xxx polymarket-arbitrage
```

### 系统服务部署

```ini
# /etc/systemd/system/polymarket-arbitrage.service
[Unit]
Description=Polymarket Arbitrage Bot
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/home/trader/polymarket_arbitrage
ExecStart=/usr/bin/python3 main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start polymarket-arbitrage
sudo systemctl status polymarket-arbitrage
```

## 📚 参考资源

- [Polymarket文档](https://docs.polymarket.com)
- [Web3.py文档](https://web3py.readthedocs.io)
- [Polygon官方文档](https://polygon.technology/developers)
