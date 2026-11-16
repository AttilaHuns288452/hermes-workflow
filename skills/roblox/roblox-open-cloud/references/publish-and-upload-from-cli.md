# Publishing places and uploading assets without Studio's GUI

Studio's Publish dialog, Open-file dialog and 3D Importer ignore synthesized keyboard and mouse
input: the field accepts a typed path, then Enter and a pixel-accurate click on Open both do nothing.
Anything that has to ship therefore goes through Open Cloud. This is also faster and scriptable, so
prefer it even when the GUI works.

## 1. Key setup (the step that silently ruins the rest)

A secret is issued **with the scopes it has at generation time**. Editing an existing key's
permissions does not re-issue it — the dashboard will show the scope ticked while every call still
returns `403 Scope not authorized`.

1. Creator Dashboard → Open Cloud → API Keys → Create API Key.
2. Fill the **Name** first. Generation refuses with "A unique name is required" otherwise, and the
   warning only appears at the bottom of the page.
3. Add each permission pair: pick the API system, then add every operation you need.
   - place publishing → `universe-places` + `write`
   - mesh/audio/image upload → `assets` + `read` **and** `write`
   - The "Select Operations to Add" input vanishes after the first operation; the dropdown then sits
     on the chevron at the right edge of the `scope:operation` chip field.
4. Save & Generate Key → tick **I understand the security risks** in the warning modal → generate.
5. Copy the secret immediately. It is shown once and is ~960 chars of base64 ending in `=`.
6. Store it `chmod 600` outside the repo. Use a separate key per capability so a compromised one can
   be revoked alone.

Sanity check before blaming the endpoint:

```bash
curl -s -X POST https://apis.roblox.com/api-keys/v1/introspect \
  -H "x-api-key: $(cat ~/.roblox_api_key)" -H 'Content-Type: application/json' -d '{}'
```

## 2. Publish a place

```bash
curl -sS -X POST \
  "https://apis.roblox.com/universes/v1/$UNIVERSE/places/$PLACE/versions?versionType=Published" \
  -H "x-api-key: $(cat ~/.roblox_api_key)" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @place.rbxlx -w '\n%{http_code}\n'
```

- Success is `200` with `{"versionNumber":N}`.
- `409 Save failed. Server is busy` is a **lock conflict with an open Studio session**, not a bad
  payload. Quit Studio, wait ~60s, retry. Retrying without closing Studio loops on 409 indefinitely.
- `.rbxlx` and `.rbxl` both work; keep the built artifact as the single input so what ships is exactly
  what was tested.

Wrap it in a retry loop and treat 409 as "wait", 4xx other than 409 as "fix the key/body":

```bash
for attempt in 1 2 3 4 5; do
  code=$(curl -sS -o /tmp/out -w '%{http_code}' /* ...publish... */)
  [ "$code" = 200 ] && { cat /tmp/out; exit 0; }
  sleep 60
done
```

## 3. Verify the publish actually reached players

A 2xx is not delivery. Read the public game record and compare `updated` against now:

```bash
curl -sS "https://games.roblox.com/v1/games?universeIds=$UNIVERSE" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['updated'])"
```

If the timestamp has not moved, players are still on the previous version regardless of what the
upload returned.

## 4. Upload a mesh (or any asset)

`multipart/form-data` with a JSON `request` part and a binary `fileContent` part:

```bash
REQUEST=$(printf '{"assetType":"Mesh","displayName":"%s","description":"%s","creationContext":{"creator":{"userId":"%s"}}}' \
  "$NAME" "$DESC" "$USER_ID")

curl -sS -X POST https://apis.roblox.com/assets/v1/assets \
  -H "x-api-key: $(cat ~/.roblox_assets_key)" \
  -F "request=$REQUEST;type=application/json" \
  -F "fileContent=@mesh.fbx;type=model/fbx"
# -> {"operationId":"...","done":false}
```

Then poll for the id; upload finishes asynchronously:

```bash
loop: curl -sS "https://apis.roblox.com/assets/v1/operations/$OP" -H "x-api-key: $KEY"
      -> {"done":true,"response":{"assetId":"1234567890",...}}
```

Notes:

- `userId` is the creator's numeric id, not the username. Group creator uses `{"groupId": "..."}` and
  a key minted under the group.
- FBX exports from Blender import with correct axes when exported `axis_forward=-Z, axis_up=Y`; OBJ
  works too but the FBX path is what the importer and the uploader agree on.
- Reference the result in game as `rbxassetid://<assetId>`.
- MeshPart `Size` is authored in the `Config`/asset table, not read from the file — the uploaded mesh
  does not carry a trustworthy world scale, so set it explicitly next to the id.
- Verified shapes worth keeping: a tapered trunk with forking limbs reads far better than a
  trunk-plus-canopy at any camera distance, and a 3-rock cluster reads as scenery where a single
  boulder reads as a dropped ball.

## 5. Ordering

1. Build the place from source (Rojo) — never upload a hand-edited place that diverges from the repo.
2. Publish, then verify the timestamp.
3. Upload the assets the new build references *before* publishing a build that uses them, otherwise the
   first players load placeholder meshes.
