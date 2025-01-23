# API para optimizar imágenes base64 en archivos HTML

## Endpoints
- **BASE_URL** = "http://127.0.0.1:8000" #entorno local

### BASE_URL/optimize/text/plane - API
- **Método:** POST

- **Status** Ready 💪😎
- **FormData Multipart REQUEST:**
    FormData Multipart
    body: ("file": "reporte_pesado.html")

- **Body (JSON) RESPONSE:**
    Te devuelve stats de la optimizacion y el contenido en texto plano del reporte html, por lo que se tendria que hacer el proceso de guardarlo como un archivo .html
    ```json
    {
        "tamaño_original": 138.93,
        "tamaño_final": 0.84,
        "porcentaje_reducido": 99.4,
        "tiempo_ejecucion_app": 2.05,
        "imagenes_procesadas": 24,
        "imagenes_optimizadas": 20,
        "html_plano_optimizado": "\n<html>\n<head>\n<title>ReportedeErrores</title>\n<style>\r\nbody{font-family:Arial,sans-serif...";
    }
    ```
### BASE_URL/optimize/file/download - API
- **Método:** POST
- **Status** Ready 💪😎
- **FormData Multipart REQUEST:**
    FormData Multipart
    body: ("file": "reporte_pesado.html")

- **Body (JSON) RESPONSE:**
    Te devuelve con el archivo .html para su descarga
    ```json
    {
        "optimized_html": "\n<html>\n<head>\n<title>ReportedeErrores</title>\n<style>\r\nbody{font-family:Arial,sans-serif...";
    }
    ```