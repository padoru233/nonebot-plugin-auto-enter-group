<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/raw/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/raw/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-auto-enter-group

_✨ NoneBot2 加群自动审批 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/padoru233/nonebot-plugin-auto-enter-group.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-auto-enter-group">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-auto-enter-group.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

帮助管理员审核入群请求，退群自动记录拒绝入群

## 📖 介绍

在群内播报申请和审核状态，添加关键词后自动进行模糊匹配。  
可开启退群黑名单，自动拒绝退群的人再次申请。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-auto-enter-group

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-auto-enter-group
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-auto-enter-group
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-auto-enter-group
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-auto-enter-group
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_auto_enter_group"]

</details>

## ⚙️ 配置

无配置项，涉及到群管需用命令进行配置
插件数据存储在目录 ``~/.local/share/nonebot2/nonebot_plugin_auto_enter_group``

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 查看关键词 | 群主/管理员/超级用户 | 否 | 群聊 | ———— |
| 添加/删除允许关键词 | 群主/管理员/超级用户 | 否 | 群聊 | <关键词> |
| 添加/删除拒绝关键词 | 群主/管理员/超级用户 | 否 | 群聊 | <关键词> |
| 启用/禁用退群黑名单 | 群主/管理员/超级用户 | 否 | 群聊 | ———— |

## 🌹 鸣谢

感谢 [大橘](https://github.com/zhiyu1998) 提供的代码，多写点让我抄抄！  
由于我不是代码相关专业，使用AI协助完成的代码
