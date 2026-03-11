"""
语音播报模块
提供两种播报能力：
1. 消息播报：对从网页获取的每条新消息进行语音播报（BROADCAST_MESSAGE_ENABLED）
2. 提醒播报：检测消息中的提醒类关键词（注意/留意/转弯/拐点），触发提醒播报（BROADCAST_ALERT_ENABLED）
"""
import os
import re
import logging
import threading

logger = logging.getLogger(__name__)

# 提醒/观察类关键词
BROADCAST_ALERT_KEYWORDS = re.compile(
    r'注意|留意|转弯|拐点',
    re.IGNORECASE
)

# TTS 锁（保证同一时间只有一个语音在播放）
_tts_lock = threading.Lock()


def _env_bool(key: str, default: bool = False) -> bool:
    """读取环境变量布尔值。"""
    val = os.getenv(key, "").strip().lower()
    if not val:
        return default
    return val in ("true", "1", "yes")


def is_message_broadcast_enabled() -> bool:
    """消息播报开关：是否对从网页获取的每条消息进行语音播报。"""
    return _env_bool("BROADCAST_MESSAGE_ENABLED", default=False)


def is_alert_broadcast_enabled() -> bool:
    """提醒播报开关：是否对包含提醒关键词的消息进行语音播报。"""
    return _env_bool("BROADCAST_ALERT_ENABLED", default=True)


def is_broadcast_alert(message: str) -> bool:
    """
    判断消息是否包含提醒类关键词（注意/留意/转弯/拐点）。
    返回 True 表示该消息是提醒类消息。
    """
    if not message:
        return False
    message = message.strip().replace('。', '.')
    message = message.replace('\u2013', '-').replace('\u2014', '-').replace('\u2012', '-').replace('\u2015', '-')
    return bool(BROADCAST_ALERT_KEYWORDS.search(message))


def broadcast_alert(message: str) -> None:
    """
    提醒类消息语音播报：“出现关键词，请人工判断”。
    受 BROADCAST_ALERT_ENABLED 开关控制。
    """
    if not is_alert_broadcast_enabled():
        return
    alert_text = f"出现关键词，请人工判断: {message}"
    logger.warning(f"[提醒播报] {alert_text}")
    print(f"🔊 [提醒播报] {alert_text}")
    _speak_async(alert_text)


def broadcast_message(message: str) -> None:
    """
    消息播报：对从网页获取的每条新消息进行语音朗读。
    受 BROADCAST_MESSAGE_ENABLED 开关控制。
    """
    if not is_message_broadcast_enabled():
        return
    logger.info(f"[消息播报] {message}")
    _speak_async(message)


# 保留旧名 broadcast 作为别名，兼容已有调用
def broadcast(message: str) -> None:
    """提醒播报（兼容别名，等同 broadcast_alert）。"""
    broadcast_alert(message)


def _speak_async(text: str) -> None:
    """在子线程中进行语音播报（非阻塞）。"""
    t = threading.Thread(target=_speak, args=(text,), daemon=True)
    t.start()


def _speak(text: str) -> None:
    """
    同步语音播报。每次调用新建 pyttsx3 引擎，避免跨线程复用导致静默。
    """
    with _tts_lock:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)
            engine.setProperty('volume', 1.0)
            # 尝试选择中文语音
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            logger.error(f"TTS 播报失败: {e}")
