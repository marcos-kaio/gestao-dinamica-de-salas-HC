from sqlalchemy.orm import Session
from app.models import Sala, Grade, Alocacao
from collections import defaultdict, Counter
import re, statistics

# --- Funções Auxiliares ---
def extrair_numero_sala(nome_visual: str) -> int:
    numeros = re.findall(r'\d+', str(nome_visual))
    if numeros: return int(numeros[-1])
    return -1

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

# --- Lógica de Alocação ---
def identificar_clusters_preferenciais(grades, salas):
    cluster_map = {}
    especialidades_oferta = set(
        s.especialidade_preferencial for s in salas 
        if s.especialidade_preferencial and "FECHADO" not in s.especialidade_preferencial
    )
    for esp in especialidades_oferta:
        salas_da_esp = [s for s in salas if s.especialidade_preferencial == esp]
        if not salas_da_esp: continue
        locais = [(s.bloco, s.andar) for s in salas_da_esp]
        if locais:
            melhor_loc = Counter(locais).most_common(1)[0][0]
            cluster_map[esp] = melhor_loc
    return cluster_map

def calcular_score(grade: Grade, sala: Sala, cluster_ideal: tuple = None) -> int:
    if sala.is_maintenance: return -999999
    
    score = 0
    sala_esp = sala.especialidade_preferencial
    grade_esp = grade.especialidade
    
    is_restricted = False
    if sala.features and isinstance(sala.features, list) and "RESTRICTED_SPECIALTY" in sala.features:
        is_restricted = True
    
    # 1. NAO MAPEADO (Penalidade)
    if grade_esp == "NAO MAPEADO":
        if sala_esp == "NAO MAPEADO": return 50
        return -800 
    
    # 2. SALA ESPECIALIZADA (Prioridade Máxima)
    if is_restricted:
        if sala_esp == grade_esp: return 10000 
        else: return -999999 
            
    # 3. MATCH DE NOME
    if sala_esp == grade_esp: score += 1000
    elif grade_esp in sala_esp: score += 800
    
    # 4. CLUSTER
    if cluster_ideal:
        bloco_ideal, andar_ideal = cluster_ideal
        if sala.bloco == bloco_ideal and str(sala.andar) == str(andar_ideal):
            score += 300
        elif sala.bloco == bloco_ideal:
            score += 100
    
    # 5. REGRAS FÍSICAS
    if "ORTOPEDIA" in grade_esp:
        if str(sala.andar) == "0": score += 2000
        else: score -= 2000
    if "OFTALMO" in grade_esp and "OFTALMO" not in sala_esp:
        score -= 5000 

    # 6. PENALIDADE DE INVASÃO
    if sala_esp != grade_esp and grade_esp not in sala_esp:
        score -= 200

    return score

def gerar_alocacao_grade(db: Session):
    db.query(Alocacao).delete()
    
    grades = db.query(Grade).all()
    # Carrega APENAS salas ativas
    salas = db.query(Sala).filter(Sala.is_maintenance == False).all()
    
    if not grades or not salas: return {"erro": "Sem dados"}
    
    # CONTADOR REAL DE SALAS ATIVAS (aprox 193)
    TOTAL_SALAS_FISICAS = len(salas)

    cluster_map = identificar_clusters_preferenciais(grades, salas)
    
    ocupacao = {
        d: {t: set() for t in ["MANHA", "TARDE", "NOITE"]} 
        for d in ["SEG", "TER", "QUA", "QUI", "SEX"]
    }
    
    resultado_detalhado = []
    conflitos = []

    def sort_priority(g):
        prio = 50
        if g.especialidade == "NAO MAPEADO": prio = 100
        elif "ORTOPEDIA" in g.especialidade: prio = 0
        elif "OFTALMO" in g.especialidade: prio = 1
        elif "GINECOLOGIA" in g.especialidade: prio = 2
        elif g.especialidade in cluster_map: prio = 10
        elif g.nome_profissional.startswith("Dr"): prio = 20
        return prio

    grades_ordenadas = sorted(grades, key=sort_priority)

    for item_grade in grades_ordenadas:
        dia = item_grade.dia_semana
        turno = item_grade.turno
        
        # --- TRAVA DE CAPACIDADE FÍSICA ---
        if dia in ocupacao and turno in ocupacao[dia]:
            # Se a lotação física for atingida, para imediatamente.
            if len(ocupacao[dia][turno]) >= TOTAL_SALAS_FISICAS:
                conflitos.append({
                    "medico": item_grade.nome_profissional,
                    "especialidade": item_grade.especialidade,
                    "motivo": "Lotação Máxima do Hospital Atingida"
                })
                continue

        melhor_sala = None
        melhor_score = -float('inf')
        cluster_alvo = cluster_map.get(item_grade.especialidade)
        
        for sala in salas:
            if dia not in ocupacao: continue
            if sala.id in ocupacao[dia][turno]: continue
                
            score = calcular_score(item_grade, sala, cluster_alvo)
            
            if score > melhor_score:
                melhor_score = score
                melhor_sala = sala
            elif score == melhor_score:
                if melhor_sala and sala.id < melhor_sala.id:
                    melhor_sala = sala
        
        limit_score = -500 
        
        if melhor_sala and melhor_score > limit_score:
            nova_alocacao = Alocacao(
                sala_id=melhor_sala.id,
                grade_id=item_grade.id,
                dia_semana=item_grade.dia_semana,
                turno=item_grade.turno,
                score=melhor_score
            )
            db.add(nova_alocacao)
            ocupacao[item_grade.dia_semana][item_grade.turno].add(melhor_sala.id)
            
            resultado_detalhado.append({
                "medico": item_grade.nome_profissional,
                "especialidade": item_grade.especialidade,
                "sala": melhor_sala.nome_visual,
                "bloco": melhor_sala.bloco,
                "andar": melhor_sala.andar,
                "dia": item_grade.dia_semana,
                "turno": item_grade.turno,
                "score": melhor_score
            })
        else:
            conflitos.append({
                "medico": item_grade.nome_profissional,
                "especialidade": item_grade.especialidade,
                "motivo": f"Sem sala compatível (Score: {melhor_score})"
            })
            
    db.commit()

    agrupamento = defaultdict(lambda: {"salas_unicas": set(), "locais": set(), "qtd_profissionais": 0})
    for item in resultado_detalhado:
        esp = item['especialidade']
        agrupamento[esp]['salas_unicas'].add(item['sala'])
        agrupamento[esp]['qtd_profissionais'] += 1
        local = f"Bloco {item['bloco']} - {item['andar']}º"
        agrupamento[esp]['locais'].add(local)

    resumo_final = []
    for especialidade, dados in agrupamento.items():
        lista_salas = sorted(list(dados['salas_unicas']), key=natural_sort_key)
        resumo_final.append({
            "ambulatorio": especialidade,
            "total_salas": len(dados['salas_unicas']),
            "total_profissionais": dados['qtd_profissionais'],
            "localizacao": sorted(list(dados['locais'])),
            "lista_salas": lista_salas
        })

    resumo_final.sort(key=lambda x: x['total_salas'], reverse=True)

    return {
        "resumo_ambulatorios": resumo_final,
        "alocacoes_detalhadas": resultado_detalhado,
        "conflitos": conflitos,
        "total_alocados": len(resultado_detalhado),
        "total_conflitos": len(conflitos)
    }

# (Funções de suporte)
def descobrir_andar_predominante(db: Session, especialidade: str):
    if not especialidade: return None, None
    term = especialidade.upper().strip()
    salas_da_esp = db.query(Sala).filter(Sala.especialidade_preferencial.contains(term)).all()
    if not salas_da_esp: return None, None
    lista_andares = [s.andar for s in salas_da_esp]
    if not lista_andares: return None, None
    andar_predominante = Counter(lista_andares).most_common(1)[0][0]
    return andar_predominante, 0

def calcular_afinidade_tempo_real(sala: Sala, especialidade_medico: str, andar_alvo: str, num_alvo: float) -> float:
    esp_medico = str(especialidade_medico).upper().strip()
    score = 0
    if not sala.especialidade_preferencial: score += 10
    esp_sala = str(sala.especialidade_preferencial)
    if esp_medico in esp_sala or esp_sala in esp_medico: score += 100
    if andar_alvo and str(sala.andar).strip() == str(andar_alvo).strip(): score += 30
    return round(score, 1)

def obter_resumo_atual(db: Session):
    alocacoes = db.query(Alocacao, Sala, Grade).join(Sala).join(Grade).all()
    resultado_detalhado = []
    for aloc, sala, grade in alocacoes:
        resultado_detalhado.append({
            "medico": grade.nome_profissional,
            "especialidade": grade.especialidade,
            "sala": sala.nome_visual,
            "bloco": sala.bloco,
            "andar": sala.andar,
            "dia": aloc.dia_semana,
            "turno": aloc.turno
        })
    return {"alocacoes_detalhadas": resultado_detalhado}