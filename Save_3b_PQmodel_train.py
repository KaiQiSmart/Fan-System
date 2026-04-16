"""
================================================================================
PROJECT: Fan Integrated Design Platform
MODULE: _3b_PQmodel_train.py
DESCRIPTION:
    - Core training logic: ResNet-1D.
    - Data Processing: Handles nested JSON structure and subdirectories.
    - Resampling: Automatically fits raw PQ data into 10 standard points (P1..Q10).
    - Dimension alignment: Sequential mapping [P1..P10, Q1..Q10].
================================================================================
"""

import os
import json
import glob
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from scipy.interpolate import interp1d

# Import configurations
from _3a_PQmodel_path import BLADE_PARAM_DIR, RANDOM_STATE
import _3a_PQmodel_algo_params as algo_params

# --- 1. Model Architecture ----------------------------------------------------
class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(out_channels)

    def forward(self, x):
        residual = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return self.relu(out)

class FanResNet(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.initial_conv = nn.Conv1d(1, 64, kernel_size=3, padding=1)
        self.res_block1 = ResidualBlock(64, 64)
        self.res_block2 = ResidualBlock(64, 64)
        self.flatten = nn.Flatten()

        self.fc = nn.Sequential(
            nn.Linear(64 * input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, output_dim)
        )

    def forward(self, x):
        x = self.initial_conv(x)
        x = self.res_block1(x)
        x = self.res_block2(x)
        x = self.flatten(x)
        return self.fc(x)

# --- 2. Data Resampling Helper -------------------------------------------------
def resample_pq(p_raw, q_raw, num_points=10):
    """Linearly resample any number of PQ points into fixed points."""
    if len(p_raw) < 2:
        return [p_raw[0]] * num_points, [q_raw[0]] * num_points
    
    raw_idx = np.linspace(0, 1, len(p_raw))
    target_idx = np.linspace(0, 1, num_points)
    
    f_p = interp1d(raw_idx, p_raw, kind='linear')
    f_q = interp1d(raw_idx, q_raw, kind='linear')
    
    return f_p(target_idx).tolist(), f_q(target_idx).tolist()

# --- 3. Data Loading & Parsing -------------------------------------------------
def load_and_preprocess(data_path, gui_logger=None):
    def log(msg):
        if gui_logger: gui_logger(msg)
        else: print(msg)

    samples = []
    
    # [Mod] Use glob to recursively find all JSON files in selected directory and sub-directories
    search_pattern = os.path.join(data_path, "**", "*.json")
    pq_files = glob.glob(search_pattern, recursive=True)

    if not pq_files:
        log(f"[ERROR] No JSON files found in: {data_path}")
        return pd.DataFrame()

    for pq_file_path in pq_files:
        try:
            # A. Load PQ Test Data
            with open(pq_file_path, "r", encoding="utf-8") as f:
                pq_json = json.load(f)

            # B. Load Corresponding Blade Geometry
            blade_name = pq_json["basic_info"]["blade_model"]
            blade_path = os.path.join(BLADE_PARAM_DIR, blade_name)
            
            if not os.path.exists(blade_path):
                log(f"[WARN] Blade file missing: {blade_name}")
                continue

            with open(blade_path, "r", encoding="utf-8") as f:
                geo = json.load(f)

            row = {}

            # C. Map Geometry Features (Based on FEATURE_ORDER)
            for k, v in geo.get("basic", {}).items():
                row[f"geo_base_{k}"] = float(v) if isinstance(v, (int, float)) else 0.0

            for k, v in geo.get("airfoil_root", {}).items():
                row[f"geo_root_{k}"] = float(v)

            for k, v in geo.get("airfoil_tip", {}).items():
                row[f"geo_tip_{k}"] = float(v)

            for k, v in geo.get("blade_3d", {}).items():
                if isinstance(v, list):
                    for i, val in enumerate(v): row[f"geo_3d_{k}_{i}"] = float(val)
                else:
                    row[f"geo_3d_{k}"] = float(v)

            # D. Operating Condition
            row["cond_operating_rpm"] = float(pq_json["basic_info"].get("speed_rpm", 0))

            # E. PQ Curve Resampling (Target: 10 Points)
            curve = pq_json["test_data"]["pq_curve"]
            raw_p = [pt["P"] for pt in curve]
            raw_q = [pt["Q"] for pt in curve]
            
            p_10, q_10 = resample_pq(raw_p, raw_q, num_points=10)

            # F. Map Labels (Strictly: P1..P10, Q1..Q10)
            for i, val in enumerate(p_10): row[f"P{i+1}"] = val
            for i, val in enumerate(q_10): row[f"Q{i+1}"] = val

            row["__filename__"] = os.path.basename(pq_file_path)
            samples.append(row)

        except Exception as e:
            log(f"[WARN] Skip {os.path.basename(pq_file_path)}: {e}")
            continue

    return pd.DataFrame(samples)

# --- 4. Training Main ----------------------------------------------------------
def train(data_path, epochs=100, gui_logger=None):
    """
    Core train function.
    @param data_path: The directory containing training JSONs (supports subfolders).
    """
    def log(msg):
        if gui_logger: gui_logger(msg)
        else: print(msg)

    log(f"[TRAIN] Initializing data from: {os.path.basename(data_path)}")
    df = load_and_preprocess(data_path, gui_logger)

    if df.empty:
        log("[ERROR] Dataset is empty after preprocessing.")
        return None

    # Input/Output columns identification
    X_cols = algo_params.FEATURE_ORDER
    y_cols = algo_params.TARGET_LABELS

    # Validate Columns
    missing = [c for c in X_cols if c not in df.columns]
    if missing:
        log(f"[ERROR] Missing feature columns: {missing}")
        return None

    X = df[X_cols].values.astype(np.float32)
    y = df[y_cols].values.astype(np.float32)

    # Split Data
    X_train, X_test, y_train, y_test, _, test_names = train_test_split(
        X, y, df["__filename__"].values, 
        test_size=(algo_params.TEST_RATIO / 100), 
        random_state=RANDOM_STATE
    )

    # Scaling
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Model Setup
    model = FanResNet(algo_params.INPUT_DIM, algo_params.OUTPUT_DIM)
    optimizer = optim.Adam(model.parameters(), lr=algo_params.LEARNING_RATE)
    criterion = nn.MSELoss()

    train_loader = DataLoader(
        TensorDataset(torch.FloatTensor(X_train_s).unsqueeze(1), torch.FloatTensor(y_train)),
        batch_size=algo_params.BATCH_SIZE,
        shuffle=True
    )

    log(f"[START] Training Mode: ResNet-1D | Samples: {len(df)} | Epochs: {epochs}")
    model.train()
    for epoch in range(epochs):
        loss_sum = 0.0
        for bx, by in train_loader:
            optimizer.zero_grad()
            pred = model(bx)
            loss = criterion(pred, by)
            loss.backward()
            optimizer.step()
            loss_sum += loss.item()

        if epoch % 20 == 0 or epoch == epochs - 1:
            log(f"> Epoch {epoch:03d} | Loss: {loss_sum / len(train_loader):.6f}")

    # Results to Return
    model.eval()
    with torch.no_grad():
        test_pred = model(torch.FloatTensor(X_test_s).unsqueeze(1)).numpy()

    log("[SUCCESS] Model trained successfully.")
    
    return {
        "model": model,
        "scaler": scaler,
        "test_y": y_test,
        "test_pred": test_pred,
        "test_names": test_names,
    }