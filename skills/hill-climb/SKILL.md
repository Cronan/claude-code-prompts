---
name: "hill-climb"
description: "Improve a finished draft of anything (code, a document, an HTML artifact, a proposal, a plan, a prompt, a skill) by rounds of cold review, verified findings and small fixes until a pre-agreed stopping rule fires. Use for hill-climb, improve until good, review and fix, harden this, make it survive review."
---

# Hill climb

A hill climb takes a complete draft and raises its quality in rounds. A round is one cold critic call, one verification of its findings, one fix batch and a new saved version. The climb stops when a rule agreed before round one fires, not when the author is tired or the reviewer runs out of things to say.

Three rules shape everything below. Throughout, the owner is the person who invoked the climb; the author is whoever produced the draft; a mechanical verifier is a Step 0 check; the checker is the Step 1b agent.

1. Self-review misses most of what matters. Models fail to correct their own errors about two thirds of the time while fixing the identical error when it arrives from someone else; an author rereading its own work finds wording, a fresh reader with the file and nothing else finds the shell command that deletes `.git`. The critic must not have seen the work being produced, and findings must reach the author as an external report.
2. Fixes introduce defects, and the defect count does not fall monotonically. A round helps only when its correction rate exceeds its corruption rate times baseline quality over the remainder, so a round on an already-clean artefact is more likely to harm than help, and the context handed to a fixer is itself a source of corruption. So: fix only confirmed, in-scope findings, hand the fixer findings rather than prose, and deliver a version a critic has read. Findings from the final critic call (the call that reaches the cap, or the last call before a stopping rule fires) are applied only where a mechanical verifier covers the edit; everything else from that call is listed for the owner.
3. A critic reports blocking defects in a correct artefact. Every cold reader handed a sound library in testing found blocking items in it, and a verifier asked "could this be true" confirmed them all. The gate that holds is scope: a finding enters a fix batch only if it breaks the Step 0 objective, the frozen behaviour, or a contract the artefact states about itself. Hardening the artefact beyond its stated requirements is the owner's decision, not the climb's.

## Step 0: set the contract, one per artefact

Two artefacts means two climbs with two contracts, two tables and two caps. Write the contract in the conversation in at most eight lines before the first critic runs, so the user sees it and the author cannot move the goalposts later.

- Objective, as a test a stranger could run. Executable document: "an engineer with no other context can execute this without asking the author a question". Code: "the verifier passes and a reviewer reading the change cold, knowing the stated intent, finds no correctness defect". Page: "every figure matches the source data (or, with no source, the page is internally consistent and dated) and it reads correctly at 390 px and 1440 px". Quality document (essay, proposal): "a reviewer applying the brief's own criteria finds no claim they would reject and no requirement unmet". If the user gave no objective, propose one in a sentence and proceed.
- Frozen behaviour. What a fix may not change. Document: reading order, length ceiling, house style, any structure the brief or CFP mandates. Code: the change's intent as the user states it (if unstated, infer it from the change, state it, proceed), every test on the base, and any interface the change does not touch; tests the change itself adds are in scope and may be wrong. For uncommitted work the base is HEAD and the artefact is the working tree; say so. Page: the data source and the published URL. A fix that moves frozen behaviour is a regression however good it looks; fix the fix, not the check.
- Verifiers. Mechanical checks needing no judgement: the test command, a linter, `json.loads` over every fenced block, a grep for banned words and em-dashes, a word count, a cross-reference check between sections. Record the exact command and environment now. A screenshot is a critic input, not a verifier, because reading it takes judgement; a page usually has no verifier. If nothing mechanical exists, say so and treat the climb as judgement-only. A verifier added mid-climb counts from the round it joins.
- Scope test. One line the checker can apply to any finding: "breaks requirement N of the objective, moves frozen behaviour, or contradicts what the artefact says about itself; otherwise out of scope". Write the objective as numbered requirements so the test has something to point at. For an executable document add to frozen behaviour: no fix may assert a fact about the environment (a log line, a URL, a validity period, a threshold) that the original does not state; it uses a named placeholder instead.
- Stopping rules and cap. State which of rules 1 to 3 in Step 4 apply; the first to fire stops the climb, and rule 4 (the cap) is always the backstop. Cap: three critic calls for prose, five for code or for documents containing shell commands. These are judgement figures, not measured ones; the literature gives a break-even condition, not a round count. If round 1 ends with zero confirmed in-scope blocking findings (after Step 1b, not the critic's raw tally, which is never zero), the cap drops to two critic calls whatever the artefact type, because the artefact is in the regime where further rounds corrupt more than they correct. If the user named a number of rounds, that is the cap. Two critics run in parallel count as two calls against the cap and as one read for rule 3. Checker calls do not count against the cap.

## Step 1: run a cold critic

A cold critic is a fresh context, reached by the first rung of this ladder that works; probe each, do not assume.

1. The Agent tool (ToolSearch if not loaded).
2. A fresh CLI process, if one is on PATH: `claude -p --no-session-persistence --model MODEL --allowedTools "Read,Grep,Glob,Bash(VERIFIER)"` where VERIFIER is the exact verifier command (so the critic can run tests but nothing else), or `codex exec` with the equivalent sandbox. A critic that cannot run the verifier because of an approval prompt is reading, not reviewing; fix the flags before the first call.
3. A same-session review from a structurally different prompt (persona, ranking, no praise), with every tally labelled "not cold". Never present it as a cold read.

Record the rung in the trajectory table's Critic column (for example `opus/cli`, `opus/agent`, `self/not cold`).

Model. Judges favour text from their own model family even on objective rubrics, and a fresh context does not remove that. Where the Agent tool exposes a model parameter, run the critic on a different model family from the one that wrote the artefact, or failing that a different model in the same family. Where only one model is available, say so beside the tally. Record the critic model in the trajectory table.

The critic gets the artefact, what it must check against, and nothing from the conversation: not the previous report, not the fix list, not the trajectory table, not your view of the problems. It will still see repository instructions and user memory. That is acceptable unless memory describes the artefact's subject or the author's position on it; if it does, say so beside the tally, because that critic is primed rather than cold.

- Executable document (runbook, build spec, handover pack): the file path.
- Code: the repository path with the code under review in place (the working tree as it stands, or the commit checked out), the diff from the base written to a file, the stated intent and frozen behaviour, and the verifier command. Tell the critic to run the verifier, edit nothing, and not read git history, because commit messages such as "fix round 1 blockers" hand it the fix list.
- Page or artifact: the HTML file (for a published artifact, read it with the Artifact tool if present and save it locally; if absent, ask the user for the HTML file) plus the source data if any. If none exists, say so in the brief and the critic ranks a figure as blocking only where the page contradicts itself. Before briefing, test the renderer with a trial screenshot (`from playwright.sync_api import sync_playwright`, launch Chromium, screenshot a blank page); if it works, tell the critic to screenshot at 390 px and 1440 px and read the screenshots. If it does not, say so and strike the width clause from the ranking row.
- Quality document: the file path and the brief or CFP it answers. Take the scoring criteria from the brief where it states them.
- Research or reference document: the file path and the number of cited sources to fetch and verify.

Persona matters more than the checklist. Brief the critic as the person who will have to live with the artefact and tell it to walk through as if using it: executing the runbook, reviewing the change before merge, viewing the page for the first time, sitting on the committee, relying on the bibliography for a decision.

Ranking scheme. Paste the row for the artefact type into the brief and hold the critic to the strict reading; critics inflate.

| Artefact | Blocking | Misleading | Minor |
|---|---|---|---|
| Executable document | Cannot take the next step without asking the author | Would take a step and get a wrong result | Wording |
| Code | Incorrect behaviour against the stated intent, or a failing or missing test | Correct now, but on a path the verifier does not cover, or a maintainer would break it | Style |
| Page or artifact | A wrong figure, a control, link or script that does not work, or unreadable at a target width | A first-time viewer would misread it; stale or undated content | Cosmetic |
| Quality document | Fails a stated requirement of the brief, or the reviewer cannot say what the contribution is | A claim the reviewer would reject as unsupported or overstated | Wording |
| Reference document | A claim the source contradicts, or a dead link | A claim the source does not support, a wrong date | Wording |

For a quality document the critic may also score 1 to 10 on the brief's criteria. Scores are reported, not acted on; the ranked list is what Step 2 acts on and the stopping rules read ranks.

Output constraints: a one-line tally first; for each defect, section, exact sentence, what is wrong, a one-line fix; one line per section that is fine; no praise; no rewriting, since a rewrite is an unreviewed draft; a word cap. A finding the critic cannot tie to a specific sentence or line is not a finding.

Where the artefact has two audiences or two halves, run two critics in parallel with different personas rather than one with a longer brief; a second cold reader catches what the first missed. Merge and deduplicate the two reports into one findings list before Step 1b, keeping the stricter rank for a shared finding, and record both critics in the table's Critic cell. A parallel pair counts two calls against the cap, so use it only where the cap leaves room.

## Step 1b: verify the findings

A critic asked to find problems reports some even when the work is sound, and longer or harsher critiques carry more invented defects. So no finding enters a fix batch unverified.

Spawn the checker, a second cold agent on the strongest model available (a weaker checker confirms whatever a stronger critic asserts; in testing a sonnet checker disputed nothing in six rounds), by the same ladder as Step 1 but with its own flags: on rung 2, `--allowedTools "Read,Grep,Glob,Bash,Write(SCRATCH/**)"` where SCRATCH is a directory outside the artefact, so it can write and run a reproduction without touching the work; for a judgement-only climb omit Bash. Brief it as the author's advocate whose job is to reject findings, and tell it that on a sound artefact most findings will fail the scope test. It gets the artefact, the Step 0 objective and scope test, the frozen behaviour, the verifier command if any, and the blocking and misleading findings as a list: section, sentence or line, claimed defect. It gets nothing else: not the critic's prose, not the tally, not the persona. It does not add findings of its own.

For each finding it returns two verdicts:
- Confirmed, not confirmed, or confirmed at a lower rank. Confirmed means reproduced, not reasoned: for code, a test the checker wrote and ran that fails on the artefact, or a run whose output shows the behaviour; for a document, the two sentences that contradict, or the step and the exact point at which a reader cannot proceed. A claim the checker finds plausible but cannot reproduce is not confirmed.
- In scope or out of scope, by the Step 0 scope test, naming the requirement or frozen item it breaks.

Only findings that are both confirmed and in scope enter the fix batch, at the checker's rank. Confirmed out-of-scope findings go straight to the owner's list as hardening suggestions, whatever their rank; they are counted in a separate column and never fixed in the climb. Unconfirmed findings are recorded as disputed and re-submitted to the next round's checker alongside that round's findings; they are not fixed, and they go on the owner's list at Step 5 if still disputed at the end. If the checker and critic disagree on rank, the checker's rank stands, because it was reached against the evidence rather than cold.

If only rung 3 of the ladder works, do the checking in-session against the artefact with the same two verdicts, label it "not cold", and still refuse to fix a finding you cannot reproduce or tie to a requirement.

## Step 2: fix in one batch, then verify

Extract the confirmed blocking and misleading findings into a list: section, line, defect, one-line fix. The fix step works from that list and the artefact, and from nothing else; the critic report and the checker's notes stay out of the fixer's context. Added context corrupts: a revision call given a helper document from another model broke more than three times as many passing programs as the same call without it.

Fix every confirmed in-scope blocking and misleading item in the list and nothing else, except after the final critic call, where rule 2 above applies: only edits a mechanical verifier covers. Add at most one test per fixed finding, the one that fails before the fix and passes after; the climb's own tests are in scope for later critics, so every extra test is a later finding waiting to happen. If blocking plus misleading exceed eight, fix the blocking items now and carry the misleading list forward unchanged into the next batch. Minor items wait until the stopping rule has fired; then fix them in one batch only where a mechanical verifier covers the edit, and list the rest. Improvements you notice yourself go on the owner's list, not into the batch.

Before applying each fix, state in a line what the edit must leave unchanged (the frozen behaviour it touches, or "nothing adjacent"). A fix that cannot be stated that way is a rewrite, and goes back to the owner's list.

When a finding is a policy question the author should not answer (which remote, which threshold, whether to change a shared interface), do not answer it. Replace it with a rule the owner can apply or a named placeholder, and tell the user.

Version every round and never overwrite the previous version; the trajectory is the evidence.

- Text: copy to `name-vN.md` (N is the round number plus one) beside the original and edit the copy. The Edit tool refuses a non-unique target; that is the safeguard. When one wrong string must change everywhere, use `replace_all` where the editor offers it and record the count.
- Code: confirm `git rev-parse --is-inside-work-tree` succeeds. If the tree is dirty with the user's own work, ask once whether to commit it as the round-1 version or to snapshot the file as versioned copies; never mix their change with a fix batch. Then one commit per fix batch on the branch under review; never create a branch or push without being asked. Outside git, use versioned copies.
- Published artifact: keep local `name-vN.html` files beside the original; republish once at Step 5, or each round if the user is watching, and say which.

Run the mechanical verifiers after the batch, before the next critic. A critic call is expensive; a grep is not.

## Step 3: next round

The next critic reads the new version in full and also receives the diff from the previous version, with no fix list, no previous report and no account of why anything changed. It is told that findings outside the diff must be blocking to be reported, since the rest of the artefact has already had a cold read; this stops each round regenerating the same out-of-scope list over the whole file. When it contradicts the previous critic (calls a fix a regression, re-ranks an accepted finding), record both and send the disputed item to that round's checker; the checker's rank stands. Revert the fix only if a mechanical verifier or the checker's reproduction shows the regression. Two cold readers disagreeing is information, not a reason to restart, and it is not a reason to take the harsher of the two.

Parallel draft for quality documents. If a quality document's second critic call, after a fix batch, still reports a confirmed blocking item of the "contribution not stated" or "fails a stated requirement" kind, a third revision is the wrong tool; the defect is in the approach, not the sentences. Instead, spawn a cold agent with the brief and the frozen behaviour (not the current draft) to produce a fresh draft, then run a cold critic that receives both drafts and the brief and reports which better meets the objective and why. Carry forward the one it prefers as the next version, note the switch in the trajectory table, and continue. This is the only place a rewrite enters a climb, and it counts as one critic call against the cap.

Keep a trajectory table. Update it each round; print it once at Step 5 unless the user is watching. The Reviewed column holds the version name or the commit SHA; the Critic column holds the critic model and ladder rung; Lines is the size of that round's fix batch.

| Round | Reviewed | Critic | Blocking | Misleading | Minor | Out of scope | Disputed | Lines |
|---|---|---|---|---|---|---|---|---|
| 1 | v1 | opus/cli | 5 | 3 | 5 | 11 | 2 | +84/-12 |
| 2 | v2 | opus/cli | 1 | 2 | 8 | 4 | 1 | +19/-3 |

Blocking and misleading are confirmed in-scope findings after Step 1b; Minor is the critic's raw minors plus findings the checker downgraded to minor; out of scope holds confirmed findings the scope test excluded; disputed holds the ones the checker did not confirm. A large out-of-scope column with a small blocking column is a sound artefact being hardened, and the owner should see that rather than a tally that looks like a defective one. Changing criteria, mechanical verifiers or critic model mid-climb starts a new table, because the rows stop being comparable.

## Step 4: stop by the rule

Each rule is evaluable from the table and the latest report without the author's judgement.

1. A mechanical verifier that covers correctness (tests, not word count) passes and the latest cold read reports zero confirmed in-scope blocking.
2. Every confirmed in-scope blocking and misleading item in the latest report is something only the owner can supply: a name, an internal fact, a decision, a pasted answer.
3. Two consecutive reads report zero confirmed in-scope blocking, and no confirmed in-scope misleading item would change a step's order, input or output (executable document), touch a path the verifier does not cover (code), concern a figure or status (page), or concern a claim the reviewer scores on (quality document). The person using the artefact is now a cheaper reviewer than another round. When round 1 ended with zero confirmed in-scope blocking, one such read is enough.
4. The cap is hit. Say so and report what remains.

"Zero findings" is not a rule; a cold reader always finds something. If the user asks why you stopped and the reason was not set in Step 0, say so and, unless it breaches the cap, run one more round with the user's own persona.

## Step 5: deliver and report

Deliver the way the user asked. Text: send the file. Code: leave commits local on the branch and report the SHA range; push or open a PR only if asked. Page: republish to the same URL, unless confirmed blocking items remain, in which case hand back the local file and the list rather than putting a known-defective version on a shared link. Then, in a few lines:

- The trajectory table.
- One line per round on what changed the design or the claims; wording fixes are not listed.
- Which rule stopped the climb.
- One consolidated owner's list: unfixed items from the final call, confirmed out-of-scope hardening suggestions (grouped, with the requirement each would add), items still disputed, minors not covered by a mechanical verifier, placeholders, improvements noticed, and anything the artefact assumes that no cold reader could check.

## Critic prompt template

Adapt it; replace the persona, inputs and checks with ones specific to the artefact.

```
You are [persona: the person who will execute, merge, view, judge or rely on this].
You have been handed [the file at PATH / the repository at PATH with the change in
place, the diff at PATH, verifier command CMD / the page at PATH and its source
data at PATH, or: there is no source data / the document at PATH and the brief it
answers at PATH]. The stated intent is: [one sentence]. Frozen behaviour: [one
line]. The author is unavailable and you have no other context. Do not read git
history. [Round 2 and later: the diff from the previous version is at PATH; the
rest of the artefact has already had a cold read, so report a finding outside
that diff only if it is blocking.]

Do not rewrite or edit anything. [Code: run CMD. Page: screenshot at 390 px and
1440 px with Playwright and read the screenshots.] Walk through it as if
[executing it / reviewing the change before merge / viewing it for the first time /
scoring it for the committee] and report every point where you would get stuck,
guess, need to ask the author, reject a claim, or could misread it.

Specifically check:
- [executable document: shell commands against the stated layout; every number
  asked for is defined precisely enough to record; every stage has an input and
  an output]
- [code: behaviour at boundaries the intent implies; concurrent callers; what the
  tests do not cover; error paths]
- [page: every figure against the source; every control and link; both widths]
- [quality document: every requirement in the brief; the contribution is stated;
  every claim is supported]
- [all: internal contradictions; anything assumed to exist with no way to check]

Rank each issue as blocking, misleading or minor, where [paste the row for this
artefact type]. Be strict about the ranking. For each: section, the exact
sentence or line, what is wrong, a one-line fix. If a section is fine, say so in
one line. Report only what would change a reader's action or a stated
requirement; a finding you cannot tie to a specific sentence or line is not a
finding. Do not praise. Under 600 words. Begin your final message with a
one-line tally: N blocking, N misleading, N minor.
```

## Checker prompt template

```
You are the author's advocate. Your job is to reject claims that do not hold.
You have been handed [the artefact at PATH] and, where it exists, [verifier
command CMD]. The objective it must meet: [numbered requirements]. Frozen
behaviour: [one line]. Below is a list of claimed defects. For each, return two
verdicts. First: CONFIRMED only if you reproduced it (for code, write and run a
test or script that shows the behaviour, and quote the output; for a document,
quote the sentences that contradict or the exact point a reader cannot proceed);
NOT CONFIRMED with why; or CONFIRMED AT [rank] with why, where [paste the row
for this artefact type]. A claim that is plausible but that you could not
reproduce is NOT CONFIRMED. Second: IN SCOPE, naming the requirement number or
frozen item it breaks, or OUT OF SCOPE. Most findings on a sound artefact are
out of scope; a real edge case that no stated requirement covers is out of
scope. Do not add findings. Do not edit the artefact. Under 500 words.

[numbered list: section, sentence or line, claimed defect]
```
