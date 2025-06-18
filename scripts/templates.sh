#!/bin/bash

Temporary notes

The mailing list headers and footers can be customized in /var/lib/mailman3/templates/list/list_name/en

------------------------------------------------
"list:member:digest:footer.txt"
-------------------------------------------------
_______________________________________________
${display_name} mailing list -- ${listname}
To unsubscribe send an email to ${short_listname}-leave@${domain}
https://${domain}/mailman3/lists/${list_id}/

----------------------------------------
"list:member:regular:footer.txt"
----------------------------------------
_______________________________________________
${display_name} mailing list -- ${listname}
To unsubscribe send an email to ${short_listname}-leave@${domain}
https://${domain}/mailman3/lists/${list_id}/
Archived at: ${hyperkitty_url}

