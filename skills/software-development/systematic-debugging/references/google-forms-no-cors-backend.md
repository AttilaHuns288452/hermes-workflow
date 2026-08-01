# Google Forms as a Free Form Backend — Reference

## Overview

Google Forms can accept form submissions via a simple HTTP POST with **no API key, no backend, no cost**. This is useful for feedback forms, surveys, or contact forms on static sites.

## How It Works

1. Create a Google Form at https://forms.google.com
2. Add your fields (Name, Message, Email, etc.)
3. Submit the form once in browser → inspect network tab to find the `entry.XXXXXX` IDs
4. POST to `https://docs.google.com/forms/d/e/{FORM_ID}/formResponse`

## Finding Entry IDs

The simplest way to find the entry ID for each field:

1. Open the published form in a browser
2. Open DevTools → Console
3. Fill in one field and run:
   ```js
   document.body.innerHTML.match(/entry\.\d+/g)
   ```
4. Match each entry ID to its field by filling one field at a time and inspecting hidden inputs:
   ```js
   document.querySelector('form')?.innerHTML
   ```
   The hidden `<input name="entry.12345" value="your typed value">` reveals the mapping.

## The POST Format

```js
const FORM_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse";

const body = new URLSearchParams({
  "entry.123456": "field value",
  "entry.789012": "another value",
  fvv: "1",
  pageHistory: "0",
  fbzx: "0",
});

await fetch(FORM_URL, {
  method: "POST",
  mode: "no-cors",  // required — Google Forms doesn't support CORS
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body,
});
```

**Important:** `mode: "no-cors"` means the browser fires the request but you can't read the response. The fetch will succeed silently even if the server returns an error. Always show the user a success message after the fire-and-forget.

## Verifying It Works

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST \
  "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "entry.123456=Test" \
  --data-urlencode "fvv=1" \
  --data-urlencode "pageHistory=0" \
  --data-urlencode "fbzx=0"
```
200 = form accepted the submission. Check Google Forms → Responses tab.

## Receiving Notifications

In the Google Form → Responses tab → ⋮ menu → "Get email notifications for new responses"

## Limitations

- No CORS responses — can't read success/failure from JavaScript
- No file uploads via no-cors POST
- Form is publicly accessible (anyone with the form ID can submit)
- No CAPTCHA — forms may get spam (enable Google Forms' built-in spam filter)
