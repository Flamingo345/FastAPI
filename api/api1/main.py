from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

# 导入配置
from config import config
from content_cleaner import clean_html_content
from silicon_flow_analyzer import analyze_with_silicon_flow

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="新闻分析API", description="清理新闻内容并通过Silicon Flow分析生成标题、关键词、标签、内容导读等")

class NewsContent(BaseModel):
    """新闻内容请求模型"""
    content: str = Field(..., description="新闻原始内容")

class NewsAnalysisResponse(BaseModel):
    """新闻分析响应模型"""
    content: str = Field(..., description="清理后的新闻内容")
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

@app.post("/analyze", response_model=APIResponse, summary="分析新闻内容", 
         description="清理新闻内容的HTML标签并分析生成标题、关键词、标签、内容导读等信息")
async def analyze_news(news: NewsContent):
    try:
        content = news.content
        
        # 检查内容是否需要清理HTML标签
        if any(tag in content.lower() for tag in ['<html', '<head', '<body', '<article']):
            logger.info("检测到HTML标签，进行内容清理...")
            content = clean_html_content(content)
            logger.info(f"内容清理完成，清理后长度: {len(content)}")
        
        # 调用Silicon Flow服务进行分析
        logger.info("开始调用Silicon Flow服务分析内容...")
        analysis_result = analyze_with_silicon_flow(content)
        
        # 构建响应数据
        response_data = NewsAnalysisResponse(
            content=content,
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    """API根路由"""
    return {"message": "欢迎使用新闻分析API，请访问/docs查看文档"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
