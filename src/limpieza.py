from pathlib import Path

import pandas as pd

from mapeo_familias import FAMILIAS

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "data" / "raw" / "2_Accidentes_Mortales_en_Mina.csv"
SALIDA = RAIZ / "data" / "processed" / "accidentes_limpio.csv"

CLAVE_EVENTO = [
    "TITULAR",
    "UNIDAD",
    "DEPARTAMENTO",
    "PROVINCIA",
    "DISTRITO",
    "TIPO_ACCIDENTE",
    "CATEGORIA",
    "FECHA_ACCIDENTE",
]

ANIOS_SUBREGISTRO = {2017, 2018, 2019}


def cargar():
    return pd.read_csv(ENTRADA, sep=";", encoding="latin-1")


def normalizar_texto(serie, mayusculas=False):
    s = (
        serie.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )
    return s.str.upper() if mayusculas else s


def limpiar(df):
    for col in ["TITULAR", "UNIDAD", "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "TIPO_ACCIDENTE"]:
        df[col] = normalizar_texto(df[col], mayusculas=True)

    df["CATEGORIA"] = normalizar_texto(df["CATEGORIA"]).fillna("No informado")

    for col in ["DEPARTAMENTO", "PROVINCIA", "DISTRITO"]:
        df[col] = df[col].fillna("NO ESPECIFICADO")

    df["ID_EVENTO"] = df.groupby(CLAVE_EVENTO, dropna=False).ngroup() + 1
    df["VICTIMAS_EVENTO"] = df.groupby("ID_EVENTO")["ID_EVENTO"].transform("size")

    df["FAMILIA_ACCIDENTE"] = df["TIPO_ACCIDENTE"].map(FAMILIAS)

    df["FECHA_ACCIDENTE"] = pd.to_datetime(
        df["FECHA_ACCIDENTE"], format="%d/%m/%Y", errors="coerce"
    )
    df["FECHA_FALLECIMIENTO"] = pd.to_datetime(
        df["FECHA_FALLECIMIENTO"], format="%d/%m/%Y", errors="coerce"
    )

    dias = (df["FECHA_FALLECIMIENTO"] - df["FECHA_ACCIDENTE"]).dt.days
    df["FECHA_INCONSISTENTE"] = dias < 0
    df["DIAS_HASTA_FALLECIMIENTO"] = dias.where(dias >= 0)

    df["ANIO"] = df["FECHA_ACCIDENTE"].dt.year
    df["MES"] = df["FECHA_ACCIDENTE"].dt.month
    df["TRIMESTRE"] = df["FECHA_ACCIDENTE"].dt.quarter
    df["DATO_CONFIABLE"] = ~df["ANIO"].isin(ANIOS_SUBREGISTRO)

    return df


def validar(df):
    sin_familia = df["FAMILIA_ACCIDENTE"].isna().sum()
    if sin_familia:
        faltantes = df.loc[df["FAMILIA_ACCIDENTE"].isna(), "TIPO_ACCIDENTE"].unique()
        raise ValueError(f"Tipos sin familia asignada: {list(faltantes)}")

    if df["FECHA_ACCIDENTE"].isna().any():
        raise ValueError("Hay fechas de accidente que no se pudieron convertir")

    print("Victimas:", len(df))
    print("Eventos:", df["ID_EVENTO"].nunique())
    print("Familias:", df["FAMILIA_ACCIDENTE"].nunique())
    print("Fechas inconsistentes:", int(df["FECHA_INCONSISTENTE"].sum()))
    print("Registros en anios con subregistro:", int((~df["DATO_CONFIABLE"]).sum()))
    print("Categoria 'No informado':", int((df["CATEGORIA"] == "No informado").sum()))
    print()
    print(df["FAMILIA_ACCIDENTE"].value_counts().to_string())


def main():
    df = cargar()
    df = limpiar(df)
    validar(df)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False, encoding="utf-8")
    print()
    print("Escrito:", SALIDA)


if __name__ == "__main__":
    main()