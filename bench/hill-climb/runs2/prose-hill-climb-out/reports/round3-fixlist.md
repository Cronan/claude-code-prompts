# Round 3 fix list

Round 3 was the final critic call (cap: 3). Per the skill, findings from the final call are applied only where a verifier covers the edit. The only verifier is mechanical (line count, section order, numbering) and covers none of the confirmed edits below, so nothing was applied. All items go to the owner's list.

Confirmed by verifier, not applied:

| # | Section | Line | Defect | Suggested fix |
|---|---|---|---|---|
| 1 | Rotation | step 6, sed replacement `$NEW_KEY` | A secret containing `\|`, `&` or `\` breaks or corrupts the substitution; YAML-significant characters parse to a different value and step 7 does not catch it (misleading, conditional on the vendor's secret character set) | State the vendor's secret alphabet, or write the line with a quoting tool (Python YAML dump) |
| 2 | Rotation | step 9, `--since "-5min"` | Window can include shutdown errors from step 5 (false failure) and runs before auth errors appear (false pass) (misleading) | `--since` the step 8 time, run 60 s after start |
| 3 | Rollback | step 13, "repeat the step 9 checks" | The -5min window still holds the failed new-key run's errors, so the re-check fails even when the restore worked (misleading) | `--since` the step 13 restart time |

Confirmed at minor: change ticket system and id source not named (steps 2-3).

Not confirmed (disputed, carried to owner): step 11 old-key identification assumes naming pattern; PyYAML not confirmed installed.
