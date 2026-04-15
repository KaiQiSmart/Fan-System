"""
================================================================================

PROJECT: Fan Integrated Design Platform
MODULE: _3b_PQmodel_train.py
DESCRIPTION:
    - Core training logic: ResNet-1D.
    - Dimension alignment: Feature space strictly follows FEATURE_ORDER (JSON full-parameter flattened).
    - Outputs: fan_pq_model_weights.pth, fan_scaler.joblib, model_config.json.
    - Training data is sourced from PQ JSON files, with blade parameters loaded and aligned based on the defined feature order.
    - The model predicts 10 points each for P and Q, resampled from the original PQ curve.
    - The training process includes detailed logging for debugging and GUI integration.
================================================================================
"""

import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Import path configurations and feature order definitions
from _3a_PQmodel_path import BLADE_PARAM_DIR, PQ_DATA_DIR, RANDOM_STATE
from _3a_PQmodel_algo_params import FEATURE_ORDER


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


# --- 2. Data Loading -----------------------------------------------------------
def load_and_preprocess(gui_logger=None):
    def log(msg):
        if gui_logger:
            gui_logger(msg)
        else:
            print(msg)

    samples = []
    pq_files = [f for f in os.listdir(PQ_DATA_DIR) if f.endswith(".json")]

    for pq_file in pq_files:
        try:
            with open(os.path.join(PQ_DATA_DIR, pq_file), "r", encoding="utf-8") as f:
                pq = json.load(f)

            blade_path = os.path.join(BLADE_PARAM_DIR, pq["conditions"]["blade_model"])
            with open(blade_path, "r", encoding="utf-8") as f:
                geo = json.load(f)

            row = {}

            # Geometry - Basic
            for k, v in geo["basic"].items():
                if isinstance(v, (int, float)):
                    row[f"geo_base_{k}"] = float(v)

            # Geometry - Airfoil Root
            for k, v in geo["airfoil_root"].items():
                if isinstance(v, (int, float)):
                    row[f"geo_root_{k}"] = float(v)

            # Geometry - Airfoil Tip
            for k, v in geo["airfoil_tip"].items():
                if isinstance(v, (int, float)):
                    row[f"geo_tip_{k}"] = float(v)

            # Geometry - Blade 3D (flatten lists)
            for k, v in geo["blade_3d"].items():
                if isinstance(v, (int, float)):
                    row[f"geo_3d_{k}"] = float(v)
                elif isinstance(v, list):
                    for i, val in enumerate(v):
                        row[f"geo_3d_{k}_{i}"] = float(val)

            # Operating condition (PQ test speed)
            rpm = pq["conditions"].get("speed_rpm")
            row["cond_operating_rpm"] = float(rpm) if rpm is not None else 0.0

            row["__filename__"] = pq_file

            # PQ curve resampling (10 points)
            raw_p = [pt["P"] for pt in pq["outputs"]["pq_curve"]]
            raw_q = [pt["Q"] for pt in pq["outputs"]["pq_curve"]]
            target_idx = np.linspace(0, len(raw_p) - 1, 10)

            p_10 = np.interp(target_idx, np.arange(len(raw_p)), raw_p)
            q_10 = np.interp(target_idx, np.arange(len(raw_q)), raw_q)

            for i in range(10):
                row[f"P_label_{i+1}"] = p_10[i]
                row[f"Q_label_{i+1}"] = q_10[i]

            samples.append(row)

        except Exception as e:
            log(f"[WARN] Skip {pq_file}: {e}")
            continue

    return pd.DataFrame(samples)


# --- 3. Training Main ----------------------------------------------------------
def train(epochs=100, gui_logger=None):
    def log(msg):
        if gui_logger:
            gui_logger(msg)
        else:
            print(msg)

    log("[TRAIN] Loading features...")
    df = load_and_preprocess(gui_logger)

    if df.empty:
        log("[ERROR] The dataset is empty!")
        return None

    X_cols = FEATURE_ORDER
    y_cols = [f"{pq}{i}" for i in range(1, 11) for pq in ("P_label_", "Q_label_")]

    y_cols = [c.replace("_label_", "_label_") for c in y_cols]

    missing = [c for c in X_cols if c not in df.columns]
    if missing:
        log(f"[ERROR] Missing features: {missing}")
        return None

    INPUT_DIM = len(X_cols)
    log(f"[INFO] INPUT_DIM = {INPUT_DIM} (locked)")

    X = df[X_cols].values.astype(np.float32)
    y = df[[f"P_label_{i}" for i in range(1, 11)] +
           [f"Q_label_{i}" for i in range(1, 11)]].values.astype(np.float32)

    X_train, X_test, y_train, y_test, _, test_names = train_test_split(
        X, y, df["__filename__"].values, test_size=0.2, random_state=RANDOM_STATE
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = FanResNet(INPUT_DIM, y.shape[1])
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    train_loader = DataLoader(
        TensorDataset(torch.FloatTensor(X_train_s).unsqueeze(1),
                      torch.FloatTensor(y_train)),
        batch_size=8,
        shuffle=True,
    )

    log(f"[START] Training for {epochs} epochs...")
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
            log(f"> Epoch {epoch:03d} | Avg Loss: {loss_sum / len(train_loader):.6f}")

    log("[SAVE] Saving model and scaler...")
    torch.save(model.state_dict(), "fan_pq_model_weights.pth")
    joblib.dump(scaler, "fan_scaler.joblib")

    with open("model_config.json", "w", encoding="utf-8") as f:
        json.dump(
            {"input_dim": INPUT_DIM, "feature_names": X_cols},
            f,
            indent=4
        )

    log("[SUCCESS] Training files updated.")

    model.eval()
    with torch.no_grad():
        test_pred = model(torch.FloatTensor(X_test_s).unsqueeze(1)).numpy()

    return {
        "model": model,
        "scaler": scaler,
        "test_y": y_test,
        "test_pred": test_pred,
        "test_names": test_names,
    }
