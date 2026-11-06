"""Create a disposable XBuilder stage/layout/obstacle fixture. Never publish it."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

PROJECT = Path(__file__).resolve().parents[1]/'project'
EXTRA = '''
func qaBalanceStage(score int) {
    resetRun
    QABalanceSafe = true
    Score = score-1
    Mushrooms = Score
    updateDifficulty
    ItemEnabled[0] = true
    ItemTaken[0] = false
    collectItem 0
    Paused = true
    println "QA_BALANCE_STAGE", Score, RankStage, Rank, DifficultyStage, Speed, nextObstacleCount()
}
func qaBalanceGround() {
    resetRun
    QABalanceSafe = true
    Paused = true
    for i := 0; i < len(OKind); i++ { OKind[i] = 0 }
    obstacle 0, 2, -30, -102
    obstacle 1, 3, 100, -102
    broadcastAndWait "render"
    println "QA_BALANCE_GROUND"
}
func qaBalanceSweep() {
    for score in [0,29,30,59,60,89,90,119,120,149,150,179,180,209,210,259,260,309,310,359,360,999] {
        resetRun
        QABalanceSafe = true
        Paused = true
        Score = score
        updateDifficulty
        Distance = 10000
        for n := 0; n < 200; n++ {
            makeChunk n%5, 800, false
            if n%50 == 49 { wait 0.001 }
        }
        println "QA_BALANCE_SWEEP", Score, RankStage, Speed
    }
    println "QA_BALANCE_ALL_PASS", 4400
}
func qaBalanceJump() {
    resetRun
    Score = 360
    Mushrooms = Score
    updateDifficulty
    AchievementStage = 0
    for i := 0; i < len(OKind); i++ { OKind[i] = 0 }
    for i := 0; i < len(ItemEnabled); i++ { ItemEnabled[i] = false }
    for i := 0; i < 5; i++ { PT[i] = -102; HasLedge[i] = false }
    obstacle 0, 3, -55, -102
    obstacle 1, 5, 11, -102
    obstacle 2, 4, 77, -102
    QABalanceSafe = false
    InputReady = true
    broadcast "requestJump"
    println "QA_BALANCE_JUMP", Score, Speed
}
onKey Key1, => { qaBalanceGround }
onKey Key2, => { qaBalanceStage 30 }
onKey Key3, => { qaBalanceStage 180 }
onKey Key4, => { qaBalanceStage 210 }
onKey Key5, => { qaBalanceStage 260 }
onKey Key6, => { qaBalanceStage 310 }
onKey Key7, => { qaBalanceStage 360 }
onKey Key8, => { qaBalanceSweep }
onKey Key9, => { qaBalanceJump }
onKey Key0, => { QABalanceSafe = true; Paused = false }
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = (PROJECT/'main.spx').read_text(encoding='utf-8')
    source = source.replace('var (','var (\n    QABalanceSafe bool',1)
    source = source.replace('func resetRun() {','func resetRun() {\n    QABalanceSafe = false',1)
    source = source.replace('onClick => {',EXTRA+'\nonClick => {',1)
    for event in ['physics','danger']:
        source = source.replace(f'            broadcastAndWait "{event}"',
                                f'            if !QABalanceSafe {{ broadcastAndWait "{event}" }}',1)
    # Keep the small console history useful during a large generation sweep.
    source = '\n'.join(line for line in source.splitlines()
                       if 'println "CHUNK"' not in line and 'println "DENSITY"' not in line)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(args.output,'w',ZIP_DEFLATED) as archive:
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file():
                relative=path.relative_to(PROJECT).as_posix()
                archive.writestr(relative,source.encode('utf-8') if relative=='main.spx' else path.read_bytes())
    print(f'QA ONLY: {args.output}')


if __name__=='__main__':
    main()
