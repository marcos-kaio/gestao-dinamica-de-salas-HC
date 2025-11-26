from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict

from app.database import engine, Base, get_db
from app.models import Sala, Grade, Alocacao
from app.services.importer import importar_salas_csv, importar_grades_csv
from app.core.optimizer import gerar_alocacao_grade, calcular_afinidade_tempo_real, descobrir_andar_predominante
from app.core.time import sincronizar_status_com_alocacao, determinar_periodo_atual

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

class CheckInRequest(BaseModel):
    medico_nome: str

class AutoCheckInRequest(BaseModel):
    medico_nome: str
    especialidade: str

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
def trigger_alocacao_inteligente(teste_dia: str = None, teste_turno: str = None, db: Session = Depends(get_db)):
    """
    Executa o algoritmo que cruza Demanda (Grades) x Oferta (Salas).
    Retorna quem ficou onde e quem ficou sem sala.
    """
    resultado = gerar_alocacao_grade(db)
    
    qtd_ocupadas, dia_usado, turno_usado = sincronizar_status_com_alocacao(db, forcar_dia=teste_dia, forcar_turno=teste_turno)
    return {
        "status": "Processamento concluído",
        "modo": "TESTE MANUAL" if teste_dia else "TEMPO REAL AUTOMÁTICO",
        "contexto_usado": f"{dia_usado} - {turno_usado}",
        "salas_ocupadas_agora": qtd_ocupadas,
        "total_alocados_semana": len(resultado["alocacoes_detalhadas"]),
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

# Rota para realizar CHECK-IN MANUAL (Ocupar a sala)
@app.post("/api/salas/{sala_id}/checkin")
def realizar_checkin(sala_id: str, dados: CheckInRequest, db: Session = Depends(get_db)):
    sala = db.query(Sala).filter(Sala.id == sala_id).first()

    if not sala:
        raise HTTPException(status_code = 404, detail="Sala não encontrada")
    
    if sala.status_atual == "OCUPADA":
        raise HTTPException(status_code = 400, detail = f"Sala já ocupada por {sala.ocupante_atual}")
    
    if sala.is_maintenance:
        raise HTTPException(status_code = 400, detail = "Esta sala está em manutenção")

    sala.status_atual = "OCUPADA"
    sala.ocupante_atual = dados.medico_nome
    sala.horario_entrada = datetime.now().strftime("%H:%M") # Pega a hora atual do servidor

    db.commit() # Salva no banco de dados
    db.refresh(sala)

    return {"message": f"Check-in realizado com sucesso para {dados.medico_nome}", "sala": sala}

@app.post("/api/salas/checkin/inteligente")
def checkin_semiautomatico(dados: AutoCheckInRequest, db: Session = Depends(get_db)):
    andar_predominante, num_ideal = descobrir_andar_predominante(db, dados.especialidade)
    print(f"DEBUG: Especialidade {dados.especialidade} prefere o andar {andar_predominante}, perto da sala {num_ideal}")

    salas_disponiveis = db.query(Sala).filter(
        Sala.status_atual == "LIVRE",
        Sala.is_maintenance == False
    ).all()

    if not salas_disponiveis:
        raise HTTPException(status_code=404, detail="Não há nenhuma sala livre no momento.")
    

    melhor_sala = None
    maior_score = -999

    for sala in salas_disponiveis:
        score = calcular_afinidade_tempo_real(sala, dados.especialidade, andar_predominante, num_ideal)
        
        if score > maior_score:
            maior_score = score
            melhor_sala = sala
        elif score == maior_score:

            pass

    # Se todas as salas disponíveis forem de outras especialidades (score 0),
    # ainda assim pegamos a primeira que estiver livre (Melhor ter sala ruim que nenhuma)
    if not melhor_sala:
        melhor_sala = salas_disponiveis[0]


    melhor_sala.status_atual = "OCUPADA"
    melhor_sala.ocupante_atual = dados.medico_nome
    melhor_sala.horario_entrada = datetime.now().strftime("%H:%M")
    
    db.commit()
    db.refresh(melhor_sala)

    return {
        "mensagem": "Check-in automático realizado com sucesso!",
        "analise_logistica": f"Preferência de andar identificada: {andar_predominante}, perto da sala {int(num_ideal)}",
        "medico": dados.medico_nome,
        "sala_alocada": {
            "id": melhor_sala.id,
            "numero": melhor_sala.nome_visual,
            "andar": melhor_sala.andar,
            "especialidade_sala": melhor_sala.especialidade_preferencial
        },
        "score_afinidade": maior_score
    }

# Rota para realizar CHECK-OUT(desocupar sala)
@app.post("/api/salas/{sala_id}/checkout")  
def realizar_checkout(sala_id: str, db: Session = Depends(get_db)):
    sala = db.query(Sala).filter(Sala.id == sala_id).first()

    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
        
    if sala.status_atual == "LIVRE":
        return {"message": "Sala já está livre"}

    # Lógica de liberar sala
    medico_anterior = sala.ocupante_atual
    sala.status_atual = "LIVRE"
    sala.ocupante_atual = None
    sala.horario_entrada = None

    db.commit()

    return {"message": f"Check-out realizado. Sala liberada por {medico_anterior}."}  

# Visualização dos dados
@app.get("/api/salas")
def listar_salas(db: Session = Depends(get_db)):
    return db.query(Sala).all()

@app.get("/api/salas/ociosas")
def listar_salas_ociosas(db: Session = Depends(get_db)):
    # retorna só as salas livres
    salas_livres = db.query(Sala).filter(
        Sala.status_atual == "LIVRE",
        Sala.is_maintenance == False
    ).all()

    return {
        "total_livres": len(salas_livres),
        "salas": salas_livres
    }
    # Se o médico agendado chegar e encontrar alguém na sala que ele deveria ocupar, ele vai encontrar a mensagem de erro:
    # Sala ocupada por {residente}. Dessa forma, ele deverá ocupar outra sala utilizando o listar_salas_ociosas

@app.get("/api/grades")
def listar_demanda(db: Session = Depends(get_db)):
    return db.query(Grade).all()

@app.get("/api/alocacoes")
def listar_alocacoes_finais(db: Session = Depends(get_db)):
    """Retorna a grade final montada (Sala + Médico + Horário)"""
    alocacoes = db.query(Alocacao).all()
    return alocacoes

@app.get("/api/mapa-especialidades")
def listar_especialidades_das_salas(db: Session = Depends(get_db)):

    dados = db.query(Sala.id, Sala.especialidade_preferencial).all()

    mapa = defaultdict(list)

    for sala_id, especialidade in dados:
        chave = especialidade.strip() if especialidade and especialidade.strip() else "SEM_PREFERENCIA"
        
        mapa[chave].append(sala_id)

    return dict(sorted(mapa.items()))