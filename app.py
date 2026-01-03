import streamlit as st, pandas as pd, locale, matplotlib.pyplot as plt, matplotlib.ticker as mtick

from engine import calculate_cpa, calculate_max_cpc, feedback_status, calculate_scenarios


# Configurações da página
st.set_page_config(
    page_title = "ROI Auto Pilot",
    layout = "wide"
)

locale.setlocale(locale.LC_MONETARY,"pt_BR.UTF-8")


# Conteúdo centralizado
st.markdown(
    "<h1 style='text-align: center;'>ROI Auto Pilot</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; font-size:18px;'>Descubra se sua campanha dá lucro antes de investir mais dinheiro</p>",
    unsafe_allow_html=True
)


# Colunas 40/20/40
col_left, spacer, col_right = st.columns([1, 0.25, 1])

with col_left:
    # Inputs
    cpc = st.number_input(
        "Quanto você está pagando por clique hoje?",
        min_value = 0.1,
        step = 0.1
    )
    st.caption("Não sabe o valor exato? Use uma média — o cálculo continua válido")

    commission = st.number_input(
        "Quanto você ganha por cada venda?",
        min_value = 0.1,
        step = 0.1
    )
    st.caption("Valor líquido da comissão (já com taxas, se houver).")

    conversion_rate_pct = st.slider(
        "Qual taxa de conversão você acredita que sua página pode alcançar?",
        min_value = 0.1,
        max_value = 10.0,
        step = 0.1
    )
    st.caption(f"Conversão usada no cálculo: {conversion_rate_pct:.2f}%")

    conversion_rate = conversion_rate_pct / 100


    # Cálculos
    cpa = calculate_cpa(cpc, conversion_rate)

    cpc_max = calculate_max_cpc(commission, conversion_rate)

    results = calculate_scenarios(cpc, commission, conversion_rate)

    # Criação do Dataframe
    df = pd.DataFrame(results)

    df_chart = df.copy()

    rename_results = {
        "conversion_rate": "Taxa de Conversão",
        "cpa": "Custo Por Aquisição",
        "cpc_max": "CPC Máximo",
        "status": "Situação da Campanha"
    }

    transform_data = ['conversion_rate']

    if results:
        df[transform_data] = df[transform_data] * 100
        df['cpa'] = df['cpa'].apply(lambda x: locale.currency(x, grouping=True))

    

    df = df.rename(columns=rename_results)


    # Exibição
    st.metric("Quanto custa gerar uma venda com essa conversão:", f"R${cpa:.2f}")

    st.metric("CPC máximo para não ficar no prejuízo:", f"R${cpc_max:.2f}")
    st.caption("Acima disso, a campanha começa a perder dinheiro.")

    if results:
        st.dataframe(
            df,
            hide_index = True,
            column_config = {
                "Taxa de Conversão": st.column_config.NumberColumn(
                        format = "%.1f %%"
                ),
                "CPC Máximo": st.column_config.NumberColumn(
                        format = f"R${cpc_max:.2f}"
                )
            }
        )

with col_right:
    st.subheader("Aqui está o ponto exato onde sua campanha deixa de dar prejuízo")
    st.caption("Compare seu CPC atual com o CPC máximo e veja se vale a pena escalar.")


    # Criação do gráfico com matplotlib
    fig, ax = plt.subplots(figsize = (10,6), dpi= 100)


    # Formatando dados e lista de cenários de conversão
    cpc_max_value = df_chart["cpc_max"].iloc[0]

    x = [0.003, 0.005, 0.0075, 0.01, 0.0125, 0.0150, 0.0175, 0.02]

    cpc_max_values = []

   
    for rate in x:
        cpc_max = calculate_max_cpc(commission, rate)
        cpc_max_values.append(cpc_max)


    # Linha horizontal - CPC Máximo
    ax.axhline(
        y=cpc,
        linestyle="--",
        linewidth = 1,
        label="CPC Atual",
        color="blue"
    )

    # Linha de comparação CPC Atual X Taxa de Conversão
    ax.plot(
        x,
        cpc_max_values,
        marker = "o",
        label = "CPC Máximo",
        color = "orange"
    )

    
    # Zona de lucro
    ax.fill_between(
        x,
        cpc_max_values,
        cpc,
        where = [cpc <= y for y in cpc_max_values],
        color = "green",
        alpha = 0.2,
        label = "Lucro"
    )

    ax.fill_between(
        x,
        cpc_max_values,
        8,
        where = [cpc <= y for y in cpc_max_values],
        color = "green",
        alpha = 0.2,
    )


    # Zona de Prejuízo
    ax.fill_between( 
        x,
        cpc,
        cpc_max_values,
        where = [cpc > y for y in cpc_max_values],
        color = "red",
        alpha = 0.5,
        label = "Prejuízo"
    )

    ax.fill_between( 
        x,
        0,
        cpc_max_values,
        where = [cpc > y for y in cpc_max_values],
        color = "red",
        alpha = 0.5,
    )


    # Encontrar break-even
    break_even_rate = None

    for rate, cpc_max in zip(x, cpc_max_values):
        if cpc_max >= cpc:
            break_even_rate = rate
            break

    if break_even_rate:
        ax.scatter(
            break_even_rate,
            cpc,
            color = "yellow",
            zorder = 5,
            label = "Break-even"
        )

        ax.axvline(
            x = break_even_rate,
            linestyle = ":",
            color = "black",
            alpha = 0.7
        )

        ax.annotate(
            f"Break-even\n{break_even_rate*100:.2f}%",
            (break_even_rate, cpc),
            textcoords = "offset points",
            xytext = (10, 10),
            fontsize = 9
        )


    # Titulos, legendas e labels
    ax.set_title("Zonas de Lucro, Prejuízo e Break-even")
    ax.set_ylabel("CPC (R$)")
    ax.set_xlabel("Taxa de Conversão (Cenários)")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax = 1))
    ax.legend()


    # Plotando a figura
    st.pyplot(fig)


    # Legendas
    st.caption("🟢 Zona de lucro: cada clique gera retorno positivo")
    st.caption("🟡 Break-even: ponto exato onde não há lucro nem prejuízo")
    st.caption("🔴 Zona de prejuízo: você paga mais por clique do que o negócio suporta")
