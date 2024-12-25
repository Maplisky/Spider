import requests
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import My_File_oper,os
import mimetypes,time
import random

# 用 get 方法访问网站,返回 response 
def Get(loggerpath, url, Max_t = 3, time_out = (5,10)):
	s = requests.Session()
	s.mount('http://', HTTPAdapter(max_retries = Max_t-1))
	s.mount('https://', HTTPAdapter(max_retries = Max_t-1))
	
	# headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
	# 		}
	
	headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
	try:
		res = s.get(url, headers = headers, timeout = time_out)
		
		My_File_oper.Write_into_logger(loggerpath, res.status_code)
		
		res.raise_for_status() # 如果状态码不是 200，抛出 HTTPError
		
		return res
	except requests.exceptions.RequestException as e:
		My_File_oper.Write_into_logger(loggerpath, e)
		print(e)
		print("Failed to request,because:" + res.reason + f" with response:{res.status_code}")

# 根据响应头 Content-Type 参数获取文件扩展名
def get_file_extension(web_data, url):
	content_type = web_data.headers.get('Content-Type', '').split(';')[0]
	extension = mimetypes.guess_extension(content_type)
	
	if extension:
		return extension
	else:
		# 尝试从 url 中获取扩展名
		return os.path.splitext(urlparse(url).path)[1]
	
# 下载页面中的资源
def download_file(loggerpath, url, base_path, visited_files, suffix, Max_retries = 3):
	try:
		if url in visited_files:
			return # 已下载的文件，跳过
		
		for attempt in range(Max_retries):
			try:
				time.sleep(0.1+random.random())
				web_data = Get(loggerpath, url, time_out = 30)
				break
			except requests.exceptions.RequestException as e:
				My_File_oper.Write_into_logger(loggerpath, e)
				print(e)
				print("Failed to request,because:" + web_data.reason + f" with response:{web_data.status_code}")
				if attempt + 1 == Max_retries:
					raise  # 在最后一次尝试后仍失败，抛出异常
				time.sleep(2 ** attempt)
		
		if web_data == None:
			return
		
		# 提取文件名
		parsed_url = urlparse(url)
		filename = os.path.basename(parsed_url.path)
		if not filename :
			filename = My_File_oper.File_Renamer(parsed_url.path)
		
		# 确定文件扩展名
		file_extension = get_file_extension(web_data, url)
		if not filename.endswith(file_extension):
			filename += file_extension
		
		# 根据文件类型创建子目录
		file_type = file_extension.replace('.', '').lower()
		
		# 文件非特定扩展名，则退出
		if not file_type or file_type not in suffix:
			return
		
		if not file_type or file_type not in ['html', 'css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'mp4', 'mp3',
                                              'webm', 'ogg', 'pdf']:
			file_type = 'other'
			
		dir_path = os.path.join(base_path, file_type)
		My_File_oper.Create_Dir(path = dir_path)
		
		
		# 如果文件名重复，则添加后缀避免覆盖
		file_path = os.path.join(dir_path, filename)
		
		base_name, ext = os.path.splitext(file_path)
		cnt = 1
		while os.path.exists(file_path):
			file_path = f"{base_name}_{cnt}{ext}"
			cnt += 1
		
		My_File_oper.Create_File(file_path, web_data.content, 'wb')
		
		# 记录已下载的文件
		visited_files.add(url)
		
		My_File_oper.Write_into_logger(loggerpath, f"Downloaded {url} to {file_path}")
		
		print(f"Downloaded {url} to {file_path}")
	except requests.exceptions.RequestException as e:
		My_File_oper.Write_into_logger(loggerpath, e)
		print(f"Failed to download {url} after {Max_retries + 1} attempts. Bacause: {e}")
		
		
# 爬取页面
def Scraper(loggerpath, savepath, base_url, Max_tries, Max_deep, suffix, visited = None, visited_files = None):
	if visited is None:
		visited = set()
	if visited_files is None:
		visited_files = set()
		
	# 标记已访问过的页面
	if base_url in visited:
		return
	
	# 达到最大递归层数
	if Max_deep == 0:
		return
	
	My_File_oper.Write_into_logger(loggerpath, f"Infomation: {loggerpath} Dirs = {savepath}")
	
	visited.add(base_url)
	
	# 读取网页数据
	web_data = Get(loggerpath, base_url, Max_tries)
    
	html = web_data.text.encode('iso-8859-1')
      
	soup = BeautifulSoup(html, 'html.parser')
    
	# 保存网页源代码
	parsed_url = urlparse(base_url)
	if parsed_url.path == '/' or parsed_url == '':
		file_path = os.path.join(savepath, 'index.html')
	else:
		file_path = os.path.join(savepath, parsed_url.path.strip("/").replace("/", "_") + '.html')
	
	My_File_oper.Create_File(file_path, soup.prettify())
	
	My_File_oper.Write_into_logger(loggerpath, f"Save HTML to {file_path}")
	
	print(f"Save HTML to {file_path}")
	
	Threads = []
	with ThreadPoolExecutor(max_workers = 5) as executor:
		for tag in soup.find_all(['link','script','img','video','audio','iframe']):
			src = None
			if tag.name == 'link' and 'href' in tag.attrs:
				src = tag['href']
			elif tag.name == 'script' and 'src' in tag.attrs:
				src = tag['src']
			elif tag.name == 'img' and 'src' in tag.attrs:
				src = tag['src']
			elif tag.name in ['video', 'audio', 'iframe'] and 'src' in tag.attrs:
				src = tag['src']
			
			if src:
				resource_url = urljoin(base_url,src)
				Threads.append(executor.submit(download_file, loggerpath, resource_url, savepath, visited_files, suffix))
		
		# 递归爬取子链接
		for son_link_tag in soup.find_all('a', href = True):
			href = son_link_tag['href']
			son_url = urljoin(base_url, href)
			# 仅爬取主域名下的子链接
			if urlparse(son_url).netloc == urlparse(base_url).netloc:
				Threads.append(executor.submit(Scraper, loggerpath, savepath, son_url, Max_tries, Max_deep - 1, suffix, visited, visited_files))

		
		for futures in as_completed(Threads):
			futures.result()
			
	print("Scrapping completed!")
	