# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],                            # Nama file utama Python kamu
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['psutil'],               # Memastikan pustaka psutil ikut terbungkus
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Internet Data',                    # <--- UBAH NAMA APLIKASI .EXE DI SINI
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                          # <--- FALSE agar jendela hitam CMD tidak muncul
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',                        # <--- NAMA FILE ICON KAMU (Harus format .ico)
)