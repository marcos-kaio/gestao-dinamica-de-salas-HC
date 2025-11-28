from sqlalchemy.orm import Session
from app.models import Sala, Grade, Alocacao
from collections import defaultdict, Counter
import re
import statistics

# --- CONFIGURAÇÕES ---
# Especialidades com preferência por acessibilidade
ESPECIALIDADES_TERREO = [
    "ortopedia", "traumatologia", "fisioterapia", "reabilitação", 
    "gastro", "proctologia"
]

def extrair_numero_sala(nome_visual: str) -> int:
    """Extrai 10 de 'E2-10'."""
    numeros = re.findall(r'\d+', str(nome_visual))
    if numeros:
        return int(numeros[-1])
    return 9999

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def extrair_zona(sala: Sala):
    """Padroniza a zona: BLOCO-ANDAR"""
    bloco = sala.bloco.upper().strip().replace("BLOCO", "").strip()
    andar = str(sala.andar).strip()
    if andar == "0" or "TÉRREO" in andar.upper():
        andar = "0"
    return f"{bloco}-{andar}"

def calcular_distancia_zonas(zona_a: str, zona_b: str):
    bloco_a, andar_a = zona_a.split('-')
    bloco_b, andar_b = zona_b.split('-')
    
    if bloco_a != bloco_b: return 1000 # Blocos diferentes = longe
    try:
        return abs(int(andar_a) - int(andar_b))
    except:
        return 100

def calcular_melhores_salas(grupo_medicos, todas_salas_disponiveis, nome_esp, infra_pref):
    """
    Avalia TODAS as salas disponíveis e escolhe as melhores.
    """
    esp_lower = nome_esp.lower()
    is_critico = any(c in esp_lower for c in ESPECIALIDADES_TERREO)
    
    # Zona Preferencial (Histórico)
    zona_pref = infra_pref.get(nome_esp)
    if not zona_pref:
        for k, v in infra_pref.items():
            if esp_lower in k.lower() or k.lower() in esp_lower:
                zona_pref = v
                break

    candidatas_pontuadas = []

    for sala in todas_salas_disponiveis:
        score = 0
        zona_sala = extrair_zona(sala)
        bloco, andar = zona_sala.split('-')
        
        # 1. ACESSIBILIDADE (Peso Ajustado)
        # Térreo ganha bônus, mas andar alto NÃO ganha penalidade mortal.
        # Assim, se o térreo encher, eles podem subir.
        if is_critico:
            if andar == "0": 
                score += 10000 
            else: 
                # Penalidade leve (antes era -50000). 
                # Permite que a sala oficial (no 3º andar) ainda tenha chance positiva se tiver match de nome.
                score -= 2000 
        else:
            if andar != "0": score += 500

        # 2. IDENTIDADE / MATCH (Peso: 5.000)
        # Se a sala é da especialidade, ganha muito ponto.
        # Ex: Ortopedia no 3º andar (Sala Oficial) = -2000 (Acesso) + 5000 (Match) = 3000 pts (VÁLIDO!)
        if sala.especialidade_preferencial:
            sala_esp_norm = sala.especialidade_preferencial.strip().lower()
            if esp_lower in sala_esp_norm or sala_esp_norm in esp_lower:
                score += 5000
        
        # 3. ZONA PREFERENCIAL (Peso: 2.000)
        if zona_pref and zona_sala == zona_pref:
            score += 2000
        elif zona_pref:
            dist = calcular_distancia_zonas(zona_sala, zona_pref)
            score -= (dist * 100)

        candidatas_pontuadas.append((sala, score))

    # Ordena: Maior Score -> Menor Número de Sala
    candidatas_pontuadas.sort(key=lambda x: (x[1], -extrair_numero_sala(x[0].nome_visual)), reverse=True)
    
    qtd_necessaria = len(grupo_medicos)
    melhores = candidatas_pontuadas[:qtd_necessaria]
    
    # Filtro de Segurança Relaxado: Aceita qualquer score > -5000
    # Isso garante que mesmo lugares ruins sejam usados se for a única opção (melhor que não atender)
    return [c for c in melhores if c[1] > -5000]

def gerar_alocacao_grade(db: Session):
    db.query(Alocacao).delete()
    
    grades = db.query(Grade).all()
    todas_salas_fisicas = db.query(Sala).filter(Sala.is_maintenance == False).all()
    
    # Mapeamento de histórico
    mapa = defaultdict(list)
    for s in todas_salas_fisicas:
        if s.especialidade_preferencial:
            esp = s.especialidade_preferencial.strip()
            if "fechado" not in esp.lower():
                mapa[esp].append(extrair_zona(s))
    
    infra_pref = {}
    for esp, locais in mapa.items():
        if locais:
            infra_pref[esp] = Counter(locais).most_common(1)[0][0]

    cronograma = defaultdict(lambda: defaultdict(list))
    for g in grades:
        cronograma[g.dia_semana][g.turno].append(g)

    final_alocacoes = []
    conflitos = []
    dias = ["SEG", "TER", "QUA", "QUI", "SEX"]
    turnos = ["MANHA", "TARDE", "NOITE"]

    for dia in dias:
        for turno in turnos:
            demanda = cronograma[dia][turno]
            if not demanda: continue

            # Agrupa
            grupos = defaultdict(list)
            for g in demanda:
                grupos[str(g.especialidade).strip()].append(g)

            # Ordena: Críticos > Grandes
            ordem = sorted(grupos.items(), key=lambda item: (
                1 if any(crit in item[0].lower() for crit in ESPECIALIDADES_TERREO) else 0,
                len(item[1])
            ), reverse=True)

            salas_ocupadas_ids = set()

            for nome_esp, medicos in ordem:
                disponiveis = [s for s in todas_salas_fisicas if s.id not in salas_ocupadas_ids]
                
                # --- OTIMIZAÇÃO: Recalibrada ---
                melhores_matches = calcular_melhores_salas(medicos, disponiveis, nome_esp, infra_pref)
                
                alocados_count = 0
                for i, (sala, score) in enumerate(melhores_matches):
                    medico = medicos[i]
                    final_alocacoes.append({
                        "sala_obj": sala,
                        "grade_obj": medico,
                        "dia": dia,
                        "turno": turno,
                        "score": score
                    })
                    salas_ocupadas_ids.add(sala.id)
                    alocados_count += 1
                
                # Sobras viram conflito
                if alocados_count < len(medicos):
                    for m in medicos[alocados_count:]:
                        conflitos.append({
                            "medico": m.nome_profissional,
                            "especialidade": m.especialidade,
                            "motivo": "Lotação máxima (todas as salas viáveis ocupadas)"
                        })

    # Persistência
    for item in final_alocacoes:
        nova = Alocacao(
            sala_id=item['sala_obj'].id,
            grade_id=item['grade_obj'].id,
            dia_semana=item['dia'],
            turno=item['turno'],
            score=item['score']
        )
        db.add(nova)

    db.commit()
    return obter_resumo_atual(db)

def formatar_obj_resumo(grade, sala, dia, turno):
    return {
        "medico": grade.nome_profissional,
        "especialidade": grade.especialidade,
        "sala": sala.nome_visual,
        "sala_id": sala.id,
        "bloco": sala.bloco,
        "andar": sala.andar,
        "dia": dia,
        "turno": turno
    }

def construir_resumo_final(detalhes, conflitos, todas_salas):
    agrupamento = defaultdict(lambda: {"salas_unicas": set(), "locais": set()})
    
    capacidade_map = defaultdict(int)
    for s in todas_salas:
        if s.especialidade_preferencial and not s.is_maintenance:
            norm = s.especialidade_preferencial.strip().lower()
            capacidade_map[norm] += 1

    for item in detalhes:
        esp = item['especialidade']
        agrupamento[esp]['salas_unicas'].add(item['sala'])
        
        andar_str = "Térreo" if str(item['andar']) == "0" else f"{item['andar']}º Andar"
        local_txt = f"{item['bloco']} - {andar_str}"
        if "BLOCO" not in local_txt.upper() and "ANEXO" not in local_txt.upper():
             local_txt = f"Bloco {local_txt}"
        agrupamento[esp]['locais'].add(local_txt)

    resumo_final = []
    for especialidade, dados in agrupamento.items():
        lista_salas = sorted(list(dados['salas_unicas']), key=natural_sort_key)
        
        esp_lower = especialidade.strip().lower()
        cap_total = 0
        # Busca flexível de capacidade (contém string)
        for k, v in capacidade_map.items():
            if esp_lower in k or k in esp_lower:
                cap_total += v
        
        if cap_total < len(lista_salas): cap_total = len(lista_salas)

        resumo_final.append({
            "ambulatorio": especialidade,
            "total_alocadas": len(dados['salas_unicas']),
            "capacidade": cap_total,
            "localizacao": sorted(list(dados['locais'])),
            "lista_salas": lista_salas
        })

    resumo_final.sort(key=lambda x: x['total_alocadas'], reverse=True)

    return {
        "resumo_ambulatorios": resumo_final,
        "alocacoes_detalhadas": detalhes,
        "conflitos": conflitos
    }

def obter_resumo_atual(db: Session):
    query = db.query(Alocacao, Sala, Grade)\
        .join(Sala, Alocacao.sala_id == Sala.id)\
        .join(Grade, Alocacao.grade_id == Grade.id)\
        .all()
    
    salas_totais = db.query(Sala).filter(Sala.is_maintenance == False).all()
    detalhes = []
    for aloc, sala, grade in query:
        detalhes.append(formatar_obj_resumo(grade, sala, aloc.dia_semana, aloc.turno))
        
    return construir_resumo_final(detalhes, [], salas_totais)

# --- FUNÇÕES DE TEMPO REAL (Simplificadas para evitar erro de import) ---
def descobrir_andar_predominante(db: Session, especialidade: str):
    return "E-0", 0
def calcular_afinidade_tempo_real(sala: Sala, especialidade_medico: str, target_local: str, num_alvo: float) -> float:
    return 0