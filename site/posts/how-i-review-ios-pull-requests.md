---
title: How I review iOS pull requests
tag: Behaviour
summary: Risk before style, deletion before addition, and three questions I ask on every diff. What I refuse to merge, and why the comment that explains the failure mode is worth ten that state the rule.
---
If a review opens with naming, the most useful attention is already spent. This is the order I read a diff in, and the things I will not merge.

## The order

::fig review-order

- **Does it do what the description says?** Not what the code says, what the description claims. If they diverge, that is the first comment, before anything else.
- **Can it crash?** Force unwraps, array indexing, casts, anything that assumes a shape it has not checked.
- **What is the failure path?** Every network call fails. Every write can be interrupted. A diff that handles only success is half a diff.
- **What was deleted?** Removed guards and removed tests first.
- **Style.** Last, and usually not at all.

## Three questions, every time

- **What happens on a slow network?** Not down, slow. That is where double submissions, spinners that never resolve and buttons that fire twice live.
- **What happens if the user backgrounds the app mid-operation?** Very few diffs survive this question untroubled, and the ones that do are the ones I trust.
- **What happens the second time?** Is the operation idempotent? Retrying a payment, a submission or a sync is where data loss is born.

## What I refuse to merge

- A skipped or disabled test. If it cannot pass, delete it and say so. A disabled test is a lie that gets inherited.
- A test that asserts nothing, or asserts the mock.
- `try?` on a write. Swallowing a failed save is how a user loses an hour of work and nobody finds out.
- A new dependency for something the platform already does.
- A control with no accessibility label. That is not a later ticket. It is an unfinished control.

::fig review-comment

## Concurrency, because that is where the crashes are

Most of the real defects I find in review are structural, not logical:

- A task started from a view that outlives the view and writes to state after it is gone.
- State mutated off the main actor that a view reads on it.
- Two writes racing to the same store with no single owner.

These do not need a deep read of the logic. They need one question: who owns this state, and on which actor is it touched? If the diff cannot answer in one sentence, that is the comment.

## Two habits that pay

**Review the smallest possible unit, early.** A large diff gets a shallow read and a rubber stamp, and both people know it. Several small diffs get real attention. If a change is too big to review carefully, the review is not the problem to fix. The change is.

**Explain the failure, not the rule.** "This will double-submit if the user taps twice before the response" teaches something. "Don't allow double taps" fixes this instance and brings the same bug back next month. The comment that names the failure mode is worth ten that quote the standard, and it is the difference between a review and a gate.

## What review is for

Not catching typos, and not proving the reviewer read the code. It is the last point at which the person who wrote something still remembers why, and someone else can ask "what happens when this goes wrong?" while the answer is cheap. Everything else about it is negotiable. That is not.
