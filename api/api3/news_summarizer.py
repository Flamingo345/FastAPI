import json
import logging
import time
import requests
from typing import Dict

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API配置
API_KEY = ''
API_URL = 'https://api.siliconflow.cn/v1'
API_MODEL = 'Qwen/Qwen2.5-32B-Instruct'

class NewsSummarizer:
    """新闻概要生成器"""
    
    def __init__(self, api_key: str = API_KEY, api_url: str = API_URL, api_model: str = API_MODEL):
        self.api_key = api_key
        self.api_url = api_url
        self.api_model = api_model
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _create_prompt(self, content: str) -> str:
        """创建提示词"""
        return f"""
        你是一名专业的新闻信息整理助手，请分析以下新闻内容，生成简要总结和AI导读。

        新闻内容：{content}

        请按以下结构分析并输出（保持JSON格式）：

        {{
            "summary": "新闻概要（150字以内）",
            "aiIntroduction": "AI导读（200字以内，重点提炼新闻价值和影响）"
        }}

        注意事项：
        1. 保持语言简洁、逻辑清晰
        2. 避免过多无关背景信息
        3. 确保内容准确性和客观性
        """

    def _call_api(self, content: str) -> Dict:
        """调用API获取分析结果"""
        payload = {
            'model': self.api_model,
            'messages': [
                {'role': 'system', 'content': '你是一个新闻编辑助手。'},
                {'role': 'user', 'content': self._create_prompt(content)}
            ]
        }

        max_retries = 3
        retry_delay = 2
        
        for retry in range(max_retries):
            try:
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=(10, 30)
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析返回的JSON内容
                analysis_result = json.loads(result['choices'][0]['message']['content'])
                return {
                    'summary': analysis_result.get('summary', '')[:150],
                    'aiIntroduction': analysis_result.get('aiIntroduction', '')[:200]
                }
                
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if retry == max_retries - 1:
                    raise Exception(f"API调用失败，已重试{max_retries}次: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2
            except Exception as e:
                raise Exception(f"API调用或处理失败: {str(e)}")

    def analyze(self, content: str) -> Dict[str, str]:
        """
        分析新闻内容并生成概要和导读
        
        Args:
            content: 新闻内容文本
            
        Returns:
            包含概要和导读的字典
        """
        try:
            logger.info("开始分析新闻内容...")
            result = self._call_api(content)
            logger.info("新闻分析完成")
            return result
        except Exception as e:
            logger.error(f"新闻分析失败: {str(e)}")
            raise

def main():
    """使用示例"""
    # 创建新闻分析器实例
    summarizer = NewsSummarizer()
    
    # 示例新闻内容
    sample_news = """
    在2024年全国两会上，政府工作报告提出，今年国内生产总值预期增长5%左右。
    这一目标的提出，充分考虑了当前国内外经济形势，体现了中国经济发展的韧性和潜力。
    报告还强调，要着力扩大内需，增强经济发展内生动力；深化重点领域改革，持续优化营商环境；
    扩大高水平对外开放，更大力度吸引和利用外资。这些举措将为实现经济增长目标提供有力支撑。
    """
    
    try:
        # 分析新闻内容
        result = summarizer.analyze(sample_news)
        
        # 打印结果
        print("\n=== 新闻分析结果 ===")
        print("\n 新闻概要：")
        print(result['summary'])
        print("\n AI导读：")
        print(result['aiIntroduction'])
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()
