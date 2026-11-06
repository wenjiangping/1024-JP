"""Create a disposable XBuilder title/illustration fixture. Never publish it."""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

PROJECT = Path(__file__).resolve().parents[1]/'project'
EXTRA = '''
func qaRankShow(target int, crystal bool) {
    resetRun
    Score = target - 1
    if crystal { Score = target - 2 }
    Mushrooms = Score
    updateDifficulty
    AchievementStage = 0
    ItemEnabled[0] = true
    ItemEnabled[2] = true
    ItemTaken[0] = false
    ItemTaken[2] = false
    if crystal { collectItem 2 } else { collectItem 0 }
    Paused = true
    println "QA_RANK_SHOW", Score, Rank, RankStage, AchievementStage, Speed, ObstacleDensity
}
func qaRankFinish() {
    finishRun "QA title settlement"
    Score = 999
    Rank = "测试实时值"
    finishRun "QA duplicate finish"
    collectItem 1
    println "QA_RANK_FROZEN", FinalScore, FinalRank
}
onKey Key1, => { qaRankShow 120, false }
onKey Key2, => { qaRankShow 140, false }
onKey Key3, => { qaRankShow 160, false }
onKey Key4, => { qaRankShow 180, false }
onKey Key5, => { qaRankShow 200, false }
onKey Key6, => { qaRankShow 120, true }
onKey Key7, => { qaRankFinish }
onKey Key8, => { Paused = false }
onKey Key9, => { qaRankShow 100, false }
onKey Key0, => { resetRun; Paused = true; println "QA_RANK_RESET", Score, Rank, AchievementStage }
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = (PROJECT/'main.spx').read_text(encoding='utf-8')
    source = source.replace('onClick => {', EXTRA+'\nonClick => {', 1)
    # Keep normal collection/rendering/UI, but bypass hazards for visual inspection.
    source = source.replace('            broadcastAndWait "physics"', '', 1)
    source = source.replace('            broadcastAndWait "danger"', '', 1)
    source = '// QARank: DISPOSABLE FIXTURE. DO NOT PUBLISH.\n'+source
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file():
                relative = path.relative_to(PROJECT).as_posix()
                archive.writestr(relative, source.encode('utf-8') if relative == 'main.spx' else path.read_bytes())
    print(f'QA ONLY: {args.output}')


if __name__ == '__main__':
    main()
