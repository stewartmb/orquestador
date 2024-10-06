#uvicorn app:app --reload
from fastapi import FastAPI,HTTPException
import httpx

app = FastAPI()

# URLs de los otros microservicios
JAVA_MICRO_URL = 'http://java-microservice:8011'
PYTHON_MICRO_URL = 'http://api-micro2:8012'
NODE_MICRO_URL = 'http://api-micro3:8013'

@app.get("/orquestador/inscripciones")
async def get_inscripciones():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{JAVA_MICRO_URL}/inscripciones")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error al obtener las inscripciones")
        return response.json()

# Orquestador que consulta todos los estudiantes desde el microservicio Java
@app.get("/orquestador/estudiantes")
async def get_estudiantes():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{JAVA_MICRO_URL}/estudiantes")
        return response.json()

# Orquestador que consulta todos los cursos desde el microservicio Python
@app.get("/orquestador/cursos")
async def get_cursos():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PYTHON_MICRO_URL}/cursos")
        return response.json()

# Orquestador que consulta todos los espacios desde el microservicio Node.js
@app.get("/orquestador/espacios")
async def get_espacios():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{NODE_MICRO_URL}/espacios")
        return response.json()

# Orquestador que consulta todos los espacios desde el microservicio Node.js
@app.get("/orquestador/espacios")
async def get_espacios():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{NODE_MICRO_URL}/espacios")
        return response.json()

# Obtener los cursos que lleva un estudiante, con detalles de los profesores y nombres de cursos
@app.get("/estudiante/{codigo}/cursos")
async def get_cursos_por_estudiante(codigo: str):
    async with httpx.AsyncClient() as client:
        try:
            # 1. Verificar si el estudiante existe en la API de Estudiantes
            estudiante_res = await client.get(f"{JAVA_MICRO_URL}/estudiantes/{codigo}")
            if estudiante_res.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Estudiante con código {codigo} no encontrado")
            estudiante = estudiante_res.json()
            print(f"Estudiante encontrado: {estudiante}")

            # 2. Obtener inscripciones de la API de Inscripciones
            inscripciones_res = await client.get(f"{JAVA_MICRO_URL}/inscripciones/estudiante/{codigo}")
            if inscripciones_res.status_code != 200:
                raise HTTPException(status_code=404, detail=f"No se encontraron inscripciones para el estudiante con código {codigo}")
            inscripciones = inscripciones_res.json()
            print(f"Inscripciones encontradas: {inscripciones}")

            # 3. Verificar si hay inscripciones
            if not inscripciones:
                raise HTTPException(status_code=404, detail=f"No se encontraron inscripciones para el estudiante con código {codigo}")

            # 4. Recorrer las inscripciones y obtener detalles del curso y profesor para cada inscripción
            cursos_detalles = []
            for inscripcion in inscripciones:
                id_curso = inscripcion["idCurso"]
                
                # Obtener detalles del curso (idCurso e idProfesor)
                curso_res = await client.get(f"{PYTHON_MICRO_URL}/cursos/{id_curso}/version2")
                if curso_res.status_code == 200:
                    curso_info = curso_res.json()
                    id_profesor = curso_info["idProfesor"]
                    
                    # Obtener detalles del curso y profesor
                    curso_nombre_res = await client.get(f"{PYTHON_MICRO_URL}/cursos/{id_curso}")
                    profesor_res = await client.get(f"{PYTHON_MICRO_URL}/profesores/{id_profesor}")

                    if curso_nombre_res.status_code == 200 and profesor_res.status_code == 200:
                        nombre_curso = curso_nombre_res.json()["Curso"][1]  # Obtener el nombre del curso
                        nombre_profesor = profesor_res.json()["Profesor"][1]  # Obtener el nombre del profesor
                        cursos_detalles.append({
                            "idCurso": curso_info["idCurso"],
                            "nombreCurso": nombre_curso,
                            "idProfesor": curso_info["idProfesor"],
                            "nombreProfesor": nombre_profesor
                        })
                    else:
                        cursos_detalles.append({
                            "idCurso": id_curso,
                            "error": "Error obteniendo detalles de curso o profesor"
                        })
                else:
                    print(f"No se encontró el curso con id {id_curso}")
                    cursos_detalles.append({
                        "idCurso": id_curso,
                        "error": f"Curso con id {id_curso} no encontrado"
                    })

            # 5. Devolver la lista de cursos con los profesores
            return {
                "codigoEstudiante": codigo,
                "nombre": estudiante["nombre"],
                "apellido": estudiante["apellido"],
                "cursos": cursos_detalles
            }
        
        except httpx.RequestError as exc:
            # Capturamos cualquier error relacionado con la solicitud HTTP
            raise HTTPException(status_code=500, detail=f"Error de conexión con los microservicios: {exc}")
        
        except Exception as e:
            # Capturamos cualquier otro tipo de error
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


# Ejecutar el servidor FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
