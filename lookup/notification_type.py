"""
Define notification types
"""

EMAIL = 2**0
TELEGRAM = 2**1
SMS = 2**2
PHONE_CALL = 2**1

ALL = EMAIL | TELEGRAM | SMS | PHONE_CALL
