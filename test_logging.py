#!/usr/bin/env python3
"""
测试日志功能
"""

import os
os.environ['LOG_LEVEL'] = 'INFO'  # 设置日志级别为INFO

import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试日志
logger.info("测试INFO日志")
logger.debug("测试DEBUG日志")
logger.warning("测试WARNING日志")

# 测试app.main的日志
app_logger = logging.getLogger('app.main')
app_logger.info("测试app.main日志")
