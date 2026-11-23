-- ============================================================
-- Entreno Pino F.S. — configuración de Supabase
-- Pega TODO esto en Supabase → SQL Editor → New query → Run.
-- Se puede ejecutar más de una vez sin romper nada.
-- ============================================================

-- Qué app es cada cuenta: alex@entreno.app → "alex", juanma@entreno.app → "juanma"
create or replace function public.my_app() returns text
language sql stable as $$
  select split_part(coalesce(auth.jwt()->>'email',''),'@',1)
$$;

-- Todos los datos de la app (semanas, ejercicios, sesiones, peso, fotos…)
create table if not exists public.docs (
  app text not null,
  path text not null,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (app, path)
);
alter table public.docs enable row level security;
drop policy if exists "docs propia app" on public.docs;
create policy "docs propia app" on public.docs for all to authenticated
  using (app = public.my_app()) with check (app = public.my_app());

-- Mezcla de cambios (igual que hacía Claude): solo cambia lo que se envía
create or replace function public.jsonb_deep_merge(a jsonb, b jsonb) returns jsonb
language plpgsql immutable as $$
declare k text; r jsonb;
begin
  if a is null or jsonb_typeof(a) <> 'object' or b is null or jsonb_typeof(b) <> 'object' then
    return b;
  end if;
  r := a;
  for k in select jsonb_object_keys(b) loop
    r := jsonb_set(r, array[k], public.jsonb_deep_merge(r->k, b->k), true);
  end loop;
  return r;
end $$;

create or replace function public.merge_doc(p_app text, p_path text, p_patch jsonb) returns void
language plpgsql security invoker as $$
begin
  if p_app <> public.my_app() then raise exception 'Sin permiso'; end if;
  insert into public.docs(app, path, data) values (p_app, p_path, p_patch)
  on conflict (app, path) do update
    set data = public.jsonb_deep_merge(public.docs.data, excluded.data), updated_at = now();
end $$;

create or replace function public.set_doc(p_app text, p_path text, p_data jsonb) returns void
language plpgsql security invoker as $$
begin
  if p_app <> public.my_app() then raise exception 'Sin permiso'; end if;
  insert into public.docs(app, path, data) values (p_app, p_path, p_data)
  on conflict (app, path) do update set data = excluded.data, updated_at = now();
end $$;

-- Cambios en directo entre Alex/Juanma y Adri
do $$ begin
  alter publication supabase_realtime add table public.docs;
exception when duplicate_object then null; end $$;

-- Quién recibe avisos por Telegram
create table if not exists public.tg_chats (
  app text not null,
  role text not null check (role in ('alumno','admin')),
  chat_id bigint not null,
  created_at timestamptz not null default now(),
  primary key (app, role, chat_id)
);
alter table public.tg_chats enable row level security;
drop policy if exists "tg ver propia app" on public.tg_chats;
create policy "tg ver propia app" on public.tg_chats for select to authenticated
  using (app = public.my_app());
drop policy if exists "tg borrar propia app" on public.tg_chats;
create policy "tg borrar propia app" on public.tg_chats for delete to authenticated
  using (app = public.my_app());

-- Fotos y vídeos (privados: solo los ve cada app)
insert into storage.buckets (id, name, public, file_size_limit)
values ('media', 'media', false, 52428800)
on conflict (id) do update set public = false, file_size_limit = 52428800;

drop policy if exists "media propia app" on storage.objects;
create policy "media propia app" on storage.objects for all to authenticated
  using (bucket_id = 'media' and (storage.foldername(name))[1] = public.my_app())
  with check (bucket_id = 'media' and (storage.foldername(name))[1] = public.my_app());
