from sqlalchemy.orm import Session
from app.models import Sala, Grade, Alocacao
from collections import defaultdict, Counter
import re, statistics

def calcular_score(grade: Grade, sala: Sala, cluster_ideal: tuple = None) -> int:
    """
    Calcula o 'match' entre uma demanda (Grade) e uma oferta (Sala).
    Quanto maior o score, melhor a alocação.
    """
    if sala.is_maintenance: return -10000
    
    score = 0
    
    sala_esp = str(sala.especialidade_preferencial).lower()
    grade_esp = str(grade.especialidade).lower()
    
    # 1. Match de Especialidade (Regra Básica)
    if sala_esp and grade_esp in sala_esp:
        score += 100
    
    # 2. Regra de Agrupamento (Novo: Clustering)
    # Se a sala está no bloco/andar ideal para essa especialidade, ganha bônus.
    if cluster_ideal:
        bloco_ideal, andar_ideal = cluster_ideal
        if sala.bloco == bloco_ideal and str(sala.andar) == str(andar_ideal):
            score += 200 # Força gravitacional para manter juntos
    
    # 3. Regras Específicas (Legado/Hardcoded)
    if "ortopedia" in grade_esp:
        if str(sala.andar) == "0" or "térreo" in str(sala.andar).lower(): 
            score += 50
        else: 
            score -= 50
            
    return score

def identificar_clusters_preferenciais(grades, salas):
    """
    Analisa a infraestrutura e define qual é o 'Andar/Bloco Principal' 
    para cada especialidade demandada na grade.
    Retorna: { 'Pediatria': ('F', '2'), 'Cardiologia': ('F', '3') }
    """
    especialidades_demandadas = set(g.especialidade for g in grades if g.especialidade)
    cluster_map = {} 
    
    for esp in especialidades_demandadas:
        esp_lower = esp.lower()
        counts = Counter()
        
        for sala in salas:
            # Conta quantas salas dessa especialidade existem em cada andar/bloco
            if sala.especialidade_preferencial and esp_lower in sala.especialidade_preferencial.lower():
                loc = (sala.bloco, sala.andar)
                counts[loc] += 1
                
        if counts:
            # Define o local vencedor (onde tem mais salas dessa especialidade)
            melhor_loc = counts.most_common(1)[0][0]
            cluster_map[esp] = melhor_loc
            
    return cluster_map

def natural_sort_key(s):
    """Função auxiliar para ordenar E2-1, E2-2, E2-10 corretamente"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def gerar_alocacao_grade(db: Session):
    db.query(Alocacao).delete()
    
    grades = db.query(Grade).all()
    salas = db.query(Sala).filter(Sala.is_maintenance == False).all()
    
    # Passo 1: Identificar onde cada especialidade deve ficar "preferencialmente"
    # Isso garante que se a Pediatria tem salas no 2º e no 3º, o algoritmo tente
    # colocar todo mundo no andar que tem mais salas (ex: 2º) antes de transbordar.
    cluster_map = identificar_clusters_preferenciais(grades, salas)
    
    ocupacao = {
        d: {t: [] for t in ["MANHA", "TARDE"]} 
        for d in ["SEG", "TER", "QUA", "QUI", "SEX"]
    }
    
    resultado_detalhado = []
    conflitos = []

    # Ordena grades para priorizar especialidades com menos opções (opcional, mas ajuda)
    # Por enquanto, mantemos a ordem de chegada ou ID

    for item_grade in grades:
        melhor_sala = None
        melhor_score = -9999
        
        # Descobre o cluster ideal para essa especialidade específica
        cluster_alvo = cluster_map.get(item_grade.especialidade)
        
        for sala in salas:
            # Verifica se já está ocupada naquele horário
            if sala.id in ocupacao.get(item_grade.dia_semana, {}).get(item_grade.turno, []):
                continue
                
            # Calcula score passando o cluster alvo
            score = calcular_score(item_grade, sala, cluster_alvo)
            
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
    # Pega o andar mais comum na infraestrutura
    if not lista_andares: return None, None
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
    Usado no Check-in Semi-Automático.
    """
    esp_medico = especialidade_medico.lower().strip()
    score = 0

    if not sala.especialidade_preferencial:
        score += 10
    
    esp_sala = str(sala.especialidade_preferencial).lower().strip()

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

def obter_resumo_atual(db: Session):
    """
    Recupera a alocação atual do banco de dados e formata para o Dashboard.
    Não altera dados, apenas lê.
    """
    # Busca todas as alocações com Join nas tabelas de Sala e Grade
    alocacoes = db.query(Alocacao, Sala, Grade)\
        .join(Sala, Alocacao.sala_id == Sala.id)\
        .join(Grade, Alocacao.grade_id == Grade.id)\
        .all()

    if not alocacoes:
        return {"resumo_ambulatorios": [], "alocacoes_detalhadas": []}

    # Reconstrói a estrutura detalhada
    resultado_detalhado = []
    for aloc, sala, grade in alocacoes:
        resultado_detalhado.append({
            "medico": grade.nome_profissional,
            "especialidade": grade.especialidade,
            "sala": sala.nome_visual,
            "sala_id": sala.id,
            "bloco": sala.bloco,
            "andar": sala.andar,
            "dia": aloc.dia_semana,
            "turno": aloc.turno
        })

    # Agrupamento (Lógica idêntica à de gerar_alocacao)
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
        "alocacoes_detalhadas": resultado_detalhado
    }