import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import numpy as np

st.set_page_config(page_title="Correlatividad Bonos - Casino", layout="wide")
st.title("🎲 Análisis de Impacto y Correlación: Bonos vs Retiros / GGR / Acreditaciones")

st.write("Subí tu archivo Excel con los datos diarios del casino. Se analizará la correlación y el impacto porcentual de los BONOS otorgados sobre RETIROS, GGR TOTAL y ACREDITACIONES.")

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

        # Cálculos adicionales
        df["% BONOS vs GGR"] = (df["BONOS"] / df["GGR TOTAL"]) * 100
        df["% BONOS vs RETIROS"] = (df["BONOS"] / df["RETIROS"]) * 100
        df["% BONOS vs ACREDITACIONES"] = (df["BONOS"] / df["ACREDITACIONES"]) * 100

        st.subheader("📊 Tabla de Correlaciones (Pearson)")
        correlaciones = df[["BONOS", "RETIROS", "GGR TOTAL", "ACREDITACIONES"]].corr(method="pearson")
        st.dataframe(correlaciones.round(2))

        st.subheader("📈 Gráficos de Dispersión")
        variables = ["RETIROS", "GGR TOTAL", "ACREDITACIONES"]

        for var in variables:
            fig, ax = plt.subplots()
            sns.regplot(data=df, x="BONOS", y=var, ax=ax, scatter_kws={"color": "#1f77b4"}, line_kws={"color": "#ff7f0e"})
            ax.set_title(f"BONOS vs {var}")
            st.pyplot(fig)

        st.subheader("📊 Bonos como % del GGR, Retiros y Acreditaciones")
        st.dataframe(df[["FECHA", "% BONOS vs GGR", "% BONOS vs RETIROS", "% BONOS vs ACREDITACIONES"]].round(2))

        st.subheader("📦 Impacto por Intervalo de Bonos")

        # Definir intervalos automáticos por cuantiles o por estrategia de corte propia
        q = df["BONOS"].quantile([0, 0.25, 0.5, 0.75, 1.0]).values

        bins = [q[0], q[1], q[2], q[3], q[4]]
        etiquetas = ["bajo", "medio", "alto", "muy alto"]
        df["nivel_bonos"] = pd.cut(df["BONOS"], bins=bins, labels=etiquetas, include_lowest=True)

        # Mostrar los rangos generados
        rangos = pd.DataFrame({
            "Intervalo bono": [f"{int(bins[i]):,} - {int(bins[i+1]):,}" for i in range(len(bins)-1)],
            "Clasificación": etiquetas
        })
        st.write("### Rangos definidos para clasificación de bonos por día")
        st.dataframe(rangos)

        # Calcular resumen
        resumen = df.groupby("nivel_bonos").agg({
            "RETIROS": "mean",
            "GGR TOTAL": "mean",
            "ACREDITACIONES": "mean",
            "BONOS": "mean"
        }).round(2).reset_index()

        base = resumen.iloc[0]
        resumen["% Retiros vs Bajo"] = resumen["RETIROS"] / base["RETIROS"] * 100 - 100
        resumen["% GGR vs Bajo"] = resumen["GGR TOTAL"] / base["GGR TOTAL"] * 100 - 100
        resumen["% Acreditaciones vs Bajo"] = resumen["ACREDITACIONES"] / base["ACREDITACIONES"] * 100 - 100

        st.dataframe(resumen)

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
            r, p = pearsonr(df["BONOS"], df[var])
            signo = "positiva" if r > 0 else "negativa"
            interpretaciones.append(f"**Bonos vs {var}**: {interpretar(r)} ({signo}, r = {r:.2f})")

        for texto in interpretaciones:
            st.markdown("- " + texto)

        st.markdown("---")
        st.markdown("💡 **Nota**: La correlación indica si dos variables se mueven juntas, pero no implica causalidad. El análisis porcentual te ayuda a entender el peso real de los bonos en la actividad financiera del casino.")
