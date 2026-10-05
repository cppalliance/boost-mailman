# Boost Mailman re-skin

The Boost mailing-list site (Postorius list management plus HyperKitty archives) restyled to look like boost.org, without forking the Mailman apps.

## Language

### Markup

**Stock markup**:
HTML produced by the installed Mailman apps (HyperKitty, Postorius, django-mailman3, allauth) that we do not own and cannot change.
_Avoid_: upstream HTML, default markup

**Template override**:
A copy of a single stock template that we own and edit, allowed only for the templates on the approved list.
_Avoid_: fork, template copy

### Pages

**Page**:
One screen of the site, identified by its Mailman route name (for example `hk_thread`, `list_summary`).
_Avoid_: view, screen, page type

**Page group**:
A named set of Pages that render the same stock layout and so share styling. A Page belongs to at most one Page group; a Page in none is ungrouped.
_Avoid_: page type, section, route list

**Post group**:
The archive reading Pages: a thread and a single message.
_Avoid_: thread pages, message group

**HyperKitty form group**:
HyperKitty Pages that are a title over one form: new message and the message, thread and list delete confirmations.
_Avoid_: message group, delete pages

**Account group**:
The signed-out allauth Pages rendered as one centred card: sign in, sign up, sign out, password reset and email confirmation.
_Avoid_: auth pages, login pages

**Settings group**:
Pages whose content sits under list, user or profile navigation: list administration, user preferences, signed-in account settings and archive user profiles.
_Avoid_: admin pages, tabbed pages

**Index group**:
The site-wide directory Pages whose table rows stack as cards on small screens: the list index, domains and users.
_Avoid_: list pages, tables

**List home group**:
The two front pages of one list: its Postorius summary and its HyperKitty archive overview.
_Avoid_: list pages, overview pages

**Signed-in view**:
A Page whose layout changes for an authenticated visitor, such as a list summary that gains the list navigation.
_Avoid_: admin view, logged-in variant

### Styles

**Vendored styles**:
The boost.org v3 design-system files we actually use, copied whole and never edited; files we do not use are not kept.
_Avoid_: vendored layer, design system, v3 CSS

**Component**:
A reusable visual unit of boost.org's design (button, card, tab, table, header) that stock markup is styled to resemble.
_Avoid_: widget, element, module

**Custom styles**:
The CSS we write on top of the Vendored styles to make stock markup look like boost.org.
_Avoid_: custom layer, overrides, custom CSS, theme

**Layer**:
A CSS cascade layer (`@layer`). Used only in this sense.
_Avoid_: using "layer" for a group of files

**Stock layer**:
The cascade layer that holds every stock stylesheet, so the Vendored styles and Custom styles beat it regardless of specificity.
_Avoid_: stock CSS layer, Bootstrap layer

**Vendor layer**:
The cascade layer that holds the Vendored styles, above the Stock layer, so the unlayered Custom styles beat it regardless of specificity.
_Avoid_: vendored layer (for the files themselves), v3 layer

**boost-important**:
The cascade layer for the few Custom styles declarations that must beat a stock `!important`, written in blocks inside the owning file.
_Avoid_: important.css, unlayered !important (except inline-style fights)

## Decisions

### Pages are found by route name and Page group

We can't change Stock markup, so Custom styles need another way to tell which Page they are styling. Both base overrides write the route name and its Page group onto the body:

```html
<body class="v3 page-{{ request.resolver_match.url_name }}" data-page-group="…">
```

Route names are Mailman's own stable identifiers (templates use them in `{% url %}`). The route-to-group mapping lives in one place, `boost/templates/boost/page-group.html`. The attribute holds one value, so a Page belongs to at most one group. Page styles are scoped by `[data-page-group="…"]`, using one level of native CSS nesting. A Page that needs styling its group does not explain is targeted by its route next to the group (`.page-<route>`), and the mismatch is logged as a candidate visual fix instead of being quietly folded into a group. A route check fails when a route name used in the partial or the CSS no longer exists in the installed apps.

Rejected:
- **Guessing the Page from its content** (`[role="main"]:has(#id_display_name):not(:has(.nav-pills))`): broke silently on markup changes and pushed specificity up until every override had to escalate.
- **Route lists repeated as `:is(.page-…)` selectors in each file**: the copies drifted apart.
- **A Python context processor**: deployment ships only templates and static files, so this would add a Python deploy path and a settings change for a lookup table.
- **A second class (`page-group-post`)**: it shares the `page-` prefix with Bootstrap's `.page-header` / `.page-item` / `.page-link`, and a class list cannot enforce one group per Page.

### Cascade layers decide who wins, not specificity

Both base overrides declare `@layer boost-important, reset, stock, vendor;`.

- `reset` holds `reset.css`. It sits below stock because its `:where()` preflight is meant to lose to Bootstrap Reboot.
- `stock` holds every stock stylesheet (Bootstrap, django-mailman3, Postorius, HyperKitty, jQuery UI, Font Awesome). Plain files use `@import url(...) layer(stock)`; HyperKitty's `{% compress css %}` block is wrapped in `@layer stock { … }` by two same-media inline hunks.
- `vendor` holds the Vendored styles, so they beat stock.
- Custom styles are unlayered, so they beat both at natural weight. `.v3` is not a specificity tool outside `reset.css`.
- `boost-important` takes only the custom declarations that must beat a stock `!important` (an unlayered `!important` loses to a layered one). An `!important` that fights an inline style or another custom rule stays unlayered.

### Components own their states

Each component file owns every state of its Component: rest, hover (gated to `(hover: hover)`), focus, active, disabled and transition. Page files only specialise Components within their Page scope, and no file undoes another. `colour.css`'s global link rules use `:where()` in every state, so a Component that colours its links owns their hover and focus too.

Shared looks on Stock markup are one rule with a grouped selector list, never a utility class. In Template overrides, markup names the Component it renders (`class="boost-card boost-about-card"`): a Component class, plus a role class for page-specific specialisation. No class names a single property.

Rejected: **centralising hovers in one motion file**, which spread every hover across three places (base, gated restatement, touch undo).

### Consequences

- Minimum browsers are Chrome 120, Safari 17.2 and Firefox 121, because of nesting and the remaining structural `:has()` uses.
- A Mailman upgrade that adds or renames routes fails the route check until the partial and the CSS route lists are updated.
- Pages without a resolved route (404s) get an empty `page-` and `data-page-group`, so only Component styling applies.
- Changing the compress block needs `compress` and a worker restart. Every hunk in it must keep the same `media`, or the output splits and leaves the layer open.
- A stock stylesheet added outside the `stock` layer wins on specificity again.
- Layered `!important`s invert: a vendored `!important` loses to a stock one and beats an unlayered custom one.
