
## Boost Mailman

A repository to store customized Boost templates for Mailman.  

The mailman servers are installed using https://github.com/cppalliance/ansible-mailman3. An installation includes both mailman-core and mailman-web. File locations on a server:  

/etc/mailman3/ Mailman core configuration files.  
/var/lib/mailman3/ Mailman core production files.  
/var/lib/mailman3/web/ Mailman web   
/var/lib/mailman3/web/project/ Django settings files. settings.py, manage.py, .env  
/opt/mailman3/ A python virtual environment used by core and web. (There are no mailman "configuration files" /opt/mailman3. It is a venv with pip packages).

## Local development

This repo ships a self-contained local stack (`docker-compose.yml` + `local/`) using the
`maxking/mailman-core` and `maxking/mailman-web` `0.5.2` images (matching production PyPI pins).
Host ports (8400/8480/8201/8224) and names (`boost-mailman-*`) are chosen so this stack can
run alongside the wg21-mailman harness.

```bash
docker compose up -d
docker compose logs -f mailman-web   # first run: migrate + collectstatic
./seed.sh                            # create lists + rich archive sample data
```

Then open:

- Postorius (lists): http://localhost:8400/mailman3/lists/
- HyperKitty (archives): http://localhost:8400/archives/
- Django admin: http://localhost:8400/admin/

How overrides load locally (mirrors production's `static_custom` + `TEMPLATES DIRS`):

- `local/settings_local.py` sets `DEBUG=True` and registers `STATICFILES_DIRS`/`TEMPLATES DIRS`.
- Templates live-reload on a browser refresh (no restart).
- The custom `boost/` static namespace is served live from its bind mount via a
  `static-map` in `local/uwsgi.ini` - edit a `boost/` CSS/img file and hard-refresh
  (Cmd+Shift+R). No `collectstatic` step; stock app static is collected by the image
  entrypoint on start.

To customize a page you have not overridden yet, copy the version-matched template out of
the container into this repo's tree and edit it, e.g.:

```bash
docker compose exec mailman-web cat \
  /usr/lib/python3.12/site-packages/hyperkitty/templates/hyperkitty/overview.html \
  > hyperkitty/templates/hyperkitty/overview.html
```

Stop / reset:

```bash
docker compose down       # stop, keep data
docker compose down -v    # stop and WIPE all data
```

Alternatively, test by logging into an existing mailman server (staging) and placing new
template files there, or by running ansible locally.

- The settings.py file in ansible has been refactored so that instead of being an ansible template, it is static and leverages environment variables. See [settings.py](./settings.py).

- **Environment Variables**: Copy file `env.template` to `.env` and adjust values to match your local environment.  
