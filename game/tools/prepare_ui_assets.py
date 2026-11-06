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
NEW_RANKS = ['林海追风侠', '秘境开拓者', '星辉守望者', '万木守护神', '森林传说王']


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


def prepare_settlement_text():
    """Rebuild the original orange result text; the running HUD stays native."""
    def text(im, xy, word, size, fill):
        font = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', size)
        ImageDraw.Draw(im).text(xy, word, font=font, fill=fill, anchor='mm')

    digits = []
    directory = SPRITES/'ScoreDigits'
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(10):
        im = Image.new('RGBA', (56, 72))
        text(im, (28, 34), str(i), 64, '#ff6428')
        im.save(directory/f'{i}.png')
        digits.append(costume(str(i), f'{i}.png', 56, 72))
    sprite('ScoreDigits', digits)
    ranks = ['蹦跶小新手', '树影穿梭客', '灌木飞毛腿', '林间寻路家', '风之探险家', '森林守护者'] + NEW_RANKS
    results = []
    directory = SPRITES/'ResultRank'
    directory.mkdir(parents=True, exist_ok=True)
    for i, rank in enumerate(ranks):
        im = Image.new('RGBA', (280, 56))
        text(im, (140, 27), rank, 32, '#ff6428')
        im.save(directory/f'{i}.png')
        results.append(costume(rank, f'{i}.png', 280, 56))
    sprite('ResultRank', results, 66, -60, .5)
    im = Image.new('RGBA', (560, 70))
    text(im, (148, 35), '囤粮分', 21, '#512516')
    text(im, (412, 35), '达成成就', 21, '#512516')
    directory = SPRITES/'ResultLabels'
    directory.mkdir(parents=True, exist_ok=True)
    im.save(directory/'art.png')
    sprite('ResultLabels', [costume('默认', 'art.png', *im.size)], 0, -25, .5, list(im.size))


def prepare_highscore_titles(source):
    """Append only the five new badges/result titles, preserving existing art and IDs."""
    badge_dir = SPRITES/'Achievement'
    result_dir = SPRITES/'ResultRank'
    badge_config = json.loads((badge_dir/'index.json').read_text(encoding='utf-8'))
    result_config = json.loads((result_dir/'index.json').read_text(encoding='utf-8'))
    manifest_path = ROOT/'game/UI-ASSETS.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    font = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 32)

    def upsert(config, entry):
        for i, old in enumerate(config['costumes']):
            if old['name'] == entry['name']:
                entry['builder_id'] = old['builder_id']
                config['costumes'][i] = entry
                return
        config['costumes'].append(entry)

    for stage, rank in enumerate(NEW_RANKS, 6):
        original = source/f'{rank}.png'
        with Image.open(original) as im:
            original_size = im.size
            height = round(im.height*640/im.width)
            im.convert('RGBA').resize((640, height), Image.Resampling.LANCZOS).save(
                badge_dir/f'{stage}.png', optimize=True)
        upsert(badge_config, costume(str(stage), f'{stage}.png', 640, height))
        im = Image.new('RGBA', (280, 56))
        ImageDraw.Draw(im).text((140, 27), rank, font=font, fill='#ff6428', anchor='mm')
        im.save(result_dir/f'{stage}.png')
        upsert(result_config, costume(rank, f'{stage}.png', 280, 56))
        entry = dict(source=original.name, sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                     originalSize=original_size, runtime=f'assets/sprites/Achievement/{stage}.png',
                     runtimeSize=[640, height])
        manifest['assets'] = [a for a in manifest['assets'] if a['runtime'] != entry['runtime']]
        manifest['assets'].append(entry)
    dump(badge_dir/'index.json', badge_config)
    dump(result_dir/'index.json', result_config)
    dump(manifest_path, manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'素材')
    parser.add_argument('--highscore-only', action='store_true',
                        help='Append the five 120+ titles without rebuilding existing resources')
    args = parser.parse_args()
    source = args.source.resolve()
    if args.highscore_only:
        prepare_highscore_titles(source)
        print('Prepared five high-score badges and original-style settlement titles')
        return
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
    prepare_settlement_text()
    cover_config = SPRITES/'HomeCover/index.json'
    cover = json.loads(cover_config.read_text(encoding='utf-8'))
    cover['visible'] = True
    dump(cover_config, cover)
    with Image.open(SPRITES/'HomeCover/art.png') as im:
        im.convert('RGB').save(PROJECT/'builder-thumbnail.jpeg', quality=92, optimize=True)

    stage=json.loads((PROJECT/'assets/index.json').read_text(encoding='utf-8'))
    for name in ['ScreenController','HomeCover','StartButton','Dimmer','HelpPanel',
                 'ResultPanel','ResultLabels','ScoreDigits','ResultRank','ResultRetry','HomeButton','Achievement']:
        if name not in stage['zorder']:stage['zorder'].append(name)
    stage['builder_spriteOrder']=[json.loads((SPRITES/n/'index.json').read_text(encoding='utf-8'))['builder_id'] for n in stage['zorder'] if isinstance(n,str)]
    dump(PROJECT/'assets/index.json',stage)
    dump(ROOT/'game/UI-ASSETS.json',dict(note='User originals preserved. Runtime HUD uses native XBuilder Monitors; settlement uses original orange text assets bound to frozen score/title.',assets=manifest))
    prepare_highscore_titles(source)
    print(f'Prepared {len(manifest)} supplied art resources and native Monitor bindings preserved')


if __name__=='__main__':main()
