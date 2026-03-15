from typing import Tuple, Optional
import ctypes
import ctypes.wintypes
from ctypes import windll

# Konstanta CryptProtectData (DPAPI)
CRYPTPROTECT_UI_FORBIDDEN = 0x01

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_char))
    ]

def crypt_protect_data(data_bytes: bytes) -> Optional[bytes]:
    """Mengenkripsi data menggunakan Windows DPAPI."""
    if not isinstance(data_bytes, bytes):
        raise TypeError("Data harus berupa bytes")

    # Inisialisasi input blob
    data_in = DATA_BLOB()
    data_in.cbData = len(data_bytes)
    data_in.pbData = ctypes.cast(ctypes.c_char_p(data_bytes), ctypes.POINTER(ctypes.c_char))

    # Output blob kosong
    data_out = DATA_BLOB()

    # Memanggil Windows API
    success = windll.crypt32.CryptProtectData(
        ctypes.byref(data_in),
        ctypes.c_wchar_p("GitLabClonerApp Token"),  # Deskripsi (optional)
        None,  # Entropy opsional, None = default
        None,  # Reserved
        None,  # Prompt struct opsional, None = default
        CRYPTPROTECT_UI_FORBIDDEN,  # Flags
        ctypes.byref(data_out)
    )

    if not success:
        return None

    # Mengambil hasil byte dari output blob
    result = ctypes.string_at(data_out.pbData, data_out.cbData)
    
    # Bebaskan alokasi memori Windows
    if data_out.pbData:
        windll.kernel32.LocalFree(ctypes.cast(data_out.pbData, ctypes.c_void_p))

    return result

def crypt_unprotect_data(encrypted_bytes: bytes) -> Optional[bytes]:
    """Mendekripsi data menggunakan Windows DPAPI."""
    if not isinstance(encrypted_bytes, bytes):
        raise TypeError("Encrypted data harus berupa bytes")

    data_in = DATA_BLOB()
    data_in.cbData = len(encrypted_bytes)
    data_in.pbData = ctypes.cast(ctypes.c_char_p(encrypted_bytes), ctypes.POINTER(ctypes.c_char))

    data_out = DATA_BLOB()
    
    success = windll.crypt32.CryptUnprotectData(
        ctypes.byref(data_in),
        None,  # Deskripsi out (bisa berupa ref ke pointer str jika mau)
        None,  # Entropy
        None,  # Reserved
        None,  # Prompt Struct
        CRYPTPROTECT_UI_FORBIDDEN, # Flags
        ctypes.byref(data_out)
    )

    if not success:
        return None

    result = ctypes.string_at(data_out.pbData, data_out.cbData)

    if data_out.pbData:
        windll.kernel32.LocalFree(ctypes.cast(data_out.pbData, ctypes.c_void_p))

    return result
