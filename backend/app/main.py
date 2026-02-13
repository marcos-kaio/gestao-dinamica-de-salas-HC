from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from contextlib import asynccontextmanager
import shutil
import os
from datetime import timedelta

from app.database import engine, Base, get_db, SessionLocal
from app.models import Sala, Grade, Alocacao, Especialidade
from app.services.importer import importar_salas_csv, importar_grades_csv
from app.core.optimizer import (
    gerar_alocacao_grade, 
    obter_resumo_atual, 
    listar_opcoes_troca, 
    aplicar_troca_manual,
    obter_dashboard_tempo_real
)
from app.core.time import get_horario_atual
from app.core.security import create_access_token, get_current_user
from app.core.config import settings

Base.metadata.create_all(bind=engine)

# --- LÓGICA DE AUTO-SEED ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        # Verifica se já existem salas
        count = db.query(Sala).count()
        if count == 0:
            importar_salas_csv() # Popula salas
            print("--- AUTO-SEED CONCLUÍDO ---")
    except Exception as e:
        print(f"Erro no Auto-Seed: {e}")
    finally:
        db.close()
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos ---
class NovaDemanda(BaseModel):
    medico_nome: str
    especialidade: str
    dia_semana: str
    turno: str
    tipo_recurso: str = "EXTRA"

class TrocaSalaRequest(BaseModel):
    nova_sala_id: str
    forcar: bool = False

class SalaUpdate(BaseModel):
    is_maintenance: bool

class SalaCreate(BaseModel):
    bloco: str
    andar: str
    especialidade_preferencial: str = ""

class LoteSalasUpdate(BaseModel):
    bloco: str
    andar: str
    is_maintenance: bool

class CheckInRequest(BaseModel):
    medico_nome: str
    especialidade: str
    sala_id: str

# --- AUTHENTICATION ---
@app.post("/api/auth/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == settings.ADMIN_USERNAME and form_data.password == settings.ADMIN_PASSWORD:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "user": {"name": "Administrador", "role": "admin"}}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuário ou senha incorretos",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.get("/")
def read_root():
    return {"message": "API GDS Online", "status": "OK"}

# --- Setup ---
@app.post("/api/setup/importar-salas", dependencies=[Depends(get_current_user)])
def trigger_import_salas(): return importar_salas_csv()

@app.post("/api/setup/importar-grades", dependencies=[Depends(get_current_user)])
def trigger_import_grades_local(): return importar_grades_csv()

@app.post("/api/upload/grades", dependencies=[Depends(get_current_user)])
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
@app.post("/api/alocacao/gerar", dependencies=[Depends(get_current_user)])
def trigger_alocacao_inteligente(db: Session = Depends(get_db)):
    res = gerar_alocacao_grade(db)
    return {"status": "OK", "resumo_executivo": res["resumo_ambulatorios"]}

@app.get("/api/alocacao/resumo", dependencies=[Depends(get_current_user)])
def ler_alocacao_atual(db: Session = Depends(get_db)):
    return obter_resumo_atual(db)

@app.get("/api/dashboard/agora")
def ler_dashboard_tempo_real(db: Session = Depends(get_db)):
    return obter_dashboard_tempo_real(db)

# --- Salas (Protegido) ---
@app.get("/api/salas", dependencies=[Depends(get_current_user)])
def listar_salas(db: Session = Depends(get_db)): return db.query(Sala).all()

@app.post("/api/salas", dependencies=[Depends(get_current_user)])
def criar_sala_manual(dados: SalaCreate, db: Session = Depends(get_db)):
    """Cria uma nova sala gerando ID sequencial automaticamente"""
    # Busca salas existentes no setor para calcular sequência
    salas_setor = db.query(Sala).filter(
        Sala.bloco == dados.bloco,
        Sala.andar == dados.andar
    ).all()
    
    max_seq = 0
    for sala in salas_setor:
        try:
            # Tenta extrair numero final
            parts = sala.id.split('-')
            if len(parts) > 1:
                seq = int(parts[-1])
                if seq > max_seq: max_seq = seq
        except: continue
    next_seq = max_seq + 1
    new_id = f"{dados.bloco}{dados.andar}-{next_seq:02d}"
    
    if db.query(Sala).filter(Sala.id == new_id).first():
        # Fallback simples se houver conflito
        new_id = f"{dados.bloco}{dados.andar}-{next_seq+1:02d}"

    nova_sala = Sala(
        id=new_id,
        nome_visual=new_id,
        bloco=dados.bloco,
        andar=dados.andar,
        especialidade_preferencial=dados.especialidade_preferencial,
        features=[],
        is_maintenance=False
    )
    
    db.add(nova_sala)
    db.commit()
    return {"message": "Sala criada com sucesso", "sala": new_id}

@app.put("/api/salas/{sala_id}", dependencies=[Depends(get_current_user)])
def atualizar_status_sala(sala_id: str, dados: SalaUpdate, db: Session = Depends(get_db)):
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not sala: raise HTTPException(404, "Sala não encontrada")
    sala.is_maintenance = dados.is_maintenance
    db.commit()
    return {"message": "Status atualizado"}

@app.put("/api/salas/lote/update", dependencies=[Depends(get_current_user)])
def atualizar_salas_lote(dados: LoteSalasUpdate, db: Session = Depends(get_db)):
    salas = db.query(Sala).filter(Sala.bloco == dados.bloco, Sala.andar == dados.andar).all()
    if not salas: raise HTTPException(404, "Nenhuma sala encontrada")
    for s in salas: s.is_maintenance = dados.is_maintenance
    db.commit()
    return {"message": "Setor atualizado", "afetados": len(salas)}

@app.delete("/api/salas/{sala_id}", dependencies=[Depends(get_current_user)])
def excluir_sala(sala_id: str, db: Session = Depends(get_db)):
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not sala: raise HTTPException(404, "Sala não encontrada")
    db.query(Alocacao).filter(Alocacao.sala_id == sala_id).delete()
    db.delete(sala)
    db.commit()
    return {"message": "Removida"}

# --- Gestão Manual ---
@app.get("/api/alocacao/{alocacao_id}/opcoes", dependencies=[Depends(get_current_user)])
def obter_opcoes_troca(alocacao_id: int, db: Session = Depends(get_db)):
    return listar_opcoes_troca(alocacao_id, db)

@app.put("/api/alocacao/{alocacao_id}/trocar", dependencies=[Depends(get_current_user)])
def realizar_troca_manual(alocacao_id: int, req: TrocaSalaRequest, db: Session = Depends(get_db)):
    resultado = aplicar_troca_manual(alocacao_id, req.nova_sala_id, req.forcar, db)
    
    if resultado["sucesso"]:
        return {"message": "Troca realizada com sucesso"}
    
    if resultado.get("motivo") == "Sala ocupada":
        raise HTTPException(status_code=409, detail=f"Sala ocupada. Deseja forçar?")
        
    raise HTTPException(400, "Erro desconhecido na troca")

@app.post("/api/grade/adicionar", dependencies=[Depends(get_current_user)])
def adicionar_demanda_manual(demanda: NovaDemanda, db: Session = Depends(get_db)):
    db.add(Grade(
        nome_profissional=demanda.medico_nome,
        especialidade=demanda.especialidade,
        dia_semana=demanda.dia_semana,
        turno=demanda.turno,
        tipo_recurso=demanda.tipo_recurso,
        origem="GESTOR"
    ))
    db.commit()
    return {"message": "OK"}

# --- CHECK-IN / CHECK-OUT REAL ---

@app.post("/api/checkin")
def realizar_checkin(dados: CheckInRequest, db: Session = Depends(get_db)):
    tempo = get_horario_atual()
    dia = tempo['dia']
    turno = tempo['turno']
    
    if not turno:
        raise HTTPException(400, "Fora do horário de funcionamento")

    # Verifica se já está ocupada AGORA
    ocupada = db.query(Alocacao).filter(
        Alocacao.sala_id == dados.sala_id,
        Alocacao.dia_semana == dia,
        Alocacao.turno == turno
    ).first()
    
    if ocupada:
        raise HTTPException(409, "Sala já ocupada neste turno")

    # Cria Grade Temporária para o Check-in
    nova_grade = Grade(
        nome_profissional=dados.medico_nome,
        especialidade=dados.especialidade,
        dia_semana=dia,
        turno=turno,
        tipo_recurso="CHECKIN_APP",
        origem="PORTAL_MEDICO"
    )
    db.add(nova_grade)
    db.commit()
    
    # Cria Alocação Efetiva
    nova_alocacao = Alocacao(
        sala_id=dados.sala_id,
        grade_id=nova_grade.id,
        dia_semana=dia,
        turno=turno,
        score=2000 
    )
    db.add(nova_alocacao)
    db.commit()
    
    return {"message": "Check-in realizado com sucesso", "alocacao_id": nova_alocacao.id}

@app.post("/api/checkout/{sala_id}")
def realizar_checkout(sala_id: str, db: Session = Depends(get_db)):
    tempo = get_horario_atual()
    dia = tempo['dia']
    turno = tempo['turno']
    
    # Remove alocação ativa neste turno/dia
    alocacao = db.query(Alocacao).filter(
        Alocacao.sala_id == sala_id, Alocacao.dia_semana == dia, Alocacao.turno == turno
    ).first()
    
    if not alocacao:
        # Tenta achar grade criada pelo portal para limpar
        raise HTTPException(404, "Nenhuma alocação ativa encontrada para liberar agora.")
        
    db.delete(alocacao)
    db.commit()
    return {"message": "Sala liberada com sucesso"}

@app.get("/api/alocacoes", dependencies=[Depends(get_current_user)])
def listar_alocacoes_finais(db: Session = Depends(get_db)): return db.query(Alocacao).all()