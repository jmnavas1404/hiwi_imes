# Sesión 3 — Sensores de movimiento: las señales sin etiqueta (BOSQUEJO v0.1)

**Responsable:** Timo
**Público:** estudiantes de Bachelor en Biomedizinische Technik, sin bases de Python
**Duración:** 3 h
**Estado:** borrador, falta información (ver "Preguntas abiertas" al final)

---

## Cómo leer este documento

| Marca | Significado |
|---|---|
| 📝 **[TEXTO]** | Contenido escrito: guía, diapositivas, hoja de trabajo, explicaciones. |
| 💻 **[CÓDIGO]** | Código o configuración técnica (experimento personalizado, script de verificación). |
| 🗂️ **[ESTRUCTURA]** | Nota para los organizadores. No se muestra a los estudiantes. |

---

## 1. Resumen de la sesión

🗂️ **[ESTRUCTURA]**

- **Tema:** qué "ve" un sensor de movimiento. Dos tipos de sensor (acelerómetro y giroscopio), tres direcciones cada uno. Los estudiantes descubren **experimentalmente** qué curva es cuál.
- **Fuera de alcance:** deriva (drift), ángulos de Euler, algoritmos de orientación (no se necesitan antes de la S7, si acaso).
- **Idea central, la "GUI sin etiquetar":** un experimento personalizado ("Foot Sensor", distribuido por código QR) muestra seis trazas en vivo llamadas *Signal 1 … Signal 6*, **sin nombres, sin unidades y sin frecuencia de muestreo**. El trabajo del grupo es rellenar cada etiqueta mediante experimentos físicos.
- **Herramientas:** IMUs Capture2Go + GUI personalizada.
- **Producto clave para la S4:** un CSV de 10 s de grabación guardado en la carpeta del grupo.

### Objetivos de aprendizaje (propuesta)

📝 **[TEXTO]**

Al terminar la sesión, el estudiante puede:

1. Explicar que un IMU contiene dos tipos de sensor (acelerómetro y giroscopio) con tres ejes cada uno.
2. Distinguir acelerómetro de giroscopio con un experimento simple (IMU en reposo).
3. Identificar qué señal corresponde a qué eje y deducir la unidad de cada sensor.
4. Montar el IMU en el pie y reconocer en la señal el movimiento "punta arriba" (toes up).
5. Exportar una grabación a CSV y comprobar que contiene lo esperado.

---

## 2. Cronograma (3 h)

🗂️ **[ESTRUCTURA]**

| Hora | Bloque | Duración | Tipo |
|---|---|---|---|
| 0:00 | Presentación + demo + código QR | 25 min | Texto (diapositivas) |
| 0:25 | Juego de etiquetas, IMU en la mano | 60 min | Texto (hoja) + código (experimento) |
| 1:25 | Pausa | 10 min | — |
| 1:35 | IMU en el pie, 5 movimientos | 35 min | Texto (hoja) + código (experimento) |
| 2:10 | Exportar CSV a la carpeta del grupo | 10 min | Texto + código (verificación) |
| 2:20 | Grabación misteriosa | 15 min | Texto |
| 2:35 | Cierre: comparar frecuencias de muestreo y eje "toes up"; preguntas | 25 min | Texto |

---

## 3. Bloque por bloque

### 3.1 Presentación (0:00 · 25 min)

📝 **[TEXTO]** *(contenido de las diapositivas, ~8–10 diapositivas)*

1. **Un sensor de movimiento convierte movimiento en curvas.** (imagen de un IMU + una curva)
2. **Dos sensores dentro:**
   - Acelerómetro: "siente" la gravedad y los empujones.
   - Giroscopio: "siente" los giros.
3. **Tres direcciones cada uno** → 2 × 3 = 6 señales.
4. **Demo en vivo:** "inclino el IMU y esta línea se mueve".
5. **La tarea de hoy:** la pantalla no dice qué es cada curva. Ustedes lo descubren.
6. **Código QR** para abrir el experimento "Foot Sensor".
7. **Qué entregan al final** (resumen de la sección 6).

---

### 3.2 Juego de etiquetas, IMU en la mano (0:25 · 60 min)

📝 **[TEXTO]** *(tabla de "trucos" que va en la hoja de trabajo)*

| ¿Qué hay que descubrir? | Cómo lo averiguan los estudiantes |
|---|---|
| ¿Cuáles 3 señales son el acelerómetro y cuáles 3 el giroscopio? | IMU en reposo: tres señales están cerca de cero (**giroscopio**); una de las otras tres tiene un valor constante distinto de cero (**gravedad**). |
| Unidad del acelerómetro | Leer el valor en reposo: ≈ 9,8 → **m/s²**; ≈ 1 → **g**. |
| Qué señal es qué eje | Poner el IMU plano, sobre su borde largo y sobre su borde corto: el valor de gravedad "salta" de una señal a otra. Giroscopio: girar sobre un borde a la vez. |
| Unidad del giroscopio | Cuarto de vuelta en ~1 s: pico ≈ 90 → **°/s**; ≈ 1,6 → **rad/s**. |
| Frecuencia de muestreo | Grabar exactamente 10 s, contar filas del CSV o leer el espaciado de las marcas de tiempo. |

📝 **[TEXTO]** *(hoja de trabajo: tabla de etiquetas)*

| Señal | ¿Sensor? | ¿Eje? | ¿Unidad? | Evidencia (qué hice / qué vi) |
|---|---|---|---|---|
| Signal 1 | | | | |
| Signal 2 | | | | |
| Signal 3 | | | | |
| Signal 4 | | | | |
| Signal 5 | | | | |
| Signal 6 | | | | |

**Cuadro de frecuencia de muestreo:** filas del CSV = ____ ; duración = 10 s ; frecuencia = ____ Hz

🗂️ **[ESTRUCTURA]** El experimento debe tener **campos de etiqueta editables**; al terminar, el grupo exporta su grabación y una captura de pantalla de la pantalla ya etiquetada.

---

### 3.3 IMU en el pie (1:35 · 35 min)

📝 **[TEXTO]** *(instrucciones en la hoja)*

1. Fija el IMU al pie con la banda elástica / calcetín / velcro (ver foto de referencia).
2. Graba cinco movimientos seguidos, con un **golpecito (tap)** antes de cada uno:
   - *tap* → punta arriba (toes up)
   - *tap* → punta abajo (toes down)
   - *tap* → pie hacia dentro
   - *tap* → pie hacia fuera
   - (quinto movimiento a definir, ver preguntas abiertas)
3. Marca a mano cada movimiento sobre la captura de pantalla.
4. Escribe: **¿cuál es la señal "toes up"?** ¿Sube o baja cuando levantas la punta?
5. Toma una foto del montaje.

**Cuadro "montaje en el pie":** ¿dónde pusiste el IMU? ____ ; ¿cómo orientado? ____

---

### 3.4 Exportar CSV (2:10 · 10 min)

📝 **[TEXTO]**

> Guarda **exactamente 10 s** de grabación como CSV en la carpeta del grupo. Este archivo lo usaremos en la Sesión 4.
> Comprueba: ¿se abre? ¿tiene 7 columnas (tiempo + 6 señales)? ¿tiene un número razonable de filas?

💻 **[CÓDIGO]** *(OPCIONAL: verificación rápida para las personas instructoras, no para los estudiantes)*

```python
# Verificación rápida de un CSV exportado (uso: instructores)
import pandas as pd

FILE_NAME = "grupo_X.csv"   # cambiar por el nombre del archivo del grupo

data = pd.read_csv(FILE_NAME)
print("Columnas:", list(data.columns))
print("Filas:", len(data))

# Duración y frecuencia aproximada (asume que la primera columna es el tiempo)
t = data.iloc[:, 0]
duration = t.iloc[-1] - t.iloc[0]
print(f"Duración: {duration:.1f} s")
print(f"Frecuencia de muestreo aprox.: {len(data) / duration:.0f} Hz")
```

🗂️ **[ESTRUCTURA]** Alternativa sin código: los estudiantes solo abren el CSV en Excel y cuentan columnas y filas (ya está en la hoja de trabajo).

⚠️ **Conexión con la Sesión 4:** el notebook de la S4 asume una columna de tiempo llamada `time_s` y seis columnas de señal. Hay que **acordar el formato exacto del CSV** entre S3 y S4 (ver preguntas abiertas).

---

### 3.5 Grabación misteriosa (2:20 · 15 min)

📝 **[TEXTO]**

> Cada grupo recibe una grabación (CSV + captura) hecha por las personas instructoras, de un movimiento desconocido (un paso, una patada, un golpe de pie, quieto…). Usando **tus etiquetas**, di qué movimiento se hizo y por qué.

**Cuadro de respuesta:** Movimiento: ____ ; Evidencia en la señal: ____

🗂️ **[ESTRUCTURA]** Este bloque se puede omitir si falta tiempo (marcado en el documento original como "could be skipped").

---

### 3.6 Cierre (2:35 · 25 min)

📝 **[TEXTO]**

- Cada grupo dice su **frecuencia de muestreo** y su **eje "toes up"** → comparar en la pizarra.
- ¿Coinciden? ¿Por qué no? (diferencias de montaje, de orientación, de dispositivo).
- Preguntas y respuestas.
- Avance de la S4: *"El archivo que guardaron es lo que van a analizar la próxima vez."*

---

## 4. El experimento personalizado "Foot Sensor"

🗂️ **[ESTRUCTURA]**

- **Distribución:** código QR.
- **Muestra:** seis trazas en vivo, nombradas solo *Signal 1 … Signal 6*. Sin unidades, sin frecuencia.
- **Funciones necesarias:**
  1. Gráfico en vivo de 6 señales.
  2. Campos de texto editables para etiquetar cada señal (nombre, unidad).
  3. Grabación de duración fija de 10 s.
  4. Exportación a CSV.
  5. La pantalla ya etiquetada debe poder capturarse.
- **Pendiente decidir la plataforma** (el documento original menciona phyphox, JavaScript o Jupyter, y Movella DOT). Ver preguntas abiertas.

💻 **[CÓDIGO]** *(esqueleto ILUSTRATIVO y NO PROBADO de un experimento phyphox; usa los sensores del teléfono como sustituto. Para leer los IMU Capture2Go o Movella DOT haría falta una entrada Bluetooth configurada a medida.)*

```xml
<phyphox version="1.7">
  <title>Foot Sensor</title>
  <category>Sensores</category>
  <description>Seis señales sin etiqueta. Descubre qué es cada una.</description>

  <data-containers>
    <container size="0">s1</container>
    <container size="0">s2</container>
    <container size="0">s3</container>
    <container size="0">s4</container>
    <container size="0">s5</container>
    <container size="0">s6</container>
    <container size="0">t</container>
  </data-containers>

  <input>
    <sensor type="accelerometer">
      <output component="x">s1</output>
      <output component="y">s2</output>
      <output component="z">s3</output>
      <output component="t">t</output>
    </sensor>
    <sensor type="gyroscope">
      <output component="x">s4</output>
      <output component="y">s5</output>
      <output component="z">s6</output>
    </sensor>
  </input>

  <views>
    <view label="Signals">
      <graph label="Signal 1" labelX="" labelY="" timeOnX="true">
        <input axis="x">t</input><input axis="y">s1</input>
      </graph>
      <!-- repetir para Signal 2 … Signal 6 -->
      <!-- campos de etiqueta editables: a resolver (ver preguntas abiertas) -->
    </view>
  </views>

  <export>
    <set name="Foot Sensor">
      <data name="Time">t</data>
      <data name="Signal 1">s1</data>
      <data name="Signal 2">s2</data>
      <data name="Signal 3">s3</data>
      <data name="Signal 4">s4</data>
      <data name="Signal 5">s5</data>
      <data name="Signal 6">s6</data>
    </set>
  </export>
</phyphox>
```

---

## 5. Material que traen las personas instructoras

🗂️ **[ESTRUCTURA]**

- [ ] 📝 Presentación (25 min).
- [ ] 💻 Experimento personalizado "Foot Sensor".
- [ ] 📝 Hoja de trabajo: tabla de etiquetas (Signal 1–6 → sensor / eje / unidad + evidencia), cuadro de frecuencia de muestreo, cuadro de montaje en el pie, cuadro de respuesta de la grabación misteriosa.
- [ ] Montaje en el pie: bandas elásticas o calcetín/velcro, una por grupo.
- [ ] 📝💻 5 grabaciones misteriosas (CSV + captura), una por grupo *(se puede omitir)*.
- [ ] 💻 **Plan B:** CSV de referencia grabado por las personas instructoras, por si falla la exportación de algún grupo (regla de dependencia con la S4).

---

## 6. Entregable (por grupo)

📝 **[TEXTO]**

1. Hoja de trabajo con las seis etiquetas y la evidencia de cada una.
2. Captura de pantalla del experimento ya etiquetado.
3. Captura de los cinco movimientos, marcada a mano, + foto del montaje.
4. Respuesta de la grabación misteriosa.
5. CSV exportado en la carpeta del grupo (verificado).

---

## 7. Trabajo autónomo

🗂️ **[ESTRUCTURA]**

| Actividad | Tiempo |
|---|---|
| Juego de etiquetas con IMU en la mano | 60 min |
| IMU en el pie, grabación de 5 movimientos, captura marcada | 35 min |
| Exportar CSV a la carpeta del grupo | 10 min |
| Grabación misteriosa | 15 min |

---

## 8. Preguntas abiertas / puntos pendientes

🗂️ **[ESTRUCTURA]**

- [ ] **Plataforma del experimento:** el documento dice "JavaScript o Jupyter notebook" en una parte y "experimento phyphox" en otra. ¿Cuál es la decisión final?
- [ ] **Go/no-go de la GUI de Movella DOT** (el documento lo remite a las "condiciones de contorno acordadas").
- [ ] **¿Los IMU Capture2Go se pueden leer desde la plataforma elegida?** Si es phyphox, hace falta una entrada Bluetooth a medida.
- [ ] **Convenciones de ejes iOS/Android:** confirmar que "toes up" se pueda encontrar en ambos.
- [ ] **Quinto movimiento:** el documento dice "cinco movimientos" pero lista solo cuatro (toes up, toes down, foot in, foot out). ¿Cuál es el quinto?
- [ ] **Formato del CSV** compartido con la S4: nombres de columnas, columna de tiempo (`time_s` en el borrador de la S4), separador decimal (¡ojo con la coma en configuración regional alemana!), unidades de tiempo.
- [ ] **Hoja de trabajo → S4:** los estudiantes usarán sus etiquetas (nombre + unidad) en el eje y de la S4. ¿Cómo las llevan de una sesión a la otra? (foto de la hoja, texto copiado…).
- [ ] **Frecuencia de muestreo:** ¿es fija o depende del dispositivo? Si el CSV tiene marcas de tiempo, ¿en qué unidad?
- [ ] **Grabaciones misteriosas:** ¿se mantienen o se omiten? (tiempo y preparación).
- [ ] **Idioma** de las hojas y de las diapositivas (alemán, inglés o español).
- [ ] **Número de grupos** y número de IMUs disponibles.
