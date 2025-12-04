# Plan de Desarrollo - Sistema de Gestión de Fortalecimiento de Proveedores

## 1. Resumen Ejecutivo

### 1.1 Descripción del Proyecto
Sistema web para gestionar proyectos de fortalecimiento de proveedores de múltiples empresas ancla, siguiendo la metodología PHVA (Planear, Hacer, Verificar, Actuar) en 4 etapas operativas, con gestión de talleres especializados y plataforma post-ruta.

### 1.2 Objetivos del Sistema
- Gestionar múltiples proyectos de fortalecimiento en paralelo
- Controlar el flujo secuencial de las 4 etapas por proveedor
- Mantener trazabilidad histórica de intervenciones por proveedor
- Facilitar la gestión de talleres y certificaciones
- Proveer dashboards y reportes ejecutivos
- Integrar comunidad y notificaciones

---

## 2. Arquitectura del Sistema

### 2.1 Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| **Backend** | Django 4.2.x + Python 3.11 |
| **Base de Datos** | PostgreSQL 15+ |
| **Frontend** | Bootstrap 5 + Vanilla JS + Chart.js |
| **Formularios** | Django Crispy Forms + Bootstrap 5 |
| **API REST** | Django REST Framework |
| **Tareas Asíncronas** | Celery + Redis |
| **Notificaciones Email** | Google Workspace API (Gmail) |
| **Notificaciones WhatsApp** | API de WhatsApp Business (Twilio/Meta) |
| **Generación PDF** | WeasyPrint / ReportLab |
| **Almacenamiento** | Google Cloud Storage |
| **Despliegue** | Google Cloud Run / Compute Engine |
| **Cache** | Redis |

### 2.2 Arquitectura Multi-Tenant
```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA PRINCIPAL                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Empresa     │  │ Empresa     │  │ Empresa     │         │
│  │ Ancla 1     │  │ Ancla 2     │  │ Ancla N     │         │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤         │
│  │ Proyecto A  │  │ Proyecto C  │  │ Proyecto E  │         │
│  │ Proyecto B  │  │ Proyecto D  │  │ Proyecto F  │         │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤         │
│  │ Proveedores │  │ Proveedores │  │ Proveedores │         │
│  │ (pueden     │  │ (pueden     │  │ (pueden     │         │
│  │ compartirse)│  │ compartirse)│  │ compartirse)│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Diagrama de Componentes
```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│  │ Dashboard  │ │ Proyectos  │ │  Talleres  │ │  Reportes  │    │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                      DJANGO BACKEND                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Core    │ │ Empresas │ │Proyectos │ │ Talleres │            │
│  │  Auth    │ │  Ancla   │ │  Etapas  │ │          │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │Proveedores│ │ Reportes │ │Notificac.│ │   API    │            │
│  │          │ │   PDF    │ │  Email   │ │   REST   │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
└──────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │PostgreSQL│   │  Redis   │   │  Celery  │
        │    DB    │   │  Cache   │   │  Worker  │
        └──────────┘   └──────────┘   └──────────┘
```

---

## 3. Modelo de Datos

### 3.1 Diagrama Entidad-Relación Principal

```
┌─────────────────┐       ┌─────────────────┐
│     Usuario     │       │  EmpresaAncla   │
├─────────────────┤       ├─────────────────┤
│ id (UUID)       │       │ id (UUID)       │
│ email           │       │ nombre          │
│ password        │       │ nit             │
│ rol             │       │ sector          │
│ telefono        │       │ logo            │
│ is_active       │       │ configuracion   │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │    ┌────────────────────┘
         │    │
         ▼    ▼
┌─────────────────────────┐
│  UsuarioEmpresaAncla    │
├─────────────────────────┤
│ usuario_id              │
│ empresa_ancla_id        │
│ rol_empresa             │
└─────────────────────────┘

┌─────────────────┐       ┌─────────────────┐
│   Proveedor     │       │    Proyecto     │
├─────────────────┤       ├─────────────────┤
│ id (UUID)       │       │ id (UUID)       │
│ razon_social    │       │ nombre          │
│ nit             │       │ empresa_ancla_id│
│ representante   │       │ fecha_inicio    │
│ email           │       │ fecha_fin       │
│ telefono        │       │ estado          │
│ sector          │       │ descripcion     │
│ tamano_empresa  │       │ consultor_id    │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │    ┌────────────────────┘
         │    │
         ▼    ▼
┌─────────────────────────┐
│  ProveedorProyecto      │
├─────────────────────────┤
│ id (UUID)               │
│ proveedor_id            │
│ proyecto_id             │
│ etapa_actual            │
│ estado                  │
│ fecha_inicio            │
│ fecha_fin               │
│ consultor_asignado_id   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                      ETAPAS                                  │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Etapa1     │   Etapa2     │   Etapa3     │    Etapa4      │
│  Diagnóstico │    Plan      │Implementación│   Monitoreo    │
├──────────────┼──────────────┼──────────────┼────────────────┤
│voz_cliente   │hallazgos[]   │tareas[]      │kpis[]          │
│diagnostico   │priorizacion  │avance        │evaluaciones[]  │
│objetivos     │cronograma    │documentos[]  │informe_final   │
│documentos[]  │aprobacion    │evidencias[]  │cierre          │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

### 3.2 Modelos Detallados por App

#### App: `core` (Autenticación y Base)
```python
# Usuarios y Roles
Usuario
- id: UUID (PK)
- email: EmailField (unique)
- password: CharField
- nombre: CharField
- apellido: CharField
- telefono: CharField
- rol: CharField [ADMIN, EMPRESA_ANCLA, PROVEEDOR, CONSULTOR]
- avatar: ImageField
- is_active: BooleanField
- created_at: DateTimeField
- updated_at: DateTimeField
```

#### App: `empresas`
```python
EmpresaAncla
- id: UUID (PK)
- nombre: CharField
- nit: CharField (unique)
- direccion: TextField
- ciudad: CharField
- sector_economico: CharField
- telefono: CharField
- email: EmailField
- logo: ImageField
- sitio_web: URLField
- descripcion: TextField
- configuracion: JSONField  # Configuraciones específicas
- is_active: BooleanField
- created_at: DateTimeField

UsuarioEmpresaAncla
- id: UUID (PK)
- usuario: FK(Usuario)
- empresa_ancla: FK(EmpresaAncla)
- rol: CharField [ADMIN_EMPRESA, GESTOR, VISUALIZADOR]
- is_active: BooleanField
```

#### App: `proveedores`
```python
Proveedor
- id: UUID (PK)
- razon_social: CharField
- nit: CharField (unique)
- nombre_comercial: CharField
- representante_legal: CharField
- email: EmailField
- telefono: CharField
- direccion: TextField
- ciudad: CharField
- departamento: CharField
- sector_economico: CharField
- tamano_empresa: CharField [MICRO, PEQUENA, MEDIANA, GRANDE]
- numero_empleados: IntegerField
- anio_constitucion: IntegerField
- sitio_web: URLField
- logo: ImageField
- descripcion: TextField
- usuario: FK(Usuario, null=True)  # Usuario de acceso del proveedor
- created_at: DateTimeField
- updated_at: DateTimeField

ProveedorEmpresaAncla
- id: UUID (PK)
- proveedor: FK(Proveedor)
- empresa_ancla: FK(EmpresaAncla)
- fecha_vinculacion: DateField
- estado: CharField [ACTIVO, INACTIVO, SUSPENDIDO]
- categoria: CharField  # Categoría dentro de la empresa ancla
- notas: TextField
```

#### App: `proyectos`
```python
Proyecto
- id: UUID (PK)
- codigo: CharField (unique, auto-generated)
- nombre: CharField
- empresa_ancla: FK(EmpresaAncla)
- descripcion: TextField
- fecha_inicio: DateField
- fecha_fin_planeada: DateField
- fecha_fin_real: DateField (null)
- estado: CharField [PLANEACION, EN_CURSO, FINALIZADO, CANCELADO]
- director_proyecto: FK(Usuario)
- presupuesto: DecimalField
- created_at: DateTimeField
- updated_at: DateTimeField

ProveedorProyecto
- id: UUID (PK)
- proveedor: FK(Proveedor)
- proyecto: FK(Proyecto)
- consultor_asignado: FK(Usuario)
- etapa_actual: IntegerField [1, 2, 3, 4]
- estado: CharField [PENDIENTE, EN_PROCESO, COMPLETADO, SUSPENDIDO]
- fecha_inicio: DateField
- fecha_fin_planeada: DateField
- fecha_fin_real: DateField (null)
- horas_consumidas: DecimalField
- notas: TextField
- created_at: DateTimeField
- updated_at: DateTimeField
```

#### App: `etapas`
```python
# ETAPA 1: Diagnóstico de Competitividad
Etapa1Diagnostico
- id: UUID (PK)
- proveedor_proyecto: FK(ProveedorProyecto, unique)
- estado: CharField [PENDIENTE, EN_PROCESO, COMPLETADO]
- fecha_inicio: DateTimeField
- fecha_fin: DateTimeField (null)
- completado_por: FK(Usuario, null)

VozCliente
- id: UUID (PK)
- etapa1: FK(Etapa1Diagnostico)
- empresa_ancla_contacto: CharField
- cargo_contacto: CharField
- necesidades_identificadas: TextField
- expectativas: TextField
- requerimientos_especificos: TextField
- fecha_entrevista: DateField
- archivo_evidencia: FileField (null)

DiagnosticoCompetitividad
- id: UUID (PK)
- etapa1: FK(Etapa1Diagnostico)
- area_evaluada: CharField
- nivel_madurez: IntegerField [1-5]
- fortalezas: TextField
- debilidades: TextField
- oportunidades: TextField
- amenazas: TextField
- observaciones: TextField
- puntaje: DecimalField

ObjetivoFortalecimiento
- id: UUID (PK)
- etapa1: FK(Etapa1Diagnostico)
- objetivo: TextField
- meta_cuantificable: CharField
- indicador: CharField
- valor_inicial: DecimalField
- valor_meta: DecimalField
- es_smart: BooleanField

DocumentoEtapa1
- id: UUID (PK)
- etapa1: FK(Etapa1Diagnostico)
- tipo: CharField [VOZ_CLIENTE, DIAGNOSTICO, GRABACION, OTRO]
- nombre: CharField
- archivo: FileField
- descripcion: TextField
- uploaded_at: DateTimeField
- uploaded_by: FK(Usuario)

# ETAPA 2: Plan de Implementación
Etapa2Plan
- id: UUID (PK)
- proveedor_proyecto: FK(ProveedorProyecto, unique)
- estado: CharField [PENDIENTE, EN_PROCESO, APROBADO, RECHAZADO]
- fecha_inicio: DateTimeField
- fecha_fin: DateTimeField (null)
- aprobado_por: FK(Usuario, null)
- fecha_aprobacion: DateTimeField (null)
- observaciones_aprobacion: TextField

HallazgoProblema
- id: UUID (PK)
- etapa2: FK(Etapa2Plan)
- hallazgo: TextField
- problema_identificado: TextField
- causa_raiz: TextField
- area_impactada: CharField
- prioridad: CharField [ALTA, MEDIA, BAJA]
- orden: IntegerField

AccionMejora
- id: UUID (PK)
- hallazgo: FK(HallazgoProblema)
- descripcion: TextField
- tipo_accion: CharField [CORRECTIVA, PREVENTIVA, MEJORA]
- recursos_necesarios: TextField
- responsable_sugerido: CharField
- impacto_esperado: IntegerField [1-5]
- esfuerzo_requerido: IntegerField [1-5]
- puntuacion_priorizacion: DecimalField  # Calculado
- seleccionada: BooleanField

CronogramaImplementacion
- id: UUID (PK)
- etapa2: FK(Etapa2Plan)
- accion_mejora: FK(AccionMejora)
- fecha_inicio_planeada: DateField
- fecha_fin_planeada: DateField
- responsable: CharField
- recursos: TextField
- entregable: CharField
- orden: IntegerField

# ETAPA 3: Implementación
Etapa3Implementacion
- id: UUID (PK)
- proveedor_proyecto: FK(ProveedorProyecto, unique)
- estado: CharField [PENDIENTE, EN_PROCESO, COMPLETADO]
- fecha_inicio: DateTimeField
- fecha_fin: DateTimeField (null)
- porcentaje_avance: DecimalField
- horas_acompanamiento: DecimalField

TareaImplementacion
- id: UUID (PK)
- etapa3: FK(Etapa3Implementacion)
- cronograma_item: FK(CronogramaImplementacion, null)
- titulo: CharField
- descripcion: TextField
- estado: CharField [PENDIENTE, EN_PROGRESO, COMPLETADA, BLOQUEADA]
- fecha_inicio_planeada: DateField
- fecha_fin_planeada: DateField
- fecha_inicio_real: DateField (null)
- fecha_fin_real: DateField (null)
- responsable: FK(Usuario)
- prioridad: CharField [ALTA, MEDIA, BAJA]
- porcentaje_avance: IntegerField [0-100]
- orden: IntegerField
- notas: TextField

EvidenciaImplementacion
- id: UUID (PK)
- tarea: FK(TareaImplementacion)
- tipo: CharField [DOCUMENTO, IMAGEN, VIDEO, OTRO]
- nombre: CharField
- archivo: FileField
- descripcion: TextField
- uploaded_at: DateTimeField
- uploaded_by: FK(Usuario)

SesionAcompanamiento
- id: UUID (PK)
- etapa3: FK(Etapa3Implementacion)
- fecha: DateTimeField
- duracion_horas: DecimalField
- modalidad: CharField [PRESENCIAL, VIRTUAL]
- temas_tratados: TextField
- compromisos: TextField
- participantes: TextField
- consultor: FK(Usuario)
- archivo_acta: FileField (null)

# ETAPA 4: Monitoreo y Evaluación
Etapa4Monitoreo
- id: UUID (PK)
- proveedor_proyecto: FK(ProveedorProyecto, unique)
- estado: CharField [PENDIENTE, EN_PROCESO, COMPLETADO]
- fecha_inicio: DateTimeField
- fecha_fin: DateTimeField (null)
- informe_final_generado: BooleanField

IndicadorKPI
- id: UUID (PK)
- etapa4: FK(Etapa4Monitoreo)
- objetivo: FK(ObjetivoFortalecimiento)
- nombre: CharField
- descripcion: TextField
- valor_inicial: DecimalField
- valor_actual: DecimalField
- valor_meta: DecimalField
- unidad_medida: CharField
- frecuencia_medicion: CharField [SEMANAL, QUINCENAL, MENSUAL]
- tendencia: CharField [MEJORANDO, ESTABLE, EMPEORANDO]

MedicionKPI
- id: UUID (PK)
- indicador: FK(IndicadorKPI)
- fecha_medicion: DateField
- valor: DecimalField
- observaciones: TextField
- registrado_por: FK(Usuario)

ReporteSemanal
- id: UUID (PK)
- etapa4: FK(Etapa4Monitoreo)
- semana_numero: IntegerField
- fecha_inicio_semana: DateField
- fecha_fin_semana: DateField
- resumen_avance: TextField
- logros: TextField
- dificultades: TextField
- proximas_acciones: TextField
- enviado: BooleanField
- fecha_envio: DateTimeField (null)

EvaluacionDirectiva
- id: UUID (PK)
- etapa4: FK(Etapa4Monitoreo)
- fecha: DateField
- participantes: TextField
- objetivos_cumplidos: TextField
- objetivos_pendientes: TextField
- ajustes_requeridos: TextField
- decisiones_tomadas: TextField
- archivo_acta: FileField (null)
- aprobado: BooleanField

InformeCierre
- id: UUID (PK)
- etapa4: FK(Etapa4Monitoreo, unique)
- fecha_generacion: DateTimeField
- resumen_ejecutivo: TextField
- objetivos_logrados: TextField
- mejoras_implementadas: TextField
- resultados_kpis: JSONField
- lecciones_aprendidas: TextField
- recomendaciones: TextField
- archivo_pdf: FileField (null)
- firmado_por: FK(Usuario, null)
- fecha_firma: DateTimeField (null)
```

#### App: `talleres`
```python
Taller
- id: UUID (PK)
- nombre: CharField
- tipo: CharField [GESTION_RIESGOS, TRANSFORMACION_DIGITAL, MEJORA_CONTINUA, SOSTENIBILIDAD, OTRO]
- descripcion: TextField
- contenido_programatico: TextField
- duracion_horas: DecimalField
- modalidad: CharField [PRESENCIAL, VIRTUAL, HIBRIDO]
- capacidad_maxima: IntegerField
- facilitador: FK(Usuario)
- material_didactico: FileField (null)
- proyecto: FK(Proyecto, null)  # Puede ser general o de un proyecto específico
- is_active: BooleanField
- created_at: DateTimeField

SesionTaller
- id: UUID (PK)
- taller: FK(Taller)
- fecha: DateTimeField
- hora_inicio: TimeField
- hora_fin: TimeField
- lugar: CharField  # Dirección o link de reunión virtual
- estado: CharField [PROGRAMADA, EN_CURSO, FINALIZADA, CANCELADA]
- notas: TextField
- grabacion_url: URLField (null)

InscripcionTaller
- id: UUID (PK)
- sesion: FK(SesionTaller)
- proveedor: FK(Proveedor)
- participante_nombre: CharField
- participante_email: EmailField
- participante_cargo: CharField
- estado: CharField [INSCRITO, CONFIRMADO, ASISTIO, NO_ASISTIO, CANCELADO]
- fecha_inscripcion: DateTimeField
- confirmacion_enviada: BooleanField

AsistenciaTaller
- id: UUID (PK)
- inscripcion: FK(InscripcionTaller)
- hora_entrada: TimeField
- hora_salida: TimeField (null)
- asistio: BooleanField
- observaciones: TextField

CertificadoTaller
- id: UUID (PK)
- inscripcion: FK(InscripcionTaller)
- codigo_certificado: CharField (unique)
- fecha_emision: DateTimeField
- archivo_pdf: FileField
- enviado: BooleanField
- fecha_envio: DateTimeField (null)

EvaluacionTaller
- id: UUID (PK)
- inscripcion: FK(InscripcionTaller)
- calificacion_general: IntegerField [1-5]
- calificacion_facilitador: IntegerField [1-5]
- calificacion_contenido: IntegerField [1-5]
- calificacion_logistica: IntegerField [1-5]
- comentarios: TextField
- sugerencias: TextField
- fecha_evaluacion: DateTimeField
```

#### App: `postruta`
```python
SuscripcionPostRuta
- id: UUID (PK)
- proveedor: FK(Proveedor)
- proyecto: FK(Proyecto)
- fecha_inicio: DateField
- fecha_fin: DateField
- estado: CharField [ACTIVA, VENCIDA, CANCELADA]
- valor_mensual: DecimalField
- created_at: DateTimeField

DatoKPIPostRuta
- id: UUID (PK)
- suscripcion: FK(SuscripcionPostRuta)
- indicador_nombre: CharField
- valor: DecimalField
- fecha_registro: DateField
- registrado_por: FK(Usuario)
- notas: TextField

MentoriaPostRuta
- id: UUID (PK)
- suscripcion: FK(SuscripcionPostRuta)
- mentor: FK(Usuario)
- fecha: DateTimeField
- duracion_minutos: IntegerField
- temas: TextField
- compromisos: TextField
- estado: CharField [PROGRAMADA, REALIZADA, CANCELADA]
- notas: TextField

EventoNetworking
- id: UUID (PK)
- nombre: CharField
- descripcion: TextField
- fecha: DateTimeField
- lugar: CharField
- tipo: CharField [CONFERENCIA, MESA_TRABAJO, RUEDA_NEGOCIOS]
- capacidad: IntegerField
- is_active: BooleanField

InscripcionEvento
- id: UUID (PK)
- evento: FK(EventoNetworking)
- proveedor: FK(Proveedor)
- participante_nombre: CharField
- participante_email: EmailField
- estado: CharField [INSCRITO, CONFIRMADO, ASISTIO]
```

#### App: `comunidad`
```python
CategoriaForo
- id: UUID (PK)
- nombre: CharField
- descripcion: TextField
- orden: IntegerField
- is_active: BooleanField

TemaForo
- id: UUID (PK)
- categoria: FK(CategoriaForo)
- titulo: CharField
- contenido: TextField
- autor: FK(Usuario)
- es_fijado: BooleanField
- es_cerrado: BooleanField
- vistas: IntegerField
- created_at: DateTimeField
- updated_at: DateTimeField

RespuestaForo
- id: UUID (PK)
- tema: FK(TemaForo)
- contenido: TextField
- autor: FK(Usuario)
- es_solucion: BooleanField
- likes: IntegerField
- created_at: DateTimeField
- updated_at: DateTimeField

RecursoCompartido
- id: UUID (PK)
- titulo: CharField
- descripcion: TextField
- tipo: CharField [DOCUMENTO, PLANTILLA, VIDEO, ENLACE]
- archivo: FileField (null)
- url: URLField (null)
- categoria: CharField
- autor: FK(Usuario)
- descargas: IntegerField
- is_public: BooleanField
- created_at: DateTimeField
```

#### App: `notificaciones`
```python
PlantillaNotificacion
- id: UUID (PK)
- codigo: CharField (unique)
- nombre: CharField
- asunto: CharField
- cuerpo_html: TextField
- cuerpo_texto: TextField
- variables: JSONField  # Lista de variables disponibles
- is_active: BooleanField

Notificacion
- id: UUID (PK)
- usuario: FK(Usuario)
- tipo: CharField [EMAIL, WHATSAPP, SISTEMA]
- plantilla: FK(PlantillaNotificacion, null)
- asunto: CharField
- mensaje: TextField
- datos: JSONField
- leida: BooleanField
- enviada: BooleanField
- fecha_envio: DateTimeField (null)
- error_envio: TextField (null)
- created_at: DateTimeField

ConfiguracionNotificacion
- id: UUID (PK)
- usuario: FK(Usuario)
- tipo_evento: CharField
- email_activo: BooleanField
- whatsapp_activo: BooleanField
- sistema_activo: BooleanField
```

#### App: `reportes`
```python
ReporteGenerado
- id: UUID (PK)
- tipo: CharField [AVANCE_PROVEEDOR, CONSOLIDADO_PROYECTO, EJECUTIVO, COMPARATIVO]
- nombre: CharField
- parametros: JSONField
- generado_por: FK(Usuario)
- archivo: FileField
- fecha_generacion: DateTimeField

ConfiguracionReporte
- id: UUID (PK)
- empresa_ancla: FK(EmpresaAncla)
- tipo_reporte: CharField
- frecuencia: CharField [DIARIO, SEMANAL, MENSUAL]
- destinatarios: JSONField
- is_active: BooleanField
```

#### App: `importacion`
```python
ImportacionMasiva
- id: UUID (PK)
- tipo: CharField [PROVEEDORES, DIAGNOSTICOS, KPIS]
- archivo_original: FileField
- archivo_procesado: FileField (null)
- estado: CharField [PENDIENTE, PROCESANDO, COMPLETADO, ERROR]
- registros_totales: IntegerField
- registros_exitosos: IntegerField
- registros_fallidos: IntegerField
- errores: JSONField
- importado_por: FK(Usuario)
- created_at: DateTimeField
- completed_at: DateTimeField (null)
```

---

## 4. Módulos y Funcionalidades

### 4.1 Módulo de Autenticación y Usuarios
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Login/Logout | Autenticación con email y contraseña | Alta |
| Registro de usuarios | Por invitación desde admin | Alta |
| Recuperación de contraseña | Envío de email con token | Alta |
| Gestión de perfil | Editar datos personales y avatar | Media |
| Roles y permisos | ADMIN, EMPRESA_ANCLA, PROVEEDOR, CONSULTOR | Alta |
| Sesiones activas | Ver y cerrar sesiones | Baja |

### 4.2 Módulo de Empresas Ancla
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| CRUD Empresas Ancla | Crear, editar, listar, desactivar | Alta |
| Configuración de empresa | Logo, datos, preferencias | Alta |
| Gestión de usuarios | Asignar usuarios a empresa | Alta |
| Dashboard empresa | Métricas y resumen de la empresa | Alta |
| Histórico de proyectos | Ver todos los proyectos de la empresa | Media |

### 4.3 Módulo de Proveedores
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| CRUD Proveedores | Crear, editar, listar, desactivar | Alta |
| Vinculación a empresas ancla | Asociar proveedor a múltiples empresas | Alta |
| Perfil del proveedor | Información completa y documentos | Alta |
| Historial de intervenciones | Todos los proyectos en los que participó | Alta |
| Portal del proveedor | Vista específica para proveedores | Alta |
| Importación masiva Excel | Cargar múltiples proveedores | Media |

### 4.4 Módulo de Proyectos
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| CRUD Proyectos | Crear, editar, listar proyectos | Alta |
| Asignación de proveedores | Agregar proveedores al proyecto | Alta |
| Asignación de consultores | Asignar consultor por proveedor | Alta |
| Timeline del proyecto | Vista general de avance | Alta |
| Dashboard del proyecto | KPIs y métricas del proyecto | Alta |
| Gestión de estados | Control de flujo del proyecto | Alta |

### 4.5 Módulo de Etapa 1 - Diagnóstico
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Registro Voz del Cliente | Formulario estructurado | Alta |
| Matriz de diagnóstico | Evaluación por áreas | Alta |
| Análisis FODA | Fortalezas, Oportunidades, etc. | Alta |
| Definición de objetivos SMART | Formulario con validación | Alta |
| Carga de documentos | Evidencias y grabaciones | Alta |
| Cierre de etapa | Validación y bloqueo | Alta |

### 4.6 Módulo de Etapa 2 - Plan
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Registro de hallazgos | Problema, causa raíz | Alta |
| Acciones de mejora | Propuestas por hallazgo | Alta |
| Matriz de priorización | Impacto vs Esfuerzo visual | Alta |
| Cronograma de trabajo | Diagrama de Gantt básico | Alta |
| Aprobación del plan | Workflow de aprobación | Alta |
| Exportar plan PDF | Documento descargable | Media |

### 4.7 Módulo de Etapa 3 - Implementación
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Tablero Kanban | Vista de tareas por estado | Alta |
| Gestión de tareas | CRUD completo | Alta |
| Carga de evidencias | Archivos por tarea | Alta |
| Registro de sesiones | Acompañamiento consultor | Alta |
| Cálculo de avance | Automático por tareas | Alta |
| Alertas de atraso | Notificaciones automáticas | Media |

### 4.8 Módulo de Etapa 4 - Monitoreo
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Dashboard de KPIs | Gráficos en tiempo real | Alta |
| Registro de mediciones | Entrada manual de valores | Alta |
| Reportes semanales | Generación y envío | Alta |
| Evaluaciones directivas | Registro de actas | Media |
| Informe de cierre | Generación automática PDF | Alta |
| Comparativo inicial/final | Gráfico de mejora | Alta |

### 4.9 Módulo de Talleres
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| CRUD Talleres | Crear y gestionar talleres | Alta |
| Programación de sesiones | Fechas y horarios | Alta |
| Inscripciones | Registro de participantes | Alta |
| Control de asistencia | Marcaje de asistencia | Alta |
| Encuesta de satisfacción | Formulario post-taller | Media |
| Generación certificados | PDF automático | Media |
| Envío de certificados | Por email | Media |

### 4.10 Módulo Post-Ruta
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Suscripciones | Gestión de membresías | Media |
| Dashboard proveedor | KPIs ingresados manualmente | Media |
| Mentorías | Agendamiento y registro | Media |
| Eventos de networking | Gestión e inscripciones | Baja |
| Recursos compartidos | Biblioteca de documentos | Baja |

### 4.11 Módulo de Comunidad
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Foros de discusión | Categorías y temas | Baja |
| Respuestas y likes | Interacción básica | Baja |
| Biblioteca de recursos | Documentos compartidos | Baja |
| Búsqueda | En foros y recursos | Baja |

### 4.12 Módulo de Reportes
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Reporte avance proveedor | Individual PDF | Alta |
| Reporte consolidado proyecto | Todos los proveedores | Alta |
| Reporte ejecutivo | Resumen para dirección | Alta |
| Reporte comparativo | Benchmarking proveedores | Media |
| Programación de reportes | Envío automático | Baja |

### 4.13 Módulo de Notificaciones
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Notificaciones en sistema | Campana con contador | Alta |
| Envío de emails | Via Google Workspace API | Alta |
| Envío de WhatsApp | Via API Twilio/Meta | Media |
| Plantillas personalizables | Editor de plantillas | Media |
| Preferencias de usuario | Configurar qué recibir | Baja |

### 4.14 Módulo de Importación/Exportación
| Funcionalidad | Descripción | Prioridad |
|---------------|-------------|-----------|
| Importar proveedores Excel | Carga masiva | Media |
| Importar diagnósticos Excel | Carga masiva | Baja |
| Exportar a Excel | Listados y reportes | Media |
| Plantillas de importación | Descargar formato | Media |

---

## 5. Interfaces de Usuario (Wireframes)

### 5.1 Dashboard Principal (Admin/Consultor)
```
┌─────────────────────────────────────────────────────────────────────┐
│ [Logo]  Sistema Fortalecimiento Proveedores    [Notif] [Usuario ▼] │
├─────────────────────────────────────────────────────────────────────┤
│ ┌─────────┐                                                         │
│ │ SIDEBAR │  ┌─────────────────────────────────────────────────┐   │
│ │         │  │ Dashboard General                               │   │
│ │ Dashboard│  ├─────────────────────────────────────────────────┤   │
│ │ Empresas │  │ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐       │   │
│ │ Proveed. │  │ │ 5     │ │ 120   │ │ 45    │ │ 85%   │       │   │
│ │ Proyectos│  │ │Proyect│ │Proved.│ │Etapa 3│ │Avance │       │   │
│ │ Talleres │  │ └───────┘ └───────┘ └───────┘ └───────┘       │   │
│ │ Reportes │  │                                                 │   │
│ │ Config.  │  │ ┌─────────────────────┐ ┌───────────────────┐  │   │
│ │          │  │ │ Proyectos Activos   │ │ Tareas Pendientes │  │   │
│ │          │  │ │ [Tabla con filtros] │ │ [Lista de tareas] │  │   │
│ │          │  │ └─────────────────────┘ └───────────────────┘  │   │
│ │          │  │                                                 │   │
│ │          │  │ ┌───────────────────────────────────────────┐  │   │
│ │          │  │ │ Avance por Proyecto      [Chart.js]       │  │   │
│ │          │  │ └───────────────────────────────────────────┘  │   │
│ └─────────┘  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Vista de Proyecto con Proveedores
```
┌─────────────────────────────────────────────────────────────────────┐
│ Proyecto: Fortalecimiento Q1 2025 - Empresa XYZ                     │
├─────────────────────────────────────────────────────────────────────┤
│ [Info General] [Proveedores] [Talleres] [Reportes] [Configuración] │
├─────────────────────────────────────────────────────────────────────┤
│ Proveedores del Proyecto (15/40)                    [+ Agregar]    │
├─────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Filtros: [Etapa ▼] [Estado ▼] [Consultor ▼] [Buscar...    ]    │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ Proveedor        │ Etapa │ Estado      │ Avance │ Consultor   │  │
│ ├──────────────────┼───────┼─────────────┼────────┼─────────────┤  │
│ │ Proveed. ABC SAS │  ●●●○ │ En proceso  │ ████░░ │ Juan Pérez  │  │
│ │ Industrias XYZ   │  ●●○○ │ En proceso  │ ██░░░░ │ Ana García  │  │
│ │ Comercial 123    │  ●○○○ │ Diagnóstico │ █░░░░░ │ Juan Pérez  │  │
│ └────────────────────────────────────────────────────────────────┘  │
│                                                                     │
│ Leyenda Etapas: ● Completada  ○ Pendiente                          │
│ 1-Diagnóstico  2-Plan  3-Implementación  4-Monitoreo               │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.3 Detalle Proveedor en Proyecto (Etapas)
```
┌─────────────────────────────────────────────────────────────────────┐
│ ← Volver │ Proveedor ABC SAS - Proyecto Fort. Q1 2025              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │ ETAPA 1  │───▶│ ETAPA 2  │───▶│ ETAPA 3  │───▶│ ETAPA 4  │     │
│  │Diagnóst. │    │   Plan   │    │ Implem.  │    │ Monitor. │     │
│  │   ✓      │    │   ✓      │    │ ▶ 65%    │    │   ○      │     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ ETAPA 3: IMPLEMENTACIÓN                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│ │ PENDIENTE   │ │ EN PROGRESO │ │ COMPLETADAS │ │ BLOQUEADAS  │   │
│ ├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤   │
│ │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │             │   │
│ │ │ Tarea 4 │ │ │ │ Tarea 2 │ │ │ │ Tarea 1 │ │ │             │   │
│ │ └─────────┘ │ │ │ 50%     │ │ │ │ ✓       │ │ │             │   │
│ │ ┌─────────┐ │ │ └─────────┘ │ │ └─────────┘ │ │             │   │
│ │ │ Tarea 5 │ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │             │   │
│ │ └─────────┘ │ │ │ Tarea 3 │ │ │ │ Tarea 0 │ │ │             │   │
│ │             │ │ │ 30%     │ │ │ │ ✓       │ │ │             │   │
│ │             │ │ └─────────┘ │ │ └─────────┘ │ │             │   │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                                                                     │
│ [+ Nueva Tarea]  [📊 Ver Gantt]  [📄 Sesiones]  [📈 Avance]       │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.4 Dashboard KPIs (Etapa 4)
```
┌─────────────────────────────────────────────────────────────────────┐
│ Monitoreo y Evaluación - Proveedor ABC SAS                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │                    INDICADORES CLAVE                            │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │ │
│ │  │ Productividad │  │ Calidad       │  │ Entregas      │       │ │
│ │  │    ▲ 25%      │  │    ▲ 15%      │  │    ▲ 30%      │       │ │
│ │  │  ┌────────┐   │  │  ┌────────┐   │  │  ┌────────┐   │       │ │
│ │  │  │   85   │   │  │  │   92   │   │  │  │   95   │   │       │ │
│ │  │  │  /100  │   │  │  │  /100  │   │  │  │  /100  │   │       │ │
│ │  │  └────────┘   │  │  └────────┘   │  │  └────────┘   │       │ │
│ │  │ Meta: 90      │  │ Meta: 95      │  │ Meta: 98      │       │ │
│ │  └───────────────┘  └───────────────┘  └───────────────┘       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Evolución de Indicadores                        [Semanal ▼]    │ │
│ │ ┌───────────────────────────────────────────────────────────┐  │ │
│ │ │                    📈 Gráfico de líneas                   │  │ │
│ │ │                    (Chart.js)                             │  │ │
│ │ └───────────────────────────────────────────────────────────┘  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ [+ Registrar Medición]  [📊 Generar Reporte]  [📤 Enviar Informe] │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. API REST (Endpoints Principales)

### 6.1 Autenticación
```
POST   /api/auth/login/
POST   /api/auth/logout/
POST   /api/auth/password/reset/
POST   /api/auth/password/change/
GET    /api/auth/user/
```

### 6.2 Empresas Ancla
```
GET    /api/empresas/                    # Listar (admin)
POST   /api/empresas/                    # Crear
GET    /api/empresas/{id}/               # Detalle
PUT    /api/empresas/{id}/               # Actualizar
DELETE /api/empresas/{id}/               # Desactivar
GET    /api/empresas/{id}/proyectos/     # Proyectos de empresa
GET    /api/empresas/{id}/proveedores/   # Proveedores vinculados
```

### 6.3 Proveedores
```
GET    /api/proveedores/                 # Listar
POST   /api/proveedores/                 # Crear
GET    /api/proveedores/{id}/            # Detalle
PUT    /api/proveedores/{id}/            # Actualizar
GET    /api/proveedores/{id}/historial/  # Historial de proyectos
POST   /api/proveedores/importar/        # Importación masiva
```

### 6.4 Proyectos
```
GET    /api/proyectos/                   # Listar
POST   /api/proyectos/                   # Crear
GET    /api/proyectos/{id}/              # Detalle
PUT    /api/proyectos/{id}/              # Actualizar
GET    /api/proyectos/{id}/proveedores/  # Proveedores del proyecto
POST   /api/proyectos/{id}/proveedores/  # Agregar proveedor
DELETE /api/proyectos/{id}/proveedores/{prov_id}/  # Quitar proveedor
GET    /api/proyectos/{id}/dashboard/    # Métricas del proyecto
```

### 6.5 Etapas (por ProveedorProyecto)
```
# Etapa 1
GET    /api/proveedor-proyecto/{id}/etapa1/
PUT    /api/proveedor-proyecto/{id}/etapa1/
POST   /api/proveedor-proyecto/{id}/etapa1/voz-cliente/
POST   /api/proveedor-proyecto/{id}/etapa1/diagnostico/
POST   /api/proveedor-proyecto/{id}/etapa1/objetivos/
POST   /api/proveedor-proyecto/{id}/etapa1/documentos/
POST   /api/proveedor-proyecto/{id}/etapa1/completar/

# Etapa 2
GET    /api/proveedor-proyecto/{id}/etapa2/
PUT    /api/proveedor-proyecto/{id}/etapa2/
POST   /api/proveedor-proyecto/{id}/etapa2/hallazgos/
PUT    /api/proveedor-proyecto/{id}/etapa2/hallazgos/{h_id}/
POST   /api/proveedor-proyecto/{id}/etapa2/acciones/
POST   /api/proveedor-proyecto/{id}/etapa2/cronograma/
POST   /api/proveedor-proyecto/{id}/etapa2/aprobar/

# Etapa 3
GET    /api/proveedor-proyecto/{id}/etapa3/
GET    /api/proveedor-proyecto/{id}/etapa3/tareas/
POST   /api/proveedor-proyecto/{id}/etapa3/tareas/
PUT    /api/proveedor-proyecto/{id}/etapa3/tareas/{t_id}/
POST   /api/proveedor-proyecto/{id}/etapa3/tareas/{t_id}/evidencias/
POST   /api/proveedor-proyecto/{id}/etapa3/sesiones/
GET    /api/proveedor-proyecto/{id}/etapa3/gantt/

# Etapa 4
GET    /api/proveedor-proyecto/{id}/etapa4/
GET    /api/proveedor-proyecto/{id}/etapa4/kpis/
POST   /api/proveedor-proyecto/{id}/etapa4/kpis/{k_id}/mediciones/
POST   /api/proveedor-proyecto/{id}/etapa4/reportes-semanales/
POST   /api/proveedor-proyecto/{id}/etapa4/evaluaciones/
POST   /api/proveedor-proyecto/{id}/etapa4/informe-cierre/
```

### 6.6 Talleres
```
GET    /api/talleres/
POST   /api/talleres/
GET    /api/talleres/{id}/
POST   /api/talleres/{id}/sesiones/
GET    /api/talleres/{id}/sesiones/{s_id}/inscripciones/
POST   /api/talleres/{id}/sesiones/{s_id}/inscripciones/
POST   /api/talleres/{id}/sesiones/{s_id}/asistencia/
POST   /api/talleres/{id}/sesiones/{s_id}/certificados/generar/
```

### 6.7 Reportes
```
GET    /api/reportes/avance-proveedor/{prov_proy_id}/
GET    /api/reportes/consolidado-proyecto/{proyecto_id}/
GET    /api/reportes/ejecutivo/{empresa_id}/
GET    /api/reportes/comparativo/{proyecto_id}/
```

---

## 7. Fases de Desarrollo

### Fase 1: Fundamentos (MVP Core)
**Objetivo:** Sistema funcional con flujo básico completo

#### Apps a desarrollar:
- `core` - Autenticación y usuarios
- `empresas` - Gestión de empresas ancla
- `proveedores` - Gestión de proveedores
- `proyectos` - Proyectos y asignaciones
- `etapas` - Las 4 etapas básicas

#### Entregables:
1. Estructura del proyecto Django
2. Modelos de datos core
3. Sistema de autenticación
4. CRUD Empresas Ancla
5. CRUD Proveedores
6. CRUD Proyectos
7. Asignación de proveedores a proyectos
8. Flujo de Etapa 1 (Diagnóstico)
9. Flujo de Etapa 2 (Plan)
10. Flujo de Etapa 3 (Implementación) - Kanban básico
11. Flujo de Etapa 4 (Monitoreo) - KPIs básicos
12. Dashboard principal
13. Templates base Bootstrap 5

---

### Fase 2: Talleres y Reportes
**Objetivo:** Gestión completa de talleres y generación de reportes

#### Apps a desarrollar:
- `talleres` - Gestión completa de talleres
- `reportes` - Generación de PDF

#### Entregables:
1. CRUD Talleres
2. Programación de sesiones
3. Sistema de inscripciones
4. Control de asistencia
5. Encuestas post-taller
6. Generación de certificados PDF
7. Reportes de avance por proveedor PDF
8. Reportes consolidados por proyecto PDF
9. Reportes ejecutivos PDF
10. Exportación a Excel

---

### Fase 3: Notificaciones e Integraciones
**Objetivo:** Sistema de comunicación completo

#### Apps a desarrollar:
- `notificaciones` - Sistema de alertas
- `importacion` - Carga masiva

#### Entregables:
1. Sistema de notificaciones en app
2. Integración Google Workspace (Gmail API)
3. Integración WhatsApp Business API
4. Plantillas de notificaciones editables
5. Preferencias de notificación por usuario
6. Importación masiva de proveedores desde Excel
7. Plantillas de importación descargables
8. Validación y reporte de errores en importación

---

### Fase 4: Post-Ruta y Comunidad
**Objetivo:** Ecosistema de mejora continua

#### Apps a desarrollar:
- `postruta` - Servicios post-intervención
- `comunidad` - Foros y recursos

#### Entregables:
1. Gestión de suscripciones post-ruta
2. Dashboard de KPIs para proveedores (entrada manual)
3. Sistema de mentorías
4. Gestión de eventos de networking
5. Foros de discusión
6. Biblioteca de recursos compartidos
7. Sistema de búsqueda

---

### Fase 5: Optimización y Despliegue
**Objetivo:** Sistema listo para producción

#### Entregables:
1. Optimización de consultas (Django Debug Toolbar, query optimization)
2. Implementación de caché con Redis
3. Configuración de Celery para tareas asíncronas
4. Pruebas unitarias y de integración
5. Configuración de Google Cloud
6. Despliegue en producción
7. Configuración de dominio y SSL
8. Documentación técnica
9. Manual de usuario

---

## 8. Estructura de Carpetas del Proyecto

```
gestion_proveedores/
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   ├── mixins.py
│   │   ├── utils.py
│   │   ├── templates/
│   │   │   └── core/
│   │   └── tests/
│   ├── empresas/
│   │   ├── (misma estructura)
│   ├── proveedores/
│   │   ├── (misma estructura)
│   ├── proyectos/
│   │   ├── (misma estructura)
│   ├── etapas/
│   │   ├── (misma estructura)
│   ├── talleres/
│   │   ├── (misma estructura)
│   ├── reportes/
│   │   ├── (misma estructura)
│   ├── notificaciones/
│   │   ├── (misma estructura)
│   ├── postruta/
│   │   ├── (misma estructura)
│   ├── comunidad/
│   │   ├── (misma estructura)
│   └── importacion/
│       ├── (misma estructura)
├── static/
│   ├── css/
│   │   ├── custom.css
│   │   └── vendors/
│   ├── js/
│   │   ├── app.js
│   │   ├── charts.js
│   │   ├── kanban.js
│   │   └── vendors/
│   ├── img/
│   └── fonts/
├── templates/
│   ├── base.html
│   ├── includes/
│   │   ├── sidebar.html
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   ├── messages.html
│   │   └── pagination.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── password_reset.html
│   │   └── password_change.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
├── media/
│   └── (archivos subidos)
├── locale/
│   └── es/
├── docs/
│   ├── api/
│   └── user_manual/
├── scripts/
│   ├── initial_data.py
│   └── backup.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

---

## 9. Configuraciones Clave

### 9.1 Variables de Entorno (.env)
```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Database
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GS_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Email (Google Workspace)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=sistema@tudominio.com
EMAIL_HOST_PASSWORD=app-password
GMAIL_API_CREDENTIALS=/path/to/gmail-credentials.json

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 9.2 Dependencias Principales (requirements/base.txt)
```txt
# Core
Django==4.2.21
psycopg2-binary==2.9.9
python-decouple==3.8
dj-database-url==2.1.0

# REST API
djangorestframework==3.14.0
django-cors-headers==4.3.1
drf-spectacular==0.27.0

# Authentication
djangorestframework-simplejwt==5.3.1

# Forms
django-crispy-forms==2.1
crispy-bootstrap5==2024.2

# Files & Storage
django-storages[google]==1.14.2
Pillow==10.2.0

# PDF Generation
weasyprint==61.2
reportlab==4.1.0

# Excel
openpyxl==3.1.2
pandas==2.2.0

# Async Tasks
celery==5.3.6
django-celery-beat==2.5.0
django-celery-results==2.5.1
redis==5.0.1

# Email & Notifications
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.116.0
twilio==8.13.0

# Utils
django-filter==23.5
django-extensions==3.2.3
python-dateutil==2.8.2
uuid==1.30

# Security
django-csp==3.7
django-secure==1.0.1
```

---

## 10. Consideraciones de Seguridad

### 10.1 Autenticación y Autorización
- Tokens JWT con expiración corta (15 min access, 7 días refresh)
- Roles con permisos granulares por recurso
- Multi-tenancy: usuarios solo ven datos de sus empresas asignadas
- Auditoría de acciones críticas (quién, qué, cuándo)

### 10.2 Protección de Datos
- Encriptación de datos sensibles en BD
- HTTPS obligatorio en producción
- Validación estricta de archivos subidos
- Sanitización de inputs para prevenir XSS/SQL Injection

### 10.3 Configuración Django
```python
# settings/production.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

---

## 11. Métricas de Éxito del Proyecto

| Métrica | Objetivo |
|---------|----------|
| Tiempo de carga de páginas | < 2 segundos |
| Uptime del sistema | > 99.5% |
| Generación de reportes PDF | < 10 segundos |
| Usuarios concurrentes soportados | 100+ |
| Tiempo de respuesta API | < 500ms |

---

## 12. Glosario

| Término | Definición |
|---------|------------|
| **Empresa Ancla** | Empresa cliente que contrata el programa de fortalecimiento |
| **Proveedor** | Empresa beneficiaria del programa de fortalecimiento |
| **Proyecto** | Ciclo de fortalecimiento (3 meses, N proveedores) |
| **Etapa** | Fase del modelo PHVA (Diagnóstico, Plan, Implementación, Monitoreo) |
| **Consultor** | Profesional que acompaña a los proveedores |
| **Post-Ruta** | Servicio de acompañamiento posterior al programa |
| **KPI** | Indicador Clave de Desempeño |

---

*Documento generado: Diciembre 2024*
*Versión: 1.0*
