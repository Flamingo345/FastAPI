"""
新闻重写和分析API服务
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import sys
import os



# 导入必要的模块
from content_cleaner import clean_html_content
from silicon_flow_analyzer import analyze_with_silicon_flow
from news_rewriter import NewsRewriter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('news_api.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="新闻重写和分析API",
    description="先对新闻内容进行重写，然后分析生成标题、关键词、标签、内容导读等"
)

class NewsContent(BaseModel):
    """新闻内容请求模型"""
    content: str = Field(..., description="新闻原始内容")

class NewsAnalysisResponse(BaseModel):
    """新闻分析响应模型"""
    original_content: str = Field(..., description="原始新闻内容")
    rewritten_content: str = Field(..., description="重写后的新闻内容")
    title: str = Field(..., description="分析生成的标题")
    keywords: List[str] = Field(..., description="关键词列表")
    tags: List[str] = Field(..., description="标签列表")
    categoryName: str = Field(..., description="栏目名称")
    aiIntroduction: str = Field(..., description="新闻概要（150字以内）")
    markdown: str = Field(..., description="Markdown格式的分析报告")

class APIResponse(BaseModel):
    """API统一响应格式"""
    code: int = 0
    msg: str = "success"
    data: Optional[NewsAnalysisResponse] = None

@app.post("/analyze", response_model=APIResponse, 
         summary="重写并分析新闻内容",
         description="先重写新闻内容，然后分析生成标题、关键词、标签、内容导读等信息")
async def analyze_news(news: NewsContent):
    try:
        original_content = news.content
        
        # 检查内容是否需要清理HTML标签
        if any(tag in original_content.lower() for tag in ['<html', '<head', '<body', '<article']):
            logger.info("检测到HTML标签，进行内容清理...")
            original_content = clean_html_content(original_content)
            logger.info(f"内容清理完成，清理后长度: {len(original_content)}")
        
        # 重写新闻内容
        logger.info("开始重写新闻内容...")
        rewriter = NewsRewriter()
        rewrite_result = rewriter.rewrite_news(original_content)
        
        if not rewrite_result:
            raise Exception("新闻重写失败")
            
        rewritten_content = rewrite_result['rewritten_content']
        logger.info("新闻重写完成")
        
        # 使用重写后的内容调用Silicon Flow服务进行分析
        logger.info("开始调用Silicon Flow服务分析重写后的内容...")
        analysis_result = analyze_with_silicon_flow(rewritten_content)
        
        # 构建响应数据
        response_data = NewsAnalysisResponse(
            original_content=original_content,
            rewritten_content=rewritten_content,
            title=analysis_result.get('title', ''),
            keywords=analysis_result.get('keywords', []),
            tags=analysis_result.get('tags', []),
            aiIntroduction=analysis_result.get('aiIntroduction', ''),
            categoryName=analysis_result.get('categoryName', ''),
            markdown=analysis_result.get('markdown', '')
        )
        
        return APIResponse(
            code=0,
            msg="success",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return APIResponse(
            code=500,
            msg=f"处理失败: {str(e)}",
            data=None
        )

@app.get("/")
def read_root():
    """API根路由"""
    return {"message": "欢迎使用新闻重写和分析API，请访问/docs查看文档"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
