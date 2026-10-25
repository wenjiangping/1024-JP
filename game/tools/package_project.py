"""Validate the exported project and package it with Python's standard library."""
import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

GAME = Path(__file__).resolve().parents[1]
PROJECT = GAME / "project"
PACKAGE = GAME / "Go-Lita-runner-v0.4.xbp"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_project():
    stage = read_json(PROJECT / "assets/index.json")
    assert stage["run"] == {"width": 480, "height": 360}, "Expected 4:3 stage"
    assert stage["physics"] is True, "Global physics must be enabled"
    assert all(not isinstance(z, dict) or z.get("val") != "Hint"
               for z in stage["zorder"]), "Removed Hint monitor reappeared"
    assert "QAScenario" not in (PROJECT / "main.spx").read_text(encoding="utf-8"), \
        "Temporary playtest fixture must not ship"
    assert "QAFlow" not in (PROJECT / "main.spx").read_text(encoding="utf-8"), \
        "Temporary screen audit must not ship"
    ids, names = [], []
    expected_controls = {
        "MoveLeft": (-205, -156, 0.21),
        "MoveRight": (-150, -156, 0.21),
        "JumpButton": (212, -156, 0.21),
        "PauseButton": (65, -156, 0.21),
        "RetryButton": (120, -156, 0.21),
    }
    expected_physics = {
        "Lita": "kinematic",
        "草地": "static", "草地2": "static", "草地3": "static",
        "草地4": "static", "草地5": "static", "草台": "static",
        "石头": "static", "石头1": "static", "树桩": "static",
        "火焰": "static", "炸弹": "static",
    }

    def require_resource(directory, relative):
        target = (directory / relative).resolve()
        assert target.is_relative_to(PROJECT.resolve()), f"Path escapes project: {relative}"
        assert target.is_file(), f"Missing resource: {target}"

    for backdrop in stage["backdrops"]:
        require_resource(PROJECT / "assets", backdrop["path"])
    for directory in sorted((PROJECT / "assets/sprites").iterdir()):
        if not directory.is_dir():
            continue
        config = read_json(directory / "index.json")
        if directory.name in expected_physics:
            assert config["physicsMode"] == expected_physics[directory.name], \
                f"Physics mode changed: {directory.name}"
        if directory.name in expected_controls:
            expected = expected_controls[directory.name]
            actual = (config["x"], config["y"], config["size"])
            assert actual == expected, f"Control geometry changed: {directory.name}"
            assert config["collisionShapeParams"] == [200.0, 200.0], \
                f"Control collision bounds differ from the supplied art: {directory.name}"
        require_resource(PROJECT, directory.name + ".spx")
        ids.append(config["builder_id"])
        names.append(directory.name)
        costumes = {c["name"] for c in config["costumes"]}
        for costume in config["costumes"]:
            require_resource(directory, costume["path"])
        for animation in config.get("fAnimations", {}).values():
            assert animation["frameFrom"] in costumes
            assert animation["frameTo"] in costumes
    sound_ids = []
    for directory in (PROJECT / "assets/sounds").iterdir():
        if directory.is_dir():
            config = read_json(directory / "index.json")
            require_resource(directory, config["path"])
            sound_ids.append(config["builder_id"])
    assert len(sound_ids) == len(set(sound_ids)), "Duplicate sound IDs"
    assert set(sound_ids) == set(stage["builder_soundOrder"]), "Sound order differs from resources"
    assert len(ids) == len(set(ids)), "Duplicate sprite IDs"
    assert set(ids) == set(stage["builder_spriteOrder"]), "Sprite order differs from resources"
    layers = [entry for entry in stage["zorder"] if isinstance(entry, str)]
    assert set(layers) == set(names), "Stage layers differ from sprites"
    require_resource(PROJECT, "main.spx")
    files = {p.relative_to(PROJECT).as_posix(): p.read_bytes()
             for p in PROJECT.rglob("*") if p.is_file()}
    return files, len(ids)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Check assets and exact archive/source consistency without writing")
    args = parser.parse_args()
    files, sprite_count = validate_project()
    if args.check:
        with ZipFile(PACKAGE) as archive:
            entries = [info.filename for info in archive.infolist() if not info.is_dir()]
            assert len(entries) == len(set(entries)), "Duplicate archive entries"
            assert set(entries) == set(files), "Archive file list differs from project"
            assert archive.testzip() is None, "Corrupt archive member"
            for name, content in files.items():
                assert archive.read(name) == content, f"Archive content differs: {name}"
    else:
        with ZipFile(PACKAGE, "w", compression=ZIP_DEFLATED) as archive:
            for name, content in sorted(files.items()):
                info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, content)
    print(f"OK: {sprite_count} sprites, {len(files)} files; {PACKAGE.name}")


if __name__ == "__main__":
    main()
