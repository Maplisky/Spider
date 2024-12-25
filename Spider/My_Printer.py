import sys,time

#实现逐字输出，参数包含 text:待输出文本，des：间隔输出时间，sleep：末尾间隔时间，end：结尾字符
def de_print(text, des = 0.08, sleep = 0, end = ''):
    for i in text:
        sys.stdout.write(i)
        sys.stdout.flush()
        time.sleep(des)
    time.sleep(sleep)
    sys.stdout.write(end)