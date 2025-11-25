import pandas as pd
import os
from app.models import Sala, Grade
from app.database import SessionLocal
from collections import defaultdict

def get_file_path(filename):
    possible_paths = [f"data/{filename}", f"backend/data/{filename}", f"../data/{filename}"]
    for path in possible_paths:
        if os.path.exists(path): return path
    return None

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
        db.query(Sala).delete()
        db.commit()
        
        salas_criadas = 0
        room_counters = defaultdict(int)
        
        for index, row in df.iterrows():
            nome_amb = str(row.get('Nome do ambulatório', '')).strip()
            pav_raw = str(row.get('Pavimento', '')).strip()
            
            if not nome_amb or nome_amb.lower() == 'nan' or not pav_raw:
                continue

            pav_upper = pav_raw.upper()
            bloco = "E" if "E" in pav_upper else "F" if "F" in pav_upper else "ANEXO"
            
            if "TÉRREO" in pav_upper:
                andar = "0"
            else:
                andar = ''.join(filter(str.isdigit, pav_raw.split(' ')[0]))
                if not andar: andar = "0"

            try:
                qtd = int(float(row.get('Número de salas existestes', 0)))
            except:
                qtd = 0

            obs = str(row.get('OBS', ''))
            features = [obs] if obs and obs.lower() != 'nan' else []
            em_obra = "fechado para obra" in nome_amb.lower()

            for i in range(qtd):
                room_counters[(bloco, andar)] += 1
                numero_sala = room_counters[(bloco, andar)]
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
        return {"status": "sucesso", "salas_importadas": salas_criadas}
    
    except Exception as e:
        db.rollback()
        return {"erro": f"Erro na importação: {str(e)}"}
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