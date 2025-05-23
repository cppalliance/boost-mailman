
## Boost Mailman

A repository to store customized Boost templates for Mailman.  

The mailman servers are installed using https://github.com/cppalliance/ansible-mailman3. An installation includes both mailman-core and mailman-web. File locations on a server:  

/etc/mailman3/ Mailman core configuration files.  
/var/lib/mailman3/ Mailman core production files.  
/var/lib/mailman3/web/ Mailman web   
/var/lib/mailman3/web/project/ Django settings files. settings.py, manage.py, .env  
/opt/mailman3/ A python virtual environment used by core and web. (There are no mailman "configuration files" /opt/mailman3. It is a venv with pip packages).

## Local development environment

- It should be possible to test code changes by logging into an existing mailman server (staging) and place new template files there. Or create a local development environment by running ansible locally. If a docker-compose file is generated, include that information in this README.   

- The settings.py file in ansible has been refactored so that instead of being an ansible template, it is static and leverages environment variables. See [settings.py](./settings.py).

- **Environment Variables**: Copy file `env.template` to `.env` and adjust values to match your local environment.  
