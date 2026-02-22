from fastapi import APIRouter, Depends, HTTPException

import numpy as np
import pandas as pd


csv_path = "./test.csv"
csv_df = pd.read_csv(csv_path, header=0, dtype=str)

coord_type_deg = True
coord_type_dms_j = True
coord_type_dms_e = True
# coords = csv_df.iloc[:,23]

def dms_to_decimal_series(series: pd.Series) -> pd.Series:
    # 1. 「;」を空白にして一括処理しやすくする
    s = series.str.replace(";", " ", regex=False)

    # 2. DMSパターン抽出
    # 例: 35度23分32.733秒
    pattern = r'(\d+)度(\d+)分([\d.]+)秒'
    
    extracted = s.str.extractall(pattern)

    # 3. float変換（NumPy配列化）
    deg = extracted[0].astype(float).to_numpy()
    minute = extracted[1].astype(float).to_numpy()
    sec = extracted[2].astype(float).to_numpy()

    # 4. 十進数変換（ベクトル演算）
    decimal = deg + minute / 60 + sec / 3600

    # 5. 元の行単位へ再構築
    decimal_series = (
        pd.Series(decimal, index=extracted.index)
        .groupby(level=0)
        .apply(lambda x: ";".join(map(str, x)))
    )

    return decimal_series


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

coords = csv_df.iloc[:, 23].apply(swap_geometry)
print(coords, type(coords))

if coord_type_dms_j:
    converted_series_coords = dms_to_decimal_series(coords)

if "point":
    geom_point_list = converted_series_coords
elif "polyline":
    geom_polyline_list = converted_series_coords
elif "polygon":
    geom_polygon_list = converted_series_coords
