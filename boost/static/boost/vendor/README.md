# Vendored Boost v3 snapshot

Frozen, unmodified copy of the Boost website **v3** visual layer used by the
Mailman re-skin. Do not edit files under this directory. Adjustments go in
`../css/` (component files such as `../css/forms.css` and `../css/cards.css`,
page files such as `../css/post.css`).

## Source

- Repo: `cppalliance/website-v2`
- Commit: `99be947e0321dba400e969f5a8e5fe57ea099fcb` (`99be947e`)
- Date copied: 2026-09-24

The numbered `00`–`16` files are not committed in that repo; they come from
its local `design-system/css/` extraction of `static/css/v3/`. Everything
else (footer, logo, fonts) was taken with `git archive 99be947e`.

## File list

`vendor/v3/css/`, all loaded by `boost/templates/boost/stylesheets.html`:

- `01-tokens-primitives.css` … `05-tokens-semantics.css`
- `06-foundations.css`
- `11-buttons.css`
- `16-headers.css`
- `footer.css`

## Pruned files

Nothing we render uses these, so they were deleted rather than kept unloaded.
Restore any of them from `website-v2` at `99be947e` (`design-system/css/` for
the numbered files, `static/css/v3/` for the rest).

- `00-borrowed-base.css`: Tailwind preflight and `@tailwindcss/forms`
  baseline. It was never loaded: Mailman already has Bootstrap Reboot, and
  `reset.css` copies the look-affecting parts.
- `10-typography.css`: every heading rule is scoped to a v3 context class our
  markup never emits.
- `14-tables.css`: only `downloads-table-card__*`-style classes.
- `avatar.css`, `banner.css`, `count-badge.css`: no template emits `.avatar`,
  `.banner` or `.count-badge`.
- `15-tabs-navs.css`: only matched Bootstrap's `.pagination` by name; those
  declarations now live in `pagination.css`.
- `13-cards.css`: only matched Bootstrap's `.card` (HyperKitty's thread admin
  card); its `align-items` and `gap` now live in `post.css`.
- `12-forms.css`: only matched `.dropdown` (identical to Bootstrap) and the
  stock `class="checkbox"` wrappers; the `.checkbox` declarations now live in
  `forms.css`.

`vendor/v3/img/`

- `Boost_Symbol_Transparent.svg` — from `static/img/Boost_Symbol_Transparent.svg`

`vendor/static/font/` — website-v2 sub-paths, because `06-foundations.css`
rewrote production's absolute `/static/font/...` URLs to
`../../static/font/...` for the design-system gallery. Vendored at
`vendor/v3/css/`, those relative URLs resolve to
`/static/boost/vendor/static/font/...`:

- `v3/mona-sans/mona-sans-vf.ttf`
- `v3/mona-sans/mona-sans-vf-italic.ttf`
- `v3/mona-sans-display/MonaSans_SemiCondensed-Regular.ttf`
- `v3/mona-sans-display/MonaSans_SemiCondensed-Medium.ttf`
- `MonaspaceNeon-Var.woff2`
- `v3/monaspace-neon/monaspace-neon-latin-400-italic.ttf`
- `MonaspaceXenon-Var.woff2`
- `MonaspaceXenon-Italic.woff2`

## Refreshing the snapshot

To pick up a newer boost.org design:

1. Copy the same file list (everything above) from a newer `website-v2`
   commit, at the same source paths.
2. Update the commit hash and date in the **Source** section above.
3. Re-check the font paths: `06-foundations.css` must still resolve its
   font URLs under `vendor/static/font/` (see the path note above).
4. Review every page against the live site. The vendored files can change
   the components underneath our Custom styles, which may then need
   updating in `../css/`.
