# Review of /hill-climb against the 2024 to 2026 literature

Scope: the skill as it stands, checked against the self-correction and LLM-as-judge literature through mid-2026, and against two proven pipelines (OpenAI's CriticGPT work and Anthropic's Claude Code review pipeline, October 2026).

## Verdict

The two foundational rules are right and now have stronger evidence behind them than when the skill was written. Cold critic, frozen behaviour, verifier-gated final fixes and versioned trajectory are ahead of most published practice. The skill has four substantive gaps, one of which (no verification step between critic and fixer) is the single biggest divergence from the proven pipelines. Six recommended edits follow, ranked.

## What the literature now says

**Self-review is a blind spot, not a capability gap.** Self-Correction Bench (Tsui 2025) injected identical errors and found a 64.5% average failure rate across 14 models at correcting their own errors, while the same models reliably fixed the same error when it arrived from an external source. The Self-Correction Illusion (Chen et al., June 2026) sharpens this: agents committed to a wrong claim in their own reasoning about 83% of the time but to a byte-identical external claim at most 3.3% of the time. The authors call it a chat-template artefact: instruction tuning makes content under external roles addressable and content in the model's own output not. This is the mechanistic reason the cold critic works, and also why the fix step works: the author will act on a critic's finding because it arrives under an external role.

Implication for the skill: rule 1 ("self-review finds nothing that matters") is directionally right but overstated. The measured failure rate is two thirds, not all. Worth softening to what the evidence supports, since the skill is itself a document a reviewer may hold to its own standard.

**Fixes corrupt, and the break-even point depends on baseline quality.** Two independent 2026 papers (Reitich, "Correction and Corruption"; Liu and Meng, "Self-Correction as Feedback Control") derive the same identity: a revision round improves net quality only when correction rate exceeds corruption rate times baseline/(1 minus baseline). At 75% baseline the multiplier is 3; at 95% it is 19. Liu and Meng measured across seven models and found a near-zero error-introduction boundary (under 0.5%) separates models where repeated self-revision helps from those where it harms; GPT-5 and four others lost accuracy under iteration, Claude Opus 4.6 and o3-mini did not. Their "verify-first" prompt intervention drove GPT-4o-mini's error-introduction rate from 2% to 0% and turned a 6.2 point loss into a 0.2 point gain.

Implication: rule 2 is right, and the cap is right in spirit, but the skill treats rounds as uniformly worth running up to the cap. An artefact that enters at high quality (first critic reports zero blocking) is in the regime where a further round is more likely to harm than help. The stopping rules do not currently respond to this.

**Added context corrupts the fixer.** Reitich's MBPP audit is the sharpest result: on 357 programs that already passed their tests, a revision call given only the task and the program broke 7.8% of them; the same call given an additional helper artefact from another model broke 28%. The helper was the problem. Your critic report is a helper artefact handed to the fixer.

Implication: the skill's rules "fix every blocking and misleading item and nothing else", "no rewriting" and "improvements you notice go on the owner's list" are the right countermeasures and this is their evidence. The skill could go one step further: the fixer should receive the ranked findings, not the critic's full prose.

**Critics asked to find problems find problems.** CriticGPT (OpenAI 2024) found that longer critiques are more likely to include hallucinated bugs and nitpicks, and that human-plus-critic teams hallucinated less than critics alone. Anthropic's current best-practices guidance says the same from the other side: a reviewer prompted to find gaps will usually report some even when the work is sound, so tell it to flag only what affects correctness or stated requirements. Anthropic's own Code Review product and internal pipeline do not go critic to fix: they dispatch parallel bug hunters, then a second group verifies each finding to remove false positives, then rank by severity.

Implication: the skill's 600-word cap and "no praise, no rewriting" constraints are well supported. "Be harsh" is not; it pushes toward the hallucination end of the trade-off. More importantly, the skill has no verify step. Findings go straight from critic to fix batch, and rule "keep the stricter rank" when critics disagree ratchets in the wrong direction when the stricter critic is the one hallucinating.

**Self-preference bias survives a fresh context.** Pombal, Rei and Martins (April 2026) tested rubric-based judging on IFEval and LiveCodeBench, where criteria are programmatically verifiable, and still found judges over 50% more likely to wrongly mark a failed criterion as satisfied when the output was their own model's. Wataoka et al. (NeurIPS 2024 workshop) trace the mechanism to perplexity: judges rate low-perplexity, familiar text higher regardless of who wrote it. Ensembling judges across families mitigates but does not eliminate it.

Implication: the skill's cold critic removes conversation contamination, which is the larger effect, but a same-family critic reading same-family prose is still biased toward it. The Agent tool exposes a model parameter; the skill does not use it.

**Judge inputs are contaminated by anything nearby.** Order, length, tone, bandwagon metadata and prior tallies all shift verdicts (Wang et al. ACL 2024; Zheng et al. 2023; the twelve-bias catalogue in "Justice or Prejudice", 2024). The skill's "do not read git history" rule, the stripping of the previous report and the fix list, and the warning about primed memory are all correct applications of this. Nothing to add except that a published trajectory table shown to a critic would be the same contamination; the skill already prints it only at Step 5.

**Sequential revision is not always the right scaling axis.** Snell et al. (2024, ICLR 2025) showed sequential revision outperforms parallel sampling on easier problems, while harder problems need parallel samples because they require a different approach rather than a repaired one. The skill is purely sequential and forbids rewriting. For code and executable documents that is correct. For a quality document whose round-one critic reports a blocking item of the kind "cannot say what the contribution is", the literature says a second revision round is the wrong tool; a fresh parallel draft against the brief, then a cold comparison, is.

## Where the skill is ahead of published practice

Three things in the skill have no clean counterpart in the papers and should stay as they are.

Frozen behaviour, with the rule "fix the fix, not the check". The corruption literature measures regressions but has no design pattern for preventing them; this is one.

Rule 2's final-call handling: findings from the last critic are applied only where a verifier covers the edit. This is the practical answer to "the version you deliver must be one a critic has read", and I have not seen it stated elsewhere.

The ranking table with artefact-specific definitions of blocking, misleading and minor. CriticGPT's human raters needed exactly this to score critiques; the skill gives it to the critic up front.

## Recommended edits, ranked

1. **Add a verify step between critic and fix batch.** After each critic call, before Step 2, a second cold agent receives each blocking and misleading finding (section, sentence, claim) plus the artefact, and returns confirmed or not confirmed with one line of evidence. Only confirmed findings enter the fix batch; unconfirmed ones are recorded in the trajectory as "disputed" and carried, not fixed. This mirrors Anthropic's hunt, verify, rank pipeline and addresses the CriticGPT hallucination result directly. It also replaces the "keep the stricter rank" rule for inter-round disagreement: a disputed rank goes to the verifier, not to the stricter critic. Cost: one cheaper call per round (the verifier can run at lower effort or on a smaller model since it checks specific claims rather than reading cold).

2. **Make the stopping rules respond to baseline quality.** Add to Step 4: if the first critic call reports zero blocking, the cap drops to two critic calls regardless of artefact type, and rule 3 collapses to one quiet round. Reason: the break-even multiplier at high baseline makes a third round more likely to corrupt than correct. State the identity in one line in the "Two rules" preamble so a reader knows why.

3. **Use a different model family for at least one critic, where the harness allows it.** In Step 1, when the Agent tool exposes a model parameter, run the critic on a different model from the one that wrote the artefact. Where only one family is available, run two critics with different personas (the skill already permits this) and treat the parallel pair as the default for the final round rather than the exception. Record the critic model in the trajectory table's Reviewed column.

4. **Replace "Be harsh" in the critic template.** Replace with: "Report only what would change a reader's action or a stated requirement. A finding you cannot tie to a specific sentence or line is not a finding." This is Anthropic's current guidance and the CriticGPT trade-off in one sentence. Keep "Do not praise" and the word cap.

5. **Hand the fixer findings, not prose.** In Step 2, extract the ranked findings into a list (section, line, defect, one-line fix) and give the fix step that list and the artefact only. The MBPP corruption result is the reason. In a single-session climb this is a discipline rather than a mechanism, but it should be stated.

6. **Add a parallel-draft escape for quality documents.** In Step 3, if a quality document's second critic still reports a blocking item of the "contribution not stated" or "fails a stated requirement" kind after a fix batch, the next round is a fresh draft against the brief by a cold agent, not a third revision, followed by a cold critic comparing the two. This is the one place the skill's "no rewriting" rule conflicts with the evidence, and it should be a narrow, explicit exception rather than a general loosening.

Two smaller wording changes: soften rule 1 to "self-review misses most of what matters" with the 64.5% figure if you want it cited; and note beside the cap that three and five are judgement figures, since no paper gives a round count, only the break-even condition.

## What I checked and did not find

No paper measures cold-critic review loops on prose documents with human ground truth; the quantitative evidence is on maths, code and short-answer tasks. The skill's quality-document and executable-document rows are therefore extrapolation, which is fine, but worth knowing. No published pipeline versions every round and keeps the trajectory as evidence; Anthropic's pipeline logs findings but the post does not describe keeping intermediate versions. The MBPP helper-corruption result is one model family on one benchmark; it is the strongest single number here and also the least replicated.

## Sources

- Reitich, "Correction and Corruption: A Two-Rate View of Error Flow in LLM Protocols" (2026): https://arxiv.org/abs/2604.18245
- Liu and Meng, "Self-Correction as Feedback Control" (2026): https://arxiv.org/abs/2604.22273
- Chen, Su and Chiang, "The Self-Correction Illusion" (2026): https://arxiv.org/abs/2606.05976
- Tsui, "Self-Correction Bench" (2025): https://arxiv.org/abs/2507.02778
- Pombal, Rei and Martins, "Self-Preference Bias in Rubric-Based Evaluation" (2026): https://arxiv.org/abs/2604.06996
- Wataoka, Takahashi and Ri, "Self-Preference Bias in LLM-as-a-Judge" (2024): https://arxiv.org/abs/2410.21819
- McAleese et al., "LLM Critics Help Catch LLM Bugs" (CriticGPT, 2024): https://arxiv.org/abs/2407.00215
- Snell et al., "Scaling LLM Test-Time Compute Optimally" (2024): summarised at https://faculty.cc.gatech.edu/~zk15/teaching/AY2025_cs7643_spring/assets/L25_Charlie_Snell_Scaling_TestTime_Compute.pdf
- Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet" (ICLR 2024)
- Kamoi et al., "When Can LLMs Actually Correct Their Own Mistakes?" (TACL 2024)
- Osmani, Lunt and Wang, "How the Claude Code team does code review" (Anthropic, 15 October 2026), via https://paddo.dev/blog/claude-reviewing-claude and https://blog.laozhang.ai/en/posts/claude-code-team-code-review
- Anthropic Claude Code best practices on reviewer subagents, via https://www.analyticsvidhya.com/blog/2026/08/claude-code-best-practices-analysis/
- Zesearch self-improvement survey (TMLR 2026) for the reading list: https://github.com/Zesearch/self-improvement-llm
