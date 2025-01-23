import base64
from bs4 import BeautifulSoup
from PIL import Image
import io
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import tempfile
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import FileResponse

class OptimizationResponse(BaseModel):
    tamaño_original: float
    tamaño_final: float
    porcentaje_reducido: float
    tiempo_ejecucion_app: float
    imagenes_procesadas: int
    imagenes_optimizadas: int
    html_plano_optimizado: str

def optimize_single_image(args):
    """
    Optimiza una sola imagen - función para procesamiento paralelo
    """
    img_tag, quality = args
    src = img_tag.get('src', '')
    
    if src.startswith('data:image'):
        try:
            match = re.match(r'data:image/([a-zA-Z+]+);base64,(.+)', src)
            if match:
                image_type, base64_data = match.groups()
                original_size = len(base64_data)
                
                # Decodificar y procesar imagen
                image_data = base64.b64decode(base64_data)
                img = Image.open(io.BytesIO(image_data))
                
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensionar si es necesario
                max_size = (800, 800)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Optimizar
                output = io.BytesIO()
                img.save(output, format='JPEG', optimize=True, quality=quality)
                optimized_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
                
                return {
                    'tag': img_tag,
                    'new_src': f"data:image/jpeg;base64,{optimized_base64}",
                    'original_size': original_size,
                    'optimized_size': len(optimized_base64),
                    'success': True
                }
        except Exception as e:
            return {
                'tag': img_tag,
                'error': str(e),
                'success': False
            }
    
    return {'tag': img_tag, 'success': False}

def optimize_html_images(content: str, quality: int = 85) -> tuple[str, dict]:
    """
    Optimiza las imágenes en el contenido HTML usando procesamiento paralelo
    """
    start_time = time.time()
    
    soup = BeautifulSoup(content, 'html.parser')
    images = soup.find_all('img')
    
    if not images:
        return content, {
            'images_processed': 0,
            'images_optimized': 0,
            'execution_time': 0,
            'original_size': 0,
            'final_size': 0
        }
    
    # Procesar imágenes en paralelo
    with ThreadPoolExecutor(max_workers=min(len(images), os.cpu_count() * 2)) as executor:
        futures = [executor.submit(optimize_single_image, (img, quality)) for img in images]
        
        total_original_size = 0
        total_optimized_size = 0
        images_optimized = 0
        
        for future in as_completed(futures):
            result = future.result()
            if result['success']:
                # Actualizar la imagen en el HTML
                result['tag']['src'] = result['new_src']
                total_original_size += result['original_size']
                total_optimized_size += result['optimized_size']
                images_optimized += 1
    
    execution_time = time.time() - start_time
    
    stats = {
        'images_processed': len(images),
        'images_optimized': images_optimized,
        'execution_time': execution_time,
        'original_size': total_original_size,
        'final_size': total_optimized_size
    }
    
    return str(soup), stats

# Crear la aplicación FastAPI
app = FastAPI(title="Optimizador de Imágenes HTML",
             description="API para optimizar imágenes base64 en archivos HTML")

@app.get("/")
async def root():
    return {"message": "API para optimizar imágenes base64 en archivos HTML"}

@app.post("/optimize/text/plane", response_model=OptimizationResponse)
async def optimize_file(file: UploadFile = File(...), quality: Optional[int] = 85):
    """
    Optimiza las imágenes de un archivo HTML
    """
    if not file.filename.endswith('.html'):
        raise HTTPException(400, detail="Solo se permiten archivos HTML")
    
    try:
        content = await file.read()
        content = content.decode('utf-8')
        
        # Optimizar contenido
        optimized_content, stats = optimize_html_images(content, quality)
        
        # Preparar respuesta
        original_size = stats['original_size'] / (1024 * 1024)  # Convertir a MB
        final_size = stats['final_size'] / (1024 * 1024)  # Convertir a MB
        reduction = ((stats['original_size'] - stats['final_size']) / stats['original_size']) * 100 if stats['original_size'] > 0 else 0
        
        return OptimizationResponse(
            tamaño_original=str(round(original_size, 2)),
            tamaño_final=str(round(final_size, 2)),
            porcentaje_reducido=str(round(reduction, 2)),
            tiempo_ejecucion_app=str(round(stats['execution_time'], 2)),
            imagenes_procesadas=stats['images_processed'],
            imagenes_optimizadas=stats['images_optimized'],
            html_plano_optimizado=optimized_content  
        )
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/optimize/file/download")
async def optimize_file_download(file: UploadFile = File(...), quality: Optional[int] = 85):
    """
    Optimiza las imágenes y devuelve el archivo HTML optimizado para descargar
    """
    if not file.filename.endswith('.html'):
        raise HTTPException(400, detail="Solo se permiten archivos HTML")
    
    try:
        content = await file.read()
        content = content.decode('utf-8')
        
        # Optimizar contenido
        optimized_content, stats = optimize_html_images(content, quality)
        
        # Crear archivo temporal para la respuesta
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmp:
            tmp.write(optimized_content)
            output_path = tmp.name
        
        # Preparar estadísticas
        original_size = stats['original_size'] / (1024 * 1024)
        final_size = stats['final_size'] / (1024 * 1024)
        reduction = ((stats['original_size'] - stats['final_size']) / stats['original_size']) * 100 if stats['original_size'] > 0 else 0
        
        # Generar nombre del archivo optimizado
        output_filename = f"optimized_{file.filename}"
        
        # Devolver el archivo y las estadísticas como headers
        response = FileResponse(
            output_path,
            media_type='text/html',
            filename=output_filename
        )
        
        # Agregar estadísticas como headers personalizados
        response.headers["X-Original-Size-MB"] = str(round(original_size, 2))
        response.headers["X-Final-Size-MB"] = str(round(final_size, 2))
        response.headers["X-Reduction-Percentage"] = str(round(reduction, 2))
        response.headers["X-Images-Processed"] = str(stats['images_processed'])
        response.headers["X-Images-Optimized"] = str(stats['images_optimized'])
        response.headers["X-Execution-Time"] = str(round(stats['execution_time'], 2))
        
        return response
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)