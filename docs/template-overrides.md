# Template overrides

Copies of upstream Mailman templates, plus our own shared partials. The
inventory of every override and partial is this file; see the section list
for what is copied and what is deliberately left stock.

Every stock stylesheet loads into `@layer stock` (see Decisions in [CONTEXT.md](../CONTEXT.md)).
When an upgrade adds a stock `<link>` to a base template, or a child template
fills `additional_stylesheets` / `additionalcss`, load it into the layer too.
An unlayered stock sheet wins over the Custom styles on specificity again.

## `postorius/templates/postorius/base.html`

- **Upstream:** `postorius/templates/postorius/base.html` (Postorius 1.3.13)
- **Why:** site chrome (header/footer), the v3 class, stylesheets, and Plausible.
- **Diff vs the installed 1.3.13 file:**
  - `<html>` / `<body>` gain `class="v3"`; `<body>` also gets
    `page-{{ request.resolver_match.url_name }}` so CSS scopes by route, and
    `data-page-group` from `boost/page-group.html`.
  - The four stock `<link>`s (Bootstrap, django-mailman3 `main.css`, Postorius
    `style.css`, Font Awesome) are one `<style>`: `@layer boost-important,
    reset, stock, vendor;` then an `@import url(…) layer(stock)` per file, same order.
  - `{% include 'boost/stylesheets.html' %}` inside `{% block additionalcss %}`.
  - `<script defer src="{% static 'boost/js/row-links.js' %}">` after that
    block (full-row clicks on the list index, subscriptions and HyperKitty
    profile tables).
  - Plausible script in `<head>`.
  - Stock Bootstrap navbar (Lists / Domains / Bans / System Information / Users /
    Archives, Sign In/Up, gravatar dropdown, noscript user menu) replaced by
    `{% include "boost/chrome-header.html" with chrome_app="postorius" chrome_logout_next="list_index" %}`.
  - Stock documentation footer replaced by `{% include "boost/chrome-footer.html" %}`.
  - All other blocks, messages, scripts, and CSRF/logout URL usage stay.

## `hyperkitty/templates/hyperkitty/base.html`

- **Upstream:** `hyperkitty/templates/hyperkitty/base.html` (HyperKitty 1.3.12)
- **Why:** site chrome (header/footer), the v3 class, stylesheets, Plausible,
  and the removed `headers.html` include.
- **Diff vs the installed 1.3.12 file:**
  - `<html>` / `<body>` gain `class="v3"`; `<body>` also gets
    `page-{{ request.resolver_match.url_name }}` so CSS scopes by route, and
    `data-page-group` from `boost/page-group.html`.
  - jQuery UI and Font Awesome `<link>`s are one `<style>`: the same layer
    order statement, then `@import url(…) layer(stock)` per file.
  - Inside `{% compress css %}`: `<style media="all">@layer stock {</style>`
    first and `<style media="all">}</style>` last; `main.css` gains
    `media="all"`. The compressor joins same-media hunks in order into one
    file, so the output opens with `@layer stock{`. Keep every hunk at the
    same media, and run `compress` plus a worker restart after any change.
  - `{% include 'boost/stylesheets.html' %}` after `{% endcompress %}`,
    then `<script defer src="{% static 'boost/js/row-links.js' %}">`
    (outside `{% compress %}`, so no `compress` run is needed for it).
  - Plausible script in `<head>`.
  - Stock `headers.html` include is removed.
  - Stock sticky `nav#navbar-main` (brand, search `form name="search"`, Manage
    lists, Sign In/Up, gravatar dropdown) replaced by
    `{% include "boost/chrome-header.html" with chrome_app="hyperkitty" chrome_logout_next="hk_root" %}`.
    The include keeps `id="navbar-main"`, `form name="search"`, hidden `mlist`,
    `id="loginDropdownMenu"`, and Bootstrap `data-bs-toggle="dropdown"`.
  - Stock HyperKitty logo footer replaced by `{% include "boost/chrome-footer.html" %}`.
  - `{% include 'hyperkitty/top.html' %}`, the keyboard-shortcuts modal,
    messages, scripts, `{% block additionaljs %}`, and `bottom.html` stay.

## `hyperkitty/templates/hyperkitty/navbar-brand.html`

- **Upstream:** `hyperkitty/templates/hyperkitty/navbar-brand.html` (HyperKitty 1.3.12)
- **Why:** Boost symbol tile linking to the current app's index, used by the shared header.
- **Diff vs the installed 1.3.12 file:** stock was
  `<a class="navbar-brand" href="{% url 'hk_root' %}">{{ site_name }}</a>`.
  Ours is a `header__logo` link with the vendored Boost SVG and no site
  name. It goes to `hk_root` when `chrome_app` is `hyperkitty` (as stock
  did) and to `list_index` otherwise.

## Our partials (not upstream copies)

- `boost/templates/boost/chrome-header.html` — three-pill header. Included from
  both bases with `chrome_app` / `chrome_logout_next`. Sign Out is a CSRF POST
  form to `{% url LOGOUT_URL %}` with hidden `next`, not the stock GET
  `?next=` link: allauth 65 shows a confirm page on GET, so a GET href does
  not sign the user out. Same named URLs and destinations as the stock
  dropdowns; no new JS.
- `boost/templates/boost/chrome-footer.html` — one-line boost.org footer plus
  the Mailman credit line.
- `boost/templates/boost/stylesheets.html` — the only list of the Vendored
  and Custom styles files and their load order; its header comment states
  the groups. The vendored files are imported into `@layer vendor` and
  `reset.css` into `@layer reset`; the other Custom styles are unlayered.
  Stock stylesheets are not linked here: both base overrides declare
  `@layer boost-important, reset, stock, vendor;` and load every stock
  sheet into `stock`.
- `boost/templates/boost/page-group.html` — maps the route name to its Page
  group (see Page group and Decisions in [CONTEXT.md](../CONTEXT.md)).
  Both bases include it inside `{% filter slugify %}` so its line breaks do
  not reach the attribute. Re-run the route check in [maintaining.md](maintaining.md) after
  editing it or upgrading Mailman.

## `hyperkitty/templates/hyperkitty/thread.html`

- **Upstream:** `hyperkitty/templates/hyperkitty/thread.html` (HyperKitty 1.3.12)
- **Why:** Display 40px title, dotted meta row, and 48px byline. Stock
  `row` / `col-md-9` / `col-md-3` grid and newer/older header stay.
- **Diff vs installed:** the centre `h3` is a `header.post-header` (`h1`,
  meta including unread for authenticated users, byline). `#next-thread`,
  `#prev-thread`, `#thread-content`, `.sort-mode`, `#replies`, `.replies`,
  `.ajaxloader`, `#stats`, the right_col include, and `additionaljs` are
  unchanged.

## `hyperkitty/templates/hyperkitty/message.html`

- **Upstream:** `hyperkitty/templates/hyperkitty/message.html` (HyperKitty 1.3.12)
- **Why:** same title block; `strip_subject` so the list prefix matches the
  thread; byline role is "Original poster" only when
  `message.pk == message.thread.starting_email.pk`.
- **Diff vs installed:** the back-chevron + `h1` header is a `post-header`.
  Stock `col-lg-9` / `col-lg-3` row and right_col include stay.

## `hyperkitty/templates/hyperkitty/threads/right_col.html`

- **Upstream:** `hyperkitty/templates/hyperkitty/threads/right_col.html` (HyperKitty 1.3.12)
- **Why:** stock's export control is a bare `a.btn` child of
  `#thread-overview-info`. A consecutive-siblings card frame makes that
  Download button become the card's side edges; CSS cannot wrap it (press
  `transform` breaks pseudo-element frames).
- **Diff vs installed:** one wrapper `<div class="boost-card boost-thread-card">` around
  the stock blocks from `#thread-date-info` through `#fav_form`. Every
  id/class/form inside is unchanged. `#thread-overview-info` stays the outer
  section. `#tags`, `#add-tag`, `#participants`, the admin
  Reattach/Delete card, and `#unreadnavbar` are untouched.

## `postorius/templates/postorius/lists/summary.html`

- **Upstream:** `postorius/templates/postorius/lists/summary.html` (Postorius 1.3.13)
- **Why:** About card + teal subscribe card, matching the bottom row of
  boost.org's library pages. CSS
  cannot group the loose summary blocks or put the CTA card first on mobile.
- **Diff vs installed:** `{% list_nav %}` stays. One `.boost-list-summary`
  wrapper (plus `.boost-list-summary--signed-in` for an authenticated visitor,
  the Signed-in view) holds `.boost-card.boost-about-card` (description, info,
  owners, archives, admin metrics) and `.boost-card.boost-subscribe-card`
  (every subscribe / pending /
  subscribed variant). Forms keep `action`, CSRF, `form-horizontal`,
  `bootstrap_form_horizontal`, `#id_email` / `#id_display_name` /
  `#id_subscriber`, and unsubscribe `name="email"`. Each subscribe form
  gains one extra `<button type="submit" class="boost-subscribe-arrow">`
  (same POST, no JS). Stock `<hr>`s between sections dropped (cards frame
  themselves). Archives heading is `h3` so About stays the card title.
  `mailing-list-card.css` was not vendored (those class names are not
  emitted). Anonymous Sign In on the subscribe card is
  `class="btn btn-teal boost-subscribe-signin"` so `list-pages.css`
  can specialise it without a login-URL hook.

## `hyperkitty/templates/hyperkitty/overview.html`

- **Upstream:** `hyperkitty/templates/hyperkitty/overview.html` (HyperKitty 1.3.12)
- **Why:** teal "Join this list" card on the right column.
  CSS cannot insert subscribe markup.
- **Diff vs installed:** one `<section class="boost-card boost-join-card">` (teal
  surface from `list-overview.css`) at the top of
  `.col-md-3`: list name, one-line description, a teal Subscribe button
  (`btn btn-teal`) to
  `{% url 'list_summary' list_id=mlist.list_id %}`, and the posting address.
  Every stock block, id, tab (`nav-pills` / `tab-pane` / `data-load-from`),
  AJAX hook, and `setup_overview` script stays. Wrapped in
  `{% if 'postorius' in INSTALLED_APPS %}`.

## Not copied

Similarly named stock templates we deliberately left alone, styled from CSS only:

- `hyperkitty/templates/hyperkitty/messages/right_col.html` — stock. Both
  sidebar links are already inside `<p>` children of `#message-overview-info`,
  so that section can be one card from `post.css` without a wrapper.
- `hyperkitty/templates/hyperkitty/messages/message.html` — stock. In-message
  Reply is link-level from `post.css` (`a.reply`).
