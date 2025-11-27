import sqlite3
from datetime import datetime
from typing import List, Optional
from src.models import Trade
import logging

logger = logging.getLogger(__name__)

class TradeDatabase:
    """交易历史数据库"""
    
    def __init__(self, db_path: str = "polymarket_trades.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建交易表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        trade_id TEXT PRIMARY KEY,
                        opportunity_id TEXT,
                        market_id TEXT,
                        buy_order_id TEXT,
                        sell_order_id TEXT,
                        buy_price REAL,
                        sell_price REAL,
                        quantity REAL,
                        profit_amount REAL,
                        profit_percentage REAL,
                        status TEXT,
                        executed_at TEXT,
                        closed_at TEXT
                    )
                ''')
                
                # 创建索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_market_id ON trades(market_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_status ON trades(status)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_executed_at ON trades(executed_at)
                ''')
                
                conn.commit()
                logger.info("数据库初始化成功")
        
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
    
    def save_trade(self, trade: Trade) -> bool:
        """保存交易到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO trades (
                        trade_id, opportunity_id, market_id, 
                        buy_order_id, sell_order_id, buy_price, sell_price,
                        quantity, profit_amount, profit_percentage,
                        status, executed_at, closed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade.trade_id,
                    trade.opportunity_id,
                    trade.market_id,
                    trade.buy_order.order_id,
                    trade.sell_order.order_id,
                    trade.buy_order.price,
                    trade.sell_order.price,
                    trade.buy_order.quantity,
                    trade.profit_amount,
                    trade.profit_percentage,
                    trade.status,
                    trade.executed_at.isoformat() if trade.executed_at else None,
                    trade.closed_at.isoformat() if trade.closed_at else None
                ))
                
                conn.commit()
                return True
        
        except Exception as e:
            logger.error(f"保存交易失败: {e}")
            return False
    
    def get_trade(self, trade_id: str) -> Optional[dict]:
        """获取单个交易"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM trades WHERE trade_id = ?', (trade_id,))
                row = cursor.fetchone()
                
                return dict(row) if row else None
        
        except Exception as e:
            logger.error(f"获取交易失败: {e}")
            return None
    
    def get_trades_by_status(self, status: str, limit: int = 100) -> List[dict]:
        """获取特定状态的交易"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    'SELECT * FROM trades WHERE status = ? ORDER BY executed_at DESC LIMIT ?',
                    (status, limit)
                )
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"获取交易失败: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """获取交易统计"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总交易数
                cursor.execute('SELECT COUNT(*) FROM trades')
                total_trades = cursor.fetchone()[0]
                
                # 成功交易数
                cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'closed'")
                closed_trades = cursor.fetchone()[0]
                
                # 总利润
                cursor.execute('SELECT SUM(profit_amount) FROM trades WHERE status = ?', ('closed',))
                total_profit = cursor.fetchone()[0] or 0
                
                # 平均利润率
                cursor.execute('SELECT AVG(profit_percentage) FROM trades WHERE status = ?', ('closed',))
                avg_profit_pct = cursor.fetchone()[0] or 0
                
                # 最大单笔利润
                cursor.execute('SELECT MAX(profit_amount) FROM trades WHERE status = ?', ('closed',))
                max_profit = cursor.fetchone()[0] or 0
                
                return {
                    "total_trades": total_trades,
                    "closed_trades": closed_trades,
                    "total_profit": round(total_profit, 2),
                    "average_profit_pct": round(avg_profit_pct, 2),
                    "max_profit": round(max_profit, 2)
                }
        
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
