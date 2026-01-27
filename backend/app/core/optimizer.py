from sqlalchemy.orm import Session
from app.models import Sala, Grade, Alocacao, Especialidade
from collections import defaultdict
from app.core.time import get_horario_atual
import re

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def normalizar(texto: str) -> str:
    return str(texto).lower().strip() if texto else ""

def calcular_score(grade: Grade, sala: Sala, zona_preferencial: dict) -> int:
    if sala.is_maintenance: return -10000
    score = 0
    if grade.especialidade_id and sala.especialidade_id:
        if grade.especialidade_id == sala.especialidade_id: score += 2000 
    elif normalizar(grade.especialidade) in normalizar(sala.especialidade_preferencial):
        score += 1500
    
    chave_sala = (sala.bloco, sala.andar)
    chave_esp = grade.especialidade_id if grade.especialidade_id else grade.especialidade
    zona_alvo = zona_preferencial.get(chave_esp)
    
    if zona_alvo:
        if chave_sala == zona_alvo: score += 500
        elif sala.bloco == zona_alvo[0]: score += 200
        else: score -= 100

    grade_nome = normalizar(grade.especialidade)
    if "oftalmo" in grade_nome and "oftalmo" not in normalizar(sala.especialidade_preferencial): return -5000 
    if ("ginecologia" in grade_nome or "obstetricia" in grade_nome) and "maca" not in str(sala.features).lower(): return -2000
    especialidades_terreo = ["ortopedia", "traumatologia", "geriatria"]
    if any(e in grade_nome for e in especialidades_terreo):
        if str(sala.andar) == "0": score += 300
        else: score -= 300
    return score

def gerar_alocacao_grade(db: Session):
    db.query(Alocacao).delete()
    grades = db.query(Grade).all()
    grades.sort(key=lambda x: (x.especialidade_id is None, x.tipo_recurso == 'RESIDENTE', x.nome_profissional))
    salas = db.query(Sala).filter(Sala.is_maintenance == False).all()
    salas.sort(key=lambda s: (s.bloco, s.andar, natural_sort_key(s.id)))
    
    mapa_zonas = defaultdict(lambda: defaultdict(int))
    for sala in salas:
        chave = (sala.bloco, sala.andar)
        esp = sala.especialidade_id if sala.especialidade_id else sala.especialidade_preferencial
        if esp: mapa_zonas[esp][chave] += 1
            
    zona_pref = {k: max(v.items(), key=lambda x: x[1])[0] for k, v in mapa_zonas.items() if v}
    ocupacao = {d: {t: set() for t in ["MANHA", "TARDE", "NOITE"]} for d in ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]}
    conflitos = []

    for item in grades:
        if item.dia_semana not in ocupacao or item.turno not in ocupacao[item.dia_semana]: continue
        ocupadas = ocupacao[item.dia_semana][item.turno]
        melhor_sala = None
        melhor_score = -9999
        
        for sala in salas:
            if sala.id in ocupadas: continue
            score = calcular_score(item, sala, zona_pref)
            if score > melhor_score:
                melhor_score = score
                melhor_sala = sala
        
        if melhor_sala and melhor_score > -1000:
            db.add(Alocacao(sala_id=melhor_sala.id, grade_id=item.id, dia_semana=item.dia_semana, turno=item.turno, score=melhor_score))
            ocupadas.add(melhor_sala.id)
        else:
            conflitos.append({"medico": item.nome_profissional, "motivo": "Sem sala"})
            
    db.commit()
    return {"resumo_ambulatorios": obter_resumo_atual(db), "conflitos": conflitos}

def obter_resumo_atual(db: Session):
    dados = db.query(Alocacao, Sala, Grade, Especialidade).join(Sala, Alocacao.sala_id == Sala.id).join(Grade, Alocacao.grade_id == Grade.id).outerjoin(Especialidade, Grade.especialidade_id == Especialidade.id).all()
    agrupamento = defaultdict(lambda: {"salas_unicas": set(), "locais": set(), "detalhes": []})
    for aloc, sala, grade, esp_obj in dados:
        nome = esp_obj.nome if esp_obj else grade.especialidade
        agrupamento[nome]['salas_unicas'].add(sala.nome_visual)
        agrupamento[nome]['locais'].add(f"Bloco {sala.bloco} - {sala.andar}")
        agrupamento[nome]['detalhes'].append({"alocacao_id": aloc.id, "medico": grade.nome_profissional, "sala": sala.nome_visual, "dia": grade.dia_semana, "turno": grade.turno, "score": aloc.score})
    
    resumo = []
    for nome, info in agrupamento.items():
        resumo.append({"ambulatorio": nome, "total_salas": len(info['salas_unicas']), "localizacao": sorted(list(info['locais'])), "lista_salas": sorted(list(info['salas_unicas']), key=natural_sort_key), "detalhes": info['detalhes']})
    resumo.sort(key=lambda x: x['total_salas'], reverse=True)
    return resumo

def listar_opcoes_troca(alocacao_id: int, db: Session):
    aloc = db.query(Alocacao).filter(Alocacao.id == alocacao_id).first()
    if not aloc: return []
    grade = db.query(Grade).filter(Grade.id == aloc.grade_id).first()
    ocupadas = {id[0] for id in db.query(Alocacao.sala_id).filter(Alocacao.dia_semana == aloc.dia_semana, Alocacao.turno == aloc.turno).all()}
    salas = db.query(Sala).filter(Sala.is_maintenance == False).all()
    opcoes = []
    for sala in salas:
        if sala.id not in ocupadas or sala.id == aloc.sala_id:
            score = calcular_score(grade, sala, {})
            opcoes.append({"sala_id": sala.id, "nome": sala.nome_visual, "score": score, "recomendado": score > 0, "atual": sala.id == aloc.sala_id})
    opcoes.sort(key=lambda x: (x['atual'], x['score']), reverse=True)
    return opcoes

def aplicar_troca_manual(alocacao_id: int, nova_sala_id: str, db: Session):
    aloc = db.query(Alocacao).filter(Alocacao.id == alocacao_id).first()
    if not aloc: return False
    if db.query(Alocacao).filter(Alocacao.sala_id == nova_sala_id, Alocacao.dia_semana == aloc.dia_semana, Alocacao.turno == aloc.turno, Alocacao.id != alocacao_id).first(): return False
    aloc.sala_id = nova_sala_id
    db.commit()
    return True

# função de monitoramento
def obter_dashboard_tempo_real(db: Session):
    tempo = get_horario_atual()
    dia = tempo['dia']
    turno = tempo['turno']
    
    salas = db.query(Sala).all()
    
    # Busca alocações APENAS do momento atual
    alocacoes_agora = db.query(Alocacao, Grade, Especialidade)\
        .join(Grade, Alocacao.grade_id == Grade.id)\
        .outerjoin(Especialidade, Grade.especialidade_id == Especialidade.id)\
        .filter(Alocacao.dia_semana == dia, Alocacao.turno == turno)\
        .all()
        
    mapa_ocupacao = {aloc.sala_id: {"medico": grade.nome_profissional, "especialidade": (esp.nome if esp else grade.especialidade)} for aloc, grade, esp in alocacoes_agora}
    
    resultado = []
    stats = {"livres": 0, "ocupadas": 0, "manutencao": 0}
    
    for sala in salas:
        status = "LIVRE"
        detalhes = None
        
        if sala.is_maintenance:
            status = "MANUTENCAO"
            stats["manutencao"] += 1
        elif sala.id in mapa_ocupacao:
            status = "OCUPADA"
            detalhes = mapa_ocupacao[sala.id]
            stats["ocupadas"] += 1
        else:
            stats["livres"] += 1
            
        resultado.append({
            "sala_id": sala.id,
            "nome": sala.nome_visual,
            "bloco": sala.bloco,
            "andar": sala.andar,
            "status": status,
            "ocupante": detalhes
        })
        
    return {
        "tempo": tempo,
        "estatisticas": stats,
        "salas": sorted(resultado, key=lambda x: natural_sort_key(x['sala_id']))
    }