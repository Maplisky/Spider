main.py 实现通过 url 读取 text + img，读取到的文件放在运行目录下，文本为 articles.txt，图像文件夹为 rumor_images

运行直接命令行跑 run.py 即可，提供了 User-Agent 的可选参数，最好这里可以直接使用用户的 UA。

注意替换一下代码里的 python 解释器路径

输入为 url.xlsx，内部格式为两列，第一列为 url，第二列为 language （可选 zh/en，默认为 zh）

| url  | language |
| ---- | -------- |
| ...  | ...      |

输出为 datasets.xlsx，符合模型的输入要求

|      | title | label | source | content | image |
| ---- | ----- | ----- | ------ | ------- | ----- |
| 0    |       |       |        |         |       |
| 1    |       |       |        |         |       |
| 2    |       |       |        |         |       |

可以直接给到模型

需要的 python 库如下：

>   newspaper3k
>   argparse
>   sys
>   requests
>   os
>   urllib.parse
>   pandas
>   nltk
>
>   其中 nltk 库下需要运行 nltk.download('punkt_tab') 