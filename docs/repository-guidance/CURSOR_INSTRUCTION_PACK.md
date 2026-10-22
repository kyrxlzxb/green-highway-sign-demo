# Cursor instruction pack: extract three clean repositories

Prepared 2026-10-22. These instructions describe the owner's requested migration, not a claim that the source code has been inspected at the company.

## How to use this pack

Attach this file to Cursor. Start with the Master Brief and Stage 1. Use a separate chat for each repository extraction, attaching the Master Brief, the audit report, and the relevant stage. Stages are separate execution requests, not authorization to execute every later stage immediately.

Suggested order: audit all three pipelines; extract landmark; extract green signs; extract blue signs; add project guidance; initialize OpenSpec; publish fresh GitLab repositories.

Fill only the locations and destinations you actually know. Inspect accessible evidence first; if a required fact remains uncertain, ask the owner and wait for confirmation before writing it as fact or performing work that depends on it. Never infer a model's exact identity from a spoken nickname.

```text
SOURCE_ROOTS:
ADDITIONAL_POSTPROCESSING_ROOTS:
NEW_REPOSITORY_PARENT:
LINUX_SERVICE_SOURCE_OR_ACCESS_METHOD:
APPROVED_INTERNAL_MODEL_ARTIFACT_LOCATION:
GITLAB_NAMESPACE_AND_THREE_REMOTE_URLS:
REPRESENTATIVE_INPUTS_AND_ACCEPTED_OUTPUTS:
```

## Master Brief — paste at the start of each migration chat

You are helping me extract three small, working AI-assisted image-processing projects from experimental code into three completely independent GitLab repositories:

1. landmark-icon-generator
2. green-sign-generator
3. blue-sign-generator

Treat these as provisional names until the actual destination names are supplied.

### My intended outcome

Create a clean baseline from the currently working implementations. Do not rewrite the applications from scratch. Preserve the original directories and their Git history untouched, but do not copy their `.git` directories, branches, tags, or commit history into the new repositories. Initialize fresh Git repositories only inside the verified new destinations.

Each project is small. Its UI is primarily an operator preview/debugging interface: select inputs/settings, inspect the prompt actually sent, run processing, inspect responses and preview/save outputs. The repositories are company assets intended for Japanese colleagues as well as me, not personal-only projects. Preserve useful existing controls without turning this into a large product or platform. Do not impose a frontend framework, plugin architecture, shared SDK, fourth repository, container stack, or elaborate packaging solely for neatness.

The three repositories must not import source code, prompts, or assets from one another or from the old directories. Document genuine external services. Independence does not mean that an application using a remote model must run offline.

Keep only the verified active implementation and necessary assets/configuration. Keep the currently selected, working prompt for each active stage or required variant, not every historical experiment. “Current” means verified in the active pipeline, not the most recently modified filename. A pipeline may legitimately need several distinct prompts; do not collapse them into one.

Exclude abandoned alternatives, duplicate implementations, unused scripts, caches, virtual environments, output dumps, old Git metadata, and historical prompt collections. Do not delete these from their original locations. Do not place an entire legacy archive inside a new repository.

Preserve required dependency notices and licenses. Exclude credentials, private input collections, and large model artifacts from Git. Use placeholder configuration and company-approved storage references where appropriate.

### Pipeline expectations — verify against the actual implementation

- Landmark: image generation followed by local code-based post-processing. Preserve the complete currently working chain. A different department's legacy Windows/Excel/macro-based testing tool is explicitly out of scope. Do not rebuild or integrate it. Normal validation of our extracted pipeline remains in scope.
- Green signs: a language/vision model returns structured information or parameters; Python generates the output. Inspect the actual contracts and rendering implementation. Do not assume historical demos used real model calls rather than manually prepared parameters.
- Blue signs: image generation -> fine-tuned VLM inference on an existing Linux server -> SVG -> AI-assisted refinement -> human adjustment/export. Verify the exact sequence, service protocol, model identity, scripts, and handoffs. Preserve the currently working approach even if it is awkward. A future green-style blue-sign pipeline is an idea, not part of this migration.

Do not assume Azure, Amazon Bedrock, image-generation providers, or the Linux VLM share an API or authentication mechanism. Record the actual providers and deployment/model identifiers from evidence, with secrets redacted.

### Working style

- Inspect before changing. Use concrete evidence, not filenames or old conversational claims, to identify active code.
- Resolve routine implementation choices yourself within the scope, but never fill factual gaps with assumptions. Follow the confirmation policy below for uncertain required information. Continue independent work while waiting.
- Author documentation in English and provide complete, equivalent Japanese documentation and explanatory comments under the bilingual policy below. Preserve Japanese/other-language sign text and required runtime prompt language; do not translate application data or runtime prompts as part of documentation localization.
- Do not change prompt meaning, model settings, image processing, or output contracts during extraction. Necessary path/import/configuration changes are allowed. Keep behavioral fixes separate and explain them.
- Distinguish static checks, replay/mocked tests, live service tests, visual review, and owner acceptance. Never claim end-to-end verification from syntax checks or fixtures alone.
- Write compact evidence and handoff notes. Do not generate ceremony, speculative roadmaps, or empty documentation trees.
- Keep migration reports in a separate migration workspace. Include only a short verified provenance/limitations note in each final repository if useful.

### Confirm uncertain facts before dependent work

If something you must write or use is uncertain, inspect available evidence first. If it does not resolve the uncertainty, ask me before completing the affected content or taking the dependent action. This applies to file locations, which source folder/version is active, file ownership, the actual Linux directory tree, deployed scripts, model artifact locations, startup commands, transport, and environment details. Old local scripts or past chat descriptions are not confirmation of current server state.

Ask concrete, grouped questions: identify the unknown, the evidence already checked, and exactly what answer or redacted command output is needed. Do not ask me to approve every routine edit. Do not guess a server path just to produce an executable command; first establish the relevant directory. Request only the smallest useful directory listing or file excerpt, not a dump of secrets or the whole server.

Until I answer, mark the affected item as `Pending owner confirmation` in working notes and leave dependent implementation/documentation unfinished. Do not convert a placeholder into a real-looking path, silently select between competing versions, or treat lack of response as confirmation. Continue unrelated work. Once confirmed, record the fact and its source briefly and use it consistently in both languages. Do not label a document or extraction complete while required factual questions remain unresolved.

### English source, complete Japanese documentation

English is the canonical authoring language; Japanese is a complete, equally usable reading version for company colleagues. Japanese must not be a summary or an abbreviated secondary guide. The default repository landing page should be Japanese without changing the English source-of-truth policy.

Use `ja` for the Japanese language suffix, not `JP` (a country label). Adopt this layout:

```text
README.md                     # Complete Japanese landing page
README.en.md                  # Canonical English README
AGENTS.md                     # Canonical English agent instructions
docs/AGENTS.ja.md              # Complete Japanese counterpart for readers
docs/PROMPT_EDITING.md         # Canonical English policy
docs/PROMPT_EDITING.ja.md      # Complete Japanese counterpart
docs/PIPELINE.md               # English, if needed
docs/PIPELINE.ja.md             # Japanese, if needed
docs/DEPLOYMENT.md             # English, if needed
docs/DEPLOYMENT.ja.md           # Japanese, if needed
```

Use the same `<name>.md` / `<name>.ja.md` pairing for other authored documents, including audit reports, validation reports, handoffs, limitations, and important decisions. The README is the deliberate exception: Japanese uses `README.md` for the landing page, English uses `README.en.md`. Do not create a third duplicate README.ja.md.

At the top of each pair, add working relative links labelled `日本語 | English`. Do not add an explanatory preface about translation, the intended nationality of readers, the owner's preferences, or why bilingual documentation was requested. Both versions must cover the same requirements, procedures, examples, warnings, limitations, verification status, and unresolved questions. Use natural professional Japanese. Keep commands, identifiers, API fields, environment variable names, paths, model names, and numeric values identical except for deliberately language-specific document links.

For changes, update English first and synchronize Japanese in the same change/commit. Compare the two versions for semantic parity and check links. Do not claim bilingual completion with stale or missing Japanese content. If a Japanese edit introduces a substantive new requirement, confirm its intended meaning and update the English source too. A discrepancy is a documentation defect to resolve, not permission to silently ignore one audience.

Keep tool-discovered filenames and syntax intact. AGENTS.md remains English and directs agents to English source documents; its Japanese counterpart lives under docs/ to avoid introducing another active instruction scope. For authored OpenSpec proposals, designs, tasks, and specs, retain English in the tool-managed paths and provide complete Japanese mirrors under `docs/ja/openspec/`, preserving the relative hierarchy. Link each mirror to its English source and update its location/links when the source is archived. Do not put duplicate translated specs or tasks into tool discovery directories unless the installed tool explicitly supports that structure. This mirror policy covers authored project content; do not manually translate or fork all third-party generated command/skill templates. Explain those workflows in bilingual project documentation instead.

For project-owned explanatory code comments and docstrings retained in the extracted code, preserve English and add an equivalent Japanese explanation adjacent to it, using compact `EN:` / `JA:` lines or paragraphs within the same comment/docstring. Include existing substantive English-only explanations, not just newly added ones. Do not duplicate source files or executable code. Do not add comments to every obvious line merely to make it bilingual. Preserve shebangs, encoding declarations, tool directives, type annotations, license notices, third-party code, and other machine-sensitive text unchanged. Translate explanatory prose, not identifiers or executable examples. If a docstring/comment is consumed at runtime or by a parser, inspect that usage first and keep its behavioral contract unchanged; document the explanation bilingually elsewhere if necessary.

This instruction pack itself is an English execution brief. The bilingual requirement applies to the project documents and comments Cursor produces or retains for the company repositories.

### Keep development instructions out of deliverable content

Treat the owner's instructions, explanations, examples, and reasons for requesting work as guidance for doing the work, not text to reproduce in its deliverables. README files, Japanese counterparts, handoffs, code comments, release notes, and other project documentation should contain relevant project facts, usage, contracts, limitations, and necessary technical explanations only.

Do not write statements such as “This Japanese document is for Japanese colleagues,” “The owner requested an English-first workflow,” “We added this because the user asked,” or narratives of the development conversation. Do not merely paraphrase those statements to conceal their conversational origin. Apply the instruction without narrating it.

Persistent agent rules may state the actionable bilingual and content policies because that is their purpose; they must not include the owner's personal background or the conversational story behind the policies. Keep translation-maintenance instructions in agent/contributor guidance, not a preface in every document. Include a technical rationale only when it helps readers understand a real design decision or operate/maintain the project; do not confuse that with an explanation of why the owner gave an instruction. Before delivery, remove leaked request text, irrelevant personal context, and meta-commentary from both language versions.

## Stage 1 — investigate the existing implementation

Read the Master Brief. Investigate all supplied source roots without changing the original source/configuration/prompts or Git state. You may create audit reports and disposable verification outputs in a separate migration workspace. Do not perform extraction, initialize Git, install OpenSpec, or alter the deployed Linux service in this stage.

1. Find actual launch commands and entry points. Trace each UI action through model calls, prompt assembly, parsing, rendering/post-processing, review, and export.
2. Inventory dependencies beyond Python imports: dynamic loaders, subprocesses, manually run scripts, configuration files, prompt fragments, assets/fonts, schemas, external services, and files passed between directories or machines.
3. Identify the actual final request payload at each model boundary, including system/user instructions, template variables, preprocessing, reference images, generation settings, response parsing, and any UI prompt overrides. Never include secrets in reports.
4. Review relevant existing Git history and handoff documents as clues. Treat the running company implementation as the authority on implemented behavior. Resolve discrepancies explicitly.
5. Classify candidate files as VERIFIED_ACTIVE, SHARED_ACTIVE, LIKELY_LEGACY, GENERATED_OR_TEMPORARY, or UNKNOWN. Include evidence and confidence. A module being imported is not proof that every implementation in it is active; lack of execution in one run is not proof of obsolescence.
6. Identify small representative inputs and accepted outputs for each pipeline. Prefer existing samples. Record actual commands and necessary manual steps. Trace active branches with the fewest useful runs. Use separate output locations; do not overwrite accepted examples.
7. Identify missing Linux-side source and deployment facts. Local upload scripts may differ from the deployed version. If authorized access is available, compare them read-only. Otherwise ask the owner to confirm the relevant server directory/tree and provide narrowly scoped inspection commands only once their target locations are established. Request redacted source/version/startup information. Wait for the answers before writing deployment facts or extracting dependent components. Do not claim to have verified inaccessible files.

Deliver a compact AUDIT.md and complete AUDIT.ja.md counterpart containing:

- One pipeline/dependency map per project.
- Actual entry points, active prompts, model/service boundaries, and final outputs.
- Proposed include/exclude inventory with evidence and unresolved items.
- Runtime verification results or a precise remaining checklist.
- Proposed extraction boundaries, including Linux service ownership.
- Only the questions that block a correct extraction.

Finish this investigation and report readiness. Do not guess the intended baseline when two versions conflict.

## Stage 2 — extract ONE repository

```text
TARGET_PROJECT: [landmark / green / blue]
DESTINATION: [new absolute path]
AUDIT_REPORT: [path]
```

Read the Master Brief and the audit report. Extract the named project using verified active components. Preserve the original projects untouched.

Create the smallest practical layout consistent with the existing implementation. A small project can remain a few Python files. Do not introduce a `src/` package hierarchy merely to match a template. Copy shared helpers as necessary so the new repository has no dependency on the old workspace or either sibling project.

Preserve active prompts byte-for-byte where possible. If moving a prompt into a file or changing assembly is necessary, compare the fully assembled request before/after with the same inputs; do not silently change whitespace-sensitive content, variable substitution, images, or settings. Do not improve prompts while extracting them.

Remove irrelevant tabs and references in the new copy. Preserve the existing ability to inspect the actual sent prompt/settings, response/error, and output. Do not build a new observability system. If the preview currently differs from the actual request or export, report that as a separate defect rather than hiding a behavior change in cleanup.

Keep the necessary fonts, icons, templates, schemas, runtime dependency declarations, and example configuration. Preserve reproducible dependency versions where known. Separate local/client and Linux server dependencies when they differ. Do not pretend that an unverified dependency version is tested.

For landmark, stop at the current usable output before the other department's legacy testing system. For green signs, preserve the model-to-parameters and parameters-to-renderer boundary. For blue signs, also apply Stage 2B below.

Validate from the new directory using a clean environment when available. Ensure nothing is imported or loaded from the old directories. Compare with the same baseline inputs:

- Deterministic stages: compare meaningful outputs; use exact comparisons where valid and explain any unavoidable rendering/environment variation.
- Model stages: preserve the actual request and settings, validate response contracts, and visually compare representative results. Do not require pixel-identical stochastic generations.
- Replay tests: identify stored model responses explicitly as replay inputs.
- Human adjustment: verify the saved/exported file represents the current edited state; if downstream outputs depend on it, verify they are not silently stale.

Do not add a large test suite. Prefer existing tests and a small reproducible smoke check covering meaningful stage boundaries and outputs. Report unavailable live API/GPU/manual checks separately.

Deliver the independently runnable extraction, minimal run instructions, verification results, and unresolved issues. Do not publish a repository as verified while required checks remain blocked. Do not silently expand scope to resolve unrelated shortcomings.

## Stage 2B — blue-sign Linux inference component

Include the project-owned Linux inference source and deployment instructions within the blue-sign repository if they belong to this pipeline. Keep a clear local/client versus Linux/server boundary; for example `server/` is sufficient if it fits the existing code. This remains one repository, not a fourth project.

Do not move multi-GB weights into Git. Keep weights/checkpoints/adapters in the company's existing approved artifact storage or server model directory. Do not introduce Git LFS or a new model platform without a demonstrated requirement. Even a relatively small fine-tuning adapter is a model artifact; decide explicitly how it is stored and versioned.

Create a concise model manifest and deployment note with verified values for:

- Exact base model identifier and revision, fine-tuned model/adapter version, and whether the deployed artifact is merged or requires a separate base model.
- All required artifacts: weights/shards, index, tokenizer/processor, configuration, adapter and base model as applicable.
- Approved retrieval/location reference without embedded credentials; local installation path supplied through configuration.
- Artifact checksums or a reliable immutable version reference where available. Mark missing values as unverified, never fabricate them.
- Inference framework and version; observed Python/PyTorch/CUDA and GPU environment where relevant. Distinguish an observed working environment from a tested minimum requirement.
- Existing startup/inference commands, input image preprocessing, request/response formats, generation settings, and SVG extraction/post-processing.
- Authentication/configuration, timeouts, failure behavior, and client endpoint configuration without exposing secrets.
- A minimal service check and a known input-to-SVG smoke check.

Preserve the existing transport (HTTP, file exchange, SSH, batch script, etc.). Do not convert it to a new API architecture just for this extraction. Reuse current deployment mechanisms rather than inventing Docker/systemd infrastructure.

If this is a centrally owned shared service rather than project-owned code, retain the client and a precise external service contract instead; document who maintains it and how its model version is identified. If project-owned server source is missing, clearly mark the extraction incomplete at that boundary instead of pretending that a client wrapper makes the system reproducible.

Include only training/export scripts actually needed to explain or rebuild the deployed artifact when they are available and in scope; omit experimental training collections and datasets. Do not require retraining for migration. Do not restart, redeploy, or replace the running server while collecting evidence.

## Stage 3 — add lightweight repository guidance

Apply this separately to each extracted repository. Base documentation on that repository's verified implementation. Do not copy speculative functionality from historical plans.

Create or update only useful documents:

- README.en.md and README.md: complete English source and Japanese landing page, covering purpose, installation, configuration, launch, inputs/outputs, actual pipeline, required external services, and limitations. Include one short pipeline diagram if useful.
- AGENTS.md and docs/AGENTS.ja.md: concise English persistent instructions and a full Japanese reading counterpart. Use the policy below, tailored to verified project facts.
- docs/PROMPT_EDITING.md and docs/PROMPT_EDITING.ja.md: the complete prompt-editing policy below in both languages.
- .env.example or the existing equivalent, .gitignore, and accurate dependency declaration.
- A short docs/PIPELINE.md or deployment note, each with a complete .ja.md counterpart, only if the README would become difficult to use. Blue signs need the Linux deployment/model artifact information.

Do not require a separate CLAUDE.md unless Claude Code is actually used. Do not duplicate the same policy in AGENTS.md, Cursor rules, and Skills. Cursor supports AGENTS.md; use it as the general instruction source. If a scoped `.cursor/rules/*.mdc` file is useful, keep it small and instruct the agent to read the canonical prompt policy when editing prompts, including prompts embedded in Python/UI/configuration. A path glob limited to `prompts/` is not sufficient by itself.

Do not create custom Skills just to satisfy a checklist. A repeatable workflow can become a Skill after its inputs, outputs, and validation are stable. OpenSpec-generated integration files are a separate, purposeful addition in Stage 4.

### AGENTS.md policy to adapt

```markdown
# Agent instructions

## Project and source of truth
- Read README.en.md and the relevant English pipeline/deployment notes before changing behavior; README.md is the complete Japanese landing page.
- Describe current implementation, verified evidence, and future ideas separately.
- Keep user instructions and their conversational/background explanations out of deliverable prose. Apply them without narrating them. Document relevant project content and useful technical rationale only; keep actionable maintenance policies in agent/contributor guidance.
- If required facts remain uncertain after inspection, ask the owner and wait before writing them as facts or performing dependent work. This includes paths, active versions, and the current Linux file tree/deployment. Record pending items explicitly and continue independent work.
- Use the documented entry points and active prompt sources. Do not revive legacy alternatives without an explicit request.
- Keep this small application simple and independently runnable. Prefer existing helpers and direct code over new frameworks or generic abstraction layers.

## Changes
- Preserve validated behavior outside the requested scope.
- Do not change models, prompt semantics, rendering rules, or stage order as incidental cleanup.
- Do not add speculative requirements, edge cases, fallback pipelines, or new dependencies.
- Treat model-generated text/parameters/SVG as data; parse and validate at the existing boundaries before use. Do not execute generated code or embedded SVG scripts.
- Prefer deterministic code for established geometry and post-processing operations; do not introduce model calls for operations already implemented reliably in code.
- Keep human edits and final exports consistent. A downstream artifact must correspond to the current upstream state.

## Prompt changes
- Read docs/PROMPT_EDITING.md before editing any runtime prompt or its assembly.
- Apply the smallest semantically complete change across all relevant active instructions and examples.
- Runtime model requests must stand on their own; they must not rely on our development conversation.
- Do not invent requirements or turn explanatory examples into universal rules.

## Verification and handoff
- Run checks appropriate to the actual change. Keep fixtures/replay and live model verification clearly distinguished.
- Check contracts and representative visual outputs where relevant; passing syntax checks does not establish visual correctness.
- Report changed behavior, checks actually performed, and any unresolved limitations.
- Author documentation and handoffs in English and maintain complete Japanese counterparts in the same change. Use README.en.md / README.md for English / Japanese; use .ja.md companions for ordinary documents and docs/AGENTS.ja.md for AGENTS.md. Keep authored OpenSpec Japanese mirrors under docs/ja/openspec/, outside tool discovery paths. Link both languages and verify semantic parity. Keep substantive explanatory comments/docstrings bilingual (EN/JA) without changing machine-sensitive text, application data, or runtime prompt language.
- Keep credentials, large model artifacts, private input collections, and disposable outputs out of Git.
- Use OpenSpec for a substantive agreed behavior/interface/pipeline change; do not force every experiment or minor edit through a full proposal.
```

Add a short project-specific section, using confirmed facts only:

- Landmark: preserve the accepted image-to-postprocessing chain and verified output contract; no integration with the external legacy test tool.
- Green: preserve the structured model response contract and deterministic rendering boundary; retain required editable elements/assets where confirmed.
- Blue: preserve the deployed VLM identity/contract, SVG refinement and human review flow. Preserve stable element IDs, coordinate systems, font/rendering assumptions, and stale-result invalidation only where these are actual requirements. Do not replace the architecture with the green-sign approach during maintenance without an explicit request.

### Canonical policy for docs/PROMPT_EDITING.md

```markdown
# Runtime prompt editing policy

## 1. Separate intent from conversational explanation
Before editing, distinguish:
- The behavior the user explicitly wants changed.
- Background explanation about why the change matters.
- Illustrative examples, counterexamples, and temporary debugging observations.
- Unresolved assumptions or suggestions.

Only translate supported behavioral requirements into runtime instructions. Do not copy the user's explanation verbatim merely because it was said during development. Do not insert internal discussion, implementation history, or agent-to-user commentary into a model prompt.

## 2. Make every request self-contained
Review the complete request the downstream model actually receives: system/developer/user messages, assembled fragments, variable values, and attached images or other inputs.

The downstream model does not know our development chat. Replace context-dependent phrases such as “the previous issue,” “as we discussed,” or “the second example” with explicit information when that information is genuinely required. References to an attached image or another message are valid only when that image/message is actually sent and unambiguously identified. If necessary context is missing, do not invent it.

Examples may be included when they clearly teach the intended behavior and are self-contained. A one-off image's geometry, color, size, or failure must not become a universal constraint unless the user requests that generalization.

## 3. Edit the whole relevant meaning, not just the pointed-to sentence
When the user highlights one sentence, identify the underlying requested change. Read the entire active prompt and inspect related active fragments, examples, schemas, assembly logic, and UI overrides.

Update semantically equivalent or dependent statements that would otherwise contradict the change. Check both positive instructions and prohibitions. Update an example if it still demonstrates the old behavior. Do not perform a blind global text replacement or modify another task's unrelated prompt.

The target is the smallest semantically complete change, not the smallest number of changed lines and not a wholesale rewrite. If the user explicitly limits edits to one exact region, respect that limit and report any remaining conflict instead of silently editing elsewhere.

## 4. Do not expand the requirement
Do not add new thresholds, rigid dimensions, categories, edge-case rules, aesthetic preferences, exception lists, fallback behavior, or “helpful” constraints unless supported by the user's request or an established project contract.

If an extra rule seems necessary, explain the gap separately. Ask only if resolving it is essential to correctness; otherwise leave it as a suggestion outside the prompt. Preserve unaffected behavior and terminology. Do not make the prompt longer simply to sound more precise.

## 5. Verify the assembled result
Before finishing:
1. State the intended behavior change briefly.
2. Review the complete final request for contradictions, duplication, missing references, and unintended generalization.
3. Check that required variables, image references, and output schemas still match the caller/parser.
4. Confirm the UI preview represents the request actually sent, if the project exposes such a preview.
5. Run an appropriate representative check when possible. State clearly if model behavior was not tested.
6. Summarize the semantic changes and any unresolved ambiguity. Keep this explanation outside the runtime prompt.

Store the canonical active prompt in its established version-controlled location. Future Git commits provide prompt history; do not accumulate prompt_final_v2_new copies. Preserve multiple prompts only when they represent distinct supported stages or modes.
```

## Stage 4 — introduce OpenSpec to the existing baseline

Read the Master Brief and the finished repository. This stage introduces development workflow/documentation; it does not authorize changing application behavior.

Check the current official OpenSpec installation instructions and the available CLI version/help. Use the company-approved installation mechanism and record the version used. Initialize only Cursor integration with the core profile, using the installed version's supported syntax. Current reference syntax is `openspec init --tools cursor --profile core`; verify it before running. Do not enable every integration or introduce cross-repository stores.

Use the generated Cursor commands/skills as installed. Current official documentation uses `/opsx-propose`, `/opsx-explore`, `/opsx-apply`, etc. in Cursor; do not assume another tool's colon syntax works here. If the editor must reload to discover integrations, say so.

Do not claim that initialization automatically understands the application. Read the code and verification evidence, then create a small baseline of the supported behavior using the installed OpenSpec schema and templates.

Use one real documentation-only change, for example `document-current-baseline`:

1. Propose it using the generated workflow. Scope: document verified current behavior and development boundaries, with no runtime changes.
2. Record requirements/scenarios for the actual input/output contract, major processing stages, necessary external services, and existing review/export behavior. Keep implementation details in the README/deployment notes rather than making every function a requirement.
3. Separate verified supported behavior from known limitations and unverified integration points. Do not turn an accidental defect into a mandatory requirement. Do not invent completed features to make the spec look comprehensive.
4. Apply only the documentation/configuration tasks. Link to existing validation evidence. Mark missing runtime checks honestly; specification syntax validation does not prove application correctness.
5. Run the installed CLI's applicable validation, resolve document/schema issues, and review the specs against the implementation.
6. Once this documentation change is actually complete, synchronize its requirements to main specs and archive it using the generated workflow. Do not fabricate past proposals, retroactive approvals, or completed engineering tasks.

Keep `openspec/config.yaml` concise: small project, canonical English artifacts with complete Japanese mirrors under docs/ja/openspec/, preserved current baseline, prompt-editing policy reference, confirmation of unresolved facts, and explicit out-of-scope work. Avoid copying entire project documents into its context field. Synchronize authored bilingual artifacts and links before completing or archiving this change; preserve the tool's expected English structure and syntax.

Deliver a short walkthrough of the actual generated files: which describe the current system, which recorded this change, what initialization generated, and what was authored from evidence. Explain one concrete future use, such as a requested response-schema change or an agreed prompt behavior change. Do not implement that example or create a speculative backlog unless requested.

For uncertain future ideas, use exploration. For a substantive agreed change, propose -> implement -> validate -> synchronize/archive, using installed commands. Routine edits and exploratory experiments need not produce full change dossiers.

## Stage 5 — initialize and publish clean GitLab repositories

Execute this stage when I supply the intended GitLab destinations and request publication. Read the Master Brief and verification results first.

1. Verify that each destination directory is the new extracted project, not an original repository or an accidentally inherited parent Git root. Preserve original repositories untouched.
2. Review the final tracked-file allowlist. Exclude old Git history, old prompts, outputs/caches, virtual environments, model weights/adapters, secret files, and private datasets. Retain required notices and small approved fixtures.
3. Verify that each repository has its own dependencies, prompt/assets, configuration example, run instructions, and truthful verification status. Check complete English/Japanese documentation parity, language-switch links, and bilingual explanatory comments. Resolve required factual confirmations before declaring the baseline complete.
4. Initialize a fresh Git history in each new directory. Commit the clean baseline, guidance, and OpenSpec files. No history import, subtree migration, or history-rewriting tool is needed for this requested outcome.
5. Use the explicitly supplied company GitLab namespace and remote URLs. Do not use personal GitHub or guess a public destination. Create private/internal projects according to the supplied company choice if creation is requested and supported.
6. Check remote state before pushing. If a destination already contains unrelated commits/files, report the conflict and do not force-push or replace it. Do not overwrite an existing project to simulate a fresh start.
7. Push when the destination is known and publication is authorized. Verify remote branch/commit identity after the push and provide the three repository URLs and commit IDs.

If live validation is blocked, prepare the clean repositories and list the exact remaining checks. Do not label them fully verified or publish them as complete unless I explicitly choose to publish with the documented limitation.

## New-chat continuation prompt

Read CURSOR_INSTRUCTION_PACK.md, the current AUDIT.md, and the relevant extraction/verification notes. Continue only the named stage/project. Do not restart the audit from scratch if its evidence remains applicable. Verify that referenced files still exist and resolve changed facts before relying on them. State the next concrete action, then perform it. Ask only for genuinely missing information that blocks that action.

## Reference documentation

Reviewed 2026-10-22; verify installed-version behavior before execution:

- https://github.com/Fission-AI/OpenSpec
- https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md
- https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md
- https://github.com/Fission-AI/OpenSpec/blob/main/docs/workflows.md
- https://cursor.com/docs/rules
