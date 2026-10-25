"""Build temporary deterministic layouts; never modify the production project."""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "game/project"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "other/Go-Lita-playtest.xbp")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT) or output.is_relative_to(ROOT / "game"):
        parser.error("Write temporary fixtures under this workspace, outside game/")
    stage = (PROJECT / "main.spx").read_text(encoding="utf-8")
    assert "QAScenario" not in stage
    stage = stage.replace("    Score int", "    QAScenario int\n    Score int", 1)
    layout = '''    if QAScenario > 0 {
        for i := 0; i < 10; i++ { OKind[i] = 0 }
        for i := 0; i < 15; i++ { ItemEnabled[i] = false }
        for i := 0; i < 5; i++ {
            PX[i] = -150 + float64(i)*400
            PW[i] = 400
            PT[i] = -102
            HasLedge[i] = false
        }
        if QAScenario <= 5 { obstacle 0, QAScenario, -65, -102 }
        if QAScenario == 6 {
            PX[0] = -290
            PW[0] = 180
            PX[1] = 100
            PW[1] = 420
        }
        if QAScenario == 7 {
            PX[0] = -265
            PW[0] = 310
            PX[1] = 90
            PW[1] = 400
            PT[1] = -74
        }
        if QAScenario == 8 {
            HasLedge[0] = true
            LX[0] = -40
            LT[0] = -18
            LW[0] = 100
        }
        println "QA", QAScenario
    }
'''
    stage = stage.replace('    broadcastAndWait "setup"',
                          layout + '    broadcastAndWait "setup"', 1)
    keys = "\n".join(f"onKey Key{i}, => {{ QAScenario = {i}; WantsRetry = true }}"
                     for i in range(1, 9))
    stage = stage.replace("onStart => {", keys + "\nonStart => {", 1)
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(PROJECT.rglob("*")):
            if path.is_file():
                name = path.relative_to(PROJECT).as_posix()
                archive.writestr(name, stage.encode("utf-8") if name == "main.spx"
                                 else path.read_bytes())
    print(f"Playtest only: {output}")


if __name__ == "__main__":
    main()
