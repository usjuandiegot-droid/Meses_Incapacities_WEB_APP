import os
import pandas as pd

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

OUTPUT_FOLDER = "outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
def limpiar_outputs():

    for archivo in os.listdir(OUTPUT_FOLDER):

        ruta = os.path.join(
            OUTPUT_FOLDER,
            archivo
        )

        try:
            if os.path.isfile(ruta):
                os.remove(ruta)

        except Exception as e:
            print(f"No se pudo eliminar {ruta}: {e}")

# ==========================================================
# FUNCIONES AUXILIARES
# ==========================================================

def cortar_por_mes(inicio, fin):
    """
    Divide un rango de fechas en segmentos mensuales
    y calcula los días correspondientes a cada mes.
    """

    if pd.isna(inicio) or pd.isna(fin):
        return []

    if fin < inicio:
        return []

    resultado = []

    cur = inicio.normalize()
    fin = fin.normalize()

    while cur <= fin:

        ultimo_mes = (
            pd.Timestamp(cur.year, cur.month, 1)
            + pd.offsets.MonthEnd(1)
        )

        hasta = min(ultimo_mes, fin)

        dias = (hasta - cur).days + 1

        resultado.append({
            "Año": cur.year,
            "Mes": cur.month,
            "Mes_Año": f"{cur.year}-{cur.month:02d}",
            "Total Días": dias
        })

        cur = hasta + pd.Timedelta(days=1)

    return resultado


def list_len(valor):
    """
    Devuelve el tamaño de una lista.
    """

    if isinstance(valor, list):
        return len(valor)

    return 0

# ==========================================================
# PROCESAMIENTO PRINCIPAL
# ==========================================================

def procesar_archivo(ruta_entrada, nombre_salida):

    ruta_salida = os.path.join(
        OUTPUT_FOLDER,
        nombre_salida
    )

    # ------------------------------------------------------
    # CARGA DEL ARCHIVO
    # ------------------------------------------------------

    df = pd.read_excel(ruta_entrada)

    df.columns = df.columns.str.strip()
    for columna in df.columns:
        if columna.lower() in ["codigo", "código"]:
            df.rename(
                columns={columna: "Codigo"},
                inplace=True
            )
            break

    # ------------------------------------------------------
    # VALIDACIÓN DE COLUMNAS
    # ------------------------------------------------------

    col_ini = "Fecha de Inicio"
    col_fin = "Fecha de Fin"

    if col_ini not in df.columns or col_fin not in df.columns:
        raise KeyError(
            f"Faltan columnas esperadas: {col_ini} o {col_fin}"
        )


    # ------------------------------------------------------
    # PREPARACIÓN DE FECHAS
    # ------------------------------------------------------

    df[col_ini] = pd.to_datetime(
        df[col_ini],
        errors="coerce"
    )

    df[col_fin] = pd.to_datetime(
        df[col_fin],
        errors="coerce"
    )


    # Índice original para trazabilidad

    df = df.reset_index(drop=True)

    df["__orig_row"] = df.index + 1


    # Fechas inválidas

    df["Flag_Fecha_Invalida"] = (
        df[col_ini].isna()
        |
        df[col_fin].isna()
    )


    # ------------------------------------------------------
    # CORRECCIÓN FECHAS INVERTIDAS
    # ------------------------------------------------------

    swap_mask = (
        (~df["Flag_Fecha_Invalida"])
        &
        (df[col_fin] < df[col_ini])
    )
    
    df.loc[
        swap_mask,
        [col_ini, col_fin]
    ] = df.loc[
        swap_mask,
        [col_fin, col_ini]
    ].to_numpy()

    # ------------------------------------------------------
    # DIVISIÓN POR MESES
    # ------------------------------------------------------

    df["__mensual"] = df.apply(
        lambda fila: cortar_por_mes(
            fila[col_ini],
            fila[col_fin]
        ),
        axis=1
    )


    # Para registros sin rango válido

    mask_empty = (
        df["__mensual"]
        .apply(list_len)
        == 0
    )


    if mask_empty.any():

        df.loc[
            mask_empty,
            "__mensual"
        ] = [[{

            "Año": pd.NA,
            "Mes": pd.NA,
            "Mes_Año": None,
            "Total Días": 0

        }]] * mask_empty.sum()



    # ------------------------------------------------------
    # EXPLODE DE MESES
    # ------------------------------------------------------

    det = df.explode(
        "__mensual",
        ignore_index=True
    )


    det = pd.concat(
        [
            det.drop(columns="__mensual"),
            det["__mensual"].apply(pd.Series)
        ],
        axis=1
    )



    # ------------------------------------------------------
    # VALIDACIÓN CÓDIGO
    # ------------------------------------------------------

    if "Codigo" not in df.columns:

        raise KeyError(
            "La columna 'Codigo' no existe en el archivo."
        )

    # ------------------------------------------------------
    # CREACIÓN TABLA MENSUAL
    # ------------------------------------------------------

    tabla = det.pivot_table(

        index=[
            "__orig_row",
            "Codigo"
        ],

        columns="Mes_Año",

        values="Total Días",

        aggfunc="sum",

        fill_value=0

    ).reset_index()



    # Eliminar columna None si existe

    if None in tabla.columns:

        tabla = tabla.drop(
            columns=[None]
        )



    # ------------------------------------------------------
    # ORDENAR MESES CRONOLÓGICAMENTE
    # ------------------------------------------------------

    mes_cols = [

        columna

        for columna in tabla.columns

        if isinstance(columna, str)

        and columna[:4].isdigit()

        and "-" in columna

    ]


    mes_cols = sorted(
        mes_cols
    )


    otras_cols = [

        columna

        for columna in tabla.columns

        if columna not in mes_cols

    ]


    tabla = tabla[
        otras_cols + mes_cols
    ]

    
    # ------------------------------------------------------
    # RECUPERAR INFORMACIÓN ORIGINAL
    # ------------------------------------------------------

    cols_originales = [

        columna

        for columna in df.columns

        if columna != "__mensual"

    ]


    tabla = tabla.merge(

        df[cols_originales],

        on=[
            "__orig_row",
            "Codigo"
        ],

        how="left"

    )



    # Columnas finales:
    # Primero información original
    # Luego meses

    columnas_finales = [

        columna

        for columna in cols_originales

        if columna in tabla.columns

    ] + mes_cols


    tabla = tabla[
        columnas_finales
    ]

    # Eliminar columnas internas de control

    tabla = tabla.drop(
        columns=[
            "__orig_row",
            "Flag_Fecha_Invalida"
        ],
        errors="ignore"
    )
    # ------------------------------------------------------
    # GUARDAR RESULTADO
    # ------------------------------------------------------

    with pd.ExcelWriter(
        ruta_salida,
        engine="openpyxl"
    ) as writer:

        tabla.to_excel(
            writer,
            index=False,
            sheet_name="DATA"
        )


    print("==============================")
    print("PROCESAMIENTO FINALIZADO")
    print(f"Entrada: {ruta_entrada}")
    print(f"Salida: {ruta_salida}")
    print(f"Filas originales: {len(df)}")
    print(f"Filas resultado: {len(tabla)}")
    print("==============================")

    print(f"Existe archivo: {os.path.exists(ruta_salida)}")

    if os.path.exists(ruta_salida):
        print(f"Tamaño archivo: {os.path.getsize(ruta_salida)} bytes")
    return ruta_salida

# ==========================================================
# PROCESAMIENTO COLOMBIA
# ==========================================================

def procesar_colombia(ruta_entrada):

    return procesar_archivo(
        ruta_entrada,
        "GLOBANT COLOMBIA Wide.xlsx"
    )



# ==========================================================
# PROCESAMIENTO PERÚ
# ==========================================================

def procesar_peru(ruta_entrada):

    return procesar_archivo(
        ruta_entrada,
        "GLOBANT PERU Wide.xlsx"
    )
