"""
新闻重写模块 - 调用Coze API重写新闻内容
"""
import requests
import json
import time
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 修改为DEBUG级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('news_rewriter.log')
    ]
)
logger = logging.getLogger(__name__)

class NewsRewriter:
    """新闻重写API客户端"""
    
    def __init__(self, api_token=None, workflow_id=None, space_id=None, base_url=None, execute_mode=None):
        """初始化API客户端"""
        # 使用与其他模块相同的API令牌和工作流ID
        self.api_token = api_token or 'pat_HjVHMMp5PDZrzeHbdMeUBHAtB5noWVqRZOenezZtnuNUHJhrYoZTvkIkUpUG8idV'
        self.base_url = base_url or 'https://api.coze.cn'
        # 使用工作流示例中的ID - 确认ID正确性
        self.workflow_id = workflow_id or '7540854742675619886'
        # 添加空间ID (从debug_url中提取)
        self.space_id = space_id or '7517113138517950515'
        # 添加执行模式 (从debug_url中提取)
        self.execute_mode = execute_mode or '2'
        
        # 初始化信息不输出到控制台
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def rewrite_news(self, content: str, max_retries: int = 3, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        调用Coze工作流重写新闻内容
        
        Args:
            content: 原始新闻内容
            max_retries: 最大重试次数
            timeout: 请求超时时间（秒）
            
        Returns:
            重写结果，失败时返回None
        """
        url = f"{self.base_url}/v1/workflow/run"
        
        # 构建请求数据 - 使用之前成功验证的完整参数格式
        data = {
            "workflow_id": self.workflow_id,
            "space_id": self.space_id,
            "execute_mode": self.execute_mode,
            # 包含多种参数名格式以确保成功
            "input": content,
            "content": content,
            "inputs": {
                "content": content,
                "input": content,
                "text": content
            },
            "parameters": {
                "content": content,
                "input": content,
                "text": content
            }
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"调用新闻重写API (尝试 {attempt + 1}/{max_retries})")
                
                # 打印请求数据用于调试
                logger.debug(f"API请求URL: {url}")
                logger.debug(f"API请求头: {self.headers}")
                logger.debug(f"API请求数据: {json.dumps(data, ensure_ascii=False)}")
                
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    data=json.dumps(data),
                    timeout=timeout
                )
                
                # 打印响应数据用于调试
                logger.debug(f"API响应状态码: {response.status_code}")
                logger.debug(f"API响应内容: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('code') == 0:
                        logger.info("新闻重写API调用成功")
                        return self._parse_response(result)
                    else:
                        logger.error(f"API返回错误: {result.get('msg')}")
                        logger.debug(f"完整响应: {result}")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        return None
                else:
                    logger.error(f"API请求失败，状态码: {response.status_code}")
                    logger.error(f"响应内容: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
            except Exception as e:
                logger.error(f"调用新闻重写API时出错 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
        
        logger.error(f"在 {max_retries} 次尝试后仍然失败")
        return None
    
    def _parse_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析API响应
        
        Args:
            response: API响应数据
            
        Returns:
            解析后的结果
        """
        try:
            if response.get('data'):
                # 解析data字段中的JSON字符串
                try:
                    data_content = json.loads(response['data'])
                    # 在成功响应中，news字段包含重写内容
                    rewritten_content = data_content.get('news', '')
                    if not rewritten_content:
                        # 如果没有news字段，尝试其他可能的字段名
                        rewritten_content = data_content.get('data', '') or data_content.get('content', '')
                except json.JSONDecodeError:
                    # 如果data不是JSON格式，直接使用原始内容
                    rewritten_content = response.get('data', '')
                
                return {
                    'rewritten_content': rewritten_content,
                    'usage': response.get('usage', {}),
                    'debug_url': response.get('debug_url', '')
                }
            else:
                logger.error("API响应中没有data字段")
                logger.debug(f"完整响应: {response}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"解析API响应失败: {e}")
            return None
        except Exception as e:
            logger.error(f"处理API响应时出错: {e}")
            return None


def test_news_rewriting():
    """测试新闻重写功能"""
    # 示例新闻内容
    sample_news = """
    入伏后，一年当中最热的时间段已来临。高温、高湿的环境和长时间的高温天气过程，都会增加中暑风险，威胁生命健康安全。

    老人、孕妇、儿童、慢性病患者、体力劳动者或需要在户外活动的人群，要密切关注天气情况，结合自己的健康状况，及时采取有效措施防暑降温。

    一、中暑的表现

    先兆中暑

    高温环境下，如果出现头痛、头晕、眼花、恶心、多汗、四肢无力发酸等症状，就要开始采取相应的防暑降温的措施，比如多多喝水、及时休息，使用冰袋、冰凉贴、湿毛巾放置颈部、腋下、大腿根帮助降温，转移到阴凉处或室内活动等等，谨防中暑进一步恶化。
    """
    
    # 创建重写器实例
    rewriter = NewsRewriter()
    
    # 调用API重写新闻
    result = rewriter.rewrite_news(sample_news)
    
    if result:
        print("\n" + "="*50)
        print("重写后的新闻内容:")
        print("="*50)
        print(result['rewritten_content'])
        print("="*50)
        
        # 显示使用统计
        usage = result.get('usage', {})
        print(f"\nToken使用情况:")
        print(f"- 输入: {usage.get('input_count', 0)} tokens")
        print(f"- 输出: {usage.get('output_count', 0)} tokens")
        print(f"- 总计: {usage.get('token_count', 0)} tokens")
    else:
        print("新闻重写失败")


if __name__ == "__main__":
    test_news_rewriting()