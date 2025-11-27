"""Polymarket套利程序 - 主入口"""
import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.arbitrage_bot import main

if __name__ == "__main__":
    main()
