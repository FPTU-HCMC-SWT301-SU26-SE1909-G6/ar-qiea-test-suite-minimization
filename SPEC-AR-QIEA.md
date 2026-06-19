# SPEC: Risk-Aware Multi-Objective Test Suite Minimization với AR-QIEA

> **Status**: APPROVED — implement theo spec này.
> **Phiên bản**: 1.0 (2026-06-12)
> **Optimization frame**: TRUE PARETO (multi-objective, không weighted-sum)

---

## 1. Mục tiêu nghiên cứu

### 1.1 Bài toán

Cho test suite gốc `T` (n tests) và coverage matrix từ Defects4J, tìm **tập các subset Pareto-optimal** `S ⊆ T` sao cho:

```
Maximize:   MSR(S), CGCC(S), ETR(S)     (3 objectives đồng thời)
Subject to: CR(S) ≥ 0.95                 (hard constraint)
```

Kết quả KHÔNG phải 1 nghiệm mà là **Pareto front** — tập nghiệm trade-off để người dùng chọn.

### 1.2 Claim mục tiêu của paper

> AR-QIEA (Adaptive Risk-aware QIEA) sinh Pareto front có **hypervolume cao hơn** NSGA-II và MO-QIEA (không risk-aware) trên benchmark Defects4J Lang, với độ tin cậy thống kê (Wilcoxon p < 0.05, 30 seeds).

### 1.3 Novelty

1. **Risk-adaptive rotation gate**: góc xoay qubit thích nghi theo "giá trị rủi ro" của từng test (chưa có trong literature MOQEA).
2. Tích hợp 3 nguồn risk thật từ Defects4J: call-graph centrality + mutation kill + execution cost.
3. Ablation study tách bạch đóng góp của risk-adaptive mechanism.

---

## 2. Định nghĩa tiêu chí (LOCKED — không đổi khi implement)

Ký hiệu: `T` = tập tất cả tests, `S` = subset được chọn, `cov(X)` = tập requirements được cover bởi X.

### 2.1 CR — Coverage Retention [CONSTRAINT]

```
CR(S) = |cov(S)| / |cov(T)|
```

- Range [0, 1]. **Constraint: CR(S) ≥ 0.95**.
- Mẫu số là coverage của **tập gốc T**, KHÔNG phải tổng số requirements trong matrix.
- Violation (cho constraint-domination): `viol(S) = max(0, 0.95 − CR(S))` — continuous, không phải binary.

### 2.2 MSR — Mutation Score Retention [OBJECTIVE max]

```
MSR(S) = |killed(S)| / |killed(T)|
```

- `killed(X)` = tập mutants bị giết bởi ít nhất 1 test trong X.
- Range [0, 1]. Nếu `killed(T) = ∅` thì MSR = 1.0 (degenerate, log warning).
- Nguồn data: P1 = synthetic (xem §6.2), P3 = Major qua `defects4j mutation`.

### 2.3 CGCC — Call Graph Centrality Coverage [OBJECTIVE max]

```
CGCC(S) = Σ_{r ∈ cov(S)} C[r]  /  Σ_{r ∈ cov(T)} C[r]
```

- `C[r]` = centrality weight của requirement r (line) — bằng centrality của **method chứa line đó**.
- Range [0, 1].
- Nguồn data: P1 = proxy từ coverage frequency (xem §6.1), P2 = javalang call graph + networkx betweenness.

### 2.4 ETR — Execution Time Reduction [OBJECTIVE max]

```
ETR(S) = 1 − Σ_{i ∈ S} t_i / Σ_{i ∈ T} t_i
```

- `t_i` = execution time của test i.
- Range [0, 1]. S = ∅ cho ETR = 1 nhưng CR = 0 → infeasible (đúng thiết kế).
- Nguồn data: P1 = proxy `t_i ∝ |cov({i})|^1.3 × lognormal noise`, P4 = parse timing thật nếu kịp.

### 2.5 ROP — Redundancy/Overlap Penalty [DIAGNOSTIC ONLY — không phải objective]

```
ROP(S) = Σ_r max(0, hits_S(r) − 1) / max(1, Σ_r hits_S(r))
```

- `hits_S(r)` = số test trong S cover requirement r.
- Chỉ báo cáo trong bảng kết quả (chứng minh AR-QIEA chọn subset ít trùng lặp hơn). KHÔNG đưa vào fitness.

---

## 3. Khung tối ưu: True Pareto

### 3.1 Tại sao không weighted-sum

- Weighted-sum cần tune weights → reviewer attack; không với tới vùng lõm của front.
- Quyết định: AR-QIEA là **Pareto-native** (archive-based MOQEA).

### 3.2 Constraint handling: Deb's constraint-domination

Nghiệm A "thắng" nghiệm B khi:

```
1. A feasible (viol=0), B infeasible (viol>0)        → A thắng
2. Cả hai infeasible                                  → viol nhỏ hơn thắng
3. Cả hai feasible                                    → Pareto dominance trên (MSR, CGCC, ETR)
```

Dùng NHẤT QUÁN ở: archive update (AR-QIEA), non-dominated sort + tournament (NSGA-II).

### 3.3 Metric so sánh chính: Hypervolume

- 3D hypervolume, maximization, **reference point = (0, 0, 0)** (mọi objective đã ∈ [0,1]).
- Chỉ tính HV trên **nghiệm feasible** trong front. Front rỗng (không nghiệm feasible) → HV = 0.
- Metrics phụ: front size, best-per-objective, ROP của knee point, IGD nếu kịp (P4).

---

## 4. Kiến trúc & Module specs

```
src/quantum_testing/
├── algorithms/
│   ├── qiea.py              # GIỮ NGUYÊN — single-obj baseline
│   ├── mqiea.py             # GIỮ NGUYÊN — memetic baseline (đã có)
│   ├── ar_qiea.py           # [NEW][WS-B] Pareto-native AR-QIEA
│   └── nsga2.py             # [NEW][WS-B] NSGA-II baseline
├── analyzers/               # [NEW][WS-C]
│   ├── __init__.py
│   ├── centrality.py        # P1 proxy + P2 javalang call graph
│   ├── mutation.py          # P1 synthetic + P3 Major wrapper
│   └── localization.py      # Ochiai/Tarantula (optional, P4)
├── problems/
│   ├── coverage.py          # GIỮ NGUYÊN
│   └── risk_problem.py      # [NEW][WS-A] RiskAwareProblem
├── metrics.py               # GIỮ NGUYÊN (apfd đã có)
├── metrics_mo.py            # [NEW][WS-A] ĐÃ CODE XONG — dominance/crowding/HV
└── cli.py                   # [WS-D] thêm subcommands sau cùng

scripts/
├── pareto_benchmark.py      # [NEW][WS-D] benchmark runner chính
├── plot_pareto.py           # [NEW][WS-D] 2D projections + HV bars
└── harvest_lang_wsl.py      # ĐÃ CÓ — harvest coverage

tests/
├── test_metrics_mo.py       # [WS-A] unit tests hypervolume/dominance
├── test_risk_problem.py     # [WS-A]
├── test_ar_qiea.py          # [WS-B]
└── test_nsga2.py            # [WS-B]
```

`[WS-x]` = workstream phân công (xem §9).

### 4.1 `metrics_mo.py` [ĐÃ CODE — review lại theo spec]

```python
def dominates(a, b) -> bool                      # Pareto dominance, maximization
def constrained_dominates(a_objs, a_viol, b_objs, b_viol) -> bool   # Deb's rule
def non_dominated_filter(points) -> list[int]    # indices của non-dominated
def crowding_distance(points) -> list[float]     # NSGA-II style
def hypervolume_2d(points) -> float              # ref (0,0)
def hypervolume_3d(points) -> float              # ref (0,0,0), sweep trên f1
def hypervolume(points) -> float                 # dispatch 2D/3D
```

**Unit tests bắt buộc** (`test_metrics_mo.py`):
- `hypervolume_2d([(1,1)]) == 1.0`; `hypervolume_2d([(1,0.5),(0.5,1)]) == 0.75`
- `hypervolume_3d([(1,1,1)]) == 1.0`
- `dominates((1,1,1),(1,1,0.5)) == True`; `dominates((1,0),(0,1)) == False`
- constrained: feasible luôn thắng infeasible bất kể objectives.

### 4.2 `problems/risk_problem.py` [WS-A]

```python
@dataclass
class MOEvaluation:
    objectives: tuple[float, float, float]   # (MSR, CGCC, ETR)
    cr: float
    violation: float                          # max(0, cr_threshold - cr)
    rop: float                                # diagnostic
    selected_count: int
    total_time: float

class RiskAwareProblem:
    def __init__(
        self,
        coverage: np.ndarray,        # bool (n_tests, n_reqs)
        centrality: np.ndarray,      # float (n_reqs,)  — C[r] ≥ 0
        mutation: np.ndarray,        # bool (n_tests, n_mutants)
        exec_times: np.ndarray,      # float (n_tests,) — t_i > 0
        cr_threshold: float = 0.95,
    ): ...

    @classmethod
    def from_matrix_csv(cls, path, risk_seed=12345, cr_threshold=0.95,
                        n_mutants_factor=2.0, kill_prob=0.6,
                        cost_exponent=1.3, noise_sigma=0.3) -> "RiskAwareProblem":
        """Load coverage thật + sinh synthetic risk (P1). Seeded, reproducible."""

    def evaluate(self, solution: Sequence[int]) -> MOEvaluation:
        """Vectorized numpy. KHÔNG dùng vòng lặp Python trên requirements."""

    def test_risk_scores(self) -> np.ndarray:
        """(n_tests,) ∈ [0,1] — input cho AR rotation.
        risk[i] = 0.5·normalize(Σ_r coverage[i,r]·C[r]) + 0.5·normalize(Σ_k mutation[i,k])
        """
```

**Quy tắc implement:**
- `evaluate` phải vectorized: `sel = np.asarray(bits, bool)`; `covered = coverage[sel].any(axis=0)`; v.v.
- Denominators (cov(T), killed(T), Σ C[r] trên cov(T), Σ t_i) **precompute trong `__init__`**.
- Edge cases: solution toàn 0 → CR=0, ETR=1, violation=0.95; matrix rỗng → raise ValueError.

### 4.3 `algorithms/ar_qiea.py` [WS-B] — TRÁI TIM CỦA PAPER

```python
@dataclass
class ArchiveEntry:
    solution: list[int]
    objectives: tuple[float, float, float]
    violation: float

class ARQIEA:
    def __init__(
        self,
        problem: RiskAwareProblem,
        pop_size: int = 40,
        max_gen: int = 150,
        rotation_angle: float = 0.01 * math.pi,
        risk_alpha: float = 1.0,        # cường độ risk-adaptive; 0 = tắt
        risk_adaptive: bool = True,     # False = MO-QIEA ablation
        archive_size: int = 50,
        seed: int | None = None,
    ): ...

    def run(self, verbose=False) -> list[ArchiveEntry]:
        """Returns final archive = Pareto front (feasible non-dominated)."""
```

**Pseudocode (chuẩn hoá — implement đúng từng bước):**

```
init: qubits[pop][n] = (1/√2, 1/√2);  archive = []
risk = problem.test_risk_scores()                     # (n,) ∈ [0,1]

for gen in 0..max_gen:
    # 1. Observe & evaluate
    sols  = [observe(ind) for ind in population]      # P(bit=1) = β²
    evals = [problem.evaluate(s) for s in sols]

    # 2. Archive update (constraint-domination)
    candidates = archive ∪ new entries
    archive = constrained_non_dominated(candidates)
    if len(archive) > archive_size:
        prune bằng crowding_distance (giữ điểm thưa)

    # 3. Rotation về guide ngẫu nhiên trong archive
    decay = 1 − 0.5·gen/max_gen
    for mỗi individual i (KHÔNG elitist skip — archive đã giữ best):
        guide = random.choice(archive)                # diversity qua guide đa dạng
        for q in 0..n:
            if sols[i][q] != guide.solution[q]:
                Δθ = rotation_angle · decay · (1 + risk_alpha·risk[q] if risk_adaptive else 1)
                rotate qubit (i,q) về phía guide.solution[q]   # R(±Δθ) chuẩn
            if rng() < 1/n:                            # Pauli-X mutation
                swap(α, β)

    # 4. Diversity injection: mỗi 20 gen, nếu std(α) < 0.05
    #    → reset 25% population về superposition

return [e for e in archive if e.violation == 0]
```

**Chú ý:**
- Khi archive rỗng gen đầu (chưa có feasible): constrained_non_dominated tự giữ các nghiệm ít vi phạm nhất (Deb's rule) → guide vẫn hoạt động.
- Rotation gate: tái dùng công thức trong `qiea.py:_quantum_rotate_single` (cos/sin + normalize).
- `risk_adaptive=False` PHẢI cho hành vi MO-QIEA thuần — đây là ablation, không được hard-code khác biệt nào khác.

### 4.4 `algorithms/nsga2.py` [WS-B]

NSGA-II chuẩn (Deb 2002), binary encoding:

```python
class NSGA2:
    def __init__(self, problem: RiskAwareProblem, pop_size=40, max_gen=150,
                 crossover_rate=0.9, mutation_rate=None,   # None → 1/n
                 seed=None): ...
    def run(self, verbose=False) -> list[ArchiveEntry]:    # cùng format AR-QIEA
```

- Fast non-dominated sort **với constrained_dominates** (không phải dominates thường).
- Crowding distance + binary tournament (rank trước, crowding sau).
- Single-point crossover, bit-flip mutation 1/n.
- Trả front feasible cuối cùng (rank-0, viol=0).

### 4.5 `analyzers/centrality.py` [WS-C]

```python
# P1 — proxy (LÀM TRƯỚC)
def frequency_centrality_proxy(coverage: np.ndarray, seed: int,
                               gamma: float = 1.0, noise_sigma: float = 0.3) -> np.ndarray:
    """C[r] = (freq[r]/max_freq)^gamma × lognormal(0, noise_sigma).
    freq[r] = số test cover requirement r. Seeded."""

# P2 — real (LÀM SAU, interface cố định từ giờ)
def build_call_graph(java_src_root: Path) -> "nx.DiGraph":
    """javalang parse → nodes = FQ method names, edges = invocation (name-match,
    APPROXIMATE — ghi rõ trong docstring + paper)."""

def betweenness_weights(graph, method_line_ranges: dict[str, tuple[int,int]],
                        requirements: list[str]) -> np.ndarray:
    """Map mỗi requirement 'file:line' → method chứa nó → betweenness centrality.
    Line không thuộc method nào → weight = min positive weight (floor)."""
```

**Gotcha P2 (đã biết trước):** javalang chỉ cho start-line của method → end-line = start của method kế − 1 trong cùng file (sort theo start). Nested/anonymous class: chấp nhận sai số, log warning.

### 4.6 `analyzers/mutation.py` [WS-C]

```python
# P1 — synthetic (LÀM TRƯỚC)
def synthetic_mutation_matrix(coverage: np.ndarray, seed: int,
                              n_mutants_factor: float = 2.0,
                              kill_prob: float = 0.6) -> np.ndarray:
    """bool (n_tests, n_mutants), n_mutants = factor × n_reqs.
    Mutant k đặt tại requirement r_k (uniform trên các req được cover ≥1 lần).
    Test i giết k với P=kill_prob NẾU coverage[i, r_k] — không cover thì không giết.
    → coupling thực tế giữa coverage và mutation."""

# P3 — real qua Major (LÀM SAU)
def run_major_mutation(project: str, bug: int, tests: list[str],
                       workdir: str) -> np.ndarray:
    """Per-test: `defects4j mutation -w <workdir> -t <test_id>` qua wsl.exe.
    Parse kill.csv/mutants.log của Major → bool matrix.
    CẢNH BÁO: rất chậm (~phút/test) — chỉ chạy hero case 1-2 bug, cache kết quả."""
```

### 4.7 `scripts/pareto_benchmark.py` [WS-D]

```
Input:  --root datasets/defects4j-panel/Lang  --seeds 30  --pop 40  --gens 150
        --algorithms ar_qiea,mo_qiea,nsga2,random_front
        --risk-seed 12345  --cr-threshold 0.95
        --output artifacts/pareto/lang-panel.json

Per case (mỗi matrix.csv) × per algorithm × per seed:
    front = algo.run()
    record: hypervolume(feasible front), front_size,
            best_msr/best_cgcc/best_etr, rop tại knee point, runtime_seconds

Đối chứng thêm (deterministic, 1 lần/case):
    greedy point: greedy set-cover full coverage → evaluate → 1 điểm
    → check: có bị front của AR-QIEA dominate không? (cột "dominates_greedy")

Aggregate: mean±std HV per algo; Wilcoxon signed-rank AR-QIEA vs từng baseline
           (paired theo seed, per case); wins/losses/ties.

Output JSON schema:
{
  "config": {...},
  "cases": {
    "<case>": {
      "n_tests": int, "n_requirements": int, "n_mutants": int,
      "greedy_point": {"objectives": [...], "cr": ..., "dominated_by": ["ar_qiea", ...]},
      "algorithms": {
        "<algo>": {
          "hv": {"mean":..,"std":..,"min":..,"max":..},
          "front_size": {...}, "runtime_seconds": {...},
          "raw": [{"seed":..,"hv":..,"front_size":..,"front":[[m,c,e],...]}, ...]
        }
      },
      "wilcoxon": {"ar_qiea_vs_nsga2": p, "ar_qiea_vs_mo_qiea": p, ...}
    }
  }
}
```

**random_front baseline**: sample `pop×gens` bitstrings với density p ~ U(0.05, 0.95) per string → evaluate → feasible non-dominated front. (Density đa dạng để trải đều kích thước subset.)

**Evaluation budget bằng nhau** giữa các thuật toán: `pop × gens` evaluations (NSGA-II: pop×(gens+1) chấp nhận được, ghi rõ trong config).

### 4.8 `scripts/plot_pareto.py` [WS-D]

- 3 panel 2D projections: (MSR,CGCC), (MSR,ETR), (CGCC,ETR) — overlay fronts của các algo, 1 seed đại diện + greedy point đánh dấu ★.
- Bar chart HV mean±std per algo per case.
- Convergence: HV của archive theo generation (cần `history_hv` từ ARQIEA — optional, thêm nếu kịp).

---

## 5. CLI (P4 — sau khi scripts chạy ổn)

```
quantum-testing analyze   --src <java_root> --coverage <matrix.csv> --out risk_profile.json
quantum-testing mutate    --project Lang --bug 5 --out mutation_matrix.csv
quantum-testing pareto    --matrix <matrix.csv> --algo ar-qiea --seeds 30 --out front.json
```

---

## 6. Data & formats

### 6.1 Đã có sẵn (không làm lại)

| Path | Nội dung |
|---|---|
| `datasets/defects4j-panel/Lang/5b/` | 13 tests × 82 reqs — matrix.csv, tests.txt, requirements.txt, metadata.json |
| `datasets/defects4j-panel/Lang/14b/` | 50 tests × 17 reqs (degenerate — vẫn dùng làm stress case) |
| `datasets/defects4j-relevant{,-24}/Lang/1b/` | 12/24 tests × 97/181 reqs |
| `scripts/harvest_lang_wsl.py` | Harvest thêm bug: `python scripts/harvest_lang_wsl.py --bugs 10,29 --limit-tests 50` |

### 6.2 Synthetic risk (P1) — quy tắc chống "thiên vị"

1. **MỌI synthetic data phải seeded** (`risk_seed` cố định = 12345 cho main run), ghi vào output JSON.
2. Mutation kill CHỈ có thể xảy ra khi test cover mutant location (coupling thực tế).
3. Centrality từ coverage frequency (proxy có cơ sở: code được nhiều test chạm ≈ code trung tâm).
4. **Sensitivity run** (P4): lặp benchmark với 3 risk_seed khác nhau → chứng minh kết quả không phải artifact của 1 lần sinh số.

### 6.3 Format files mới

```
risk_profile.json:      {"centrality": {"<file:line>": w, ...}, "method_map": {...}, "source": "proxy|javalang"}
mutation_matrix.csv:    test_id, m0, m1, ...  (0/1; cùng convention matrix.csv)
exec_times.json:        {"<test_id>": seconds, ...}  (P4, optional)
```

---

## 7. Benchmark protocol (LOCKED)

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| Cases | Lang-5b, Lang-14b (P1) → +2-3 bug harvest thêm (P2+) | 14b là stress case degenerate |
| Seeds | 30 (range 42..71) | mọi thuật toán stochastic |
| Budget | pop=40 × gens=150 = 6000 evals | bằng nhau mọi algo |
| risk_seed | 12345 (main), {7, 99, 2024} (sensitivity) | |
| CR threshold | 0.95 | |
| Algorithms | ar_qiea, mo_qiea (ablation), nsga2, random_front (+greedy point) | |
| Metric chính | Hypervolume 3D, ref (0,0,0), feasible only | |
| Statistical test | Wilcoxon signed-rank, paired by seed, α=0.05 | scipy |

### Bảng kết quả paper (template)

| Algorithm | HV (mean±std) | Front size | Best MSR | Best CGCC | Best ETR | Dominates greedy? | p vs AR-QIEA |
|---|---|---|---|---|---|---|---|
| AR-QIEA (ours) | | | | | | | — |
| MO-QIEA (ablation) | | | | | | | |
| NSGA-II | | | | | | | |
| Random front | | | | | | | |

---

## 8. Phases & acceptance criteria

### P1 — Core + synthetic (TARGET: chạy được end-to-end)
- [ ] `metrics_mo.py` + unit tests pass *(code đã có, cần test)*
- [ ] `risk_problem.py` + unit tests pass
- [ ] `ar_qiea.py` (cả 2 mode risk on/off) + `nsga2.py`
- [ ] `pareto_benchmark.py` chạy Lang-5b/14b, 30 seeds
- [ ] **GATE**: HV(ar_qiea) ≥ HV(mo_qiea) và ≥ HV(random_front) với p<0.05 trên ≥1 case.
  Nếu FAIL → tune (risk_alpha, archive_size, rotation) trước khi sang P2. Nếu vẫn fail → review lại risk score formula.

### P2 — Real centrality
- [ ] `build_call_graph` + `betweenness_weights` (javalang + networkx)
- [ ] Map line→method với end-line heuristic, có unit test trên 1 file Java mẫu
- [ ] Re-run benchmark với real CGCC; so sánh kết quả proxy vs real (1 đoạn analysis)

### P3 — Real mutation (hero case)
- [ ] `run_major_mutation` cho Lang-5b (13 tests — khả thi nhất)
- [ ] Cache mutation matrix vào `datasets/.../5b/mutation_matrix.csv`
- [ ] Re-run benchmark hero case với real MSR

### P4 — Paper-ready
- [ ] Sensitivity: 3 risk_seeds
- [ ] Plots (`plot_pareto.py`), bảng template §7
- [ ] ROP diagnostic + APFD (nếu có trigger tests)
- [ ] CLI subcommands
- [ ] Harvest thêm 2-3 Lang bugs (29, 30, 35 — nhiều test classes) nếu còn thời gian

---

## 9. Phân công đề xuất (4 workstreams, song song được)

| WS | Module | Phụ thuộc | Effort |
|---|---|---|---|
| **WS-A** | `metrics_mo.py` (review+test), `risk_problem.py` | không | 0.5-1 ngày |
| **WS-B** | `ar_qiea.py`, `nsga2.py` + tests | WS-A interfaces (§4.2-4.4 đã cố định — code song song được với mock) | 1-1.5 ngày |
| **WS-C** | `analyzers/` (P1 proxy 0.5 ngày → P2 javalang 1 ngày → P3 Major 1-2 ngày) | không (interface cố định) | rải theo phase |
| **WS-D** | `pareto_benchmark.py`, `plot_pareto.py`, CLI | WS-A+B xong P1 | 1 ngày |

**Quy tắc tích hợp:**
- Interfaces trong spec này là CONTRACT — đổi signature phải thông báo cả team.
- Mọi randomness phải đi qua `np.random.default_rng(seed)` — KHÔNG dùng `random` module hay global numpy state.
- `ArchiveEntry` là format trao đổi chung giữa WS-B và WS-D.
- Style: theo code hiện có (type hints, docstrings, dataclasses).

---

## 10. Tech stack

| Package | Dùng cho | Phase |
|---|---|---|
| numpy (có sẵn) | matrices, RNG | P1 |
| scipy | Wilcoxon | P1 (đã dùng trong panel_benchmark) |
| matplotlib (đã cài) | plots | P1 |
| javalang | Java AST parse | P2 |
| networkx | call graph centrality | P2 |
| lizard (optional) | cyclomatic complexity | P4 |
| Major (có sẵn trong Defects4J) | real mutation — KHÔNG dùng PIT | P3 |

## 11. Known risks & mitigations

| Risk | Mitigation |
|---|---|
| AR-QIEA không thắng ablation (novelty không ăn) | GATE ở P1 — phát hiện sớm với synthetic, tune risk_alpha ∈ {0.5, 1, 2} trước khi kết luận |
| Lang-14b degenerate (17 must-have tests) | Giữ làm stress case; CR=0.95 cho phép bỏ ~1 req → vẫn có không gian; kết luận chính dựa trên 5b + bugs harvest thêm |
| Per-test Major mutation quá chậm | Hero case 13 tests duy nhất; timeout 30 phút/test; cache mọi kết quả |
| javalang call graph sai (no type resolution) | Ghi rõ "approximate" trong paper; sensitivity giữa proxy vs real centrality là 1 finding |
| Synthetic bias làm AR-QIEA thắng giả | Quy tắc §6.2 + sensitivity 3 seeds + real data ở P2/P3 |
| HV bằng nhau giữa các algo (matrix quá nhỏ) | Harvest bug lớn hơn (Lang-29: 25 test classes) ở P4 |
```
