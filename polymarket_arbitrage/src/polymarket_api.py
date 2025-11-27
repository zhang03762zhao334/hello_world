import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PolymarketAPI:
    """Polymarket API客户端"""
    
    def __init__(self, base_url: str = "https://clob.polymarket.com"):
        self.base_url = base_url
        self.gamma_api_url = "https://gamma-api.polymarket.com"
        self.session = requests.Session()
    
    def get_markets(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取活跃市场列表"""
        try:
            url = f"{self.gamma_api_url}/markets"
            params = {
                "limit": limit,
                "offset": offset,
                "active": True
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取市场列表失败: {e}")
            return []
    
    def get_market(self, market_id: str) -> Optional[Dict]:
        """获取特定市场详情"""
        try:
            url = f"{self.gamma_api_url}/markets/{market_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取市场 {market_id} 失败: {e}")
            return None
    
    def get_order_book(self, market_id: str) -> Optional[Dict]:
        """获取订单簿"""
        try:
            url = f"{self.base_url}/order-book/{market_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取订单簿 {market_id} 失败: {e}")
            return None
    
    def get_prices(self, market_id: str) -> Optional[Dict]:
        """获取市场价格"""
        try:
            url = f"{self.gamma_api_url}/prices"
            params = {"market_id": market_id}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取价格失败: {e}")
            return None
    
    def get_user_orders(self, user_address: str) -> List[Dict]:
        """获取用户订单"""
        try:
            url = f"{self.base_url}/user/{user_address}/orders"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取用户订单失败: {e}")
            return []
    
    def get_user_positions(self, user_address: str) -> List[Dict]:
        """获取用户头寸"""
        try:
            url = f"{self.gamma_api_url}/user/{user_address}/positions"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"获取用户头寸失败: {e}")
            return []
    
    def create_order(self, order_data: Dict) -> Optional[Dict]:
        """创建订单 (需要签名)"""
        try:
            url = f"{self.base_url}/create-order"
            response = self.session.post(url, json=order_data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"创建订单失败: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            url = f"{self.base_url}/cancel-order"
            payload = {"id": order_id}
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"取消订单 {order_id} 失败: {e}")
            return False
