"""Create a disposable high-score runtime fixture. Never publish this package."""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

PROJECT = Path(__file__).resolve().parents[1] / "project"

EXTRA = '''
func qaCapacitySweep() {
    if QACapacityBusy { return }
    QACapacityBusy = true
    for score in [0, 19, 20, 39, 40, 59, 60, 70, 79, 80, 99, 100, 126, 999] {
        resetRun
        Paused = true
        Score = score
        Mushrooms = score
        updateDifficulty
        Distance = 10000
        for n := 0; n < 200; n++ {
            makeChunk n%5, 800, false
            if n%50 == 49 { wait 0.001 }
        }
        println "QA_CAPACITY_PASS", score, ObstacleDensity, obstacleBudget
    }
    println "QA_CAPACITY_ALL_PASS", 2800
    QACapacityBusy = false
}
func qaCapacityLive(score int) {
    resetRun
    Score = score
    Mushrooms = score
    updateDifficulty
    QACapacityAutoplay = true
    println "QA_CAPACITY_LIVE", Score, Speed
}
onKey Key1, => { qaCapacitySweep }
onKey Key2, => { if !QACapacityBusy { qaCapacityLive 70 } }
onKey Key3, => { if !QACapacityBusy { qaCapacityLive 80 } }
onKey Key4, => { if !QACapacityBusy { qaCapacityLive 100 } }
onKey Key5, => { if !QACapacityBusy { qaCapacityLive 126 } }
onKey Key6, => { if !QACapacityBusy { finishRun "QA high-score settlement" } }
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = (PROJECT / "main.spx").read_text(encoding="utf-8")
    # XGo classfiles allow one top-level variable declaration block.
    source = source.replace("var (", "var (\n    QACapacityBusy bool\n    QACapacityAutoplay bool", 1)
    source = source.replace("onClick => {", EXTRA + "\nonClick => {", 1)
    source = source.replace('func resetRun() {',
                            'func resetRun() {\n    QACapacityAutoplay = false', 1)
    # Keep production world generation, pickups, rendering, HUD and UI running.
    # Only this fixture bypasses player hazards so a long run is reproducible.
    source = source.replace('            broadcastAndWait "physics"',
                            '            if !QACapacityAutoplay { broadcastAndWait "physics" }', 1)
    source = source.replace('            broadcastAndWait "danger"',
                            '            if !QACapacityAutoplay { broadcastAndWait "danger" }', 1)
    source = "// QACapacity: DISPOSABLE FIXTURE. DO NOT PUBLISH.\n" + source
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(PROJECT.rglob("*")):
            if path.is_file():
                relative = path.relative_to(PROJECT).as_posix()
                archive.writestr(relative, source.encode("utf-8")
                                 if relative == "main.spx" else path.read_bytes())
    print(f"QA ONLY: {args.output}")


if __name__ == "__main__":
    main()
