"""Chat channels module with plugin architecture."""

from nano_hermes.channels.base import BaseChannel
from nano_hermes.channels.manager import ChannelManager

__all__ = ["BaseChannel", "ChannelManager"]
