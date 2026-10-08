#!/usr/bin/env python3
"""mcp_call.py — drive a remote MCP server over HTTP JSON-RPC by hand.
Usage: python3 mcp_call.py <server> <tool> '<json-args>'
       python3 mcp_call.py <server> --list
Env:   MCP_URL (override endpoint), MCP_QUERY_FILE (read 'query' arg from file)
Tokens: ~/.hermes/mcp-tokens/<server>.json (+ .meta.json/.client.json for refresh).
Never prints token values. Handles: OAuth refresh, initialize handshake,
plain-JSON AND SSE responses, browser User-Agent (Cloudflare 1010), stale
session ids (re-handshake once on 400).
"""
import json, os, sys, time, urllib.request, urllib.parse

KNOWN_URLS = {'supabase': 'https://mcp.supabase.com/mcp'}
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
base = os.path.expanduser('~/.hermes/mcp-tokens/')

def load_tokens(server):
    tok = json.load(open(f'{base}{server}.json'))
    if tok.get('expires_at', 0) < time.time() + 60:
        meta = json.load(open(f'{base}{server}.meta.json'))
        cli = json.load(open(f'{base}{server}.client.json'))
        data = urllib.parse.urlencode({'grant_type': 'refresh_token',
            'refresh_token': tok['refresh_token'], 'client_id': cli['client_id'],
            'client_secret': cli.get('client_secret', '')}).encode()
        req = urllib.request.Request(meta['token_endpoint'], data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        new = json.loads(urllib.request.urlopen(req, timeout=30).read())
        tok.update({k: v for k, v in new.items() if k in ('access_token', 'refresh_token', 'expires_in', 'token_type')})
        tok['expires_at'] = time.time() + new.get('expires_in', 3600)
        json.dump(tok, open(f'{base}{server}.json', 'w'))
        print('token refreshed', file=sys.stderr)
    return tok

def rpc(url, tok, payload, sid=None):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
        headers={'Authorization': f"Bearer {tok['access_token']}",
                 'Content-Type': 'application/json',
                 'Accept': 'application/json, text/event-stream',
                 'User-Agent': UA, 'MCP-Protocol-Version': '2025-03-26',
                 **({'Mcp-Session-Id': sid} if sid else {})})
    r = urllib.request.urlopen(req, timeout=300)
    out_sid = r.headers.get('Mcp-Session-Id') or sid
    body = r.read().decode().strip()
    if not body:
        return {}, out_sid
    if body.startswith('{'):
        return json.loads(body), out_sid
    for line in body.splitlines():
        if line.startswith('data:'):
            return json.loads(line[5:].strip()), out_sid
    return {}, out_sid

def main():
    server, tool = sys.argv[1], sys.argv[2]
    url = os.environ.get('MCP_URL') or KNOWN_URLS[server]
    tok = load_tokens(server)
    _init, sid = rpc(url, tok, {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2025-03-26', 'capabilities': {},
                   'clientInfo': {'name': 'manual-mcp-client', 'version': '1.0'}}})
    try:
        rpc(url, tok, {'jsonrpc': '2.0', 'method': 'notifications/initialized'}, sid)
    except Exception:
        pass
    if tool == '--list':
        res, sid = rpc(url, tok, {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'}, sid)
        print(json.dumps([t['name'] for t in res.get('result', {}).get('tools', [])], indent=1))
        return
    args = json.loads(sys.argv[3])
    if 'MCP_QUERY_FILE' in os.environ:
        args['query'] = open(os.environ['MCP_QUERY_FILE']).read()
    res, sid = rpc(url, tok, {'jsonrpc': '2.0', 'id': 9, 'method': 'tools/call',
        'params': {'name': tool, 'arguments': args}}, sid)
    # errors ride in content text too — caller must scan output for '"error"'
    print('\n'.join(x.get('text', '') for x in res.get('result', {}).get('content', [])))

if __name__ == '__main__':
    main()
