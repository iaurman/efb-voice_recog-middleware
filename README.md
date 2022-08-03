# VoiceRecogMiddleware: A middleware for EFB 

## Original Project

本项目基于：https://github.com/ehForwarderBot/efb-voice_recog-middleware

## Changes

1. 保证了只发送一次包括识别的语音，不重复发送
2. 只启用一个识别引擎时：去除语音识别工具的名称、去除第一个多余回车
3. 去除结尾的句号。
4. 删除了'recog`'命令（使用此命令原仓库可满足需求）

## Installation

```
pip install git+https://github.com/iaurman/efb-voice_recog-middleware/
```
