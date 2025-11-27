import logging
import os
from datetime import datetime

def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """配置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # 文件处理器
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"arbitrage_{datetime.now().strftime('%Y%m%d')}.log")
    fh = logging.FileHandler(log_file)
    fh.setLevel(getattr(logging, log_level))
    
    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, log_level))
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
