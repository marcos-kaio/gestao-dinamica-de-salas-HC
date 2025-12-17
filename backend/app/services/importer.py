import pandas as pd
import os
import re
import unicodedata
from app.models import Sala, Grade
from app.database import SessionLocal
from collections import defaultdict

def get_file_path(filename):
    possible_paths = [
        f"data/{filename}", 
        f"backend/data/{filename}", 
        f"../data/{filename}",
        filename
    ]
    for path in possible_paths:
        if os.path.exists(path): return path
    return None

def normalize_text(text):
    """Padroniza texto: SEM ACENTOS e UPPERCASE"""
    if not isinstance(text, str): return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text.upper().strip()

# --- REGRAS DE MAPEAMENTO ---
MAPPING_RULES = [
    ("TELEMEDICINA", "IGNORAR"), ("TELEENFERMAGEM", "IGNORAR"), ("TELEFONOAUDIOLOGIA", "IGNORAR"),
    ("TELENUTRICAO", "IGNORAR"), ("TELETERAPIA", "IGNORAR"), ("TELECONSULTA", "IGNORAR"),
    ("TELE-TRIAGEM", "IGNORAR"), ("NAVEGACAO", "IGNORAR"),
    ("BRONCOSCOPIA", "PNEUMOLOGIA"),
    ("HEMODIALISE", "NEFROLOGIA"), ("TRANSPLANTE RENAL", "NEFROLOGIA"),
    ("PALIATIVOS", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("PLASTICA", "PLASTICA"),
    ("COLPOSCOPIA", "COLPOSCOPIA"), ("COLPO", "COLPOSCOPIA"),
    ("PUERICULTURA", "PUERICULTURA"),
    ("GASTROPEDIATRIA", "PEDIATRIA"), ("NEUROPEDIATRIA", "PEDIATRIA"), ("PEDIATRIA", "PEDIATRIA"),
    ("ENDOMETRIOSE", "GINECOLOGIA/ OBSTETRICIA"), ("GESTACIONAL", "GINECOLOGIA/ OBSTETRICIA"),
    ("MASTOLOGIA", "GINECOLOGIA/ OBSTETRICIA"), ("GINECOLOGIA", "GINECOLOGIA/ OBSTETRICIA"),
    ("GINECO", "GINECOLOGIA/ OBSTETRICIA"), ("OBSTETRICIA", "GINECOLOGIA/ OBSTETRICIA"),
    ("OBST", "GINECOLOGIA/ OBSTETRICIA"),
    ("ESPACO TRANS", "ESPACO TRANS"),
    ("TERAPIA FAMILIAR", "TERAPIA FAMILIAR"),
    ("NEUROLOGIA", "NEUROLOGIA"), ("NEURO", "NEUROLOGIA"),
    ("ENDOCRINOLOGIA", "ENDOCRINOLOGIA"), ("ENDOCRINO", "ENDOCRINOLOGIA"), ("OBESIDADE", "ENDOCRINOLOGIA"),
    ("PRE OPERATORIO", "PRE OPERATORIO"), ("PRE-OPERATORIO", "PRE OPERATORIO"),
    ("ANESTESIOLOGIA", "PRE OPERATORIO"), 
    ("SALA DE VACINA", "SALA DE VACINA"), ("VACINA", "SALA DE VACINA"),
    ("ONCOLOGIA", "ONCOLOGIA"), ("ONCO", "ONCOLOGIA"), ("QUIMIOTERAPIA", "ONCOLOGIA"),
    ("FONOAUDIOLOGIA", "FONOAUDIOLOGIA"), ("FONO", "FONOAUDIOLOGIA"),
    ("NEFROLOGIA", "NEFROLOGIA"), ("NEFRO", "NEFROLOGIA"),
    ("ORTOPEDIA", "ORTOPEDIA"), ("ORTO", "ORTOPEDIA"),
    ("CARDIOLOGIA", "CARDIOLOGIA"), ("CARDIO", "CARDIOLOGIA"),
    ("HEMATOLOGIA", "HEMATOLOGIA"), ("HEMATO", "HEMATOLOGIA"),
    ("PNEUMOLOGIA", "PNEUMOLOGIA"), ("PNEUMO", "PNEUMOLOGIA"),
    ("UROLOGIA", "UROLOGIA"), ("URO", "UROLOGIA"),
    ("DOENCAS INFECTO", "DOENCAS INFECTO CONTAGIOSAS- DIP"), ("DIP", "DOENCAS INFECTO CONTAGIOSAS- DIP"),
    ("INFECTO", "DOENCAS INFECTO CONTAGIOSAS- DIP"),
    ("VASCULAR", "VASCULAR"),
    ("OTORRINO", "OTORRINO"),
    ("OFTALMO", "OFTALMO"), ("OCULISTICA", "OFTALMO"), ("OCI - AVAL", "OFTALMO"),
    ("PSIQUIATRIA", "PSIQUIATRIA"), ("SAUDE MENTAL", "PSIQUIATRIA"),
    ("DERMATOLOGIA", "DERMATOLOGIA"), ("DERMATO", "DERMATOLOGIA"),
    ("GASTRO", "GASTRO"), ("PROCTOLOGIA", "GASTRO"),
    ("REUMATOLOGIA", "REUMATOLOGIA"), ("REUMATO", "REUMATOLOGIA"),
    ("LUPUS", "REUMATOLOGIA"), ("GOTA", "REUMATOLOGIA"), ("ARTRITE", "REUMATOLOGIA"),
    ("ALERGIA", "PNEUMOLOGIA"), ("IMUNOLOGIA", "PNEUMOLOGIA"),
    ("NUTRICAO", "ENDOCRINOLOGIA"), 
    ("PSICOLOGIA", "PSIQUIATRIA"),
    ("SERVICO SOCIAL", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("FISIOTERAPIA", "ORTOPEDIA"), 
    ("EDUCACAO FISICA", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("BUCOMAXILOFACIAL", "OTORRINO"), ("ODONTOLOGIA", "CIRURGIA GERAL"), ("ESTOMATOLOGIA", "OTORRINO"),
    ("TERAPIA OCUPACIONAL", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("MEDICINA DO TRABALHO", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("ACUPUNTURA", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("RADIOLOGIA", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("PESQUISA", "CLINICA MEDICA/ GERIATRIA/ DOR"), ("ESTOMIAS", "CIRURGIA GERAL"),
    ("CLINICA MEDICA", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("CLINICA GERAL", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("GERIATRIA", "CLINICA MEDICA/ GERIATRIA/ DOR"), ("DOR", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("HOSPITAL-DIA", "CLINICA MEDICA/ GERIATRIA/ DOR"), ("TRIAGEM", "CLINICA MEDICA/ GERIATRIA/ DOR"),
    ("CIRURGIA GERAL", "CIRURGIA GERAL"), ("CIRURGIA", "CIRURGIA GERAL"),
    ("ENFERMAGEM", "IGNORAR"), ("FARMACIA", "IGNORAR"),
]

def map_specialty(specialty_raw):
    norm_spec = normalize_text(specialty_raw)
    for keyword, target in MAPPING_RULES:
        if keyword in norm_spec: return target
    return "NAO MAPEADO"

def extrair_bloco_e_andar(pavimento_raw):
    raw = normalize_text(pavimento_raw)
    if "ANEXO" in raw: bloco = "ANEXO"
    elif "BLOCO F" in raw: bloco = "F"
    elif "BLOCO E" in raw: bloco = "E"
    elif "BLOCO C" in raw: bloco = "C"
    else: bloco = "E"
    if "TERREO" in raw: andar = "0"
    else:
        match = re.search(r'\d+', raw)
        andar = match.group(0) if match else "0"
    return bloco, andar

def importar_salas_csv():
    filename = "salas.csv"
    csv_path = get_file_path(filename)
    if not csv_path: return {"erro": f"Arquivo '{filename}' não encontrado."}

    try: 
        # Lê o CSV. Pandas já identifica NaN para células vazias.
        df = pd.read_csv(csv_path)
    except Exception as e: return {"erro": f"Erro ao ler CSV: {str(e)}"}

    db = SessionLocal()
    try:
        db.query(Sala).delete()
        salas_criadas = 0
        room_counters = defaultdict(int)
        
        for _, row in df.iterrows():
            nome_raw = row.get('Nome do ambulatório')
            pav_raw = row.get('Pavimento')
            
            # --- FILTRO ANTIFANTASMA INFALÍVEL ---
            # Se o nome for nulo (NaN), ignora. Isso mata a linha 34 (Total: 255).
            if pd.isna(nome_raw): continue
            if pd.isna(pav_raw): continue
            
            # Converte para string limpa
            nome_clean = normalize_text(str(nome_raw))
            if not nome_clean or nome_clean == 'NAN' or "TOTAL" in nome_clean: continue

            try:
                # Tenta ler a quantidade
                val = row.get('Número de salas existestes', 0)
                if pd.isna(val): qtd = 0
                else: qtd = int(float(val))
                
                # Trava extra: 60 salas é o teto para um ambulatório
                if qtd > 60: continue 
            except: qtd = 0

            if qtd <= 0: continue

            caracteristica = normalize_text(str(row.get('Característica', '')))
            is_specialized = "ESPECIALIZADO" in caracteristica
            
            bloco, andar = extrair_bloco_e_andar(str(pav_raw))
            is_obra = "FECHADO PARA OBRA" in nome_clean or "FECHADO PARA OBRAS" in nome_clean
            if is_obra: nome_clean = "FECHADO PARA OBRAS"

            obs = str(row.get('OBS', ''))
            features = []
            if not pd.isna(obs): features.append(str(obs))
            if is_specialized: features.append("RESTRICTED_SPECIALTY")

            for _ in range(qtd):
                room_counters[(bloco, andar)] += 1
                sala_id = f"{bloco}{andar}-{room_counters[(bloco, andar)]:02d}"
                
                nova_sala = Sala(
                    id=sala_id, nome_visual=sala_id, bloco=bloco, andar=andar,
                    especialidade_preferencial=nome_clean, features=features, is_maintenance=is_obra
                )
                db.add(nova_sala)
                salas_criadas += 1
        
        db.commit()
        return {"status": "sucesso", "salas_importadas": salas_criadas}
    except Exception as e:
        db.rollback()
        return {"erro": f"Erro crítico salas: {str(e)}"}
    finally:
        db.close()

def map_dia_semana(valor):
    try:
        v = float(valor)
        if v == 2.0: return "SEG"
        if v == 3.0: return "TER"
        if v == 4.0: return "QUA"
        if v == 5.0: return "QUI"
        if v == 6.0: return "SEX"
    except: pass
    return "IND"

def importar_grades_csv():
    filename = "Grades 2.csv"
    path = get_file_path(filename)
    if not path: path = get_file_path("grades.csv")
    if not path: return {"erro": "Arquivo de grades não encontrado"}
    
    try: 
        df = pd.read_csv(path)
        # Remove duplicatas exatas (erro de cópia)
        df.drop_duplicates(inplace=True)
    except Exception as e: return {"erro": f"Erro ao ler CSV: {str(e)}"}

    db = SessionLocal()
    try:
        db.query(Grade).delete()
        grades_criadas = 0
        for _, row in df.iterrows():
            raw_spec = str(row.get('nome_especialidade', ''))
            especialidade_mapeada = map_specialty(raw_spec)
            
            if especialidade_mapeada == "IGNORAR": continue
            
            dia = map_dia_semana(row.get('dia_semana'))
            if dia == "IND": continue
            
            turno = normalize_text(str(row.get('turno', '')))
            if "MANHA" in turno: turno = "MANHA"
            elif "TARDE" in turno: turno = "TARDE"
            else: turno = "NOITE"
            
            vinculo = normalize_text(str(row.get('vinculo_descricao', '')))
            tipo = "RESIDENTE" if "RESIDENTE" in vinculo else "DOCENTE"

            nova_grade = Grade(
                nome_profissional=str(row.get('nome', 'Profissional')),
                especialidade=especialidade_mapeada,
                tipo_recurso=tipo, dia_semana=dia, turno=turno, origem="Grades2"
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