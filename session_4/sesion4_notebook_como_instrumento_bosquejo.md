# Sesión 4 — El notebook como instrumento (BOSQUEJO v0.1)

**Responsable:** Jakob
**Público:** estudiantes de Bachelor en Biomedizinische Technik, sin bases de Python
**Estado:** borrador, falta información (ver sección "Preguntas abiertas" al final)

---

## Cómo leer este documento

Cada bloque está marcado con una etiqueta para distinguir qué es texto y qué es código:

| Marca | Significado |
|---|---|
| 📝 **[TEXTO]** | Contenido escrito: guía, instrucciones, explicaciones, tarjetas para estudiantes. Va en la guía impresa/PDF o en celdas Markdown del notebook. |
| 💻 **[CÓDIGO]** | Código Python que va dentro de celdas de código del notebook (incluye los comentarios `#` que son parte del código). |
| 🗂️ **[ESTRUCTURA]** | Nota para los organizadores. No se muestra a los estudiantes. |

---

## 1. Resumen de la sesión

🗂️ **[ESTRUCTURA]**

- **Idea central:** el notebook funciona como un instrumento de medición: los estudiantes no lo programan, *giran perillas* (parámetros marcados).
- **Los estudiantes nunca escriben código desde una celda vacía.**
- **Supervisión:** mínima o nula. La guía y el notebook llevan la sesión.
- **Fuera de alcance:** conceptos básicos de Python (variables, listas, bucles), enseñanza de pandas/matplotlib.
- **Herramientas:**
  - JupyterLite en el navegador (sin cuentas, a diferencia de Colab).
  - Un chat LLM gratuito en el navegador (en lugar de Copilot).
  - Tarjeta con 3 prompts que funcionan.

### Objetivos de aprendizaje (propuesta)

📝 **[TEXTO]**

Al terminar la sesión, el estudiante puede:

1. Ejecutar un notebook de principio a fin con sus propios datos de sensor.
2. Identificar el bloque "YOU MAY CHANGE THIS" y modificar solo esos valores.
3. Pedirle a un LLM que le explique qué hace una celda.
4. Pedirle a un LLM un cambio pequeño y comprobar si funcionó.
5. Guardar una figura como PNG.

---

## 2. Estructura temporal (propuesta, a confirmar)

🗂️ **[ESTRUCTURA]**

| Min | Bloque | Tipo |
|---|---|---|
| 0–10 | Bienvenida, abrir JupyterLite, subir el CSV propio | Texto (guía) |
| 10–15 | Ejecutar el notebook completo con el CSV de referencia ("primer clic") | Texto + código ya escrito |
| 15–45 | Celdas 1–5 con los datos propios, cambiando parámetros | Código + texto |
| 45–65 | Trabajo con el LLM: explicar una celda + un cambio pequeño | Texto (tarjeta de prompts) |
| 65–75 | Guardar PNG, cierre y reflexión | Texto |

*(Duración total pendiente de confirmar.)*

---

## 3. Material para estudiantes

### 3.1 Guía de la sesión (documento corto, 1–2 páginas)

📝 **[TEXTO]**

Secciones propuestas:

1. **Qué vamos a hacer hoy** (3 frases, sin jerga).
2. **Antes de empezar:** abrir JupyterLite, abrir el notebook, subir tu CSV.
3. **Cómo se ejecuta una celda:** `Shift + Enter` o botón ▶. Qué significa `[*]` junto a la celda.
4. **La regla de oro:** solo cambias lo que está dentro de la caja `YOU MAY CHANGE THIS`.
5. **Qué hacer si sale un error en rojo:** no entrar en pánico, leer la última línea, copiarla al LLM (ver tarjeta).
6. **Mini-reto final:** ver sección 5.

### 3.2 Tarjeta de prompts para el LLM

📝 **[TEXTO]**

> Tres prompts que funcionan. Copia, pega y rellena lo que está entre `[ ]`.

**Prompt A — Explicar una celda**
```text
Soy estudiante de ingeniería biomédica y no sé programar. Explícame en
lenguaje sencillo, línea por línea, qué hace este código de Python.
No cambies nada, solo explícalo:

[pega aquí el código de la celda]
```

**Prompt B — Hacer un cambio pequeño**
```text
Aquí hay un código de Python. Quiero UN solo cambio: [describe el cambio,
p. ej. "que la línea del gráfico sea roja"]. Devuélveme el código completo
con el cambio y dime exactamente qué línea cambiaste:

[pega aquí el código de la celda]
```

**Prompt C — Entender un error**
```text
Al ejecutar esta celda me sale este error. Explícame en palabras simples
qué significa y cómo lo arreglo, tocando lo mínimo posible:

[pega el código]
[pega el mensaje de error]
```

🗂️ **[ESTRUCTURA]** *Pendiente: decidir qué LLM gratuito recomendamos (y si requiere cuenta) y probar los 3 prompts con él.*

---

## 4. El notebook (5 celdas)

🗂️ **[ESTRUCTURA]**
Cada celda tiene: (a) un encabezado grande en comentarios, (b) una caja `YOU MAY CHANGE THIS`, (c) código fijo que no se toca. Se ejecuta a la primera con el CSV de referencia incluido.

**Supuestos temporales** (se ajustan cuando tengamos el CSV real): columna de tiempo llamada `time_s`; seis señales con nombres tipo `signal_1 … signal_6`; nombre del archivo `reference_data.csv`.

---

### Celda 0 (opcional) — Bienvenida

📝 **[TEXTO]** *(celda Markdown)*

```markdown
# 🔬 El notebook como instrumento
Este notebook funciona como un aparato de medición: tú no lo construyes,
solo giras las perillas.

**Reglas:**
1. Ejecuta las celdas de arriba hacia abajo (Shift + Enter).
2. Solo cambia lo que está dentro de la caja "YOU MAY CHANGE THIS".
3. Si algo sale en rojo, lee la última línea del mensaje. No es el fin del mundo.
```

💻 **[CÓDIGO]** *(instalación/import necesarios para JupyterLite, a validar)*

```python
# Preparación (no tocar)
import pandas as pd
import matplotlib.pyplot as plt
```

---

### Celda 1 — Load (Cargar)

**Qué hace:** lee el CSV, muestra las primeras filas y los nombres de columnas.
**Puede cambiar:** el nombre del archivo.

📝 **[TEXTO]** *(texto de apoyo en Markdown encima de la celda)*

```markdown
## Celda 1 — Cargar los datos
Esta celda abre tu archivo CSV y te enseña las primeras filas, para que veas
cómo se llaman tus columnas. Esos nombres los necesitarás en la Celda 3.
```

💻 **[CÓDIGO]**

```python
# ==============================================================
#  CELDA 1 — CARGAR LOS DATOS
#  Qué hace: abre un archivo CSV (una tabla) y muestra las
#  primeras filas y los nombres de las columnas.
# ==============================================================

# --------------------------------------------------------------
#  >>> YOU MAY CHANGE THIS <<<
#  FILE_NAME: el nombre de tu archivo, entre comillas.
#  Ejemplo: "mis_datos.csv"
#  Error típico: FileNotFoundError -> el nombre está mal escrito
#  o el archivo no está subido. Revisa mayúsculas y la extensión .csv
# --------------------------------------------------------------
FILE_NAME = "reference_data.csv"
# --------------------------------------------------------------

# --- A partir de aquí NO cambies nada ---
data = pd.read_csv(FILE_NAME)
print("Primeras filas:")
print(data.head())
print()
print("Nombres de las columnas:")
print(list(data.columns))
```

---

### Celda 2 — Plot everything (Graficar todo)

**Qué hace:** las seis señales contra el tiempo.
**Puede cambiar:** nada (usa lo cargado en la Celda 1).

📝 **[TEXTO]**

```markdown
## Celda 2 — Ver todas las señales
Esta celda dibuja las seis señales a la vez. No hay nada que cambiar:
solo mira y compara. ¿Cuál señal parece más "ruidosa"? ¿Cuál es más lenta?
```

💻 **[CÓDIGO]**

```python
# ==============================================================
#  CELDA 2 — GRAFICAR TODAS LAS SEÑALES
#  Qué hace: dibuja las seis señales contra el tiempo.
#  No hay nada que cambiar aquí.
#  Error típico: NameError: name 'data' is not defined
#  -> te saltaste la Celda 1. Ejecútala primero.
# ==============================================================

# --- NO cambies nada ---
signal_columns = [c for c in data.columns if c != "time_s"]

fig, axes = plt.subplots(len(signal_columns), 1, sharex=True, figsize=(10, 12))
for ax, col in zip(axes, signal_columns):
    ax.plot(data["time_s"], data[col])
    ax.set_ylabel(col)
axes[-1].set_xlabel("Tiempo (s)")
plt.tight_layout()
plt.show()
```

---

### Celda 3 — Pick one signal (Elegir una señal)

**Qué hace:** grafica una sola columna con etiqueta de eje y.
**Puede cambiar:** nombre de la columna y etiqueta del eje y (las que definieron en la Sesión 3).

📝 **[TEXTO]**

```markdown
## Celda 3 — Elegir una señal
Elige UNA señal de las que viste en la Celda 1 y ponle la etiqueta correcta
(nombre de la magnitud y unidad), como lo definiste en la Sesión 3.
```

💻 **[CÓDIGO]**

```python
# ==============================================================
#  CELDA 3 — ELEGIR UNA SEÑAL
#  Qué hace: dibuja solo una columna, con su etiqueta en el eje y.
# ==============================================================

# --------------------------------------------------------------
#  >>> YOU MAY CHANGE THIS <<<
#  COLUMN_NAME: nombre EXACTO de la columna (mira la lista de la
#               Celda 1). Entre comillas.
#  Y_LABEL: lo que quieres leer en el eje vertical, con unidad.
#           Ejemplo: "Frecuencia cardíaca (lpm)"
#  Error típico: KeyError -> el nombre de la columna no existe tal
#  cual lo escribiste (¿mayúsculas? ¿espacios?). Cópialo de la Celda 1.
# --------------------------------------------------------------
COLUMN_NAME = "signal_1"
Y_LABEL = "Señal 1 (unidad)"
# --------------------------------------------------------------

# --- A partir de aquí NO cambies nada ---
plt.figure(figsize=(10, 4))
plt.plot(data["time_s"], data[COLUMN_NAME])
plt.xlabel("Tiempo (s)")
plt.ylabel(Y_LABEL)
plt.show()
```

---

### Celda 4 — Zoom

**Qué hace:** recorta el gráfico a una ventana de tiempo y añade título.
**Puede cambiar:** tiempo de inicio, tiempo de fin, título.

📝 **[TEXTO]**

```markdown
## Celda 4 — Acercarse a un momento
Elige un intervalo de tiempo interesante (¿un movimiento? ¿un pico?) y
ponle un título que diga qué estás viendo.
```

💻 **[CÓDIGO]**

```python
# ==============================================================
#  CELDA 4 — ZOOM A UNA VENTANA DE TIEMPO
#  Qué hace: muestra solo una parte de la señal y le pone título.
# ==============================================================

# --------------------------------------------------------------
#  >>> YOU MAY CHANGE THIS <<<
#  START_TIME: segundo donde empieza el recorte (número)
#  END_TIME:   segundo donde termina (debe ser MAYOR que START_TIME)
#  TITLE:      título del gráfico, entre comillas
#  Error típico: un gráfico vacío -> tu intervalo está fuera del
#  rango de tus datos. Mira el eje de tiempo de la Celda 2.
# --------------------------------------------------------------
START_TIME = 5
END_TIME = 15
TITLE = "Mi título aquí"
# --------------------------------------------------------------

# --- A partir de aquí NO cambies nada ---
window = data[(data["time_s"] >= START_TIME) & (data["time_s"] <= END_TIME)]

plt.figure(figsize=(10, 4))
plt.plot(window["time_s"], window[COLUMN_NAME])
plt.xlabel("Tiempo (s)")
plt.ylabel(Y_LABEL)
plt.title(TITLE)
plt.show()
```

---

### Celda 5 — Save (Guardar)

**Qué hace:** guarda la figura como PNG.
**Puede cambiar:** nombre del archivo.

📝 **[TEXTO]**

```markdown
## Celda 5 — Guardar tu figura
Tu figura se guarda como imagen PNG. Búscala en el panel de archivos
(izquierda), clic derecho → Download.
```

💻 **[CÓDIGO]**

```python
# ==============================================================
#  CELDA 5 — GUARDAR LA FIGURA
#  Qué hace: guarda el gráfico de la Celda 4 como imagen PNG.
# ==============================================================

# --------------------------------------------------------------
#  >>> YOU MAY CHANGE THIS <<<
#  OUTPUT_NAME: nombre de la imagen. Debe terminar en .png
#  Ejemplo: "mi_figura.png"
# --------------------------------------------------------------
OUTPUT_NAME = "figure.png"
# --------------------------------------------------------------

# --- A partir de aquí NO cambies nada ---
plt.figure(figsize=(10, 4))
plt.plot(window["time_s"], window[COLUMN_NAME])
plt.xlabel("Tiempo (s)")
plt.ylabel(Y_LABEL)
plt.title(TITLE)
plt.savefig(OUTPUT_NAME, dpi=150, bbox_inches="tight")
plt.show()
print(f"Guardado como {OUTPUT_NAME}")
```

---

## 5. Tarea con LLM (integrada en el flujo)

📝 **[TEXTO]** *(tarjeta / celda Markdown tras la Celda 4)*

**Parte A — Entender:** copia el código de la Celda 4 y usa el **Prompt A**. Escribe con tus palabras (2 frases): ¿qué hace la línea que empieza con `window = ...`?

**Parte B — Un cambio pequeño:** usa el **Prompt B** para pedir UN cambio (ejemplos: color de la línea, grosor, cuadrícula). Pega el código nuevo en la celda y ejecútalo.

**Parte C — Comprobar:** ¿funcionó? ¿Cambió solo lo que pediste? Si no, usa el **Prompt C**.

🗂️ **[ESTRUCTURA]** *Idea: ofrecer 3 cambios "seguros" sugeridos para evitar que los estudiantes pidan cosas demasiado grandes.*

---

## 6. Entregable / evidencia de aprendizaje (propuesta)

📝 **[TEXTO]**

Cada estudiante entrega:
1. Su PNG final.
2. Una captura del prompt que usó con el LLM y la respuesta.
3. Dos frases: *"Lo que aprendí sobre cómo funciona el notebook"* y *"Dónde el LLM se equivocó o me confundió (si pasó)."*

---

## 7. Preguntas abiertas / información que falta

🗂️ **[ESTRUCTURA]**

- [ ] ¿Formato real del CSV? (nombres de columnas, separador, nombre de la columna de tiempo, frecuencia de muestreo)
- [ ] ¿Qué sensor(es) y qué seis señales exactamente?
- [ ] ¿Duración total de la sesión?
- [ ] ¿Qué LLM gratuito se recomienda y requiere registro?
- [ ] **Técnico JupyterLite:** validar que pandas/matplotlib cargan sin instalar nada, cómo suben los estudiantes su CSV y cómo descargan el PNG.
- [ ] ¿Los estudiantes trabajan en pares o individualmente?
- [ ] ¿Idioma del notebook y de la guía: alemán, inglés o español? (Los comentarios están en español en este borrador; el encabezado `YOU MAY CHANGE THIS` se mantuvo en inglés según el brief.)
- [ ] Conexión con la Sesión 3: ¿en qué formato tienen sus etiquetas (nombre + unidad)?
- [ ] ¿Se necesita plan B si JupyterLite falla en la red de la universidad?
- [ ] ¿Hay que decidir cómo se maneja la Celda 5 (re-dibuja la figura) para que funcione aunque el estudiante ejecute fuera de orden?
