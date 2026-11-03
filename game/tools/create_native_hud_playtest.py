"""Create a disposable native-HUD regression package. Never publish this fixture."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

PROJECT = Path(__file__).resolve().parents[1] / "project"

EXTRA = '''
func qaThreshold(stage int) {
    resetRun
    Score = stage*20-1
    Mushrooms = Score
    updateDifficulty
    ItemEnabled[0] = true
    ItemTaken[0] = false
    collectItem 0
    collectItem 0
    Paused = true
    println "QA_THRESHOLD", Score, Mushrooms, Diamonds, Rank
}
onKey Key1, => { qaThreshold 1 }
onKey Key2, => { qaThreshold 2 }
onKey Key3, => { qaThreshold 3 }
onKey Key4, => { qaThreshold 4 }
onKey Key5, => { qaThreshold 5 }
onKey Key6, => {
    resetRun
    Score = 126
    Mushrooms = 120
    Diamonds = 2
    updateDifficulty
    finishRun "QA three digit settlement"
    collectItem 0
    finishRun "QA duplicate finish"
    Score = 999
    println "QA_FROZEN", FinalScore, Score, Rank
}
onKey Key7, => { resetRun; finishRun "QA zero settlement"; println "QA_ZERO", FinalScore, Rank }
onKey Key8, => {
    resetRun
    Score = 18
    Mushrooms = 18
    updateDifficulty
    ItemEnabled[2] = true
    ItemTaken[2] = false
    collectItem 2
    collectItem 2
    Paused = true
    collectItem 0
    println "QA_CRYSTAL_PAUSED", Score, Mushrooms, Diamonds, Rank
}
onKey Key9, => { finishRun "QA crystal settlement"; println "QA_CRYSTAL_FINAL", FinalScore, Rank }
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = (PROJECT / "main.spx").read_text(encoding="utf-8")
    source = source.replace("onClick => {", EXTRA + "\nonClick => {", 1)
    source = "// QAHUD: DISPOSABLE FIXTURE. DO NOT PUBLISH.\n" + source
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(PROJECT.rglob("*")):
            if path.is_file():
                relative = path.relative_to(PROJECT).as_posix()
                archive.writestr(relative, source.encode("utf-8") if relative == "main.spx" else path.read_bytes())
    print(f"QA ONLY: {args.output}")


if __name__ == "__main__":
    main()
