import os
import argparse
import pandas as pd
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--User_Agent', type=str, default = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', help='User_Agent.')
	args= parser.parse_args()
	
	python_path = 'D:/Others/Anaconda/envs/myenv/python.exe'  # 替换为你的Python解释器路径
	try:
		df = pd.read_excel('./url.xlsx',dtype={'url': str, 'language': str})
	except FileNotFoundError:
		print("url.xlsx 文件不存在，请确保文件存在于当前目录。")
		exit(1)
	
	# print(f"读取到的URL: {urls}")
	# print(df)
	for row in df[['url', 'language']].itertuples(index=False):
		# print(type(row.url),type(row.language))
		url = row.url.strip()
		language = str(row.language).strip()
		if language=='nan':
			language = 'zh'
		if language not in ['zh', 'en']:
			print(f"不支持的语言: {language}，跳过")
			continue
		if not url:
			print("空URL，跳过")
			continue
		print(f"Processing URL: {url}, Language: {language}")
		os.system(f'{python_path} main.py --url {url} --language {language} --User_Agent "{args.User_Agent}"')
		