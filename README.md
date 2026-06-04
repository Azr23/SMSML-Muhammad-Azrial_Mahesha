# Eksperimen SML Muhammad-Azrial

Struktur proyek ini dibagi menjadi preprocessing dan modelling lokal yang memakai dataset hasil preprocessing, bukan dataset mentah.

- `.workflow/namadataset_raw/phishing_email_detection_2026_dataset.csv` sebagai dataset mentah.
- `preprocessing/Eksperimen_Muhammad-Azrial.ipynb` sebagai notebook eksperimen manual.
- `preprocessing/automate_Muhammad-Azrial.py` sebagai otomasi preprocessing.
- `preprocessing/namadataset_preprocessing.csv` sebagai output dataset siap latih.
- `.github/workflows/preprocess.yml` sebagai workflow GitHub Actions.

## Kriteria 2 - Membangun_model

Folder [Membangun_model](Membangun_model) digunakan untuk melatih model dari dataset yang sudah dipreprocessing.

Struktur final yang dipakai:

- [Membangun_model/modelling.py](Membangun_model/modelling.py) sebagai baseline MLflow lokal dengan autolog.
- [Membangun_model/modelling_tuning.py](Membangun_model/modelling_tuning.py) sebagai training dengan hyperparameter tuning dan manual logging.
- [Membangun_model/phishing_email_detection_2026_dataset_preprocessing.csv](Membangun_model/phishing_email_detection_2026_dataset_preprocessing.csv) sebagai dataset siap latih.
- [Membangun_model/requirements.txt](Membangun_model/requirements.txt) sebagai dependency training lokal.
- [Membangun_model/screenshoot_dashboard.jpg](Membangun_model/screenshoot_dashboard.jpg) dan [Membangun_model/screenshoot_artifak.jpg](Membangun_model/screenshoot_artifak.jpg) sebagai bukti screenshot setelah run lokal selesai.

### Menjalankan lokal

```powershell
python -m pip install -r Membangun_model/requirements.txt
python Membangun_model/modelling.py
python Membangun_model/modelling_tuning.py
```

Run MLflow akan tersimpan lokal di folder [Membangun_model/mlruns](Membangun_model/mlruns). Screenshot dashboard dan artefak dapat diambil setelah run selesai.

## Menjalankan otomatisasi preprocessing (lokal)

```powershell
python preprocessing/automate_Muhammad-Azrial.py \
  --input .workflow/namadataset_raw/phishing_email_detection_2026_dataset.csv \
  --output preprocessing/namadataset_preprocessing.csv
```

## Menjalankan workflow

Workflow akan jalan saat:
- push ke branch `main` atau `master`
- pull request ke `main` atau `master`
- trigger manual `workflow_dispatch`

Setiap run akan mengunggah artifact bernama `namadataset_preprocessing`.

## Workflow MLflow

Workflow [`.github/workflows/mlflow-ci.yml`](.github/workflows/mlflow-ci.yml) menjalankan baseline dan tuning dari folder [Membangun_model](Membangun_model) lalu mengunggah `artifacts/` dan `mlruns/` sebagai bukti retraining lokal.

### Catatan

- File screenshot yang dipakai sebagai bukti ada di [Membangun_model/screenshoot_dashboard.jpg](Membangun_model/screenshoot_dashboard.jpg) dan [Membangun_model/screenshoot_artifak.jpg](Membangun_model/screenshoot_artifak.jpg).
- Artefak hasil training ada di [Membangun_model/artifacts](Membangun_model/artifacts).

## Kriteria 3 - Workflow-CI

Struktur workflow CI yang terpisah ada di folder [Workflow-CI](Workflow-CI). Folder ini disiapkan sebagai repo mandiri untuk MLflow Project dan GitHub Actions CI retraining.

- [Workflow-CI/MLProject/modelling.py](Workflow-CI/MLProject/modelling.py) sebagai skrip training MLflow Project.
- [Workflow-CI/MLProject/MLproject](Workflow-CI/MLProject/MLproject) sebagai definisi entry point `train`.
- [Workflow-CI/MLProject/conda.yaml](Workflow-CI/MLProject/conda.yaml) sebagai environment project.
- [Workflow-CI/MLProject/phishing_email_detection_2026_dataset_preprocessing.csv](Workflow-CI/MLProject/phishing_email_detection_2026_dataset_preprocessing.csv) sebagai dataset siap latih.
- [Workflow-CI/.github/workflows/workflow-ci.yml](Workflow-CI/.github/workflows/workflow-ci.yml) sebagai workflow CI retraining.
- [Workflow-CI/DockerHub.txt](Workflow-CI/DockerHub.txt) sebagai placeholder jalur Advance.
