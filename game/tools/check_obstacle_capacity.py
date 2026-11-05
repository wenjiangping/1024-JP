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
    names = ["updateRank", "updateDifficulty", "obstacle", "makeChunk"]
    has_quota = "func nextObstacleCount(" in source
    if has_quota:
        names.insert(3, "nextObstacleCount")
    functions = "\n\n".join(extract_function(source, name) for name in names)
    # Convert only XGo's command-style calls; keep production expressions,
    # branches, loop limits and all array writes intact.
    functions = re.sub(r'println (.*?)(?= }$|$)', r'trace(\1)', functions,
                       flags=re.MULTILINE)
    functions = functions.replace("        updateRank\n", "        updateRank()\n")
    functions = functions.replace("            obstacle a+j, kind, x, top",
                                  "            obstacle(a+j, kind, x, top)")
    functions = functions.replace("    OKind[k] = kind", """    if k < activeChunk*2 || k >= activeChunk*2+2 {
        panic(fmt.Sprintf("slot ownership violated: score=%d chunk=%d index=%d", Score, activeChunk, k))
    }
    generatedX = append(generatedX, x)
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
func rand(min, max float64) float64 { return min + rng.Float64()*(max-min) }
func trace(args ...any) {}
'''
    quota_checks = '''
    for _, density := range []float64{1, 1.3, 1.69, 2.197, 2.8561, 3.71293} {
        ObstacleDensity, obstacleBudget = density, 0
        total := 0
        for n := 1; n <= 10000; n++ {
            count := nextObstacleCount()
            if count < 0 || count > 2 { panic("quota exceeds route capacity") }
            total += count
            expected := math.Min(density, 2)*float64(n)
            if math.Abs(float64(total)-expected) > 1.000001 { panic("fractional quota drift") }
            if obstacleBudget < 0 || obstacleBudget >= 1 { panic("quota backlog") }
        }
    }
    fmt.Println("PASS fractional quota: 60000 allocations, count <= 2, no backlog")
'''
    # Reference math in both variants so --source can check the pre-fix code.
    suffix = '''
func main() {
    _ = math.Abs
QUOTA_CHECKS
    scores := []int{0,19,20,39,40,59,60,70,79,80,99,100,126,999}
    for _, score := range scores {
        total := 0
        for seed := int64(1); seed <= 20; seed++ {
            rng = mathrand.New(mathrand.NewSource(seed))
            Score, DifficultyStage = score, -1
            updateDifficulty()
            if obstacleBudget != 0 { panic("stage transition retained quota") }
            expectedSpeed := 58.0
            for j := 0; j < DifficultyStage; j++ { expectedSpeed *= 1.3 }
            if math.Abs(Speed-expectedSpeed) > 0.000001 { panic("speed changed") }
            Distance, previousPattern, previousGap, previousTop, challengeStreak = 10000, -1, false, -102, 0
            PX, PW, PT = [5]float64{}, [5]float64{}, [5]float64{}
            LX, LT, LW = [5]float64{}, [5]float64{}, [5]float64{}
            HasLedge = [5]bool{}
            OX, OY, OW, OH = [10]float64{}, [10]float64{}, [10]float64{}, [10]float64{}
            OKind = [10]int{}
            for n := 0; n < 1000; n++ {
                activeChunk = (n+3)%5
                generatedX = nil
                wasGap := previousGap
                makeChunk(activeChunk, 800, false)
                if len(generatedX) > 2 { panic("too many obstacles") }
                if len(generatedX) == 2 && generatedX[1]-generatedX[0] < 130 { panic("jump corridor lost") }
                if (wasGap || previousGap) && len(generatedX) != 0 { panic("gap corridor obstructed") }
                Distance += PW[activeChunk]
                total++
            }
            // Opening routes must remain clear even at the highest stage.
            for activeChunk = 0; activeChunk < 5; activeChunk++ {
                generatedX = nil
                makeChunk(activeChunk, 800, true)
                if len(generatedX) != 0 { panic("opening route obstructed") }
            }
        }
        fmt.Printf("PASS score=%d regenerated=%d: slot ownership, bounds, spacing, safe routes\\n", score, total)
    }
    fmt.Println("PASS 280000 generated routes; no array overflow or cross-chunk obstacle write")
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
