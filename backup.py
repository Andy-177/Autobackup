import os
import shutil
import time
import zipfile
from datetime import datetime
import sys

# 检测是否运行在打包环境
if getattr(sys, 'frozen', False):
    # 打包环境
    current_dir = os.path.dirname(sys.executable)
else:
    # 源代码运行环境
    current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义配置文件路径
config_file_path = os.path.join(current_dir, "backupcfg.cfg")

# 定义backup文件夹路径
backup_folder = os.path.join(current_dir, "backup")

# 定义archive文件夹路径
archive_folder = os.path.join(current_dir, "archive")

# 检查配置文件是否存在，如果不存在则创建
if not os.path.exists(config_file_path):
    with open(config_file_path, "w") as config_file:
        config_file.write("archive = True\n")
        config_file.write("backup_interval = 5\n")
    print(f"配置文件 '{config_file_path}' 已创建。")
else:
    print(f"配置文件 '{config_file_path}' 已存在。")

# 读取配置文件并更新配置
try:
    with open(config_file_path, "r") as config_file:
        config_lines = config_file.readlines()

    config = {}
    for line in config_lines:
        key, value = line.strip().split(" = ")
        if key == "archive":
            config[key] = value.lower() == "true"
        elif key == "backup_interval":
            config[key] = int(value)

    # 如果配置文件中的值无效或缺失，使用默认值并修复配置文件
    if "archive" not in config or not isinstance(config["archive"], bool):
        config["archive"] = True
    if "backup_interval" not in config or not isinstance(config["backup_interval"], int) or config["backup_interval"] <= 0:
        config["backup_interval"] = 5

    # 更新配置文件为有效值
    with open(config_file_path, "w") as config_file:
        config_file.write(f"archive = {config['archive']}\n")
        config_file.write(f"backup_interval = {config['backup_interval']}\n")
    print(f"配置文件 '{config_file_path}' 已更新为有效值。")

except Exception as e:
    print(f"读取配置文件时出错：{e}。使用默认配置并修复配置文件。")
    config = {
        "archive": True,
        "backup_interval": 5
    }
    # 修复配置文件
    with open(config_file_path, "w") as config_file:
        config_file.write(f"archive = {config['archive']}\n")
        config_file.write(f"backup_interval = {config['backup_interval']}\n")
    print(f"配置文件 '{config_file_path}' 已修复。")

# 使用配置文件中的值更新脚本配置
archive = config["archive"]
interval_mins = config["backup_interval"]
interval_seconds = interval_mins * 60

# 创建backup文件夹（如果不存在）
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)
    print(f"文件夹 '{backup_folder}' 已创建。")
else:
    print(f"文件夹 '{backup_folder}' 已存在。")

# 创建archive文件夹（如果不存在）
if not os.path.exists(archive_folder):
    os.makedirs(archive_folder)
    print(f"文件夹 '{archive_folder}' 已创建。")
else:
    print(f"文件夹 '{archive_folder}' 已存在。")

# 定义需要复制的文件夹名称
folders_to_copy = ["world", "world_nether", "world_the_end"]

# 定义源文件夹路径（位于当前脚本的上一级目录）
parent_dir = os.path.dirname(current_dir)

# 无限循环，每过指定时间间隔执行一次复制操作
while True:
    print("开始复制文件夹...")
    for folder in folders_to_copy:
        # 源文件夹路径
        source_folder = os.path.join(parent_dir, folder)
        # 目标文件夹路径
        target_folder = os.path.join(backup_folder, folder)
        
        # 检查源文件夹是否存在
        if os.path.exists(source_folder):
            # 如果目标文件夹已存在，先删除
            if os.path.exists(target_folder):
                shutil.rmtree(target_folder)
                print(f"已存在的目标文件夹 '{target_folder}' 已删除。")
            
            # 复制文件夹及其内容
            shutil.copytree(source_folder, target_folder)
            print(f"文件夹 '{source_folder}' 已成功复制到 '{target_folder}'。")
        else:
            print(f"源文件夹 '{source_folder}' 不存在，跳过复制。")
    
    # 如果启用了Archive功能
    if archive:
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 定义ZIP文件名
        zip_file_name = f"backup_{timestamp}.zip"
        # 定义ZIP文件路径
        zip_file_path = os.path.join(archive_folder, zip_file_name)
        
        # 创建ZIP文件
        with zipfile.ZipFile(zip_file_path, "w") as zipf:
            for folder in folders_to_copy:
                target_folder = os.path.join(backup_folder, folder)
                for root, dirs, files in os.walk(target_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 计算相对路径
                        relative_path = os.path.relpath(file_path, backup_folder)
                        zipf.write(file_path, arcname=relative_path)
        print(f"所有文件夹已压缩为 '{zip_file_path}'。")
    
    # 等待指定的时间间隔
    print(f"等待 {interval_mins} 分钟后再次执行...")
    time.sleep(interval_seconds)