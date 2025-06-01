import newspaper
import argparse
import sys,requests
import os,re
from urllib.parse import urlparse,parse_qs,unquote
import pandas as pd

def extract_image_name(proxy_url):
    # """从代理URL中提取真实图片文件名"""
    # 解析代理URL的查询参数
    parsed_url = urlparse(proxy_url)
    query_params = parse_qs(parsed_url.query)
    
    # 提取并解码真实图片URL
    if 'url' in query_params:
        encoded_url = query_params['url'][0]
        real_url = unquote(encoded_url)  # 解码URL编码
    else:
        real_url= proxy_url  # 如果没有查询参数，直接使用原始URL
    # 从真实URL提取文件名
    name = os.path.basename(real_url)
    if(name [-3:] == 'jpg' or name[-3:] == 'png'):
        return name
    else:
        return name+".jpg"  # 如果不是图片文件名，返回默认的jpg文件名
	# 如果无法提取文件名，返回None
    return None

def findall(html):
	# """提取HTML中的所有图片链接"""
	imgs = []
	for i in range(0,len(html)):
		if html[i] == '<' and html[i+1] == 'i' and html[i+2] == 'm' and html[i+3] == 'g':
			j = i + 4
			while j < len(html) and html[j] != '>':
				if html[j] == 's' and html[j+1] == 'r' and html[j+2] == 'c':
					p= j + 5
					# print(f"找到图片标签: {html[i:j+1]}")
					while p < len(html) and html[p] != html[j+4]:
						p += 1
					print(f"找到图片链接: {html[j+5:p]}")
					if p < len(html):
						imgs.append(html[j+5:p])
				j += 1
	# 返回所有提取到的图片链接
	return imgs

def main(args):
	df = pd.read_excel('./datasets.xlsx', index_col = 0) if os.path.exists('./datasets.xlsx') else None
	if df is None:
		# 如果文件不存在，创建一个新的DataFrame
		print("Creating a new DataFrame as datasets.xlsx does not exist.")
		df = pd.DataFrame(columns=['title', 'label', 'source', 'content', 'image'])
	else:
		print("Loading existing DataFrame from datasets.xlsx.")
	url = args.url
	language = args.language
	
	# 创建文章对象
	article = newspaper.Article(url, language = language, 
								keep_article_html = True, 
								browser_user_agent = args.User_Agent
								)
	try:
		# 下载文章
		article.download()
		# 解析文章
		article.parse()
		# 执行自然语言处理
		article.nlp()
		
		# print(article.text)
		
		# 输出文章信息
		text = article.text
		text = re.split(r'[.!?:,\'，。\n\s]',text)
		
		# current_dir =os.getcwd()
		# print(f"当前目录: {current_dir}")
		# 保存文章
		
		with open('./articles.txt', 'w', encoding='utf-8') as f:
			f.write(f"{article.title}\n\n{article.text} \n")
		
		# 下载图片
		html = article.html
		# with open('./test.html', 'w', encoding='utf-8') as f:
		# 	f.write(html)
		
		if not os.path.exists('./rumor_images'):
			os.makedirs('./rumor_images')
			
		start_sit = html.find(article.title)
		end_sit = html.rfind(text[-2] if len(text[-1])==0 else text[-1])
		# print(f"text={text}")
		# print(f"开始位置: {start_sit}, 结束位置: {end_sit}")
		# 提取图片链接
		imgs = findall(html[start_sit:end_sit])
		# print(imgs)
		
		cnt = 0
		image_output =''
		for img in imgs:
			if not (img.startswith('http') or img.startswith('https')):
				img = 'https:' + img  # 确保图片链接是完整的
			cnt += 1
			# print(img)
			img_name = extract_image_name(img)
			if not img_name:
				# 如果无法提取图片名，则使用默认的文件名
				img_name = 'default_image.jpg'
			img_name = f"{cnt}_{img_name}"  # 添加计数前缀以避免重复
			# print(img_name)
			img_path = os.path.join('./rumor_images', img_name)
			if not os.path.exists(img_path):
				try:
					response = requests.get(img, timeout=30, headers={'User-Agent': args.User_Agent})
					response.raise_for_status()
					with open(img_path, 'wb') as img_file:
						img_file.write(response.content)
					print(f"Downloaded image: {img_name}")
					
				except requests.RequestException as e:
					print(f"Failed to download {img}: {e}", file=sys.stderr)
			image_output += img_name + '|'
		image_output = image_output[:-1]  # 去掉最后的分隔符
		# 添加到DataFrame
		df = pd.concat([df, pd.DataFrame({
			'title': [article.title],
			'label': ['0'],
			'source': [article.source_url],
			'content': [article.text],
			'image': [image_output]
		})], ignore_index=True)
	except Exception as e:
		print(f"Error processing the article: {e}", file=sys.stderr)
	
	df.to_excel('./datasets.xlsx', index=True)
	
import nltk
if __name__ == '__main__':
	# nltk.download('punkt_tab') // 一个需要的库
	parser = argparse.ArgumentParser()
	# urldefault = 'https://news.qq.com/rain/a/20250531A06KKP00'  # 默认新闻链接
	urldefault = 'https://news.cctv.com/2025/05/31/ARTIiEFeMgLIJ3hAHSBt7U5M250531.shtml?spm=C94212.P4YnMod9m2uD.ENPMkWvfnaiV.101' # 默认新闻链接
	parser.add_argument('--url', type=str, default=urldefault,help='The URL of the news article to process.')
	parser.add_argument('--language', type=str, default='zh', choices=['zh','en'],help='Language of the article (default: cn).')
	parser.add_argument('--User_Agent', type=str, default = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', help='User_Agent.')
	args = parser.parse_args()
	main(args)