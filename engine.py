# Break-even: Custo total = Receita total

# CPA, CPC e Conversão

# CPA = CPC / Conversão


### Features ###

# Calcular CPA
def calculate_cpa(cpc, conversion_rate):
     
    return cpc / conversion_rate


# Calcular CPC Máximo
def calculate_max_cpc(commission, conversion_rate):

    return commission * conversion_rate


# Verificar viabilidade da campanha
def feedback_status(cpa, commission):

    status = (
    "Viável (Lucro) 🟢"
    if cpa < commission
    else "Break-even 🟡"
    if cpa == commission
    else "Inviável (Prejuízo) 🔴"
    )
    return status


# Calcular cenários de conversões
def calculate_scenarios(cpc, commission, conversion_rate):
    
    results = []

    cpa_scenario = calculate_cpa(cpc, conversion_rate)
    cpc_max_scenario = calculate_max_cpc(commission, conversion_rate)
    status_scenario = feedback_status(cpa_scenario, commission)
    
    scenario_data = {
    "conversion_rate": conversion_rate,
    "cpa": cpa_scenario,
    "cpc_max": cpc_max_scenario,
    "status": status_scenario
    }
    results.append(scenario_data)
           
    return results


# Formatar casas decimais
def formatDec(valor):

    return f"R${valor:.2f}"




