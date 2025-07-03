import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

st.set_page_config(page_title="Correlatividad Bonos - Casino", layout="wide")
st.title("🎲 Análisis de Correlación: Bonos vs Retiro / GGR / Acreditaciones")

st.write("Subí tu archivo Excel con los datos diarios del casino. Se analizará la correlación entre BONOS otorgados y las variables: RETIROS, GGR TOTAL y ACREDITACIONES.")

archivo = st.file_uploader("📄 Subí el archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    columnas_obligatorias = ["FECHA", "GGR TOTAL", "BONOS", "ACREDITACIONES", "RETIROS"]

    if not all(col in df.columns for col in columnas_obligatorias):
        st.error("❌ Faltan columnas necesarias en el archivo. Asegurate de incluir: " + ", ".join(columnas_obligatorias))
    else:
        df = df.dropna(subset=columnas_obligatorias)

        df["FECHA"] = pd.to_datetime(df["FECHA"], errors='coerce')
        df = df.sort_values("FECHA")

        # Seleccionamos solo las columnas relevantes
        df_analisis = df[["FECHA", "BONOS", "RETIROS", "GGR TOTAL", "ACREDITACIONES"]].copy()

        # Calcular correlaciones y mostrar tabla
        st.subheader("📊 Tabla de Correlaciones (Pearson)")
        correlaciones = df_analisis[["BONOS", "RETIROS", "GGR TOTAL", "ACREDITACIONES"]].corr(method="pearson")
        st.dataframe(correlaciones.round(2))

        # Mostrar gráficos de dispersión con línea de tendencia
        st.subheader("📈 Gráficos de Dispersión")
        variables = ["RETIROS", "GGR TOTAL", "ACREDITACIONES"]

        for var in variables:
            fig, ax = plt.subplots()
            sns.regplot(data=df_analisis, x="BONOS", y=var, ax=ax, scatter_kws={"color": "#1f77b4"}, line_kws={"color": "#ff7f0e"})
            ax.set_title(f"BONOS vs {var}")
            st.pyplot(fig)

        # Interpretaciones
        st.subheader("🧠 Interpretación Automática")
        interpretaciones = []

        def interpretar(r):
            if abs(r) >= 0.7:
                return "Fuerte correlación"
            elif abs(r) >= 0.4:
                return "Correlación moderada"
            elif abs(r) >= 0.2:
                return "Correlación débil"
            else:
                return "Sin correlación significativa"

        for var in variables:
            r, p = pearsonr(df_analisis["BONOS"], df_analisis[var])
            signo = "positiva" if r > 0 else "negativa"
            interpretaciones.append(f"**Bonos vs {var}**: {interpretar(r)} ({signo}, r = {r:.2f})")

        for texto in interpretaciones:
            st.markdown("- " + texto)

        st.markdown("---")
        st.markdown("💡 **Nota**: La correlación indica si dos variables se mueven juntas, pero no implica causalidad. Es decir, un valor alto de bonos puede estar asociado a mayores retiros, pero eso no significa necesariamente que uno cause al otro.")
