from csv import writer
import csv
import tkinter as tk
from tkinter import ttk, filedialog
import os
from elementpath.xpath31 import XPath31Parser

class XPathExtractorFramework:
    def __init__(self, root):
        self.root = root
        self.root.title("XPath 数据提取器 (单表达式)")
        self.root.geometry("900x750")
        
        # 存储数据的变量
        self.file_path = ""  # 文件路径
        self.xpath_expression = ""  # XPath 表达式
        self.results = []  # 提取的结果，可能是多维数组
        self.column_count = 1  # 默认列数
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文件选择部分
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=80)
        self.file_entry.grid(row=0, column=0, padx=(0, 10))
        
        # 浏览文件按钮 - 功能已实现
        ttk.Button(file_frame, text="浏览...", command=self.browse_file).grid(row=0, column=1)
        
        # XPath输入部分
        xpath_frame = ttk.LabelFrame(main_frame, text="XPath 表达式 (输入一个完整的XPath表达式)", padding="10")
        xpath_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.xpath_text = tk.Text(xpath_frame, width=50, height=10)
        self.xpath_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加XPath滚动条
        xpath_scrollbar = ttk.Scrollbar(xpath_frame, orient="vertical", command=self.xpath_text.yview)
        xpath_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.xpath_text.configure(yscrollcommand=xpath_scrollbar.set)
        
        # 列数输入部分
        column_frame = ttk.Frame(xpath_frame)
        column_frame.grid(row=1, column=0, pady=5, sticky=tk.W)
        
        ttk.Label(column_frame, text="列数:").pack(side=tk.LEFT, padx=(0, 5))
        self.column_var = tk.StringVar(value="1")
        self.column_spinbox = ttk.Spinbox(column_frame, from_=1, to=100, width=10, textvariable=self.column_var)
        self.column_spinbox.pack(side=tk.LEFT)
        
        # 转换按钮
        ttk.Button(column_frame, text="转换为二维数组", command=self.convert_to_2d_array, width=15).pack(side=tk.LEFT, padx=10)
        
        # 预览区
        preview_frame = ttk.LabelFrame(main_frame, text="预览结果", padding="10")
        preview_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建带滚动条的文本框来显示结果
        self.create_result_display(preview_frame)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # 确定按钮 - 您需要实现执行逻辑
        self.execute_btn = ttk.Button(button_frame, text="执行 XPath", command=self.execute_xpath, width=15)
        self.execute_btn.pack(side=tk.LEFT, padx=10)
        
        # 导出按钮 - 您需要实现导出逻辑
        self.export_btn = ttk.Button(button_frame, text="导出文件", command=self.export_file, width=15)
        self.export_btn.pack(side=tk.LEFT, padx=10)
        
        # 清空按钮
        ttk.Button(button_frame, text="清空", command=self.clear_all, width=15).pack(side=tk.LEFT, padx=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        xpath_frame.rowconfigure(0, weight=1)
        xpath_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        
    def create_result_display(self, parent):
        """创建结果显示区域 - 使用文本框显示原始结果"""
        # 创建一个Frame来包含文本框和滚动条
        result_frame = ttk.Frame(parent)
        result_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建文本框
        self.result_text = tk.Text(result_frame, width=60, height=25)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加垂直滚动条
        v_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=v_scrollbar.set)
        
        # 添加水平滚动条
        h_scrollbar = ttk.Scrollbar(result_frame, orient="horizontal", command=self.result_text.xview)
        h_scrollbar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.result_text.configure(xscrollcommand=h_scrollbar.set, wrap=tk.NONE)
        
        # 配置网格权重
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
    def browse_file(self):
        """浏览文件 - 功能已实现"""
        filetypes = [
            ("标记语言文件", "*.xml *.html *.htm *.xhtml"),
            ("XML文件", "*.xml"),
            ("HTML文件", "*.html *.htm"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_path = filename
            self.file_path_var.set(filename)
            self.update_status(f"已选择文件: {os.path.basename(filename)}")
    
    def execute_xpath(self):
        """执行XPath查询"""
        # 获取文件路径
        file_path = self.file_path_var.get()
        if not file_path:
            self.update_status("错误: 请先选择文件")
            return
            
        # 获取XPath表达式（整个文本框内容作为一个表达式）
        self.xpath_expression = self.xpath_text.get("1.0", tk.END).strip()
        
        if not self.xpath_expression:
            self.update_status("错误: 请输入XPath表达式")
            return
            
        self.update_status("正在执行XPath查询...")
        
        # 清空结果显示区域
        self.result_text.delete("1.0", tk.END)
        
        try:
            from lxml import etree
            import elementpath
            
            # 加载文件
            if file_path.lower().endswith(('.html', '.htm')):
                parser = etree.HTMLParser()
            else:
                parser = etree.XMLParser()
            tree = etree.parse(file_path, parser)
            
            # 执行 XPath
            self.results = elementpath.select(tree.getroot(), self.xpath_expression, parser=XPath31Parser)
            
            # 在文本框中显示结果
            self.display_results(self.results)
            
            self.update_status(f"执行完成，结果类型: {type(self.results).__name__}")
            
        except Exception as e:
            self.update_status(f"执行错误: {str(e)}")
            # 在文本框中显示错误信息
            self.result_text.insert("1.0", f"错误: {str(e)}")
    
    def display_results(self, results):
        """在文本框中显示结果"""
        if not results:
            self.result_text.insert("1.0", "无结果")
            return
            
        # 清空文本框
        self.result_text.delete("1.0", tk.END)
        
        # 将结果转换为字符串显示
        result_str = self.format_results(results)
        self.result_text.insert("1.0", result_str)
    
    def format_results(self, results):
        """格式化结果为字符串"""
        # 处理不同类型的结果
        if isinstance(results, list):
            if len(results) == 0:
                return "空列表"
            
            # 检查是否为二维数组
            if all(isinstance(item, list) for item in results):
                # 是二维数组
                lines = []
                for i, row in enumerate(results):
                    # 将每行转换为字符串
                    row_str = ", ".join(str(item) for item in row)
                    lines.append(f"行 {i+1} ({len(row)}列): [{row_str}]")
                return "\n".join(lines)
            else:
                # 是一维数组
                items = [str(item) for item in results]
                return f"结果列表 ({len(results)} 项):\n" + "\n".join([f"  {i+1}: {item}" for i, item in enumerate(items)])
        elif isinstance(results, (str, int, float, bool)):
            # 单个值
            return f"单个结果: {results}"
        else:
            # 其他类型
            return f"结果类型: {type(results).__name__}\n值: {str(results)}"
    
    def convert_to_2d_array(self):
        """将一维数组转换为二维数组"""
        if not hasattr(self, 'results') or not self.results:
            self.update_status("错误: 没有数据可以转换，请先执行XPath查询")
            return
        
        try:
            # 获取列数
            column_count = int(self.column_var.get())
            if column_count <= 0:
                self.update_status("错误: 列数必须大于0")
                return
                
            # 检查当前结果是否已经是一维列表
            if not isinstance(self.results, list):
                self.update_status("错误: 结果不是列表类型，无法转换")
                return
                
            # 检查是否为二维列表
            if isinstance(self.results[0], list):
                self.update_status("结果已经是二维数组")
                return
                
            # 计算行数
            total_items = len(self.results)
            rows = total_items // column_count
            if total_items % column_count != 0:
                rows += 1
                
            # 转换为二维数组
            converted_results = []
            for i in range(rows):
                start_idx = i * column_count
                end_idx = min(start_idx + column_count, total_items)
                row = self.results[start_idx:end_idx]
                
                # 如果行不满，用空字符串填充
                if len(row) < column_count:
                    row += [""] * (column_count - len(row))
                    
                converted_results.append(row)
                
            self.results = converted_results
            self.display_results(self.results)
            self.update_status(f"转换完成: {len(self.results)}行 × {column_count}列")
            
        except ValueError:
            self.update_status("错误: 请输入有效的列数")
        except Exception as e:
            self.update_status(f"转换错误: {str(e)}")
    
    def export_file(self):
        """导出文件 - 支持多种格式"""
        if not hasattr(self, 'results') or not self.results:
            self.update_status("错误: 没有数据可以导出，请先执行XPath查询")
            return
        
        # 定义支持的文件格式
        filetypes = [
            ("CSV文件", "*.csv"),
            ("Excel文件 (XLSX)", "*.xlsx"),
            ("Excel文件 (XLS)", "*.xls"),
            ("所有文件", "*.*")
        ]
        
        # 获取文件名
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=filetypes,
            title="导出文件"
        )
        
        if not filename:
            return  # 用户取消了保存
        
        self.update_status("正在导出数据...")
        
        try:
            # 根据文件扩展名选择导出方法
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.csv':
                self.export_to_csv(filename)
            elif file_ext == '.xlsx':
                self.export_to_excel_xlsx(filename)
            elif file_ext == '.xls':
                self.export_to_excel_xls(filename)
            else:
                # 默认使用CSV格式
                self.export_to_csv(filename)
            
            self.update_status(f"数据已导出到: {filename}")
            
        except ImportError as e:
            self.update_status(f"导出错误: 缺少必要的库。请安装: {str(e)}")
        except Exception as e:
            self.update_status(f"导出错误: {str(e)}")
    
    def export_to_csv(self, filename):
        """导出为CSV格式"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            
            # 检查results的维度
            if not self.results:
                return  # 空列表，不保存
            
            # 检查是否为二维列表
            if isinstance(self.results[0], list):
                # 二维列表：直接写入多行
                writer.writerows(self.results)
            else:
                # 一维列表：写入单行
                writer.writerow(self.results)
    
    def export_to_excel_xlsx(self, filename):
        """导出为XLSX格式"""
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl")
        
        # 创建工作簿和工作表
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "XPath结果"
        
        # 写入数据
        if isinstance(self.results[0], list):
            # 二维列表
            for row in self.results:
                ws.append(row)
        else:
            # 一维列表
            ws.append(self.results)
        
        # 保存文件
        wb.save(filename)
    
    def export_to_excel_xls(self, filename):
        """导出为XLS格式"""
        try:
            import xlwt
        except ImportError:
            raise ImportError("xlwt")
        
        # 创建工作簿和工作表
        wb = xlwt.Workbook()
        ws = wb.add_sheet("XPath结果")
        
        # 写入数据
        if isinstance(self.results[0], list):
            # 二维列表
            for row_idx, row in enumerate(self.results):
                for col_idx, value in enumerate(row):
                    ws.write(row_idx, col_idx, str(value))
        else:
            # 一维列表
            for col_idx, value in enumerate(self.results):
                ws.write(0, col_idx, str(value))
        
        # 保存文件
        wb.save(filename)
    
    def clear_all(self):
        """清空所有内容"""
        self.file_path_var.set("")
        self.xpath_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        self.results = []
        self.column_var.set("1")
        self.update_status("已清空所有内容")
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = XPathExtractorFramework(root)
    
    # 使窗口可调整大小
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == "__main__":
    main()