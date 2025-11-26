from sqlalchemy.orm import Session
from app.models import Sala, Grade, Alocacao
from datetime import datetime

# Função para conseguir o tempo atual
def determinar_periodo_atual():
    """
    Função auxiliar para descobrir o dia e turno atual.
    Retorna (dia_semana, turno). Ex: ("SEG", "MANHA")
    """
    agora = datetime.now()
    
    #mapeamento dos dias
    dias_map = {0: "SEG", 1: "TER", 2: "QUA", 3: "QUI", 4: "SEX", 5: "SAB", 6: "DOM"}
    dia_atual = dias_map.get(agora.weekday(), "SEG")

    hora = agora.hour
    if 6 <= hora < 13:
        turno_atual = "MANHA"
    elif 13 <= hora < 19:
        turno_atual = "TARDE"
    else:
        turno_atual = "NOITE"
        
    print(f" [SISTEMA] Horário Detectado: {agora} | Dia: {dia_atual} | Turno: {turno_atual}")
    return dia_atual, turno_atual

def sincronizar_status_com_alocacao(db: Session, forcar_dia: str = None, forcar_turno: str = None):
    """
    Pega as alocações planejadas e aplica no status real das salas.
    """

    dia, turno = determinar_periodo_atual()

    if forcar_dia: dia = forcar_dia
    if forcar_turno: turno = forcar_turno

    print(f"--- Sincronizando Realidade para: {dia} - {turno} ---")


    salas = db.query(Sala).all()
    for s in salas:
        if not s.is_maintenance:
            s.status_atual = "LIVRE"
            s.ocupante_atual = None
            s.horario_entrada = None

    alocacoes_do_momento = db.query(Alocacao).filter(
        Alocacao.dia_semana == dia,
        Alocacao.turno == turno
    ).all()

    count_ocupadas = 0
    for aloc in alocacoes_do_momento:
        sala = db.query(Sala).filter(Sala.id == aloc.sala_id).first()
        if sala and not sala.is_maintenance:
            # Busca o nome do médico na tabela Grade para preencher
            grade = db.query(Grade).filter(Grade.id == aloc.grade_id).first()
            nome_medico = grade.nome_profissional if grade else "Alocação Automática"

            sala.status_atual = "OCUPADA"
            sala.ocupante_atual = nome_medico
            sala.horario_entrada = datetime.now().strftime("%H:%M")
            count_ocupadas += 1

    db.commit()
    return count_ocupadas, dia, turno

