
## Common commands - managing mailman-web  

There are multiple ways to run the `mailman-web` command. The latest and recommended method is now to call the wrapper convenience script `mailman-web-wrapper` (as root) located in /usr/local/bin/mailman-web-wrapper which will set necessary parameters including user account, executable path, and environment variables. That makes it easy to call the command and not be concerned about those details. If you'd like to more information about previous methods, see [earlier-notes-to-keep.md](earlier-notes-to-keep.md) .

Run migrations:  

```
# sudo mailman-web-wrapper migrate
```

Refresh threads cache:  

```
# sudo mailman-web-wrapper runjob -v 3 hyperkitty recent_threads_cache
```

## Lists of cron jobs

```

# sudo mailman-web-wrapper runjobs minutely --list
Job List: 0 jobs

# sudo mailman-web-wrapper runjobs quarter_hourly --list
Job List: 0 jobs

# sudo mailman-web-wrapper runjobs hourly --list
Job List: 3 jobs
 appname    - jobname                - when   - help
--------------------------------------------------------------------------------
 hyperkitty - new_lists_from_mailman - hourly - Import new lists from Mailman
 hyperkitty - thread_starting_email  - hourly - Find the starting email when it is missing
 hyperkitty - update_index           - hourly - Update the full-text index

# sudo mailman-web-wrapper runjobs daily --list
Job List: 5 jobs
 appname           - jobname              - when  - help
--------------------------------------------------------------------------------
 django_extensions - cache_cleanup        - daily - Cache (db) cleanup Job
 django_extensions - daily_cleanup        - daily - Django Daily Cleanup Job
 hyperkitty        - orphan_emails        - daily - Reattach orphan emails
 hyperkitty        - recent_threads_cache - daily - Refresh the recent threads cache
 hyperkitty        - sync_mailman         - daily - Sync user and list properties with Mailman

# sudo mailman-web-wrapper runjobs weekly --list
Job List: 0 jobs

# sudo mailman-web-wrapper runjobs monthly --list
Job List: 2 jobs
 appname    - jobname                - when    - help
--------------------------------------------------------------------------------
 hyperkitty - empty_threads          - monthly - Remove empty threads
 hyperkitty - update_and_clean_index - monthly - Update the full-text index and clean old entries

# sudo mailman-web-wrapper runjobs yearly --list
Job List: 1 jobs
 appname    - jobname            - when   - help
--------------------------------------------------------------------------------
 hyperkitty - thread_order_depth - yearly - Compute thread order and depth for all threads

```

## Managing mailman core

The latest and recommended method to call the `mailman` cli command is now to run the wrapper convenience script `mailman-wrapper` (as root) located in /usr/local/bin/mailman-wrapper which will set necessary parameters including user account, executable path, and environment variables. That makes it easy to call the command and not be concerned about those details. If you'd like to more information about previous methods, see [earlier-notes-to-keep.md](earlier-notes-to-keep.md) .

Example:

```
# sudo mailman-wrapper help

# sudo mailman-wrapper version
```

