# Go Lita v0.7 native HUD and HomeCover plan

## Goal

Repair the score handoff between the running screen and the settlement screen, while using XBuilder's built-in Monitor widgets for the score and title controls. Replace the project listing thumbnail with the existing `HomeCover` artwork so the project card and editor cover show the same home screen.

## Implementation plan

1. Add native XBuilder Monitor widgets bound to the stage globals `Score`, `FinalScore`, and `Rank`.
   - `ScoreMonitor` and `RankMonitor` are visible only on `Screen == 2`.
   - `SettlementScoreMonitor` and `SettlementRankMonitor` are visible only on `Screen == 3`.
   - Keep `FinalScore` assigned in `finishRun` before the screen changes, so settlement reads the exact score from the ending frame.
2. Remove the hand-drawn score/title sprite controls and their layer-management code. The monitor visibility is synchronized from stage code with `getWidget(Monitor, ...)` and the standard `show`/`hide` APIs.
3. Keep collection and difficulty updates in one path. `Score` remains the only live score source; `FinalScore` is the frozen settlement snapshot, and `Rank` is updated from the same difficulty stage table.
4. Set `game/project/builder-thumbnail.jpeg` from `HomeCover` artwork and keep the `HomeCover` sprite as the runtime home screen cover.
5. Extend the package validator to require the native monitors, the frozen settlement binding, the HomeCover thumbnail, and an archive/source byte-for-byte match.

## Acceptance criteria

- During `Screen == 2`, the XBuilder system widgets show `囤粮分: <Score>` and `称号: <Rank>`.
- On `Screen == 3`, the system widgets show `囤粮分: <FinalScore>` and the final title; the values remain stable while the settlement page is open.
- Finishing on the same frame as a pickup never increments the settlement score, because danger is resolved before pickup and `FinalScore` is captured once.
- The project card thumbnail is the `HomeCover` artwork, and the exported package contains the same thumbnail and source assets.
- `python game/tools/package_project.py --check` and `git diff --check` pass before importing the package into the original XBuilder project.

## XBuilder rollout

After this plan is reviewed in the pull request, import the generated XBP into the existing `En / IdeaDash` project, run the home → help → play → settlement flow, verify the native monitors and cover, then publish the updated project once.
