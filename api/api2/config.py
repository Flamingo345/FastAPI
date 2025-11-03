import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 硅基流动API配置
config = {
    'api_key': 'sk-eppztmqsnfqycmyeioweoaghfdxnpbavrwdyleqacxykymar',
    'api_url': 'https://api.siliconflow.cn/v1',
    'api_model': 'Qwen/Qwen2.5-32B-Instruct'
}
