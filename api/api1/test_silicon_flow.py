import os
import json
import requests
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_silicon_flow_api():
    """
    测试硅基流动API的连接和配置
    """
    print("=== 硅基流动API测试工具 ===")
    
    # 1. 检查环境变量
    print("\n1. 检查环境变量配置...")
    
    # 尝试从不同位置加载.env文件
    env_locations = [
        '.env'
 
    ]
    
    env_loaded = False
    for env_path in env_locations:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"✓ 成功加载配置文件: {env_path}")
            env_loaded = True
            break
    
    if not env_loaded:
        print("! 警告: 未找到.env文件")
    
    # 获取API配置
    api_key = os.getenv('SILICON_FLOW_API_KEY')
    api_url = os.getenv('SILICON_FLOW_API_URL', 'https://api.siliconflow.cn/v1')
    api_model = os.getenv('SILICON_FLOW_API_MODEL', 'Qwen/Qwen2.5-32B-Instruct')
    
    # 检查API密钥
    if not api_key:
        print("✗ 错误: 未找到API密钥 (SILICON_FLOW_API_KEY)")
        return
    else:
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        print(f"✓ API密钥: {masked_key}")
    
    print(f"✓ API地址: {api_url}")
    print(f"✓ 使用模型: {api_model}")
    
    # 2. 测试API连接
    print("\n2. 测试API连接...")
    
    # 构建请求头
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # 构建简单的测试消息
    test_message = "你好，这是一个测试消息。请用一句话回复。"
    
    # 构建请求体
    payload = {
        'model': api_model,
        'messages': [
            {'role': 'system', 'content': '你是一个测试助手。'},
            {'role': 'user', 'content': test_message}
        ]
    }
    
    try:
        # 发送测试请求
        print("正在发送测试请求...")
        response = requests.post(
            f"{api_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=(5, 10)  # 连接超时5秒，读取超时10秒
        )
        
        # 检查响应
        if response.status_code == 200:
            print("✓ API连接成功！")
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {}).get('content', '')
                print(f"\n响应内容: {message}")
            print("\n响应详情:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"✗ API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ 连接错误: 无法连接到API服务器")
    except requests.exceptions.Timeout:
        print("✗ 连接超时: API服务器响应时间过长")
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {str(e)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_silicon_flow_api()
