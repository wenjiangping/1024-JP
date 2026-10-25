"""Build a temporary XBuilder screen/score audit package; production is untouched."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/'game/project'
OUTPUT=ROOT/'other/v019/Go-Lita-flow-playtest.xbp'


def main():
    text=(PROJECT/'main.spx').read_text(encoding='utf-8')
    text=text.replace('    Screen int', '    QAFlow bool\n    QARoutes int\n    QAObjects int\n    Screen int',1)
    text=text.replace('        count := int(obstacleBudget)',
                      '        count := int(obstacleBudget)\n        if QAFlow { QARoutes++; QAObjects += count }',1)
    # Keep the visible console small during the actual generator audit.
    text=text.replace('        println "DENSITY", DifficultyStage, ObstacleDensity, count, obstacleBudget','')
    text=text.replace('    if !opening { println "CHUNK", i, pattern, gap, width, top, OKind[a], OKind[a+1] }','')
    extra='''
func qaThreshold(stage int) {
    resetRun
    Score = stage*20-1
    Mushrooms = Score
    DifficultyStage = -1
    updateDifficulty
    println "QA_BELOW", Score, DifficultyStage, Rank
    ItemEnabled[0] = true
    ItemTaken[0] = false
    collectItem 0
    Paused = true
    broadcastAndWait "pauseChanged"
    println "QA_THRESHOLD", Score, DifficultyStage, Rank, AchievementStage, Speed, ObstacleDensity
}
func qaAudit() {
    resetRun
    Paused = true
    for i := 0; i <= 5; i++ {
        Score = i*20
        Mushrooms = Score
        DifficultyStage = -1
        updateDifficulty
        QAFlow = true
        QARoutes = 0
        QAObjects = 0
        Distance = 5000
        for j := 0; j < 300; j++ {
            previousGap = false
            challengeStreak = 0
            makeChunk 0, 0, false
        }
        QAFlow = false
        println "QA_DENSITY", i, QARoutes, QAObjects, ObstacleDensity, obstacleBudget
    }
    resetRun
    Score = 99
    Mushrooms = 99
    DifficultyStage = -1
    updateDifficulty
    ItemEnabled[2] = true
    ItemTaken[2] = false
    collectItem 2
    println "QA_CRYSTAL_CROSS", Score, DifficultyStage, Rank, AchievementStage
    AchievementStage = 0
    Score = 126
    Mushrooms = 120
    Diamonds = 2
    updateDifficulty
    println "QA_CAP", Score, DifficultyStage, Rank, AchievementStage
    finishRun "QA audit settlement"
}
onKey Key1, => { qaThreshold 1 }
onKey Key2, => { qaThreshold 2 }
onKey Key3, => { qaThreshold 3 }
onKey Key4, => { qaThreshold 4 }
onKey Key5, => { qaThreshold 5 }
onKey Key6, => { resetRun; Score = 126; Mushrooms = 120; Diamonds = 2; updateDifficulty; finishRun "QA settlement 126" }
onKey Key7, => { resetRun; finishRun "QA settlement zero" }
onKey Key8, => { resetRun; Score = 18; Mushrooms = 18; updateDifficulty; ItemEnabled[2] = true; ItemTaken[2] = false; collectItem 2; Paused = true; broadcast "pauseChanged"; println "QA_CRYSTAL_21", Score, DifficultyStage, Rank }
onKey Key9, => { qaAudit }
'''
    text=text.replace('onClick => {',extra+'\nonClick => {',1)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(OUTPUT,'w',ZIP_DEFLATED) as z:
        for p in sorted(PROJECT.rglob('*')):
            if p.is_file():
                relative=p.relative_to(PROJECT).as_posix()
                z.writestr(relative,text.encode('utf-8') if relative=='main.spx' else p.read_bytes())
    print(f'Playtest only: {OUTPUT}')


if __name__=='__main__':main()
