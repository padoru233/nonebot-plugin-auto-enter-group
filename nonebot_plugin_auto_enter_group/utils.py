import json
from pathlib import Path
from nonebot import logger, require

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

# 使用插件提供的存储路径
DATA_PATH: Path = store.get_plugin_data_file("data.json")

# 全局变量
data = None

def load_data():
    """加载数据"""
    global data  # 声明使用全局变量
    try:
        if DATA_PATH.exists():
            with DATA_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug("Loaded data.")
        else:
            data = {"groups": {}}
            save_data(data)  # 创建空文件
            logger.debug("No existing data file found. Starting with empty data.")
    except Exception as e:
        logger.error(f"Failed to initialize data: {e}")
        data = {"groups": {}}
    
    return data

def save_data(data):
    """保存数据"""
    try:
        with DATA_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.debug("Data saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save data: {e}")

def add_keyword(group_id, keyword):
    """向指定群组添加关键词"""
    global data  # 声明使用全局变量
    if data is None:
        load_data()  # 确保数据已加载

    group_data = data["groups"].setdefault(group_id, {"keywords": [], "exit_records": {"enabled": False, "members": []}})

    if keyword not in group_data["keywords"]:  # 防止重复添加
        group_data["keywords"].append(keyword)
        save_data(data)  # 保存更新后的数据
        logger.success(f"Added keyword '{keyword}' for group {group_id}.")
        return True
    else:
        logger.warning(f"Keyword '{keyword}' already exists for group {group_id}.")
        return False

def remove_keyword(group_id, keyword):
    """从指定群组删除关键词"""
    global data
    if data is None:
        load_data()

    group_data = data["groups"].setdefault(group_id, {"keywords": [], "exit_records": {"enabled": False, "members": []}})

    if keyword in group_data["keywords"]:
        group_data["keywords"].remove(keyword)
        save_data(data)
        logger.success(f"Removed keyword '{keyword}' for group {group_id}.")
        return True
    else:
        logger.warning(f"Keyword '{keyword}' does not exist for group {group_id}.")
        return False

def record_exit(user_id: str, group_id: str):
    """记录用户退群事件"""
    global data  # 声明使用全局变量
    if data is None:
        load_data()  # 确保数据已加载

    group_data = data["groups"].setdefault(group_id, {"keywords": [], "exit_records": {"enabled": True, "members": []}})
    
    if group_data["exit_records"]["enabled"]:
        group_data["exit_records"]["members"].append(user_id)
        save_data(data)  # 保存更新后的数据
        logger.success(f"记录用户 {user_id} 退出群组 {group_id}。")
    else:
        logger.warning(f"{group_id} 该群组没有开启退群黑名单")

def enable_exit_recording(group_id: str, enabled: bool):
    """启用或禁用退群记录"""
    global data  # 声明使用全局变量
    if data is None:
        load_data()  # 确保数据已加载

    group_data = data["groups"].setdefault(group_id, {"keywords": [], "exit_records": {"enabled": False, "members": []}})
    group_data["exit_records"]["enabled"] = enabled
    save_data(data)  # 保存更新后的数据
    logger.success(f"群组 {group_id} {'开启' if enabled else '关闭'} 退群黑名单。")
