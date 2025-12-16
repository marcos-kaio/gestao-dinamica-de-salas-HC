from sqlalchemy.orm import Session
from app.models import Sala, Grade, Alocacao
from datetime import datetime

def determinar_periodo_atual():
    agora = datetime.now()
    dias_map = {0: "SEG", 1: "TER", 2: "QUA", 3: "QUI", 4: "SEX", 5: "SAB", 6: "DOM"}
    dia_atual = dias_map.get(agora.weekday(), "SEG")

    hora = agora.hour
    if 6 <= hora < 13:
        turno_atual = "MANHA"
    elif 13 <= hora < 19:
        turno_atual = "TARDE"
    else:
        turno_atual = "NOITE"
        
    print(f" [SISTEMA] Horário: {agora} | Dia: {dia_atual} | Turno: {turno_atual}")
    return dia_atual, turno_atual

def sincronizar_status_com_alocacao(db: Session, forcar_dia: str = None, forcar_turno: str = None):
    dia, turno = determinar_periodo_atual()
    if forcar_dia: dia = forcar_dia
    if forcar_turno: turno = forcar_turno

    # Busca alocações do momento
    alocacoes = db.query(Alocacao).filter(
        Alocacao.dia_semana == dia,
        Alocacao.turno == turno
    ).all()
    
    mapa_reservas = {a.sala_id: a.grade_id for a in alocacoes}
    salas = db.query(Sala).all()
    count_ocupadas = 0
    agora_str = datetime.now().strftime("%H:%M")

    for s in salas:
        if s.is_maintenance: continue
        
        grade_id = mapa_reservas.get(s.id)
        if grade_id:
            # Sala alocada!
            grade = db.query(Grade).filter(Grade.id == grade_id).first()
            if grade:
                s.status_atual = "OCUPADA"
                # Grava Nome (Especialidade) para o Monitoramento
                s.ocupante_atual = f"{grade.nome_profissional} ({grade.especialidade})"
                # IMPORTANTE: A especialidade ativa da sala passa a ser a do médico
                s.especialidade_atual = grade.especialidade
                
                if not s.horario_entrada:
                    s.horario_entrada = agora_str
                count_ocupadas += 1
        else:
            # Sala Livre
            # Se estava ocupada por alocação automática, limpa.
            # (Mantém se tiver lógica de check-in manual persistente, mas aqui resetamos para refletir o turno)
            if s.status_atual == "OCUPADA":
                 s.status_atual = "LIVRE"
                 s.ocupante_atual = None
                 s.especialidade_atual = None # Volta a ser "genérica" ou do CSV
                 s.horario_entrada = None

    db.commit()
    return count_ocupadas, dia, turno