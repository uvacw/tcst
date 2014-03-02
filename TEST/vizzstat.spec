# -*- mode: python -*-
a = Analysis(['vizzstat.py'],
             pathex=['/Users/dami/Dropbox/uva/tcst/TEST'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='vizzstat',
          debug=False,
          strip=None,
          upx=True,
          console=True )
