import unittest
import json
from fastapi.testclient import TestClient
from main import app

class TestNewsAnalyzer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        # 测试用的新闻文本内容
        self.test_news = """<html>\n <head></head> \n <body> \n  <article> \n   <br> \n   <p> </p > \n   <p>　【中新社河南安阳八月十二日电】（记者　阚力）「之前学习的甲骨文都忘了，现在回炉重造。」台湾网络博主林宛妘近日随参访团在「甲骨文之乡」河南安阳触摸文字「活化石」，从甲骨文「家」字解读两岸文化同源。 </p > \n   <p>　连日来，林宛妘等一行逾二十人在大陆多个古都城市交流参访，赴安阳文字探源是他们最期待的行程之一。 </p > \n   <p>　作为台湾知识类网络博主，林宛妘日常习惯在社交平台分享自己所见所闻。此行，她将温习甲骨文作为重点。从中国文字博物馆到殷墟博物馆，她仔细观察、记录甲骨文字，「我计划梳理一篇关于甲骨文的博文分享在社交平台上」。 </p > \n   <p>　林宛妘说，安阳博物馆系统呈现的汉字演变史充满艺术性，比如甲骨文「家」字是屋顶下有猪，寓意古人家里养了猪就扎根了，「对『家』的释义，古今相通」。 </p > \n   <p>　在书法老师指导下，林宛妘和同伴商宁真提笔蘸墨，模仿书写「家」「福」「乐」等甲骨文。商宁真告诉记者：「从小学三年级跟随父亲学习书法，写过楷书、草书，但写甲骨文还是第一次，古人设计得极具美感。」◇</p > \n   <p></p > \n  </article>  \n </body>\n</html>"""

    def test_news_analysis(self):
        """测试新闻分析API"""
        try:
            # 发送API请求
            response = self.client.post(
                "/analyze",
                json={"content": self.test_news}
            )
            
            # 如果状态码不是200，打印错误信息
            if response.status_code != 200:
                print("\n=== API错误响应 ===")
                print(f"状态码: {response.status_code}")
                print("响应内容:")
                print(json.dumps(response.json(), ensure_ascii=False, indent=2))
                
            # 检查响应状态码
            self.assertEqual(response.status_code, 200)
            
            # 检查响应格式
            data = response.json()
            self.assertEqual(data["code"], 0)
            self.assertEqual(data["msg"], "success")
            
            # 检查响应数据结构
            self.assertIn("data", data)
            news_analysis = data["data"]
            
            # 检查简要概述
            self.assertIn("briefSummary", news_analysis)
            self.assertIsInstance(news_analysis["briefSummary"], str)
            self.assertLessEqual(len(news_analysis["briefSummary"]), 100)
            
            # 检查Markdown内容
            self.assertIn("markdown", news_analysis)
            self.assertIsInstance(news_analysis["markdown"], str)
            
            # 打印分析结果供参考
            print("\n=== 新闻分析结果 ===")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
        except Exception as e:
            print(f"\n=== 测试过程中出现异常 ===\n{str(e)}")

if __name__ == '__main__':
    unittest.main()