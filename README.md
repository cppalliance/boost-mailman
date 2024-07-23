
## Boost Mailman

A repository to store customized Boost templates for Mailman.  

The mailman servers are installed using https://github.com/cppalliance/ansible-mailman3. An installation includes both mailman-core and mailman-web. File locations on a server:  

/etc/mailman3/ Mailman core configuration files.  
/var/lib/mailman3/ Mailman core production files.  
/var/lib/mailman3/web/ Mailman web   
/var/lib/mailman3/web/project/ Django settings files. settings.py, manage.py, .env  

## Local development environment

- It should be possible to test code changes by logging into an existing mailman server (staging) and place new template files there. Or create a local development environment by running ansible locally. If a docker-compose file is generated, include that information in this README.   

- The settings.py file in ansible has been refactored so that instead of being an ansible template, it is static and leverages environment variables. See [settings.py](./settings.py).

- **Environment Variables**: Copy file `env.template` to `.env` and adjust values to match your local environment.  

- settings.py now includes an "import settings_custom" at the end of the file. One idea is to add customizations in [settings_custom.py](./settings_custom.py). If there are general improvements any mailman installation would use, put those in settings.py itself and submit the changes back to the ansible repository also.   


## Templates and Styles

The templates and styles have been modified to more closely match the Boost website and those customizations are housed in the following directories.

### Postorious

The `postorious/templates` directory should override the templates provided in the Postorious project.  

Style customizations reside in `postorious/static` directory and can replace what is provided by the Postorious project.  Bootstrap is updated to latest via the CDN in the base template.  

### Hyperkitty

The `hyperkitty/templates` directory should override the templates provided in the Hyperkitty project.  

Style customizations reside in `hyperkitty/static` directory and can replace what is provided by the Hyperkitty project.  Bootstrap sass update is in progress with dark mode support and will be added to this static directory.