-- Biblioteca de ejercicios compartida (app 'shared'): todos la leen, solo el entrenador la cambia.
drop policy if exists "compartido lectura" on public.docs;
create policy "compartido lectura" on public.docs for select to authenticated using (app = 'shared');

insert into public.docs(app, path, data)
select 'shared', 'library/exercises',
       jsonb_build_object('exercises', coalesce(data->'exercises','[]'::jsonb),
                          'customGroups', coalesce(data->'customGroups','[]'::jsonb),
                          'customWorks', coalesce(data->'customWorks','[]'::jsonb))
from public.docs where app = 'alex' and path = 'library/main'
on conflict (app, path) do nothing;

select app, path, jsonb_array_length(data->'exercises') as ejercicios from public.docs where app = 'shared';
