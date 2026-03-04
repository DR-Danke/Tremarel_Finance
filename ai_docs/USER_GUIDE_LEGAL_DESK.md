# Manual de Usuario — Legal Desk

**Versión:** 1.0
**Plataforma:** Tremarel Finance — Módulo Legal Desk (POC)
**Fecha:** Marzo 2026

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Acceso y Navegación](#2-acceso-y-navegación)
3. [Dashboard](#3-dashboard)
4. [Gestión de Clientes](#4-gestión-de-clientes)
5. [Gestión de Especialistas](#5-gestión-de-especialistas)
6. [Gestión de Casos](#6-gestión-de-casos)
   - 6.1 [Crear un Caso](#61-crear-un-caso)
   - 6.2 [Lista y Filtros de Casos](#62-lista-y-filtros-de-casos)
   - 6.3 [Detalle del Caso](#63-detalle-del-caso)
   - 6.4 [Flujo de Estados del Caso](#64-flujo-de-estados-del-caso)
   - 6.5 [Asignación de Especialistas](#65-asignación-de-especialistas)
   - 6.6 [Entregables](#66-entregables)
   - 6.7 [Negociación de Precios](#67-negociación-de-precios)
   - 6.8 [Mensajes](#68-mensajes)
   - 6.9 [Documentos](#69-documentos)
7. [Analytics](#7-analytics)
8. [Referencia Rápida](#8-referencia-rápida)

---

## 1. Introducción

Legal Desk es un módulo de gestión de casos legales diseñado para **Faroo Legal**, una plataforma global que conecta clientes con abogados especializados. El sistema reemplaza la gestión manual (WhatsApp, email, Notion) con un flujo estructurado que incluye:

- **Registro de clientes** (empresas e individuos)
- **Directorio de especialistas legales** con áreas de expertise y jurisdicciones
- **Gestión completa del ciclo de vida de casos legales** (11 estados)
- **Motor de asignación inteligente** que sugiere los mejores especialistas para cada caso
- **Negociación de precios** con historial completo
- **Seguimiento de entregables**, mensajes y documentos por caso
- **Dashboard y Analytics** con métricas en tiempo real

---

## 2. Acceso y Navegación

### Requisitos de acceso

Legal Desk requiere autenticación. Inicie sesión con sus credenciales para acceder al módulo.

### Navegación por la barra lateral

En la barra lateral izquierda, busque la sección **POCs** y expándala. Dentro encontrará la subsección **Legal Desk** con las siguientes opciones:

| Opción | Descripción |
|---|---|
| **Dashboard** | Panel principal con KPIs y gráficos |
| **Cases** | Lista y gestión de casos legales |
| **Specialists** | Directorio de especialistas legales |
| **Clients** | Registro de clientes |
| **Analytics** | Análisis detallado de datos |

La barra lateral se puede colapsar para mostrar solo iconos, haciendo clic en el botón de menú. El estado de las secciones expandidas/colapsadas se mantiene entre sesiones.

---

## 3. Dashboard

**Ruta:** `Legal Desk → Dashboard`

El Dashboard ofrece una visión general rápida de la operación con cuatro tarjetas de KPI y dos gráficos.

### Tarjetas de resumen

| Indicador | Descripción |
|---|---|
| **Active Cases** | Cantidad de casos que no están cerrados ni archivados |
| **Total Cases** | Total histórico de casos creados |
| **Specialists Active** | Cantidad de especialistas activos en la plataforma |
| **Total Clients** | Total de clientes registrados |

### Gráficos

- **Cases by Status** — Gráfico circular (pie chart) que muestra la distribución de casos por estado. Cada sector tiene un color diferente según el estado.
- **Cases by Domain** — Gráfico de barras que muestra la cantidad de casos por dominio legal (Corporativo, Propiedad Intelectual, Laboral, Fiscal, etc.).

### Acciones disponibles

- **Botón Refresh**: Actualiza los datos del dashboard en tiempo real.

---

## 4. Gestión de Clientes

**Ruta:** `Legal Desk → Clients`

Esta sección permite registrar y consultar los clientes que solicitan servicios legales.

### Lista de clientes

Se muestra una tabla con las columnas:

| Columna | Descripción |
|---|---|
| **Name** | Nombre del cliente o empresa |
| **Type** | Tipo: Company (Empresa) o Individual (Persona) |
| **Email** | Correo electrónico de contacto |
| **Country** | País de origen |
| **Industry** | Industria o sector |

### Crear un nuevo cliente

1. Haga clic en el botón **"Add Client"**.
2. Se abre un cuadro de diálogo con el formulario de registro.
3. Complete los campos:

| Campo | Obligatorio | Descripción |
|---|---|---|
| **Name** | Sí | Nombre completo del cliente o razón social (máx. 255 caracteres) |
| **Client Type** | Sí | Seleccione: Company o Individual |
| **Contact Email** | No | Dirección de correo electrónico (se valida formato) |
| **Contact Phone** | No | Número de teléfono |
| **Country** | No | País |
| **Industry** | No | Industria o sector de actividad |

4. Haga clic en **"Create Client"** para guardar.
5. Al crearse exitosamente, aparece un mensaje de confirmación.

---

## 5. Gestión de Especialistas

**Ruta:** `Legal Desk → Specialists`

Esta sección gestiona el directorio de abogados y especialistas legales disponibles para asignación a casos.

### Vista de especialistas

Los especialistas se muestran como **tarjetas** (cards), cada una con:

- **Nombre completo** y correo electrónico
- **Años de experiencia**
- **Tarifa por hora** con moneda
- **Puntuación general** — Estrellas (1-5) más valor numérico
- **Indicador de carga de trabajo** — Barra de progreso que muestra `actual/máximo` de casos concurrentes
  - 🔴 Rojo: ≥80% de capacidad
  - 🟠 Naranja: ≥50% de capacidad
  - 🔵 Azul: <50% de capacidad

### Crear un nuevo especialista

1. Haga clic en **"Add Specialist"**.
2. Complete el formulario:

**Datos principales:**

| Campo | Obligatorio | Descripción |
|---|---|---|
| **Full Name** | Sí | Nombre completo (máx. 255 caracteres) |
| **Specialist Type** | No | Individual o Boutique Firm |
| **Email** | Sí | Correo electrónico (se valida formato) |
| **Phone** | No | Teléfono de contacto |
| **Country** | No | País de residencia |
| **Years of Experience** | No | Años de experiencia profesional |
| **Hourly Rate** | No | Tarifa por hora |

**Áreas de expertise** (sección dinámica — agregar/eliminar filas):

| Campo | Descripción |
|---|---|
| **Legal Domain** | Dominio legal (ver tabla de dominios abajo) |
| **Proficiency Level** | Nivel: Junior, Intermediate o Expert |

**Jurisdicciones** (sección dinámica — agregar/eliminar filas):

| Campo | Descripción |
|---|---|
| **Country** | País de la jurisdicción |
| **Region** | Región o estado |
| **Is Primary** | Marcar si es jurisdicción principal |

3. Haga clic en **"Create Specialist"** para guardar.

### Dominios legales disponibles

| Dominio | Descripción |
|---|---|
| Corporate | Derecho Corporativo |
| IP | Propiedad Intelectual |
| Labor | Derecho Laboral |
| Tax | Derecho Fiscal |
| Litigation | Litigios |
| Real Estate | Derecho Inmobiliario |
| Immigration | Inmigración |
| Regulatory | Regulatorio |
| Data Privacy | Privacidad de Datos |
| Commercial | Derecho Comercial |

---

## 6. Gestión de Casos

### 6.1 Crear un Caso

**Ruta:** `Legal Desk → Cases → New Case`

1. Desde la lista de casos, haga clic en **"New Case"**.
2. Complete el formulario:

| Campo | Obligatorio | Descripción |
|---|---|---|
| **Title** | Sí | Título descriptivo del caso (máx. 255 caracteres) |
| **Description** | No | Descripción detallada del caso |
| **Client** | Sí | Seleccione el cliente (búsqueda con autocompletado) |
| **Legal Domain** | Sí | Dominio legal del caso |
| **Case Type** | No | Advisory (Consultoría) o Litigation (Litigio) |
| **Complexity** | No | Low, Medium, High o Critical |
| **Priority** | No | Low, Medium, High o Urgent |
| **Client Budget** | No | Presupuesto estimado del cliente |
| **Deadline** | No | Fecha límite |
| **Jurisdiction** | No | Jurisdicción aplicable |

3. Haga clic en **"Create Case"**.
4. Al crearse, será redirigido automáticamente al detalle del caso.

### 6.2 Lista y Filtros de Casos

**Ruta:** `Legal Desk → Cases`

La lista muestra todos los casos en una tabla con columnas:

| Columna | Descripción |
|---|---|
| **Case #** | Número identificador del caso |
| **Title** | Título del caso |
| **Client** | Nombre del cliente |
| **Domain** | Dominio legal (badge con color) |
| **Status** | Estado actual (badge con color) |
| **Priority** | Prioridad (badge con color) |

#### Filtros disponibles

Utilice los selectores en la parte superior de la tabla para filtrar:

- **Status** — Filtrar por cualquiera de los 11 estados
- **Domain** — Filtrar por dominio legal
- **Priority** — Filtrar por prioridad (Low, Medium, High, Urgent)

Para ver el detalle de un caso, haga clic en la fila correspondiente.

### 6.3 Detalle del Caso

**Ruta:** `Legal Desk → Cases → [caso seleccionado]`

La vista de detalle es la pantalla más completa del módulo. Incluye:

**Encabezado:** Muestra el número de caso, título, y badges de estado, dominio y prioridad. Debajo se muestran botones para las **transiciones de estado válidas** desde el estado actual.

**6 pestañas:**

| Pestaña | Contenido |
|---|---|
| **Overview** | Información general, financiera y del cliente |
| **Specialists** | Especialistas asignados y sugerencias |
| **Deliverables** | Lista de entregables y su progreso |
| **Pricing** | Historial y negociación de precios |
| **Messages** | Hilo de comunicación del caso |
| **Documents** | Documentos adjuntos al caso |

#### Pestaña Overview

Muestra la información completa del caso organizada en secciones:

- **Información general:** Descripción, tipo de caso, complejidad
- **Información financiera:** Presupuesto del cliente, costo estimado, cotización final, porcentaje de margen
- **Fecha límite**
- **Información del cliente:** Nombre, tipo, email de contacto
- **Clasificación AI:** Resultado de la clasificación automática (formato JSON)

### 6.4 Flujo de Estados del Caso

Cada caso pasa por un flujo de estados definido. Solo se permiten las transiciones válidas según el estado actual:

```
New (Nuevo)
  ↓
Classifying (Clasificando)
  ↓
Open (Abierto)
  ↓
Assigning (Asignando)
  ↓
Active (Activo)
  ↓
In Progress (En Progreso)
  ↓
Review (En Revisión)
  ↓  ↘
Negotiating    Completed
(Negociando)   (Completado)
  ↓               ↓
Completed      Closed
(Completado)   (Cerrado)
  ↓               ↓
Closed         Archived
(Cerrado)      (Archivado)
  ↓
Archived
(Archivado)
```

**Descripción de cada estado:**

| Estado | Descripción |
|---|---|
| **New** | Caso recién creado, pendiente de clasificación |
| **Classifying** | El sistema está clasificando el caso (puede incluir clasificación por IA) |
| **Open** | Caso clasificado y listo para asignar especialistas |
| **Assigning** | En proceso de búsqueda y asignación de especialistas |
| **Active** | Especialistas asignados, caso activo |
| **In Progress** | Trabajo en curso por parte de los especialistas |
| **Review** | Entregables en revisión |
| **Negotiating** | En fase de negociación de precios o términos |
| **Completed** | Caso completado exitosamente |
| **Closed** | Caso cerrado formalmente |
| **Archived** | Caso archivado para referencia histórica |

Para avanzar el estado, haga clic en los botones de transición que aparecen debajo del título del caso en la vista de detalle.

### 6.5 Asignación de Especialistas

**Pestaña:** `Detalle del Caso → Specialists`

Esta sección gestiona qué especialistas trabajan en el caso.

#### Especialistas asignados

Se muestra una tabla con:

| Columna | Descripción |
|---|---|
| **Specialist ID** | Identificador del especialista |
| **Role** | Rol asignado: Lead, Support, Reviewer o Consultant |
| **Status** | Estado: Proposed, Accepted, Rejected, Active o Completed |
| **Proposed Fee** | Tarifa propuesta |
| **Agreed Fee** | Tarifa acordada |

#### Motor de sugerencia inteligente

1. Haga clic en **"Suggest Specialists"**.
2. El sistema evalúa a todos los especialistas disponibles usando 5 factores ponderados:

| Factor | Peso | Descripción |
|---|---|---|
| Nivel de competencia | 30 pts | Coincidencia del dominio legal y nivel de expertise |
| Puntuación general | 25 pts | Historial de calificaciones del especialista |
| Disponibilidad | 20 pts | Capacidad actual vs. máxima de casos concurrentes |
| Jurisdicción | 15 pts | Coincidencia con la jurisdicción del caso |
| Experiencia | 10 pts | Años de experiencia profesional |

3. Se muestran los **5 mejores candidatos** en una tabla con:
   - Nombre
   - Puntuación general
   - Puntuación de disponibilidad
   - Coincidencia de expertise
   - Botón **"Assign"** para asignar al caso

### 6.6 Entregables

**Pestaña:** `Detalle del Caso → Deliverables`

Los entregables son las tareas o hitos que deben completarse dentro del caso.

#### Lista de entregables

Cada entregable muestra:
- Título y descripción
- Estado actual (con selector desplegable para cambiar estado)
- Especialista asignado
- Fecha de vencimiento

#### Estados de entregables

| Estado | Descripción |
|---|---|
| **Pending** | Pendiente de inicio |
| **In Progress** | En progreso |
| **Review** | En revisión |
| **Completed** | Completado |
| **Cancelled** | Cancelado |

#### Agregar un entregable

1. En la parte inferior de la pestaña, complete el formulario inline:
   - **Title** (obligatorio): Título del entregable
   - **Description**: Descripción detallada
   - **Due Date**: Fecha de vencimiento
2. Haga clic en **"Add"**.

### 6.7 Negociación de Precios

**Pestaña:** `Detalle del Caso → Pricing`

Esta sección gestiona el proceso de negociación de precios entre Faroo Legal y el cliente/especialista.

#### Línea de tiempo de precios

Se muestra un historial vertical cronológico (stepper) con cada acción de precios:
- Tipo de acción (Propuesta, Contraoferta, Aceptación, Rechazo)
- Fecha y hora
- Monto anterior → monto nuevo
- Persona que realizó el cambio
- Notas adicionales

#### Acciones de precios

En la parte inferior se encuentran los controles para negociar:

1. **Campos de entrada:**
   - **Amount**: Monto de la propuesta o contraoferta
   - **Notes**: Notas o justificación

2. **Botones de acción:**
   - **Propose** — Crear una propuesta inicial de precio
   - **Counter** — Enviar una contraoferta
   - **Accept** (verde) — Aceptar el precio actual
   - **Reject** (rojo) — Rechazar la propuesta actual

**Fórmula de margen:** El sistema calcula automáticamente el porcentaje de margen:

```
Margen % = ((Precio cliente - Costo especialista) / Precio cliente) × 100
```

### 6.8 Mensajes

**Pestaña:** `Detalle del Caso → Messages`

Un hilo de comunicación asociado al caso para coordinar entre las partes.

#### Visualización de mensajes

- Los mensajes se muestran en orden cronológico en un panel scrollable.
- Los **mensajes internos** (visibles solo para el equipo de Faroo) se identifican con un chip naranja "Internal".
- Use el checkbox **"Show Internal"** para mostrar u ocultar los mensajes internos.

#### Enviar un mensaje

1. Complete el formulario:
   - **Sender Type**: User, Specialist o System
   - **Sender Name**: Nombre del remitente
   - **Message**: Texto del mensaje
   - **Internal**: Marque si el mensaje es solo para uso interno
2. Haga clic en **"Send"**.

### 6.9 Documentos

**Pestaña:** `Detalle del Caso → Documents`

Permite asociar documentos al caso (actualmente registra metadatos, sin carga de archivos).

#### Lista de documentos

| Columna | Descripción |
|---|---|
| **File Name** | Nombre del archivo |
| **Type** | Tipo de archivo |
| **Size (KB)** | Tamaño en kilobytes |
| **Uploaded By** | Persona que subió el documento |
| **Date** | Fecha de carga |

#### Agregar un documento

1. Complete el formulario:
   - **File Name** (obligatorio): Nombre del archivo
   - **File URL** (obligatorio): URL del documento
   - **File Type**: Tipo de archivo (PDF, DOCX, etc.)
   - **Uploaded By**: Nombre de quien registra el documento
2. Haga clic en **"Add"**.

---

## 7. Analytics

**Ruta:** `Legal Desk → Analytics`

Ofrece un análisis más detallado de los datos operativos.

### Tarjetas de resumen

| Indicador | Descripción |
|---|---|
| **Total Cases** | Número total de casos |
| **Active Cases** | Casos actualmente activos |
| **Total Specialists** | Total de especialistas registrados |

### Gráfico: Casos por Dominio

Gráfico de barras de ancho completo que muestra la distribución de casos por dominio legal. Cada barra tiene un color único asociado al dominio.

### Utilización de Especialistas

Panel informativo (disponible próximamente — requiere datos de asignación de casos para calcular métricas de utilización).

---

## 8. Referencia Rápida

### Atajos de navegación

| Acción | Ruta |
|---|---|
| Ir al Dashboard | `Legal Desk → Dashboard` |
| Ver todos los casos | `Legal Desk → Cases` |
| Crear un caso nuevo | `Legal Desk → Cases → New Case` |
| Ver especialistas | `Legal Desk → Specialists` |
| Ver clientes | `Legal Desk → Clients` |
| Ver analytics | `Legal Desk → Analytics` |

### Roles de especialistas en un caso

| Rol | Descripción |
|---|---|
| **Lead** | Abogado principal responsable del caso |
| **Support** | Abogado de apoyo |
| **Reviewer** | Revisor de entregables y documentación |
| **Consultant** | Consultor especializado en un tema puntual |

### Prioridades de caso

| Prioridad | Uso recomendado |
|---|---|
| **Low** | Casos sin urgencia, plazos flexibles |
| **Medium** | Casos con plazos definidos pero sin presión inmediata |
| **High** | Casos con plazos próximos o impacto significativo |
| **Urgent** | Casos que requieren atención inmediata |

### Niveles de complejidad

| Nivel | Descripción |
|---|---|
| **Low** | Caso sencillo, procedimientos estándar |
| **Medium** | Complejidad moderada, requiere especialización |
| **High** | Alta complejidad, múltiples jurisdicciones o partes |
| **Critical** | Máxima complejidad, impacto estratégico o riesgo elevado |

---

*Manual generado para Tremarel Finance — Módulo Legal Desk (POC) v1.0*
