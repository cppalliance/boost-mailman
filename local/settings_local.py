# Local-dev settings overlay, imported at the end of the maxking/mailman-web
# image settings via `from settings_local import *`.
#
# Purpose: reproduce the production override mechanism locally, where
# boost-mailman/settings.py registers a custom static dir + templates dir.
# In prod those are static_custom/ and templates/ next to the project; here
# docker-compose.yml bind-mounts them under /opt/boost-custom/ (outside the
# web_data volume so the entrypoint's chown does not choke on read-only mounts).
import sys

# Dev-only: the maxking/mailman-web image hardcodes `DEBUG = False` in its
# settings.py and ignores DJANGO_DEBUG. Because this overlay is imported last
# (`from settings_local import *`), reassigning DEBUG here wins. DEBUG=True
# turns on debug tracebacks, static-view helpers, and django-debug-toolbar-style
# behavior. NEVER ship this to production.
#
# IMPORTANT: DEBUG=True is NOT sufficient for live template reload under uWSGI.
# In Django 4.1+ the default template config ALWAYS wraps loaders in
# `django.template.loaders.cached.Loader` (see django/template/engine.py) - the
# cached wrap only used to be conditional on `not debug` in older Django. That
# in-memory template cache has no mtime invalidation, so once uWSGI's worker
# loads a template it never re-reads the file. `runserver` circumvents this by
# subscribing to the autoreload signal that clears the cache; uWSGI does not.
# The template-loaders block below is what actually makes edits live-reload -
# see the explicit `loaders` key which takes Django's `else` branch and skips
# the cached wrap.
DEBUG = True

# Custom static source dir (collected into STATIC_ROOT by collectstatic).
# Holds the shared `boost/` namespace plus per-app overrides.
STATICFILES_DIRS = ["/opt/boost-custom/static_custom"]

# Custom template dir, searched before app templates (loader precedence).
# `TEMPLATES` is a list-of-dicts that we must mutate in place on the already-
# imported base settings module (a plain reassignment here would not propagate
# back to Django since the base module has already cached its own attribute).
# If the base module / TEMPLATES structure isn't what we expect, fail loudly
# rather than silently serving stock upstream chrome - that mystery is one of
# the most painful failure modes for this project.
_base_name = __name__.rsplit(".", 1)[0] if "." in __name__ else "settings"
_base = sys.modules.get(_base_name)
if _base is None:
    raise RuntimeError(
        f"settings_local.py could not find the base settings module "
        f"(expected sys.modules[{_base_name!r}]); custom templates would be "
        f"silently ignored. Check the maxking/mailman-web image's settings "
        f"import order."
    )
_templates = getattr(_base, "TEMPLATES", None)
if not _templates or not isinstance(_templates, list) or "DIRS" not in _templates[0]:
    raise RuntimeError(
        f"settings_local.py expected {_base_name}.TEMPLATES to be a non-empty "
        f"list-of-dicts with a 'DIRS' key; got {_templates!r}. Custom template "
        f"override cannot be wired up."
    )
_templates[0]["DIRS"] = ["/opt/boost-custom/templates"]

# Live template reload under uWSGI. Setting an explicit `loaders` list makes
# Django's Engine constructor take the `else` branch and NOT wrap the loaders
# in `cached.Loader` - so every request reads the template file fresh from
# disk. Django forbids combining `app_dirs=True` with an explicit `loaders`
# list, so we drop `APP_DIRS` and list the app-directories loader by hand
# (same set as the default, just un-cached).
_templates[0]["APP_DIRS"] = False
_templates[0].setdefault("OPTIONS", {})["loaders"] = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
# Dev-only: DEBUG=True turns django-compressor off, so HyperKitty's
# `{% compress css %}` block would run the sassc precompiler during requests,
# which takes minutes under amd64 emulation on Apple Silicon and ties up the
# uWSGI workers. Serve the bundle the image entrypoint builds with
# `compress --force` on every start instead. The boost CSS sits outside the
# compress block, so it still live-reloads.
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
