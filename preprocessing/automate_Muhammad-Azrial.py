import argparse
import json
import re
from pathlib import Path

import pandas as pd


def clean_text(value: str) -> str:
    value = str(value).lower().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def load_raw_data(raw_path: Path) -> pd.DataFrame:
    return pd.read_csv(raw_path)


def run_eda_summary(df: pd.DataFrame) -> dict:
    summary = {
        "shape": {"rows": int(df.shape[0]), "cols": int(df.shape[1])},
        "missing_values": {k: int(v) for k, v in df.isna().sum().to_dict().items()},
        "duplicate_rows": int(df.duplicated().sum()),
    }

    if "is_phishing" in df.columns:
        summary["target_distribution"] = {
            str(k): int(v) for k, v in df["is_phishing"].value_counts().to_dict().items()
        }

    return summary


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df_prep = df.copy()

    # 1) Hapus missing values
    df_prep = df_prep.dropna()

    # 2) Hapus duplikat
    df_prep = df_prep.drop_duplicates()

    # 3) Normalisasi kolom teks
    df_prep["sender_email_clean"] = df_prep["sender_email"].apply(clean_text)
    df_prep["subject_clean"] = df_prep["subject"].apply(clean_text)

    # 4) Feature engineering
    df_prep["sender_domain"] = (
        df_prep["sender_email"].str.split("@").str[-1].str.lower().str.strip()
    )
    df_prep["subject_word_count"] = df_prep["subject_clean"].str.split().str.len()

    # 5) Pastikan tipe numerik konsisten
    numeric_cols = [
        "has_link",
        "has_attachment",
        "urgency_score",
        "spelling_errors",
        "email_length_words",
        "subject_word_count",
        "is_phishing",
    ]

    for col in numeric_cols:
        df_prep[col] = pd.to_numeric(df_prep[col], errors="coerce")

    df_prep = df_prep.dropna(subset=numeric_cols)
    df_prep[numeric_cols] = df_prep[numeric_cols].astype(int)

    return df_prep


def save_processed_data(df_prep: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_prep.to_csv(output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automasi preprocessing dataset phishing email hingga siap dilatih"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path dataset raw CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path output dataset preprocessing CSV",
    )
    args = parser.parse_args()

    df = load_raw_data(args.input)
    eda_summary = run_eda_summary(df)
    print("EDA Summary:")
    print(json.dumps(eda_summary, indent=2))

    df_prep = preprocess_data(df)
    save_processed_data(df_prep, args.output)

    print("Preprocessing selesai")
    print(f"Shape sebelum preprocessing: {df.shape}")
    print(f"Shape sesudah preprocessing: {df_prep.shape}")
    print(f"Output tersimpan di: {args.output}")


if __name__ == "__main__":
    main()
