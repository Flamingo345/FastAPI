from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

# 导入配置
from config import config
from silicon_flow_analyzer import analyze_with_silicon_flow

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="新闻概要分析API", description="分析新闻内容并生成新闻概要和AI深度导读")

class NewsContent(BaseModel):
    """新闻内容请求模型"""
    content: str = Field(..., description="新闻内容")

class NewsAnalysisResponse(BaseModel):
    """新闻分析响应模型"""
    briefSummary: str = Field(..., description="新闻简要概述（100字以内）")
    markdown: str = Field(..., description="Markdown格式的分析报告")

class APIResponse(BaseModel):
    """API统一响应格式"""
    code: int = 0
    msg: str = "success"
    data: Optional[NewsAnalysisResponse] = None

@app.post("/analyze", response_model=APIResponse, summary="分析新闻内容", 
         description="分析新闻内容并生成新闻概要和AI深度导读")
async def analyze_news(news: NewsContent):
    try:
        content = news.content
        
        # 调用Silicon Flow服务进行分析
        logger.info("开始调用Silicon Flow服务分析内容...")
        analysis_result = analyze_with_silicon_flow(content)
        
        # 构建响应数据
        response_data = NewsAnalysisResponse(
            briefSummary=analysis_result['briefSummary'],
            markdown=analysis_result['markdown']
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
    return {"message": "欢迎使用新闻概要分析API，请访问/docs查看文档"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)



