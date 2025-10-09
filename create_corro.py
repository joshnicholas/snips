def build_correspondence(big, little, big_id_col, little_id_col, big_stem, little_stem, out_path, area_crs="EPSG:3577"):
    import geopandas as gpd
    from shapely import make_valid

    big = big[[big_id_col, "geometry"]].copy()
    little = little[[little_id_col, "geometry"]].copy()

    big["geometry"] = big.geometry.apply(make_valid)
    little["geometry"] = little.geometry.apply(make_valid)

    big = big.to_crs(area_crs)
    little = little.to_crs(area_crs)

    # little = little[little.area > 0]
    # big = big[big.area > 0]

    little_areas = little.assign(little_area_m2=little.area)[[little_id_col, "little_area_m2"]]

    inter = gpd.overlay(
        little[[little_id_col, "geometry"]],
        big[[big_id_col, "geometry"]],
        how="intersection",
    )

    inter["int_area_m2"] = inter.area
    inter = inter[inter["int_area_m2"] > 0]

    inter_agg = inter.groupby([little_id_col, big_id_col], as_index=False)["int_area_m2"].sum()
    inter_agg = inter_agg.merge(little_areas, on=little_id_col, how="left")
    inter_agg[f"share_of_{little_stem}"] = (inter_agg["int_area_m2"] / inter_agg["little_area_m2"]) * 100

    out = inter_agg.rename(columns={little_id_col: little_stem, big_id_col: big_stem})[
        [little_stem, big_stem, f"share_of_{little_stem}"]
    ]

    out[little_stem] = out[little_stem].astype(str)
    out[big_stem] = out[big_stem].astype(str)

    out.to_csv(out_path, index=False)
