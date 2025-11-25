from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import engine, Base, get_db
from app.models import Sala, Grade, Alocacao
from app.services.importer import importar_salas_csv, importar_grades_csv
from app.core.optimizer import gerar_alocacao_grade

# Inicializa o Banco de Dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GDS - Gestão Dinâmica de Salas")

# Configuração de CORS
origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de Entrada
class NovaDemanda(BaseModel):
    medico_nome: str
    especialidade: str
    dia_semana: str
    turno: str
    tipo_recurso: str = "EXTRA"

@app.get("/")
def read_root():
    return {"message": "API GDS Online", "status": "OK", "mode": "Grade Semanal"}

# Importação dos dados
@app.post("/api/setup/importar-salas")
def trigger_import_salas():
    """Lê o CSV de infraestrutura física e popula o banco"""
    return importar_salas_csv()

@app.post("/api/setup/importar-grades")
def trigger_import_grades():
    """Lê o CSV de grades médicas (AGHU) e popula o banco"""
    return importar_grades_csv()

# Motor de alocação
@app.post("/api/alocacao/gerar")
def trigger_alocacao_inteligente(db: Session = Depends(get_db)):
    """
    Executa o algoritmo que cruza Demanda (Grades) x Oferta (Salas).
    Retorna quem ficou onde e quem ficou sem sala.
    """
    resultado = gerar_alocacao_grade(db)
    
    return {
        "status": "Processamento concluído",
        "total_alocados": len(resultado["alocacoes_detalhadas"]), 
        "total_conflitos": len(resultado["conflitos"]),
        "resumo_executivo": resultado["resumo_ambulatorios"],
        "detalhes": resultado
    }

@app.post("/api/grade/adicionar")
def adicionar_demanda_manual(demanda: NovaDemanda, db: Session = Depends(get_db)):
    """
    Permite ao Gestor adicionar um recurso extra na grade
    (Ex: Um residente que chegou de última hora).
    """
    nova_grade = Grade(
        nome_profissional=demanda.medico_nome,
        especialidade=demanda.especialidade,
        dia_semana=demanda.dia_semana,
        turno=demanda.turno,
        tipo_recurso=demanda.tipo_recurso,
        origem="GESTOR"
    )
    db.add(nova_grade)
    db.commit()
    return {"message": "Demanda adicionada à grade com sucesso! Rode a alocação novamente para incluí-lo."}

# Visualização dos dados
@app.get("/api/salas")
def listar_salas(db: Session = Depends(get_db)):
    return db.query(Sala).all()

@app.get("/api/grades")
def listar_demanda(db: Session = Depends(get_db)):
    return db.query(Grade).all()

@app.get("/api/alocacoes")
def listar_alocacoes_finais(db: Session = Depends(get_db)):
    """Retorna a grade final montada (Sala + Médico + Horário)"""
    alocacoes = db.query(Alocacao).all()
    return alocacoes