/**
 * Batch character image fetcher from AniList public API
 * 
 * Usage:
 *   1. Edit the SEARCHES array at the bottom to include your character names
 *   2. Run: node scripts/batch-fetch-character-images.js
 *   3. Wait ~2 min for 40 characters (1.5s delay between requests = rate limit safety)
 *   4. Copy the output into your characters.ts file
 * 
 * Rate limit: ~90 requests/min. The script uses 1500ms delay between requests.
 * If you hit rate limiting, increase the delay in setTimeout().
 */

const https = require('https');

function fetchCharacterImageUrl(searchName) {
  return new Promise((resolve) => {
    const body = JSON.stringify({
      query: `query ($search: String) { Character(search: $search) { image { large } } }`,
      variables: { search: searchName }
    });

    const req = https.request({
      hostname: 'graphql.anilist.co',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'Accept': 'application/json'
      }
    }, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          const url = json?.data?.Character?.image?.large;
          if (url) {
            resolve(url.replace(/\\\//g, '/'));
          } else {
            resolve(null);
          }
        } catch (e) {
          resolve(null);
        }
      });
    });

    req.on('error', () => resolve(null));
    req.write(body);
    req.end();
  });
}

async function fetchAll(searches) {
  const results = [];
  for (let i = 0; i < searches.length; i++) {
    const [charId, searchName] = searches[i];
    console.error(`[${i + 1}/${searches.length}] Fetching ${searchName}...`);
    const url = await fetchCharacterImageUrl(searchName);
    if (url) {
      results.push({ charId, url });
      console.error(`  ✅ Found: ${charId}`);
    } else {
      console.error(`  ❌ Not found: ${searchName}`);
    }
    // Wait 1.5s between requests to avoid rate limiting
    if (i < searches.length - 1) {
      await new Promise(r => setTimeout(r, 1500));
    }
  }
  return results;
}

// Example usage - replace with your character names:
// [charId, searchName]
const SEARCHES = [
  ['gojo-satoru', 'Gojo Satoru'],
  ['hinata', 'Hinata Hyuga'],
  ['levi', 'Levi'],
  ['tanjiro', 'Tanjiro Kamado'],
  ['lelouch', 'Lelouch Lamperouge'],
];

fetchAll(SEARCHES).then(results => {
  console.log('\n=== RESULTS ===\n');
  for (const { charId, url } of results) {
    console.log(`    imageUrl: "${url}",`);
  }
  console.log('\n=== DONE ===');
});
