PDF2zh · MegaPower定制版
由 guaguastandup 开源 · 由 epcellic 重建
本项目遵循 AGPL-3.0 license · 基于版本 4.1.7 构建
==================================================

【快速开始】
1. 安装 Python 3.12（https://www.python.org/downloads/，安装时勾选 Add to PATH）
2. 双击外层目录的「启动Server(无窗口).bat」
3. 浏览器自动打开等待页，服务就绪后自动进入控制台
4. 在「翻译」页上传 PDF，点击翻译即可

【首次使用】
- 首次启动会自动安装 flask 等基础依赖（约 1 分钟）
- 首次翻译会自动创建 pdf2zh_next 翻译环境并加载排版模型，
  可能需要 10~30 分钟（取决于网络），之后翻译即为正常速度
- 想提前装好翻译环境，可运行 server\warmup\install-with-uv.bat

【日常使用】
- 启动：双击「启动Server(无窗口).bat」（已在运行则直接打开页面）
- 停止：网页「终端」页 → 停止服务；或开启「关页停服」，
  关闭所有网页约 45 秒后自动停止
- 重启：网页「终端」页 → 重启，完成后页面自动刷新
- 翻译产物在 server\translated\ 目录，网页「本地文件」页可在线打开/另存/删除

【界面说明】
- 翻译：上传 PDF、选择引擎/服务/语言/输出类型，四个操作（翻译/裁剪/对照/裁剪对照）
- 翻译任务：实时进度
- 本地文件：translated 目录文件管理
- 终端：服务器实时日志、交互提示按钮应答、重启/停止
- 帮助：文件类型说明与文档链接

【故障排查】
- 双击没反应：检查 Python 是否安装（命令行执行 py -3 --version）
- 等待页超时：查看 server\server_console.log 中的报错
- 翻译失败：网页「终端」页有实时日志，截图报错信息排查
- 更新翻译环境：在 server 目录执行 py -3 update_packages.py

【开源信息】
原项目: https://github.com/guaguastandup/zotero-pdf2zh
重建者: https://epcellic.github.io
许可证: https://www.gnu.org/licenses/agpl-3.0.en.html
