# VoiceRecogMiddleware: A middleware for EFB 

## Original Project

本项目基于：https://github.com/ehForwarderBot/efb-voice_recog-middleware

## Changes

1. 保证了只发送一次包括识别的语音，不重复发送
2. 在发送的文字中，去除语音识别工具的名称
3. 在发送的文字中，去除结尾的句号。
4. 删除了'recog`'命令（使用此命令原仓库可满足需求）

## Installation

```
pip install git+https://github.com/iaurman/efb-voice_recog-middleware/
```
