-- RestaurantOS Seed Data for Development & Demo
-- Depends on: schema.sql, create_restaurant_tables.sql, create_person_table.sql,
--   create_resource_table.sql, create_event_table.sql, create_document_table.sql,
--   create_inventory_movement_table.sql, create_recipe_tables.sql
--
-- Creates a complete RestaurantOS demo environment:
--   1 demo user, 2 restaurants, 12 persons, 18 resources, 8 documents,
--   20 events/tasks, 30 inventory movements, 6 recipes with ingredients.
--
-- Designed to exercise every dashboard widget:
--   - Today's tasks grouped by responsible (pending + completed)
--   - Upcoming document expirations (valid, expiring_soon, expired)
--   - Low stock items (current_stock < minimum_stock)
--   - Recent inventory movements
--   - Pending alerts (alerta_stock, vencimiento, alerta_rentabilidad)
--   - Stat cards (employees, resources, active docs, completed today, overdue)
--   - Recipe profitability (profitable + unprofitable)
--   - Summary bars on each page
--
-- Idempotent: Uses ON CONFLICT DO NOTHING so the script is safely re-runnable.
-- Atomic: Wrapped in a single transaction.

BEGIN;

-- ============================================================================
-- DEMO USER
-- Email: demo.ros@tremarel.com  /  Password: RestaurantOS2026!
-- ============================================================================
INSERT INTO users (id, email, password_hash, first_name, last_name, role, allowed_modules)
VALUES (
  'a0000000-0000-0000-0000-000000000001',
  'demo.ros@tremarel.com',
  -- bcrypt hash of "RestaurantOS2026!"
  '$2b$12$E99.cPRcBAj8rxhfZ2rQHOMVpVGKBFYg2aFvX7GKPOHvQp/yRGKR2',
  'RestaurantOS',
  'Demo',
  'admin',
  '["restaurant-os"]'
) ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- RESTAURANTS (2)
-- ============================================================================
INSERT INTO restaurant (id, name, address, owner_id)
VALUES
  ('b1000000-0000-0000-0000-000000000001', 'La Parrilla de Andres',  'Cra 7 #72-41, Bogota', 'a0000000-0000-0000-0000-000000000001'),
  ('b1000000-0000-0000-0000-000000000002', 'Sabor Costeno Express', 'Cll 85 #15-23, Bogota', 'a0000000-0000-0000-0000-000000000001')
ON CONFLICT (id) DO NOTHING;

-- Link user to both restaurants
INSERT INTO user_restaurants (user_id, restaurant_id, role)
VALUES
  ('a0000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001', 'admin'),
  ('a0000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000002', 'admin')
ON CONFLICT (user_id, restaurant_id) DO NOTHING;


-- ============================================================================
-- PERSONS (12) — for "La Parrilla de Andres"
-- 7 employees, 3 suppliers, 1 owner — exercises all type chips + summary bar
-- ============================================================================
INSERT INTO person (id, restaurant_id, name, role, email, whatsapp, push_token, type)
VALUES
  -- Employees
  ('c1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001', 'Carlos Martinez',    'Chef Principal',    'carlos@parrilla.co',    '+573001234567', 'fcm_token_carlos', 'employee'),
  ('c1000000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000001', 'Maria Lopez',        'Sous Chef',         'maria@parrilla.co',     '+573001234568', NULL,               'employee'),
  ('c1000000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000001', 'Juan Perez',         'Mesero',            'juan@parrilla.co',      '+573001234569', 'fcm_token_juan',   'employee'),
  ('c1000000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000001', 'Ana Garcia',         'Cajera',            'ana@parrilla.co',       '+573001234570', NULL,               'employee'),
  ('c1000000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000001', 'Pedro Ramirez',      'Mesero',            NULL,                    '+573001234571', NULL,               'employee'),
  ('c1000000-0000-0000-0000-000000000006', 'b1000000-0000-0000-0000-000000000001', 'Laura Torres',       'Administradora',    'laura@parrilla.co',     '+573001234572', 'fcm_token_laura',  'employee'),
  ('c1000000-0000-0000-0000-000000000007', 'b1000000-0000-0000-0000-000000000001', 'Diego Herrera',      'Barman',            NULL,                    '+573001234573', NULL,               'employee'),
  -- Suppliers
  ('c1000000-0000-0000-0000-000000000008', 'b1000000-0000-0000-0000-000000000001', 'Carnes del Llano',   'Proveedor Carnes',  'ventas@carnesllano.co', '+573009876543', NULL,               'supplier'),
  ('c1000000-0000-0000-0000-000000000009', 'b1000000-0000-0000-0000-000000000001', 'Distribuidora ABC',  'Proveedor General', 'pedidos@distabc.co',    '+573009876544', NULL,               'supplier'),
  ('c1000000-0000-0000-0000-000000000010', 'b1000000-0000-0000-0000-000000000001', 'Fruver del Campo',   'Proveedor Verduras','info@fruver.co',        '+573009876545', NULL,               'supplier'),
  -- Owner
  ('c1000000-0000-0000-0000-000000000011', 'b1000000-0000-0000-0000-000000000001', 'Andres Cardona',     'Propietario',       'andres@parrilla.co',    '+573005551234', 'fcm_token_andres', 'owner'),
  -- 1 person for 2nd restaurant
  ('c1000000-0000-0000-0000-000000000012', 'b1000000-0000-0000-0000-000000000002', 'Valentina Ruiz',     'Chef Principal',    'vale@saborcosteno.co',  '+573007771234', NULL,               'employee')
ON CONFLICT (id) DO NOTHING;


-- ============================================================================
-- RESOURCES (18) — for "La Parrilla de Andres"
-- Mix of productos, activos, servicios. Some LOW STOCK to trigger alerts.
-- ============================================================================
INSERT INTO resource (id, restaurant_id, type, name, unit, current_stock, minimum_stock, last_unit_cost)
VALUES
  -- Productos (ingredients) — 12 items, 3 are LOW STOCK
  ('d0100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Lomo de Res',       'kg',     8.0,   15.0,  32000),   -- LOW STOCK
  ('d0100000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Pechuga de Pollo',  'kg',    25.0,   10.0,  14000),
  ('d0100000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Chorizo Santarosano','kg',    3.5,    5.0,  18000),   -- LOW STOCK
  ('d0100000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Papa Criolla',      'kg',    40.0,   20.0,   3500),
  ('d0100000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Arroz',             'kg',    50.0,   25.0,   3200),
  ('d0100000-0000-0000-0000-000000000006', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Cebolla Cabezona',  'kg',    12.0,    8.0,   2800),
  ('d0100000-0000-0000-0000-000000000007', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Tomate',            'kg',    15.0,   10.0,   3000),
  ('d0100000-0000-0000-0000-000000000008', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Aceite Vegetal',    'litros', 2.0,    5.0,   8500),   -- LOW STOCK
  ('d0100000-0000-0000-0000-000000000009', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Sal',               'kg',    10.0,    3.0,   1200),
  ('d0100000-0000-0000-0000-000000000010', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Cerveza Nacional',  'unidad',120.0,  50.0,   2500),
  ('d0100000-0000-0000-0000-000000000011', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Limon',             'kg',    6.0,    4.0,   4000),
  ('d0100000-0000-0000-0000-000000000012', 'b1000000-0000-0000-0000-000000000001', 'producto', 'Aguacate',          'unidad',30.0,   15.0,   2000),
  -- Activos (equipment) — 4 items
  ('d0100000-0000-0000-0000-000000000013', 'b1000000-0000-0000-0000-000000000001', 'activo',   'Parrilla Industrial','unidad',2.0,   1.0,  4500000),
  ('d0100000-0000-0000-0000-000000000014', 'b1000000-0000-0000-0000-000000000001', 'activo',   'Nevera Vertical',   'unidad', 3.0,   2.0,  2800000),
  ('d0100000-0000-0000-0000-000000000015', 'b1000000-0000-0000-0000-000000000001', 'activo',   'Horno Industrial',  'unidad', 1.0,   1.0,  6200000),
  ('d0100000-0000-0000-0000-000000000016', 'b1000000-0000-0000-0000-000000000001', 'activo',   'Licuadora Industrial','unidad',2.0,  1.0,   850000),
  -- Servicios — 2 items
  ('d0100000-0000-0000-0000-000000000017', 'b1000000-0000-0000-0000-000000000001', 'servicio', 'Gas Natural',       'mes',    1.0,   1.0,  350000),
  ('d0100000-0000-0000-0000-000000000018', 'b1000000-0000-0000-0000-000000000001', 'servicio', 'Servicio de Aseo',  'mes',    1.0,   1.0,  180000)
ON CONFLICT (id) DO NOTHING;


-- ============================================================================
-- DOCUMENTS (8) — for "La Parrilla de Andres"
-- Mix of valid, expiring_soon, expired to exercise all status chips + alerts
-- ============================================================================
INSERT INTO document (id, restaurant_id, type, issue_date, expiration_date, person_id, description)
VALUES
  -- VALID (expiration > 30 days from now)
  ('e0100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001', 'camara_comercio',
   '2025-06-01', '2026-06-01', NULL,
   'Registro Camara de Comercio Bogota'),

  ('e0100000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000001', 'contrato',
   '2026-01-15', '2027-01-15', 'c1000000-0000-0000-0000-000000000008',
   'Contrato de suministro de carnes - Carnes del Llano'),

  ('e0100000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000001', 'licencia',
   '2025-09-01', '2026-09-01', NULL,
   'Licencia de funcionamiento'),

  -- EXPIRING SOON (within 30 days — dates relative to ~March 2026)
  ('e0100000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000001', 'manipulacion_alimentos',
   '2025-03-20', '2026-03-20', 'c1000000-0000-0000-0000-000000000001',
   'Certificado manipulacion alimentos - Carlos Martinez'),

  ('e0100000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000001', 'bomberos',
   '2025-03-25', '2026-03-25', NULL,
   'Permiso de Bomberos - Sede principal'),

  ('e0100000-0000-0000-0000-000000000006', 'b1000000-0000-0000-0000-000000000001', 'extintor',
   '2025-04-01', '2026-03-15', NULL,
   'Servicio de extintores - Proxima recarga'),

  -- EXPIRED (already past)
  ('e0100000-0000-0000-0000-000000000007', 'b1000000-0000-0000-0000-000000000001', 'sanidad',
   '2024-12-01', '2025-12-01', NULL,
   'Certificado inspeccion sanitaria - VENCIDO'),

  ('e0100000-0000-0000-0000-000000000008', 'b1000000-0000-0000-0000-000000000001', 'manipulacion_alimentos',
   '2025-02-01', '2026-02-01', 'c1000000-0000-0000-0000-000000000002',
   'Certificado manipulacion alimentos - Maria Lopez - VENCIDO')
ON CONFLICT (id) DO NOTHING;


-- ============================================================================
-- EVENTS / TASKS (20) — for "La Parrilla de Andres"
-- Mix of: today's pending tasks, today's completed, overdue, future, alerts
-- Uses CURRENT_DATE so they're always "today" when seeded
-- ============================================================================
INSERT INTO event (id, restaurant_id, type, description, date, frequency, responsible_id, notification_channel, status, completed_at)
VALUES
  -- ===== TODAY'S PENDING TASKS (6) — shows in dashboard "Tareas de Hoy" =====
  ('f1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Recibir pedido de Carnes del Llano', CURRENT_DATE + TIME '08:00', 'none',
   'c1000000-0000-0000-0000-000000000001', 'whatsapp', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Verificar inventario de bebidas', CURRENT_DATE + TIME '09:30', 'daily',
   'c1000000-0000-0000-0000-000000000004', 'email', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Preparar mise en place almuerzo', CURRENT_DATE + TIME '10:00', 'daily',
   'c1000000-0000-0000-0000-000000000002', 'push', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Revisar reservas del dia', CURRENT_DATE + TIME '07:30', 'daily',
   'c1000000-0000-0000-0000-000000000006', 'email', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000001', 'checklist',
   'Checklist apertura cocina', CURRENT_DATE + TIME '06:30', 'daily',
   'c1000000-0000-0000-0000-000000000001', 'push', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000006', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Limpiar parrillas y campana', CURRENT_DATE + TIME '16:00', 'daily',
   'c1000000-0000-0000-0000-000000000007', 'whatsapp', 'pending', NULL),

  -- ===== TODAY'S COMPLETED TASKS (3) — stats: "tasks_completed_today" =====
  ('f1000000-0000-0000-0000-000000000007', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Abrir caja registradora', CURRENT_DATE + TIME '06:00', 'daily',
   'c1000000-0000-0000-0000-000000000004', 'email', 'completed', CURRENT_TIMESTAMP),

  ('f1000000-0000-0000-0000-000000000008', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Verificar temperatura neveras', CURRENT_DATE + TIME '06:15', 'daily',
   'c1000000-0000-0000-0000-000000000001', 'push', 'completed', CURRENT_TIMESTAMP),

  ('f1000000-0000-0000-0000-000000000009', 'b1000000-0000-0000-0000-000000000001', 'checklist',
   'Revision de aseo banos', CURRENT_DATE + TIME '07:00', 'daily',
   'c1000000-0000-0000-0000-000000000005', 'whatsapp', 'completed', CURRENT_TIMESTAMP),

  -- ===== OVERDUE TASKS (3) — yesterday/earlier, still pending =====
  ('f1000000-0000-0000-0000-000000000010', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Pagar factura gas natural', CURRENT_DATE - INTERVAL '2 days' + TIME '10:00', 'none',
   'c1000000-0000-0000-0000-000000000006', 'email', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000011', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Solicitar cotizacion extintores', CURRENT_DATE - INTERVAL '3 days' + TIME '14:00', 'none',
   'c1000000-0000-0000-0000-000000000006', 'email', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000012', 'b1000000-0000-0000-0000-000000000001', 'pago',
   'Pago nomina quincenal', CURRENT_DATE - INTERVAL '1 day' + TIME '09:00', 'none',
   'c1000000-0000-0000-0000-000000000011', 'email', 'pending', NULL),

  -- ===== FUTURE TASKS (4) — upcoming this week =====
  ('f1000000-0000-0000-0000-000000000013', 'b1000000-0000-0000-0000-000000000001', 'turno',
   'Turno extra sabado - Juan', CURRENT_DATE + INTERVAL '2 days' + TIME '11:00', 'none',
   'c1000000-0000-0000-0000-000000000003', 'whatsapp', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000014', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Inventario mensual completo', CURRENT_DATE + INTERVAL '3 days' + TIME '08:00', 'monthly',
   'c1000000-0000-0000-0000-000000000006', 'email', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000015', 'b1000000-0000-0000-0000-000000000001', 'tarea',
   'Reunion con proveedor frutas', CURRENT_DATE + INTERVAL '1 day' + TIME '15:00', 'none',
   'c1000000-0000-0000-0000-000000000010', 'email', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000016', 'b1000000-0000-0000-0000-000000000001', 'pago',
   'Pago arriendo local', CURRENT_DATE + INTERVAL '5 days' + TIME '09:00', 'monthly',
   'c1000000-0000-0000-0000-000000000011', 'email', 'pending', NULL),

  -- ===== ALERT EVENTS (4) — shows in dashboard "Alertas Pendientes" =====
  ('f1000000-0000-0000-0000-000000000017', 'b1000000-0000-0000-0000-000000000001', 'alerta_stock',
   'Stock bajo: Lomo de Res (8 kg / min 15 kg)', CURRENT_DATE + TIME '00:00', 'none',
   NULL, 'push', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000018', 'b1000000-0000-0000-0000-000000000001', 'alerta_stock',
   'Stock bajo: Aceite Vegetal (2 lt / min 5 lt)', CURRENT_DATE + TIME '00:00', 'none',
   NULL, 'push', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000019', 'b1000000-0000-0000-0000-000000000001', 'vencimiento',
   'Certificado manipulacion alimentos vence en 14 dias', CURRENT_DATE + TIME '00:00', 'none',
   NULL, 'email', 'pending', NULL),

  ('f1000000-0000-0000-0000-000000000020', 'b1000000-0000-0000-0000-000000000001', 'alerta_rentabilidad',
   'Receta "Bandeja Paisa" margen bajo: 52%', CURRENT_DATE + TIME '00:00', 'none',
   NULL, 'email', 'pending', NULL)
ON CONFLICT (id) DO NOTHING;


-- ============================================================================
-- INVENTORY MOVEMENTS (30) — for "La Parrilla de Andres"
-- Recent movements (last 7 days) to populate dashboard table + resource drawer
-- ============================================================================
INSERT INTO inventory_movement (id, resource_id, restaurant_id, type, quantity, reason, date, person_id, notes)
VALUES
  -- === Day -6: Weekly purchase delivery ===
  ('a0100000-0000-0000-0000-000000000001', 'd0100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001',
   'entry', 20.0, 'compra', CURRENT_TIMESTAMP - INTERVAL '6 days', 'c1000000-0000-0000-0000-000000000008', 'Pedido semanal carnes'),
  ('a0100000-0000-0000-0000-000000000002', 'd0100000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000001',
   'entry', 15.0, 'compra', CURRENT_TIMESTAMP - INTERVAL '6 days', 'c1000000-0000-0000-0000-000000000008', 'Pedido semanal pollo'),
  ('a0100000-0000-0000-0000-000000000003', 'd0100000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000001',
   'entry', 50.0, 'compra', CURRENT_TIMESTAMP - INTERVAL '6 days', 'c1000000-0000-0000-0000-000000000009', 'Bulto arroz 50kg'),

  -- === Day -5: Produce + usage ===
  ('a0100000-0000-0000-0000-000000000004', 'd0100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001',
   'exit', 3.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '5 days', 'c1000000-0000-0000-0000-000000000001', 'Servicio almuerzo'),
  ('a0100000-0000-0000-0000-000000000005', 'd0100000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000001',
   'exit', 2.5, 'uso', CURRENT_TIMESTAMP - INTERVAL '5 days', 'c1000000-0000-0000-0000-000000000001', 'Servicio almuerzo'),
  ('a0100000-0000-0000-0000-000000000006', 'd0100000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000001',
   'exit', 5.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '5 days', 'c1000000-0000-0000-0000-000000000002', 'Papas para acompanamiento'),
  ('a0100000-0000-0000-0000-000000000007', 'd0100000-0000-0000-0000-000000000010', 'b1000000-0000-0000-0000-000000000001',
   'exit', 24.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '5 days', 'c1000000-0000-0000-0000-000000000007', 'Cervezas servicio noche'),

  -- === Day -4: Recipe production ===
  ('a0100000-0000-0000-0000-000000000008', 'd0100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001',
   'exit', 2.0, 'receta', CURRENT_TIMESTAMP - INTERVAL '4 days', 'c1000000-0000-0000-0000-000000000001', 'Produccion Lomo al Trapo x4'),
  ('a0100000-0000-0000-0000-000000000009', 'd0100000-0000-0000-0000-000000000009', 'b1000000-0000-0000-0000-000000000001',
   'exit', 0.2, 'receta', CURRENT_TIMESTAMP - INTERVAL '4 days', 'c1000000-0000-0000-0000-000000000001', 'Sal para Lomo al Trapo'),
  ('a0100000-0000-0000-0000-000000000010', 'd0100000-0000-0000-0000-000000000006', 'b1000000-0000-0000-0000-000000000001',
   'exit', 1.0, 'receta', CURRENT_TIMESTAMP - INTERVAL '4 days', 'c1000000-0000-0000-0000-000000000001', 'Cebolla para guarnicion'),

  -- === Day -3: Spoilage + adjustment ===
  ('a0100000-0000-0000-0000-000000000011', 'd0100000-0000-0000-0000-000000000007', 'b1000000-0000-0000-0000-000000000001',
   'exit', 2.0, 'merma', CURRENT_TIMESTAMP - INTERVAL '3 days', 'c1000000-0000-0000-0000-000000000002', 'Tomates danados - calor'),
  ('a0100000-0000-0000-0000-000000000012', 'd0100000-0000-0000-0000-000000000012', 'b1000000-0000-0000-0000-000000000001',
   'exit', 5.0, 'merma', CURRENT_TIMESTAMP - INTERVAL '3 days', 'c1000000-0000-0000-0000-000000000002', 'Aguacates demasiado maduros'),
  ('a0100000-0000-0000-0000-000000000013', 'd0100000-0000-0000-0000-000000000010', 'b1000000-0000-0000-0000-000000000001',
   'entry', 48.0, 'compra', CURRENT_TIMESTAMP - INTERVAL '3 days', 'c1000000-0000-0000-0000-000000000009', 'Reposicion cervezas'),

  -- === Day -2: Daily usage ===
  ('a0100000-0000-0000-0000-000000000014', 'd0100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001',
   'exit', 4.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '2 days', 'c1000000-0000-0000-0000-000000000001', 'Servicio fin de semana alto'),
  ('a0100000-0000-0000-0000-000000000015', 'd0100000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000001',
   'exit', 2.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '2 days', 'c1000000-0000-0000-0000-000000000001', 'Chorizos servicio sabado'),
  ('a0100000-0000-0000-0000-000000000016', 'd0100000-0000-0000-0000-000000000008', 'b1000000-0000-0000-0000-000000000001',
   'exit', 2.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '2 days', 'c1000000-0000-0000-0000-000000000002', 'Aceite para freidora'),
  ('a0100000-0000-0000-0000-000000000017', 'd0100000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000001',
   'exit', 8.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '2 days', 'c1000000-0000-0000-0000-000000000002', 'Arroz servicio completo'),
  ('a0100000-0000-0000-0000-000000000018', 'd0100000-0000-0000-0000-000000000011', 'b1000000-0000-0000-0000-000000000001',
   'exit', 3.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '2 days', 'c1000000-0000-0000-0000-000000000007', 'Limones para limonada y bar'),

  -- === Day -1: Yesterday ===
  ('a0100000-0000-0000-0000-000000000019', 'd0100000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000001',
   'exit', 3.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '1 day', 'c1000000-0000-0000-0000-000000000001', 'Pollo servicio almuerzo'),
  ('a0100000-0000-0000-0000-000000000020', 'd0100000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000001',
   'exit', 6.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '1 day', 'c1000000-0000-0000-0000-000000000002', 'Papa criolla acompanamiento'),
  ('a0100000-0000-0000-0000-000000000021', 'd0100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001',
   'exit', 3.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '1 day', 'c1000000-0000-0000-0000-000000000001', 'Res servicio cena'),
  ('a0100000-0000-0000-0000-000000000022', 'd0100000-0000-0000-0000-000000000010', 'b1000000-0000-0000-0000-000000000001',
   'exit', 36.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '1 day', 'c1000000-0000-0000-0000-000000000007', 'Cervezas domingo'),

  -- === Today: Fresh movements ===
  ('a0100000-0000-0000-0000-000000000023', 'd0100000-0000-0000-0000-000000000006', 'b1000000-0000-0000-0000-000000000001',
   'entry', 10.0, 'compra', CURRENT_TIMESTAMP - INTERVAL '2 hours', 'c1000000-0000-0000-0000-000000000010', 'Entrega verduras Fruver del Campo'),
  ('a0100000-0000-0000-0000-000000000024', 'd0100000-0000-0000-0000-000000000007', 'b1000000-0000-0000-0000-000000000001',
   'entry', 8.0, 'compra', CURRENT_TIMESTAMP - INTERVAL '2 hours', 'c1000000-0000-0000-0000-000000000010', 'Entrega tomates frescos'),
  ('a0100000-0000-0000-0000-000000000025', 'd0100000-0000-0000-0000-000000000012', 'b1000000-0000-0000-0000-000000000001',
   'entry', 20.0, 'compra', CURRENT_TIMESTAMP - INTERVAL '2 hours', 'c1000000-0000-0000-0000-000000000010', 'Entrega aguacates'),
  ('a0100000-0000-0000-0000-000000000026', 'd0100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001',
   'exit', 1.5, 'uso', CURRENT_TIMESTAMP - INTERVAL '1 hour', 'c1000000-0000-0000-0000-000000000001', 'Preparacion almuerzo hoy'),
  ('a0100000-0000-0000-0000-000000000027', 'd0100000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000001',
   'exit', 3.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '1 hour', 'c1000000-0000-0000-0000-000000000002', 'Arroz almuerzo hoy'),
  ('a0100000-0000-0000-0000-000000000028', 'd0100000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000001',
   'exit', 1.5, 'produccion', CURRENT_TIMESTAMP - INTERVAL '30 minutes', 'c1000000-0000-0000-0000-000000000001', 'Produccion picada x6'),
  ('a0100000-0000-0000-0000-000000000029', 'd0100000-0000-0000-0000-000000000008', 'b1000000-0000-0000-0000-000000000001',
   'exit', 1.0, 'uso', CURRENT_TIMESTAMP - INTERVAL '30 minutes', 'c1000000-0000-0000-0000-000000000002', 'Aceite freidora hoy'),
  ('a0100000-0000-0000-0000-000000000030', 'd0100000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000001',
   'entry', 15.0, 'ajuste', CURRENT_TIMESTAMP - INTERVAL '15 minutes', 'c1000000-0000-0000-0000-000000000006', 'Ajuste inventario papa tras conteo')
ON CONFLICT (id) DO NOTHING;


-- ============================================================================
-- RECIPES (6) — for "La Parrilla de Andres"
-- 4 profitable (margin >= 60%), 2 unprofitable — exercises profitability badges
-- ============================================================================
-- Recipe 1: Lomo al Trapo — PROFITABLE (72% margin)
INSERT INTO recipe (id, restaurant_id, name, sale_price, current_cost, margin_percent, is_profitable, is_active)
VALUES ('aa100000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001',
        'Lomo al Trapo', 68000, 19040, 72.00, TRUE, TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO recipe_item (id, recipe_id, resource_id, quantity, unit)
VALUES
  ('bb100000-0000-0000-0000-000000000001', 'aa100000-0000-0000-0000-000000000001', 'd0100000-0000-0000-0000-000000000001', 0.5, 'kg'),
  ('bb100000-0000-0000-0000-000000000002', 'aa100000-0000-0000-0000-000000000001', 'd0100000-0000-0000-0000-000000000009', 0.2, 'kg'),
  ('bb100000-0000-0000-0000-000000000003', 'aa100000-0000-0000-0000-000000000001', 'd0100000-0000-0000-0000-000000000006', 0.15, 'kg')
ON CONFLICT (id) DO NOTHING;

-- Recipe 2: Pollo a la Parrilla — PROFITABLE (69% margin)
INSERT INTO recipe (id, restaurant_id, name, sale_price, current_cost, margin_percent, is_profitable, is_active)
VALUES ('aa100000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000001',
        'Pollo a la Parrilla', 38000, 11780, 69.00, TRUE, TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO recipe_item (id, recipe_id, resource_id, quantity, unit)
VALUES
  ('bb100000-0000-0000-0000-000000000004', 'aa100000-0000-0000-0000-000000000002', 'd0100000-0000-0000-0000-000000000002', 0.35, 'kg'),
  ('bb100000-0000-0000-0000-000000000005', 'aa100000-0000-0000-0000-000000000002', 'd0100000-0000-0000-0000-000000000004', 0.3, 'kg'),
  ('bb100000-0000-0000-0000-000000000006', 'aa100000-0000-0000-0000-000000000002', 'd0100000-0000-0000-0000-000000000005', 0.2, 'kg'),
  ('bb100000-0000-0000-0000-000000000007', 'aa100000-0000-0000-0000-000000000002', 'd0100000-0000-0000-0000-000000000008', 0.05, 'litros')
ON CONFLICT (id) DO NOTHING;

-- Recipe 3: Picada Parrillera (para 2) — PROFITABLE (65% margin)
INSERT INTO recipe (id, restaurant_id, name, sale_price, current_cost, margin_percent, is_profitable, is_active)
VALUES ('aa100000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000001',
        'Picada Parrillera (2 personas)', 85000, 29750, 65.00, TRUE, TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO recipe_item (id, recipe_id, resource_id, quantity, unit)
VALUES
  ('bb100000-0000-0000-0000-000000000008', 'aa100000-0000-0000-0000-000000000003', 'd0100000-0000-0000-0000-000000000001', 0.3, 'kg'),
  ('bb100000-0000-0000-0000-000000000009', 'aa100000-0000-0000-0000-000000000003', 'd0100000-0000-0000-0000-000000000002', 0.25, 'kg'),
  ('bb100000-0000-0000-0000-000000000010', 'aa100000-0000-0000-0000-000000000003', 'd0100000-0000-0000-0000-000000000003', 0.25, 'kg'),
  ('bb100000-0000-0000-0000-000000000011', 'aa100000-0000-0000-0000-000000000003', 'd0100000-0000-0000-0000-000000000004', 0.4, 'kg'),
  ('bb100000-0000-0000-0000-000000000012', 'aa100000-0000-0000-0000-000000000003', 'd0100000-0000-0000-0000-000000000012', 1.0, 'unidad')
ON CONFLICT (id) DO NOTHING;

-- Recipe 4: Limonada Natural — PROFITABLE (82% margin)
INSERT INTO recipe (id, restaurant_id, name, sale_price, current_cost, margin_percent, is_profitable, is_active)
VALUES ('aa100000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000001',
        'Limonada Natural', 8000, 1440, 82.00, TRUE, TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO recipe_item (id, recipe_id, resource_id, quantity, unit)
VALUES
  ('bb100000-0000-0000-0000-000000000013', 'aa100000-0000-0000-0000-000000000004', 'd0100000-0000-0000-0000-000000000011', 0.15, 'kg'),
  ('bb100000-0000-0000-0000-000000000014', 'aa100000-0000-0000-0000-000000000004', 'd0100000-0000-0000-0000-000000000009', 0.02, 'kg')
ON CONFLICT (id) DO NOTHING;

-- Recipe 5: Bandeja Paisa — NOT PROFITABLE (52% margin, below 60% threshold)
INSERT INTO recipe (id, restaurant_id, name, sale_price, current_cost, margin_percent, is_profitable, is_active)
VALUES ('aa100000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000001',
        'Bandeja Paisa', 35000, 16800, 52.00, FALSE, TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO recipe_item (id, recipe_id, resource_id, quantity, unit)
VALUES
  ('bb100000-0000-0000-0000-000000000015', 'aa100000-0000-0000-0000-000000000005', 'd0100000-0000-0000-0000-000000000001', 0.2, 'kg'),
  ('bb100000-0000-0000-0000-000000000016', 'aa100000-0000-0000-0000-000000000005', 'd0100000-0000-0000-0000-000000000003', 0.15, 'kg'),
  ('bb100000-0000-0000-0000-000000000017', 'aa100000-0000-0000-0000-000000000005', 'd0100000-0000-0000-0000-000000000005', 0.3, 'kg'),
  ('bb100000-0000-0000-0000-000000000018', 'aa100000-0000-0000-0000-000000000005', 'd0100000-0000-0000-0000-000000000004', 0.2, 'kg'),
  ('bb100000-0000-0000-0000-000000000019', 'aa100000-0000-0000-0000-000000000005', 'd0100000-0000-0000-0000-000000000012', 1.0, 'unidad'),
  ('bb100000-0000-0000-0000-000000000020', 'aa100000-0000-0000-0000-000000000005', 'd0100000-0000-0000-0000-000000000008', 0.1, 'litros')
ON CONFLICT (id) DO NOTHING;

-- Recipe 6: Costillas BBQ — NOT PROFITABLE (45% margin, well below threshold)
INSERT INTO recipe (id, restaurant_id, name, sale_price, current_cost, margin_percent, is_profitable, is_active)
VALUES ('aa100000-0000-0000-0000-000000000006', 'b1000000-0000-0000-0000-000000000001',
        'Costillas BBQ', 52000, 28600, 45.00, FALSE, TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO recipe_item (id, recipe_id, resource_id, quantity, unit)
VALUES
  ('bb100000-0000-0000-0000-000000000021', 'aa100000-0000-0000-0000-000000000006', 'd0100000-0000-0000-0000-000000000001', 0.6, 'kg'),
  ('bb100000-0000-0000-0000-000000000022', 'aa100000-0000-0000-0000-000000000006', 'd0100000-0000-0000-0000-000000000006', 0.2, 'kg'),
  ('bb100000-0000-0000-0000-000000000023', 'aa100000-0000-0000-0000-000000000006', 'd0100000-0000-0000-0000-000000000007', 0.15, 'kg'),
  ('bb100000-0000-0000-0000-000000000024', 'aa100000-0000-0000-0000-000000000006', 'd0100000-0000-0000-0000-000000000008', 0.08, 'litros'),
  ('bb100000-0000-0000-0000-000000000025', 'aa100000-0000-0000-0000-000000000006', 'd0100000-0000-0000-0000-000000000009', 0.05, 'kg')
ON CONFLICT (id) DO NOTHING;


-- ============================================================================
-- VERIFY COUNTS
-- ============================================================================
DO $$
DECLARE
  v_users       INT;
  v_restaurants INT;
  v_persons     INT;
  v_resources   INT;
  v_documents   INT;
  v_events      INT;
  v_movements   INT;
  v_recipes     INT;
  v_items       INT;
BEGIN
  SELECT COUNT(*) INTO v_users       FROM users           WHERE email = 'demo.ros@tremarel.com';
  SELECT COUNT(*) INTO v_restaurants FROM restaurant       WHERE id IN ('b1000000-0000-0000-0000-000000000001','b1000000-0000-0000-0000-000000000002');
  SELECT COUNT(*) INTO v_persons     FROM person           WHERE restaurant_id = 'b1000000-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_resources   FROM resource         WHERE restaurant_id = 'b1000000-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_documents   FROM document         WHERE restaurant_id = 'b1000000-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_events      FROM event            WHERE restaurant_id = 'b1000000-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_movements   FROM inventory_movement WHERE restaurant_id = 'b1000000-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_recipes     FROM recipe           WHERE restaurant_id = 'b1000000-0000-0000-0000-000000000001';
  SELECT COUNT(*) INTO v_items       FROM recipe_item      WHERE recipe_id IN (SELECT id FROM recipe WHERE restaurant_id = 'b1000000-0000-0000-0000-000000000001');

  RAISE NOTICE '';
  RAISE NOTICE '========================================';
  RAISE NOTICE '  RestaurantOS Seed Data Summary';
  RAISE NOTICE '========================================';
  RAISE NOTICE '  Users:        %', v_users;
  RAISE NOTICE '  Restaurants:  %', v_restaurants;
  RAISE NOTICE '  Persons:      %', v_persons;
  RAISE NOTICE '  Resources:    %', v_resources;
  RAISE NOTICE '  Documents:    %', v_documents;
  RAISE NOTICE '  Events:       %', v_events;
  RAISE NOTICE '  Movements:    %', v_movements;
  RAISE NOTICE '  Recipes:      %', v_recipes;
  RAISE NOTICE '  Recipe Items: %', v_items;
  RAISE NOTICE '========================================';
END $$;

COMMIT;
