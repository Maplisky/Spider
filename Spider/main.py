import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import spider,sys

class SpiderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # 界面标题
        self.title_label = tk.Label(root, text="爬爬 Need", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # 输入区域
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(self.input_frame, text="用户名（用于储存文件）:").grid(row=0, column=0, sticky="w")
        self.username_entry = tk.Entry(self.input_frame, width=40)
        self.username_entry.grid(row=0, column=1, padx=10)

        tk.Label(self.input_frame, text="URL:").grid(row=1, column=0, sticky="w")
        self.url_entry = tk.Entry(self.input_frame, width=40)
        self.url_entry.grid(row=1, column=1, padx=10)

        tk.Label(self.input_frame, text="最大递归深度:").grid(row=2, column=0, sticky="w")
        self.max_deep_entry = tk.Entry(self.input_frame, width=40)
        self.max_deep_entry.grid(row=2, column=1, padx=10)

        tk.Label(self.input_frame, text="最大尝试次数:").grid(row=3, column=0, sticky="w")
        self.max_tries_entry = tk.Entry(self.input_frame, width=40)
        self.max_tries_entry.grid(row=3, column=1, padx=10)

        tk.Label(self.input_frame, text="后缀(可选，默认全选):").grid(row=4, column=0, sticky="w")
        self.suffix_entry = tk.Entry(self.input_frame, width=40)
        self.suffix_entry.grid(row=4, column=1, padx=10)

        # 启动按钮
        self.start_button = tk.Button(root, text="开爬！", command=self.start_crawling)
        self.start_button.pack(pady=10)

        # 进度显示区域
        self.progress_label = tk.Label(root, text="任务进度:", font=("Arial", 12))
        self.progress_label.pack()

        self.progress_frame = tk.Frame(root)
        self.progress_frame.pack(fill="both", padx=20, pady=5)

        self.progress_text = tk.Text(self.progress_frame, height=10, state="disabled", wrap="word")
        self.progress_text.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.progress_frame, orient="vertical", command=self.progress_text.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.progress_text.configure(yscrollcommand=self.scrollbar.set)

    def start_crawling(self):
        # 从输入框获取参数
        username = self.username_entry.get().strip()
        url = self.url_entry.get().strip()
        max_deep = self.max_deep_entry.get().strip()
        max_tries = self.max_tries_entry.get().strip()
        suffix = self.suffix_entry.get().strip()

        # 验证输入
        if not username or not url or not max_deep.isdigit() or not max_tries.isdigit():
            messagebox.showerror("输入错误", "请确保所有字段填写正确!")
            return

        suffix_list = suffix.split() if suffix else ['html', 'css', 'js', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'mp4', 'mp3',
                                              'webm', 'ogg', 'pdf']

        # 禁用按钮防止重复操作
        self.start_button.config(state="disabled")

        # 开启新线程执行爬虫任务
        crawler_thread = Thread(
            target = self.run_spider,
            args = (username, url, int(max_deep), int(max_tries), suffix_list),
            daemon = True,
        )
        crawler_thread.start()

    def run_spider(self, username, url, max_deep, max_tries, suffix):
        try:
            # 将输出定向到 GUI
            original_stdout = sys.stdout
            sys.stdout = TextRedirector(self.progress_text)

            # 调用爬虫
            savepath = spider.getData(username, url, max_deep, max_tries, suffix)

            # 恢复按钮
            self.start_button.config(state="normal")
            
			# 文件储存
            result = messagebox.askyesno("确认", "是否储存？")
            spider.SaveData(savepath, result)
            
        except Exception as e:
            messagebox.showerror("错误", f"爬虫任务失败: {e}")
        finally:
            sys.stdout = original_stdout
            self.start_button.config(state="normal")

    def append_progress(self, text):
        self.progress_text.configure(state="normal")
        self.progress_text.insert("end", text + "\n")
        self.progress_text.see("end")
        self.progress_text.configure(state="disabled")


class TextRedirector:
    """将标准输出重定向到文本框"""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", string)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SpiderGUI(root)
    root.mainloop()
