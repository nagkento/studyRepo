from fastapi import APIRouter, Depends, HTTPException

import numpy as np
import pandas as pd

coord_type_deg = True
coord_type_dms_j = True
coord_type_dms_e = True
# coords = csv_df.iloc[:,23]

def conver_to_decimal_series(series: pd.Series, pattern) -> pd.Series:
    # 1. ; で分解（ポリライン対応）
    exploded = series.str.split(";").explode()

    # 2. DMS抽出
    pattern = r'(\d+)度(\d+)分([\d.]+)秒'
    extracted = exploded.str.extractall(pattern)

    if extracted.empty:
        result = pd.Series(index=series.index, dtype=str)
    else:
        # 3. NumPy高速変換
        deg = extracted[0].to_numpy(dtype=np.float64)
        minute = extracted[1].to_numpy(dtype=np.float64)
        sec = extracted[2].to_numpy(dtype=np.float64)

        decimal = deg + minute/60 + sec/3600

        # 4. 緯度経度ペアへ整形（2個ずつまとめる）
        decimal_pairs = decimal.reshape(-1, 2)

        # 5. "lat lon" 形式へ
        formatted = np.char.add(
            decimal_pairs[:, 0].astype(str),
            np.char.add(" ", decimal_pairs[:, 1].astype(str))
        )

        # 6. explodedのindexに合わせて戻す
        formatted_series = pd.Series(formatted, index=exploded.index)

        # 7. 元の行へ戻す（;で連結）
        result = formatted_series.groupby(level=0).agg(";".join)

def swap_geometry(coord_string: str) -> str:
    if not isinstance(coord_string, str) or coord_string.strip() == "":
        return coord_string
    # ; を空白にして一括パース
    arr = np.fromstring(
        coord_string.replace(";", " "),
        sep=" ")
    # 要素数チェック（偶数でなければ異常）
    if arr.size % 2 != 0:
        return coord_string     
    arr = arr.reshape(-1, 2)
    # 列入れ替え（lat lon → lon lat）
    arr = arr[:, ::-1]

    # 1点だけの場合（ポイント）
    if arr.shape[0] == 1:
        return f"{arr[0,0]} {arr[0,1]}"

    # 複数点（ポリライン）
    return ";".join(" ".join(map(str, row)) for row in arr)


########
import pandas as pd
import numpy as np
import re


def convert_and_swap_series(series: pd.Series, pattern) -> pd.Series:
    """
    ・DMSなら十進数へ変換
    ・lat lon → lon lat へ変換
    ・ポイント／ポリライン両対応
    ・完全ベクトル化（大量データ対応）
    """

    # -----------------------------
    # ① DMSかどうかをSeries全体で判定（1回だけ）
    # -----------------------------
    is_dms_j = series.str.contains("度", regex=False).any()
    is_dms_e = series.str.contains("゜", regex=False).any()

    # -----------------------------
    # ② DMS → 十進数変換（必要な場合のみ）
    # -----------------------------
    if is_dms_j:

        exploded = series.str.split(";").explode()
        """
        exploadedの中身     
        0    35度30分0秒 140度15分0秒
        1    35度30分0秒 140度15分0秒
        1    35度45分30秒 140度30分30秒
        dtype: object        
        """


        # pattern = r'(\d+)度(\d+)分([\d.]+)秒'
        extracted = exploded.str.extractall(pattern)
        """
        extractedの中身  
               1マッチ     2マッチ   
        0    35 30 0     140 15 0
        1    35 30 0     140 15 0
        1    35 45 30    140 30 30
        dtype: object        
        """


        if extracted.empty:
            return series

        # NumPy高速変換
        deg = extracted[0].to_numpy(dtype=np.float64)
        minute = extracted[1].to_numpy(dtype=np.float64)
        sec = extracted[2].to_numpy(dtype=np.float64)

        decimal = deg + minute / 60 + sec / 3600

        # 2個ずつペア化（lat lon）
        decimal = decimal.reshape(-1, 2)

        formatted = np.char.add(
            decimal[:, 0].astype(str),
            np.char.add(" ", decimal[:, 1].astype(str))
        )

        formatted_series = pd.Series(formatted, index=exploded.index)

        series = formatted_series.groupby(level=0).agg(";".join)

    # -----------------------------
    # ③ lat lon → lon lat 入れ替え（全体一括）
    # -----------------------------
    exploded = series.str.split(";").explode()

    # ;を空白化して一括数値化
    arr = np.fromstring(
        " ".join(exploded.values).replace(";", " "),
        sep=" "
    )

    if arr.size % 2 != 0:
        return series  # 異常データ保護

    arr = arr.reshape(-1, 2)

    # 列入れ替え（lat lon → lon lat）
    arr = arr[:, ::-1]

    # 再構築
    swapped = pd.Series(
        np.char.add(
            arr[:, 0].astype(str),
            np.char.add(" ", arr[:, 1].astype(str))
        ),
        index=exploded.index
    )

    result = swapped.groupby(level=0).agg(";".join)

    return result


########




csv_path = "./test.csv"
csv_df = pd.read_csv(csv_path, header=0, dtype=str)

if "point":
 
    converted_series_coords = dms_to_decimal_series(coords)
    geom_point_list = converted_series_coords
elif "polyline":
    if coord_type_dms_e:
        pattern = r'(\d+)°(\d+)\'([\d.]+)"'
    if coord_type_dms_j:
        pattern = r'(\d+)度(\d+)分([\d.]+)秒'
    dcml_series_coords = convert_and_swap_series(csv_df.iloc[:, 23], pattern)
    converted_series_coords = (coords)
    geom_polyline_list = converted_series_coords
elif "polygon":
    coords = csv_df.iloc[:, 23].apply(swap_geometry)
    converted_series_coords = dms_to_decimal_series(coords)
    geom_polygon_list = converted_series_coords
