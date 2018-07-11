# -*- mode: python -*-

"""
# NOTE for using packager like pyinstaller:
# matplotlib has an *rc file in which it wants to load TkAgg
# This can be modified if Tkinter is not needed
# otherwise get Tkinter and FileDalog as 'hidden-imports'
# from the file:  /etc/matplotlibrc: (changes marked with ***)

    #### CONFIGURATION BEGINS HERE

    # The default backend; one of GTK GTKAgg GTKCairo GTK3Agg GTK3Cairo
    # CocoaAgg MacOSX Qt4Agg Qt5Agg TkAgg WX WXAgg Agg Cairo GDK PS PDF SVG
    # Template.
    # You can also deploy your own backend outside of matplotlib by
    # referring to the module name (which must be in the PYTHONPATH) as
    # 'module://my_backend'.

    #modified by ullix
    #backend      : TkAgg
*** backend      : Qt4Agg


    # If you are using the Qt4Agg backend, you can choose here
    # to use the PyQt4 bindings or the newer PySide bindings to
    # the underlying Qt4 toolkit.

    #modified by ullix
    #backend.qt4 : PyQt4        # PyQt4 | PySide
*** backend.qt4 : PyQt4        # PyQt4 | PySide

"""

block_cipher = None

#options = [ ('v', None, 'OPTION'), ('W ignore', None, 'OPTION') ]
options = [ ]

a = Analysis(['geigerlog'],
             pathex=['/home/ullix/geigerlog'],
             binaries=[],
             datas=[('gres/*', 'gres'), ('data/*', 'data'), ('geigerlog.cfg', '.'), ('matplotlibrc', '.'), ('GeigerLog-Manual*', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['wx', 'gtk+', 'Tkinter', 'gtk', 'gdk', 'gtk2', 'gtk3', 'cairo', 'wayland', 'xinerama', 'share', 'icons', 'atk', 'pango', 'pil', 'PIL'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          options,
          exclude_binaries=True,
          name='geigerlog',
          debug=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='geigerlog')
