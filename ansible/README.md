
## Ansible customizations

When deploying the ansible role https://github.com/cppalliance/ansible-mailman3, copy the custom/ folder here to the ansible tasks/ folder, so the resulting directory structure is tasks/custom/main.yml.

Set this in the SSL section to include boost-specific redirects.

    location ~ ^/Archives(.*)$ { return 301 https://listarchives.boost.org/Archives$1; }
    location ~ ^/boost-announce(.*)$ { return 301 https://listarchives.boost.org/boost-announce$1; }
    location ~ ^/boost-users(.*)$ { return 301 https://listarchives.boost.org/boost-users$1; }

Notice ../scripts/templates.sh.  Where should they go, to be more automated?


