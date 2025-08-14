export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const formData = await req.formData();

  const r = await fetch("https://echoiq-unnm.onrender.com/transcribe", {
    method: "POST",
    body: formData,
  });

  return new Response(await r.text(), {
    status: r.status,
    headers: {
      "content-type": r.headers.get("content-type") ?? "application/json",
      // prevent caching of API responses
      "cache-control": "no-store",
    },
  });
}
