# Structured Research with AI: A Practitioner’s Guide  
  
Author: Ivan Cronyn | Date: March 2026 | Version: 7  
  
## What this document is  
  
A complete guide to producing evidence-backed documents using AI. It covers setup, prompt development, multi-pass research, reconciliation, drafting, fact validation, voice editing, and final document production. It includes a worked example with every prompt written out. The implementation instructions use Claude, but the method works with any model capable of web search and structured output.  
  
## Who it’s for  
  
Anyone who needs to produce something grounded in evidence. No programming required.  
  
## What it produces  
  
Anything that needs to be right: competitive analyses, board papers, internal proposals, research reports, policy briefs, technical assessments, or long-form articles. The pipeline scales. A blog post backed by three sources doesn’t need the same rigour as a regulatory submission. This guide tells you how to calibrate.  
  
## Before You Build the Pipeline: Five Things That Work Right Now  
  
You don’t need to read this entire guide to improve your next research conversation. The full pipeline described later systematises these ideas into a repeatable process, but each one works on its own, in any AI tool, starting today.  
  
### Write a brief before you start  
  
A three-sentence statement changes the output more than any prompt technique. Before you type anything, write down: what the document is for, who will read it, and what a good answer looks like. “Research Datadog” is a bad brief. “Produce a pricing comparison that the CFO can use to decide whether we raise enterprise rates” is a good one. The difference is that the second version tells the model what counts as relevant. Without it, you get a Wikipedia-shaped answer that covers everything and serves nothing.  
  
You don’t need a template. Open a text file and write: one sentence on the purpose, one on the audience, one on what success looks like. Upload it or paste it at the start of your conversation. That’s it.  
  
### Tell the model to quote sources before summarising them  
  
When an AI model reads a source and immediately summarises it, the summary can drift from what the source actually says. Small drifts compound. By the end of a long research session, claims may bear only a passing resemblance to their sources.  
  
One sentence in your prompt fixes this: “For every source you find, quote the specific passage that supports the claim before summarising it.” This forces the model to ground each finding in actual text before interpreting it. The quote becomes an anchor you can check. If the summary says something the quote doesn’t, you can see it. Anthropic’s own hallucination reduction guidance recommends exactly this technique: ask the model to extract word-for-word quotes first, then perform the task.  
  
### Give permission to say “I don’t know”  
  
Models default to producing answers. They will generate plausible text about topics where they have no reliable information, because that is what the training optimises for. You need to break this default explicitly.  
  
Add to your prompt: “If you cannot find credible evidence, say ‘I could not find public evidence for this.’ Do not invent or infer sources.” This single instruction changes the failure mode from confident fabrication to honest gaps. Gaps are useful. They tell you where to look next, or where to accept that public information doesn’t exist. A fabricated claim disguised as a finding wastes your time and, if it reaches a decision-maker, your credibility.  
  
### Ask for confidence ratings on each claim  
  
Not all findings are equal, but without a rating system, every claim in a research output reads with the same authority. A number from an SEC filing and an estimate from an undated blog post sit side by side, indistinguishable.  
  
Ask the model to rate every claim: High (multiple corroborating sources or a primary source like a filing or official report), Medium (single credible source or reasonable inference from strong evidence), Low (unverified, inferred, or based on secondary reporting only). This takes no setup. You’re giving the model a vocabulary for uncertainty, and it will use it. The ratings propagate: when you later draft a document from the research, you know which claims to state as fact and which to hedge. A draft built on rated evidence is a draft you can defend.  
  
### Run the same question twice and compare  
  
This is the simplest version of the multi-pass method that forms the core of this guide. Take your most important research question. Ask it in one conversation. Then open a new conversation and ask it again. Compare the two answers.  
  
Where they agree, you have corroboration. Where they disagree, you have something worth investigating. A single pass follows whatever search results come back first. Two passes surface contradictions, alternative sources, and findings that one pass missed. In the project that produced this guide, the third pass on every topic found at least one thing the first two didn’t. You don’t need three passes for a blog post. But two conversations instead of one, on the question that matters most, costs fifteen minutes and catches blind spots that no amount of prompt engineering will fix.  
  
The rest of this guide systematises these five practices into a structured, repeatable pipeline with templates, worked examples, and quality controls at every stage.  
  
## Part 1: What You’re Building and How to Scale It  
  
The pipeline has six phases:  
  
1. Foundation — Write the files that tell the model what you’re doing, who you’re writing for, and what standards to follow.  
1. Research — Run one or more research passes on each topic, then (if using multiple passes) reconcile them into one authoritative file per topic.  
1. Synthesis and drafting — Combine the research into a gap analysis and a first draft.  
1. Fact validation — Subject every claim in the draft to a confidence assessment with sources.  
1. Final rewrite and voice editing — Rewrite based on the validation, then check the prose for machine-writing patterns.  
1. Document production — Produce a formatted output file as a separate, final step.  
  
Each phase produces markdown files. The files accumulate into a knowledge base that the model reads before starting each new session. This is what gives the process memory and coherence across multiple conversations.  
  
### How to size the pipeline for your task  
  
Not every document needs three research passes and a formal reconciliation. The full pipeline described here is for work where errors have consequences: board papers, regulatory submissions, published research, competitive analyses that will drive strategy. For lighter work, use a lighter version.  
  
**Full pipeline** (3 passes per topic, formal reconciliation, fact validation, voice editing): Use when the document will be read by people who check sources, when wrong claims have real costs, or when the document anchors a decision worth more than the time you spend on it. Expect 12–20 sessions across one to two weeks for a four-topic project. Cost depends on your model, provider, and access tier. A paid subscription to most AI providers covers it within monthly limits, though you may hit rate limits on heavy research days. If using the API directly, a four-topic full-pipeline project might cost $15-50 at March 2026 pricing — check your provider’s pricing page for current rates, as these change frequently.  
  
**Medium pipeline** (2 passes per topic, light reconciliation, fact validation, one editing pass): Use for internal reports, proposals, or articles where accuracy matters but the audience won’t audit every source. Two passes catch the most obvious gaps and contradictions. Skip the formal five-step reconciliation and instead do a comparison pass: “Read both files. Where do they agree? Where do they disagree? Produce one file with the strongest findings.” Expect 8–12 sessions. Cost roughly halves.  
  
**Light pipeline** (1 pass per topic, no reconciliation, validation optional, one editing pass): Use for blog posts, internal memos, background briefings, or any document where you’re synthesising publicly available information on well-covered topics. One research pass with the same quality constraints (sources, confidence ratings, URLs) still produces better output than an unstructured conversation. Skip reconciliation entirely. Consider skipping formal fact validation if you’re willing to spot-check sources yourself. Expect 4–8 sessions.  
  
### Decision framework for pass count per topic  
  
Three passes when the topic is the centrepiece of your argument, when you expect contradictions between sources, or when primary sources are hard to find. Three passes when getting it wrong would undermine the whole document.  
  
Two passes when public information is reasonably abundant but you want a check against blind spots. Two passes for important-but-not-central topics.  
  
One pass when the topic is background context, when sources are abundant and likely to agree, or when you already have high confidence in readily available information.  
  
You can mix pass counts within a single project. The competitor deep-dive might get three passes while the market overview gets one.  
  
### A warning before you start: source fabrication  
  
AI models can generate plausible-looking URLs, author names, and publication dates that don’t exist. The confidence-rating system in this pipeline reduces the risk (a fabricated source would typically get a “Low” rating), but it does not eliminate it. The research prompts instruct the model to use web search and cite real sources, but you should always click through to the original source URL for any claim that matters to your argument. If the URL leads nowhere, the claim is unsupported regardless of what the research file says.  
  
This risk is highest when the model is summarising rather than directly quoting search results. The multi-pass method helps (a fabricated source is unlikely to appear in all passes), but is not a guarantee. Budget 30 to 60 minutes for manual source-checking on any document over 2,000 words.  
  
## Part 2: Implementation with Claude  
  
Pick a model and stick with it for the duration of a project. Behaviour varies across models within the same family — prose style, verbosity, how extended thinking works, how web search results get synthesised — and switching mid-project introduces inconsistency between passes that the reconciliation step then has to absorb.  
  
### Claude.ai (web or mobile chat)  
  
Use Projects. A Project is a persistent workspace where you upload files and have conversations that share the same context.  
  
Setup steps:  
  
1. Go to claude.ai and click “Projects” in the left sidebar.  
1. Create a new Project. Give it a descriptive name.  
1. Open the Project and click “Project knowledge” to add files. Upload your foundation files (Part 3).  
1. Set the Project’s “Instructions” field. This is the system prompt: text Claude reads at the start of every conversation in the project. Put your writing standards, file conventions, and session behaviour rules here. (Anthropic’s documentation calls this a “system prompt” throughout. In Claude.ai, it lives in the Project Instructions field.)  
1. Start a new conversation within the project for each session. Each conversation inherits the project knowledge and system prompt.  
  
**Managing research passes:** To keep passes independent, do not upload Pass A’s output to the project knowledge before running Pass B. Run all passes, save the outputs locally, then upload them all for the reconciliation conversation.  
  
**Shared knowledge articles:** If you work in a Claude.ai Team or Enterprise plan, you can create shared knowledge articles that persist across projects and team members. Use these for reusable assets: your writing standards file, source quality criteria, or templates you use across multiple projects. In a Team workspace, go to “Team knowledge” to create these.  
  
### Claude Code (command line)  
  
Claude Code runs in a terminal and reads/writes files on your machine.  
  
Setup steps:  
  
1. Create a project directory:  
  
```  
mkdir -p my-research-project/{knowledge,passes,reconciled,drafts,output}  
```  
  
1. Place foundation files in `knowledge/`.  
1. Create a `CLAUDE.md` file in the project root. This is Claude Code’s equivalent of the system prompt. Put your writing standards and conventions here.  
1. For each research pass, run Claude Code pointing at the relevant files:  
  
```  
claude "Read the files in knowledge/ and run Session 1 Pass A.  
  Write output to passes/01-topic-a.md"  
```  
  
1. For reconciliation, point Claude Code at all passes:  
  
```  
claude "Read knowledge/ and passes/01-topic-*.md.  
  Reconcile into reconciled/01-topic.md"  
```  
  
**Advantage:** Full control over file visibility. You can script the entire pipeline with a shell script for repeatable runs.  
  
**Extended thinking:** For reconciliation and fact validation sessions, consider enabling extended thinking if your Claude Code version supports it. These are the steps where reasoning quality matters most. Extended thinking lets Claude work through contradictions and evidence chains more carefully before producing output. In the API, you enable it by setting `thinking.type` to `"enabled"` and providing a `budget_tokens` value.  
  
**Project segmentation:** For large projects, create separate directories for each phase. Only symlink or copy the files Claude needs for each session. This prevents context bloat.  
  
### Claude Cowork (desktop automation)  
  
Cowork reads files from your desktop and writes output files.  
  
Setup steps:  
  
1. Create a folder structure on your desktop matching the pipeline phases.  
1. Point Cowork at the relevant folders for each session.  
1. Give it the session prompt. Cowork will read the files, do the work, and write the output.  
  
**Advantage:** No terminal required. Works with your existing file management.  
  
## Part 3: Foundation Files  
  
Before any research begins, write three to four files. These are the backbone. Claude reads them before every session. Spend real time on these. A vague brief produces vague research.  
  
### File 1: Research Brief (00-research-brief.md)  
  
This is the session plan. It tells Claude what to research, in what order, with what output files.  
  
```  
# 00 — Research Brief  
  
**What this file contains:** The research plan for [your project],  
broken into [N] sessions.  
  
**Key framing decisions:** [What precedents or case studies anchor  
the work. What structural choices you've already made.]  
  
**Open questions before starting:** [What you need to figure out.]  
  
-----  
  
## Context  
  
[Who will read the output. What thesis you're testing. What makes  
this worth researching. Two to four paragraphs.]  
  
## Session plan  
  
### Session 1: [Topic name]  
  
**Output:** `01-topic-name.md`  
**Passes:** [1/2/3 — state why you chose this number]  
  
[List 5-10 specific questions you want answered. Not "research  
competitor X" but "Research competitor X's product line: pricing  
model, market share, key differentiators against our product,  
customer segments, disclosed revenue, recent product launches,  
and any known weaknesses from customer reviews or analyst  
commentary."]  
  
### Session 2: [Topic name]  
  
**Output:** `02-topic-name.md`  
**Passes:** [1/2/3]  
  
[Same specificity. Reference what Session 1 should have  
established.]  
  
[Continue for all sessions...]  
  
## Source priorities  
  
**Primary:** [e.g., company websites, SEC filings, analyst reports,  
named executive interviews, conference transcripts]  
  
**Secondary:** [e.g., industry press, trade publications]  
  
**Avoid:** [e.g., generic listicles, undated blog posts, unnamed  
sources]  
  
Always include URLs and publication dates.  
  
## Decision points  
  
[Where to stop and reassess before continuing. E.g., "After  
Session 1, assess whether the thesis holds. If not, revise  
the strategic framing before continuing."]  
```  
  
**Why this matters:** Without a research brief, each session starts from scratch. Claude doesn’t know what you’ve covered, what you’re building toward, or what quality you expect.  
  
### File 2: Internal Context (00-internal-context.md)  
  
The stuff Claude can’t find online. Your first-hand knowledge.  
  
```  
# 00 — Internal Context  
  
[Write freely. Include:  
- Your role and access  
- Key stakeholders and what motivates them  
- Budget constraints  
- Existing assets the project builds on  
- Internal politics that shape feasibility  
- Anything from experience that wouldn't appear in  
  published sources]  
```  
  
**Why this matters:** The best research in the world fails if it doesn’t account for organisational reality.  
  
### File 3: Strategic Framing (00-strategic-framing.md)  
  
The analytical lens. Write this after some initial thinking or after the first research session.  
  
```  
# 00 — Strategic Framing  
  
**What this file contains:** The analytical lens for the  
[document type].  
  
**Core insight:** [One to two sentences. The idea that makes the  
whole argument work.]  
  
**Open question:** [What evidence would confirm or refute this?]  
  
-----  
  
## [Explain the insight]  
  
[Three to five paragraphs. Concrete examples. Why this framing  
is better than the obvious alternative.]  
  
## How this frames the [document]  
  
[What the document argues given this framing. What failure modes  
it avoids.]  
```  
  
### File 4: Writing Standards  
  
Define voice, banned patterns, and structural rules. This can go in the system prompt (Project Instructions) or as a separate file.  
  
At minimum, ban the obvious AI tells: “delve”, “landscape”, “crucial”, “leverage”, “innovative”, em-dashes, and the habit of starting every paragraph with an adverb. Specify your language variant (British English, American English). Specify your voice: formal, conversational, board-level, technical. Include two or three examples of writing you consider good.  
  
The more specific you are, the less editing you do later.  
  
## Part 4: How Prompts Get Developed  
  
Most guides present prompts as finished artefacts. In practice, prompts are developed iteratively through conversation with Claude. Understanding this process is more valuable than any template.  
  
### The actual sequence from the project that produced this guide  
  
**Step 1: Start with a rough brief.** The first prompt for this project was a consultant-style framework: seven numbered sections, generic instructions like “research the governance structure”, no stated purpose, no hypothesis. It would have produced a Wikipedia-shaped output.  
  
**Step 2: Ask Claude to critique the prompt.** The literal instruction was “Improve this prompt.” Claude identified specific problems: no stated purpose (blog post? white paper? internal proposal?), no hypothesis to test (“tell me about X” vs “test whether X confirms Y”), overlapping sections that would produce redundant output, the most interesting question buried at the end, no depth guidance (500 words or 5,000?).  
  
**Step 3: Discuss the real purpose.** When told this was for an internal white paper proposal, Claude’s response was “That changes everything. The Zurich AI Lab stops being the subject and becomes the precedent.” This reframing shaped the entire project.  
  
**Step 4: Challenge assumptions.** The original plan included Anthropic as a structural research partner. Claude pushed back: “Anthropic is a product company. ‘Technology provider’ and ‘research partner’ are different relationships with different governance requirements. Conflating them weakens the proposal.” This led to repositioning AI companies as vendors throughout the white paper.  
  
**Step 5: Structure for context management.** When asked “How do I split this into sessions so I don’t run out of context?”, Claude designed the session plan with file conventions, summary headers, and the rule that each session should read existing files before starting. It also added the stopping instruction: “If context is getting long, summarise findings so far into the output file and stop.”  
  
**Step 6: Refine through use.** After the first research session produced output, the prompts for subsequent sessions were adjusted. Questions that produced thin results were made more specific. Questions that produced too much generic content were tightened.  
  
### The lesson  
  
Don’t try to write the perfect prompt on the first attempt. Instead:  
  
Write a rough version of what you want. Ask Claude to critique it. Use phrases like “What’s wrong with this prompt?” or “How would you improve this?” Discuss the real purpose. Often the prompt improves once Claude understands the actual audience and the decision the output serves. Challenge your own assumptions. Claude will push back on structural choices if asked. Add context management rules after you understand how long the sessions will be. Revise after the first session based on what worked and what didn’t.  
  
If you use the Anthropic Console (the API workbench), there is a dedicated prompt improver tool that automates some of this iteration. It takes your draft prompt and produces a structured version with XML tags, chain-of-thought instructions, and example formatting. It won’t replace the conversation about purpose and framing (steps 3 and 4), but it’s useful for tightening the mechanics.  
  
### A note on prompt structure  
  
Throughout this guide, the prompt templates use XML tags to separate different types of content: `<instructions>`, `<questions>`, `<constraints>`, `<output_format>`. This is not decorative. Anthropic’s prompting documentation recommends XML tags to help Claude parse complex prompts without misinterpretation (Anthropic 2025b). Wrapping each type of content in its own tag reduces the chance that Claude treats a constraint as a question or confuses output format instructions with research guidance. Include the tags even in Claude.ai. They cost nothing and measurably improve consistency.  
  
## Part 5: The Research Method  
  
### Why multiple passes?  
  
A single research pass follows whatever thread Claude finds first. If the first search result is wrong, narrow, or outdated, the entire session drifts. Multiple independent passes solve this:  
  
Pass A might find a primary source that B missed. Pass B might find a contradictory data point. Pass C might find a more recent source superseding what A found. The reconciliation forces you to resolve contradictions instead of ignoring them. The academic foundation for this approach is the self-consistency method (Wang et al. 2022), which demonstrated that sampling multiple independent reasoning paths and selecting the most consistent answer produces better results than a single pass. Anthropic’s own hallucination reduction guidance recommends the same principle: “Run Claude through the same prompt multiple times and compare the outputs. Inconsistencies across outputs could indicate hallucinations” (Anthropic 2025a).  
  
In the project that produced this guide, reconciliation consistently surfaced value. For one topic, Pass A found an external ranking that explained an institution’s motivation. Pass B identified that a key partner was not actually an expert in the claimed field. Pass C found infrastructure details the others missed. No single pass would have produced the same quality.  
  
### The independence rule  
  
Each pass must be independent. Pass B must not see Pass A’s output.  
  
In Claude.ai Projects: run each pass in a separate conversation. Don’t upload pass outputs to the project knowledge until reconciliation.  
  
In Claude Code: run each pass in a separate invocation, pointing only at foundation files and previously reconciled research.  
  
### The correlated sources problem  
  
This is the structural weakness of the multi-pass method and you need to understand it. Independence of passes does not guarantee independence of sources. If the same incorrect article ranks first in web search results, all three passes will find it and cite it. Reconciliation will treat this as “established” (multiple passes agree with compatible sources), but the underlying evidence is a single source.  
  
Be alert to this during reconciliation. Ask whether the sources are genuinely independent or whether multiple passes are citing the same underlying report, press release, or dataset. Three citations that all trace back to one press release are one source, not three.  
  
For high-stakes topics, consider varying query formulations between passes. Pass A might research “Datadog pricing model enterprise” while Pass B tries “Datadog contract structure customer complaints”. Different queries surface different parts of the search index.  
  
### The research pass prompt (template)  
  
```  
<instructions>  
# Session [N], Pass [A/B/C]: [Topic Name]  
  
Read all files in the project knowledge base. List them. Read  
the summary headers of any existing research files before  
starting.  
</instructions>  
  
<task>  
Research [specific topic]. Answer the following questions:  
</task>  
  
<questions>  
1. [Specific question]  
2. [Specific question]  
3. [Specific question]  
[etc.]  
</questions>  
  
<constraints>  
## Research standards  
  
- Use web search to find primary and secondary sources.  
- For every source you find, quote the specific passage that  
  supports the claim before summarising it. This grounds  
  your findings in the actual text and reduces the risk of  
  hallucination (Anthropic 2025a).  
- Every claim needs a source: URL, author, publication, date.  
- Every claim needs a confidence rating:  
  - **High:** Multiple corroborating sources or official/primary  
    source.  
  - **Medium:** Single credible source or reasonable inference  
    from strong evidence.  
  - **Low:** Unverified, inferred, or based on secondary  
    reporting only.  
- If you cannot find credible evidence, say "I could not find  
  public evidence for this." This is a better answer than a  
  plausible guess. Do not invent or infer sources.  
- If evidence is thin, flag it explicitly.  
- Depth over breadth. If running out of context, it's better to  
  cover three questions thoroughly than six superficially.  
</constraints>  
  
<example_output>  
## Question 1: Revenue and growth  
  
Datadog reported $2.13 billion in FY24 revenue.  
  
> "Total revenue was $2,128.3 million for the fiscal year ended  
> December 31, 2024, an increase of 26% year-over-year."  
> — Datadog 10-K filing, February 2025  
  
**Source:** https://[URL to SEC filing]  
**Confidence:** High (primary source, official filing)  
  
Revenue breakdown by product line is not disclosed in the 10-K.  
I could not find public evidence for a segment-level breakdown.  
</example_output>  
  
<example_bad_output>  
## What bad output looks like  
  
**No source:**  
Datadog's enterprise customers typically pay $200K-$500K annually.  
**Confidence:** High  
  
This is unusable. No URL, no publication, no date. The confidence  
rating is unjustified — where did "High" come from?  
  
**Vague sourcing:**  
Datadog has been growing rapidly according to various industry  
reports.  
**Source:** https://www.google.com/search?q=datadog+revenue  
**Confidence:** Medium  
  
A search URL is not a source. "Various industry reports" names  
nothing. This claim cannot be verified or traced.  
  
**Confidence without reasoning:**  
Datadog's churn rate is approximately 5%.  
**Source:** Reddit thread, r/devops, undated  
**Confidence:** Medium  
  
An undated Reddit thread is not a Medium-confidence source. This  
should be Low at best, with a flag that the claim is unverified.  
</example_bad_output>  
  
<output_format>  
Write as `[NN]-[topic]-[a/b/c].md`.  
  
Open with a three-line summary:  
1. What this file contains  
2. Key findings  
3. Open questions  
  
Organise by question, with sources and confidence inline.  
  
End with a sources table: source name, date, URL, primary/  
secondary classification.  
</output_format>  
```  
  
The `<example_output>` section is new in this version. It shows Claude the exact format you want: a claim, the quoted passage from the source, the URL, and the confidence rating. Anthropic’s prompting documentation identifies examples as one of the most reliable ways to steer output format, tone, and structure (Anthropic 2025b). A few lines of example output measurably improve consistency across passes.  
  
The `<example_bad_output>` section works the same way in reverse. Showing Claude what failure looks like — a missing source, a search URL passed off as a citation, a confidence rating that doesn’t match the evidence — is as effective as showing it what success looks like. Anthropic’s prompting documentation confirms that Claude 4.x models pay close attention to both positive and negative examples (Anthropic 2025b).  
  
### Cost note  
  
The multi-pass method roughly triples the research cost (in tokens and time) compared to single-pass research. At March 2026 pricing (Sonnet 4.6 at $3/M input, $15/M output), a three-pass research session costs roughly $2-5 via the API depending on web search volume and output length. Check Anthropic’s pricing page for current rates. For a four-topic project with three passes each, expect 12 research sessions plus 4 reconciliation sessions before you start drafting. For the same project with two passes, expect 8 research sessions plus 4 reconciliations. For single-pass, 4 research sessions and no reconciliation.  
  
Budget accordingly. For the light and medium pipeline variants described in Part 1, the savings are proportional.  
  
## Part 6: Reconciliation  
  
This is where the multi-pass method earns its keep. The reconciliation is not a merge. It is critical analysis. Skip this section entirely if you are running single-pass research.  
  
### The reconciliation prompt (template)  
  
```  
<instructions>  
# Session [N] Reconciliation: [Topic Name]  
  
Read the research passes:  
- [NN]-[topic]-a.md  
- [NN]-[topic]-b.md  
[- [NN]-[topic]-c.md if three passes]  
  
Produce a single reconciled file: [NN]-[topic].md  
</instructions>  
  
<task>  
## Reconciliation method  
  
Before writing the reconciled output, work through the  
following steps. For steps 1-3, reason through each item  
in <thinking> tags before recording your conclusion.  
  
### 1. Corroboration analysis  
  
For each key finding, extract the relevant passage from  
each pass file that addresses it. Quote the specific claims  
from each pass before assessing agreement.  
  
Which findings appear in two or more passes? These are your  
highest-confidence claims. Check whether sources are genuinely  
independent (the same underlying source cited by multiple passes  
doesn't count as corroboration). Three citations of the same  
press release are one source, not three.  
  
When resolving disagreements, weight by confidence. A single  
High-confidence primary source outweighs two Medium-confidence  
secondary reports on the same underlying data. Recent work on  
confidence-informed self-consistency (Taubenfeld et al. 2025)  
confirms that weighting by confidence produces better results  
than treating all paths equally.  
  
### 2. Contradiction resolution  
  
Where do passes disagree? For each contradiction:  
- State what each pass claims, quoting the specific text.  
- Identify which source is more authoritative (primary over  
  secondary, named over unnamed, recent over old).  
- Resolve with explicit reasoning.  
- If unresolvable, flag as an open question.  
  
### 3. Unique findings assessment  
  
What did only one pass find? For each:  
- Strong unique source: include.  
- Weak source or unsupported inference: flag or cut.  
- Don't discard just because it's unique. A single primary  
  source beats three secondary ones.  
  
### 4. Source quality audit  
  
Compile all sources. Remove duplicates. Flag undated, unnamed,  
rehashed, or potentially outdated sources. The reconciled file  
should have a cleaner source base than any individual pass.  
  
### 5. Gap identification  
  
What did none of the passes find? Confirmed gaps are  
valuable: they tell the document what cannot be established  
from public sources.  
</task>  
  
<output_format>  
Same three-line opening summary. Every claim carries confidence  
and source. Where evidence is weak, prefer cutting the claim to  
including it with Low confidence.  
</output_format>  
```  
  
### What good reconciliation looks like  
  
Suppose three passes researched Datadog’s revenue:  
  
**Pass A:** “Datadog reported $2.13B in FY24 revenue (10-K filing, Feb 2025). High confidence.”  
  
**Pass B:** “Datadog’s annual revenue exceeded $2 billion in 2024 (TechCrunch article, March 2025). Medium confidence.”  
  
**Pass C:** “Datadog revenue was $2.1B in 2024, growing 26% year-over-year (analyst estimate, Morgan Stanley note, Jan 2025). Medium confidence.”  
  
**Bad reconciliation** (a merge):  
  
“Datadog reported revenue of approximately $2.1-2.13B in FY24, growing around 26% year-over-year, according to multiple sources including their 10-K filing, TechCrunch, and Morgan Stanley.”  
  
This looks thorough but does no analytical work. It doesn’t note that Pass B’s source is secondary (TechCrunch reporting on the same filing Pass A found directly). It doesn’t check whether Pass C’s “26% growth” is consistent with the absolute number. It treats three citations as corroboration when two of them derive from the same underlying source.  
  
**Good reconciliation:**  
  
“Datadog reported $2.13B in FY24 revenue (10-K filing, February 2025). High confidence: primary source, corroborated by Pass A and Pass B (though Pass B’s TechCrunch source is secondary reporting on the same filing, not independent corroboration). Pass C cites 26% YoY growth from a Morgan Stanley estimate published before the 10-K. Checking: $2.13B vs. FY23 revenue of $1.68B (also from 10-K) gives 26.8% growth, consistent with the analyst estimate. The growth figure is verified. Note: the Morgan Stanley note predates the filing and rounds down; the 10-K is authoritative.”  
  
The good version traces each source, flags dependent sources, cross-checks the arithmetic, and distinguishes between primary evidence and reporting on that evidence. This is the work that makes reconciliation worth doing.  
  
**Extended thinking note:** If you’re using Claude Code or the API with extended thinking enabled, the reconciliation step benefits most. The reasoning required to resolve contradictions and assess source independence is exactly the kind of multi-step analysis that extended thinking handles well.  
  
After reconciliation, remove the individual pass files from the project knowledge. Only the reconciled file remains. Later sessions should only see authoritative versions.  
  
## Part 7: Synthesis and Drafting (Single Pass)  
  
After research is complete, the remaining sessions run once each.  
  
### Gap analysis prompt  
  
```  
<instructions>  
# Session [N]: Gap Analysis  
  
Read all reconciled research files: [list them].  
</instructions>  
  
<task>  
Synthesise findings into a gap analysis structured around the  
decisions the document must make.  
  
Before writing, think step by step in <thinking> tags about:  
- What the evidence collectively supports  
- Where it contradicts itself across topics  
- What transfers from precedents and what doesn't  
  
Then write the gap analysis covering:  
- What the evidence supports strongly  
- Where evidence is thin or absent  
- What transfers from precedents and what doesn't  
- What structural questions remain  
  
End with a numbered list of open questions, categorised as:  
(a) Answerable through further research  
(b) Requires internal conversations or primary data  
</task>  
  
<output_format>  
Output: [NN]-gap-analysis.md  
</output_format>  
```  
  
### Draft prompt  
  
```  
<instructions>  
# Session [N]: Draft  
  
Read all files [00 through gap analysis]. Place the research  
files and foundation files at the top of context (Anthropic  
2025c). Read them in full before beginning the draft.  
</instructions>  
  
<task>  
Draft the [document type].  
</task>  
  
<structure>  
[Specify section structure. Be explicit about what each section  
contains and roughly how long.]  
</structure>  
  
<constraints>  
- Target: [X] to [Y] words.  
- Every claim must trace to the research files. If unsupported,  
  cut it.  
- If evidence is weak, say so in the text. Do not smooth over  
  uncertainty.  
- Apply writing standards from the project knowledge base.  
- [Tone guidance for your audience.]  
</constraints>  
  
<output_format>  
Output: [NN]-draft.md  
</output_format>  
```  
  
## Part 8: Fact Validation  
  
This is the step most people skip. After the first draft, subject every factual claim to independent verification.  
  
### What this step does  
  
The draft was written by the same system that did the research. It has the same blind spots, the same tendency to present inferences as facts. In the project that produced this guide, the validation step caught: claims that drifted from “Medium confidence” in research to “stated as fact” in the draft, numbers rounded in a misleading direction, two claims that couldn’t be traced to any source at all, and an industry estimate cited without the caveat that it was modelled, not measured.  
  
None of these were fabricated. They were the normal entropy of information passing through multiple processing steps. Validation catches drift and inflation well.  
  
### What this step does not do  
  
Be clear-eyed about the limits. This step checks the draft against the research files. If a source was fabricated during the research phase, validation will “confirm” it because it exists in the research files.  
  
More subtly, running validation through the same model, even in a fresh conversation, is not the same as independent verification. LLMs exhibit self-preference bias: they score their own outputs higher than equivalent text from other sources, and this bias correlates linearly with the model’s ability to recognise its own output (Panickssery et al. 2024). A fresh conversation reduces conversational momentum (Claude won’t “remember” writing the draft), but the same model still has the same training data, the same tendencies, and the same blind spots.  
  
Same-model validation is a useful check for catching drift and inflation. It is not a substitute for human source-checking. For any claim where the original source matters, you need to open the URL and confirm the claim is there. For high-stakes documents (board papers, published research, regulatory submissions), consider running fact validation through a different model entirely: Gemini, GPT, or another provider. Cross-family verification is more effective than self-verification because different models have different training data and different failure modes.  
  
### The fact validation prompt  
  
```  
<instructions>  
# Fact Validation  
  
Read the draft: [NN]-draft.md  
Read all research files: [list them]  
</instructions>  
  
<task>  
Go through the draft paragraph by paragraph. For every factual  
claim (not opinions, not framing — facts), produce an entry:  
  
| # | Claim (as stated in draft) | Source (original, not  
research file) | Research file ref | Confidence | Status |  
Notes |  
  
Before assessing each claim, extract the relevant quote from  
the research file that supports it. If no relevant passage  
exists in any research file, mark as UNSOURCED immediately.  
</task>  
  
<confidence_levels>  
- **HIGH:** Multiple corroborating primary sources.  
- **MEDIUM:** Single credible source or strong inference.  
- **LOW:** Unverified or outdated.  
- **UNVERIFIED:** Cannot find a source in research files.  
</confidence_levels>  
  
<status_definitions>  
- **VERIFIED:** Claim matches source accurately.  
- **INACCURATE:** Claim misstates the source.  
- **INFLATED:** Broadly correct but overstated.  
- **OUTDATED:** Source old enough that claim may not hold.  
- **UNSOURCED:** No source found.  
</status_definitions>  
  
<output_format>  
## After the table  
  
Summary: total claims, breakdown by status, claims to cut or  
correct.  
  
## Then produce  
  
A corrected draft: [NN]-draft-validated.md  
  
In the corrected draft:  
- Fix inaccurate claims.  
- Qualify inflated claims.  
- Remove or flag unsourced claims.  
- Downgrade LOW-confidence claims to hedged language.  
</output_format>  
```  
  
### How to run it  
  
Run this in a new conversation with the draft and all research files. Starting fresh forces Claude to re-read rather than relying on context from writing the draft.  
  
For documents over 3,000 words, split the validation by section. One conversation per major section. This keeps Claude focused and prevents it getting sloppy toward the end.  
  
## Part 9: Final Rewrite and Voice Editing  
  
The validated draft has correct facts but may read like a patched document. The rewrite produces a clean version and strips machine-writing patterns in a single pass.  
  
### The voice editing problem  
  
A document that reads like AI output will be dismissed as AI output, regardless of how good the research is. Machine-writing patterns operate at three levels:  
  
**Structural patterns** (most detectable): Sentence length uniformity, paragraph length uniformity, epistemic flatness (every claim stated with equal confidence), register consistency (the same formality level from start to finish). These are what automated classifiers catch.  
  
**Language patterns:** Hedging phrases (“It’s worth noting”), transition words (“Furthermore”, “Moreover”), significance inflation (“crucial”, “pivotal”), and vocabulary choices that cluster in AI training data.  
  
**Voice absence** (the real problem): Clean but lifeless text fails as obviously as text full of AI tells. The hallmarks: emotional flatness, opinion absence, lack of specific detail, temporal flattening (everything in a vague present tense).  
  
**A note on model versions:** Claude’s newer models (4.x series) produce more natural, less verbose output than earlier versions. If you’re using a current model, the rewrite may catch fewer patterns than expected. That’s fine. Check, but don’t force changes where the prose already reads naturally.  
  
### The stet ruleset  
  
Stet is a structured editing ruleset that identifies and removes patterns that betray machine authorship. The full ruleset is available at github.com/Cronan/claude-code-prompts/tree/main/skills/stet. It can be used as a Claude Code skill, a project knowledge file, or a standalone editing prompt.  
  
**Installation:** In Claude Code, clone or download the SKILL.md file into your skills directory and reference it in your CLAUDE.md. In Claude.ai Projects, upload SKILL.md to your Project Knowledge as `stet.md`.  
  
### The rewrite prompt  
  
```  
<instructions>  
# Final Rewrite  
  
Read: [NN]-draft-validated.md  
Read: writing standards file  
Read: stet.md (voice editing ruleset, if using)  
</instructions>  
  
<task>  
Rewrite from the validated draft. This is not an edit. It is a  
rewrite that preserves all factual content while producing a  
document that reads as though one person wrote it in one sitting.  
</task>  
  
<constraints>  
1. Every fact from the validated draft must appear.  
2. Apply writing standards. Strip AI-writing patterns.  
3. Check for structural tells (sentence length uniformity,  
   paragraph length uniformity, epistemic flatness), language  
   tells (hedging phrases, transition words, significance  
   inflation), and voice absence (emotional flatness, opinion  
   absence, lack of specific detail).  
4. Voice: [describe, e.g. "a senior professional writing for  
   peers, not a consultant pitching to a client"].  
5. Vary sentence and paragraph length deliberately.  
6. Write the executive summary last.  
7. Target: [X] to [Y] words.  
8. Leave one or two minor imperfections. Do not overcorrect.  
   Applying these rules uniformly is itself a detectable pattern.  
</constraints>  
  
<output_format>  
Output: [NN]-final.md  
</output_format>  
```  
  
## Part 10: Document Production  
  
This is a separate, final step. All research, writing, and editing is done in markdown. The formatted document is produced only when the content is stable.  
  
### Why markdown first  
  
Markdown is lightweight, version-controllable, and doesn’t fight you on formatting. Writing in Word while iterating on content means fighting with styles, pagination, and formatting every time you make a structural change. Write in markdown. Convert once at the end.  
  
### The Word document prompt  
  
```  
<instructions>  
# Produce Word Document  
  
Read [NN]-final.md  
  
Read the docx skill file at /mnt/skills/public/docx/SKILL.md  
(Claude Code) or follow standard docx creation practices.  
  
Produce a formatted Word document: [NN]-output.docx  
</instructions>  
  
<formatting>  
- Page size: A4 (or US Letter if preferred)  
- Font: Arial 11pt body, 14pt section headings, 16pt title  
- Margins: 1 inch all sides  
- Line spacing: 1.15  
- Page numbers in footer, centred  
- Title page with:  
  - Document title  
  - Author name and role  
  - Date  
  - Classification (e.g., "Internal / Confidential")  
- Section headings styled as Heading 1, Heading 2, etc.  
- No table of contents unless the document exceeds 15 pages  
- No bullet points in body text (the document uses prose)  
</formatting>  
  
<constraints>  
Transfer the full content of [NN]-final.md into the document.  
Do not edit, add, or remove content. This is a formatting  
step, not a writing step.  
</constraints>  
```  
  
In Claude.ai, Claude will use its computer tools to generate the .docx file, which you can download. In Claude Code, it will write the file directly to your filesystem.  
  
## Part 11: Context Management  
  
Context is the single most important constraint when working with Claude across multiple sessions.  
  
### What context is  
  
Claude’s context window is the total amount of text it can “see” at once: the system prompt, project knowledge files, conversation history, and any files it reads during the session. Context window sizes vary by model and access tier. In Claude.ai on a paid plan, the default is 200,000 tokens (roughly 150,000 words). Claude Opus 4.6 and Sonnet 4.6 support up to 1 million tokens natively via the API. Sonnet 4.5 and Sonnet 4 support 1 million tokens with a beta header for eligible API users.  
  
But capacity is not the binding constraint. Quality degrades well before you hit the token limit. Anthropic’s context engineering guidance describes this as a function of attention mechanics: as the context window fills, the model’s ability to attend to specific passages weakens, particularly for information in the middle of the window. Think of it as signal-to-noise ratio. Every token of context that isn’t relevant to the current task dilutes attention on the tokens that are. This is why the practical advice throughout this guide — keep reconciled files to 1,000-2,000 words, use three-line summaries, don’t load files you don’t need — matters even when you have 200K or 1M tokens available. You’re not managing capacity. You’re managing attention.  
  
The practical advice that follows applies regardless of window size, because quality tends to degrade before you hit the hard limit.  
  
### Two kinds of context  
  
**Project knowledge** (Claude.ai) or **foundation files** (Claude Code) are loaded at the start of every conversation. They persist. Your research brief, internal context, and writing standards are always available. You don’t “run out” of project knowledge mid-conversation.  
  
**Conversation context** is everything that happens within a single chat session: your prompts, Claude’s responses, any files read during the conversation, and any web search results. This is the real constraint. As the conversation gets long, earlier content may be compressed or summarised to make room for new content. In Claude Code, this compression (called compaction) is explicit and configurable. In Claude.ai, it happens automatically in very long conversations.  
  
The practical implication: keep each session focused on one task. Don’t combine research and drafting in the same conversation. Don’t run all passes in one chat. Start a fresh conversation for each session in the pipeline.  
  
### How to avoid running out of context  
  
**Keep research files concise.** The reconciled output for each topic should be 1,000 to 2,000 words of distilled findings, not 5,000 words of raw notes. Cut weak claims. Cut redundant sourcing. Keep the strong findings with their sources and confidence ratings.  
  
**Use the three-line summary convention.** Every file opens with three lines: what it contains, key findings, and open questions. When Claude reads a file, it gets the most important information first. If context is tight, Claude can read summaries without loading full files.  
  
**Don’t load everything at once.** The draft session needs to reference multiple research files. If those files are concise, they’ll fit. If any file ballooned, trim it before starting the draft session.  
  
**Use the stopping rule.** Include this in your system prompt:  
  
```  
If context is getting long: summarise findings so far into  
the output file and stop. Do not sacrifice depth for  
completeness. It is better to produce thorough research on  
three questions than shallow coverage of six. If necessary,  
produce a continuation prompt for the next session.  
```  
  
**Split long sessions.** If the fact validation session is trying to check 50 claims across a 4,000-word document, split it into two sessions: one for the first half, one for the second.  
  
**Start fresh for validation.** Always run fact validation in a new conversation. If you run it in the same conversation where you wrote the draft, Claude will have contextual momentum toward confirming what it just wrote.  
  
### Approximate token budgets  
  
For a four-topic project at the draft stage, your context load might look like this:  
  
Foundation files (research brief, internal context, strategic framing, writing standards): roughly 3,000-5,000 words or 4,000-7,000 tokens.  
  
Four reconciled research files at 1,500 words each: roughly 6,000 words or 8,000 tokens.  
  
Gap analysis: roughly 1,500 words or 2,000 tokens.  
  
Total before the conversation starts: roughly 14,000-17,000 tokens. This leaves ample room in a 200K context window. The risk isn’t the files. It’s a conversation that runs long because Claude produces verbose research output and you continue in the same session.  
  
### File versioning  
  
A pipeline that produces 15 or more files across two weeks needs a naming convention. The simplest approach: if you need to revise a reconciled file after new information surfaces, create `01-datadog-v2.md` and remove `01-datadog.md` from the project knowledge. Don’t pre-emptively version files.  
  
The draft and rewrite phases already use different filenames for each stage (`06-draft.md`, `06-draft-validated.md`, `07-final.md`), so versioning is built in.  
  
If you’re using Claude Code with git, commit after each session. This gives you full version history without cluttering filenames.  
  
## Part 12: Worked Example — Software Product Competitor Analysis  
  
This section walks through the complete pipeline for a competitor analysis. Every prompt is written out in full. This is a full-pipeline example (three passes for the primary competitor, two for secondary competitors, one for market context).  
  
### The scenario  
  
You’re the Head of Product Marketing at a mid-size B2B SaaS company that sells an observability platform. Your CEO has asked for a competitive analysis that the leadership team can use to make pricing and positioning decisions. The main competitors are Datadog, New Relic, Dynatrace, and Grafana Labs. The document needs to be credible enough that the VP of Sales and the CFO will trust its conclusions.  
  
### Foundation file 1: Research Brief  
  
```  
# 00 — Research Brief  
  
**What this file contains:** Research plan for a competitive  
analysis of the B2B observability platform market, covering  
four primary competitors and producing a strategic positioning  
document.  
  
**Key framing decisions:** This is not a feature comparison  
matrix. It is a strategic document that answers: where are we  
strong, where are we vulnerable, and what should we do about  
pricing and positioning in the next 12 months?  
  
**Open questions:** Whether our pricing is a vulnerability or  
an advantage depends on data we don't yet have about  
competitor contract structures.  
  
-----  
  
## Context  
  
We sell an observability platform to mid-market and enterprise  
engineering teams. ACV range is $50K-$500K. We compete  
primarily against Datadog, New Relic, Dynatrace, and Grafana  
Labs (with its commercial Grafana Cloud offering).  
  
The CEO wants this analysis to inform three decisions:  
1. Whether to raise prices on the enterprise tier.  
2. Whether to invest in a free/open-source tier to compete  
   with Grafana.  
3. How to position against Datadog in enterprise deals we're  
   losing.  
  
The first readers are the CEO, CFO, and VP of Sales. They  
want numbers, not narratives. Where numbers aren't available,  
they want honest ranges with sourced estimates.  
  
## Session plan  
  
### Session 1: Datadog deep dive  
  
**Output:** `01-datadog.md`  
**Passes:** 3 (primary competitor, centrepiece of the analysis)  
  
Research Datadog as the primary competitor. Cover:  
1. Revenue and growth. Latest quarterly/annual results.  
   Revenue breakdown by product line if disclosed. Customer  
   count and ACV if available.  
2. Pricing model. Published pricing. How enterprise pricing  
   works in practice (from customer reports, analyst  
   commentary, or Gartner/Forrester reviews). Known discounting  
   patterns. Usage-based vs. seat-based mix.  
3. Product strategy. Recent launches and roadmap signals.  
   Acquisitions. Where they're investing. What analyst  
   reports say about product strengths and gaps.  
4. Market position. Gartner Magic Quadrant and Forrester Wave  
   placement. Win rates if available from any source. Key  
   customer segments.  
5. Known weaknesses. Customer complaints (G2, Gartner Peer  
   Insights). Pricing backlash. Churn data if available.  
   Technical limitations cited in reviews.  
6. Sales motion. Enterprise sales team structure if known.  
   Partner ecosystem. How they compete in deals (discounting,  
   bundling, multi-year commits).  
  
### Session 2: New Relic and Dynatrace  
  
**Output:** `02-new-relic-dynatrace.md`  
**Passes:** 2 (secondary competitors, important but not central)  
  
Research New Relic and Dynatrace. For each, cover the same  
six areas as Session 1 but at lower depth. Focus on what  
differentiates them from Datadog and from us.  
  
Additional questions for New Relic:  
- Impact of the consumption-based pricing pivot. Has it  
  helped or hurt?  
- Current financial health (they've had rough quarters).  
  
Additional questions for Dynatrace:  
- The AI angle (Davis AI). How real is it? Customer reception.  
- Enterprise penetration vs. Datadog.  
  
### Session 3: Grafana Labs and open-source dynamics  
  
**Output:** `03-grafana.md`  
**Passes:** 2 (different kind of competitor, needs two angles)  
  
Research Grafana Labs. Different kind of competitor (open-source  
core with commercial cloud offering) so the questions differ:  
1. Revenue and funding. Latest disclosed revenue or funding  
   round valuation. Growth rate if available.  
2. Open-source strategy. What's free vs. paid. How the  
   open-source community feeds the commercial business.  
3. Grafana Cloud. Pricing, features, enterprise capabilities.  
   How it competes with full-stack platforms like Datadog.  
4. Our specific exposure. Where are customers using Grafana  
   alongside or instead of our product? Is the threat at the  
   bottom of the market (free tier displacing paid) or at the  
   top (Grafana Cloud winning enterprise deals)?  
5. Community and ecosystem. Plugin ecosystem, contributor  
   base, integration breadth.  
  
### Session 4: Market dynamics and pricing intelligence  
  
**Output:** `04-market-pricing.md`  
**Passes:** 1 (background context, well-covered publicly)  
  
Research the broader observability market and pricing dynamics:  
1. Market size and growth. Gartner, IDC, or Forrester market  
   size estimates. Growth rate. Where the growth is coming from.  
2. Pricing trends. Is the market moving toward consumption-  
   based, seat-based, or hybrid? What are customers pushing  
   back on?  
3. Enterprise buying behaviour. Who makes the decision (VP  
   Eng, CTO, platform team)? What matters most in evaluation  
   (price, features, ecosystem, support)?  
4. Analyst commentary on the competitive landscape. Recent  
   Gartner or Forrester assessments.  
5. M&A activity and its implications.  
  
## Source priorities  
  
**Primary:** Company earnings calls and 10-K/10-Q filings,  
Gartner/Forrester published research, company pricing pages,  
named analyst interviews or reports.  
  
**Secondary:** G2 and Gartner Peer Insights reviews  
(aggregate trends, not individual reviews), trade press  
(InfoWorld, The New Stack, TechCrunch for funding), customer  
case studies on company websites.  
  
**Avoid:** Vendor-sponsored content disguised as analysis,  
undated blog posts, generic "top 10 observability tools"  
listicles.  
  
## Decision points  
  
After Session 1, assess whether Datadog is the right primary  
competitor to anchor the analysis. If the research shows  
we're losing more deals to Grafana or Dynatrace, adjust.  
  
After Session 4, the pricing question should be answerable.  
If evidence is too thin for a pricing recommendation, say so.  
```  
  
### Foundation file 2: Internal Context  
  
```  
# 00 — Internal Context  
  
Our ARR is $45M, growing 35% YoY. Average ACV is $120K. We  
have approximately 400 customers, mostly in the $50K-$300K  
range. We have 12 enterprise customers above $500K ACV.  
  
We lose about 30% of competitive deals to Datadog. We don't  
have good data on why.  
  
[The full file continues with pricing structure, internal  
stakeholder positions, and funding context. See the Internal  
Context template in Part 3 for the format.]  
```  
  
### Foundation file 3: Strategic Framing  
  
```  
# 00 — Strategic Framing  
  
**Core insight:** The observability market is bifurcating.  
Enterprise buyers want consolidation (one platform, one vendor,  
one contract). Developer-led buyers want composability  
(best-of-breed tools, open source, plug together). Datadog is  
winning the first motion. Grafana is winning the second. We're  
in the middle, which is the worst place to be.  
  
**Open question:** Can we find evidence that being "in the  
middle" is actually defensible for the mid-market, or do we  
need to pick a lane?  
  
[The full framing analysis follows the template in Part 3.]  
```  
  
### Running the research passes  
  
For Session 1 (Datadog), run three passes with the research pass prompt from Part 5, substituting the Session 1 questions. Each pass runs in a separate conversation.  
  
**Pass A prompt** (the full prompt for one pass):  
  
```  
<instructions>  
# Session 1, Pass A: Datadog Deep Dive  
  
Read all files in the project knowledge base. List them. Read  
the summary headers of any existing research files before  
starting.  
</instructions>  
  
<task>  
Research Datadog as the primary competitor to our observability  
platform. Answer the following questions:  
</task>  
  
<questions>  
1. Revenue and growth. Latest quarterly/annual results. Revenue  
   breakdown by product line if disclosed. Customer count and  
   ACV if available.  
2. Pricing model. Published pricing. How enterprise pricing  
   works in practice (from customer reports, analyst commentary,  
   or Gartner/Forrester reviews). Known discounting patterns.  
   Usage-based vs. seat-based mix.  
3. Product strategy. Recent launches and roadmap signals.  
   Acquisitions. Where they're investing. What analyst reports  
   say about product strengths and gaps.  
4. Market position. Gartner Magic Quadrant and Forrester Wave  
   placement. Win rates if available from any source. Key  
   customer segments.  
5. Known weaknesses. Customer complaints (G2, Gartner Peer  
   Insights). Pricing backlash. Churn data if available.  
   Technical limitations cited in reviews.  
6. Sales motion. Enterprise sales team structure if known.  
   Partner ecosystem. How they compete in deals.  
</questions>  
  
<constraints>  
- Use web search for primary and secondary sources.  
- For every source you find, quote the specific passage that  
  supports the claim before summarising it.  
- Every claim needs a source: URL, author, publication, date.  
- Every claim needs a confidence rating:  
  - **High:** Multiple corroborating sources or official source  
    (earnings call, 10-K, company pricing page).  
  - **Medium:** Single credible source (named analyst,  
    established trade press) or reasonable inference.  
  - **Low:** Unverified, inferred, or based on secondary  
    reporting only.  
- If you cannot find credible evidence, say "I could not find  
  public evidence for this." Do not invent or infer sources.  
- Depth over breadth. If running out of context, cover revenue/  
  pricing/weaknesses thoroughly and note what's incomplete.  
</constraints>  
  
<example_output>  
## Question 1: Revenue and growth  
  
Datadog reported $2.13 billion in FY24 revenue.  
  
> "Total revenue was $2,128.3 million for the fiscal year ended  
> December 31, 2024, an increase of 26% year-over-year."  
> — Datadog 10-K filing, February 2025  
  
**Source:** https://[SEC filing URL]  
**Confidence:** High (primary source, official filing)  
</example_output>  
  
<output_format>  
Write as `01-datadog-a.md`.  
  
Open with a three-line summary:  
1. What this file contains  
2. Key findings  
3. Open questions  
  
Organise by question, with sources and confidence inline.  
  
End with a sources table.  
</output_format>  
```  
  
Passes B and C use the identical prompt (changing only the suffix to `-b` and `-c`). The point is not to vary the prompt. It’s that independent execution produces different search paths and different findings. Consider varying the query approach between passes: Pass B might emphasise customer reviews and analyst commentary, Pass C might focus on financial filings and pricing pages. This partially addresses the correlated sources problem.  
  
### Reconciliation  
  
After all three Datadog passes are complete, run the reconciliation prompt from Part 6, pointing it at the three pass files.  
  
### Remaining sessions  
  
For Sessions 2 and 3 (two passes each), run the same structure with two passes and a lighter reconciliation: “Read both files. Where do they agree? Where do they disagree? Produce one file with the strongest findings.”  
  
For Session 4 (one pass), run a single research pass. No reconciliation needed.  
  
### Gap analysis, draft, validation, rewrite, and production  
  
Follow the prompts from Parts 7, 8, 9, and 10, substituting the relevant filenames. The gap analysis for this example should address the three CEO decisions directly. The draft should take a position on each. The validation should check every revenue figure, pricing claim, and market share assertion against the research files.  
  
### Total session count for this example  
  
Session 1 (Datadog): 3 passes + 1 reconciliation = 4 sessions  
Session 2 (New Relic/Dynatrace): 2 passes + 1 reconciliation = 3 sessions  
Session 3 (Grafana): 2 passes + 1 reconciliation = 3 sessions  
Session 4 (Market): 1 pass = 1 session  
Gap analysis: 1 session  
Draft: 1 session  
Fact validation: 1-2 sessions  
Rewrite: 1 session  
Document production: 1 session  
  
Total: 16-17 sessions across one to two weeks.  
  
## Part 13: Lessons Learned  
  
**The foundation files matter more than the prompts.** A clear research brief with a good framing document produces good research even with mediocre prompts. A brilliant prompt template can’t rescue a vague brief.  
  
**Reconciliation is where the value lives.** The multi-pass method is only as good as the reconciliation. A lazy reconciliation that combines all three passes produces a long, unfocused file. A rigorous one that resolves contradictions and cuts weak claims produces something you can build on.  
  
**Same-model fact validation catches drift, not fabrication.** The validation step reliably catches claims that inflated from “Medium confidence” to “stated as fact” and numbers that rounded in a misleading direction. It does not reliably catch fabricated sources, because the same model tends to confirm its own prior output (Panickssery et al. 2024). Manual source-checking is still your responsibility for claims that matter. For high-stakes documents, cross-model verification is worth the extra cost.  
  
**Voice editing is not cosmetic.** A document that reads like AI output gets treated as AI output. But newer Claude models produce more natural prose. Check for machine-writing patterns, but don’t force changes where the output already reads well. Over-editing is its own kind of artificiality.  
  
**The hardest part is knowing when to stop researching.** There is always one more source. The session boundaries in the research brief exist to prevent this. Sometimes thin results mean the information doesn’t exist publicly. Running additional passes won’t conjure it. Note the gap and move on.  
  
**If the evidence doesn’t support your thesis, change the thesis.** This is the second hardest part. After two sessions of research, you’ve invested time and the foundation files are built around your original framing. The sunk cost makes it tempting to keep looking for confirming evidence. But a document that argues something the evidence doesn’t support will fail when a sceptical reader checks the sources. Update the strategic framing file. The research you’ve already done isn’t wasted. The evidence serves whatever argument it actually supports.  
  
**Show the draft to its reader early.** In the project that produced this guide, the first complete draft was technically sound but argued the wrong thing. The feedback said “the whole argument needs to lead with business value.” Build a feedback step into your timeline.  
  
**Prompt development is a conversation.** The best prompts in this project emerged from Claude pushing back on assumptions (repositioning AI companies from partners to vendors) and from discussing the real purpose rather than the stated one. Don’t try to get the prompt right on the first attempt.  
  
**Context management is the binding constraint.** Keep reconciled files concise. Use the stopping rule. Start fresh conversations for validation. Split long sessions. The distinction between project knowledge (always available) and conversation context (the real limit) is worth understanding before you start.  
  
## Appendix: File Map  
  
After Foundation:  
  
```  
00-research-brief.md  
00-internal-context.md  
00-strategic-framing.md  
00-writing-standards.md (or in system prompt)  
stet.md (voice editing ruleset, optional)  
```  
  
After each research session (e.g., Session 1 with 3 passes):  
  
```  
01-topic-a.md ← pass A (deleted after reconciliation)  
01-topic-b.md ← pass B (deleted after reconciliation)  
01-topic-c.md ← pass C (deleted after reconciliation)  
01-topic.md   ← reconciled (kept)  
```  
  
After each research session (e.g., Session 4 with 1 pass):  
  
```  
04-topic.md ← single pass (kept as-is)  
```  
  
After all research:  
  
```  
01 through 04 ← reconciled files only  
```  
  
After synthesis:  
  
```  
05-gap-analysis.md  
06-draft.md  
```  
  
After validation:  
  
```  
06-draft-validated.md  
```  
  
After rewrite:  
  
```  
07-final.md  
```  
  
After document production:  
  
```  
07-final.docx  
```  
  
## References  
  
Anthropic (2025a). “Reduce hallucinations.” Claude API Documentation. https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations  
  
Anthropic (2025b). “Prompting best practices.” Claude API Documentation. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices  
  
Anthropic (2025c). “Long context prompting tips.” Claude API Documentation. https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips  
  
Panickssery, A., Bowman, S.R. and Feng, S. (2024). “LLM Evaluators Recognize and Favor Their Own Generations.” Advances in Neural Information Processing Systems 37 (NeurIPS 2024). https://arxiv.org/abs/2404.13076  
  
Taubenfeld, A., Sheffer, T., Ofek, E., Feder, A., Goldstein, A., Gekhman, Z. and Yona, G. (2025). “Confidence Improves Self-Consistency in LLMs.” Findings of the Association for Computational Linguistics: ACL 2025. https://aclanthology.org/2025.findings-acl.1030/  
  
Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., Chowdhery, A. and Zhou, D. (2022). “Self-Consistency Improves Chain of Thought Reasoning in Language Models.” Proceedings of the International Conference on Learning Representations (ICLR 2023). https://arxiv.org/abs/2203.11171  
