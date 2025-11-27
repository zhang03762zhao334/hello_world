import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from src.models import Market, ArbitrageOpportunity, Order
from src.polymarket_api import PolymarketAPI

logger = logging.getLogger(__name__)

class ArbitrageDetector:
    """套利机会检测引擎"""
    
    def __init__(self, api: PolymarketAPI, min_profit_pct: float = 0.5):
        self.api = api
        self.min_profit_pct = min_profit_pct
        self.opportunities = []
    
    def detect_opportunities(self, markets: List[Dict]) -> List[ArbitrageOpportunity]:
        """检测所有市场中的套利机会"""
        opportunities = []
        
        for market in markets:
            try:
                market_id = market.get("id")
                if not market_id:
                    continue
                
                # 获取订单簿
                order_book = self.api.get_order_book(market_id)
                if not order_book:
                    continue
                
                # 检测该市场中的套利机会
                market_opportunities = self._detect_market_opportunities(
                    market_id, 
                    market, 
                    order_book
                )
                opportunities.extend(market_opportunities)
                
            except Exception as e:
                logger.error(f"检测市场 {market.get('id')} 时出错: {e}")
                continue
        
        self.opportunities = opportunities
        return opportunities
    
    def _detect_market_opportunities(
        self, 
        market_id: str, 
        market: Dict, 
        order_book: Dict
    ) -> List[ArbitrageOpportunity]:
        """检测单个市场中的套利机会"""
        opportunities = []
        
        try:
            outcomes = market.get("outcomes", [])
            if len(outcomes) < 2:
                return opportunities
            
            # 从订单簿获取价格
            prices = self._extract_prices_from_orderbook(order_book, outcomes)
            if not prices or len(prices) < 2:
                return opportunities
            
            # 检查互补对（如YES/NO）
            for i in range(len(prices)):
                for j in range(i + 1, len(prices)):
                    opp = self._check_complementary_pair(
                        market_id, i, j, prices[i], prices[j]
                    )
                    if opp:
                        opportunities.append(opp)
            
            return opportunities
        except Exception as e:
            logger.error(f"分析市场 {market_id} 时出错: {e}")
            return opportunities
    
    def _extract_prices_from_orderbook(self, order_book: Dict, outcomes: List[str]) -> List[float]:
        """从订单簿提取最佳价格"""
        try:
            prices = []
            
            for outcome_id, outcome_name in enumerate(outcomes):
                # 获取该结果的最佳买入和卖出价格
                best_bid = 0.0
                best_ask = 1.0
                
                bids = order_book.get("bids", [])
                asks = order_book.get("asks", [])
                
                # 找到该结果对应的最佳报价
                for bid in bids:
                    if bid.get("outcome_id") == outcome_id:
                        best_bid = max(best_bid, float(bid.get("price", 0)))
                
                for ask in asks:
                    if ask.get("outcome_id") == outcome_id:
                        best_ask = min(best_ask, float(ask.get("price", 1)))
                
                # 使用中间价格
                mid_price = (best_bid + best_ask) / 2 if best_bid > 0 else best_ask
                prices.append(mid_price)
            
            return prices
        except Exception as e:
            logger.error(f"提取价格失败: {e}")
            return []
    
    def _check_complementary_pair(
        self, 
        market_id: str, 
        outcome_1: int, 
        outcome_2: int, 
        price_1: float, 
        price_2: float
    ) -> Optional[ArbitrageOpportunity]:
        """
        检查互补对中是否存在套利机会
        在二元市场中，YES和NO价格之和应该接近1.0
        """
        try:
            # 检查价格之和是否小于1（套利机会）
            price_sum = price_1 + price_2
            
            if price_sum >= 1.0:
                return None
            
            # 计算利润率
            profit_pct = ((1.0 - price_sum) / price_sum) * 100
            
            if profit_pct < self.min_profit_pct:
                return None
            
            # 创建套利机会对象
            opportunity = ArbitrageOpportunity(
                opportunity_id=f"{market_id}_{outcome_1}_{outcome_2}_{datetime.now().timestamp()}",
                market_id=market_id,
                buy_outcome=outcome_1,  # 买较便宜的
                sell_outcome=outcome_2 if price_2 > price_1 else outcome_1,
                buy_price=min(price_1, price_2),
                sell_price=max(price_1, price_2),
                profit_percentage=profit_pct,
                max_size=self._calculate_max_size(price_1, price_2),
                detected_at=datetime.now()
            )
            
            logger.info(
                f"检测到套利机会: {market_id} - 利润: {profit_pct:.2f}% - "
                f"价格和: {price_sum:.4f}"
            )
            
            return opportunity
        
        except Exception as e:
            logger.error(f"检查互补对时出错: {e}")
            return None
    
    def _calculate_max_size(self, price_1: float, price_2: float) -> float:
        """
        基于价格计算最大交易大小
        使用流动性和风险考虑
        """
        # 简化计算：基于较低价格的可用流动性
        min_price = min(price_1, price_2)
        # 假设每个价格点有100美元的流动性
        max_size = 100.0 / min_price if min_price > 0 else 100.0
        return min(max_size, 1000.0)  # 最大1000个代币
