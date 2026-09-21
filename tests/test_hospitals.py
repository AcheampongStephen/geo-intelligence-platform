import geopandas as gpd

DATA_PATH = "data/processed/hospitals.parquet"


def test_dataset_exists():
    gdf = gpd.read_parquet(DATA_PATH)

    assert len(gdf) > 0


def test_names_are_present():
    gdf = gpd.read_parquet(DATA_PATH)

    assert gdf["name"].notna().all()


def test_coordinates_are_valid():
    gdf = gpd.read_parquet(DATA_PATH)

    assert gdf["latitude"].between(-90, 90).all()
    assert gdf["longitude"].between(-180, 180).all()


def test_osm_ids_are_unique():
    gdf = gpd.read_parquet(DATA_PATH)

    assert gdf["osm_id"].is_unique


def test_geometry_is_valid():
    gdf = gpd.read_parquet(DATA_PATH)

    assert gdf.geometry.notna().all()
    assert gdf.geometry.is_valid.all()


def test_coordinate_system():
    gdf = gpd.read_parquet(DATA_PATH)

    assert gdf.crs is not None
