import re
from pathlib import Path
from nonebot import on_request, on_notice, Bot, get_driver, logger, on_command
from nonebot.adapters.onebot.v11.event import GroupDecreaseNoticeEvent, GroupMessageEvent, GroupRequestEvent, Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from .utils import load_data, add_keyword, remove_keyword, record_exit, enable_exit_recording

driver = get_driver()

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="加群自动审批",
    description="帮助管理员审核入群请求，退群自动记录拒绝入群",
    usage="""
        查看关键词：群主/管理员可查看入群关键词
        
        添加/删除关键词：添加/删除关键词 <关键词>
        入群答案自动进行关键词模糊匹配
        
        退群黑名单：启用/禁用退群黑名单
        退群后不允许再次加入
    """.strip(),
)

# 加载数据
data = load_data()

# 读取关键词命令
get_keywords = on_command("查看关键词", priority=5, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, block=False)

@get_keywords.handle()
async def handle_get_keywords(event: GroupMessageEvent):
    group_id = str(event.group_id)
    allowed_keywords = data["groups"].get(group_id, {}).get("keywords", [])
    logger.success(f"群组 {group_id} 的关键词被请求。")

    if allowed_keywords:
        await get_keywords.finish(f"当前入群关键词：{', '.join(allowed_keywords)}")
    else:
        await get_keywords.finish("当前没有入群关键词")

# 添加关键词命令
add_keyword_cmd = on_command("添加关键词", priority=5, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, block=True)

@add_keyword_cmd.handle()
async def handle_add_keyword(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = str(event.group_id)
    keyword = args.extract_plain_text().strip()
# 检查关键词是否为空
    if not keyword:
        await add_keyword_cmd.finish("关键词不能为空，请输入有效的关键词。")
        logger.warning(f"尝试添加空关键词到群组 {group_id}。")
        return
    # 调用 data_source.py 中的 add_keyword 函数
    if add_keyword(group_id, keyword):
        await add_keyword_cmd.finish(f"关键词 '{keyword}' 已添加到当前群组。")
        logger.success(f"关键词 '{keyword}' 已添加到群组 {group_id}。")
    else:
        await add_keyword_cmd.finish(f"关键词 '{keyword}' 已存在于当前群组。")
        logger.warning(f"尝试添加已存在的关键词 '{keyword}' 到群组 {group_id}。")

# 删除关键词命令
remove_keyword_cmd = on_command("删除关键词", priority=5, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, block=True)

@remove_keyword_cmd.handle()
async def handle_remove_keyword(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = str(event.group_id)
    keyword = args.extract_plain_text().strip()
    
    if not keyword:
        await remove_keyword_cmd.finish("关键词不能为空，请输入有效的关键词。")
        logger.warning(f"尝试删除空关键词从群组 {group_id}。")
        return

    if remove_keyword(group_id, keyword):
        await remove_keyword_cmd.finish(f"关键词 '{keyword}' 已从当前群组删除。")
        logger.success(f"关键词 '{keyword}' 已从群组 {group_id} 删除。")
    else:
        await remove_keyword_cmd.finish(f"关键词 '{keyword}' 不存在于当前群组。")
        logger.warning(f"尝试删除不存在的关键词 '{keyword}' 从群组 {group_id}。")

# 启用退群记录命令
enable_exit_cmd = on_command("启用退群黑名单", priority=5, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, block=True)

@enable_exit_cmd.handle()
async def handle_enable_exit(event: GroupMessageEvent):
    group_id = str(event.group_id)
# 调用 data_source.py 中的 enable_exit_recording 函数
    enable_exit_recording(group_id, True)
    await enable_exit_cmd.finish(f"群 {group_id} 的退群退群黑名单功能已启用。")
    logger.success(f"群 {group_id} 的退群退群黑名单功能已启用。")

# 禁用退群记录命令
disable_exit_cmd = on_command("禁用退群黑名单", priority=5, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, block=True)

@disable_exit_cmd.handle()
async def handle_disable_exit(event: GroupMessageEvent):
    group_id = str(event.group_id)
# 调用 data_source.py 中的 enable_exit_recording 函数
    enable_exit_recording(group_id, False)
    await disable_exit_cmd.finish(f"群 {group_id} 的退群退群黑名单功能已禁用。")
    logger.success(f"群 {group_id} 的退群退群黑名单功能已禁用。")

# 处理群成员减少事件
group_decrease_handler = on_notice(priority=3, block=False)

@group_decrease_handler.handle()
async def handle_group_decrease(bot: Bot, event: GroupDecreaseNoticeEvent):
    # 检查事件类型
    if event.sub_type in ["leave", "kick"]:
        group_id = str(event.group_id)
        user_id = str(event.user_id)

        # 检查该群组是否启用了退群记录
        group_data = data["groups"].get(group_id, {})
        if group_data.get("exit_records", {}).get("enabled", False):
            record_exit(user_id, group_id)
            logger.success(f"用户 {user_id} 的退群事件已记录在群 {group_id} 中。")
        else:
            logger.info(f"群 {group_id} 的退群黑名单功能已禁用，未记录用户 {user_id} 的退群事件。")

# 处理群请求事件
group_request_handler = on_request(priority=4, block=False)

@group_request_handler.handle()
async def handle_first_receive(bot: Bot, event: GroupRequestEvent):
    flag = event.flag
    sub_type = event.sub_type
    group_id = str(event.group_id)
    user_id = str(event.user_id)

    allowed_answers = data["groups"].get(group_id, {}).get("keywords", [])
    logger.debug(f"群组 {group_id} 的允许关键词: {allowed_answers}")
    
    comment = event.comment
    group_req_ans = re.findall(re.compile('答案：(.*)'), comment)
    group_req_ans = group_req_ans[0] if group_req_ans else comment

    logger.success(f'收到加群请求，答案：{group_req_ans}')

    # 检查群组是否开启了退群记录功能
    group_data = data["groups"].get(group_id, {})
    if group_data.get("exit_records", {}).get("enabled", False):
        # 检查用户是否在退群记录中
        if user_id in group_data.get("exit_records", {}).get("members", []):
            await bot.set_group_add_request(flag=flag, sub_type=sub_type, approve=False, reason='本群已开启退群不允许再次进入。检测到你退出过该群，所以只好说再见！')
            logger.success(f"用户 {user_id} 被拒绝加入群 {group_id}，原因：已退出过该群。")
            return

    await group_request_handler.send(f"收到加群事件：\n用户：{user_id} \n{comment}\n加群类型：{'加群' if sub_type == 'add' else '邀请'}")
    
    if not allowed_answers:
        await group_request_handler.finish("当前群组没有设置关键词，请联系管理员！")
        logger.warning(f"用户 {user_id} 尝试加入群 {group_id}，但该群没有设置关键词。")
        return

    if any(keyword in group_req_ans for keyword in allowed_answers):
        await bot.set_group_add_request(flag=flag, sub_type=sub_type, approve=True, reason=' ')
        await group_request_handler.finish("答案判断成功！已自动处理申请！")
        logger.success("请求基于关键词匹配已批准。")
    else:
        await group_request_handler.finish("答案判断失败！请管理员手动处理一下！")
        logger.success("请求因关键词不匹配被拒绝。")
