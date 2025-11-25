from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from app.database import Base

class Sala(Base):
    __tablename__ = "salas"

    id = Column(String, primary_key=True, index=True) 
    nome_visual = Column(String)
    bloco = Column(String)
    andar = Column(String)
    
    # Regras de Negócio (Oferta)
    especialidade_preferencial = Column(String)
    features = Column(JSON) # Lista de equipamentos/obs
    is_maintenance = Column(Boolean, default=False) # Se está interditado
    
    status_atual = Column(String, default="LIVRE") 

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    nome_profissional = Column(String)
    especialidade = Column(String)
    tipo_recurso = Column(String) # "DOCENTE", "RESIDENTE", "EXTRA"
    dia_semana = Column(String)
    turno = Column(String)
    
    origem = Column(String, default="AGHU") # "AGHU" ou "GESTOR"

class Alocacao(Base):
    __tablename__ = "alocacoes"

    id = Column(Integer, primary_key=True, index=True)
    
    sala_id = Column(String, ForeignKey("salas.id"))
    grade_id = Column(Integer, ForeignKey("grades.id"))
    
    # Redundância para facilitar consultas rápidas
    dia_semana = Column(String)
    turno = Column(String)
    score = Column(Integer) # Para o algoritmo saber quão boa foi essa escolha