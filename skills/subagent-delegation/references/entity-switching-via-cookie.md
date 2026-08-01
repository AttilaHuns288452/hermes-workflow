# Entity Switching via Cookie — Multi-Tenant Pattern

**Proven in:** CashFlow OS (2026-07-30). One user, multiple entities (personal + businesses).
All server actions automatically scope data to the selected entity via a cookie.

## The Pattern

1. **Client-side**: Entity switcher dropdown writes `cf_entity_id` cookie on change:
   ```tsx
   <select onChange={e => {
     setSelected(e.target.value);
     localStorage.setItem("selectedEntity", e.target.value);
     document.cookie = `cf_entity_id=${e.target.value}; path=/; max-age=31536000`;
     window.location.reload();
   }}>
   ```

2. **Server-side**: `getEntity()` reads the cookie, falls back to personal:
   ```ts
   import { cookies } from "next/headers";
   import { cache } from "react";

   export const getEntity = cache(async () => {
     const supabase = await createClient();
     const { data: { user } } = await supabase.auth.getUser();
     if (!user) return { error: "Not authenticated" };

     const cookieStore = await cookies();
     const selectedId = cookieStore.get("cf_entity_id")?.value;

     if (selectedId) {
       // Verify user owns this entity
       const { data: entity } = await supabase
         .from("entities").select("id").eq("id", selectedId).eq("user_id", user.id).single();
       if (entity) return { supabase, entityId: entity.id };
     }

     // Fallback: user's personal entity
     const { data: entity } = await supabase.from("entities")
       .select("id").eq("user_id", user.id).eq("type", "personal").single();
     return entity ? { supabase, entityId: entity.id } : { error: "No entity found" };
   });
   ```

3. **💡 React.cache() bonus**: Multiple server actions called from the same page share one
   auth+entity lookup. Dashboard calls 8 actions → 1 auth round-trip, not 8.

## Why Cookie Over localStorage

- `localStorage` is browser-only — server actions can't read it
- Cookies are sent with every HTTP request — available in SSR, middleware, and server actions
- `next/headers.cookies()` reads them natively, no extra packages
- No API changes needed — all existing server actions benefit automatically

## When to Use

- Multi-tenant apps where one user owns multiple orgs/workspaces
- Business mode switches (personal ↔ company dashboard)
- Any scenario where a server action needs context passed from the client without explicit parameters

## Pitfalls

- **Cookie must be on the same domain** — `path=/` ensures it's sent to all routes
- **After setting cookie, reload** — the server-side cookie isn't updated until the next request
- **Don't cache cookie-based getEntity cross-user** — ensure `eq("user_id", user.id)` check before trusting the entity ID from the cookie
- **React.cache() is per-request** — it resets between page loads. Perfect for this pattern.

## Security

The cookie value is just a UUID. It cannot be used to access other users' entities because
`getEntity()` always verifies `entities.user_id = auth.uid()`. Even if a user tampers with
the cookie, RLS provides defense-in-depth.
