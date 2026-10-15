# Lenses — <project or "all projects"> (<first date> – <last date>, N messages)

> The example lenses below are fictional, to show the shape. Replace them all.

## Lenses

### 1. Fixed in one place, stale everywhere else
- **Rule:** when a pattern changes, every instance changes in the same pass.
- **Look for:** the same component styled differently across screens; old copy left in a second file; a constant duplicated instead of shared.
- **Quotes:** "you fixed it on the settings page but the profile page still has the old one" (03-14) · "make it global, not per screen" (04-02)

### 2. Nothing jumps while loading
- **Rule:** no layout shift, flicker or late-appearing text on first paint or on back-navigation.
- **Look for:** content whose height depends on async data without a placeholder; images without size; text that swaps after hydration.
- **Quotes:** "the header jumps every time I come back" (03-20) · "it flashes the default avatar first" (05-01)

### 3. Copy must match the current state
- **Rule:** labels and prompts reflect what is true for this user right now.
- **Look for:** "free trial" shown to people who already used it; "add to home screen" inside the installed app; plan text that ignores the selected plan.
- **Quotes:** "why does it still say 7 days free after I picked monthly?" (06-11)

<!-- 8–15 lenses in total, most frequent or emphatic first -->

## How they decide
- Wants to **see it** (screenshots, a running build) before choosing — "I can't decide without seeing the screen" (04-18).
- Wants it to **match a reference** product they already shipped.
- Prefers **a recommendation**, not a menu of equal options.

## Standing rules
- "From now on, always run the full check before you say it's done." (05-09)

## Tells
- "...again?" · "this looks cheap" · "why is X there?" · repeated question marks

## Open threads
- [ ] Sign in with Apple — "later, after the first release" (03-02); not seen done.
- [ ] Clean up old test accounts — asked 06-20; no follow-up.
