# 🌸 Bebe Names Studio | Gestor de Nombres

Aplicación web interactiva y moderna para explorar, clasificar y gestionar la lista de nombres femeninos revisados del documento **Nombres Version 1.0.pdf**, junto con **500 nuevos nombres seleccionados de origen latino y español** con sus significados y orígenes.

---

## 🚀 Cómo Iniciar la Aplicación

Puedes usar la aplicación de **dos formas muy sencillas**:

### Opción 1: Con Servidor Local (Recomendado - sincroniza directamente con `names_db.json`)
1. Haz doble clic en **`start_app.bat`** (o ejecuta en PowerShell `./start_app.ps1` o `python server.py`).
2. Se abrirá automáticamente tu navegador en **`http://localhost:8000`**.
3. Todos los cambios de estado, notas y nuevos nombres se guardarán de inmediato en el archivo **`names_db.json`** en esta misma carpeta.

### Opción 2: Modo Directo Sin Servidor
1. Haz doble clic en el archivo **`index.html`** directamente.
2. La aplicación se ejecutará de forma autónoma en tu navegador y guardará todos los cambios en el almacenamiento local (`localStorage`), con opción de descargar y restaurar copias de seguridad en cualquier momento con 1 clic.

---

## 📊 Resumen de Datos Extraídos

- **Total de Nombres en la Base de Datos:** **1,672 nombres**
  - **Provenientes del PDF Versión 1.0:** **1,172 nombres**
  - **500 Nuevos Nombres Latinos / Españoles (sin repetir ninguno del PDF):** **500 nombres**
- **Clasificación Inicial de Estados:**
  - ⭐ **Favoritos (23 nombres):** Nombres resaltados en amarillo en el PDF (p. ej. *Alexandra, Ana, Anahí, Camille, Caterina, Corina, Isabel, Krista, Lisa, Marcella, María, Maribel, Millie, Mina, Nadia, Natalia, Nicole, Pamela, Paula, Paulina, Sara, Tania, Ximena*).
  - 👍 **Posibles (558 nombres):** Nombres con flecha `->` del PDF (58 nombres) + los **500 nuevos nombres latinos/españoles** añadidos en estado de revisión.
  - ❌ **Excluidos (1,091 nombres):** Todos los nombres con números tachados en la revisión del PDF.

---

## ✨ Características Principales

1. **Gestión de Estados con 1 Clic:**
   - Cambia cualquier nombre entre **⭐ Favorito**, **👍 Posible** y **❌ Excluido** con botones de acceso directo en cada tarjeta o fila.
2. **Añadir Nuevos Nombres:**
   - Botón **`➕ Añadir Nombre`** para registrar nuevos nombres con su etimología, significado, estado inicial y notas personales. Detección automática en tiempo real de duplicados.
3. **Editar y Anotar:**
   - Permite corregir significados, orígenes o añadir notas familiares (p. ej., *"Nombre de la abuela"*, *"Combina con María"*).
4. **Modo Descubrimiento Rápido ("Estilo Swipe / Tarjetas"):**
   - Una vista interactiva para calificar nombres uno a uno con teclas de flecha (← Excluir, ↓ Posible, → Favorito). Ideal para revisar en pareja los 500 nuevos nombres.
5. **Búsqueda y Filtros Potentes:**
   - Búsqueda en tiempo real por nombre, significado, origen o notas.
   - Pestañas por estado: *Todos*, *Favoritos*, *Posibles*, *Excluidos*.
   - Filtro por origen de lista (*PDF v1.0*, *500 Nuevos Latinos*, *Añadidos por ti*).
   - Filtro por etimología (*Español, Latín, Griego, Hebreo, Italiano, Francés, Vasco, Catalán, etc.*).
   - Cinta alfabética interactiva (A-Z).
6. **Vistas Alternables:**
   - **Cuadrícula de Tarjetas:** Elegante, con avatares pastel y significados en cursiva.
   - **Tabla Detallada:** Compacta y ordenada para gestión rápida.
7. **Exportación y Respaldos:**
   - Exporta a **Excel (CSV con codificación UTF-8)** con un solo clic.
   - Descarga de copias de seguridad en formato **JSON**.
   - Restauración a la lista inicial cuando lo desees.

---

## 📁 Archivos Incluidos

- `index.html`: La aplicación web completa, reactiva y adaptable a móviles.
- `names_db.json`: Base de datos de los 1,672 nombres en formato JSON.
- `names_db_backup.json`: Respaldo original intacto para permitir restauraciones.
- `server.py`: Servidor HTTP ligero en Python (biblioteca estándar, sin dependencias externas).
- `start_app.bat`: Acceso directo para iniciar la app en Windows con un doble clic.
- `start_app.ps1`: Script de inicio para PowerShell.
- `Nombres Version 1.0.pdf`: El archivo PDF original con las anotaciones y marcas de revisión.
