// Función "notify": la app la llama para mandar un aviso por Telegram.
// Supabase → Edge Functions → Deploy a new function → nombre: notify → pega esto.
import { createClient } from "npm:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};
function serviceKey(): string {
  const legacy = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (legacy) return legacy;
  try { const k = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}"); return k.default ?? Object.values(k)[0] as string; } catch { return ""; }
}
const json = (b: unknown, s = 200) =>
  new Response(JSON.stringify(b), { status: s, headers: { ...cors, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const url = Deno.env.get("SUPABASE_URL")!;
    const admin = createClient(url, serviceKey());
    const jwt = (req.headers.get("Authorization") ?? "").replace(/^Bearer\s+/i, "");
    const { data: { user } } = await admin.auth.getUser(jwt);
    if (!user?.email) return json({ error: "no autorizado" }, 401);
    let app = user.email.split("@")[0];
    const body = await req.json();
    const { to, text } = body;
    if (app === "adri") {
      if (typeof body.app !== "string" || !/^[a-z0-9]+$/.test(body.app)) return json({ error: "falta la app" }, 400);
      app = body.app;
    }
    if (!["alumno", "admin"].includes(to) || typeof text !== "string" || !text.trim()) {
      return json({ error: "datos no válidos" }, 400);
    }
    const q = admin.from("tg_chats").select("chat_id").eq("role", to);
    const { data: chats } = await (to === "admin" ? q.in("app", [app, "adri"]) : q.eq("app", app));
    const token = Deno.env.get("TG_TOKEN")!;
    let sent = 0;
    const ids = [...new Set((chats ?? []).map((c) => c.chat_id))];
    for (const chat_id of ids) {
      const r = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id, text: text.slice(0, 900) }),
      });
      if (r.ok) sent++;
    }
    return json({ sent });
  } catch (e) {
    return json({ error: String(e) }, 500);
  }
});
