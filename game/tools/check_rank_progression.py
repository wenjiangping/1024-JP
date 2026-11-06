"""Exercise the production title, pickup and settlement functions with Go."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile
from check_obstacle_capacity import extract_function, PROJECT


def make_harness(source):
    globals_block = source[source.index('var ('):source.index('\nfunc syncMonitors')]
    functions = '\n\n'.join(extract_function(source, name) for name in
                            ['scoreStage', 'updateRank', 'updateDifficulty', 'collectItem', 'finishRun'])
    functions = re.sub(r'println (.*?)(?= }$|$)', r'trace(\1)', functions, flags=re.MULTILINE)
    functions = re.sub(r'^(\s*)(updateRank|updateDifficulty|syncMonitors)$',
                       r'\1\2()', functions, flags=re.MULTILINE)
    functions = re.sub(r'broadcast "[^"]+"', 'trace()', functions)
    return '''package main
import ("fmt"; "math")
var timer float64
func trace(args ...any) {}
func syncMonitors() {}
''' + globals_block + '\n' + functions + '''
var titles = []string{"蹦跶小新手", "树影穿梭客", "灌木飞毛腿", "林间寻路家", "风之探险家", "森林守护者", "林海追风侠", "秘境开拓者", "星辉守望者", "万木守护神", "森林传说王"}
func require(ok bool, message string) { if !ok { panic(message) } }
func initRun(score int) {
    Score, RankStage, DifficultyStage = score, -1, -1
    AchievementStage, AchievementTime = 0, 0
    Mushrooms, Diamonds = 0, 0
    Running, Paused, Screen = true, false, 2
    ItemTaken, ItemEnabled = [15]bool{}, [15]bool{}
    ItemEnabled[0], ItemEnabled[2] = true, true
    updateDifficulty()
}
func check(score int, title string) {
    require(Score == score && Rank == title, fmt.Sprintf("score/title: %d %q", Score, Rank))
    stage := expectedStage(score)
    if stage > 5 { stage = 5 }
    factor := 1.0
    for i := 0; i < stage; i++ { factor *= 1.3 }
    require(DifficultyStage == stage && math.Abs(Speed-58*factor)<1e-9 && math.Abs(ObstacleDensity-factor)<1e-9, "difficulty changed")
}
var thresholds = []int{0,30,60,90,120,150,180,210,260,310,360}
func expectedStage(score int) int {
    stage := 0
    for i, threshold := range thresholds { if score >= threshold { stage = i } }
    return stage
}
func main() {
    // Every score, including each boundary's neighbours and the final title cap.
    initRun(0)
    for score := 0; score <= 450; score++ {
        expected := expectedStage(score)
        previous := RankStage
        Score = score
        AchievementStage, AchievementTime, obstacleBudget = 0, 0.75, 0.625
        updateDifficulty()
        check(score, titles[expected])
        if expected != previous {
            require(AchievementStage == expected && AchievementTime == 0, "missing promotion badge")
        } else {
            require(AchievementStage == 0 && AchievementTime == 0.75, "duplicate promotion badge")
        }
        if previous >= 5 && !(previous < 7 && expected >= 7) { require(obstacleBudget == 0.625, "unexpected terrain quota reset") }
    }
    // Actual pickups cross every old/new boundary, including a +3 crystal jump.
    for stage := 1; stage <= 10; stage++ {
        for _, crystal := range []bool{false, true} {
            start, item, score := thresholds[stage]-1, 0, thresholds[stage]
            if crystal { start, item, score = thresholds[stage]-2, 2, thresholds[stage]+1 }
            initRun(start)
            collectItem(item)
            check(score, titles[stage])
            require(AchievementStage == stage, "pickup badge mismatch")
            collectItem(item)
            check(score, titles[stage])
            Paused = true
            ItemTaken[item] = false
            collectItem(item)
            check(score, titles[stage])
            Paused = false
            finishRun("test")
            require(FinalScore == score && FinalRank == titles[stage] && AchievementStage == 0, "settlement mismatch")
            collectItem(item)
            Score, Rank = 999, "changed live state"
            finishRun("again")
            require(FinalScore == score && FinalRank == titles[stage], "settlement not frozen")
        }
    }
    initRun(999)
    check(999, titles[10])
    initRun(0)
    check(0, titles[0])
    require(AchievementStage == 0, "initial run showed promotion")
    fmt.Println("PASS 451 score values; 20 mushroom/crystal boundary crossings; duplicate/paused/finished pickups; frozen settlement; capped speed and stage-7 quota reset; title cap/reset")
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()
    scratch = args.work_dir.resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(GOCACHE=str(scratch/'go-cache'), GOPATH=str(scratch/'go-path'),
               GOTMPDIR=str(scratch), GOTOOLCHAIN='local')
    with tempfile.TemporaryDirectory(prefix='rank-', dir=scratch) as temporary:
        program = Path(temporary)/'main.go'
        program.write_text(make_harness((PROJECT/'main.spx').read_text(encoding='utf-8')), encoding='utf-8')
        subprocess.run(['go', 'run', str(program)], env=env, check=True)


if __name__ == '__main__':
    main()
