from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import shutil
import os

from app.database import engine, Base, get_db
from app.models import Sala, Grade, Alocacao, Especialidade
from app.services.importer import importar_salas_csv, importar_grades_csv
from app.core.optimizer import (
    gerar_alocacao_grade, 
    obter_resumo_atual, 
    listar_opcoes_troca, 
    aplicar_troca_manual,
    obter_dashboard_tempo_real # IMPORTANTE
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="GDS - Gestão Dinâmica de Salas")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NovaDemanda(BaseModel):
    medico_nome: str
    especialidade: str
    dia_semana: str
    turno: str
    tipo_recurso: str = "EXTRA"

class TrocaSalaRequest(BaseModel):
    nova_sala_id: str

@app.get("/")
def read_root():
    return {"message": "API GDS Online", "status": "OK"}

# --- Setup ---
@app.post("/api/setup/importar-salas")
def trigger_import_salas(): return importar_salas_csv()

@app.post("/api/setup/importar-grades")
def trigger_import_grades_local(): return importar_grades_csv()

@app.post("/api/upload/grades")
async def upload_grades_csv(file: UploadFile = File(...)):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "..", "data")
        os.makedirs(data_dir, exist_ok=True)
        file_location = os.path.join(data_dir, "grades.csv")
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        resultado = importar_grades_csv()
        return {"message": "Processado", "detalhes": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Core ---
@app.post("/api/alocacao/gerar")
def trigger_alocacao_inteligente(db: Session = Depends(get_db)):
    res = gerar_alocacao_grade(db)
    return {"status": "OK", "resumo_executivo": res["resumo_ambulatorios"]}

@app.get("/api/alocacao/resumo")
def ler_alocacao_atual(db: Session = Depends(get_db)):
    return obter_resumo_atual(db)

# --- Monitoramento Tempo Real ---
@app.get("/api/dashboard/agora")
def ler_dashboard_tempo_real(db: Session = Depends(get_db)):
    """Retorna o status das salas neste exato momento."""
    return obter_dashboard_tempo_real(db)

# --- Gestão Manual ---
@app.get("/api/alocacao/{alocacao_id}/opcoes")
def obter_opcoes_troca(alocacao_id: int, db: Session = Depends(get_db)):
    return listar_opcoes_troca(alocacao_id, db)

@app.put("/api/alocacao/{alocacao_id}/trocar")
def realizar_troca_manual(alocacao_id: int, req: TrocaSalaRequest, db: Session = Depends(get_db)):
    if aplicar_troca_manual(alocacao_id, req.nova_sala_id, db):
        return {"message": "Sucesso"}
    raise HTTPException(400, "Erro na troca")

@app.post("/api/grade/adicionar")
def adicionar_demanda_manual(demanda: NovaDemanda, db: Session = Depends(get_db)):
    db.add(Grade(nome_profissional=demanda.medico_nome, especialidade=demanda.especialidade, dia_semana=demanda.dia_semana, turno=demanda.turno, tipo_recurso=demanda.tipo_recurso, origem="GESTOR"))
    db.commit()
    return {"message": "OK"}

@app.get("/api/salas")
def listar_salas(db: Session = Depends(get_db)): return db.query(Sala).all()