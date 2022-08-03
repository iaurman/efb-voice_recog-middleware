# coding: utf-8
import logging
import copy
import threading
import mimetypes
from os import PathLike
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
import shutil

from ehforwarderbot import coordinator, Middleware, Message, MsgType
from ehforwarderbot.utils import get_config_path
from . import __version__ as version
from .engines.baidu import BaiduSpeech
from .engines.azure import AzureSpeech
from .engines.iflytek import IFlyTekSpeech
from .engines.tencent import TencentSpeech

import time

class VoiceRecogMiddleware(Middleware):
    """
    Middleware - Voice recognize middleware
    Convert voice mesage to text message.
    Author: Catbaron <https://github.com/catbaron>, 
            Eana Hufwe <https://1a23.com>
    """

    middleware_id: str = "catbaron.voice_recog"
    middleware_name: str = "Voice Recognition Middleware"
    __version__ = version.__version__
    logger: logging.Logger = logging.getLogger(
        "plugins.%s.VoiceRecogMiddleware" % middleware_id)

    voice_engines: List = []

    def __init__(self, instance_id: str = None):
        super().__init__()
        self.config: Dict[str: Any] = self.load_config()
        engines: Dict[str, Any] = self.config.get("speech_api", dict())
        # self.lang: str = self.config.get('language', 'zh')

        if "baidu" in engines:
            self.voice_engines.append(
                BaiduSpeech(engines['baidu'])
                )
        if "azure" in engines:
            self.voice_engines.append(
                AzureSpeech(engines['azure'])
            )
        if "iflytek" in engines:
            self.voice_engines.append(
                IFlyTekSpeech(engines['iflytek'])
            )
        if "tencent" in engines:
            self.voice_engines.append(
                TencentSpeech(engines['tencent'])
            )

    def load_config(self) -> Optional[Dict]:
        config_path: Path = get_config_path(self.middleware_id)
        if not config_path.exists():
            raise FileNotFoundError('The configure file does not exist!')
        with config_path.open('r') as f:
            d: Dict[str, Any] = yaml.load(f, Loader=yaml.SafeLoader)
            if not d:
                raise RuntimeError('Load configure file failed!')
                return
            return d

    def recognize(self, file: PathLike) -> List[str]:
        '''
        Recognize the audio file to text.
        :param file: An audio file. It should be FILE object in 'rb'
            mode or string of path to the audio file.
        '''
        with ThreadPoolExecutor(max_workers=5) as exe:
            futures = {
                exe.submit(e.recognize, file): (e.engine_name, e.lang)
                for e in self.voice_engines
            }
            results = []
            for future in as_completed(futures):
                engine_name, lang = futures[future]
                try:
                    data = "; ".join(future.result())
                    if len(data) > 1000:
                        data = data[:1000] + " ..."
                    results.append('\n' + data.rstrip('。'))
                        # f'\n{engine_name} ({lang}): {data}'
                except Exception as exc:
                    results.append(f'\n{engine_name} ({lang}): {repr(exc)}')
            return results

    @staticmethod
    def sent_by_master(message: Message) -> bool:
        return message.deliver_to != coordinator.master

    def process_message(self, message: Message) -> Optional[Message]:
        """
        Process a message with middleware
        Args:
            message (:obj:`.Message`): Message object to process
        Returns:
            Optional[:obj:`.Message`]: Processed message or None if discarded.
        """
        # If sent by slave channel
        if self.sent_by_master(message):
            return message

        # If a voice message
        try:
            if message.type != MsgType.Voice:
                return message
        except Exception as e:
            # Unknown error
            print(f"{e}:, {message.__dict__}")
            raise e

        # If any voice engines loaded
        if not self.voice_engines:
            return message

        # Voice Recognition
        try:
            result_text: str = '\n'.join(self.recognize(message.path))
        except Exception:
            result_text = 'Failed to recognize voice content.'
        if getattr(message, 'text', None) is None:
            message.text = ""
        message.text += result_text
        message.text = message.text[:4000]

        # Return message
        return message
