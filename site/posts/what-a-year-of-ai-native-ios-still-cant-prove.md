---
title: What a year of AI-native iOS development still can't prove
tag: Process
summary: I audited the agent setup behind a year of iOS work and scored it seven out of ten. Nine failure modes, each with the number that makes it concrete, and the two gaps that keep it from a ten.
---
I gave my AI-native iOS setup a year, then audited it. The score was seven out of ten. The strong parts were the ones I had built on purpose: a context file every tool reads, specs that survive a handover, guardrails around what an agent may touch, and a verification path that ends in a command. The weak parts were the ones I assumed would take care of themselves: measurement and portability.

That gap is the useful part. Nine failure modes follow, each with the number that makes it concrete instead of a feeling.

## The file that made the repo legible became a second copy of it

The highest-leverage file in the repo was the root `AGENTS.md`. `CLAUDE.md`, `GEMINI.md` and the Copilot instructions were symlinks to it, so every tool read one source. For a while that was the whole trick: an agent starts with an empty context window, and this was the one document it could not miss.

::fig year-file

Then it grew to 18 KB. Somewhere along the way it stopped pointing at the design docs and started summarising them. Two copies of the same rule, one in the pointer and one in the doc it pointed to, with no way to tell which was current. A pointer file stays a pointer or it becomes a second truth. The fix was deletion: keep the index and the non-negotiables, link the rest.

## A doc twelve decisions behind is a trust bug, not a typo

Thirteen ADRs, one per decision that would otherwise live in a review thread. Each answers why, the question a new agent cannot infer from the code. The failure mode is staleness. An index that lists twelve when there are thirteen is not a formatting problem. It tells the next reader, human or model, that the missing decision never happened.

Once a doc lies, it gets ignored, and then it may as well not exist. The fix is a freshness check in CI: every ADR is indexed, every index entry resolves, and the check fails on a doc that no longer matches the code it describes. A reminder is not a check.

## A rule violated twice is a script, not a sentence

Two things held without argument: the secret scan and SwiftLint, both in pre-commit. One thing did not: a paragraph in the conventions file telling agents how to write a merge request body. It was violated twice in a week. That is the threshold. The second violation is the signal that the rule needs a mechanism, not more emphasis.

::fig year-rules

So it became a script, and so did two other rules that kept slipping. One checks that every new file is registered where the build expects it. One checks that the docs index matches the docs on disk. An agent writes either in minutes, so cost is no longer the excuse.

## Four narrow agents beat one clever one

The setup ran four roles: an architect that plans, a reviewer that reads, a qa agent that tests, and a fixer that repairs. The important part was not the division of labour. It was the capability limits. qa could not edit a file. The fixer could not push. A reviewer that can quietly fix stops reviewing and starts patching, and the review becomes a formality.

::fig year-roles

Narrow roles without limits are just four prompts with the same permissions. The limits are what make the roles real.

## Verification is the whole trick

Every claim an agent makes has to end in a command. Build through one path, compare against snapshot references, run CI on a machine with a simulator per slot. Determinism is what makes "it builds" checkable. Without it the sentence is a paragraph, and a paragraph is not evidence.

The failure mode is not a broken build. It is a green sentence with no command behind it, repeated until everyone believes it. I stopped accepting the sentence.

## The most valuable reasoning in the repo was the part I did not track

Plans, ledgers, the record of what was tried and abandoned: 42,770 lines, all gitignored. The code was tracked. The reasoning that produced it was not. That is backwards. A plan is the cheapest artifact to keep and the most expensive to reconstruct, especially for an agent that has to re-derive the constraints from scratch.

Commit the plan and the progress log. Ignore only the review packages, which are large, generated and disposable.

## Portability is the unpaid bill

162 skills lived on my machine. The config lived in one home directory. The app targeted an iOS 26 API while the deployment floor was 17.6, which meant the clever parts only worked on the newest runtime. None of that travels with a clone. Whoever picks up the repo gets the code and none of the setup that made the code cheap to change.

The fix is boring: vendor the six skills actually used, pin them to the supported version, and write a setup script a fresh machine can run. The other 156 are a personal library, not a dependency.

## You cannot improve what you do not count

I had no numbers on dispatch, rework or defects. I could tell you the setup felt faster. I could not tell you whether a change to the context file reduced rework or just changed its shape. Taste is a fine reason to try something. It is a bad reason to keep it.

A handful of golden tasks, re-run whenever the config changes, would turn the argument into evidence. Not a benchmark suite: five tasks with known-good outcomes, a fixed command, and a note on what moved.

## The agent-friendly CI and the safe CI are not the same CI

The pipeline that let agents move quickly was not the pipeline that contained them. Three conveniences did the damage: the self-hosted runner was unprotected, deploy jobs were allowed to fail, and the coverage gate was piped to true so a red result could not stop a release. Each made the happy path faster and the failure path quieter.

The fix is separation: a fast lane for agent feedback and a protected lane for anything that ships, with required gates that a convenience flag cannot skip. Convenience and safety are both real requirements. They just do not belong in the same job.

Seven out of ten is not the point. The gap is. The setup is strong exactly where I spent the time, context, specs, guardrails and verification, and weak where I assumed the tooling would cover me. That is a more useful map for the next year than another list of things that worked.

The setup was never the product. The evidence was.
