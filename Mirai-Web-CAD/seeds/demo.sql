-- Mirai Web CAD MVP demo seed.
-- Safe to re-run after migration 0001; rows are upserted by primary key.

insert into projects (id, name, owner, status)
values ('prj_demo_road_001', '道路拡幅デモ案件', 'mirai-demo', 'active')
on conflict (id) do update set
  name = excluded.name,
  owner = excluded.owner,
  status = excluded.status,
  updated_at = now();

insert into drawings (id, project_id, name, unit, current_version, state)
values ('dwg_demo_001', 'prj_demo_road_001', '道路拡幅 仮設施工図 MVP', 'mm', 1, 'draft')
on conflict (id) do update set
  name = excluded.name,
  unit = excluded.unit,
  current_version = excluded.current_version,
  state = excluded.state,
  updated_at = now();

insert into drawing_versions (id, drawing_id, version_no, state, content, content_hash, created_by)
values (
  'ver_demo_001_001',
  'dwg_demo_001',
  1,
  'draft',
  '{
    "unit": "mm",
    "layers": ["図枠", "中心線", "構造物", "仮設", "注記"],
    "entities": [
      {"id": "e_frame_1", "type": "line", "layer": "図枠"},
      {"id": "e_center_1", "type": "line", "layer": "中心線"},
      {"id": "e_box_1", "type": "rect", "layer": "構造物"},
      {"id": "e_crane_1", "type": "circle", "layer": "仮設"}
    ]
  }'::jsonb,
  'seed-demo-hash-v1',
  'system'
)
on conflict (id) do update set
  state = excluded.state,
  content = excluded.content,
  content_hash = excluded.content_hash;

insert into audit_logs (id, actor_id, action, target_type, target_id, detail)
values (
  'audit_seed_demo_001',
  'system',
  'seed.loaded',
  'drawing',
  'dwg_demo_001',
  '{"source": "seeds/demo.sql", "purpose": "mvp demo"}'::jsonb
)
on conflict (id) do update set detail = excluded.detail;
