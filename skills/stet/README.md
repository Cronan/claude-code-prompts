# /stet

*Stet* is a proofreading mark from the Latin for "let it stand." An editor crosses something out, reconsiders, writes *stet* in the margin and dots the deletion -- the original stays.

This skill does the inverse. AI has overwritten your voice with its patterns: uniform sentence lengths, the same three-paragraph cadence, "furthermore" and "leverage" and "comprehensive" on every page. The writing is genuinely worse with these patterns in it -- not because it triggers detectors, but because it is monotonous, vague, and sounds like everyone else. `/stet` identifies 27 of these patterns and strips them, letting what you actually meant to say come through.

This is not a humanizer. Humanizers rewrite text to evade classifiers. Stet edits text to make it better. The difference matters: a humanizer optimizes for the signal, stet fixes the underlying problem. If you are trying to pass off AI output as your own, this is the wrong tool. If you used AI to draft something and want it to actually sound like you wrote it, read on.

## The 27 patterns

Organized by how much they degrade the writing -- from structural problems that make entire passages feel synthetic, down to surface noise that accumulates.

**Structural patterns** (rhythm and shape -- what makes text feel monotonous):

1. Sentence length uniformity -- every sentence is 15-25 words
2. Paragraph length uniformity -- every paragraph is 3-5 sentences
3. Epistemic uniformity -- equal confidence in every claim
4. Register consistency -- formality never shifts
5. Punctuation distribution -- only commas, periods, and dashes

**Vocabulary and construction** (word choice and phrasing that sounds generic):

6. Overused AI vocabulary -- furthermore, comprehensive, leverage, foster, delve, seamless, nuanced ...
7. Copula avoidance -- "serves as" instead of "is"
8. Significance inflation -- everything is pivotal, crucial, transformative
9. Superficial participle phrases -- "highlighting the importance of"
10. Causal over-assertion -- clean because/therefore chains where reality is messy
11. Vague attributions -- "industry experts suggest"

**Polish** (individually minor, collectively diagnostic):

12. Promotional language -- groundbreaking, revolutionary, game-changing
13. Formulaic section headers -- "Why this matters," "Looking ahead"
14. Weak transitions -- Furthermore, Moreover, In addition
15. Bureaucratic bloat -- "in order to," "due to the fact that"
16. Intensifiers -- very, really, extremely, incredibly
17. Formatting tells -- em dash overuse, excessive boldface
18. Communication artifacts -- "I hope this helps," "Let me know if"
19. Hedging and sycophancy -- "Great question!", "The possibilities are endless"

**Corpus-level** (visible only when comparing multiple texts by the same "author"):

20. Cross-text verbatim repetition
21. Structural homogeneity
22. Convergent framing devices
23. Motif overuse

**Voice and personality** (what to add, not just what to remove):

24. Emotional flatness -- no reaction to the material
25. Opinion absence -- every side presented with equal weight
26. Absence of specific detail -- "a large-scale system" vs. the actual system
27. Temporal flattening -- everything in vague present tense

## Before and after

**Before:**

> The team evaluated several deployment strategies before selecting blue-green deployments. This approach allows seamless switching between production environments. The rollback process becomes significantly simpler with this architecture. Teams can verify new releases against production traffic before committing fully.

**After:**

> The team tried three deployment strategies. Blue-green won, mostly because rollbacks are instant -- you just flip the route back. Whether the added infrastructure complexity is worth it depends on how often you actually need to roll back, which in our case turned out to be roughly once a sprint, so yes.

Each pattern includes diagnostics, before/after examples, and fix guidance. Full specification: [`SKILL.md`](SKILL.md).

**Important:** When stet adds specific details (pattern 26) or temporal anchoring (pattern 27), it uses details already present in the text or clearly plausible from context. It does not invent statistics, dates, or anecdotes. Where the text lacks specifics, stet flags the gap for you to fill.

## Install

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Copy the skill into your repo:

```
cp -r skills/stet/ your-repo/.claude/skills/stet/
```

Then invoke it on any text file:

```
/stet article.md
```

Or on a collection:

```
/stet posts/piece-a.md posts/piece-b.md posts/piece-c.md
```

## Research references

The pattern list draws on published research:

- [Linguistic Characteristics of AI-Generated Text: A Survey (arXiv, 2025)](https://arxiv.org/pdf/2510.05136) -- sentence length distributions, punctuation entropy, vocabulary frequency
- [The Disappearing Author: Linguistic and Cognitive Markers (2025)](https://researchleap.com/the-disappearing-author-linguistic-and-cognitive-markers-of-ai-generated-communication/) -- epistemic uniformity, affective markers, cognitive markers
- [Comparative linguistic analysis of human vs. machine-generated text (2025)](https://www.tandfonline.com/doi/full/10.1080/09540091.2025.2507183) -- structural regularity, stylistic consistency
- [Monitoring AI-Modified Content at Scale -- Liang et al. (ICML, 2024)](https://arxiv.org/abs/2403.07183) -- vocabulary frequency shifts in LLM-modified text
- [DetectGPT: Zero-Shot Machine-Generated Text Detection -- Mitchell et al. (ICML, 2023)](https://arxiv.org/abs/2301.11305) -- perplexity-based detection
- [GLTR: Statistical Detection and Visualization of Generated Text -- Gehrmann et al. (ACL, 2019)](https://aclanthology.org/P19-3019/) -- token probability uniformity

## Word list derivation

The overused vocabulary list (pattern 6) and other word lists were compiled by generating 20 passages across varied topics and registers, then counting which words appeared disproportionately often relative to equivalent human writing, and cross-referencing against the published corpus studies listed above.
