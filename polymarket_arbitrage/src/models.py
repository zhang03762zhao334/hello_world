from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Market:
    """市场数据模型"""
    market_id: str
    question: str
    description: str
    outcome_tokens: List[str]
    prices: List[float]  # 各结果的价格
    liquidity: float
    volume: float
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

@dataclass
class Order:
    """订单模型"""
    order_id: str
    market_id: str
    token_id: int  # 0=YES, 1=NO 等
    price: float
    quantity: float
    is_buy: bool
    total_cost: float
    created_at: datetime
    status: str = "pending"

@dataclass
class ArbitrageOpportunity:
    """套利机会"""
    opportunity_id: str
    market_id: str
    buy_outcome: int  # 买入的结果索引
    sell_outcome: int  # 卖出的结果索引
    buy_price: float
    sell_price: float
    profit_percentage: float
    max_size: float  # 最大交易大小
    detected_at: datetime

@dataclass
class Trade:
    """交易记录"""
    trade_id: str
    opportunity_id: str
    market_id: str
    buy_order: Order
    sell_order: Order
    profit_amount: float
    profit_percentage: float
    status: str
    executed_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
