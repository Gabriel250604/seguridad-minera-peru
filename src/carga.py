import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "data" / "processed" / "accidentes_limpio.csv"

load_dotenv(RAIZ / ".env")


def motor():
    usuario = os.getenv("DB_USER")
    clave = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    base = os.getenv("DB_NAME")
    return create_engine(
        f"postgresql+psycopg2://{usuario}:{clave}@{host}:{puerto}/{base}"
    )


def construir_dimensiones(df):
    empresas = (
        df[["TITULAR"]]
        .drop_duplicates()
        .sort_values("TITULAR")
        .reset_index(drop=True)
    )
    empresas.insert(0, "id_empresa", empresas.index + 1)
    empresas.columns = ["id_empresa", "titular"]

    unidades = (
        df[["UNIDAD", "DEPARTAMENTO", "PROVINCIA", "DISTRITO"]]
        .drop_duplicates()
        .sort_values(["DEPARTAMENTO", "UNIDAD"])
        .reset_index(drop=True)
    )
    unidades.insert(0, "id_unidad", unidades.index + 1)
    unidades.columns = ["id_unidad", "unidad", "departamento", "provincia", "distrito"]

    tipos = (
        df[["TIPO_ACCIDENTE", "FAMILIA_ACCIDENTE"]]
        .drop_duplicates()
        .sort_values("TIPO_ACCIDENTE")
        .reset_index(drop=True)
    )
    tipos.insert(0, "id_tipo", tipos.index + 1)
    tipos.columns = ["id_tipo", "tipo_accidente", "familia"]

    return empresas, unidades, tipos


def construir_hechos(df, empresas, unidades, tipos):
    f = df.merge(empresas, left_on="TITULAR", right_on="titular", how="left")
    f = f.merge(
        unidades,
        left_on=["UNIDAD", "DEPARTAMENTO", "PROVINCIA", "DISTRITO"],
        right_on=["unidad", "departamento", "provincia", "distrito"],
        how="left",
    )
    f = f.merge(tipos, left_on="TIPO_ACCIDENTE", right_on="tipo_accidente", how="left")

    if len(f) != len(df):
        raise ValueError(f"El cruce alteró el número de filas: {len(df)} -> {len(f)}")
    for col in ["id_empresa", "id_unidad", "id_tipo"]:
        if f[col].isna().any():
            raise ValueError(f"Quedaron filas sin {col}")

    f = f.sort_values(["FECHA_ACCIDENTE", "TITULAR", "UNIDAD"]).reset_index(drop=True)

    return pd.DataFrame(
        {
            "id_accidente": range(1, len(f) + 1),
            "id_evento": f["ID_EVENTO"].astype(int),
            "id_empresa": f["id_empresa"].astype(int),
            "id_unidad": f["id_unidad"].astype(int),
            "id_tipo": f["id_tipo"].astype(int),
            "fecha_accidente": f["FECHA_ACCIDENTE"],
            "fecha_fallecimiento": f["FECHA_FALLECIMIENTO"],
            "dias_hasta_fallecimiento": f["DIAS_HASTA_FALLECIMIENTO"].astype("Int64"),
            "fecha_inconsistente": f["FECHA_INCONSISTENTE"].astype(bool),
            "victimas_evento": f["VICTIMAS_EVENTO"].astype(int),
            "categoria": f["CATEGORIA"],
        }
    )


def cargar(engine, empresas, unidades, tipos, hechos):
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE fact_accidente, dim_empresa, dim_unidad, dim_tipo "
                "RESTART IDENTITY CASCADE"
            )
        )

    for tabla, datos in [
        ("dim_empresa", empresas),
        ("dim_unidad", unidades),
        ("dim_tipo", tipos),
        ("fact_accidente", hechos),
    ]:
        datos.to_sql(tabla, engine, if_exists="append", index=False)
        print(f"{tabla}: {len(datos)} filas")


def main():
    df = pd.read_csv(
        ENTRADA, parse_dates=["FECHA_ACCIDENTE", "FECHA_FALLECIMIENTO"]
    )
    empresas, unidades, tipos = construir_dimensiones(df)
    hechos = construir_hechos(df, empresas, unidades, tipos)

    engine = motor()
    cargar(engine, empresas, unidades, tipos, hechos)

    with engine.connect() as conn:
        dias = conn.execute(text("SELECT COUNT(*) FROM dim_tiempo")).scalar()
    print(f"dim_tiempo: {dias} filas")


if __name__ == "__main__":
    main()