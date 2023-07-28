# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=['/home/ubuntu/projects/robot/iris'],  # 수정된 pathex
    binaries=[],
    datas=[

        ('/home/ubuntu/projects/robot/iris/mmdet', 'mmdet'),
        ('/home/ubuntu/projects/robot/iris/mmseg', 'mmseg'),
        ('/home/ubuntu/projects/robot/iris/odCfgFile', 'odCfgFile'),
        ('/home/ubuntu/projects/robot/iris/sgCfgFile', 'sgCfgFile'),
        ('/home/ubuntu/projects/robot/iris/yoloCfgFile', 'yoloCfgFile'),
        ('/home/ubuntu/.pyenv/versions/3.8.12/lib/python3.8/site-packages/mmcv', 'mmcv'),  # mmcv 패키지 위치를 잘 찾아서 넣어주세요
        ('/home/ubuntu/.pyenv/versions/3.8.12/lib/python3.8/site-packages/yapf_third_party/_ylib2to3', 'yapf_third_party/_ylib2to3'),  # yapf의 Grammar.txt 위치를 잘 찾아서 넣어주세요
        ('/home/ubuntu/projects/robot/iris/screen/calibration/index.py', 'screen/calibration'),
        ('/home/ubuntu/projects/robot/iris/screen/image_shoot/index.py', 'screen/image_shoot'),
        ('/home/ubuntu/projects/robot/iris/screen/inference/index.py', 'screen/inference'),
        ('/home/ubuntu/projects/robot/iris/screen/inference/category.py', 'screen/inference'),
        ('/home/ubuntu/projects/robot/iris/screen/calibration/step/step1.py', 'screen/inference/step'),
        ('/home/ubuntu/projects/robot/iris/screen/calibration/step/step2.py', 'screen/inference/step'),
        ('/home/ubuntu/projects/robot/iris/screen/calibration/step/step3.py', 'screen/inference/step'),
        ('/home/ubuntu/projects/robot/iris/screen/image_shoot/step/step1.py', 'screen/image_shoot/step'),

    ],
    hiddenimports=[
        'mmdet',
        'mmcv',
        'mmdet.apis',
        'mmdet.models',
        'mmseg.apis',
        'mmcv.image',
        'mmcv.ops',
        'mmcv.array',
        'yapf',  # yapf를 추가
        # 필요에 따라 더 추가
    ],
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
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)