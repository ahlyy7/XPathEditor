# XPathEditor v1.0.0 — 发布说明

发布日期：一月 19, 2026

简短说明：
XPathEditor 是一个用于编辑、测试与调试 XPath 表达式的小型桌面/工具型应用。此版本为首个稳定发布，包含实时解析与评估、语法高亮、示例文档与会话导入/导出功能，兼容 Windows 与 __Visual Studio 2022__ 调试体验。

主要亮点
- 实时解析与评估 XPath 表达式（基于 elementpath，引入对 XPath 3.1 表达式的支持）
- 可视化编辑器与语法高亮
- 支持 XML 与 HTML 文档加载与解析
- 导入/导出会话（保存当前表达式与结果）
- 基本的 XQuery 风格扩展（for 循环等）
- 在 __Visual Studio 2022__ 中可直接打开、调试与构建（使用 __File > Open > Project/Solution__ 或 __Open Folder__；构建请使用 __Build > Build Solution__，测试可通过 __Test Explorer__ 运行）

新增（主要功能）
- 实时评估面板：即时显示匹配节点与文本结果
- 会话管理：保存/载入工作会话（包含已加载文档与表达式）
- 样例文档集合与使用示例（README 中附示例）
- 基础测试套件（pytest）与 CI 配置骨架

修复与改进
- 修复了在空输入或异常 XPath 表达式时的崩溃问题
- 改进对编码与换行的兼容性（更健壮地处理 Windows/Unix 编码差异）
- 更友好的错误提示与定位信息
- 性能优化：对大型文档的查询评估速度提升与内存占用改进

已知问题
- 部分环境下第三方库（如 `lxml`）可能需要本机编译工具或预编译 wheel；Windows 上可能需安装 __Build Tools for Visual Studio__ 或使用预编译包
- XQuery 扩展为有限子集，尚未实现完整 XQuery 标准
- 对超大 XML/HTML 文档仍存在内存峰值问题，建议分割或使用流式处理

升级与兼容性说明
- 推荐 Python 3.8+（若使用 Python 组件）
- 更新前请备份已有会话文件（导出功能）
- 若使用 Visual Studio 进行构建/调试，请确保使用 __Visual Studio 2022__ 并载入正确的启动项目

安装 / 获取发行版
- 直接下载本仓库的 Release ZIP 或使用 git 克隆：
  - git clone https://github.com/ahlyy7/XPathEditor.git
- 若包含 Python 组件：
  - python -m venv env
  - .\env\Scripts\activate
  - pip install -r requirements.txt
  - python XPathEditorGUI.py（若存在对应入口脚本）

贡献与致谢
- 贡献者：@ahlyy7 及社区贡献者
- 欢迎通过查看仓库根目录的 `CONTRIBUTING.md` 参与贡献（包含分支与提交规范）

许可证
- 本项目采用 MIT 许可证。详见仓库根目录的 `LICENSE` 文件。

附注
- 若需我将此发布说明写入仓库（`RELEASE_NOTES.md`）并创建对应 Release（包括打 tag、上传 zip），请确认是否需要我直接提交并推送或仅生成文本供你手动使用。