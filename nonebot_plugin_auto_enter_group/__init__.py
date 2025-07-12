from nonebot import logger, on_command, on_notice, on_request
from nonebot.adapters.onebot.v11 import Bot, GroupDecreaseNoticeEvent, GroupMessageEvent, GroupRequestEvent, Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from .utils import (
    add_keyword_allowed,
    add_keyword_disallowed,
    enable_exit_recording,
    load_data,
    record_exit,
    remove_keyword_allowed,
    remove_keyword_disallowed,
)

# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="加群自动审批",
    description="帮助管理员审核入群请求，退群自动记录拒绝入群",
    type="application",
    homepage="https://github.com/padoru233/nonebot-plugin-auto-enter-group",
    usage="""
        查看关键词：群主/管理员可查看入群关键词
        添加/删除允许关键词 <关键词>：添加/删除自动允许入群关键词
        添加/删除拒绝关键词 <关键词>：添加/删除自动拒绝入群关键词
        入群答案自动进行关键词模糊匹配
        启用/禁用退群黑名单：启用/禁用本群退群黑名单，启用后退群用户将无法再次加入
    """,
    supported_adapters={"~onebot.v11"},
)


# 加载数据
data = load_data()


# 读取关键词命令
get_keywords = on_command(
    "查看关键词",
    priority=5,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=False,
)


@get_keywords.handle()
async def handle_get_keywords(event: GroupMessageEvent):
    group_id = str(event.group_id)
    allowed_keywords = data["groups"].get(group_id, {}).get("allowed_keywords", [])
    disallowed_keywords = data["groups"].get(group_id, {}).get("disallowed_keywords", [])
    message = ""
    if allowed_keywords:
        message += f"当前允许入群关键词：{', '.join(allowed_keywords)}\n"
    else:
        message += "当前没有允许入群关键词\n"
    if disallowed_keywords:
        message += f"当前拒绝入群关键词：{', '.join(disallowed_keywords)}"
    else:
        message += "当前没有拒绝入群关键词"
    await get_keywords.finish(message)


# 添加允许关键词命令
add_allowed_keyword = on_command(
    "添加允许关键词",
    priority=5,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=True,
)


@add_allowed_keyword.handle()
async def handle_add_allowed(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = str(event.group_id)
    keyword = args.extract_plain_text().strip().lower()
    if not keyword:
        await add_allowed_keyword.finish("关键词不能为空，请输入有效的关键词。")
        return
    if add_keyword_allowed(group_id, keyword):
        await add_allowed_keyword.finish(f"允许关键词 '{keyword}' 已添加到当前群组。")
    else:
        await add_allowed_keyword.finish(f"允许关键词 '{keyword}' 已存在于当前群组。")


# 删除允许关键词命令
remove_allowed_keyword = on_command(
    "删除允许关键词",
    priority=5,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=True,
)


@remove_allowed_keyword.handle()
async def handle_remove_allowed(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = str(event.group_id)
    keyword = args.extract_plain_text().strip().lower()
    if not keyword:
        await remove_allowed_keyword.finish("关键词不能为空，请输入有效的关键词。")
        return
    if remove_keyword_allowed(group_id, keyword):
        await remove_allowed_keyword.finish(f"允许关键词 '{keyword}' 已从当前群组删除。")
    else:
        await remove_allowed_keyword.finish(f"允许关键词 '{keyword}' 不存在于当前群组。")


# 添加拒绝关键词命令
add_disallowed_keyword = on_command(
    "添加拒绝关键词",
    priority=5,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=True,
)


@add_disallowed_keyword.handle()
async def handle_add_disallowed(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = str(event.group_id)
    keyword = args.extract_plain_text().strip().lower()
    if not keyword:
        await add_disallowed_keyword.finish("关键词不能为空，请输入有效的关键词。")
        return
    if add_keyword_disallowed(group_id, keyword):
        await add_disallowed_keyword.finish(f"拒绝关键词 '{keyword}' 已添加到当前群组。")
    else:
        await add_disallowed_keyword.finish(f"拒绝关键词 '{keyword}' 已存在于当前群组。")


# 删除拒绝关键词命令
remove_disallowed_keyword = on_command(
    "删除拒绝关键词",
    priority=5,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=True,
)


@remove_disallowed_keyword.handle()
async def handle_remove_disallowed(event: GroupMessageEvent, args: Message = CommandArg()):
    group_id = str(event.group_id)
    keyword = args.extract_plain_text().strip().lower()
    if not keyword:
        await remove_disallowed_keyword.finish("关键词不能为空，请输入有效的关键词。")
        return
    if remove_keyword_disallowed(group_id, keyword):
        await remove_disallowed_keyword.finish(f"拒绝关键词 '{keyword}' 已从当前群组删除。")
    else:
        await remove_disallowed_keyword.finish(f"拒绝关键词 '{keyword}' 不存在于当前群组。")


# 启用退群记录命令
enable_exit_cmd = on_command(
    "启用退群黑名单",
    priority=5,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=True,
)


@enable_exit_cmd.handle()
async def handle_enable_exit(event: GroupMessageEvent):
    group_id = str(event.group_id)
    enable_exit_recording(group_id, True)
    await enable_exit_cmd.finish(f"群 {group_id} 的退群黑名单功能已启用。")
    logger.info(f"群 {group_id} 的退群黑名单功能已启用。")


# 禁用退群记录命令
disable_exit_cmd = on_command(
    "禁用退群黑名单",
    priority=5,
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    block=True,
)


@disable_exit_cmd.handle()
async def handle_disable_exit(event: GroupMessageEvent):
    group_id = str(event.group_id)
    enable_exit_recording(group_id, False)
    await disable_exit_cmd.finish(f"群 {group_id} 的退群黑名单功能已禁用。")
    logger.info(f"群 {group_id} 的退群黑名单功能已禁用。")


# 处理群成员减少事件
group_decrease_handler = on_notice(priority=1, block=False)


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
            try:
                user_name = (await bot.get_stranger_info(user_id=int(user_id)))["nickname"] or "未知昵称"
            except Exception:
                user_name = "未知昵称"
            await group_decrease_handler.finish(f"群友「{user_name}」({user_id})离开了我们，再见，或许再也不见。")
        else:
            try:
                user_name = (await bot.get_stranger_info(user_id=int(user_id)))["nickname"] or "未知昵称"
            except Exception:
                user_name = "未知昵称"
            await group_decrease_handler.finish(f"群友「{user_name}」({user_id})离开了我们，祝她幸福。")


# 处理群请求事件
group_request_handler = on_request(priority=1, block=False)


@group_request_handler.handle()
async def handle_first_receive(bot: Bot, event: GroupRequestEvent):
    flag = event.flag
    sub_type = event.sub_type
    if sub_type == "invite":
        return
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    comment = getattr(event, "comment", "") or ""
    comment = comment.lower()
    group_data = data["groups"].get(group_id, {})
    # 检查群组是否开启了退群记录功能
    if group_data.get("exit_records", {}).get("enabled", False):
        # 检查用户是否在退群记录中
        if user_id in group_data.get("exit_records", {}).get("members", []):
            await bot.set_group_add_request(
                flag=flag,
                sub_type=sub_type,
                approve=False,
                reason="直到现在还执迷于过去，真让人看不下去。",
            )
            logger.info(f"用户 {user_id} 被拒绝加入群 {group_id}，原因：已退出过该群。")
            return
    disallowed_keywords = group_data.get("disallowed_keywords", [])
    if any(keyword in comment for keyword in disallowed_keywords):
        await bot.set_group_add_request(
            flag=flag,
            sub_type=sub_type,
            approve=False,
            reason="你这个人，满脑子都只想着自己呢。",
        )
        logger.info(f"用户 {user_id} 被拒绝加入群 {group_id}，原因：关键词不允许。")
        return
    await group_request_handler.send(f"收到加群请求：\n用户：{user_id} \n验证信息：{comment}")
    allowed_answers = group_data.get("allowed_keywords", [])
    if not allowed_answers:
        logger.warning(f"用户 {user_id} 尝试加入群 {group_id}，但该群没有设置关键词。")
        await group_request_handler.finish("本群未设置关键词，无法自动处理。")
    if any(keyword in comment for keyword in allowed_answers):
        await bot.set_group_add_request(flag=flag, sub_type=sub_type, approve=True, reason=" ")
        logger.info("请求基于关键词匹配已批准。")
        await group_request_handler.finish("判断成功，已自动批准入群。")
    else:
        logger.info("请求因关键词不匹配转入手动处理。")
        await group_request_handler.finish("判断失败，请手动处理申请。")
