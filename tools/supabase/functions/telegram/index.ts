// Función "telegram": recibe los mensajes que le escribís al bot y guarda quién quiere avisos.
// Supabase → Edge Functions → Deploy a new function → nombre: telegram → pega esto.
// IMPORTANTE: en los ajustes de esta función, desactiva "Verify JWT".
import { createClient } from "npm:@supabase/supabase-js@2";

function serviceKey(): string {
  const legacy = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (legacy) return legacy;
  try { const k = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}"); return k.default ?? Object.values(k)[0] as string; } catch { return ""; }
}
const token = () => Deno.env.get("TG_TOKEN")!;
async function reply(chat_id: number, text: string) {
  await fetch(`https://api.telegram.org/bot${token()}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id, text }),
  });
}

Deno.serve(async (req) => {
  if (req.headers.get("x-telegram-bot-api-secret-token") !== Deno.env.get("TG_SECRET")) {
    return new Response("no", { status: 401 });
  }
  const upd = await req.json().catch(() => ({}));
  const msg = upd.message;
  if (!msg?.chat?.id) return new Response("ok");
  const text = String(msg.text ?? "").trim();
  const m = /^\/start\s+([a-z0-9]+)_(alumno|admin)_([A-Za-z0-9]{8,40})$/.exec(text);
  if (!m) {
    await reply(msg.chat.id, "Hola 👋 Para recibir avisos, abre la app de entreno, pulsa la campana 🔔 y luego «Conectar Telegram».");
    return new Response("ok");
  }
  const [, app, role, key] = m;
  const db = createClient(Deno.env.get("SUPABASE_URL")!, serviceKey());
  const { data } = await db.from("docs").select("data").eq("app", app).eq("path", "library/tg").maybeSingle();
  if (!data || data.data?.key !== key) {
    await reply(msg.chat.id, "Ese enlace no es válido. Vuelve a pulsar «Conectar Telegram» desde la app.");
    return new Response("ok");
  }
  await db.from("tg_chats").upsert({ app, role, chat_id: msg.chat.id });
  const quien = role === "admin" ? "entrenador" : "alumno";
  await reply(msg.chat.id, `✅ Conectado. A partir de ahora recibirás aquí los avisos de la app (${app}, como ${quien}).`);
  return new Response("ok");
});
