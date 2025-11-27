import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()

@dataclass
class PolymarketConfig:
    """Polymarket API配置"""
    # Polymarket API端点
    API_BASE_URL: str = "https://clob.polymarket.com"
    # 中级API端点
    GAMMA_API_URL: str = "https://gamma-api.polymarket.com"
    
    # 钱包配置
    PRIVATE_KEY: str = os.getenv("POLYMARKET_PRIVATE_KEY", "")
    WALLET_ADDRESS: str = os.getenv("POLYMARKET_WALLET_ADDRESS", "")
    
    # RPC端点（Polygon）
    RPC_URL: str = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")
    
    # 交易配置
    MIN_PROFIT_PERCENTAGE: float = 0.5  # 最小利润率 (%)
    MAX_POSITION_SIZE: float = 100.0    # 最大头寸大小 (USDC)
    GAS_LIMIT: int = 500000
    
    # 监控配置
    CHECK_INTERVAL: int = 5  # 检查间隔 (秒)
    LOG_LEVEL: str = "INFO"
    ENABLE_TRADING: bool = os.getenv("ENABLE_TRADING", "false").lower() == "true"
    
    # 数据库配置
    DB_PATH: str = "sqlite:///polymarket_trades.db"

config = PolymarketConfig()
