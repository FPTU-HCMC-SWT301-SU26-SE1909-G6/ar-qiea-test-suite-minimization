"""Centrality estimators for risk-aware test minimization."""
from __future__ import annotations

from pathlib import Path

import numpy as np


def frequency_centrality_proxy(
    coverage: np.ndarray,
    seed: int,
    gamma: float = 1.0,
    noise_sigma: float = 0.3,
) -> np.ndarray:
    """Seeded P1 proxy: frequently covered requirements are treated as central."""
    cov = np.asarray(coverage, dtype=bool)
    if cov.ndim != 2 or cov.size == 0:
        raise ValueError("coverage must be a non-empty 2D matrix")
    rng = np.random.default_rng(seed)
    freq = cov.sum(axis=0).astype(float)
    max_freq = float(freq.max()) if freq.size else 0.0
    base = np.zeros_like(freq, dtype=float) if max_freq <= 0 else (freq / max_freq) ** gamma
    noise = rng.lognormal(mean=0.0, sigma=noise_sigma, size=freq.shape)
    return np.maximum(0.0, base * noise)


def build_call_graph(java_src_root: Path):
    """Build an approximate Java method call graph using javalang name matching."""
    try:
        import javalang
        import networkx as nx
    except ImportError as exc:
        raise ImportError("build_call_graph requires javalang and networkx") from exc

    root = Path(java_src_root)
    graph = nx.DiGraph()
    methods_by_simple_name: dict[str, list[str]] = {}
    parsed_files = []

    for java_file in root.rglob("*.java"):
        try:
            tree = javalang.parse.parse(java_file.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        package = tree.package.name if tree.package else ""
        for _, cls in tree.filter(javalang.tree.ClassDeclaration):
            class_name = f"{package}.{cls.name}" if package else cls.name
            for method in cls.methods:
                node = f"{java_file}:{class_name}.{method.name}"
                graph.add_node(node)
                methods_by_simple_name.setdefault(method.name, []).append(node)
                parsed_files.append((node, method))

    for caller, method in parsed_files:
        for _, invocation in method.filter(javalang.tree.MethodInvocation):
            for callee in methods_by_simple_name.get(invocation.member, []):
                if callee != caller:
                    graph.add_edge(caller, callee)
    return graph


def betweenness_weights(
    graph,
    method_line_ranges: dict[str, tuple[int, int]],
    requirements: list[str],
) -> np.ndarray:
    """Map ``file:line`` requirements to containing-method betweenness weights."""
    try:
        import networkx as nx
    except ImportError as exc:
        raise ImportError("betweenness_weights requires networkx") from exc

    centrality = nx.betweenness_centrality(graph) if len(graph) else {}
    positive = [float(v) for v in centrality.values() if float(v) > 0]
    floor = min(positive) if positive else 1.0
    weights: list[float] = []
    for req in requirements:
        try:
            file_part, line_part = req.rsplit(":", 1)
            line = int(line_part)
        except ValueError:
            weights.append(floor)
            continue
        matched = None
        for method, (start, end) in method_line_ranges.items():
            if method.startswith(file_part) and start <= line <= end:
                matched = method
                break
        weights.append(float(centrality.get(matched, floor)))
    return np.asarray(weights, dtype=float)
