from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


def _box(ax, xy, width, height, text, face="#eef6ff", edge="#2f6fed", fontsize=8):
    rect = Rectangle(xy, width, height, linewidth=1.2, edgecolor=edge, facecolor=face)
    ax.add_patch(rect)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        wrap=True,
    )


def _arrow(ax, start, end):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=1.0,
            color="#334155",
        )
    )


def save_layered_architecture(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis("off")

    layers = [
        ("Device Layer", 11.6, ["IoMT Data Owner", "Synthetic Health Data", "Data Consumer"]),
        ("Edge Layer", 9.2, ["Integrity Scoring", "MA-CP-ABE", "Version Revocation"]),
        ("Data Service Layer", 6.8, ["CKKS Computation", "EBR Reliability", "ML Pricing"]),
        ("Blockchain Layer", 4.4, ["CID Registry", "User Versions", "Transaction Logs"]),
        ("Storage Layer", 2.0, ["IPFS Simulator", "Encrypted Payloads", "CID Retrieval"]),
    ]

    for title, y, items in layers:
        ax.add_patch(Rectangle((0.7, y - 0.2), 8.6, 1.8, linewidth=1.0, edgecolor="#94a3b8", facecolor="#f8fafc"))
        ax.text(0.9, y + 1.35, title, fontsize=10, fontweight="bold", va="center")
        for i, item in enumerate(items):
            _box(ax, (1.1 + i * 2.75, y + 0.15), 2.25, 0.9, item)

    for y1, y2 in [(11.75, 10.6), (9.35, 8.2), (6.95, 5.8), (4.55, 3.4)]:
        _arrow(ax, (5, y1), (5, y2))

    ax.text(
        5,
        0.85,
        "Figure: Layered BDPP-IoT architecture extending the base paper with MA-CP-ABE, EBR, and ML pricing.",
        ha="center",
        fontsize=9,
    )
    plt.savefig(path, dpi=400, bbox_inches="tight")
    plt.close(fig)


def save_methodology_pipeline(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    boxes = [
        ((0.6, 5.8), "1. Generate\nIoMT Data"),
        ((3.0, 5.8), "2. Score Integrity\nand Metadata"),
        ((5.4, 5.8), "3. CKKS\nEncrypt"),
        ((7.8, 5.8), "4. Store in\nIPFS"),
        ((10.2, 5.8), "5. Log CID\non Ledger"),
        ((0.6, 3.3), "6. MA-CP-ABE\nPolicy Check"),
        ((3.0, 3.3), "7. Version\nRevocation Check"),
        ((5.4, 3.3), "8. Homomorphic\nOperation"),
        ((7.8, 3.3), "9. EBR\nReliability"),
        ((10.2, 3.3), "10. ML Price\nPrediction"),
        ((5.4, 0.8), "11. Game Pricing\nand Transaction Log"),
    ]

    for xy, label in boxes:
        _box(ax, xy, 1.85, 1.0, label, face="#ecfeff", edge="#0891b2", fontsize=8)

    for start, end in [
        ((2.45, 6.3), (3.0, 6.3)),
        ((4.85, 6.3), (5.4, 6.3)),
        ((7.25, 6.3), (7.8, 6.3)),
        ((9.65, 6.3), (10.2, 6.3)),
        ((11.1, 5.8), (1.5, 4.3)),
        ((2.45, 3.8), (3.0, 3.8)),
        ((4.85, 3.8), (5.4, 3.8)),
        ((7.25, 3.8), (7.8, 3.8)),
        ((9.65, 3.8), (10.2, 3.8)),
        ((11.1, 3.3), (6.35, 1.8)),
    ]:
        _arrow(ax, start, end)

    ax.text(
        7,
        0.25,
        "Figure: End-to-end BDPP-IoT methodology pipeline for simulated medical IoT data transactions.",
        ha="center",
        fontsize=9,
    )
    plt.savefig(path, dpi=400, bbox_inches="tight")
    plt.close(fig)

