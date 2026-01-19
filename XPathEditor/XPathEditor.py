import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import lxml.etree as ET
import elementpath
import csv
import os
from io import StringIO

class XPathExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("XPath 数据提取器")
        self.root.geometry("900x700")
        
        # 存储解析结果
        self.results = []
        self.tree = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文件选择部分
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=80).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(file_frame, text="浏览...", command=self.browse_file).grid(row=0, column=1)
        
        # XPath输入部分
        xpath_frame = ttk.LabelFrame(main_frame, text="XPath 表达式 (每行一个)", padding="10")
        xpath_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        self.xpath_text = tk.Text(xpath_frame, width=50, height=15)
        self.xpath_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加示例XPath
        self.add_example_xpaths()
        
        # 预览区
        preview_frame = ttk.LabelFrame(main_frame, text="预览结果", padding="10")
        preview_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建表格
        self.create_result_table(preview_frame)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="执行 XPath", command=self.execute_xpath, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="导出 CSV", command=self.export_csv, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="清空", command=self.clear_all, width=15).pack(side=tk.LEFT, padx=10)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        xpath_frame.rowconfigure(0, weight=1)
        xpath_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        
    def create_result_table(self, parent):
        """创建结果表格"""
        columns = ("#", "节点", "文本内容", "属性")
        
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=20)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置列标题
        self.tree.heading("#", text="序号")
        self.tree.heading("节点", text="节点")
        self.tree.heading("文本内容", text="文本内容")
        self.tree.heading("属性", text="属性")
        
        # 设置列宽
        self.tree.column("#", width=50, anchor=tk.CENTER)
        self.tree.column("节点", width=150)
        self.tree.column("文本内容", width=250)
        self.tree.column("属性", width=200)
        
    def add_example_xpaths(self):
        """添加示例XPath表达式"""
        examples = [
            "//*",  # 所有元素
            "//title",  # 所有title元素
            "//@href",  # 所有href属性
            "//a/text()",  # 所有a元素的文本
            "//div[@class='content']",  # class为content的div
            "//p[contains(@class, 'text')]",  # class包含text的p元素
            "count(//*)",  # 元素总数
            "//item[position() <= 5]"  # 前5个item元素
        ]
        
        for example in examples:
            self.xpath_text.insert(tk.END, example + "\n")
        
    def browse_file(self):
        """浏览文件"""
        filetypes = [
            ("标记语言文件", "*.xml *.html *.htm *.xhtml"),
            ("XML文件", "*.xml"),
            ("HTML文件", "*.html *.htm"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_path.set(filename)
            self.load_file(filename)
    
    def load_file(self, filename):
        """加载文件"""
        try:
            # 根据文件扩展名选择解析器
            if filename.lower().endswith(('.html', '.htm')):
                parser = ET.HTMLParser()
            else:
                parser = ET.XMLParser()
            
            self.tree = ET.parse(filename, parser)
            messagebox.showinfo("成功", f"文件加载成功: {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载文件:\n{str(e)}")
    
    def execute_xpath(self):
        """执行XPath查询"""
        # 检查文件是否加载
        if not self.file_path.get():
            messagebox.showwarning("警告", "请先选择文件")
            return
            
        if self.tree is None:
            messagebox.showwarning("警告", "请先加载有效的XML/HTML文件")
            return
        
        # 获取XPath表达式
        xpaths = self.xpath_text.get("1.0", tk.END).strip().split('\n')
        xpaths = [x.strip() for x in xpaths if x.strip()]
        
        if not xpaths:
            messagebox.showwarning("警告", "请输入XPath表达式")
            return
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.results = []
        row_index = 1
        
        try:
            root = self.tree.getroot()
            
            for xpath in xpaths:
                try:
                    # 使用elementpath执行XPath
                    results = elementpath.select(root, xpath)
                    
                    if not results:
                        # 如果没有结果，添加占位符
                        self.results.append({
                            'xpath': xpath,
                            'results': [],
                            'count': 0
                        })
                        continue
                    
                    # 处理结果
                    xpath_results = []
                    for i, result in enumerate(results):
                        result_dict = {
                            'index': row_index,
                            'node': str(result.tag) if hasattr(result, 'tag') else type(result).__name__,
                            'text': '',
                            'attrs': ''
                        }
                        
                        # 处理元素节点
                        if hasattr(result, 'tag'):
                            # 获取文本内容
                            if result.text and result.text.strip():
                                result_dict['text'] = result.text.strip()
                            
                            # 获取属性
                            if result.attrib:
                                attrs = ', '.join([f'{k}="{v}"' for k, v in result.attrib.items()])
                                result_dict['attrs'] = attrs
                            
                            # 添加到表格
                            self.tree.insert('', tk.END, values=(
                                row_index,
                                result.tag,
                                result_dict['text'],
                                result_dict['attrs']
                            ))
                            
                        # 处理文本节点或属性
                        elif isinstance(result, str):
                            result_dict['node'] = 'Text/Attr'
                            result_dict['text'] = result[:100]  # 限制长度
                            
                            self.tree.insert('', tk.END, values=(
                                row_index,
                                'Text/Attr',
                                result[:100],
                                ''
                            ))
                        
                        xpath_results.append(result_dict)
                        row_index += 1
                    
                    self.results.append({
                        'xpath': xpath,
                        'results': xpath_results,
                        'count': len(xpath_results)
                    })
                    
                except Exception as e:
                    messagebox.showwarning("XPath错误", f"XPath表达式错误: {xpath}\n错误信息: {str(e)}")
            
            # 显示统计信息
            total_results = sum(r['count'] for r in self.results)
            messagebox.showinfo("完成", f"执行完成！\n共找到 {total_results} 个匹配项")
            
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中发生错误:\n{str(e)}")
    
    def export_csv(self):
        """导出为CSV文件"""
        if not self.results:
            messagebox.showwarning("警告", "没有数据可以导出，请先执行XPath查询")
            return
        
        # 选择保存位置
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入表头
                writer.writerow(['序号', 'XPath表达式', '节点类型', '文本内容', '属性', '原始XPath'])
                
                # 写入数据
                row_num = 1
                for xpath_data in self.results:
                    xpath = xpath_data['xpath']
                    for result in xpath_data['results']:
                        writer.writerow([
                            row_num,
                            result.get('node', ''),
                            result.get('text', ''),
                            result.get('attrs', ''),
                            xpath
                        ])
                        row_num += 1
                
                # 写入统计信息
                writer.writerow([])
                writer.writerow(['统计信息'])
                writer.writerow(['XPath表达式', '匹配数量'])
                for xpath_data in self.results:
                    writer.writerow([xpath_data['xpath'], xpath_data['count']])
            
            messagebox.showinfo("成功", f"数据已导出到:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("导出错误", f"无法导出文件:\n{str(e)}")
    
    def clear_all(self):
        """清空所有内容"""
        self.file_path.set("")
        self.xpath_text.delete("1.0", tk.END)
        self.add_example_xpaths()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.results = []
        self.tree = None

def main():
    root = tk.Tk()
    app = XPathExtractor(root)
    
    # 使窗口可调整大小
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == "__main__":
    main()