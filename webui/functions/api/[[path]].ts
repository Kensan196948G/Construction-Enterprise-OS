/**
 * API プロキシ — Cloudflare Pages Function
 *
 * https://construction-os.mirai-dx-platform.com/api/v1/* を
 * Cloudflare Tunnel(api.construction-os.mirai-dx-platform.com)経由で
 * auth サービス(Neon 接続)へ転送する。
 * 本 Function は /api/* にマウントされるため、params.path には
 * "v1/..." が入る(先頭の /api は含まれない)。
 */
export async function onRequest(context: { request: Request; params: { path?: string[] } }) {
  const { request, params } = context;
  const path = (params.path ?? []).join("/");
  const url = new URL(request.url);
  const target = new URL(`http://api.construction-os.mirai-dx-platform.com/api/${path}`);
  target.search = url.search;

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.set("x-forwarded-host", url.host);

  const body = ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer();
  const resp = await fetch(target.toString(), {
    method: request.method,
    headers,
    body: body as BodyInit | undefined,
  });

  const out = new Response(resp.body, { status: resp.status, headers: resp.headers });
  return out;
}
