export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const body = await req.text();

  const r = await fetch("https://echoiq-unnm.onrender.com/sentiment", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });

  return new Response(await r.text(), {
    status: r.status,
    headers: {
      "content-type": r.headers.get("content-type") ?? "application/json",
      "cache-control": "no-store",
    },
  });
}
