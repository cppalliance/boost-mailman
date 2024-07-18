
## Common commands  

Managing mailman-web.  

There are multiple ways to run mailman-web commands. One method is to continue as the `root` user, using sudo each time. For example:  

```
sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web migrate
```

Another method is to switch to the proper mailman web user `mailman3-web`, configure enviroment variables, and then directly run a command.  

```
sudo su - mailman3-web
. /opt/mailman3/bin/activate
cd /var/lib/mailman3/web/project
export PYTHONPATH=$PYTHONPATH:$PWD
export DJANGO_SETTINGS_MODULE=settings
```

```
mailman-web update_index_one_list boost@lists.cppal-dev.boost.cppalliance.org
```

The command `mailman-web` is mostly equivalent to `python3 manage.py`.  

Run migrations:  

```
sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web migrate
```

Refresh threads cache:  

```
sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web runjob -v 3 hyperkitty recent_threads_cache
```

## Lists of cron jobs

```

root@lists:/opt/mailman3/bin# sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web runjobs minutely --list
Job List: 0 jobs

root@lists:/opt/mailman3/bin# sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web runjobs quarter_hourly --list
Job List: 0 jobs

root@lists:/opt/mailman3/bin# sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web runjobs hourly --list
Job List: 3 jobs
 appname    - jobname                - when   - help
--------------------------------------------------------------------------------
 hyperkitty - new_lists_from_mailman - hourly - Import new lists from Mailman
 hyperkitty - thread_starting_email  - hourly - Find the starting email when it is missing
 hyperkitty - update_index           - hourly - Update the full-text index

root@lists:/opt/mailman3/bin# sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web runjobs daily --list
Job List: 5 jobs
 appname           - jobname              - when  - help
--------------------------------------------------------------------------------
 django_extensions - cache_cleanup        - daily - Cache (db) cleanup Job
 django_extensions - daily_cleanup        - daily - Django Daily Cleanup Job
 hyperkitty        - orphan_emails        - daily - Reattach orphan emails
 hyperkitty        - recent_threads_cache - daily - Refresh the recent threads cache
 hyperkitty        - sync_mailman         - daily - Sync user and list properties with Mailman

root@lists:/opt/mailman3/bin# sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web runjobs weekly --list
Job List: 0 jobs

root@lists:/opt/mailman3/bin# sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web runjobs monthly --list
Job List: 2 jobs
 appname    - jobname                - when    - help
--------------------------------------------------------------------------------
 hyperkitty - empty_threads          - monthly - Remove empty threads
 hyperkitty - update_and_clean_index - monthly - Update the full-text index and clean old entries

root@lists:/opt/mailman3/bin# sudo -u mailman3-web MAILMAN_WEB_CONFIG=/var/lib/mailman3/web/project/settings.py /opt/mailman3/bin/mailman-web runjobs yearly --list
Job List: 1 jobs
 appname    - jobname            - when   - help
--------------------------------------------------------------------------------
 hyperkitty - thread_order_depth - yearly - Compute thread order and depth for all threads

```
