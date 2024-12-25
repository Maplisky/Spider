from My_Printer import de_print
import My_File_oper
import My_web_tool

def SaveData(savepath, result):
    if result:
        de_print("saving......\n", sleep=2)
        de_print(f"爬虫任务完成！文件已保存至: {savepath}\n", sleep=1)
    else :
        # 如果不保存则删除已爬取的内容
        My_File_oper.Delete_Dir(savepath)
        de_print("完成！\n")
    return
        
def getData(Username, url, Max_deep, Max_tries, suffix):
      
    # 设置储存路径
	savepath = My_File_oper.Create_Dir(Username, mod = 1)
    
	# 设置日志文件
	logger_path = My_File_oper.set_logger(savepath, Username)
	
	# 爬取资源
	My_web_tool.Scraper(logger_path, savepath, url, Max_tries, Max_deep, suffix)
	
	return savepath
    
	
# def main():
#     # 命令行输入参数：用户名，访问的 url，最大递归层数（-1 表示不限层数），最大访问次数，特定后缀的文件
# 	suffix = ['html', 'css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'mp4', 'mp3',
#                                               'webm', 'ogg', 'pdf']
# 	if len(sys.argv) > 5:
# 		suffix = sys.argv[5:]
            
# 	savepath = getData(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), suffix)
	
	

# if __name__ == '__main__':
#     main()