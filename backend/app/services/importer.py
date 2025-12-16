import pandas as pd
import os
import re
from app.models import Sala, Grade
from app.database import SessionLocal
from collections import defaultdict

def get_file_path(filename):
    possible_paths = [f"data/{filename}", f"backend/data/{filename}", f"../data/{filename}"]
    for path in possible_paths:
        if os.path.exists(path): return path
    return None

def extrair_bloco_e_andar(pavimento_raw):
    """
    Extrai informações precisas de strings como:
    '1º pavimento (Térreo) Bloco E' -> Bloco: E, Andar: 0
    '3º pavimento Bloco F' -> Bloco: F, Andar: 3
    '1º pavimento (Térreo) Anexo' -> Bloco: ANEXO, Andar: 0
    """
    raw = str(pavimento_raw).strip().upper()
    
    # Definição do Bloco
    if "ANEXO" in raw:
        bloco = "ANEXO"
    elif "BLOCO F" in raw:
        bloco = "F"
    elif "BLOCO E" in raw:
        bloco = "E"
    elif "BLOCO C" in raw:
        bloco = "C"
    else:
        bloco = "E"

    # Definição do Andar
    if "TÉRREO" in raw or "TERREO" in raw:
        andar = "0"
    else:
        # Pega o primeiro dígito numérico que encontrar
        match = re.search(r'\d+', raw)
        andar = match.group(0) if match else "0"

    return bloco, andar

def importar_salas_csv():
    filename = "salas.csv"
    csv_path = get_file_path(filename)
    
    if not csv_path:
        return {"erro": f"Arquivo '{filename}' não encontrado."}

    try:
        df = pd.read_csv(csv_path, dtype=str)
    except Exception as e:
        return {"erro": f"Erro ao ler CSV: {str(e)}"}

    db = SessionLocal()
    
    try:
        # Limpa tabela atual
        db.query(Sala).delete()
        
        salas_criadas = 0
        # Contador para gerar IDs únicos sequenciais por andar
        room_counters = defaultdict(int)
        
        for index, row in df.iterrows():
            nome_amb = str(row.get('Nome do ambulatório', '')).strip()
            pav_raw = str(row.get('Pavimento', '')).strip()
            
            if not nome_amb or nome_amb.lower() == 'nan' or not pav_raw:
                continue

            # Extração Robusta
            bloco, andar = extrair_bloco_e_andar(pav_raw)

            # Quantidade de salas
            qtd_str = row.get('Número de salas existestes', '0')
            try:
                qtd = int(float(qtd_str)) if qtd_str.lower() != 'nan' else 0
            except:
                qtd = 0

            obs = str(row.get('OBS', ''))
            features = [obs] if obs and obs.lower() != 'nan' else []
            
            # Verifica se é obra e PADRONIZA O NOME
            em_obra = "fechado para obra" in nome_amb.lower()
            if em_obra:
                nome_amb = "Fechado para Obras"

            # Gera as salas individuais no banco
            for _ in range(qtd):
                room_counters[(bloco, andar)] += 1
                numero_sala = room_counters[(bloco, andar)]
                
                # ID legível: BlocoAndar-Numero
                sala_id = f"{bloco}{andar}-{numero_sala}"
                
                nova_sala = Sala(
                    id=sala_id,
                    nome_visual=sala_id, 
                    bloco=bloco,
                    andar=andar,
                    especialidade_preferencial=nome_amb,
                    features=features,
                    is_maintenance=em_obra
                )
                db.add(nova_sala)
                salas_criadas += 1
        
        db.commit()
        return {
            "status": "sucesso", 
            "salas_importadas": salas_criadas, 
            "detalhe": "Mapeamento de Blocos E, F, C e Anexo corrigido."
        }
    
    except Exception as e:
        db.rollback()
        return {"erro": f"Erro crítico na importação: {str(e)}"}
    finally:
        db.close()

def importar_grades_csv():
    path = get_file_path("grades.csv")
    if not path: return {"erro": "Arquivo não encontrado"}
    
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return {"erro": f"Erro ao ler CSV: {str(e)}"}

    db = SessionLocal()
    try:
        db.query(Grade).delete()
        grades_criadas = 0
        
        for _, row in df.iterrows():
            nova_grade = Grade(
                nome_profissional=str(row['medico_nome']),
                especialidade=str(row['especialidade']),
                tipo_recurso=str(row.get('tipo_recurso', 'DOCENTE')),
                dia_semana=str(row['dia_semana']),
                turno=str(row['turno']),
                origem="AGHU"
            )
            db.add(nova_grade)
            grades_criadas += 1
        
        db.commit()
        return {"status": "sucesso", "grades_importadas": grades_criadas}
    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
    finally:
        db.close()