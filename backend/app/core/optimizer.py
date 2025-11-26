from sqlalchemy.orm import Session
from app.models import Sala, Grade, Alocacao
from collections import defaultdict, Counter
import re, statistics

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
    
def extrair_numero_sala(nome_visual: str) -> int:
    """
    Transforma 'E3-40' em 40.
    Lógica: Pega o ÚLTIMO grupo numérico encontrado na string.
    """
    numeros = re.findall(r'\d+', str(nome_visual))
    
    if numeros:
        return int(numeros[-1])
        
    return -1

def descobrir_andar_predominante(db: Session, especialidade: str):
    if not especialidade: return None, None

    salas_da_esp = db.query(Sala).filter(
        Sala.especialidade_preferencial.ilike(f"%{especialidade}%")
    ).all()
    
    if not salas_da_esp:
        return None, None
    
    lista_andares = [s.andar for s in salas_da_esp]
    andar_predominante = Counter(lista_andares).most_common(1)[0][0]
    
    numeros_salas = []
    for s in salas_da_esp:
        if s.andar == andar_predominante:
            num = extrair_numero_sala(s.nome_visual)
            if num > 0:
                numeros_salas.append(num)
                
    numero_alvo = statistics.median(numeros_salas) if numeros_salas else 0
    
    return andar_predominante, numero_alvo

def calcular_afinidade_tempo_real(sala: Sala, especialidade_medico: str, andar_alvo: str, num_alvo: float) -> float:
    """
    Retorna uma pontuação de quão boa é a sala para essa especialidade.
    """
    esp_medico = especialidade_medico.lower().strip()
    score = 0

    if not sala.especialidade_preferencial:
        score += 10
    
    esp_sala = sala.especialidade_preferencial.lower().strip()

    if esp_medico in esp_sala or esp_sala in esp_medico:
        score += 100

    if andar_alvo:
        if str(sala.andar).strip() == str(andar_alvo).strip():
            score += 30  # Bônus logístico (Desempate)
            if num_alvo and num_alvo > 0:
                num_sala = extrair_numero_sala(sala.nome_visual)

                if num_sala > 0:
                    distancia = abs(num_alvo - num_sala)
                    penalidade = distancia * 0.5
                    score -= penalidade

    return round(score, 1)