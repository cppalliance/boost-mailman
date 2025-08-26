
## Message Formatting

The format of a message on Hyperkitty or via email is determined by a few different factors.

- The list setting "Convert html to plaintext."

"Should Mailman convert text/html parts to plain text? This conversion happens after MIME attachments have been stripped."  Let's call that `convert-html-to-plaintext` in this document.  

(Actually, in Postorius, this setting should be adjusted by turning on or off *all filtering*.)  

- The list setting "Archive Rendering mode."

"Choices are Plain text or Markdown text. This option enables rendering of emails in archiver as rich text with formatting based on markup in the email.  Currently, this option is only supported by Hyperkitty." Let's call that `archive-render-mode` in this document. Markdown is explained at https://docs.mailman3.org/projects/hyperkitty/en/latest/rendering.html.  Notably, HTML is not a supported "Archive Rendering mode". 

That creates 4 combinations from those 2 options. Let's review each combination. The first is currently enabled. This was chosen after testing, when it was discovered to be a preferable option that avoids problems, as discussed below.  

**Option 1**. convert-html-to-plaintext="YES" archive-render-mode="Plain text"

Incoming message are converted to plain text, and Hyperkitty displays plain text.

This combination had the fewest bugs or glitches, it generally works fine.

Plain text matches mailman2, which users were accustomed to, and it's sufficient for most discussions. 

Of course, a disadvantage is no special display formatting, but that's not a blocker to using the list.

**Option 2**. convert-html-to-plaintext="YES" archive-render-mode="Markdown"

Numerous problems.   

To start with "this option is only supported by Hyperkitty". Testing confirms that formatting isn't carried over to emails, and emails are just as important as the web. Emails continues to render as plain text.  
Many email clients compose their emails with html, but with this setting, html formatting fails to be rendered.  
Markdown italics and bold are shown in the web ui, however the surrounding asterisks (which are intended to be merely markdown symbols) remain and are shown on the page, which is buggy.  

**Option 3**. convert-html-to-plaintext="NO" archive-render-mode="Plain text"

The Hyperkitty web UI shows plain text. There is also a funny "attachment" link. That's the HTML version of the message. If you click the attachment, in another browser tab, by itself, the rendered HTML content appears. Or often times the browser refuses to open the attachment directly, and so you must download the attachment and then open it.

Email is "correct". The HTML format is supported. So it's halfway there.  

Email and the web show completely different results. 

And there are the clunky "attachment" links.

**Option 4**. convert-html-to-plaintext="NO" archive-render-mode="Markdown"

This is a terrible mix of non-compatible formatting. Emails will see HTML rendering but not the Markdown. Web will see the Markdown rendering, but not the HTML. 
The markdown is still broken, as mentioned in Option 2 above.  
The clunky "attachment" link is present. If you are able to view the attachment, it matches the email rendering (HTML, but not Markdown).

## Future

What is a desirable future solution?  
- Turn off filtering. That is convert-html-to-plaintext="No".  
- Enable Hyperkitty to display HTML messages. See https://gitlab.com/mailman/hyperkitty/-/issues/476 . In this case, HTML should not be an "attachment", but shown in the main window. An HTML sanitizer would need to be installed to prevent malicious attacks. The implementation would be "Settings -> Archive Rendering mode -> Plain text or HTML or Markdown".    

This solution may not cover "everything" but it would be a large step towards displaying formatted message content that can be customized by the message sender.   
