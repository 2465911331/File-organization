import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
import time

# 定义文件类型和对应的文件夹名称（可以根据需要扩展）
FILE_CATEGORIES = {
    # 图片
    '.bmp': '图片', '.jpg': '图片', '.jpeg': '图片', '.png': '图片', '.tif': '图片',
    '.gif': '图片', '.pcx': '图片', '.tga': '图片', '.exif': '图片', '.fpx': '图片',
    '.svg': '图片', '.psd': '设计文件', '.cdr': '设计文件', '.pcd': '图片', '.dxf': '设计文件',
    '.ufo': '设计文件', '.eps': '设计文件', '.ai': '设计文件', '.raw': '图片', '.wmf': '图片',
    '.webp': '图片', '.avif': '图片', '.apng': '图片',
    # 视频
    '.mp4': '视频', '.avi': '视频', '.mkv': '视频', '.mov': '视频', '.wmv': '视频',
    '.flv': '视频', '.ts': '视频', '.rmvb': '视频', '.webm': '视频',
    '.mpg': '视频', '.r3d': '视频', '.mxf': '视频', '.mts': '视频',
    # 音频
    '.mp3': '音频', '.wav': '音频', '.aac': '音频', '.flac': '音频', '.ogg': '音频',
    '.wma': '音频', '.m4a': '音频', '.aiff': '音频',
    # 文档
    '.doc': '文档', '.docx': '文档', '.pdf': '文档', '.txt': '文档', '.xls': '文档',
    '.xlsx': '文档', '.ppt': '文档', '.pptx': '文档', '.md': '文档', '.csv': '文档',
    '.rtf': '文档', '.odt': '文档', '.ods': '文档',
    # 压缩包
    '.zip': '压缩包', '.rar': '压缩包', '.7z': '压缩包', '.tar': '压缩包', '.gz': '压缩包',
    '.bz2': '压缩包', '.xz': '压缩包',
    # 系统镜像
    '.iso': '系统镜像', '.img': '系统镜像', '.bin': '系统镜像', '.dmg': '系统镜像',
    # 程序与脚本
    '.exe': '程序', '.msi': '程序', '.bat': '脚本', '.sh': '脚本', '.py': '脚本',
    '.js': '脚本', '.html': '脚本', '.css': '脚本', '.php': '脚本', '.java': '脚本',
    '.c': '脚本', '.cpp': '脚本', '.cs': '脚本', '.rb': '脚本', '.go': '脚本',
    '.swift': '脚本', '.ts': '脚本', '.json': '脚本', '.xml': '脚本', '.yml': '脚本',
    '.deb': '程序', '.rpm': '程序', '.apk': '程序', '.app': '程序',
    '.appimage': '程序', '.msix': '程序', '.appxbundle': '程序', '.msixbundle': '程序', '.ipk': '程序',
    # 设计文件
    '.dxf': '设计文件', '.dwg': '设计文件', '.psd': '设计文件', '.ai': '设计文件', '.cdr': '设计文件',
    '.skp': '设计文件', '.3ds': '设计文件', '.max': '设计文件',
    # 数据库文件
    '.db': '数据库', '.sql': '数据库', '.sqlite': '数据库', '.mdb': '数据库',
    '.accdb': '数据库',
    # 字体文件
    '.ttf': '字体', '.otf': '字体', '.woff': '字体', '.woff2': '字体', '.eot': '字体',
    # 其他常用
    '.torrent': '种子文件', '.log': '日志文件', '.ini': '配置文件', '.cfg': '配置文件',
    '.bak': '备份文件', '.tmp': '临时文件'
}

# 二级分类规则
SECONDARY_CATEGORIES = {
    '.apk': 'Android',
    '.app': 'macOS',
    '.deb': 'Linux',
    '.rpm': 'Linux',
    '.exe': 'Windows',
    '.msi': 'Windows',
    '.appimage': 'Linux',
    '.msix': 'Windows',
    '.appxbundle': 'Windows',
    '.msixbundle': 'Windows',
    '.ipk': 'Linux'
}

# 未知类型文件的文件夹名称
UNKNOWN_FOLDER = '其他'

class FileOrganizerApp:
    def __init__(self, master):
        self.master = master
        master.title("文件整理工具")
        master.geometry("500x250") # 设置窗口初始大小

        self.folder_path = tk.StringVar()
        self.status_text = tk.StringVar()
        self.status_text.set("请选择要整理的文件夹")

        # --- GUI 组件 ---

        # 文件夹选择部分
        folder_frame = ttk.Frame(master, padding="10")
        folder_frame.pack(fill=tk.X)

        folder_label = ttk.Label(folder_frame, text="目标文件夹:")
        folder_label.pack(side=tk.LEFT, padx=(0, 5))

        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, state='readonly', width=40)
        self.folder_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.browse_button = ttk.Button(folder_frame, text="浏览...", command=self.browse_folder)
        self.browse_button.pack(side=tk.LEFT)

        # 操作按钮部分
        action_frame = ttk.Frame(master, padding="10")
        action_frame.pack(fill=tk.X)

        self.organize_button = ttk.Button(action_frame, text="开始整理", command=self.start_organization_thread, state=tk.DISABLED)
        self.organize_button.pack(pady=5)

        # 进度条部分
        progress_frame = ttk.Frame(master, padding="10")
        progress_frame.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        # 状态标签
        self.status_label = ttk.Label(master, textvariable=self.status_text, padding="10")
        self.status_label.pack(fill=tk.X)

    def browse_folder(self):
        """打开文件夹选择对话框"""
        foldername = filedialog.askdirectory()
        if foldername:
            self.folder_path.set(foldername)
            self.status_text.set(f"已选择: {foldername}")
            self.organize_button.config(state=tk.NORMAL) # 选择了文件夹后启用整理按钮
            self.progress_bar['value'] = 0 # 重置进度条
        else:
            # 如果用户取消选择，保持原状或清空
            # self.folder_path.set("") # 可选：清空路径
            # self.status_text.set("请选择要整理的文件夹") # 可选：重置状态
            self.organize_button.config(state=tk.DISABLED)

    def start_organization_thread(self):
        """启动一个新线程来执行文件整理，防止GUI冻结"""
        selected_path = self.folder_path.get()
        if not selected_path or not os.path.isdir(selected_path):
            messagebox.showerror("错误", "请先选择一个有效的文件夹！")
            return

        # 禁用按钮防止重复点击
        self.organize_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        self.status_text.set("正在准备整理...")
        self.progress_bar['value'] = 0
        self.master.update_idletasks() # 立即更新界面

        # 创建并启动线程
        organize_thread = threading.Thread(target=self.organize_files, args=(selected_path,), daemon=True)
        organize_thread.start()

    def organize_files(self, target_folder):
        """实际执行文件整理的核心逻辑"""
        try:
            files_to_move = []
            # 1. 识别文件
            self.update_status("正在扫描文件...")
            for item in os.listdir(target_folder):
                item_path = os.path.join(target_folder, item)
                if os.path.isfile(item_path):
                    files_to_move.append(item)

            if not files_to_move:
                self.update_status("文件夹中没有需要移动的文件。")
                self.enable_buttons()
                messagebox.showinfo("完成", "文件夹中没有需要移动的文件。")
                return

            # 2. 设置进度条最大值
            self.progress_bar['maximum'] = len(files_to_move)
            processed_count = 0

            self.update_status(f"开始整理 {len(files_to_move)} 个文件...")

            # 3. 移动文件
            for filename in files_to_move:
                source_path = os.path.join(target_folder, filename)
                file_extension = os.path.splitext(filename)[1].lower()  # 获取小写扩展名

                # 确定目标文件夹
                category_folder_name = FILE_CATEGORIES.get(file_extension, UNKNOWN_FOLDER)
                destination_folder_path = os.path.join(target_folder, category_folder_name)

                # 检查是否需要二级分类
                if file_extension in SECONDARY_CATEGORIES:
                    secondary_folder_name = SECONDARY_CATEGORIES[file_extension]
                    destination_folder_path = os.path.join(destination_folder_path, secondary_folder_name)

                # 4. 创建目标文件夹（如果不存在）
                if not os.path.exists(destination_folder_path):
                    try:
                        os.makedirs(destination_folder_path)
                        print(f"创建文件夹: {destination_folder_path}")  # 控制台输出日志
                    except OSError as e:
                        print(f"错误：无法创建文件夹 {destination_folder_path}: {e}")
                        self.update_status(f"错误: 无法创建文件夹 {category_folder_name}")
                        continue  # 跳过这个文件

                # 5. 移动文件
                destination_path = os.path.join(destination_folder_path, filename)

                # 防止文件移动到自身（虽然在此逻辑下不太可能发生）
                if source_path == destination_path:
                    continue

                try:
                    shutil.move(source_path, destination_path)
                    print(f"移动: {filename} -> {destination_folder_path}/")  # 控制台输出日志
                except Exception as e:
                    print(f"错误：无法移动文件 {filename}: {e}")
                    self.update_status(f"警告: 无法移动 {filename}")
                    continue

                # 6. 更新进度条和状态
                processed_count += 1
                self.master.after(0, self.update_progress, processed_count, len(files_to_move))

            self.update_status("整理完成！")
            messagebox.showinfo("完成", f"成功整理了 {processed_count} 个文件。")

        except Exception as e:
            self.update_status(f"发生错误: {e}")
            messagebox.showerror("错误", f"整理过程中发生错误: {e}")
        finally:
            self.enable_buttons()

    def update_status(self, message):
        """安全更新状态标签文本 (从任何线程)"""
        self.master.after(0, lambda: self.status_text.set(message))

    def update_progress(self, current_value, max_value):
        """安全更新进度条 (在主线程中)"""
        self.progress_bar['value'] = current_value
        # 可以选择性地更新状态标签，显示百分比或计数
        # self.status_text.set(f"正在整理... ({current_value}/{max_value})")
        self.master.update_idletasks() # 强制GUI更新

    def enable_buttons(self):
        """安全地重新启用按钮 (从任何线程)"""
        self.master.after(0, lambda: self.organize_button.config(state=tk.NORMAL))
        self.master.after(0, lambda: self.browse_button.config(state=tk.NORMAL))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()