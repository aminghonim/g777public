"""
Grabber Base - الأساس لموديول استخراج البيانات
"""

from ..browser_core import WhatsAppBrowser


class GrabberBase(WhatsAppBrowser):
    """
    Base class for DataGrabber, initializing the WhatsApp session.
    """

    def __init__(self, headless: bool = False):
        super().__init__(headless=headless)
