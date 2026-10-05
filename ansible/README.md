
## Ansible customizations

When deploying the ansible role https://github.com/cppalliance/ansible-mailman3, copy the custom-boost/ folder here to the ansible tasks/ folder, so the resulting directory structure is tasks/custom-boost/main.yml.

### `mailman3_boost_branch`

Which branch of this repo the role deploys. `custom-boost/main.yml` clones
`boost-mailman` into `/opt/github/ansible-managed/boost-mailman` and copies
its `boost/`, `hyperkitty/` and `postorius/` static and template trees from
there. The variable defaults to `master`; set it in host/group vars to a
pushed branch to preview that branch on staging (re-run the role after the
push).

### `mailman3_static_custom`

The boost deployment must set `mailman3_static_custom: true` in its host/group
vars (that inventory is not in this repo). The variable is read by
`ansible-mailman3/templates/settings.py.j2` and defaults to off, so other
deployments keep the stock look.

This depends on the `ansible-mailman3` change being merged (the toggle that
replaces the commented-out `STATICFILES_DIRS` block). Until that merge lands,
`custom-boost/main.yml` can copy files into `static_custom/` but Django will
not serve them.

After deploy, check on staging that both of these return 200:

- `/static/boost/css/reset.css`
- `/static/boost/vendor/static/font/v3/mona-sans/mona-sans-vf.ttf`

A missing toggle fails loudly in practice: `custom-boost/main.yml` copies the
template overrides whether or not the toggle is set, so the pages render the
new markup with every `boost/` stylesheet returning 404. Merge the
`ansible-mailman3` toggle change before deploying the redesign.

Set this in the SSL section to include boost-specific redirects.

    location ~ ^/Archives(.*)$ { return 301 https://listarchives.boost.org/Archives$1; }
    location ~ ^/boost-announce(.*)$ { return 301 https://listarchives.boost.org/boost-announce$1; }
    location ~ ^/boost-users(.*)$ { return 301 https://listarchives.boost.org/boost-users$1; }
    location ~ ^/mailman/listinfo.cgi/(.*)$ { return 301 https://$host/mailman3/lists/$1.$host; }

Notice ../scripts/templates.sh.  Where should they go, to be more automated?


