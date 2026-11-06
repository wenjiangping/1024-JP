"""Exercise production terrain generation with Go; keep generated files outside the repo."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile

PROJECT = Path(__file__).resolve().parents[1] / "project"


def extract_function(source, name):
    start = source.index(f"func {name}(")
    end = source.find("\nfunc ", start + 1)
    return source[start:end if end != -1 else len(source)]


def make_harness(source):
    names = ["scoreStage", "updateRank", "updateDifficulty", "obstacle", "makeChunk"]
    has_quota = "func nextObstacleCount(" in source
    if has_quota:
        names.insert(3, "nextObstacleCount")
    functions = "\n\n".join(extract_function(source, name) for name in names)
    # Convert only XGo's command-style calls; keep production expressions,
    # branches, loop limits and all array writes intact.
    functions = re.sub(r'println (.*?)(?= }$|$)', r'trace(\1)', functions,
                       flags=re.MULTILINE)
    functions = re.sub(r'^(\s*)updateRank$', r'\1updateRank()', functions, flags=re.MULTILINE)
    functions = functions.replace("            obstacle a+j, kind, x, top",
                                  "            obstacle(a+j, kind, x, top)")
    functions = functions.replace("    OKind[k] = kind", """    if k < activeChunk*3 || k >= activeChunk*3+3 {
        panic(fmt.Sprintf("slot ownership violated: score=%d chunk=%d index=%d", Score, activeChunk, k))
    }
    generatedX = append(generatedX, x)
    generatedKind = append(generatedKind, kind)
    OKind[k] = kind""", 1)
    globals_block = source[source.index("var ("):source.index("\nfunc syncMonitors")]
    prefix = '''package main
import (
    "fmt"
    "math"
    mathrand "math/rand"
)
var rng *mathrand.Rand
var activeChunk int
var generatedX []float64
var generatedKind []int
var forcedPattern = -1
func rand(min, max float64) float64 { if forcedPattern >= 0 && min == 0 && max == 999 { return float64(forcedPattern) }; return min + rng.Float64()*(max-min) }
func trace(args ...any) {}
'''
    quota_checks = '''
    for stage := 0; stage <= 10; stage++ {
        Score, RankStage, DifficultyStage = thresholds[stage], -1, -1
        updateDifficulty()
        density := math.Min(ObstacleDensity, 2)
        if stage >= 7 { density = 3 }
        total := 0
        for n := 1; n <= 10000; n++ {
            count := nextObstacleCount()
            limit := 2
            if stage >= 7 { limit = 3 }
            if count < 0 || count > limit { panic("quota exceeds route capacity") }
            total += count
            expected := density*float64(n)
            if math.Abs(float64(total)-expected) > 1.000001 { panic("fractional quota drift") }
            if obstacleBudget < 0 || obstacleBudget >= 1 { panic("quota backlog") }
        }
    }
    fmt.Println("PASS 110000 quota allocations: stages 0-6 <= 2, stages 7-10 = 3, no backlog")
'''
    # Reference math in both variants so --source can check the pre-fix code.
    suffix = '''
var thresholds = []int{0,30,60,90,120,150,180,210,260,310,360}
func main() {
    _ = math.Abs
QUOTA_CHECKS
    scores := []int{0,29,30,59,60,89,90,119,120,149,150,179,180,209,210,259,260,309,310,359,360,999}
    for _, score := range scores {
        total := 0
        for seed := int64(1); seed <= 20; seed++ {
            rng = mathrand.New(mathrand.NewSource(seed))
            Score, RankStage, DifficultyStage = score, -1, -1
            updateDifficulty()
            if obstacleBudget != 0 { panic("stage transition retained quota") }
            expectedSpeed := 58.0
            for j := 0; j < DifficultyStage; j++ { expectedSpeed *= 1.3 }
            if math.Abs(Speed-expectedSpeed) > 0.000001 { panic("speed changed") }
            Distance, previousPattern, previousGap, previousTop, challengeStreak = 10000, -1, false, -102, 0
            PX, PW, PT = [5]float64{}, [5]float64{}, [5]float64{}
            LX, LT, LW = [5]float64{}, [5]float64{}, [5]float64{}
            HasLedge = [5]bool{}
            OX, OY, OW, OH = [15]float64{}, [15]float64{}, [15]float64{}, [15]float64{}
            OKind = [15]int{}
            for n := 0; n < 1000; n++ {
                activeChunk = (n+3)%5
                generatedX, generatedKind = nil, nil
                wasGap := previousGap
                makeChunk(activeChunk, 800, false)
                limit := 2
                if RankStage >= 7 { limit = 3 }
                if len(generatedX) > limit { panic("too many obstacles") }
                if len(generatedX) == 3 {
                    if generatedX[0]-22 < 800+55 || generatedX[2]+22 > 800+PW[activeChunk]-55 { panic("route margin lost") }
                    for j := 1; j < 3; j++ { if generatedX[j]-generatedX[j-1] < 65.9 { panic("cluster spacing lost") } }
                    if generatedKind[0] > 3 { panic("missing solid takeoff") }
                }
                if len(generatedX) == 2 && generatedX[1]-generatedX[0] < 130 { panic("jump corridor lost") }
                if (wasGap || previousGap) && len(generatedX) != 0 { panic("gap corridor obstructed") }
                Distance += PW[activeChunk]
                total++
            }
            // Opening routes must remain clear even at the highest stage.
            for activeChunk = 0; activeChunk < 5; activeChunk++ {
                generatedX, generatedKind = nil, nil
                makeChunk(activeChunk, 800, true)
                if len(generatedX) != 0 { panic("opening route obstructed") }
            }
        }
        fmt.Printf("PASS score=%d regenerated=%d: slot ownership, bounds, spacing, safe routes\\n", score, total)
    }
    fmt.Println("PASS 440000 generated routes; no array overflow or cross-chunk obstacle write")
    for stage, score := range thresholds {
        bombs, fires := 0, 0
        for pattern := 0; pattern < 10; pattern++ {
            rng = mathrand.New(mathrand.NewSource(1))
            Score, RankStage, DifficultyStage = score, -1, -1
            updateDifficulty()
            forcedPattern = pattern
            Distance, previousPattern, previousGap, previousTop, challengeStreak = 10000, -1, false, -102, 0
            activeChunk = 0
            generatedX, generatedKind = nil, nil
            makeChunk(0, 800, false)
            for _, kind := range generatedKind { if kind == 5 { bombs++ }; if kind == 4 { fires++ } }
        }
        expectedBombs := 2
        expectedFires := 2
        if stage >= 7 { expectedBombs, expectedFires = 4, 4 }
        if bombs != expectedBombs || fires != expectedFires { panic(fmt.Sprintf("hazard distribution stage=%d bombs=%d fires=%d", stage, bombs, fires)) }
        fmt.Printf("PASS stage=%d all 10 patterns: bombs=%d (2x previous bomb opportunity), fire=%d\\n", stage, bombs, fires)
    }
    forcedPattern = -1
}
'''.replace("QUOTA_CHECKS", quota_checks if has_quota else "")
    return prefix + globals_block + "\n" + functions + suffix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True,
                        help="Explicit scratch directory for Go source, cache and temporary files")
    parser.add_argument("--source", type=Path, default=PROJECT / "main.spx",
                        help="Override production script for a pre-fix negative control")
    args = parser.parse_args()
    scratch = args.work_dir.resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(GOCACHE=str(scratch / "go-cache"), GOPATH=str(scratch / "go-path"),
               GOTMPDIR=str(scratch), GOTOOLCHAIN="local")
    with tempfile.TemporaryDirectory(prefix="capacity-", dir=scratch) as temporary:
        program = Path(temporary) / "main.go"
        program.write_text(make_harness(args.source.read_text(encoding="utf-8")),
                           encoding="utf-8")
        subprocess.run(["go", "run", str(program)], env=env, check=True)


if __name__ == "__main__":
    main()
