from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class Turno(str, enum.Enum):
    MANHA = "M"
    TARDE = "T"
    NOITE = "N"

class Especialidade(Base):
    __tablename__ = "especialidades"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True) # Ex: "PEDIATRIA"
    nome_original = Column(String) # Ex: "PEDIATRIA - ENDOCRINO" (para referência)

    # Relacionamentos
    salas = relationship("Sala", back_populates="especialidade_rel")
    grades = relationship("Grade", back_populates="especialidade_rel")

class Sala(Base):
    __tablename__ = "salas"
    id = Column(String, primary_key=True, index=True)
    nome_visual = Column(String)
    bloco = Column(String)
    andar = Column(String)
    
    # Vínculo com a tabela Especialidade
    especialidade_id = Column(Integer, ForeignKey("especialidades.id"), nullable=True)
    especialidade_preferencial = Column(String) # Mantém string para fallback visual
    especialidade_rel = relationship("Especialidade", back_populates="salas")
    
    features = Column(JSON)
    is_maintenance = Column(Boolean, default=False)
    status_atual = Column(String, default="LIVRE")

class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    nome_profissional = Column(String)
    
    # Vínculo com a tabela Especialidade
    especialidade_id = Column(Integer, ForeignKey("especialidades.id"), nullable=True)
    especialidade = Column(String) # String original da grade
    especialidade_rel = relationship("Especialidade", back_populates="grades")
    
    tipo_recurso = Column(String)
    dia_semana = Column(String)
    turno = Column(String)
    origem = Column(String)

class Alocacao(Base):
    __tablename__ = "alocacoes"
    id = Column(Integer, primary_key=True, index=True)
    sala_id = Column(String, ForeignKey("salas.id"))
    grade_id = Column(Integer, ForeignKey("grades.id"))
    dia_semana = Column(String)
    turno = Column(String)
    score = Column(Integer)