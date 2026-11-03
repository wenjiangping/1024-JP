"""Derive runtime UI resources from the user's original art, without editing it.

Requires Pillow. Run with --source <the supplied 素材 directory> to rebuild.
Runtime resources are committed; rebuilding is optional.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import uuid
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'game/project'
SPRITES = PROJECT / 'assets/sprites'


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def sprite(name, costumes, x=0, y=0, size=1, rect=None):
    directory = SPRITES / name
    directory.mkdir(parents=True, exist_ok=True)
    old = directory / 'index.json'
    config = json.loads(old.read_text(encoding='utf-8')) if old.exists() else {}
    config.update(heading=90, x=x, y=y, size=size, rotationStyle='none', physicsMode='no',
                  costumeIndex=0, visible=False, isDraggable=False,
                  collisionPivot={'x':0,'y':0}, collisionShapeType='rect',
                  collisionShapeParams=rect or [1,1], costumes=costumes,
                  fAnimations={}, animBindings={}, builder_id=config.get('builder_id', uuid.uuid4().hex[:21]))
    dump(old, config)


def costume(name, filename, w, h):
    return dict(name=name, path=filename, x=w/2, y=h/2, faceRight=0, bitmapResolution=1,
                imageWidth=w, imageHeight=h, builder_id=uuid.uuid4().hex[:21])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'素材')
    args = parser.parse_args()
    source = args.source.resolve()
    manifest = []

    def image_asset(name, filename, width, x=0, y=0, size=.5):
        original = source/filename
        with Image.open(original) as im:
            im = im.convert('RGBA')
            original_size = im.size
            height = round(im.height*width/im.width)
            im = im.resize((width,height), Image.Resampling.LANCZOS)
            target = SPRITES/name
            target.mkdir(parents=True, exist_ok=True)
            im.save(target/'art.png', optimize=True)
        sprite(name, [costume('默认', 'art.png', width, height)], x,y,size,[width,height])
        manifest.append(dict(source=filename, sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                             originalSize=original_size, runtime=f'assets/sprites/{name}/art.png',
                             runtimeSize=[width,height]))

    image_asset('HomeCover','开始封面.png',960)
    image_asset('HelpPanel','游戏开始说明.png',880)
    image_asset('ResultPanel','game over.png',680,0,30)
    badge_costumes=[]
    badge_dir=SPRITES/'Achievement'
    badge_dir.mkdir(parents=True, exist_ok=True)
    for i in range(1,6):
        original=source/f'成就{i}.png'
        with Image.open(original) as im:
            original_size=im.size
            h=round(im.height*640/im.width)
            im.convert('RGBA').resize((640,h),Image.Resampling.LANCZOS).save(badge_dir/f'{i}.png',optimize=True)
        badge_costumes.append(costume(str(i),f'{i}.png',640,h))
        manifest.append(dict(source=original.name,sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                             originalSize=original_size,runtime=f'assets/sprites/Achievement/{i}.png',runtimeSize=[640,h]))
    sprite('Achievement',badge_costumes,0,72,.4375)

    buttons = {
        'MoveLeft':('按键-左.svg',-205,-156,42),
        'MoveRight':('按键-右.svg',-150,-156,42),
        'JumpButton':('按键-上.svg',-95,-156,42),
        'PauseButton':('按键-暂停.svg',120,-156,42),
        'RetryButton':('按键-重新开始-1.svg',175,-156,42),
        'StartButton':('按键-开始.svg',0,-98,146),
        'ResultRetry':('按键-重新开始.svg',-62,-138,110),
        'HomeButton':('按键-返回主页.svg',62,-138,110),
    }
    for name,(filename,x,y,width) in buttons.items():
        import xml.etree.ElementTree as ET
        xml=ET.parse(source/filename).getroot()
        w,h=float(xml.attrib['width']),float(xml.attrib['height'])
        directory=SPRITES/name
        directory.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source/filename,directory/'button.svg')
        cs=[costume('默认','button.svg',w,h)]
        if name=='PauseButton':
            shutil.copyfile(source/'按键-暂停后开始.svg',directory/'resume.svg')
            cs.append(costume('继续','resume.svg',200,200))
        sprite(name,cs,x,y,width/w,[w,h])
        manifest.append(dict(source=filename,sha256=hashlib.sha256((source/filename).read_bytes()).hexdigest(),
                             runtime=f'assets/sprites/{name}/button.svg'))

    def png_sprite(name, im, x=0,y=0,size=.5):
        directory=SPRITES/name
        directory.mkdir(parents=True,exist_ok=True)
        im.save(directory/'art.png')
        sprite(name,[costume('默认','art.png',*im.size)],x,y,size,list(im.size))

    png_sprite('Dimmer',Image.new('RGBA',(960,720),(10,31,38,185)))
    png_sprite('ScreenController',Image.new('RGBA',(1,1),(0,0,0,0)))
    cover_config = SPRITES/'HomeCover/index.json'
    cover = json.loads(cover_config.read_text(encoding='utf-8'))
    cover['visible'] = True
    dump(cover_config, cover)
    with Image.open(SPRITES/'HomeCover/art.png') as im:
        im.convert('RGB').save(PROJECT/'builder-thumbnail.jpeg', quality=92, optimize=True)

    stage=json.loads((PROJECT/'assets/index.json').read_text(encoding='utf-8'))
    for name in ['ScreenController','HomeCover','StartButton','Dimmer','HelpPanel',
                 'ResultPanel','ResultRetry','HomeButton','Achievement']:
        if name not in stage['zorder']:stage['zorder'].append(name)
    stage['builder_spriteOrder']=[json.loads((SPRITES/n/'index.json').read_text(encoding='utf-8'))['builder_id'] for n in stage['zorder'] if isinstance(n,str)]
    dump(PROJECT/'assets/index.json',stage)
    dump(ROOT/'game/UI-ASSETS.json',dict(note='User originals preserved. Runtime PNGs resized proportionally; score and title use native XBuilder Monitor widgets.',assets=manifest))
    print(f'Prepared {len(manifest)} supplied art resources and native Monitor bindings preserved')


if __name__=='__main__':main()
