class GeoIntelligenceError(Exception):
    """
    Base exception for the Geo-Intelligence Platform.
    """


class DatasetNotFoundError(GeoIntelligenceError):
    """
    Raised when a required platform dataset
    cannot be found.
    """

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path

        super().__init__(f"Required dataset not found: {dataset_path}")
