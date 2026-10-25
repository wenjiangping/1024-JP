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
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'game/project'
SPRITES = PROJECT / 'assets/sprites'
RANKS = ['蹦跶小新手', '树影穿梭客', '灌木飞毛腿', '林间寻路家', '风之探险家', '森林守护者']


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
        'JumpButton':('按键-上.svg',212,-156,42),
        'PauseButton':('按键-暂停.svg',65,-156,42),
        'RetryButton':('按键-重新开始-1.svg',120,-156,42),
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
            # Reuse the supplied down arrow as a right-facing resume symbol.
            raw=(source/'按键-下.svg').read_text(encoding='utf-8')
            pos=raw.index('>')+1
            raw=raw[:pos]+'<g transform="rotate(-90 100 100)">'+raw[pos:]
            raw=raw.replace('</svg>','</g></svg>')
            (directory/'resume.svg').write_text(raw,encoding='utf-8',newline='\n')
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
    font_path='C:/Windows/Fonts/msyhbd.ttc'
    def font(n): return ImageFont.truetype(font_path,n)
    def text(im,xy,word,n,fill,anchor='mm'):
        ImageDraw.Draw(im).text(xy,word,font=font(n),fill=fill,anchor=anchor)

    panel=Image.new('RGBA',(220,44))
    d=ImageDraw.Draw(panel)
    d.rounded_rectangle((0,0,219,43),radius=10,fill='#e5fcff')
    d.polygon([(0,0),(132,0),(118,44),(0,44)],fill='#20a8f4')
    text(panel,(62,21),'囤粮分',23,'white')
    png_sprite('ScorePanel',panel,-178,162)
    rank_costumes=[]
    for i,rank in enumerate(RANKS):
        im=Image.new('RGBA',(284,44));d=ImageDraw.Draw(im)
        d.rounded_rectangle((0,0,283,43),radius=8,fill='#e5fcff')
        d.polygon([(0,0),(102,0),(88,44),(0,44)],fill='#20a8f4')
        text(im,(47,21),'称号',23,'white');text(im,(188,21),rank,22,'#199add')
        directory=SPRITES/'RankPanel';directory.mkdir(parents=True,exist_ok=True)
        im.save(directory/f'{i}.png')
        rank_costumes.append(costume(str(i),f'{i}.png',284,44))
    sprite('RankPanel',rank_costumes,-14,162,.5)
    # Dynamic score digits are shared by the HUD and settlement, never baked results.
    digits=[];directory=SPRITES/'ScoreDigits';directory.mkdir(parents=True,exist_ok=True)
    for i in range(10):
        im=Image.new('RGBA',(56,72));text(im,(28,34),str(i),64,'#ff6428')
        im.save(directory/f'{i}.png');digits.append(costume(str(i),f'{i}.png',56,72))
    sprite('ScoreDigits',digits)
    results=[];directory=SPRITES/'ResultRank';directory.mkdir(parents=True,exist_ok=True)
    for i,rank in enumerate(RANKS):
        im=Image.new('RGBA',(280,56));text(im,(140,27),rank,32,'#ff6428')
        im.save(directory/f'{i}.png');results.append(costume(str(i),f'{i}.png',280,56))
    sprite('ResultRank',results,66,-60,.5)
    labels=Image.new('RGBA',(560,70))
    text(labels,(148,35),'囤粮分',21,'#512516');text(labels,(412,35),'达成成就',21,'#512516')
    png_sprite('ResultLabels',labels,0,-25)

    stage=json.loads((PROJECT/'assets/index.json').read_text(encoding='utf-8'))
    # HUD is now rendered as explicit UI sprites so page visibility is deterministic.
    stage['zorder']=[n for n in stage['zorder'] if isinstance(n,str)]
    for name in ['ScreenController','ScorePanel','RankPanel','ScoreDigits','HomeCover','StartButton',
                 'Dimmer','HelpPanel','ResultPanel','ResultLabels','ResultRank','ResultRetry','HomeButton','Achievement']:
        if name not in stage['zorder']:stage['zorder'].append(name)
    stage['builder_spriteOrder']=[json.loads((SPRITES/n/'index.json').read_text(encoding='utf-8'))['builder_id'] for n in stage['zorder']]
    dump(PROJECT/'assets/index.json',stage)
    dump(ROOT/'game/UI-ASSETS.json',dict(note='User originals preserved. Runtime PNGs resized proportionally; UI text generated with Microsoft YaHei Bold.',assets=manifest))
    print(f'Prepared {len(manifest)} supplied art resources and dynamic UI text sprites')


if __name__=='__main__':main()
