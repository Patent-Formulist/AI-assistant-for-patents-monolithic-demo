from enum import Enum


class MessageTimings(Enum):
    SHORT_FEEDBACK = 0.5  # Для быстрых подтверждений
    READABLE_FEEDBACK = 2.0  # Чтобы пользователь успел прочитать
    LONG_FEEDBACK = 3.5  # Для важных сообщений
