import os
import json
import logging
import time
import requests

from fastapi import HTTPException



# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入配置
from config import config

# 获取硅基流动API配置
SILICON_FLOW_API_KEY = config['api_key']
SILICON_FLOW_API_URL = config['api_url']
API_MODEL = config['api_model']

def analyze_with_silicon_flow(content: str) -> dict:
    """
    调用硅基流动API分析新闻内容
    
    Args:
        content: 新闻内容文本
        
    Returns:
        包含分析结果的字典
    """
    if not SILICON_FLOW_API_KEY:
        raise HTTPException(status_code=500, detail="硅基流动API密钥未配置，请检查.env文件")

    # 构建请求头
    headers = {
        'Authorization': f'Bearer {SILICON_FLOW_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # 调试信息
    logger.info(f"API密钥: {SILICON_FLOW_API_KEY[:8]}...{SILICON_FLOW_API_KEY[-4:]}")
    logger.info(f"API地址: {SILICON_FLOW_API_URL}")
    logger.info(f"使用模型: {API_MODEL}")

    # 新闻分析提示词模板
    ANALYSIS_PROMPT_TEMPLATE = """
    你是一名专业的新闻信息整理助手，擅长将各类新闻内容进行简要总结，并提炼关键信息点，方便读者快速了解新闻的核心内容。

    分析以下新闻内容，提取关键信息并按要求格式化输出，以简体中文输出。

    新闻内容：{content}

    请按以下结构分析并输出（保持JSON格式）：

    {{
        "title": "新闻标题（40字以内）",
        "keywords": ["关键词1", "关键词2", "关键词3", "关键词4"],
        "tags": ["标签1", "标签2", "标签3"],
        "categoryName": "栏目分类（从以下选择：澳闻, 珠海, 港台, 国内, 国际, 旅游, 头条, 头条报, 看澳门, 视频, 贵州, 娱乐, 攻略, 运势, 美食, 外雇天地, 粤韵周刊）",
        "aiIntroduction": "新闻概要（150字以内）",
        "content": "清理后的新闻内容",
        "markdown": "# 新闻分析报告\\n\\n1. **新闻核心概括**\\n   - 标题：[15字以内的标题]\\n   - 内容：[提炼新闻核心主题，概括主要事件]\\n\\n2. **背景与概要**\\n   - 标题：[贴合内容的标题]\\n   - 内容：[用几句话概述新闻的背景、主要事件和核心信息]\\n\\n3. **关键要点**\\n   - 标题：[贴合内容的标题]\\n   - 要点：\\n     * [要点1，可用'背景'、'措施'、'影响'等作为提示词]\\n     * [要点2]\\n     * [要点3]\\n\\n4. **重要信息与指标**\\n   - 标题：[贴合内容的标题]\\n   - 信息：\\n     * [关键数据/时间/地点/指标1]\\n     * [事实2]\\n     * [事实3]\\n\\n5. **结论与趋势**\\n   - 标题：[体现总结性质的标题]\\n   - 内容：[总结新闻的整体趋势、意义、影响或未来发展方向]"
    }}

    注意事项：
    1. 每个部分的标题需与新闻内容相关，不要使用固定的通用标题
    2. 保持语言简洁、逻辑清晰，避免过多无关背景
    3. 数据与指标应忠实于原文表述
    4. 如果某部分信息不足，可以省略该部分，但保持整体结构完整
    5. 确保JSON格式完全正确，所有字符串使用双引号，特别注意转义字符
    6. markdown格式中的换行使用\\n，列表项使用*号
    """

    # 构建请求体
    payload = {
        'model': API_MODEL,
        'messages': [
            {'role': 'system', 'content': '你是一个新闻编辑助手。'},
            {'role': 'user', 'content': ANALYSIS_PROMPT_TEMPLATE.format(content=content)}
        ]
    }

    # 重试机制配置
    max_retries = 3
    retry_delay = 2  # 初始重试延迟(秒)
    retry_count = 0
    response = None

    while retry_count < max_retries:
        try:
            # 发送API请求
            response = requests.post(
                f"{SILICON_FLOW_API_URL}/chat/completions",
                json=payload,
                headers=headers,
                timeout=(10, 30)  # 连接超时10秒，读取超时30秒
            )
            response.raise_for_status()
            result = response.json()
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            retry_count += 1
            logger.warning(f"API调用失败(第{retry_count}/{max_retries}次): {str(e)}，将在{retry_delay}秒后重试")
            time.sleep(retry_delay)
            retry_delay *= 2  # 指数退避
        except requests.exceptions.RequestException as e:
            logger.error(f"API调用失败(不可重试): {str(e)}")
            raise HTTPException(status_code=500, detail=f"调用Silicon Flow API失败: {str(e)}")

    if retry_count >= max_retries and response is None:
        raise HTTPException(status_code=500, detail=f"API调用超时，已重试{max_retries}次")

    try:
        # 解析JSON响应内容
        analysis_result = json.loads(result['choices'][0]['message']['content'])

        # 处理返回结果
        return {
            "title": analysis_result.get('title', '')[:40],  # 限制标题长度
            "keywords": analysis_result.get('keywords', [])[:4],  # 限制关键词数量
            "tags": analysis_result.get('tags', [])[:3],  # 限制标签数量
            "categoryName": analysis_result.get('categoryName', '')[:10],  # 限制栏目名称长度
            "content": analysis_result.get('content', ''),  # 清理后的新闻内容
            "aiIntroduction": analysis_result.get('aiIntroduction', '')[:150],  # 新闻概要，限制150字
            "markdown": analysis_result.get('markdown', '')  # Markdown格式的分析报告
        }
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"API返回格式异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析API响应失败: {str(e)}")
    except Exception as e:
        logger.error(f"分析结果处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理分析结果失败: {str(e)}")
