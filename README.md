# ChartViewer
Kivy based tool for visualising data as horizontal barchart or (in future) as other charts

## 2020-9-13 增加中文字体支持
- 下载中文字体（已放在项目中）：我选择了思源字体，因为这种字体是可以免费行业使用的，这样的话，生成的软件就不会因为字体侵权。
- 下载的文件放到你的安装目录里面，我的kivy的安装目录是：

```
/home/你自己的用户名/anaconda3/lib/python3.7/site-packages/Kivy-1.11.0-py3.7-linux-x86_64.egg/kivy/data/fonts
```

- 在home文件夹中，ctr+h 显示所有的文件夹，这里有一个 .kivy 的文件夹，其中有一个配置文件 config.ini ，双击打开，修改如下：

```
#注释掉原来这行
#default_font = ['Roboto', 'data/fonts/Roboto-Regular.ttf', 'data/fonts/Roboto-Italic.ttf', 'data/fonts/Roboto-Bold.ttf', 'data/fonts/Roboto-BoldItalic.ttf']
#改为下面这行
default_font = ['Roboto', 'data/fonts/GenJyuuGothic-Normal-2.ttf']

```
