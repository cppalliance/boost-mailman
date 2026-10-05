/* row-links.js: a click anywhere in these rows follows the row's link.
 *
 * Not a CSS stretched link: Safari does not contain a position:absolute
 * ::after in a position:relative <tr>, so the overlay covers the whole
 * table and every click goes to the last row. The listener is delegated
 * because HyperKitty replaces the profile tables over AJAX. /archives/
 * rows are handled by HyperKitty's own hyperkitty-index.js. The cursor
 * rules in tables.css and list-index.css name the same rows.
 */
(() => {
  const ROWS = [
    ".page-list_index table tbody tr",
    ".page-ps_user_profile table tbody tr",
    ":is(.page-hk_user_favorites, .page-hk_user_last_views, .page-hk_user_votes) .user-profile-content > .table tbody tr:not(.list-address)",
  ].join(", ");
  const LINK = "td > a:not(.btn):not(.cancel)";
  // form: the votes rows hold the like/cancel form; its text stays inert.
  const CONTROLS = "a, button, input, select, textarea, label, form";

  function follow(event, newTab) {
    if (event.defaultPrevented) return;
    const row = event.target.closest(ROWS);
    if (!row || event.target.closest(CONTROLS)) return;
    // A drag that selects cell text ends in a click; keep the selection.
    if (!window.getSelection().isCollapsed) return;
    const link = row.querySelector(LINK);
    if (!link) return;
    if (newTab) {
      window.open(link.href, "_blank", "noopener");
    } else {
      window.location.assign(link.href);
    }
  }

  document.addEventListener("click", (event) => {
    if (event.button === 0) {
      follow(event, event.metaKey || event.ctrlKey || event.shiftKey);
    }
  });
  document.addEventListener("auxclick", (event) => {
    if (event.button === 1) follow(event, true);
  });
})();
