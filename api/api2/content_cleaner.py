import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_html_content(html_content: str) -> str:
    """
    清理HTML内容，去除外层标签，只保留内容部分
    
    Args:
        html_content: 原始HTML内容
        
    Returns:
        清理后的内容
    """
    if not html_content:
        return html_content
    
    try:
        # 使用正则表达式去除外层的html、head、body、article标签
        cleaned_content = re.sub(r'<html[^>]*>', '', html_content, flags=re.IGNORECASE)
        cleaned_content = re.sub(r'</html>', '', cleaned_content, flags=re.IGNORECASE)
        cleaned_content = re.sub(r'<head[^>]*>.*?</head>', '', cleaned_content, flags=re.IGNORECASE | re.DOTALL)
        cleaned_content = re.sub(r'<body[^>]*>', '', cleaned_content, flags=re.IGNORECASE)
        cleaned_content = re.sub(r'</body>', '', cleaned_content, flags=re.IGNORECASE)
        cleaned_content = re.sub(r'<article[^>]*>', '', cleaned_content, flags=re.IGNORECASE)
        cleaned_content = re.sub(r'</article>', '', cleaned_content, flags=re.IGNORECASE)
        
        # 去除多余的空白行和首尾空白
        cleaned_content = re.sub(r'\n\s*\n', '\n', cleaned_content)
        cleaned_content = cleaned_content.strip()
        
        logger.info(f"内容清理完成: 原始长度 {len(html_content)} -> 清理后长度 {len(cleaned_content)}")
        return cleaned_content
        
    except Exception as e:
        logger.error(f"清理HTML内容时出错: {str(e)}")
        raise
