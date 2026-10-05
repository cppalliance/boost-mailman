# Maintaining the re-skin

Recipes for everyday changes: restyle a button, change a colour, adjust one
page. The vocabulary (Stock markup, Page, Page group, Component, Custom
styles, Layer) is defined in [CONTEXT.md](../CONTEXT.md); the template
inventory is in [template-overrides.md](template-overrides.md); known gaps
are in [known-issues.md](known-issues.md).

## Find the rule that styles something

Inspect the element in DevTools, then search for its class under
`boost/static/boost/css/`. Every Component has one owner file, so there is
one place to edit.

Components: `buttons.css`, `forms.css`, `tables.css`, `tabs.css` (nav-pills
and nav-tabs), `cards.css` (shared card surface), `alerts.css`, `badges.css`,
`pagination.css`, `dropdowns.css`, `avatars.css`.

Chrome: `chrome.css` (adapts the vendored header/footer to Mailman pages).

Page areas: `post.css` (thread and single-message pages), `post-sidebar.css`
(their sidebar, tags, votes), `thread-rows.css` (thread lists and the
overview tabs), `archives-index.css` (`/archives/`), `search-results.css`,
`list-index.css` (Postorius list/domain/user indexes), `list-overview.css`
(HyperKitty list overview and its join card), `list-pages.css` (Postorius
list summary), `account.css` (sign in/up/reset cards), `admin.css` (role
pills, members stack, admin tables).

Base: `reset.css`, `typography.css`, `colour.css` (page colours and the
shared focus ring), `shell.css` (containers).

Script: `boost/static/boost/js/row-links.js` makes a whole table row follow
its link on the list index, subscriptions and HyperKitty profile tables.
A new clickable table needs its row selector added to the script's `ROWS`
list and a `cursor: pointer` rule in its CSS file.

The vendored boost.org files under `boost/static/boost/vendor/` are never
edited; see [their README](../boost/static/boost/vendor/README.md).

House style: comments explain a Bootstrap, HyperKitty, allauth or browser
constraint, nothing else.

## Change a button

Every variant only sets custom properties: `--boost-btn-bg`,
`--boost-btn-border` and `--boost-btn-fg`, plus their `-hover`, `-focus` and
`-active` values. One `.btn` rule reads them (header comment of
`buttons.css`). So:

- Recolour a variant: change its custom properties in the
  "Variant mapping" section of `buttons.css`.
- Add a variant: copy an existing block and change the properties.
- Hover colours are applied by the `@media (hover: hover) and (pointer:
  fine)` block near the end of the file; set `--boost-btn-*-hover` on the
  variant, and the block picks them up.

The mapping from Bootstrap's variant names to the boost.org look:
`btn-primary` and `btn-success` are the dark primary button; `btn-teal` is
for teal cards; the "start a new thread" links are a small mustard accent
button; held-message Accept is green; `btn-secondary`, `btn-outline-*`,
`btn-info` and `btn-warning` are the outline look; `btn-danger` is the
error look.

## Change a colour, font size or spacing

Use the design tokens: `--color-*`, `--font-size-*`, `--space-*`,
`--border-radius-*`, from `boost/static/boost/vendor/v3/css/01`-`05`. Never
edit the vendor files. If a token's value is wrong for one element, override
that property in our CSS; do not redefine the token globally.

## Change one page, or one kind of page

Both base overrides put the Mailman route name and its Page group on
`<body>`:

```html
<body class="v3 page-{{ request.resolver_match.url_name }}" data-page-group="…">
```

- A whole Page group: scope with the attribute, one level of native
  nesting: `[data-page-group="settings"] { … }`. The groups are named and
  listed in `boost/templates/boost/page-group.html`.
- One page: scope with `.page-<route>` next to the group, with a comment
  saying why the group is not enough.

Put the rule in the file that owns the page area (see the map above), not
in a new file.

## Change the header or footer

Markup: `boost/templates/boost/chrome-header.html` and
`chrome-footer.html`; both base templates include them. Styles:
`chrome.css`. The logo image is vendored
(`boost/vendor/v3/img/Boost_Symbol_Transparent.svg`).

## Add a CSS file

Prefer extending the owner file. If a file is genuinely new, add a
`<link>` to `boost/templates/boost/stylesheets.html` in the group its
header comment names. The order matters, because later files specialise
earlier ones. Keep files under 500 lines.

## See your change locally

CSS and templates reload on a hard browser refresh (Cmd+Shift+R). If
HyperKitty pages still show old CSS, the compressed stock CSS is stale:
`docker compose restart mailman-web`.

Check at desktop and phone width, signed out and signed in. The seeded
superuser is `admin`. The image entrypoint creates it with
`createsuperuser --noinput`, which leaves no usable password, so set one
once: `docker compose exec mailman-web python manage.py changepassword
admin`. Hover the thing you changed.

## "My rule doesn't apply"

The usual causes, most frequent first:

1. **The rule is inside `@media (hover: hover) and (pointer: fine)`.**
   Hover styles only apply to a real mouse. DevTools touch emulation
   disables the media query; test with a real pointer or force the
   pseudo-class.
2. **Another Custom styles rule has higher specificity or loads later.**
   Find it in DevTools (the winning rule is struck through in yours) and
   edit that rule instead of adding a stronger one.
3. **Stock has an `!important`.** An unlayered `!important` loses to a
   layered one, so put your declaration in an `@layer boost-important { … }`
   block in the same file.
4. **The page is not in the group you scoped to.** Check
   `data-page-group` on `<body>`, and the group list in
   `boost/templates/boost/page-group.html`.

The full layer order and reasoning is in [CONTEXT.md](../CONTEXT.md),
"Cascade layers decide who wins, not specificity".

## Edit or add a template override

Only when CSS cannot do it (CSS cannot wrap elements, add markup or change
text). The copied templates live under `hyperkitty/templates/` and
`postorius/templates/`.

- **Edit an existing override.** Keep the stock ids and classes, because
  HyperKitty's JavaScript reads them. Update the file's entry in
  [template-overrides.md](template-overrides.md).
- **Add one.** Copy the stock file out of the container (the command is in
  the repo [README](../README.md)), commit it unchanged first, then commit
  your edits so the diff shows only your changes, and add a
  template-overrides.md entry: upstream version, why, and the diff.

## Don't "fix" these

Awkward CSS that stock markup forces. They look like smells but each has a
reason (recorded in a comment at the spot):

- `!important` against Bootstrap's own `!important` utilities.
- ID-scoped selectors against HyperKitty's ID rules.
- Hiding with a clip instead of `display: none` where HyperKitty's JS reads
  the DOM.
- URL-matched selectors (`[href*="message/new"]`) on stock links that have
  no class to hook.
- The role-pill `nth-child` rule in `admin.css`.
- Clickable table rows are JavaScript (`row-links.js`), not a CSS stretched
  link. Safari does not contain a `position: absolute` `::after` in a
  `position: relative` `<tr>`, so the overlay covers the whole table and
  every click goes to the last row.
- The admin nav's `li.dropdown` is `position: static` under 768px. The
  scrolling row would otherwise clip its menus.

## Upgrading Mailman

When HyperKitty or Postorius changes version:

1. Diff each override against the new stock file. The version it was
   copied from is in the file's header comment and its
   [template-overrides.md](template-overrides.md) entry. Bring the stock
   changes across.
2. Run the route check below.
3. Check that HyperKitty's compressed CSS still opens with
   `@layer stock{` (view source, first line of the compressed file). If it
   does not, the stock CSS is not layered and wins again. The base
   template's compress block is where to fix it.
4. Update the version numbers in the override comments and docs.

### Route check

Every route name used by `boost/templates/boost/page-group.html` or by a
`.page-<route>` selector in the CSS must exist in the installed apps. After
a Mailman upgrade (or after editing either side), run:

```bash
docker exec -w /opt/mailman-web boost-mailman-web python3 manage.py shell -c '
from django.urls import URLResolver, get_resolver
def walk(ps):
    for p in ps:
        if isinstance(p, URLResolver): yield from walk(p.url_patterns)
        elif p.name: yield p.name
print("\n".join(sorted(set(walk(get_resolver().url_patterns)))))' > /tmp/routes.txt
{ grep -oE 'r == "[a-z0-9_]+"' boost/templates/boost/page-group.html | cut -d'"' -f2
  grep -ohE '\.page-[a-z0-9_]+' boost/static/boost/css/*.css | sed 's/^\.page-//' | grep -vxE 'header|item|link'
} | sort -u | comm -23 - /tmp/routes.txt
```

Any output is a route name that no longer exists. That page lost its
Mailman route, and its styling will silently disappear. Fix
`page-group.html` or the CSS, then re-run until it prints nothing.