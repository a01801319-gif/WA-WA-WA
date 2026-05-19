import json
import os

def build_static_site():
    app_path = "app.py"
    output_path = "index.html"
    
    if not os.path.exists(app_path):
        print(f"Error: {app_path} no encontrado.")
        return
        
    print(f"Leyendo {app_path}...")
    with open(app_path, "r", encoding="utf-8") as f:
        app_code = f.read()
        
    # Convertir el código de Python a una cadena JSON segura para incrustar en JS
    app_code_json = json.dumps(app_code)
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Dashboard Analítico de Ventas y Promociones</title>
    
    <!-- SEO Meta Tags -->
    <meta name="description" content="Dashboard interactivo en Python para análisis de ventas y promociones que corre 100% en el navegador con privacidad total. Genera insights con Qwen2.">
    <meta name="author" content="Antigravity Sales Dashboard">
    
    <!-- Estilo de stlite -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build/stlite.css" />
    
    <!-- Estilo personalizado para la pantalla de carga (Premium UI) -->
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        body {{
            background-color: #0e1117;
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }}
        
        #loading-container {{
            text-align: center;
            max-width: 500px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(15px);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            z-index: 100;
            transition: opacity 0.5s ease;
        }}
        
        .logo-section {{
            font-size: 64px;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }}
        
        h1 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #2196f3, #4caf50);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        p {{
            font-size: 14px;
            color: #a0a0a0;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        
        /* Spinner Animado */
        .spinner-box {{
            width: 70px;
            height: 70px;
            margin: 0 auto 20px auto;
            position: relative;
        }}
        
        .circle-outer {{
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 3px solid transparent;
            border-top-color: #2196f3;
            border-bottom-color: #4caf50;
            animation: spin 1.5s linear infinite;
        }}
        
        .circle-inner {{
            width: 80%;
            height: 80%;
            position: absolute;
            top: 10%;
            left: 10%;
            border-radius: 50%;
            border: 3px solid transparent;
            border-left-color: #ff9800;
            border-right-color: #e91e63;
            animation: spin-reverse 1s linear infinite;
        }}
        
        .status-tag {{
            display: inline-block;
            padding: 6px 16px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 50px;
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #00e676;
            font-weight: 600;
            box-shadow: 0 0 15px rgba(0, 230, 118, 0.2);
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        @keyframes spin-reverse {{
            0% {{ transform: rotate(360deg); }}
            100% {{ transform: rotate(0deg); }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        /* Ocultar el root de stlite inicialmente para evitar parpadeos */
        #root {{
            width: 100vw;
            height: 100vh;
            display: none;
        }}
    </style>
</head>
<body>
    <!-- Pantalla de carga Premium -->
    <div id="loading-container">
        <div class="logo-section">📊</div>
        <h1>Iniciando WebAssembly Python</h1>
        <p>
            Cargando el entorno de Python (Pyodide), Pandas, Plotly y las librerías analíticas directamente en tu navegador.<br>
            <strong>Tus datos se procesan localmente de forma 100% privada y segura.</strong>
        </p>
        <div class="spinner-box">
            <div class="circle-outer"></div>
            <div class="circle-inner"></div>
        </div>
        <div class="status-tag" id="status-text">Cargando Pyodide...</div>
    </div>

    <!-- Contenedor de la app Streamlit -->
    <div id="root"></div>

    <!-- JS de stlite -->
    <script type="module">
        import {{ mount }} from "https://cdn.jsdelivr.net/npm/@stlite/browser@0.85.1/build/stlite.js";
        
        const appCode = {app_code_json};
        
        const statusText = document.getElementById("status-text");
        
        setTimeout(() => {{
            statusText.innerText = "Descargando Pandas y Plotly...";
        }}, 3000);
        
        setTimeout(() => {{
            statusText.innerText = "Inicializando Streamlit en navegador...";
        }}, 6000);

        mount(
            {{
                entrypoint: "app.py",
                files: {{
                    "app.py": appCode
                }},
                requirements: ["pandas", "openpyxl", "plotly", "requests", "pyodide-http"]
            }},
            document.getElementById("root")
        ).then(() => {{
            // Ocultar pantalla de carga y mostrar la app
            const loader = document.getElementById("loading-container");
            loader.style.opacity = 0;
            setTimeout(() => {{
                loader.style.display = "none";
                const rootApp = document.getElementById("root");
                rootApp.style.display = "block";
            }}, 500);
        }}).catch((err) => {{
            console.error(err);
            const statusText = document.getElementById("status-text");
            statusText.innerText = "Error de Carga: " + err.message;
            statusText.style.color = "#ff3333";
            statusText.style.boxShadow = "0 0 15px rgba(255, 51, 51, 0.4)";
            statusText.style.background = "rgba(255, 51, 51, 0.1)";
        }});
    </script>
</body>
</html>
"""

    print(f"Escribiendo {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("¡Construcción finalizada con éxito! index.html generado listo para subir a GitHub Pages.")

if __name__ == "__main__":
    build_static_site()
