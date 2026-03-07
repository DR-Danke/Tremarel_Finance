# LUTEC — Discovery & Levantamiento de Procesos
## Documento Consolidado de Reuniones | 4 de marzo de 2026

---

## 1. PERFIL DEL CLIENTE (Datos Firmográficos)

| Campo | Detalle |
|---|---|
| **Razón Social** | Grupo Lutec S.A.S |
| **Ubicación** | Bogotá D.C., Colombia |
| **Sector** | Construcción / Iluminación / Ingeniería Eléctrica |
| **Objeto Social** | Comercio al por menor de electrodomésticos, gasodomésticos y equipos de iluminación; instalaciones eléctricas de la construcción |
| **Modelo de negocio** | B2B — Proveedor aliado de constructoras; integrador de iluminación e ingeniería eléctrica |
| **Verticales** | 3 líneas: (1) Proyectos de ingeniería eléctrica, (2) Venta directa de iluminación, (3) Licitaciones/proyectos públicos |
| **Clientes** | Constructoras colombianas (Inge Urbe, etc.) |
| **Tamaño estimado** | ~50-80 empleados (8 personas en Compras, 6 en Presupuestos, equipo financiero, inventarios, 47 bodegas) |
| **ERP actual** | Word Office (sistema contable actual) |
| **ERP en migración** | Auranet (ERP chileno, especializado en construcción — migración iniciada nov. 2025) |
| **Herramientas** | Monday.com (gestión de tareas), Excel (presupuestos, Kardex, APUs), BIM (revisión de planos 3D) |
| **Contacto principal** | Daniel Giraldo (Gerencia General) |
| **Website** | www.lutec.com.co |

---

## 2. STAKEHOLDERS Y SPEAKERS IDENTIFICADOS

| Nombre | Rol / Área | Participó en |
|---|---|---|
| **Daniel Giraldo** | Gerente General / Sponsor del proyecto | Conciliación bancaria, Gerencia (x2) |
| **Catalina Carranza** | Gerente Financiera | Conciliación bancaria, Facturación/Compras |
| **Oscar Pinzón** | Director de Presupuestos | Presupuesto (x3) |
| **Wendy** | Compras / Logística | Facturación/Compras |
| **José** | Coordinador de Inventarios | Conciliación bancaria |
| **Marco** | Jefe de Compras (no presente) | Mencionado como fuente de histórico de costos |
| **Daniel Cardona** | Consultor KAI Partners — Discovery lead | Todas las sesiones |

---

## 3. MAPA DE ÁREAS Y PROCESOS LEVANTADOS

### 3.1 Contabilidad y Tesorería (Catalina Carranza)

**Equipo:** Contador junior, persona de tesorería (dedicada full-time a conciliaciones de egresos), coordinadora de cartera.

**Proceso de conciliación bancaria:**
- 5 cuentas bancarias: 2 cuentas de ahorro (Davivienda, Bogotá), 1 cuenta corriente, 2 fiducias
- Descarga DIARIA de movimientos bancarios (Excel + PDF como soporte)
- Conciliación diaria de entradas y salidas para egresos y recibos de caja
- Conciliación mensual completa al cierre
- Usan concatenares y buscares en Excel como método propio para acelerar cruces
- ~30 reglas contables para conciliaciones
- Auxiliares descargados de Word Office (1 por banco = 5 auxiliares mensuales)

**Proceso de facturación electrónica (RADIAN / DIAN):**
- +500 facturas mensuales de compra (95%+ nacionales)
- Descarga diaria de Excel de la DIAN con facturas recibidas
- Contabilización una a una: validan OC + RP + factura
- Eventos de aceptación/rechazo ante DIAN vía XML (uno a uno = "mamera")
- Descubrimiento reciente: proveedor externo que hace descarga masiva de XML (~$13,000 COP por ~500 facturas) — redujo 2 personas a 2 horas de trabajo
- 2 personas dedicadas a proceso RADIAN antes de este hallazgo

**Proceso de cartera / cuentas por cobrar:**
- Clientes pagan por fiducias → no detallan tercero ni concepto de pago
- Una sola fiducia puede enviar pagos de múltiples clientes
- Coordinadora de cartera tiene mapeo manual de qué fiducias pagan qué clientes, pero no siempre funciona
- Retenciones variables por cliente (mismo producto, diferentes porcentajes)

### 3.2 Inventarios (José)

**Equipo:** Coordinación de inventarios, almacenistas en bodegas.

**Estructura:**
- 47 bodegas (en obra y centrales)
- ~15,000 productos en base de datos (pueden repetirse por calidad/cliente)
- Kardex manual en Excel como respaldo del sistema Word Office
- Almacenistas reportan DIARIAMENTE entradas y salidas vía correo (PDF)
- Coordinación monta consumos en Word Office con base en reportes

**Flujo:**
- Recepción: almacenista valida OC vs. entrega (cantidades, referencias, marcas) → crea RP (Remisión Proveedor) en Word Office
- Salida: vía Requisición (RQ) para ingeniería, o Pedido para iluminación
- Reporte semanal a Ingeniería e Iluminación de inventarios disponibles
- No hay análisis histórico de provisión/compras (reconocido como oportunidad no ejecutada)
- Picos de entrada: primeras 1.5 semanas del mes (~50 OC diarias), luego incrementan salidas

### 3.3 Compras (Wendy)

**Equipo:** 8 personas en compras.

**Flujo de compras:**
1. Reciben requerimiento de Ingeniería o Iluminación vía Monday
2. Generan OC en Word Office → descargan → suben a Monday
3. Envían OC al proveedor
4. Proveedor entrega → Inventarios hace RP
5. **GAP CRÍTICO:** Subida de soportes a Monday es donde tienen carencias
   - Proveedores no siempre envían soportes con factura
   - Obras sin almacenista = no hay quién certifique recepción
   - Soportes llegan por correo y WhatsApp (16 puntos de datos: 8 WhatsApp + 8 correos de los compradores + correo de facturación)
6. Sin soportes completos, Contabilidad no puede contabilizar → factura queda en pendiente
7. No hay protocolo de rechazo automático de facturas sin soporte

**Flujo iluminación (venta directa):**
- Comercial cotiza directamente con proveedores Y con clientes (juez y parte)
- Comercial sube cotización en Excel a Monday
- Compras recibe la solicitud pero la negociación la hizo Comercial
- Precios fluctúan diariamente → no sirve histórico → deben llamar a proveedor cada vez
- No consultan inventario al cotizar → comprometen entregas sin verificar stock
- Descoordinación: Comercial negocia tiempos sin validar con Logística

### 3.4 Presupuestos (Oscar Pinzón)

**Equipo:** 6 personas, dedicadas 100% a presupuestar.
**Volumen:** 10-12 presupuestos POR SEMANA.

**Flujo de presupuestación:**
1. Cliente (constructora) envía Excel con sábana de cantidades — cada cliente tiene formato propio
2. Oscar asigna en Monday → presupuestador toma Excel del cliente
3. Codificación manual: buscan en base de APUs existente (Excel con filtros) para asociar códigos a actividades
4. Cada actividad tiene insumos, cantidades, rendimientos → se pegan manualmente
5. **Tiempo por presupuesto nuevo: hasta 3 DÍAS de trabajo manual por codificación**
6. Muchos ítems se repiten entre presupuestos → automatización obvia
7. Validación vs. base de productos/proveedores para precios
8. Una persona dedicada exclusivamente a BIM: revisa planos 3D para detectar anomalías (alturas, especificaciones no evidentes en 2D)
9. Devuelven al cliente el mismo Excel completado con precios y notas

**Base de datos de APUs:**
- Construida internamente en Excel con filtros
- Categorías: tuberías (tipos, diámetros, ductos), cajas, platinas, cables, etc.
- Cada APU tiene: insumos, incidencias por unidad/metro, tiempos de obra, proveedor mapeado
- Base incompleta — se alimenta conforme llegan nuevos presupuestos

**Valor diferenciador perdido:**
- Antes revisaban planos de clientes y devolvían observaciones técnicas ("su diseño no cumple norma, le faltan cantidades")
- Esto les ganó clientes grandes
- Ya no lo hacen por volumen de trabajo → oportunidad de recuperar con automatización

### 3.5 Gerencia (Daniel Giraldo)

**Visión estratégica:**
- Migración a ERP Auranet (desde nov. 2025) — decidido por incapacidad de Word Office para control presupuestal por obra
- Competencia directa de Auranet en Colombia: "5" (no les funcionó por modelo de venta directa)
- Doble contabilidad temporal durante migración
- NO quiere reducir personal → quiere liberar equipo para nuevos consorcios
- Áreas faltantes por levantar: Ingeniería, SST, RRHH, Proyectos Públicos
- Interés en reducir cierre contable y conciliaciones para liberar recursos
- Solicitó propuesta y cruce de archivos de conciliación (entrega entre mañana y pasado)

---

## 4. PAIN POINTS CONSOLIDADOS (Matriz de Dolores)

### 🔴 CRÍTICOS (Alto impacto en operación y rentabilidad)

| # | Dolor | Área | Impacto cuantificado | Frecuencia |
|---|---|---|---|---|
| P1 | Codificación manual de presupuestos (APUs) | Presupuestos | Hasta 3 días por proyecto × 10-12 proyectos/semana = ~30-36 días-hombre/semana | Diario |
| P2 | Proceso RADIAN uno a uno (+500 facturas/mes) | Contabilidad | 2 personas dedicadas full-time antes de solución externa | Diario |
| P3 | Falta de soportes en cadena OC→RP→Factura | Compras + Contabilidad | Retraso en contabilización → retraso en cierre → informes 1 semana atrasados | Diario |
| P4 | Conciliación bancaria manual (5 bancos) | Tesorería | 1 persona dedicada full-time a conciliar egresos diarios | Diario |
| P5 | Pagos de fiducias sin detalle de tercero | Cartera | Demora significativa en identificar pagos → afecta cierre | Por evento |
| P6 | Comercial como juez y parte (cotiza y vende) | Comercial/Compras | Descoordinación en precios, tiempos, despachos; margen no controlado | Permanente |

### 🟡 IMPORTANTES (Impacto en eficiencia y control)

| # | Dolor | Área | Impacto | Frecuencia |
|---|---|---|---|---|
| P7 | No hay control presupuestal por obra en Word Office | Finanzas | No pueden generar alertas de sobrecosto ni controlar bolsa por proyecto | Permanente |
| P8 | Inventario sin análisis histórico de provisión | Inventarios | No se hace proyección de compras basada en histórico | Permanente |
| P9 | 16 puntos de entrada de documentos (8 WhatsApp + 8 correos + correo facturación) | Compras | Fragmentación documental → pérdida de trazabilidad | Diario |
| P10 | Obras sin almacenista = sin RP | Inventarios | No hay certificación de recepción → factura queda en limbo | Por proyecto |
| P11 | Precios de iluminación fluctúan diariamente | Compras | No sirve histórico → llamada manual a proveedor cada cotización | Diario |
| P12 | Base de APUs incompleta y en construcción | Presupuestos | Cada presupuesto nuevo puede requerir crear APUs desde cero | Por proyecto |
| P13 | No se devuelven revisiones técnicas a clientes por falta de tiempo | Presupuestos | Pérdida de propuesta de valor diferenciadora | Permanente |

### 🟢 OPORTUNIDADES (Quick wins identificados)

| # | Oportunidad | Área | Impacto esperado |
|---|---|---|---|
| O1 | Descarga masiva XML (ya probada con proveedor externo) | Contabilidad | De 2 personas full-time a 2 horas de trabajo |
| O2 | Automatización de match APUs por similitud | Presupuestos | Reducir 3 días a horas por presupuesto |
| O3 | Rechazo automático de facturas sin soporte | Contabilidad | Eliminar ciclos de revisión y seguimiento |
| O4 | Alertas automáticas a proveedores en obras sin almacenista | Compras | Eliminar gap de soportes de entrega |
| O5 | Matriz consolidada de listas de precios por proveedor | Compras | Cotización automatizada sin llamar proveedor |
| O6 | Reglas contables para conciliación de fiducias (~80% de casos) | Cartera | Reducir tiempo de cruce de pagos de fiducias |

---

## 5. FLUJOS DE TRABAJO MAPEADOS

### 5.1 Flujo de Compra → Facturación → Pago (Ingeniería)

```
INGENIERÍA → Requerimiento (Monday)
    ↓
PRESUPUESTOS → Codifica APUs → Cotiza → Devuelve a cliente
    ↓
CLIENTE → Aprueba OC
    ↓
COMPRAS → Genera OC en Word Office → Sube a Monday → Envía a proveedor
    ↓
PROVEEDOR → Entrega mercancía
    ↓
INVENTARIOS → Valida OC vs. entrega → Crea RP en Word Office
    ↓
CONTABILIDAD → Cruza OC + RP + Factura (DIAN) → Contabiliza
    ↓                                    ↗ [Si falta algo → DEVUELVE a Compras]
TESORERÍA → Programa pago → Ejecuta egreso
    ↓
CONCILIACIÓN → Cruza bancos vs. auxiliares (diario + mensual)
```

### 5.2 Flujo de Venta Directa (Iluminación)

```
COMERCIAL → Cotiza con proveedor + Cotiza al cliente (Excel)
    ↓
CLIENTE → Aprueba → OC del cliente llega
    ↓
COMERCIAL → Sube a Monday
    ↓
COMPRAS → Genera OC a proveedor (pero negociación la hizo Comercial)
    ↓
PROVEEDOR → Entrega
    ↓
INVENTARIOS → RP → Pedido de salida
    ↓
COMPRAS → Programa despacho al cliente
    ↓
COMERCIAL → Indica a Contabilidad que facture
    ↓
CONTABILIDAD → Factura de venta (copia exacta del pedido)
```

### 5.3 Flujo de Conciliación Bancaria

```
TESORERÍA → Descarga movimientos diarios (5 bancos: Excel + PDF)
    ↓
    → Descarga auxiliares de Word Office (1 por banco)
    ↓
    → Cruce diario: entradas (recibos de caja) + salidas (egresos)
    ↓
    → Problemas: fiducias sin detalle, nómina como totalazo, retenciones variables
    ↓
    → Conciliación mensual final (después del 5 del mes por extractos)
    ↓
GERENCIA FINANCIERA → Informe semanal (martes → datos del miércoles anterior)
    ↓
    → Cierre mensual: ~7-10 días hábiles de retraso
```

---

## 6. STACK TECNOLÓGICO ACTUAL

| Herramienta | Uso | Limitaciones identificadas |
|---|---|---|
| **Word Office** (ERP) | Contabilidad, OC, RP, facturación, inventarios, Kardex | No permite control presupuestal por obra; no integra con Monday; no genera alertas |
| **Monday.com** | Gestión de tareas, asignación de proyectos, seguimiento de OC | No conectado a Word Office; soportes se pierden; no hay automatizaciones |
| **Excel** | Presupuestos, APUs, Kardex respaldo, conciliaciones, listas de precios | Fragmentado; múltiples versiones; sin integración |
| **DIAN (plataforma)** | Eventos RADIAN (aceptación/rechazo) | Proceso uno a uno; sin carga masiva nativa |
| **BIM** | Revisión de planos 3D para presupuestos | Solo 1 persona dedicada; no integrado con flujo de cotización |
| **Correo electrónico** | Recepción de facturas, soportes, comunicación con proveedores | Fragmentado en múltiples cuentas |
| **WhatsApp** | Comunicación con proveedores sobre soportes | Sin trazabilidad formal |
| **Auranet** (en migración) | ERP nuevo — control presupuestal, integración OC↔RP↔Factura | En etapa de capacitaciones; migración pendiente |

---

## 7. CUANTIFICACIÓN DE DOLORES (Estimación de Impacto)

### Tiempo perdido estimado por mes:

| Proceso | Personas | Horas/mes estimadas | Costo oportunidad |
|---|---|---|---|
| Codificación manual APUs | 6 personas | ~480-720 hrs/mes (6 personas × 80-120 hrs) | El más costoso: bloquea presupuestos, retrasa cotizaciones, pierde diferenciación |
| Proceso RADIAN (antes de solución masiva) | 2 personas | ~320 hrs/mes | Ya mitigado parcialmente con proveedor externo |
| Conciliación bancaria diaria | 1 persona | ~160 hrs/mes | Retrasa cierre → retrasa informes → gerencia sin visibilidad |
| Seguimiento de soportes faltantes | Compras + Contabilidad | ~80-120 hrs/mes | Ciclos de ida y vuelta que retrasan toda la cadena |
| Cruce de pagos de fiducias | 1 persona (cartera) | ~40-80 hrs/mes | Variable según volumen de pagos por fiducia |
| **TOTAL ESTIMADO** | | **~1,000-1,400 hrs/mes** | |

### Impacto en indicadores de negocio:

- **Cierre contable:** 7-10 días de retraso → gerencia toma decisiones con datos desactualizados
- **Cotizaciones:** 3 días por presupuesto vs. potencialmente horas → pierde licitaciones por velocidad
- **Propuesta de valor:** Ya no revisan planos técnicamente → pierden diferenciación que les ganó clientes grandes
- **Control de costos:** Sin control presupuestal por obra → riesgo de sobrecostos no detectados
- **Flujo de caja:** Facturas estancadas por falta de soportes → proveedores sin pagar → relación deteriorada

---

## 8. CIP (CLIENT IDEAL PROFILE) Y CASO DE USO

### Perfil del caso:
- **Industria:** Construcción + distribución de material eléctrico/iluminación
- **Complejidad:** Alta — múltiples líneas de negocio con flujos distintos que convergen en misma cadena de compras y contabilidad
- **Madurez digital:** Baja-Media — usan Monday pero no explotan automatizaciones; Excel como backbone operativo
- **Disposición al cambio:** ALTA — gerencia explícitamente busca automatización, ya decidió migración de ERP, no quiere reducir personal sino liberar capacidad
- **Presupuesto señalado:** No explícito, pero Daniel Giraldo dijo "pásame la propuesta, hay mucho por trabajar acá"
- **Quick win path:** Conciliación bancaria (resultados en 1-2 meses según conversación con gerencia)

### Caso de uso prioritario (recomendación):

**FASE 1 — Quick Wins (1-2 meses):**
1. Automatización de conciliación bancaria (Davivienda + Bogotá) con motor de reglas contables
2. Automatización de descarga masiva y clasificación de XML (DIAN/RADIAN)
3. Sistema de alertas para soportes faltantes en cadena OC→RP→Factura

**FASE 2 — Core Value (2-4 meses):**
1. Motor de match de APUs por similitud semántica (base de datos de presupuestos + IA)
2. Automatización del flujo OC→RP→Facturación→Pago con validaciones y checks automáticos
3. Matriz de precios consolidada con actualización automática desde cotizaciones históricas

**FASE 3 — Transformación (4-6 meses):**
1. Integración con Auranet (nuevo ERP) una vez migrado
2. Dashboard de control presupuestal por obra en tiempo real
3. Revisión técnica automatizada de planos/especificaciones (recuperar propuesta de valor)

---

## 9. DOCUMENTOS SOLICITADOS / PENDIENTES

| Documento | Quién entrega | Estado | Para qué |
|---|---|---|---|
| Movimientos bancarios Davivienda (febrero) | Catalina Carranza | Solicitado | POC de conciliación automatizada |
| Extracto bancario Davivienda (febrero) | Catalina Carranza | Solicitado | POC de conciliación automatizada |
| Auxiliar Word Office Davivienda (febrero) | Catalina Carranza | Solicitado | POC de conciliación automatizada |
| Movimientos bancarios Bogotá (febrero) | Catalina Carranza | Solicitado | POC de conciliación automatizada |
| Extracto bancario Bogotá (febrero) | Catalina Carranza | Solicitado | POC de conciliación automatizada |
| Auxiliar Word Office Bogotá (febrero) | Catalina Carranza | Solicitado | POC de conciliación automatizada |
| Archivo de cliente (sábana de cantidades) | Oscar Pinzón | Solicitado | POC de automatización de APUs |
| Base de datos de APUs con códigos | Oscar Pinzón | Solicitado | POC de automatización de APUs |
| Histórico de costos y consolidado de compras | Marco (Jefe Compras) | Pendiente | Entender base de pricing |

**Destino de archivos:** hola@huevos.ai (correo compartido por Daniel Cardona en reunión)

---

## 10. ACTION ITEMS Y PRÓXIMOS PASOS

### Para KAI Partners:
1. ✅ Consolidar transcripciones y análisis (este documento)
2. 🔲 Recibir archivos de conciliación bancaria de Catalina
3. 🔲 Cruzar archivos de conciliación — entregar resultado entre mañana y pasado (compromiso de Daniel Cardona con Daniel Giraldo)
4. 🔲 Recibir archivos de presupuestos/APUs de Oscar
5. 🔲 Preparar propuesta comercial con fases de automatización
6. 🔲 Agendar sesión con Marco (Compras) para entender histórico de costos
7. 🔲 Evaluar integración con Auranet (ERP en migración)

### Para Lutec:
1. 🔲 Catalina: enviar 6 archivos de conciliación (3 Davivienda + 3 Bogotá) a hola@huevos.ai
2. 🔲 Oscar: enviar archivo de cliente + base de APUs con códigos
3. 🔲 Marco: compartir método y bases de datos de histórico de costos
4. 🔲 Continuar capacitaciones Auranet (paralelamente)
5. 🔲 Documentos / soportes: definir protocolo de rechazo de facturas sin soporte

---

## 11. CITAS TEXTUALES RELEVANTES

> **Daniel Giraldo (Gerencia):** "Eso es lo que necesito sin duda, porque yo no quiero reducir el equipo. Al revés, tengo que liberar el equipo porque necesitamos organizar unas cosas de otros consorcios que estamos firmando."

> **Catalina Carranza (Finanzas):** "Ese 80% del chicharrón [de pagos de fiducias] se podría resolver con reglas contables de ejercicios anteriores."

> **Oscar Pinzón (Presupuestos):** "Ahí es donde perdemos el tiempo" — refiriéndose a la codificación manual vs. dedicar tiempo a revisión técnica de planos.

> **Catalina Carranza:** "Me encanta que nos entiendes" — tras el mapeo de la cadena OC→RP→Factura→Pago y los problemas con anticipos.

> **Daniel Giraldo:** "Pásame la propuesta, hay mucho, mucho por trabajar. Usted tiene un cliente acá."

---

## 12. METADATA DE REUNIONES

| # | Título | Duración | Speakers | Fireflies ID |
|---|---|---|---|---|
| 1 | Lutec — proceso de conciliación bancaria | 40 min | Daniel Cardona, Catalina Carranza, Daniel Giraldo, José (Inventarios) | 01KJX4ZR7BRJ9792BJQG2Z03NC |
| 2 | Lutec pt 2 (Facturación y Compras) | 28 min | Daniel Cardona, Catalina Carranza, Wendy (Compras) | 01KJX7D1BBJYRXNR3MJ69RDGRQ |
| 3 | Lutec — Presupuesto | 13 min | Daniel Cardona, Oscar Pinzón | 01KJX954RB8J3220GXFNJY05KV |
| 4 | Presupuesto (APUs y productos) | ~1 min | Oscar Pinzón | 01KJX9YB98WQAT38DETRJSSP54 |
| 5 | Presupuesto (Monday y revisiones) | ~1.5 min | Oscar Pinzón, Daniel Cardona | 01KJXA10CKZ6VT7B5125JZ01XR |
| 6 | Gerencia (resumen operativo) | 5 min | Daniel Cardona, Daniel Giraldo | 01KJXA4P6WETWGQDMPJ2JPQARM |
| 7 | Gerencia (ERP y estrategia) | 3 min | Daniel Cardona, Daniel Giraldo | 01KJXAEB0380QS82RP6Z6G21EX |
| **TOTAL** | | **~92 minutos** | **6 stakeholders** | |

---

*Documento generado por KAI Partners — Análisis de Discovery*
*Fecha de generación: 4 de marzo de 2026*
*Consultor: Daniel Cardona*
*Cliente: Grupo Lutec S.A.S*
