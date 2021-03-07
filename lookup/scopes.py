"""
Define user scopes
"""

OPENLIGHT = 2**0
OPENWASTE = 2**1
OPENWATER = 2**2
OPENCOUNTER = 2**3


names = {
    OPENLIGHT: 'OPENLIGHT',
    OPENWASTE: 'OPENWASTE',
    OPENWATER: 'OPENWATER',
    OPENCOUNTER: 'OPENCOUNTER'
}

names_list = [names[n] for n in names]

