import os
import requests
import time
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import streamlit as st

# 配置Tesseract路径（根据您的安装路径修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows示例路径

# Streamlit界面
st.title('微博图片OCR识别工具')
st.write('请输入微博用户主页链接以获取其图片中的文字.')

# 输入微博链接
url = st.text_input('请输入微博用户主页链接:', 'https://m.weibo.cn/u/1644724561?luicode=10000011&lfid=1005051644724561')

# 提交按钮
if st.button('获取图片并识别文字'):
    if url:
        with st.spinner('正在获取图片和识别文字...'):
            # 设置浏览器选项，防止反爬虫
            options = Options()
            options.add_argument("--headless")  # 无界面模式
            options.add_argument("--disable-gpu")  # 禁用GPU加速
            options.add_argument("--no-sandbox")  # 不使用沙盒
            driver = webdriver.Chrome(options=options)

            # 打开微博页面
            driver.get(url)
            time.sleep(3)  # 等待页面加载完成

            # 获取页面的HTML内容
            html = driver.page_source

            # 关闭浏览器
            driver.quit()

            # 使用BeautifulSoup解析页面内容
            soup = BeautifulSoup(html, 'html.parser')

            # 提取所有图片URL
            image_urls = []
            images = soup.find_all('img')
            for img in images:
                if 'src' in img.attrs:
                    img_url = img.attrs['src']
                    if img_url.startswith('http'):
                        image_urls.append(img_url)

            # 创建文件夹保存图片
            os.makedirs('images', exist_ok=True)

            # 下载图片
            for idx, img_url in enumerate(image_urls):
                img_response = requests.get(img_url)
                img_path = os.path.join('images', f'image_{idx+1}.jpg')
                
                # 保存图片到本地
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)

            # 对每张图片使用OCR识别文字
            ocr_texts = []
            for idx in range(len(image_urls)):
                img_path = os.path.join('images', f'image_{idx+1}.jpg')
                img = Image.open(img_path)
                
                # 使用OCR识别图片中的文字
                text = pytesseract.image_to_string(img)
                ocr_texts.append(text)

            # 将识别的文字保存到文本文件
            result_file = 'ocr_result.txt'
            with open(result_file, 'w', encoding='utf-8') as f:
                for idx, text in enumerate(ocr_texts):
                    f.write(f"图片 {idx+1} 的文字内容：\n")
                    f.write(text)
                    f.write("\n\n")

            # 提供下载链接
            st.success('OCR识别完成！')
            st.download_button(
                label="下载识别的文字",
                data=open(result_file, 'r').read(),
                file_name=result_file,
                mime='text/plain'
            )
    else:
        st.error("请输入有效的微博链接！")
