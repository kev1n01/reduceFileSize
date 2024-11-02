# API para optimizar imágenes base64 en archivos HTML

## Endpoints
- **BASE_URL** = ""

### BASE_URL/optimize - API
- **Método:** POST

- **Status** Ready 💪😎
- **Body (JSON) REQUEST:**
    ```json
    {
      "file": "reporte.html",
    }
    ```
- **Body (JSON) RESPONSE:**
    Te devuelve stats de la optimizacion y el html en texto plano por lo que se tendria que hacer el proceso de guardar el archivo como .html
    ```json
    {
        "original_size": 138.93,
        "final_size": 0.83,
        "reduction_percentage": 99.40,
        "execution_time": 4.10,
        "images_processed": 24,
        "images_optimized": 20,
        "optimized_html": "\n<html>\n<head>\n<title>ReportedeErrores</title>\n<style>\r\nbody{font-family:Arial,sans-serif...";
    }
    ```
### BASE_URL/optimize/file - API
- **Método:** POST
- **Status** Ready 💪😎
- **Body (JSON) REQUEST:**
    ```json
    {
      "file": "reporte.html",
    }
    ```
- **Body (JSON) RESPONSE:**
    Te devuelve con el archivo .html
    ```json
    {
        "optimized_html": "\n<html>\n<head>\n<title>ReportedeErrores</title>\n<style>\r\nbody{font-family:Arial,sans-serif...";
    }
    ```