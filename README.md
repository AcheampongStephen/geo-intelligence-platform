\# Geo-Intelligence Platform



A Python-based geospatial data engineering and intelligence platform for analyzing healthcare accessibility using real-world OpenStreetMap data.



The platform currently ingests hospital and pharmacy locations, validates and transforms geospatial data, calculates hospital-to-pharmacy accessibility metrics, generates intelligence scores, and exposes the resulting data through a FastAPI REST API.



The project is being developed incrementally from a local Python implementation toward a production-oriented cloud architecture with data engineering, geospatial analytics, DevSecOps, observability, and AWS infrastructure.



\---



\## Project Status



\*\*Current stage:\*\* Engineering foundation complete.



The current implementation includes:



\- Real-world OpenStreetMap hospital and pharmacy ingestion

\- Geospatial transformation with GeoPandas and Shapely

\- Parquet-based raw, processed, and curated data layers

\- Data-quality validation

\- Nearest-pharmacy analysis

\- Pharmacy coverage analysis at 1 km, 2 km, and 5 km

\- Hospital accessibility scoring

\- FastAPI REST API

\- Environment-based configuration

\- Structured application logging

\- Centralized API exception handling

\- Automated testing with pytest

\- Enforced test-coverage threshold

\- Ruff linting and formatting

\- MyPy static type checking

\- Bandit security scanning

\- Git-based source control and repository hygiene



Cloud infrastructure, PostGIS, containers, CI/CD, streaming, and machine-learning capabilities are part of the planned architecture and are not yet implemented.



\---



\## Problem Statement



Access to nearby pharmacies can be an important component of healthcare accessibility.



This project uses real geospatial data to answer questions such as:



\- What is the nearest pharmacy to each hospital?

\- How far away is that pharmacy?

\- How many pharmacies exist within 1 km, 2 km, and 5 km?

\- Which hospitals have limited pharmacy access?

\- Which locations may represent healthcare-accessibility gaps?

\- How can these metrics be exposed through an API for downstream applications?



The initial study area covers the Columbia, South Carolina region.



\---



\## Current Architecture



```text

&#x20;               OpenStreetMap

&#x20;                    |

&#x20;                    v

&#x20;             Overpass API

&#x20;                    |

&#x20;                    v

&#x20;         Python Data Ingestion

&#x20;                    |

&#x20;                    v

&#x20;            data/raw/\*.json

&#x20;                    |

&#x20;                    v

&#x20;      GeoPandas / Shapely ETL

&#x20;                    |

&#x20;                    v

&#x20;        data/processed/\*.parquet

&#x20;                    |

&#x20;                    v

&#x20;         Data Quality Validation

&#x20;                    |

&#x20;                    v

&#x20;         Geospatial Analytics

&#x20;            /             \\

&#x20;           /               \\

&#x20;          v                 v

&#x20; Nearest Pharmacy    Coverage Analysis

&#x20;                      1 / 2 / 5 km

&#x20;           \\               /

&#x20;            \\             /

&#x20;             v           v

&#x20;         Intelligence Layer

&#x20;                 |

&#x20;                 v

&#x20;    Accessibility Score + Category

&#x20;                 |

&#x20;                 v

&#x20;      Curated Metrics Parquet

&#x20;                 |

&#x20;                 v

&#x20;             FastAPI

&#x20;                 |

&#x20;                 v

&#x20;         REST API Consumers

```



\---



\## Data Pipeline



\### 1. Ingestion



Hospital and pharmacy locations are retrieved from OpenStreetMap through the Overpass API.



The ingestion layer stores source responses as JSON under:



```text

data/raw/

```



Current ingestion modules:



```text

src/ingestion/osm\_ingest.py

src/ingestion/pharmacy\_ingest.py

```



\---



\### 2. Processing



Raw OpenStreetMap objects are transformed into structured geospatial datasets.



The processing layer extracts information such as:



\- OSM object type

\- OSM identifier

\- Facility name

\- Healthcare metadata

\- Address information

\- Latitude

\- Longitude

\- Shapely geometry



Processed geospatial datasets use WGS 84:



```text

EPSG:4326

```



Processing modules:



```text

src/processing/osm\_hospitals.py

src/processing/osm\_pharmacies.py

src/processing/validate\_hospitals.py

```



\---



\### 3. Data Quality



Hospital data is validated before entering the curated layer.



Current error-level checks include:



\- Missing hospital names

\- Missing latitude or longitude

\- Invalid coordinate ranges

\- Duplicate OSM identifiers

\- Invalid geometry



Current warning-level checks include:



\- Missing city

\- Missing state

\- Duplicate coordinates



The validation process produces a quality report and only promotes the hospital dataset when required validation checks pass.



\---



\## Geospatial Analytics



Distance calculations require a projected coordinate system rather than geographic latitude/longitude coordinates.



The analytics layer projects data into:



```text

EPSG:32617

WGS 84 / UTM Zone 17N

```



Distances are therefore calculated in meters before being converted to kilometers.



\### Nearest Pharmacy Analysis



For each hospital, the platform determines the nearest pharmacy and calculates its distance.



Distance categories are:



| Distance | Category |

|---|---|

| < 1 km | VERY\_CLOSE |

| < 2 km | CLOSE |

| < 5 km | MODERATE |

| >= 5 km | FAR |



\### Pharmacy Coverage



For every hospital, the platform calculates the number of pharmacies within:



```text

1 km

2 km

5 km

```



Coverage categories currently use the following rules:



| Condition | Category |

|---|---|

| No pharmacy within 2 km | LOW |

| No pharmacy within 1 km but at least one within 2 km | MODERATE |

| At least 2 pharmacies within 1 km | HIGH |

| Otherwise | GOOD |



Analytics modules:



```text

src/analytics/hospital\_pharmacy\_analysis.py

src/analytics/pharmacy\_coverage.py

```



\---



\## Intelligence Layer



The platform combines nearest-pharmacy distance and pharmacy-density information into an accessibility score.



The maximum score is:



```text

100

```



\### Distance Component



Maximum: \*\*40 points\*\*



| Nearest Pharmacy | Points |

|---|---:|

| <= 1 km | 40 |

| <= 2 km | 30 |

| <= 5 km | 20 |

| <= 10 km | 10 |

| > 10 km or unavailable | 0 |



\### Pharmacy Density Within 1 km



Maximum: \*\*30 points\*\*



| Pharmacies | Points |

|---|---:|

| >= 3 | 30 |

| 2 | 25 |

| 1 | 15 |

| 0 | 0 |



\### Pharmacy Density Within 5 km



Maximum: \*\*30 points\*\*



| Pharmacies | Points |

|---|---:|

| >= 10 | 30 |

| 5–9 | 25 |

| 2–4 | 15 |

| 1 | 5 |

| 0 | 0 |



\### Accessibility Categories



| Score | Category |

|---|---|

| 80–100 | HIGH\_ACCESS |

| 60–79 | MODERATE\_ACCESS |

| 40–59 | LIMITED\_ACCESS |

| 0–39 | LOW\_ACCESS |



Implementation:



```text

src/intelligence/hospital\_pharmacy\_metrics.py

```



These scores are project-defined analytical indicators and should not be interpreted as clinical assessments or official healthcare-accessibility standards.



\---



\## Current Dataset Snapshot



The current local pipeline processes:



```text

Hospitals:   14

Pharmacies:  48

```



Current analysis identified:



```text

Hospitals with pharmacy within 1 km:   7

Hospitals with pharmacy within 2 km:   9

Hospitals with pharmacy within 5 km:  13



Average nearest-pharmacy distance:  2.21 km

Maximum nearest-pharmacy distance: 11.05 km

```



Current accessibility categories:



```text

HIGH\_ACCESS:      6

MODERATE\_ACCESS:  2

LIMITED\_ACCESS:   2

LOW\_ACCESS:       4

```



These values represent the current local OpenStreetMap-derived dataset and may change when source data or geographic coverage changes.



\---



\## REST API



The intelligence dataset is exposed through FastAPI.



API implementation:



```text

src/api/main.py

```



Current endpoints include:



| Method | Endpoint | Purpose |

|---|---|---|

| GET | `/` | Service information |

| GET | `/health` | Application and dataset health |

| GET | `/hospitals` | Retrieve hospitals |

| GET | `/hospitals/{hospital\_id}` | Retrieve one hospital |

| GET | `/hospitals/{hospital\_id}/pharmacy-access` | Retrieve pharmacy-access intelligence |

| GET | `/analytics/summary` | Retrieve aggregate analytics |



The API includes centralized exception handling and avoids exposing internal dataset paths in missing-dataset responses.



\---



\## Configuration



Application configuration is managed with `pydantic-settings`.



Create the local environment file from the example:



```bash

cp .env.example .env

```



Default configuration:



```env

APP\_NAME=Geo-Intelligence Platform API

APP\_VERSION=1.0.0

ENVIRONMENT=development

LOG\_LEVEL=INFO

DATA\_DIR=data

METRICS\_PATH=data/curated/hospital\_pharmacy\_metrics.parquet

```



The real `.env` file is intentionally excluded from Git.



\---



\## Installation



\### Requirements



\- Python 3.12

\- Conda or another Python environment manager

\- Git



Clone the repository and enter the project directory:



```bash

git clone <repository-url>

cd geo-intelligence-platform

```



Create and activate an environment. For example:



```bash

conda create -n geo-intel python=3.12

conda activate geo-intel

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Create local configuration:



```bash

cp .env.example .env

```



\---



\## Running the Data Pipeline



The current pipeline can be executed incrementally.



\### Hospital ingestion



```bash

python src/ingestion/osm\_ingest.py

```



\### Pharmacy ingestion



```bash

python src/ingestion/pharmacy\_ingest.py

```



\### Hospital processing



```bash

python src/processing/osm\_hospitals.py

```



\### Pharmacy processing



```bash

python src/processing/osm\_pharmacies.py

```



\### Hospital validation



```bash

python src/processing/validate\_hospitals.py

```



\### Nearest-pharmacy analysis



```bash

python src/analytics/hospital\_pharmacy\_analysis.py

```



\### Pharmacy coverage



```bash

python src/analytics/pharmacy\_coverage.py

```



\### Intelligence metrics



```bash

python src/intelligence/hospital\_pharmacy\_metrics.py

```



\---



\## Running the API



After generating the curated metrics dataset:



```bash

uvicorn src.api.main:app --reload

```



The API is then available locally at:



```text

http://127.0.0.1:8000

```



FastAPI interactive documentation is available at:



```text

http://127.0.0.1:8000/docs

```



\---



\## Testing



Run the complete test suite:



```bash

pytest

```



The project currently contains:



```text

55 automated tests

```



The test suite covers:



\- Hospital dataset validation

\- API behavior

\- Missing-resource handling

\- JSON-safe API responses

\- Degraded health behavior

\- Pharmacy coverage classification

\- Geospatial radius counting

\- Accessibility scoring boundaries

\- Accessibility category boundaries



Coverage is automatically measured by pytest.



The repository enforces a minimum total coverage threshold of:



```text

65%

```



Current measured coverage:



```text

67.86%

```



The coverage threshold is intended as a regression guard and can be increased as pipeline orchestration is refactored into smaller testable units.



\---



\## Code Quality



\### Ruff



Lint:



```bash

ruff check src tests

```



Check formatting:



```bash

ruff format --check src tests

```



\### MyPy



Check application code:



```bash

mypy src

```



Check tests:



```bash

mypy tests

```



\### Bandit



Run static security analysis:



```bash

bandit -r src

```



Current engineering baseline:



```text

Ruff linting       PASS

Ruff formatting    PASS

MyPy source        PASS

MyPy tests         PASS

Bandit findings    0

Pytest             55 passed

Coverage           67.86%

Coverage minimum   65%

```



\---



\## Project Structure



```text

geo-intelligence-platform/

|

|-- data/

|   |-- raw/

|   |-- processed/

|   `-- curated/

|

|-- notebooks/

|

|-- src/

|   |-- analytics/

|   |   |-- debug\_pharmacy\_distance.py

|   |   |-- hospital\_pharmacy\_analysis.py

|   |   `-- pharmacy\_coverage.py

|   |

|   |-- api/

|   |   |-- exception\_handlers.py

|   |   |-- exceptions.py

|   |   `-- main.py

|   |

|   |-- config/

|   |   |-- logging.py

|   |   `-- settings.py

|   |

|   |-- ingestion/

|   |   |-- osm\_ingest.py

|   |   `-- pharmacy\_ingest.py

|   |

|   |-- intelligence/

|   |   `-- hospital\_pharmacy\_metrics.py

|   |

|   `-- processing/

|       |-- osm\_hospitals.py

|       |-- osm\_pharmacies.py

|       `-- validate\_hospitals.py

|

|-- tests/

|   |-- test\_analytics.py

|   |-- test\_api.py

|   |-- test\_hospitals.py

|   `-- test\_intelligence.py

|

|-- .env.example

|-- .gitignore

|-- pytest.ini

|-- requirements.txt

|-- requirements-lock.txt

`-- README.md

```



Generated datasets are excluded from Git. `.gitkeep` files preserve the data-layer directory structure.



\---



\## Planned Architecture



The project is designed to evolve from the current local implementation toward a cloud-native geospatial intelligence platform.



```text

&#x20;                    External Data Sources

&#x20;                   /                     \\

&#x20;                  v                       v

&#x20;          OpenStreetMap              Future Sources

&#x20;                  \\                       /

&#x20;                   \\                     /

&#x20;                    v                   v

&#x20;                        Ingestion

&#x20;                           |

&#x20;                           v

&#x20;                      Amazon S3

&#x20;                Raw / Processed / Curated

&#x20;                           |

&#x20;               +-----------+-----------+

&#x20;               |                       |

&#x20;               v                       v

&#x20;         Python / Spark              Athena

&#x20;               |

&#x20;               v

&#x20;      PostgreSQL + PostGIS

&#x20;               |

&#x20;      +--------+---------+

&#x20;      |                  |

&#x20;      v                  v

&#x20;  OpenSearch          DynamoDB

&#x20;      \\                  /

&#x20;       \\                /

&#x20;        v              v

&#x20;           Application Layer

&#x20;                  |

&#x20;            API Gateway

&#x20;                  |

&#x20;                 WAF

&#x20;                  |

&#x20;                  v

&#x20;             Web / Mobile

```



The exact cloud architecture will evolve as each infrastructure phase is implemented.



\---



\## Development Roadmap



\### Phase 0 — Core Prototype



\*\*Complete\*\*



\- OpenStreetMap ingestion

\- Hospital processing

\- Pharmacy processing

\- Geospatial analysis

\- Accessibility intelligence

\- FastAPI service



\### Phase 1 — Engineering Foundation



\*\*Complete\*\*



\- Dependency management

\- Environment configuration

\- Structured logging

\- Centralized error handling

\- Ruff

\- MyPy

\- Bandit

\- pytest

\- Coverage enforcement

\- Git repository hygiene

\- Architecture documentation



\### Phase 2 — PostgreSQL + PostGIS



Planned:



\- PostgreSQL database

\- PostGIS extension

\- Database schema

\- SQLAlchemy integration

\- Spatial persistence

\- Spatial queries

\- Database-backed API



\### Phase 3 — Containers



Planned:



\- Dockerfile

\- Docker Compose

\- Containerized API

\- Containerized database

\- Health checks

\- Image security scanning



\### Phase 4 — AWS Data Lake



Planned:



\- Amazon S3

\- Raw / processed / curated zones

\- IAM

\- Encryption

\- Athena

\- Cloud-based pipeline execution



\### Phase 5 — AWS Application Architecture



Planned:



\- Managed application services

\- API Gateway

\- AWS WAF

\- RDS PostgreSQL

\- Secrets management

\- Production networking



\### Phase 6 — Infrastructure as Code



Planned:



\- Terraform

\- Reusable modules

\- Remote state

\- Environment separation



\### Phase 7 — CI/CD + DevSecOps



Planned:



\- GitHub Actions

\- Automated tests

\- Ruff and MyPy gates

\- Bandit

\- Dependency security scanning

\- Container scanning

\- Infrastructure scanning

\- Automated deployment workflow



\### Phase 8 — Observability + Security



Planned:



\- CloudWatch

\- CloudTrail

\- GuardDuty

\- Security Hub

\- Centralized logging

\- Metrics and alerts

\- Least-privilege IAM

\- KMS encryption



\### Phase 9 — Streaming and Scale



Planned:



\- Streaming ingestion

\- Distributed processing

\- Larger geographic coverage

\- Scalable geospatial workloads



\### Phase 10 — Intelligence / Machine Learning



Planned:



\- Accessibility anomaly detection

\- Geospatial clustering

\- Predictive analytics

\- Automated intelligence generation



\### Phase 11 — Visualization and Portfolio Delivery



Planned:



\- Interactive dashboard

\- Maps

\- Architecture diagrams

\- Deployment documentation

\- Portfolio case study



\---



\## Engineering Principles



This project follows several core engineering principles:



1\. \*\*Real data over synthetic demonstrations\*\*  

&#x20;  The platform uses real OpenStreetMap geospatial data.



2\. \*\*Reproducible pipelines\*\*  

&#x20;  Generated datasets are treated as pipeline artifacts rather than source code.



3\. \*\*Data quality before analytics\*\*  

&#x20;  Validation occurs before datasets enter the curated analytical layer.



4\. \*\*Correct geospatial calculations\*\*  

&#x20;  Distance calculations use an appropriate projected coordinate reference system.



5\. \*\*Configuration outside application logic\*\*  

&#x20;  Environment-specific values are managed through application settings.



6\. \*\*Security by design\*\*  

&#x20;  Secrets are excluded from source control and static security analysis is part of the engineering workflow.



7\. \*\*Automated quality gates\*\*  

&#x20;  Testing, coverage, linting, formatting, typing, and security scanning are continuously enforceable.



8\. \*\*Incremental cloud migration\*\*  

&#x20;  Local functionality is established and validated before equivalent production infrastructure is introduced.



\---



\## Data Source



Current geospatial facility data is derived from OpenStreetMap through the Overpass API.



OpenStreetMap data quality and completeness can vary by location. Results therefore reflect the available source data at ingestion time and should not be interpreted as an authoritative registry of healthcare facilities.



\---



\## Author



\*\*Stephen Acheampong\*\*



Geo-Intelligence Platform — Python, geospatial data engineering, APIs, cloud architecture, and DevSecOps.

