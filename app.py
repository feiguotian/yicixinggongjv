import requests
import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time
import streamlit as st
from PIL import Image
import io

# 配置Tesseract路径（如果已安装，视情况而定）
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows 示例路径

# 设置无头浏览器（不显示图形界面）
options = Options()
options.add_argument("--headless")  # 无头模式
options.add_argument("--no-sandbox")  # 禁用沙盒
options.add_argument("--disable-gpu")  # 禁用 GPU 加速

# 设置 ChromeDriver 路径（与 app.py 在同一文件夹中）
driver_path = Path("chromedriver.exe")  # 使用相对路径

# 使用 Selenium 启动 ChromeDriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 输入微博相册页面链接
url = st.text_input('请输入微博相册页面链接', 'https://m.weibo.cn/p/second?containerid=1078031644724561_-_photoall&page=1&count=24&title=%E5%9B%BE%E7%89%87%E5%A2%99')

if url:
    driver.get(url)
    time.sleep(5)  # 等待页面加载完成，确保图片加载

    # 获取所有图片的 URL
    images = driver.find_elements_by_tag_name('img')
    image_urls = [img.get_attribute('src') for img in images if img.get_attribute('src')]

    if image_urls:
        st.write(f"找到 {len(image_urls)} 张图片，开始识别文字...")
        
        # 下载图片并进行 OCR 识别
        ocr_results = []
        for img_url in image_urls:
            try:
                # 下载图片
                response = requests.get(img_url)
                img = Image.open(io.BytesIO(response.content))

                # 使用 pytesseract 识别图片中的文字
                text = pytesseract.image_to_string(img)
                ocr_results.append(text)
            except Exception as e:
                st.write(f"下载或识别图片时出错: {img_url}, 错误: {e}")
        
        # 将所有识别的文本合并
        result_text = '\n\n'.join(ocr_results)

        # 显示识别结果
        st.text_area('识别结果', result_text, height=300)

        # 提供下载按钮
        st.download_button(
            label="下载识别的文本",
            data=result_text,
            file_name="ocr_result.txt",
            mime="text/plain"
        )

    else:
        st.write("没有找到图片，请确保输入的微博链接正确，或者该页面没有图片。")

# 关闭浏览器
driver.quit()
