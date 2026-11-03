---
title: A design system is a review policy, not a library
tag: Craft
summary: Importing a token package changes nothing. The system holds when the correct choice is easier than the wrong one, and when review refuses the local override.
---
A design system is a set of decisions, and review is what enforces them. The package is only where the decisions live. Once those two come apart, and they come apart quietly, what is left is a colour palette with a README.

I have watched more than one design system die at screen three. The failure is always the same and never looks like a design problem at the time. Someone had a deadline, the component almost fit, and they wrote the value inline. That file is now the precedent.

::fig design-review

## Three copies of every value

In a healthy system a colour comes from exactly two places: the design source, and the token that mirrors it. In a real codebase there is a third, the literal somebody pasted into a view, and that is the one that ages badly. It does not break. It drifts, one hex at a time, until nobody can change the brand colour without a treasure hunt.

::fig design-copies

## What makes it stick

- **Token names describe intent, not value.** `surface`, `danger` and `border-subtle` survive a redesign. `grey300` does not, and it invites the next person to pick a neighbouring number by eye.
- **The default has to be the correct one.** If using the system is harder than not using it, the system loses every time to someone under pressure. Convenience beats policy.
- **The component owns its spacing.** A system where every screen re-specifies the padding of the same button is a component in name only.
- **Review rejects the override.** This is the enforcement. Not a lint rule or a guideline, but a person saying no, in a review, with a reason. The first few of those set the norm for the next hundred.

## What I check in review

- No raw colour values outside the tokens file. None, including "just for the shadow".
- No font sizes written as numbers in a view.
- Spacing from the scale, not `13` because it looked right that afternoon.
- A component not re-specifying spacing it already defines.
- For a new token: does an existing one already mean this? Duplicated intent is how a token file becomes a colour palette.

## The cost, said out loud

A design system slows down the first screen and speeds up the tenth. That is the whole trade, and it is a bad deal if you only ever build one screen. Teams abandon systems because nobody said the first half of that sentence, so the first screen feels like overhead and the tenth never arrives.

Say it in the same breath as the plan. "This will be slower for a fortnight and faster after that" is a sentence a team can agree to. "We are adopting a design system" is not.

## The design side is a person, not a handoff

The systems I have seen work have a designer who reads the diff, or a developer who keeps the design file open. The ones that fail have a Figma link and a prayer. The gap between the mock and the implementation is where defaults get invented, and invented defaults are the start of the third copy.

None of this is about tooling. It is about which choice is the path of least resistance on a Thursday afternoon, and who is standing between the deadline and the hardcoded hex.
