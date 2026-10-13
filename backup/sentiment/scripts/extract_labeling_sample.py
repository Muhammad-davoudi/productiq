#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def _normalize_text(s):
    if pd.isna(s):
        return ""
    s = str(s).strip()
    s = s.replace("\u200c", " ").replace("\u200f", " ").replace("\u200e", " ")
    return " ".join(s.split())

def _length_bucket(n):
    if n <= 30:
        return "very_short"
    if n <= 80:
        return "short"
    if n <= 180:
        return "medium"
    if n <= 350:
        return "long"
    return "very_long"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/digikala-comments.csv", help="Input CSV")
    parser.add_argument("--n", type=int, default=1000, help="Sample size")
    parser.add_argument("--seed", type=int, default=42, help="Seed")
    parser.add_argument("--output", default="data/raw/labeling_sample_1000.csv", help="Output CSV")
    args = parser.parse_args()

    inp = PROJECT_ROOT / args.input if not Path(args.input).is_absolute() else Path(args.input)
    if not inp.exists():
        print(f"ERROR: Input file not found: {inp}")
        sys.exit(1)

    outp = PROJECT_ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)

    print(f"Reading dataset from {inp}...")
    df = pd.read_csv(inp, low_memory=False)

    text_col = None
    for cand in ["comment_text", "text", "comment", "body", "review"]:
        for col in df.columns:
            if col.lower() == cand:
                text_col = col
                break
        if text_col:
            break

    if not text_col:
        print(f"ERROR: No text column found! Available: {list(df.columns)}")
        sys.exit(1)

    rate_col = None
    for cand in ["rate", "rating", "score", "stars"]:
        for col in df.columns:
            if col.lower() == cand:
                rate_col = col
                break
        if rate_col:
            break

    cat_col = None
    for cand in ["category", "main_category", "cat"]:
        for col in df.columns:
            if col.lower() == cand:
                cat_col = col
                break
        if cat_col:
            break

    subcat_col = None
    for cand in ["subcategory", "sub_category", "subcat"]:
        for col in df.columns:
            if col.lower() == cand:
                subcat_col = col
                break
        if subcat_col:
            break

    df = df.copy()
    df["__clean_text__"] = df[text_col].map(_normalize_text)
    df = df[df["__clean_text__"].str.len() > 5].copy()

    df["__len_bucket__"] = df["__clean_text__"].str.len().map(_length_bucket)

    group_cols = ["__len_bucket__"]
    if rate_col:
        df["__rate_clean__"] = pd.to_numeric(df[rate_col], errors="coerce").fillna(-1).astype(int)
        group_cols.insert(0, "__rate_clean__")
    if cat_col:
        group_cols.append(cat_col)

    # Deterministic balanced sampling
    df = df.sample(frac=1.0, random_state=args.seed).reset_index(drop=True)
    grouped = df.groupby(group_cols, dropna=False)

    samples = []
    groups = [g.reset_index(drop=True) for _, g in grouped]
    idx = 0
    while len(samples) < args.n:
        added = False
        for g in groups:
            if idx < len(g):
                samples.append(g.iloc[idx])
                added = True
                if len(samples) >= args.n:
                    break
        if not added:
            break
        idx += 1

    sample_df = pd.DataFrame(samples).head(args.n)

    result_cols = {"id": range(1, len(sample_df) + 1), "text": sample_df["__clean_text__"]}
    if rate_col:
        result_cols["rate"] = sample_df[rate_col]
    if cat_col:
        result_cols["category"] = sample_df[cat_col]
    if subcat_col:
        result_cols["subcategory"] = sample_df[subcat_col]

    final_df = pd.DataFrame(result_cols)
    final_df.to_csv(outp, index=False, encoding="utf-8")
    print(f"Success! {len(final_df)} diverse rows saved to {outp}")

if __name__ == "__main__":
    main()
