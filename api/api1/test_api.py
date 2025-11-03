import requests
import json

def test_news_analysis():
    """测试新闻分析API"""
    import logging
    logging.basicConfig(level=logging.INFO)
    # API地址
    url = "http://localhost:8001/analyze"
    

    
    # 测试带HTML标签的新闻内容
    test_news_with_html = f"""
<html>\n <head></head> \n <body> \n  <article> \n   <br> \n   <p> </p > \n   <p>　【中新社河南安阳八月十二日电】（记者　阚力）「之前学习的甲骨文都忘了，现在回炉重造。」台湾网络博主林宛妘近日随参访团在「甲骨文之乡」河南安阳触摸文字「活化石」，从甲骨文「家」字解读两岸文化同源。 </p > \n   <p>　连日来，林宛妘等一行逾二十人在大陆多个古都城市交流参访，赴安阳文字探源是他们最期待的行程之一。 </p > \n   <p>　作为台湾知识类网络博主，林宛妘日常习惯在社交平台分享自己所见所闻。此行，她将温习甲骨文作为重点。从中国文字博物馆到殷墟博物馆，她仔细观察、记录甲骨文字，「我计划梳理一篇关于甲骨文的博文分享在社交平台上」。 </p > \n   <p>　林宛妘说，安阳博物馆系统呈现的汉字演变史充满艺术性，比如甲骨文「家」字是屋顶下有猪，寓意古人家里养了猪就扎根了，「对『家』的释义，古今相通」。 </p > \n   <p>　在书法老师指导下，林宛妘和同伴商宁真提笔蘸墨，模仿书写「家」「福」「乐」等甲骨文。商宁真告诉记者：「从小学三年级跟随父亲学习书法，写过楷书、草书，但写甲骨文还是第一次，古人设计得极具美感。」◇</p > \n   <p></p > \n  </article>  \n </body>\n</html>
    """
    
    # 准备请求数据
    payload = {
        "content": test_news_with_html
    }
    
    try:
        # 发送POST请求
        print("正在发送请求...")
        response = requests.post(url, json=payload)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            
            # 美化输出结果
            print("\n=== API响应结果 ===")
            print(f"状态码: {result.get('code')}")
            print(f"消息: {result.get('msg')}")
            
            if result.get('data'):
                data = result['data']
                print("\n1. 基本信息:")
                print(f"标题: {data.get('title')}")
                print(f"关键词: {', '.join(data.get('keywords', []))}")
                print(f"标签: {', '.join(data.get('tags', []))}")
                print(f"栏目: {data.get('categoryName')}")
                
                print("\n2. 新闻概要:")
                print(data.get('aiIntroduction', ''))
                
                print("\n3. 清理后的内容:")
                content = data.get('content', '')
                print(content)
                
                print("\n4. 分析报告:")
                print(data.get('markdown', '').replace('\\n', '\n'))
            
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("连接失败：请确保API服务器正在运行（http://localhost:8000）")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_news_analysis()
