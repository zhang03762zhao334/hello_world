import logging
import time
from typing import List
from datetime import datetime
from src.polymarket_api import PolymarketAPI
from src.arbitrage_detector import ArbitrageDetector
from src.trade_executor import TradeExecutor, OrderSigner
from src.database import TradeDatabase
from src.models import ArbitrageOpportunity
from config.settings import config
from config.logger import setup_logger

logger = setup_logger("ArbitrageBot", config.LOG_LEVEL)

class ArbitrageBot:
    """套利机器人主类"""
    
    def __init__(
        self,
        api: PolymarketAPI,
        detector: ArbitrageDetector,
        executor: TradeExecutor,
        db: TradeDatabase,
        check_interval: int = 5
    ):
        self.api = api
        self.detector = detector
        self.executor = executor
        self.db = db
        self.check_interval = check_interval
        self.is_running = False
        self.total_opportunities = 0
        self.total_trades = 0
    
    def start(self):
        """启动套利机器人"""
        logger.info("=" * 60)
        logger.info("Polymarket套利机器人已启动")
        logger.info(f"交易模式: {'启用' if self.executor.enable_trading else '模拟'}")
        logger.info(f"最小利润率: {self.detector.min_profit_pct}%")
        logger.info(f"检查间隔: {self.check_interval}秒")
        logger.info("=" * 60)
        
        self.is_running = True
        
        try:
            while self.is_running:
                self._scan_for_opportunities()
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止...")
        except Exception as e:
            logger.error(f"机器人遇到错误: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止套利机器人"""
        self.is_running = False
        
        # 平仓所有活跃交易
        for trade_id in list(self.executor.active_trades.keys()):
            self.executor.close_trade(trade_id)
        
        # 显示统计信息
        stats = self.db.get_statistics()
        logger.info("=" * 60)
        logger.info("套利机器人已停止")
        logger.info(f"检测到的套利机会: {self.total_opportunities}")
        logger.info(f"执行的交易: {self.total_trades}")
        logger.info("交易统计:")
        logger.info(f"  - 总交易数: {stats.get('total_trades', 0)}")
        logger.info(f"  - 已平仓: {stats.get('closed_trades', 0)}")
        logger.info(f"  - 总利润: ${stats.get('total_profit', 0):.2f}")
        logger.info(f"  - 平均利润率: {stats.get('average_profit_pct', 0):.2f}%")
        logger.info(f"  - 最大单笔利润: ${stats.get('max_profit', 0):.2f}")
        logger.info("=" * 60)
    
    def _scan_for_opportunities(self):
        """扫描市场寻找套利机会"""
        try:
            # 获取所有市场
            logger.debug("正在获取市场列表...")
            markets = self.api.get_markets(limit=50)
            
            if not markets:
                logger.warning("未获取到市场数据")
                return
            
            logger.debug(f"获取到 {len(markets)} 个市场")
            
            # 检测套利机会
            opportunities = self.detector.detect_opportunities(markets)
            
            if opportunities:
                logger.info(f"检测到 {len(opportunities)} 个套利机会")
                self.total_opportunities += len(opportunities)
                
                # 按利润率排序
                opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
                
                # 执行最好的几个机会
                for opp in opportunities[:5]:  # 限制同时执行的交易数
                    self._execute_opportunity(opp)
            else:
                logger.debug("未发现套利机会")
        
        except Exception as e:
            logger.error(f"扫描市场时出错: {e}")
    
    def _execute_opportunity(self, opportunity: ArbitrageOpportunity):
        """执行单个套利机会"""
        try:
            # 计算交易大小
            size = min(
                opportunity.max_size,
                config.MAX_POSITION_SIZE / opportunity.buy_price
            )
            
            logger.info(
                f"执行套利 - 市场: {opportunity.market_id} "
                f"- 利润: {opportunity.profit_percentage:.2f}% "
                f"- 大小: {size:.2f}"
            )
            
            # 执行交易
            trade = self.executor.execute_arbitrage(opportunity, size)
            
            if trade:
                # 保存到数据库
                self.db.save_trade(trade)
                self.total_trades += 1
                
                logger.info(
                    f"交易执行成功 - 预期利润: ${trade.profit_amount:.2f}"
                )
                
                # 如果交易已完成，立即平仓
                if trade.status in ["executed", "simulated"]:
                    time.sleep(1)
                    self.executor.close_trade(trade.trade_id)
                    self.db.save_trade(trade)
        
        except Exception as e:
            logger.error(f"执行套利机会失败: {e}")

def main():
    """主函数"""
    # 初始化组件
    api = PolymarketAPI()
    detector = ArbitrageDetector(api, config.MIN_PROFIT_PERCENTAGE)
    signer = OrderSigner(config.PRIVATE_KEY)
    executor = TradeExecutor(api, signer, config.ENABLE_TRADING)
    db = TradeDatabase(config.DB_PATH)
    
    # 创建机器人
    bot = ArbitrageBot(api, detector, executor, db, config.CHECK_INTERVAL)
    
    # 启动机器人
    bot.start()

if __name__ == "__main__":
    main()
