// Conexión con Supabase y Telegram (datos públicos: la seguridad la ponen las contraseñas).
window.SB_CONFIG = {
  url: "https://ahnldmjextacbibtmrcg.supabase.co",
  key: "sb_publishable_o8moLFnFWqpsxIgFgje6Tg_8CAbMj0g",
  bot: "EntrenoPinoFSBot",
  // Alumnos de Adri (para añadir uno nuevo: añadirlo aquí, crear su carpeta y su cuenta <app>@entreno.app)
  students: [
    { app: "alex", name: "Alex", img: "alex/img/tiburon.jpg" },
    { app: "juanma", name: "Juanma", img: "juanma/img/juanma.png" }
  ]
};
