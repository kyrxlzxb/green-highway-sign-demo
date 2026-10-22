# Repository authoring rules

[日本語](PERSONAL_REPOSITORY_RULES.ja.md) | [English](PERSONAL_REPOSITORY_RULES.md)

## English and Japanese

- Author project documentation in English and provide a complete, semantically equivalent Japanese version. Japanese must not be a summary. Keep procedures, examples, requirements, limitations, and verification status aligned.
- Update both languages in the same change. Check semantic parity and relative links before claiming completion.
- Use README.en.md for the English source and README.md for the complete Japanese landing page. Use <name>.md and <name>.ja.md for other documents. Add concise `日本語 | English` links without a translation preface.
- Preserve tool-required filenames and schemas. Keep AGENTS.md in English with its Japanese reading counterpart at docs/AGENTS.ja.md. Keep Japanese mirrors of tool-managed documents outside automatic discovery paths unless the tool explicitly supports multilingual artifacts.
- Keep substantive project-owned explanatory comments and docstrings bilingual with adjacent EN/JA prose. Do not duplicate executable source or add unnecessary comments to obvious code.
- Preserve identifiers, commands, paths, API fields, configuration keys, runtime prompt language, application data, legal notices, third-party code, and machine-sensitive directives. Documentation localization must not change behavior.

## Deliverable content

- Apply user instructions without reproducing or narrating them in the deliverable.
- Do not copy the user's conversational explanations, personal context, illustrative remarks, or reasons for requesting the work into README files, other documentation, code comments, or release notes.
- Do not write that Japanese documentation exists “for Japanese colleagues,” that a choice was made “because the user requested it,” or similar meta-commentary.
- Include relevant project facts, usage instructions, contracts, limitations, and technical rationale that helps readers operate or maintain the system.
- Keep actionable authoring/maintenance policies in agent or contributor guidance. Do not repeat them as prefaces throughout project documentation.
- Before delivery, check both language versions for leaked conversation content, unnecessary instruction explanations, and unsupported factual claims.

## Uncertain facts

- Inspect available evidence before making factual claims. If required facts remain uncertain, ask the owner before finalizing the affected content or performing dependent work.
- This includes file locations, active versions, server directory structure, model artifacts, and deployment commands. Do not invent plausible values or treat old conversations as proof of current deployment state.
- Mark unresolved items in working notes, wait for confirmation, and continue unrelated work. Do not claim the affected work is complete while required facts remain unresolved.
