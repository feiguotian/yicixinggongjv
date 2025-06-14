import os
import requests
import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
import streamlit as st

# 安装 Chrome 依赖
os.system("apt-get update")
os.system("apt-get install -y libnss3 libgdk-pixbuf2.0-0 libatk-bridge2.0-0 libxss1 libgdk-x11-2.0-0")

# 配置 Chrome 浏览器选项
options = Options()
options.add_argument("--headless")  # 启动无头模式，避免打开浏览器界面
options.add_argument("--no-sandbox")  # 禁用沙盒
options.add_argument("--disable-gpu")  # 禁用 GPU 加速

# 使用 WebDriverManager 自动下载并启动 ChromeDriver
service = Service(ChromeDriverManager().install())

# 启动 Chrome 浏览器
driver = webdriver.Chrome(service=service, options=options)

# 目标微博用户页面链接
url = st.text_input('请输入微博用户主页链接', '')

if url:
    driver.get(url)
    st.write("页面加载完成，开始提取图片...")

    # 获取页面中所有图片的URL
    images = driver.find_elements_by_tag_name('img')
    image_urls = [img.get_attribute('src') for img in images if img.get_attribute('src')]

    # 下载并处理每张图片
    ocr_results = []
    for img_url in image_urls:
        response = requests.get(img_url)
        img = Image.open(io.BytesIO(response.content))

        # 使用pytesseract识别图片中的文字
        text = pytesseract.image_to_string(img)
        ocr_results.append(text)

    # 将所有识别的文本合并
    result_text = '\n\n'.join(ocr_results)

    # 显示文本结果
    st.text_area('识别结果', result_text, height=300)

    # 提供下载按钮
    st.download_button(
        label="下载识别的文本",
        data=result_text,
        file_name="ocr_result.txt",
        mime="text/plain"
    )

# 关闭浏览器
driver.quit()
