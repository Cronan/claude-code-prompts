---
name: "hill-climb"
description: "Improve a finished draft of anything (code, a document, an HTML artifact, a proposal, a plan, a prompt, a skill) by rounds of cold review, verified findings and small fixes until a pre-agreed stopping rule fires. Use for hill-climb, improve until good, review and fix, harden this, make it survive review."
---

# Hill climb

A hill climb takes a complete draft and raises its quality in rounds. A round is one cold critic call, one verification of its findings, one fix batch and a new saved version. The climb stops when a rule agreed before round one fires, not when the author is tired or the reviewer runs out of things to say.

Two rules shape everything below.

1. Self-review misses most of what matters. Models fail to correct their own errors about two thirds of the time while fixing the identical error when it arrives from someone else; an author rereading its own work finds wording, a fresh reader with the file and nothing else finds the shell command that deletes `.git`. The critic must not have seen the work being produced, and findings must reach the author as an external report.
2. Fixes introduce defects, and the defect count does not fall monotonically. A round helps only when its correction rate exceeds its corruption rate times baseline quality over the remainder, so a round on an already-clean artefact is more likely to harm than help, and the context handed to a fixer is itself a source of corruption. So: fix only confirmed findings, hand the fixer findings rather than prose, and deliver a version a critic has read. Findings from the final critic call are applied only where a verifier covers the edit; everything else from that call is listed for the owner.

## Step 0: set the contract, one per artefact

Two artefacts means two climbs with two contracts, two tables and two caps. Write the contract in the conversation in at most four lines before the first critic runs, so the user sees it and the author cannot move the goalposts later.

- Objective, as a test a stranger could run. Executable document: "an engineer with no other context can execute this without asking the author a question". Code: "the verifier passes and a reviewer reading the change cold, knowing the stated intent, finds no correctness defect". Page: "every figure matches the source data (or, with no source, the page is internally consistent and dated) and it reads correctly at 390 px and 1440 px". Quality document (essay, proposal): "a reviewer applying the brief's own criteria finds no claim they would reject and no requirement unmet". If the user gave no objective, propose one in a sentence and proceed.
- Frozen behaviour. What a fix may not change. Document: reading order, length ceiling, house style, any structure the brief or CFP mandates. Code: the change's intent as the user states it (if unstated, infer it from the change, state it, proceed), every test on the base, and any interface the change does not touch; tests the change itself adds are in scope and may be wrong. For uncommitted work the base is HEAD and the artefact is the working tree; say so. Page: the data source and the published URL. A fix that moves frozen behaviour is a regression however good it looks; fix the fix, not the check.
- Verifiers. Mechanical checks needing no judgement: the test command, a linter, `json.loads` over every fenced block, a grep for banned words and em-dashes, a word count, a cross-reference check between sections. Record the exact command and environment now. A screenshot is a critic input, not a verifier, because reading it takes judgement; a page usually has no verifier. If nothing mechanical exists, say so and treat the climb as judgement-only. A verifier added mid-climb counts from the round it joins.
- Stopping rules and cap. State which of rules 1 to 3 in Step 4 apply; the first to fire stops the climb, and rule 4 (the cap) is always the backstop. Cap: three critic calls for prose, five for code or for documents containing shell commands. These are judgement figures, not measured ones; the literature gives a break-even condition, not a round count. If the first critic call reports zero blocking, the cap drops to two critic calls whatever the artefact type, because the artefact is in the regime where further rounds corrupt more than they correct. If the user named a number of rounds, that is the cap. Two critics run in parallel count as two calls against the cap and as one read for rule 3. Verification calls do not count against the cap.

## Step 1: run a cold critic

Use the Agent tool to spawn a fresh subagent; check it is present first (ToolSearch if not loaded). If no subagent tool exists, a cold critic is impossible in this session: say so, then continue Steps 1 to 5 with a same-session review written from a structurally different prompt (persona, ranking, no praise), labelling every tally "not cold". Never present a same-session review as a cold read.

Model. Judges favour text from their own model family even on objective rubrics, and a fresh context does not remove that. Where the Agent tool exposes a model parameter, run the critic on a different model family from the one that wrote the artefact, or failing that a different model in the same family. Where only one model is available, say so beside the tally. Record the critic model in the trajectory table.

The critic gets the artefact, what it must check against, and nothing from the conversation: not the previous report, not the fix list, not the trajectory table, not your view of the problems. It will still see repository instructions and user memory. That is acceptable unless memory describes the artefact's subject or the author's position on it; if it does, say so beside the tally, because that critic is primed rather than cold.

- Executable document (runbook, build spec, handover pack): the file path.
- Code: the repository path with the code under review in place (the working tree as it stands, or the commit checked out), the diff from the base written to a file, the stated intent and frozen behaviour, and the verifier command. Tell the critic to run the verifier, edit nothing, and not read git history, because commit messages such as "fix round 1 blockers" hand it the fix list.
- Page or artifact: the HTML file (for a published artifact, read it with the Artifact tool if present and save it locally) plus the source data if any. If none exists, say so in the brief and the critic ranks a figure as blocking only where the page contradicts itself. Before briefing, test the renderer with a trial screenshot (`from playwright.sync_api import sync_playwright`, launch Chromium, screenshot a blank page); if it works, tell the critic to screenshot at 390 px and 1440 px and read the screenshots. If it does not, say so and strike the width clause from the ranking row.
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

Where the artefact has two audiences or two halves, run two critics in parallel with different personas rather than one with a longer brief; a second cold reader catches what the first missed. Two parallel critics are also the default for the final critic call of any climb, since the delivered version is the one that most needs two readers.

## Step 1b: verify the findings

A critic asked to find problems reports some even when the work is sound, and longer or harsher critiques carry more invented defects. So no finding enters a fix batch unverified.

Spawn a second cold agent (it may be a smaller model or lower effort, since it checks named claims rather than reading cold). It gets the artefact, the frozen behaviour, the verifier command if any, and the blocking and misleading findings as a list: section, sentence or line, claimed defect. It gets nothing else: not the critic's prose, not the tally, not the persona. For each finding it returns one of: confirmed, with the evidence in a line; not confirmed, with why; or confirmed at a lower rank, with why. It does not add findings of its own.

Confirmed findings enter the fix batch at the verifier's rank. Unconfirmed findings are recorded in the trajectory as disputed and carried forward; they are not fixed, and they go on the owner's list at Step 5 if still disputed at the end. If the verifier and critic disagree on rank, the verifier's rank stands, because it was reached against the evidence rather than cold.

If no second agent is available, do the verification in-session against the artefact, label it "not cold", and still refuse to fix a finding you cannot tie to a line.

## Step 2: fix in one batch, then verify

Extract the confirmed blocking and misleading findings into a list: section, line, defect, one-line fix. The fix step works from that list and the artefact, and from nothing else; the critic report and the verifier's notes stay out of the fixer's context. Added context corrupts: a revision call given a helper document from another model broke more than three times as many passing programs as the same call without it.

Fix every confirmed blocking and misleading item in the list and nothing else, except after the final critic call, where rule 2 above applies. If blocking plus misleading exceed eight, fix the blocking items now and carry the misleading list forward unchanged into the next batch. Minor items wait until the stopping rule has fired; then fix them in one batch only where a verifier covers the edit, and list the rest. Improvements you notice yourself go on the owner's list, not into the batch.

Before applying each fix, state in a line what the edit must leave unchanged (the frozen behaviour it touches, or "nothing adjacent"). A fix that cannot be stated that way is a rewrite, and goes back to the owner's list.

When a finding is a policy question the author should not answer (which remote, which threshold, whether to change a shared interface), do not answer it. Replace it with a rule the owner can apply or a named placeholder, and tell the user.

Version every round and never overwrite the previous version; the trajectory is the evidence.

- Text: copy to `name-v3.md` beside the original and edit the copy. The Edit tool refuses a non-unique target; that is the safeguard. When one wrong string must change everywhere, use `replace_all` where the editor offers it and record the count.
- Code: confirm `git rev-parse --is-inside-work-tree` succeeds. If the tree is dirty with the user's own work, ask once whether to commit it as the round-1 version or to snapshot the file as versioned copies; never mix their change with a fix batch. Then one commit per fix batch on the branch under review; never create a branch or push without being asked. Outside git, use versioned copies.
- Published artifact: keep local `name-v3.html` files beside the original; republish once at Step 5, or each round if the user is watching, and say which.

Run the verifiers after the batch, before the next critic. A critic call is expensive; a grep is not.

## Step 3: next round

The next critic reads the new version in full with no knowledge of what changed. When it contradicts the previous critic (calls a fix a regression, re-ranks an accepted finding), record both and send the disputed item to the Step 1b verifier for that round; the verifier's rank stands. Revert the fix only if a verifier shows the regression. Two cold readers disagreeing is information, not a reason to restart, and it is not a reason to take the harsher of the two.

Parallel draft for quality documents. If a quality document's second critic call, after a fix batch, still reports a confirmed blocking item of the "contribution not stated" or "fails a stated requirement" kind, a third revision is the wrong tool; the defect is in the approach, not the sentences. Instead, spawn a cold agent with the brief and the frozen behaviour (not the current draft) to produce a fresh draft, then run a cold critic that receives both drafts and the brief and reports which better meets the objective and why. Carry forward the one it prefers as the next version, note the switch in the trajectory table, and continue. This is the only place a rewrite enters a climb, and it counts as one critic call against the cap.

Keep a trajectory table. Update it each round; print it once at Step 5 unless the user is watching. The Reviewed column holds the version name or the commit SHA; the Critic column holds the critic model.

| Round | Reviewed | Critic | Blocking | Misleading | Minor | Disputed |
|---|---|---|---|---|---|---|
| 1 | v1 | opus | 5 | 13 | 5 | 2 |
| 2 | v2 | opus | 3 | 15 | 8 | 1 |

Counts are confirmed findings after Step 1b; disputed holds the ones the verifier did not confirm. Changing criteria, verifiers or critic model mid-climb starts a new table, because the rows stop being comparable.

## Step 4: stop by the rule

Each rule is evaluable from the table and the latest report without the author's judgement.

1. A verifier that covers correctness (tests, not word count) passes and the latest cold read reports zero confirmed blocking.
2. Every confirmed blocking and misleading item in the latest report is something only the owner can supply: a name, an internal fact, a decision, a pasted answer.
3. Two consecutive reads report zero confirmed blocking, and no confirmed misleading item would change a step's order, input or output (executable document), touch a path the verifier does not cover (code), concern a figure or status (page), or concern a claim the reviewer scores on (quality document). The person using the artefact is now a cheaper reviewer than another round. When the first critic call reported zero blocking, one such read is enough.
4. The cap is hit. Say so and report what remains.

"Zero findings" is not a rule; a cold reader always finds something. If the user asks why you stopped and the reason was not set in Step 0, say so and, unless it breaches the cap, run one more round with the user's own persona.

## Step 5: deliver and report

Deliver the way the user asked. Text: send the file. Code: leave commits local on the branch and report the SHA range; push or open a PR only if asked. Page: republish to the same URL, unless confirmed blocking items remain, in which case hand back the local file and the list rather than putting a known-defective version on a shared link. Then, in a few lines:

- The trajectory table.
- One line per round on what changed the design or the claims; wording fixes are not listed.
- Which rule stopped the climb.
- One consolidated owner's list: unfixed items from the final call, items still disputed, minors not covered by a verifier, placeholders, improvements noticed, and anything the artefact assumes that no cold reader could check.

## Critic prompt template

Adapt it; replace the persona, inputs and checks with ones specific to the artefact.

```
You are [persona: the person who will execute, merge, view, judge or rely on this].
You have been handed [the file at PATH / the repository at PATH with the change in
place, the diff at PATH, verifier command CMD / the page at PATH and its source
data at PATH, or: there is no source data / the document at PATH and the brief it
answers at PATH]. The stated intent is: [one sentence]. Frozen behaviour: [one
line]. The author is unavailable and you have no other context. Do not read git
history.

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

## Verifier prompt template

```
You have been handed [the artefact at PATH] and, where it exists, [verifier
command CMD]. Frozen behaviour: [one line]. Below is a list of claimed defects.
For each, check it against the artefact (run CMD where relevant) and return
exactly one of: CONFIRMED, with the evidence in one line; NOT CONFIRMED, with why
in one line; CONFIRMED AT [rank], with why in one line, where [paste the row for
this artefact type]. Do not add findings. Do not edit anything. Under 400 words.

[numbered list: section, sentence or line, claimed defect]
```
