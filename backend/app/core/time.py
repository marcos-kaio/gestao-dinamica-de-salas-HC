from datetime import datetime
import pytz

def get_horario_atual():
    """Retorna o dia e turno atuais baseados no horário de Recife."""
    tz = pytz.timezone('America/Recife')
    agora = datetime.now(tz)
    
    dias = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM']
    dia_atual = dias[agora.weekday()]
    
    hora = agora.hour
    turno_atual = None
    
    # Definição dos Turnos
    if 6 <= hora < 13:
        turno_atual = 'MANHA'
    elif 13 <= hora < 18: # Ajustar conforme a realidade do HC
        turno_atual = 'TARDE'
    elif 18 <= hora < 23:
        turno_atual = 'NOITE'
    else:
        turno_atual = 'MADRUGADA'
        
    return {
        "dia": dia_atual,
        "turno": turno_atual,
        "hora_legivel": agora.strftime("%H:%M"),
        "data_legivel": agora.strftime("%d/%m/%Y")
    }