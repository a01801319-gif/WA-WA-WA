# Dashboard Analítico de Ventas y Promociones con Python & Qwen2 LLM

Este proyecto es una aplicación web interactiva desarrollada en **Python** que te permite cargar bases de datos de ventas y promociones (en formato Excel o CSV) para visualizar el desempeño comercial, aplicar filtros avanzados por **Departamento**, **Subdepartamento** y **SKU**, y generar insights de negocio automáticos utilizando el modelo de lenguaje **Qwen2**.

La aplicación ofrece dos modos de ejecución:
1. **Local Tradicional**: Ejecución rápida con servidor Python estándar mediante `streamlit`.
2. **Estático para GitHub Pages (WebAssembly)**: Usando `stlite` (Streamlit compilado en WebAssembly), todo el código de Python corre directamente en el navegador del usuario. Esto te permite alojar la página de manera gratuita en **GitHub Pages** como un archivo HTML estático (`index.html`) con total privacidad y seguridad, ya que tus datos nunca salen de tu computadora.

---

## Estructura del Proyecto

*   `app.py`: Archivo de código fuente principal en Python (contiene toda la lógica de Streamlit, procesamiento de datos con Pandas, gráficos de Plotly y conectividad con Qwen2).
*   `index.html`: La versión WebAssembly autocompilada para GitHub Pages.
*   `build.py`: Script de Python que compila y actualiza el código de `app.py` dentro de `index.html`.
*   `generate_sample_data.py`: Script auxiliar para generar datos de prueba (`ventas.csv` y `promociones.csv`) si deseas probar las visualizaciones antes de subir tus archivos reales.
*   `ventas.csv` y `promociones.csv`: Archivos de muestra autogenerados.

---

## 🚀 Guía de Uso Local

### 1. Requisitos Previos
Necesitas tener Python instalado (versión 3.8 o superior). Instala las librerías necesarias ejecutando:

```bash
pip install streamlit pandas openpyxl plotly requests
```

### 2. Generar Datos de Prueba (Opcional)
Si deseas probar la aplicación con datos ficticios realistas:

```bash
python generate_sample_data.py
```
Esto generará los archivos `ventas.csv` y `promociones.csv` en tu directorio local.

### 3. Ejecutar la Aplicación
Corre la aplicación localmente con el siguiente comando:

```bash
streamlit run app.py
```
Se abrirá automáticamente una ventana en tu navegador web (usualmente en `http://localhost:8501`).

---

## 🌐 Despliegue en GitHub Pages (Sin Servidor)

Gracias a `stlite`, puedes desplegar tu dashboard interactivo de Python directamente en GitHub Pages en 3 simples pasos:

### Paso 1: Actualizar el HTML estático
Si realizas modificaciones en `app.py`, compila los cambios en `index.html` ejecutando:

```bash
python build.py
```

### Paso 2: Crear un repositorio en GitHub
1. Entra a tu cuenta de GitHub y crea un nuevo repositorio público (ej. `ventas-dashboard`).
2. Sube el archivo `index.html` al repositorio. *(No es necesario subir el código de python ni los datos si solo quieres la versión web, pero subirlos te servirá de respaldo).*
3. Puedes subirlo mediante la interfaz web de GitHub o con comandos git:
   ```bash
   git init
   git add index.html
   git commit -m "Initial commit con dashboard estático de Python"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```

### Paso 3: Activar GitHub Pages
1. Ve a la pestaña **Settings** (Configuración) de tu repositorio en GitHub.
2. En la barra lateral izquierda, haz clic en **Pages**.
3. En la sección **Build and deployment**, bajo **Source**, selecciona **Deploy from a branch**.
4. Selecciona tu rama principal (`main` o `master`) y la carpeta raíz `/ (root)`. Haz clic en **Save** (Guardar).
5. En un par de minutos, GitHub te dará un enlace (ej. `https://tu_usuario.github.io/tu_repositorio/`) donde tu dashboard interactivo de Python estará en línea y listo para ser usado.

---

## 🤖 Integración del LLM Qwen2

El dashboard cuenta con un panel inteligente de generación de insights empresariales. Puedes configurar la conexión con Qwen2 de las siguientes maneras:

### Opción A: Ollama Local (Recomendado para uso privado offline)
Si deseas correr el modelo Qwen2 de forma local en tu computadora:
1. Instala [Ollama](https://ollama.com).
2. Descarga y ejecuta el modelo Qwen2 o Qwen2.5 en tu terminal:
   ```bash
   ollama run qwen2.5
   # o bien:
   ollama run qwen2
   ```
3. En la barra lateral de la aplicación (tanto local como web), selecciona **Ollama (Local)**.
4. Si ejecutas la aplicación localmente con `streamlit run app.py`, la conexión funcionará de inmediato.
5. **Nota sobre GitHub Pages (HTTPS)**: Si estás usando el sitio web subido a GitHub Pages, las políticas de seguridad del navegador bloquean las llamadas a direcciones locales HTTP directas (`http://localhost:11434`) debido al bloqueo de *Mixed Content*. Para solucionarlo, puedes:
   * Correr la aplicación localmente usando `streamlit run app.py`.
   * Habilitar un túnel HTTPS seguro para Ollama (por ejemplo usando ngrok: `ngrok http 11434` y colocando esa URL `https` en el campo del dashboard).

### Opción B: OpenRouter o Hugging Face (Nube)
Si no deseas correr el modelo localmente:
1. Crea una cuenta gratuita en [OpenRouter](https://openrouter.ai) o obtén un token en [Hugging Face](https://huggingface.co).
2. Selecciona el proveedor correspondiente en la barra lateral del dashboard.
3. Introduce tu API Key/Token y presiona el botón **Generar Insights**. Los datos se enviarán cifrados y de manera segura al modelo Qwen2 en la nube.
