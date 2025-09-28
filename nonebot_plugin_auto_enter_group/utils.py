import json
from pathlib import Path

from nonebot import logger, require

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

# 使用插件提供的存储路径
DATA_PATH: Path = store.get_plugin_data_file("data.json")

# 全局变量
data = {}


def load_data():
    """加载数据"""
    global data
    try:
        if DATA_PATH.exists():
            with DATA_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            migrated = False
            for _, group_data in data.get("groups", {}).items():
                if "keywords" in group_data:
                    group_data["allowed_keywords"] = group_data.pop("keywords")
                    migrated = True
                if "disallowed_keywords" not in group_data:
                    group_data["disallowed_keywords"] = []
                    migrated = True
            if migrated:
                save_data(data)
                logger.info("数据已迁移。")
            logger.debug("加载数据成功。")
        else:
            data = {"groups": {}}
            save_data(data)  # 创建空文件
            logger.debug("未找到数据文件，已创建新文件。")
    except Exception as e:
        data = {"groups": {}}
        logger.error(f"无法加载数据，原因为: {e}")
    return data


def save_data(data):
    """保存数据"""
    try:
        with DATA_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.debug("数据保存成功。")
    except Exception as e:
        logger.error(f"无法保存数据，原因为: {e}")


def add_keyword_allowed(group_id, keyword):
    """向指定群组添加允许关键词"""
    global data
    if not data:
        load_data()
    group_data = data["groups"].setdefault(
        group_id, {"allowed_keywords": [], "disallowed_keywords": [], "exit_records": {"enabled": False, "members": []}}
    )
    if keyword not in group_data["allowed_keywords"]:  # 防止重复添加
        group_data["allowed_keywords"].append(keyword)
        save_data(data)  # 保存更新后的数据
        logger.info(f"{group_id}添加允许关键词'{keyword}'成功。")
        return True
    else:
        logger.warning(f"允许关键词'{keyword}'已在{group_id}的关键词列表中。")
        return False


def remove_keyword_allowed(group_id, keyword):
    """从指定群组删除允许关键词"""
    global data
    if not data:
        load_data()
    group_data = data["groups"].setdefault(
        group_id, {"allowed_keywords": [], "disallowed_keywords": [], "exit_records": {"enabled": False, "members": []}}
    )
    if keyword in group_data["allowed_keywords"]:
        group_data["allowed_keywords"].remove(keyword)
        save_data(data)
        logger.info(f"{group_id}删除允许关键词'{keyword}'成功。")
        return True
    else:
        logger.warning(f"允许关键词'{keyword}'不在{group_id}的关键词列表中。")
        return False


def add_keyword_disallowed(group_id, keyword):
    """向指定群组添加拒绝关键词"""
    global data
    if not data:
        load_data()
    group_data = data["groups"].setdefault(
        group_id, {"allowed_keywords": [], "disallowed_keywords": [], "exit_records": {"enabled": False, "members": []}}
    )
    if keyword not in group_data["disallowed_keywords"]:  # 防止重复添加
        group_data["disallowed_keywords"].append(keyword)
        save_data(data)  # 保存更新后的数据
        logger.info(f"{group_id}添加拒绝关键词'{keyword}'成功。")
        return True
    else:
        logger.warning(f"拒绝关键词'{keyword}'已在{group_id}的关键词列表中。")
        return False


def remove_keyword_disallowed(group_id, keyword):
    """从指定群组删除拒绝关键词"""
    global data
    if not data:
        load_data()
    group_data = data["groups"].setdefault(
        group_id, {"allowed_keywords": [], "disallowed_keywords": [], "exit_records": {"enabled": False, "members": []}}
    )
    if keyword in group_data["disallowed_keywords"]:
        group_data["disallowed_keywords"].remove(keyword)
        save_data(data)
        logger.info(f"{group_id}删除拒绝关键词'{keyword}'成功。")
        return True
    else:
        logger.warning(f"拒绝关键词'{keyword}'不在{group_id}的关键词列表中。")
        return False


def record_exit(user_id: str, group_id: str):
    """记录用户退群事件"""
    global data
    if not data:
        load_data()
    group_data = data["groups"][group_id]
    if group_data["exit_records"]["enabled"]:
        group_data["exit_records"]["members"].append(user_id)
        save_data(data)
        logger.info(f"记录用户 {user_id} 退出群组 {group_id}。")
    else:
        logger.warning(f"{group_id} 该群组没有开启退群黑名单")


def enable_exit_recording(group_id: str, enabled: bool):
    """启用或禁用退群记录"""
    global data
    if not data:
        load_data()
    group_data = data["groups"].setdefault(
        group_id, {"allowed_keywords": [], "disallowed_keywords": [], "exit_records": {"enabled": False, "members": []}}
    )
    group_data["exit_records"]["enabled"] = enabled
    save_data(data)
    logger.info(f"群组 {group_id} {'开启' if enabled else '关闭'} 退群黑名单。")


def get_group_blacklist(group_id):
    """获取指定群组的退群黑名单"""
    global data
    if not data:
        load_data()
    group_data = data["groups"].get(group_id, {})
    exit_records = group_data.get("exit_records", {"enabled": False, "members": []})
    return exit_records.get("members", [])


def add_to_blacklist(group_id, user_id):
    """将用户添加到指定群组的退群黑名单"""
    global data
    if not data:
        load_data()
    try:
        group_data = data["groups"].setdefault(
            group_id,
            {
                "allowed_keywords": [],
                "disallowed_keywords": [],
                "exit_records": {"enabled": False, "members": []}
            }
        )

        if user_id not in group_data["exit_records"]["members"]:
            group_data["exit_records"]["members"].append(user_id)
            save_data(data)
            return True
        return False
    except:
        return False


def remove_from_blacklist(group_id, user_id):
    """从指定群组的退群黑名单中移除用户"""
    global data
    if not data:
        load_data()
    try:
        group_data = data["groups"].get(group_id)
        if not group_data:
            return False

        if user_id in group_data["exit_records"]["members"]:
            group_data["exit_records"]["members"].remove(user_id)
            save_data(data)
            return True
        return False
    except:
        return False
