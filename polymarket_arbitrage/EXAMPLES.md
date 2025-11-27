# Polymarket套利程序 - 使用示例

## 📖 目录
1. [基础示例](#基础示例)
2. [自定义配置](#自定义配置)
3. [调试和监控](#调试和监控)
4. [实战案例](#实战案例)

## 基础示例

### 示例 1: 运行模拟模式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env (至少需要 POLYGON_RPC_URL)

# 3. 运行测试
python test.py

# 4. 启动机器人（模拟模式）
python main.py
```

### 示例 2: 自定义参数运行

```python
# 在 main.py 中修改参数
from config.settings import PolymarketConfig
from src.arbitrage_bot import ArbitrageBot
from src.polymarket_api import PolymarketAPI
from src.arbitrage_detector import ArbitrageDetector
from src.trade_executor import TradeExecutor, OrderSigner
from src.database import TradeDatabase

# 自定义配置
class CustomConfig(PolymarketConfig):
    MIN_PROFIT_PERCENTAGE = 1.0  # 只做>1%的交易
    MAX_POSITION_SIZE = 50.0
    CHECK_INTERVAL = 10

config = CustomConfig()

# 初始化组件
api = PolymarketAPI()
detector = ArbitrageDetector(api, config.MIN_PROFIT_PERCENTAGE)
signer = OrderSigner(config.PRIVATE_KEY)
executor = TradeExecutor(api, signer, False)  # 模拟模式
db = TradeDatabase()

# 创建并启动机器人
bot = ArbitrageBot(api, detector, executor, db, config.CHECK_INTERVAL)
bot.start()
```

## 自定义配置

### 配置 1: 保守型（低风险）

```python
# config/settings.py
MIN_PROFIT_PERCENTAGE = 2.0      # 只做利润≥2%的交易
MAX_POSITION_SIZE = 50.0         # 单次最多$50
CHECK_INTERVAL = 10              # 每10秒检查一次
```

**特点：**
- 机会少，但利润大
- 风险低，执行成功率高
- 适合保守型交易者

### 配置 2: 激进型（高风险）

```python
# config/settings.py
MIN_PROFIT_PERCENTAGE = 0.1      # 做利润≥0.1%的交易
MAX_POSITION_SIZE = 500.0        # 单次最多$500
CHECK_INTERVAL = 2               # 每2秒检查一次
```

**特点：**
- 机会多，但利润小
- 风险较高，需要快速执行
- 适合激进型交易者

### 配置 3: 平衡型（推荐）

```python
# config/settings.py
MIN_PROFIT_PERCENTAGE = 0.5      # 做利润≥0.5%的交易
MAX_POSITION_SIZE = 100.0        # 单次最多$100
CHECK_INTERVAL = 5               # 每5秒检查一次
```

## 调试和监控

### 启用详细日志

```python
# 修改 config/settings.py
LOG_LEVEL = "DEBUG"

# 运行程序
python main.py
```

日志输出示例：
```
2024-01-15 10:23:45,123 - arbitrage_detector - DEBUG - 扫描 50 个市场
2024-01-15 10:23:46,234 - polymarket_api - DEBUG - 获取订单簿: market_123
2024-01-15 10:23:47,345 - arbitrage_detector - INFO - 检测到套利机会: market_123 - 利润: 0.75% - 价格和: 0.9925
2024-01-15 10:23:48,456 - trade_executor - INFO - 执行套利 - 市场: market_123 - 利润: 0.75% - 大小: 50.00
```

### 查看实时统计

```python
# 创建一个监控脚本
import sqlite3
from config.settings import config

def show_live_stats():
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 获取今日统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(profit_amount) as total_profit,
                AVG(profit_percentage) as avg_profit_pct
            FROM trades 
            WHERE DATE(executed_at) = DATE('now')
        """)
        
        total, profit, avg_pct = cursor.fetchone()
        print(f"今日交易数: {total}")
        print(f"总利润: ${profit or 0:.2f}")
        print(f"平均利润率: {avg_pct or 0:.2f}%")

# 运行监控
if __name__ == "__main__":
    show_live_stats()
```

### 数据库查询示例

```bash
# 查看所有已平仓交易
sqlite3 polymarket_trades.db "SELECT * FROM trades WHERE status='closed' ORDER BY executed_at DESC LIMIT 10;"

# 计算总利润
sqlite3 polymarket_trades.db "SELECT SUM(profit_amount) FROM trades WHERE status='closed';"

# 找到最赚钱的市场
sqlite3 polymarket_trades.db "SELECT market_id, SUM(profit_amount) as total FROM trades WHERE status='closed' GROUP BY market_id ORDER BY total DESC LIMIT 5;"
```

## 实战案例

### 案例 1: 识别价格异常

```python
# 检测市场中的价格异常
from src.arbitrage_detector import ArbitrageDetector
from src.polymarket_api import PolymarketAPI

api = PolymarketAPI()
detector = ArbitrageDetector(api, min_profit_pct=0.3)

# 获取单个市场
market = api.get_market("0x123abc")
order_book = api.get_order_book("0x123abc")

# 分析价格
prices = detector._extract_prices_from_orderbook(
    order_book, 
    market.get('outcomes', [])
)

print(f"YES价格: {prices[0]:.4f}")
print(f"NO价格: {prices[1]:.4f}")
print(f"价格和: {sum(prices):.4f}")

if sum(prices) < 1.0:
    profit_pct = ((1.0 - sum(prices)) / sum(prices)) * 100
    print(f"套利机会: {profit_pct:.2f}%")
```

### 案例 2: 回测历史交易

```python
# 分析过去的交易性能
import sqlite3
from config.settings import config
from datetime import datetime, timedelta

def analyze_performance(days_back=7):
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 计算周期统计
        date_from = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        cursor.execute("""
            SELECT 
                DATE(executed_at) as trade_date,
                COUNT(*) as trade_count,
                SUM(profit_amount) as daily_profit,
                AVG(profit_percentage) as avg_return
            FROM trades 
            WHERE executed_at >= ? AND status = 'closed'
            GROUP BY DATE(executed_at)
            ORDER BY executed_at DESC
        """, (date_from,))
        
        print(f"过去{days_back}天的交易分析:")
        print("-" * 60)
        print(f"{'日期':<12} {'交易数':<8} {'总利润':<12} {'平均回报':<10}")
        print("-" * 60)
        
        total_profit = 0
        for date, count, profit, avg_return in cursor.fetchall():
            print(f"{date:<12} {count:<8} ${profit or 0:<11.2f} {avg_return or 0:<9.2f}%")
            total_profit += (profit or 0)
        
        print("-" * 60)
        print(f"{'总计':<12} {'':8} ${total_profit:<11.2f}")

analyze_performance(7)
```

### 案例 3: 风险评估

```python
# 评估交易风险
import sqlite3
from config.settings import config

def risk_assessment():
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 计算成功率
        cursor.execute("SELECT COUNT(*) FROM trades WHERE status='closed'")
        closed_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trades")
        total_trades = cursor.fetchone()[0]
        
        success_rate = (closed_trades / total_trades * 100) if total_trades > 0 else 0
        
        # 计算盈利率
        cursor.execute("SELECT SUM(profit_amount) FROM trades WHERE status='closed'")
        total_profit = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(profit_amount) FROM trades WHERE profit_amount < 0")
        total_loss = abs(cursor.fetchone()[0] or 0)
        
        profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')
        
        print("风险评估报告:")
        print(f"成功率: {success_rate:.1f}% ({closed_trades}/{total_trades})")
        print(f"总利润: ${total_profit:.2f}")
        print(f"总亏损: ${total_loss:.2f}")
        print(f"利润因子: {profit_factor:.2f}")
        
        if profit_factor > 2:
            print("评级: ✓ 风险可控")
        elif profit_factor > 1:
            print("评级: ⚠ 风险中等")
        else:
            print("评级: ✗ 风险过高")

risk_assessment()
```

### 案例 4: 实时监控仪表板

```python
# 创建实时监控脚本
import time
import os
from config.settings import config
from src.database import TradeDatabase

def display_dashboard():
    db = TradeDatabase(config.DB_PATH)
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        
        stats = db.get_statistics()
        
        print("=" * 60)
        print("Polymarket 套利机器人 - 实时监控")
        print("=" * 60)
        print(f"总交易数: {stats['total_trades']}")
        print(f"已平仓: {stats['closed_trades']}")
        print(f"总利润: ${stats['total_profit']:.2f}")
        print(f"平均利润率: {stats['average_profit_pct']:.2f}%")
        print(f"最大单笔利润: ${stats['max_profit']:.2f}")
        print("=" * 60)
        print(f"更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("按 Ctrl+C 退出")
        
        time.sleep(5)

if __name__ == "__main__":
    try:
        display_dashboard()
    except KeyboardInterrupt:
        print("\n监控已停止")
```

## 常见操作

### 操作 1: 暂停机器人

```python
# 在运行中按 Ctrl+C 暂停
# 机器人会自动：
# 1. 平仓所有活跃交易
# 2. 显示统计信息
# 3. 保存所有数据
```

### 操作 2: 清空历史交易

```bash
# 完全重置数据库
rm polymarket_trades.db

# 程序会自动创建新的数据库
```

### 操作 3: 导出交易历史

```bash
# 导出为CSV
sqlite3 -header -csv polymarket_trades.db "SELECT * FROM trades;" > trades.csv

# 导出为JSON
sqlite3 -json polymarket_trades.db "SELECT * FROM trades;" > trades.json
```

### 操作 4: 备份数据库

```bash
# 创建备份
cp polymarket_trades.db polymarket_trades.db.backup.$(date +%Y%m%d)

# 列出所有备份
ls -la polymarket_trades.db.backup*
```

## 性能优化建议

### 根据CPU使用优化

```python
# CPU使用过高 → 增加检查间隔
CHECK_INTERVAL = 10  # 从5改为10秒

# CPU使用过低 → 减少检查间隔
CHECK_INTERVAL = 2   # 从5改为2秒
```

### 根据内存使用优化

```python
# 定期清理数据库
def cleanup_database():
    db.execute("""
        DELETE FROM trades 
        WHERE executed_at < datetime('now', '-30 days')
    """)
```

### 根据API调用限制优化

```python
# 如果API返回速率限制错误
CHECK_INTERVAL = 15  # 增加等待时间
```

## 故障排除

### 问题：没有检测到任何机会

```python
# 解决方案1: 降低利润率阈值
MIN_PROFIT_PERCENTAGE = 0.1  # 从0.5改为0.1

# 解决方案2: 增加市场查询数量
api.get_markets(limit=200)  # 从50改为200

# 解决方案3: 检查市场流动性
def check_market_liquidity():
    markets = api.get_markets()
    for market in markets:
        if market['liquidity'] > 1000:  # 流动性>$1000
            print(f"好市场: {market['id']}")
```

### 问题：订单执行失败

```python
# 启用调试日志
LOG_LEVEL = "DEBUG"

# 检查钱包余额
def check_balance():
    positions = api.get_user_positions(config.WALLET_ADDRESS)
    print(f"USDC余额: {positions.get('balance', 0)}")
```

---

**更多示例和文档，请查看 ADVANCED.md**
