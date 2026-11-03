---
title: AI-native development is a process, not a feature
tag: Process
summary: What I write down so an agent is useful inside a real codebase: the conventions file, the brief, the one piece of evidence I accept, and the parts I refuse to hand over.
---
"AI-native" describes how an app gets built. Nothing about it ships inside the app. The engineering that matters is not the model either. It is the document you write so a tool with an empty context window can work inside a codebase that took years to shape.

I have spent recent weeks setting this up on my own projects: an agent harness in the editor, skills, plugins. The installation is the easy half. These are the rules that survived contact.

## The agent starts every task with nothing, so the document is the memory

The first surprise is how much of a good brief turns out to be a restatement of rules nobody had written down. Which language mode. Which deployment floor. Which layer may call which. What "done" means. When to stop and ask instead of trying harder.

Those conventions used to live in a senior engineer's head and in the review comments of a dozen pull requests. A tool with an empty context window can read neither. Written down once, they become what every task is briefed from. That is why the file matters more than the prompt, and why "I run an agent in my editor" describes almost none of the work.

## What the IDE now gives you, and what it does not

This stopped being a bolt-on. The Xcode 26 release notes describe "coding intelligence features that help you write code, generate tests and documentation, fix errors, refactor existing implementations, and navigate codebases", with a model of your choosing, including one that runs locally on Apple silicon.

Xcode 27 pushes in exactly the direction of this post: "Planning with agents is now first class in Xcode. Plans appear as editable Markdown artifacts next to the conversation", to review, annotate, discuss and approve before the agent proceeds. And the Xcode MCP server's tools now reach real platform state: the active run state, the debugger console, schemes and run destinations, build settings, compiler flags, entitlements and Info.plist keys.

That list deserves two readings, because two of its items are the whole discipline in miniature. A plan you must approve before work starts is a review gate placed at the cheapest possible moment. Entitlements and Info.plist behind a tool call means the blast radius of a careless instruction now includes your signing configuration.

What the platform still does not ship is the part specific to your codebase. The harness is general. The conventions are not. That asymmetry is where a person's leverage sits.

## Four things I write down before the first task

::fig ai-brief

- **Conventions.** What the compiler and linter enforce and, more usefully, what they cannot: which layer may depend on which, where a string comes from, what an error is allowed to say.
- **Boundaries.** The files an agent may touch and the ones it must stop at and ask about. Credentials, permissions, payments, privacy surfaces and anything that leaves the machine are always on the second list.
- **Definition of done.** The exact command that proves the change. Not "looks right": a build, or a test that was red and is now green.
- **Stop conditions.** After a few failed attempts, re-plan instead of trying harder. Never delete or skip a test to reach green. Never widen the scope of a change without saying so.

The shape, as a pattern and not anyone's real file:

```
Conventions        language mode, deployment floor, layer rules, where strings live
Boundaries         may touch: <paths>. must ask: credentials, permissions, payments
Definition of done the one command that proves it
Stop conditions    three failed attempts, then re-plan. never skip a test. never widen scope
Roles              who plans, who writes, who verifies, who is allowed to fix
```

::fig ai-gate

## Two rules about what never goes into a prompt

**Secrets and paths.** A key prefix or a home-directory path is not prose, so a word-by-word blocklist can never anticipate it. The check has to be shaped, not spelled. This site's own content check fails the build on a key-shaped string or a `/Users/<name>/` path in the published output. Not because a blog post would contain one, but because that class is guessable, and a script can hold a guessable class.

**Transcripts.** A real transcript is a document about your job. A pattern is a document about your craft. So I show the structure of a brief, the invariant, the constraint and the evidence, and never the text. The text carries whatever the session happened to contain, and nobody can write the blocklist for a conversation in advance. This is the rule I broke most often before I wrote it down.

## What stays a person's job

**Specificity.** App Review is blunt about it: guideline 2.3.1(a) requires new features to be "described with specificity in the Notes for Review section of App Store Connect (generic descriptions will be rejected)". A generic description is exactly what a templated draft does well: plausible, complete-looking and about nothing. The model can draft. The specificity has to be mine.

**The irreversible.** Deployments, credentials, purchases, anything a revert cannot undo.

**The shape of the whole.** Whether the feature should exist, where the seam belongs, which of two working designs will still be right in a year. An empty context window does not make any of that easier to delegate.

The pattern keeps repeating: agents are good at the parts of engineering that are typing and bad at the parts that are deciding. Most of the value of setting this up is the writing down, being forced to say in plain language which is which.
