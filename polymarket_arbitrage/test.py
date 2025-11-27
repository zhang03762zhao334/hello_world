"""
Polymarket套利机器人 - 测试脚本
演示如何使用各个模块
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.polymarket_api import PolymarketAPI
from src.arbitrage_detector import ArbitrageDetector
from config.settings import config
from config.logger import setup_logger

logger = setup_logger("TestBot", config.LOG_LEVEL)

def test_api_connection():
    """测试API连接"""
    logger.info("=" * 60)
    logger.info("测试1: API连接")
    logger.info("=" * 60)
    
    api = PolymarketAPI()
    markets = api.get_markets(limit=5)
    
    if markets:
        logger.info(f"✓ 成功获取 {len(markets)} 个市场")
        for market in markets[:3]:
            logger.info(f"  - {market.get('question', 'N/A')}")
    else:
        logger.warning("✗ 无法获取市场数据")
    
    return markets

def test_detector(markets):
    """测试套利检测"""
    if not markets:
        logger.warning("无市场数据，跳过检测测试")
        return
    
    logger.info("=" * 60)
    logger.info("测试2: 套利检测")
    logger.info("=" * 60)
    
    api = PolymarketAPI()
    detector = ArbitrageDetector(api, config.MIN_PROFIT_PERCENTAGE)
    
    opportunities = detector.detect_opportunities(markets[:3])
    
    if opportunities:
        logger.info(f"✓ 检测到 {len(opportunities)} 个套利机会")
        for opp in opportunities[:3]:
            logger.info(
                f"  - 市场: {opp.market_id} "
                f"- 利润: {opp.profit_percentage:.2f}% "
                f"- 最大大小: {opp.max_size:.2f}"
            )
    else:
        logger.info("✓ 当前没有检测到套利机会（这很正常）")

def test_configuration():
    """测试配置"""
    logger.info("=" * 60)
    logger.info("测试3: 配置检查")
    logger.info("=" * 60)
    
    logger.info(f"最小利润率: {config.MIN_PROFIT_PERCENTAGE}%")
    logger.info(f"最大头寸大小: ${config.MAX_POSITION_SIZE}")
    logger.info(f"检查间隔: {config.CHECK_INTERVAL}秒")
    logger.info(f"交易模式: {'实盘' if config.ENABLE_TRADING else '模拟'}")
    logger.info(f"数据库: {config.DB_PATH}")
    
    if config.PRIVATE_KEY:
        logger.info(f"✓ 私钥已配置")
    else:
        logger.warning("✗ 私钥未配置（无法执行真实交易）")
    
    if config.WALLET_ADDRESS:
        logger.info(f"✓ 钱包地址: {config.WALLET_ADDRESS}")
    else:
        logger.warning("✗ 钱包地址未配置")

def main():
    """运行所有测试"""
    logger.info("")
    logger.info("🚀 Polymarket套利机器人 - 测试套件")
    logger.info("")
    
    # 测试配置
    test_configuration()
    
    # 测试API连接
    markets = test_api_connection()
    
    # 测试检测
    test_detector(markets)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ 测试完成！")
    logger.info("")
    logger.info("下一步:")
    logger.info("1. 配置 .env 文件中的钱包信息")
    logger.info("2. 运行 'python main.py' 启动机器人")
    logger.info("3. 默认以模拟模式运行（ENABLE_TRADING=false）")
    logger.info("=" * 60)
    logger.info("")

if __name__ == "__main__":
    main()
