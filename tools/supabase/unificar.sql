-- Unificación: la cuenta adri@entreno.app puede entrar en todas las apps de alumnos.
create or replace function public.can_app(p_app text) returns boolean
language sql stable as $$
  select public.my_app() = p_app or public.my_app() = 'adri'
$$;

drop policy if exists "docs propia app" on public.docs;
create policy "docs propia app" on public.docs for all to authenticated
  using (public.can_app(app)) with check (public.can_app(app));

create or replace function public.merge_doc(p_app text, p_path text, p_patch jsonb) returns void
language plpgsql security invoker as $$
begin
  if not public.can_app(p_app) then raise exception 'Sin permiso'; end if;
  insert into public.docs(app, path, data) values (p_app, p_path, p_patch)
  on conflict (app, path) do update
    set data = public.jsonb_deep_merge(public.docs.data, excluded.data), updated_at = now();
end $$;

create or replace function public.set_doc(p_app text, p_path text, p_data jsonb) returns void
language plpgsql security invoker as $$
begin
  if not public.can_app(p_app) then raise exception 'Sin permiso'; end if;
  insert into public.docs(app, path, data) values (p_app, p_path, p_data)
  on conflict (app, path) do update set data = excluded.data, updated_at = now();
end $$;

drop policy if exists "tg ver propia app" on public.tg_chats;
create policy "tg ver propia app" on public.tg_chats for select to authenticated
  using (public.can_app(app));
drop policy if exists "tg borrar propia app" on public.tg_chats;
create policy "tg borrar propia app" on public.tg_chats for delete to authenticated
  using (public.can_app(app));

drop policy if exists "media propia app" on storage.objects;
create policy "media propia app" on storage.objects for all to authenticated
  using (bucket_id = 'media' and public.can_app((storage.foldername(name))[1]))
  with check (bucket_id = 'media' and public.can_app((storage.foldername(name))[1]));
