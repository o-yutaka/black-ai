# ROGII Segment-Level Structured Candidate Selector

Status: implemented on `main`; local regression tests `4 passed`; CLI smoke `PASS`.

目的は、候補trajectoryを井戸全体で1本選ぶのではなく、**正しい候補を正しい区間で選択すること**です。

## 構造

1. GR/PF/geometry/surface/roughnessをrow×candidateのtarget-safe evidenceへ正規化
2. winner交差、posterior entropy、候補dispersion、margin変化から区間境界を検出
3. 各区間の候補evidenceを集約
4. Viterbi/DPで候補pathを選択
5. switch、TVT連続性、slope jump、curvature jumpを罰則化
6. 低信頼区間だけTop-2 blend
7. 任意でvisible prefixだけからdatum+slopeをrobust補正

## 非交渉条件

- hidden TVTをfeature・境界・重み選択に使わない
- public LB由来のwell固有補正を入れない
- 最大switch数、最小区間長、P90非悪化を昇格gateにする
- `00bbac68`のようなhard wellはID指定ではなく、二峰性・低margin・高dispersion状態で検出する

## 入力NPZ

必須:

- `candidate_predictions`: `[rows, candidates]`

次のどちらか:

- `local_evidence`: `[rows, candidates]`
- または `gr_score`, `pf_score`, `geometry_score`, `surface_score`

任意:

- `candidate_names`
- `observed_tvt` と `visible_prefix_mask`（visible prefix補正を同時指定）

## 実行

```bash
PYTHONPATH=. python competitions/rogii/run_segment_selector.py \
  --input candidate_bundle.npz \
  --config competitions/rogii/config/segment_selector.json \
  --output-dir artifacts/segment_selector
```

出力:

- `selected_trajectory.csv`
- `segment_report.json`
- `segment_weights.npy`

## Kaggle昇格gate

- frozen convex/controlよりpooled RMSE改善
- disjoint 90 wellsで5 folds中4以上改善
- hard-well subset非悪化
- P90非悪化
- bootstrap 95%上限 `< 0`
- hidden target read `0`

候補集合にrow-oracle 4点台のheadroomがあっても、selectorが独立holdoutで回収できなければ提出へ昇格させません。
