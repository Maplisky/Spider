import time,os,re

# 处理不合法文件名
def File_Renamer(file_name):
	illegal = r'[\/\\\:\*\?\"\<\>\|]'
	file_name = re.sub(illegal, '_', file_name)
	return file_name
		

# 按照时间创建文件夹
def Create_Dir(Username = 'admin', mod = 0, **kwargs):
	try:
		if mod:
			savetime = time.asctime()
			savepath = File_Renamer(Username + " " + savetime)
			os.makedirs(savepath)
			return savepath
		else :
			if not os.path.exists(kwargs['path']):
				os.makedirs(kwargs['path'])
	except OSError as e:
		print(f'Error occurred:{e}')
		exit(0)

# 删除文件夹
def Delete_Dir(file_path):
	try:
		os.system(f'rmdir /s /q \"{file_path}\"')
	except OSError as e:
		print(f'Error occurred:{e}')
		
# 创建文件，参数为：(储存路径+文件名)，内容
def Create_File(file_path, content, write_mod = 'w'):
	if write_mod != 'w':
		with open(file_path, write_mod) as file:
			file.write(content)
	else :
		with open(file_path, write_mod, encoding = "utf-8") as file:
			file.write(content)

# 向日志文件写入
def Write_into_logger(file_path, content):
	try:
		savetime = time.asctime()
		with open(file_path, 'a') as file:
			file.write(f"{savetime} {content}\n")
	except PermissionError:
		print("Failed to write into log!")
		
# 设置日志文件
def set_logger(savepath,Username):
	logger_path = f"{savepath}\\logger.log"
	Write_into_logger(logger_path, f"Username: {Username}\n")
	return logger_path
