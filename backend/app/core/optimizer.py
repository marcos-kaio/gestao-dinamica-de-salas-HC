from sqlalchemy.orm import Session
from app.models import Sala, Grade, Alocacao
from collections import defaultdict
import re

def calcular_score(grade: Grade, sala: Sala) -> int:
    if sala.is_maintenance: return -10000
    
    score = 0
    
    sala_esp = str(sala.especialidade_preferencial).lower()
    grade_esp = str(grade.especialidade).lower()
    
    if sala_esp and grade_esp in sala_esp:
        score += 100
    
    if "ortopedia" in grade_esp:
        if str(sala.andar) == "0" or "térreo" in str(sala.andar).lower(): 
            score += 50
        else: 
            score -= 50
            
    return score

def natural_sort_key(s):
    """Função auxiliar para ordenar E2-1, E2-2, E2-10 corretamente"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def gerar_alocacao_grade(db: Session):
    db.query(Alocacao).delete()
    
    grades = db.query(Grade).all()
    salas = db.query(Sala).filter(Sala.is_maintenance == False).all()
    
    ocupacao = {
        d: {t: [] for t in ["MANHA", "TARDE"]} 
        for d in ["SEG", "TER", "QUA", "QUI", "SEX"]
    }
    
    resultado_detalhado = []
    conflitos = []

    for item_grade in grades:
        melhor_sala = None
        melhor_score = -9999
        
        for sala in salas:
            if sala.id in ocupacao.get(item_grade.dia_semana, {}).get(item_grade.turno, []):
                continue
                
            score = calcular_score(item_grade, sala)
            
            if score > melhor_score:
                melhor_score = score
                melhor_sala = sala
        
        if melhor_sala and melhor_score > -1000:
            nova_alocacao = Alocacao(
                sala_id=melhor_sala.id,
                grade_id=item_grade.id,
                dia_semana=item_grade.dia_semana,
                turno=item_grade.turno,
                score=melhor_score
            )
            db.add(nova_alocacao)
            
            if item_grade.dia_semana in ocupacao and item_grade.turno in ocupacao[item_grade.dia_semana]:
                ocupacao[item_grade.dia_semana][item_grade.turno].append(melhor_sala.id)
            
            resultado_detalhado.append({
                "medico": item_grade.nome_profissional,
                "especialidade": item_grade.especialidade,
                "sala": melhor_sala.nome_visual,
                "sala_id": melhor_sala.id,
                "bloco": melhor_sala.bloco,
                "andar": melhor_sala.andar,
                "dia": item_grade.dia_semana,
                "turno": item_grade.turno
            })
        else:
            conflitos.append({
                "medico": item_grade.nome_profissional,
                "especialidade": item_grade.especialidade,
                "motivo": "Sem sala disponível ou compatível"
            })
            
    db.commit()

    # Geração do resumo
    agrupamento = defaultdict(lambda: {"salas_unicas": set(), "locais": set()})

    for item in resultado_detalhado:
        esp = item['especialidade']
        agrupamento[esp]['salas_unicas'].add(item['sala'])
        local = f"Bloco {item['bloco']} - {item['andar']}"
        agrupamento[esp]['locais'].add(local)

    resumo_final = []
    for especialidade, dados in agrupamento.items():
        lista_salas = sorted(list(dados['salas_unicas']), key=natural_sort_key)
        
        resumo_final.append({
            "ambulatorio": especialidade,
            "total_salas": len(dados['salas_unicas']),
            "localizacao": list(dados['locais']),
            "lista_salas": lista_salas
        })

    resumo_final.sort(key=lambda x: x['total_salas'], reverse=True)

    return {
        "resumo_ambulatorios": resumo_final,
        "alocacoes_detalhadas": resultado_detalhado,
        "conflitos": conflitos
    }