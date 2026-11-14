# Awesome Anti-Slop

Skills, prompts, linters and research for cutting generic AI writing.

The familiar stuff: staged revelations, five paragraphs that all sound alike, a joke explained after it lands, and a final sentence trying very hard to be a quote.

This collection starts with writing. It includes tools for English and other languages, technical documentation, academic work and personal voice. Entries link to their authors; no skill files are repackaged here.

## Start here

- [Peter Yang's no-ai-slop](https://github.com/petergyang/no-ai-slop/blob/main/skills/no-ai-slop/SKILL.md) for preserving personality while cutting canned rhetoric.
- [blader's humanizer](https://github.com/blader/humanizer/blob/main/SKILL.md) for spotting staged openings, forced contrasts and unnecessary explanations.
- [hannsxpeter's humanizer](https://github.com/hannsxpeter/humanizer/blob/main/SKILL.md) for working from a writing sample instead of a generic idea of “human.”
- [vale-ai-tells](https://github.com/tbhb/vale-ai-tells) for repeatable checks in technical documentation.

These are editorial starting points based on their instructions. This repository has not run a comparative benchmark or security audit. A lower pattern score does not establish better writing or tell you who wrote it.

## Contents

- [General writing skills](#general-writing-skills)
- [Specialist and house styles](#specialist-and-house-styles)
- [Languages](#languages)
- [Linters and pattern checkers](#linters-and-pattern-checkers)
- [Research and further reading](#research-and-further-reading)
- [Overlap and choosing a skill](#overlap-and-choosing-a-skill)
- [Contributing](#contributing)

## General writing skills

- [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill/blob/main/skills/humanizer/SKILL.md) - Pattern catalog with casual, professional, technical, warm and blunt voice profiles.
- [adewale/anti-slop-writing](https://github.com/adewale/anti-slop-writing/blob/main/skills/anti-slop-writing/SKILL.md) - Edits inflated claims, canned emphasis and paragraph flow; asks whether the evidence earns the sentence.
- [alex-jb/de-ai-writing-skill](https://github.com/alex-jb/de-ai-writing-skill) - Targets stacked aphorisms, formulaic contrasts, stock vocabulary and manifesto-style endings.
- [ameenmo/humanize-skill](https://github.com/ameenmo/humanize-skill/blob/main/SKILL.md) - Combines AI-pattern cleanup with an Ogilvy-inspired editing pass for clarity, jargon and the purpose of the piece.
- [blader/humanizer](https://github.com/blader/humanizer/blob/main/SKILL.md) - Edits staged openings, forced contrasts, repetitive closers and explanations of things the reader already knows.
- [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) - Audit and rewrite skill with voice profiles, detect-only mode and a bundled detector.
- [davidamitchell/Skills](https://github.com/davidamitchell/Skills/blob/main/remove-ai-slop/SKILL.md) - Checklist for filler, narrator distance, formulaic transitions and aphoristic endings.
- [davidcogan/avoid-ai-writing](https://github.com/davidcogan/avoid-ai-writing/blob/main/SKILL.md) - Audits and rewrites prose while preserving claim boundaries and genre conventions. Its metadata credits Conor Bronsdon; compare the conorbronsdon project above.
- [eskayML/anti-slop](https://github.com/eskayML/anti-slop/blob/main/SKILL.md) - Register matching and a validator. Also imposes strict punctuation rules, including one comma per sentence.
- [firemonster612/human-writing-skill](https://github.com/firemonster612/human-writing-skill/blob/main/skills/human-writing/SKILL.md) - Vocabulary, sentence rhythm and register rules with a self-audit. Claimed research support has not been independently checked here.
- [hannsxpeter/humanizer](https://github.com/hannsxpeter/humanizer/blob/main/SKILL.md) - Matches a supplied writing sample before removing recurring patterns. Includes checks against over-editing.
- [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop/blob/main/SKILL.md) - Compact rules against filler, formulaic structures and manufactured punchlines. Its blanket adverb and passive-voice bans need editorial judgment.
- [harshaneel/humanize](https://github.com/harshaneel/humanize) - Two writing skills with reference material on making prose more natural and relatable; research claims are the project's own.
- [henders23/humaniser](https://github.com/henders23/humaniser/blob/main/SKILL.md) - Voice calibration and repository-wide prose audits. Credits blader, hardikpandya and brandonwise.
- [iizcm/stop-slop-skill](https://github.com/iizcm/stop-slop-skill/blob/main/SKILL.md) - Short, strict checklist that bans several ordinary constructions, including sentence-initial “So.” Included for comparison.
- [immeasurablematt/a16z-anti-slop](https://github.com/immeasurablematt/a16z-anti-slop) - Editing skill adapted from an a16z crypto article; starts with what the writing needs to accomplish.
- [impactcrew/dont-be-a-sloperator](https://github.com/impactcrew/dont-be-a-sloperator) - Principle-based instructions for reducing generic copy and empty claims.
- [jalaalrd/anti-ai-slop-writing](https://github.com/jalaalrd/anti-ai-slop-writing) - Constraint-based writing skill covering stock vocabulary, sentence shapes and formatting.
- [joanrojas/slopless](https://github.com/joanrojas/slopless) - Synthesis of earlier anti-slop skills with voice protection, pattern references and editing checks.
- [kjmagnan1s/anti-slop](https://github.com/kjmagnan1s/anti-slop/blob/main/SKILL.md) - Consolidates several predecessors, with voice protection, correction intake and a separate completeness review.
- [madebybeings/human-copywriting-skill](https://github.com/madebybeings/human-copywriting-skill) - Writing and editing skill that prioritizes what to say and how much to explain before word choice.
- [MariusAure/anti-slop-writing](https://github.com/MariusAure/anti-slop-writing) - Single diagnostic-and-revision prompt that considers audience, evidence and genre before rewriting.
- [misbahsy/anti-ai-slop](https://github.com/misbahsy/anti-ai-slop/blob/main/skills/anti-ai-slop/SKILL.md) - Rewrite workflow with a Python linter and a separate reviewer. Its assurance claims are not independent evidence of effectiveness.
- [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop/blob/main/skills/no-ai-slop/SKILL.md) - Preserves bluntness, humor and useful digressions; calls for deleting fake-profound endings rather than polishing them.
- [SalZaki/antislop](https://github.com/SalZaki/antislop/blob/main/skills/remove-ai-slop/SKILL.md) - Conservative edits with register preservation and user vocabulary overrides; prefers cutting padding to rewriting everything.
- [shir-danishyar/humanize](https://github.com/shir-danishyar/humanize) - Writing and revision skill with register awareness, voice calibration and a Python linter.
- [sineminflux/no-ai-slop](https://github.com/sineminflux/no-ai-slop/blob/main/SKILL.md) - Compact writing rules, a separate final check and an explicit exception for the author's own voice.
- [westonhancock/unslop](https://github.com/westonhancock/unslop/blob/main/SKILL.md) - Emphasizes minimal edits and protecting the writer's uneven rhythm, vocabulary and personal traits.

## Specialist and house styles

- [AIScientists-Dev/academic-humanizer](https://github.com/AIScientists-Dev/academic-humanizer) - Editing guidance for papers and grant proposals, with attention to scholarly voice and evidence.
- [AMishradev/outbound-writing](https://github.com/AMishradev/outbound-writing) - Cold-email writing skill that gathers concrete facts before drafting and reviews repetitive AI phrasing.
- [AnswerDotAI/skill-plugins](https://github.com/AnswerDotAI/skill-plugins/blob/main/plugins/codex-aai/skills/write-prose/SKILL.md) - Annotated plain/sloppy examples for documentation and explanatory prose; draws on the NousResearch anti-slop reference.
- [forint573/human-copywrite](https://github.com/forint573/human-copywrite) - Marketing and long-form copy skill covering brand voice, factual preservation and removal of drafting residue.
- [junbolian/Academic-Humanizer](https://github.com/junbolian/Academic-Humanizer) - English and Chinese academic editing with checks for preservation of numbers, equations, citations and theorem statements.
- [mdlamar/ASD-STE100](https://github.com/mdlamar/ASD-STE100) - Simplified Technical English skill and linter packaged for opencode; includes the author's reported experiments.
- [realrossmanngroup/no_ai_slop_writing_rules](https://github.com/realrossmanngroup/no_ai_slop_writing_rules) - An example of a specific author's house style: Louis Rossmann's writing rules and skills.
- [rookslog/stylewright](https://github.com/rookslog/stylewright) - Writing skills tied to named style standards, with a companion linter.
- [stephenturner/skill-deslop](https://github.com/stephenturner/skill-deslop) - Prose editing skill with examples weighted toward scientific writing and technical blog posts.

## Languages

- [anhnx000/viet-nhu-nguoi](https://github.com/anhnx000/viet-nhu-nguoi) - Vietnamese writing skill with a local pattern checker and factual checks; also documents English support.
- [Dradradre/korean-anti-slop-writing](https://github.com/Dradradre/korean-anti-slop-writing) - Korean writing skill and standalone checking script for reports, messages, interface copy and blog posts.
- [durmazoguzhan/turkish-humanify](https://github.com/durmazoguzhan/turkish-humanify) - Turkish writing and revision skill with register-specific guidance and preservation of technical terms.
- [dwaang/anti-slop](https://github.com/dwaang/anti-slop) - English and Russian editing guidance drawing on Stop Slop and Humanizer approaches.
- [iKora128/stop-ai-slop-jp](https://github.com/iKora128/stop-ai-slop-jp) - Japanese adaptation of hardikpandya/stop-slop with local examples and pattern references.
- [LifelongLazyLearner/qu-ai-wei](https://github.com/LifelongLazyLearner/qu-ai-wei) - Simplified Chinese rewriting skill for stock phrasing, mechanical structure and translation-like prose.
- [masharawi/ontslopper](https://github.com/masharawi/ontslopper) - Dutch rewriting skill and chat instructions for stock phrasing and generic AI tone.
- [nynynakazawa/anti-slop-writing](https://github.com/nynynakazawa/anti-slop-writing) - Separate English and Japanese skills, each with language-specific rules and linting guidance.
- [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) - Chinese prose editing guidance that preserves factual scope and voice; related to the Humanizer family.
- [OthmanAdi/humanizer-semitic](https://github.com/OthmanAdi/humanizer-semitic) - Separate skills for Modern Standard Arabic, Egyptian Arabic, Levantine Arabic and Hebrew.
- [tentenco/shuorenhua-zh-tw](https://github.com/tentenco/shuorenhua-zh-tw) - Traditional Chinese editing for Taiwan, including regional usage and punctuation. Credits MrGeDiao/shuorenhua and Better-Humanizer-zh-TW.

## Linters and pattern checkers

- [brandonwise/humanizer](https://github.com/brandonwise/humanizer) - OpenClaw skill and standalone CLI with vocabulary and text-statistics checks; credits blader/humanizer.
- [FeedHive/ai-slop-detector](https://github.com/FeedHive/ai-slop-detector) - Catalog of writing patterns with explanations and rewrites, plus an agent skill and hosted checker.
- [ilien-dev/quiron](https://github.com/ilien-dev/quiron) - Writing skill with local measurements against human-text baselines and register-specific checks.
- [judetelan/ai-humanizer](https://github.com/judetelan/ai-humanizer/blob/main/SKILL.md) - JavaScript detector with lexical and rhythm checks, file audits and optional editor hooks.
- [seyedehsanhadi/sloptrim](https://github.com/seyedehsanhadi/sloptrim) - Local Python detector for writing patterns in saved prose files; supports file-edit hooks.
- [tbhb/vale-ai-tells](https://github.com/tbhb/vale-ai-tells) - Vale rules for AI-associated language patterns, aimed primarily at technical documentation.
- [yanstd888/humanizer-lint](https://github.com/yanstd888/humanizer-lint) - Local prose and rhythm linter with language packs, targeting stock phrases and repetitive wording.

## Research and further reading

- [Daguilar0123/ai-writing-skill-field-guide](https://github.com/Daguilar0123/ai-writing-skill-field-guide) - Survey of writing skills with maintenance analysis and published evaluation material. Results belong to its authors.
- [mshumer/unslop](https://github.com/mshumer/unslop) - Generates samples in a chosen domain, identifies a model's repeated defaults and produces a custom instruction file.
- [NousResearch/autonovel](https://github.com/NousResearch/autonovel/blob/master/ANTI-SLOP.md) - A prose-pattern reference inside the autonovel project; also used by AnswerDotAI's writing skill.
- [sam-paech/auto-antislop](https://github.com/sam-paech/auto-antislop) - Pipeline for measuring model-specific overused phrases, generating preference data and fine-tuning a model.
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) - Editorial pattern guide cited by many of these skills. Patterns are clues to inspect, not proof of authorship.
- [zhuyansen/awesome-humanizer-skills](https://github.com/zhuyansen/awesome-humanizer-skills) - A broader directory spanning writing, code and UI, with its own testing and security labels. Useful for further discovery.

## Overlap and choosing a skill

Many entries share ancestors. Humanizer variants often draw from Wikipedia and blader/humanizer. Stop Slop variants reuse Hardik Pandya's rules. Some projects combine both. The annotations identify relationships stated in the inspected sources; they are not a complete genealogy.

Read the instructions before choosing one. Some protect the author's slang and punctuation; others prohibit ordinary constructions. A rule that helps a technical manual may wreck a casual post. Give the skill a sample of the voice you want and check whether the rewrite still sounds like that person.

Try one at a time. Compare the original and revised text for meaning, missing details and unwanted changes of tone. Installing several overlapping rule sets does not give you several independent editors.

## Contributing

Add a resource through a pull request, or open an issue with its source URL.

Run `mise run check` (or `python3 scripts/check.py`) to check links and section anchors before submitting a change. The link check makes public HTTP requests; it does not install or run any listed tool.

- Link to the author's repository, skill file or original guide.
- Put it in the closest section, alphabetically by owner and project name.
- Describe what it does in one or two sentences. Name the language or writing context when relevant.
- For an adaptation, name the upstream project and explain the useful difference. Repackaging alone does not need another entry.
- Check that the destination exists and the description matches its current contents.
- Attribute benchmark results to their authors. Avoid untested “best,” “undetectable” or security claims.

Scope: resources that help people identify, prevent or edit generic AI prose. General-purpose writing apps and code/UI-only cleanup tools are outside the current collection. Broader directories are linked under further reading.

The initial collection was checked on 14 November 2026. It contains 61 resources and is open to additions. Source inspection confirms what a project documents, not that every advertised feature works.

Discovery included GitHub search, [Awesome Humanizer Skills](https://github.com/zhuyansen/awesome-humanizer-skills) and the [AI Writing Skill Field Guide](https://github.com/Daguilar0123/ai-writing-skill-field-guide). Descriptions here were written from the linked primary sources; those collections' rankings and security labels are not adopted here.

## License

This collection's original descriptions are dedicated to the public domain under [CC0 1.0](LICENSE). Linked projects retain their own licenses.
