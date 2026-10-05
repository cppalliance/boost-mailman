# Known issues

Small gaps and inconsistencies the redesign shipped with, and what fixing
each one would involve. Nothing here is broken for a visitor. Fixing any
of it is a design decision, not a bug fix, so check with the site owners
first.

Background on the approach is in [CONTEXT.md](../CONTEXT.md); recipes for
making changes are in [maintaining.md](maintaining.md).

## Accessibility and interface gaps (template-only fixes)

- **No skip link.** The header is read on every page before the content.
  A "skip to main content" link, hidden until focused, is the standard fix.
  It needs markup, so it belongs in
  `boost/templates/boost/chrome-header.html`.
- **The footer's social link group isn't announced.** `chrome-footer.html`
  wraps the icon links in `<div class="footer__social" aria-label="Social
  links">`, but a plain `div` with an `aria-label` is ignored by screen
  readers. Give it a landmark role (`<nav>`) or label each link's container
  differently.
- **Search placeholders don't end in an ellipsis.** The placeholder text
  comes from the stock templates ("Search…"-style). Trailing ellipses are
  a small boost.org convention; changing them means overriding the search
  form templates.

## Interface gaps that change visuals

These have visible effects, so they were left for a decision:

- **Form fields under 16px zoom on iOS.** Focusing a smaller field makes
  Safari zoom the whole page in. Raising inputs to 16px changes their
  proportions across every form.
- **No `text-wrap: balance` on headings.** Multi-line card and page titles
  can leave a short trailing word.
- **No `touch-action` or tap-highlight on header controls.** Touch targets
  in the header use mouse-oriented hover states only.
- **No `scroll-margin-top` under the sticky header.** Anchor jumps land
  with the target hidden behind the header.
- **No `color-scheme: light`.** Native controls (scrollbars, form
  elements) render dark on dark-mode OSes with a light site.

## Known style inconsistencies, kept on purpose

The redesign's first pass had one rule: change nothing visually, only
restyle. Where boost.org's look and Mailman's markup disagreed, the
existing pixels usually won. These are the surviving cases:

- **The signup and login pages treat their bottom link differently.**
  Signup's "sign in" link is underlined; login's matching "sign up" link
  is plain (see the comment near the end of `account.css`). Make them
  match if a direction is chosen.
- **`manage_user` borrows the list summary's spacing.** It shares
  `list-pages.css` rules with the list-home group for lack of its own
  spec.
- **The list summary's card paragraphs were never styled.** Secondary
  colour and constrained width were authored for the About/subscribe card
  text but never rendered, so the declarations were dropped rather than
  kept dead.
- **Bad-token pages render without the account card.** The allauth card
  (`account.css`) only applies when the page contains a form; the
  invalid-token reset and failed-confirmation pages show a bare error
  paragraph instead.
- **Links inside message bodies don't get the body link look.** There is
  no `.email-body a` rule, so links in archived emails keep Bootstrap's
  default styling rather than the site's link look.
- **The archive overview and `global_bans` borrow Settings-group rules.**
  Their tables and containers are styled as if they were settings pages
  (`admin.css`, `tables.css`). Close enough to pass, not designed.
- **Overview thread headings render at HyperKitty's size.** `thread-rows.css`
  styles weight and colour but not size or family, so the stock 18px
  Display survives; the v3 look would be a 16px sans.
- **HyperKitty values kept over the Component spec.** With stock CSS in a
  layer, our rules would win, so these files re-apply HyperKitty's values
  to keep the old pixels: the `span.new` badge size (78%,
  `archives-index.css`), `table.user-data` (95%, `tables.css`), the
  reattach-search button (12px, `buttons.css`), and the sort-mode active
  underline (4px, `archives-index.css`). Bringing them to the v3 spec is a
  visible change, one rule at a time.

## Loose ends

- **The bans and last-posts tables were only checked with hand-injected
  rows.** The seed data has none, so their empty and populated states
  beyond that are unverified.
- **Every table's row hover underlines its links, clickable or not.**
  `.table tr:hover td a:not(.btn)` in `tables.css` underlines a row's
  links when the pointer is anywhere in the row. On tables whose rows
  are clickable (list index, subscriptions, HyperKitty profile tables,
  `/archives/`) that is right. On the others, the members table for
  example, it suggests a row click that does nothing. The fix is to scope
  that rule to the clickable rows, which changes how the other tables
  look on hover.
- **Tables without a `<thead>` get the card frame but no header strip.**
  The `tables.css` frame and the header background are separate rules;
  heading-less tables look slightly unfinished.
- **Optional: load one CSS file instead of 33.** The stock templates
  compress their CSS; our `<link>` per file is deliberately outside that
  pipeline (see the stylesheets include). Moving it inside the
  `{% compress %}` block would need a Mailman-side check that the layer
  declarations survive compression.