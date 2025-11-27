import logging
import hashlib
from typing import Optional, Tuple
from datetime import datetime
from eth_account import Account
from src.models import Order, ArbitrageOpportunity, Trade
from src.polymarket_api import PolymarketAPI
from config.settings import config

logger = logging.getLogger(__name__)

class OrderSigner:
    """订单签名和验证"""
    
    def __init__(self, private_key: str):
        try:
            self.account = Account.from_key(private_key)
            self.address = self.account.address
        except Exception as e:
            logger.error(f"初始化账户失败: {e}")
            self.account = None
            self.address = None
    
    def sign_order(self, order_data: dict) -> Optional[str]:
        """签署订单"""
        if not self.account:
            logger.error("账户未初始化，无法签署订单")
            return None
        
        try:
            # 创建订单哈希
            message_hash = self._create_order_hash(order_data)
            
            # 使用账户签署消息
            signed = self.account.sign_message({
                "messageHash": message_hash
            })
            
            return signed.signature.hex()
        except Exception as e:
            logger.error(f"签署订单失败: {e}")
            return None
    
    def _create_order_hash(self, order_data: dict) -> str:
        """创建订单的哈希值"""
        order_string = (
            f"{order_data.get('market_id', '')}"
            f"{order_data.get('token_id', '')}"
            f"{order_data.get('price', '')}"
            f"{order_data.get('quantity', '')}"
            f"{order_data.get('is_buy', '')}"
        )
        return hashlib.keccak256(order_string.encode()).digest()

class TradeExecutor:
    """交易执行引擎"""
    
    def __init__(self, api: PolymarketAPI, signer: OrderSigner, enable_trading: bool = False):
        self.api = api
        self.signer = signer
        self.enable_trading = enable_trading
        self.active_trades = {}
    
    def execute_arbitrage(self, opportunity: ArbitrageOpportunity, size: float) -> Optional[Trade]:
        """执行套利交易"""
        
        if not self.enable_trading:
            logger.info(
                f"交易模式禁用。模拟执行套利: {opportunity.opportunity_id} "
                f"- 大小: {size} - 利润: {opportunity.profit_percentage:.2f}%"
            )
            return self._simulate_trade(opportunity, size)
        
        try:
            logger.info(f"执行套利: {opportunity.opportunity_id}")
            
            # 步骤1: 下买入订单
            buy_order = self._create_buy_order(
                opportunity.market_id,
                opportunity.buy_outcome,
                opportunity.buy_price,
                size
            )
            
            if not buy_order:
                logger.error("创建买入订单失败")
                return None
            
            # 步骤2: 下卖出订单
            sell_order = self._create_sell_order(
                opportunity.market_id,
                opportunity.sell_outcome,
                opportunity.sell_price,
                size
            )
            
            if not sell_order:
                logger.error("创建卖出订单失败，取消买入订单")
                self.api.cancel_order(buy_order.order_id)
                return None
            
            # 创建交易记录
            trade = Trade(
                trade_id=f"trade_{opportunity.opportunity_id}",
                opportunity_id=opportunity.opportunity_id,
                market_id=opportunity.market_id,
                buy_order=buy_order,
                sell_order=sell_order,
                profit_amount=size * (opportunity.sell_price - opportunity.buy_price),
                profit_percentage=opportunity.profit_percentage,
                status="executed",
                executed_at=datetime.now()
            )
            
            self.active_trades[trade.trade_id] = trade
            logger.info(f"交易执行成功: {trade.trade_id} - 预期利润: {trade.profit_amount:.2f} USDC")
            
            return trade
        
        except Exception as e:
            logger.error(f"执行套利失败: {e}")
            return None
    
    def _create_buy_order(
        self, 
        market_id: str, 
        outcome_id: int, 
        price: float, 
        quantity: float
    ) -> Optional[Order]:
        """创建买入订单"""
        try:
            order_data = {
                "market_id": market_id,
                "token_id": outcome_id,
                "price": price,
                "quantity": quantity,
                "is_buy": True,
                "signer": self.signer.address,
            }
            
            # 签署订单
            signature = self.signer.sign_order(order_data)
            if not signature:
                return None
            
            order_data["signature"] = signature
            
            # 提交到API
            response = self.api.create_order(order_data)
            if not response or "id" not in response:
                logger.error(f"API返回错误: {response}")
                return None
            
            order = Order(
                order_id=response["id"],
                market_id=market_id,
                token_id=outcome_id,
                price=price,
                quantity=quantity,
                is_buy=True,
                total_cost=price * quantity,
                created_at=datetime.now(),
                status="confirmed"
            )
            
            logger.info(f"买入订单已创建: {order.order_id} - 价格: {price} - 数量: {quantity}")
            return order
        
        except Exception as e:
            logger.error(f"创建买入订单失败: {e}")
            return None
    
    def _create_sell_order(
        self, 
        market_id: str, 
        outcome_id: int, 
        price: float, 
        quantity: float
    ) -> Optional[Order]:
        """创建卖出订单"""
        try:
            order_data = {
                "market_id": market_id,
                "token_id": outcome_id,
                "price": price,
                "quantity": quantity,
                "is_buy": False,
                "signer": self.signer.address,
            }
            
            # 签署订单
            signature = self.signer.sign_order(order_data)
            if not signature:
                return None
            
            order_data["signature"] = signature
            
            # 提交到API
            response = self.api.create_order(order_data)
            if not response or "id" not in response:
                logger.error(f"API返回错误: {response}")
                return None
            
            order = Order(
                order_id=response["id"],
                market_id=market_id,
                token_id=outcome_id,
                price=price,
                quantity=quantity,
                is_buy=False,
                total_cost=price * quantity,
                created_at=datetime.now(),
                status="confirmed"
            )
            
            logger.info(f"卖出订单已创建: {order.order_id} - 价格: {price} - 数量: {quantity}")
            return order
        
        except Exception as e:
            logger.error(f"创建卖出订单失败: {e}")
            return None
    
    def _simulate_trade(self, opportunity: ArbitrageOpportunity, size: float) -> Trade:
        """模拟交易（测试模式）"""
        buy_order = Order(
            order_id=f"sim_buy_{opportunity.opportunity_id}",
            market_id=opportunity.market_id,
            token_id=opportunity.buy_outcome,
            price=opportunity.buy_price,
            quantity=size,
            is_buy=True,
            total_cost=opportunity.buy_price * size,
            created_at=datetime.now(),
            status="simulated"
        )
        
        sell_order = Order(
            order_id=f"sim_sell_{opportunity.opportunity_id}",
            market_id=opportunity.market_id,
            token_id=opportunity.sell_outcome,
            price=opportunity.sell_price,
            quantity=size,
            is_buy=False,
            total_cost=opportunity.sell_price * size,
            created_at=datetime.now(),
            status="simulated"
        )
        
        profit = size * (opportunity.sell_price - opportunity.buy_price)
        
        trade = Trade(
            trade_id=f"sim_trade_{opportunity.opportunity_id}",
            opportunity_id=opportunity.opportunity_id,
            market_id=opportunity.market_id,
            buy_order=buy_order,
            sell_order=sell_order,
            profit_amount=profit,
            profit_percentage=opportunity.profit_percentage,
            status="simulated",
            executed_at=datetime.now()
        )
        
        return trade
    
    def close_trade(self, trade_id: str) -> bool:
        """平仓交易"""
        try:
            trade = self.active_trades.get(trade_id)
            if not trade:
                logger.warning(f"交易 {trade_id} 未找到")
                return False
            
            # 取消订单
            self.api.cancel_order(trade.buy_order.order_id)
            self.api.cancel_order(trade.sell_order.order_id)
            
            trade.status = "closed"
            trade.closed_at = datetime.now()
            
            logger.info(f"交易已平仓: {trade_id}")
            return True
        
        except Exception as e:
            logger.error(f"平仓交易 {trade_id} 失败: {e}")
            return False
