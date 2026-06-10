# ドキュメント・スクリプト整理メモ

**日付**: 2026-04-21  
**目的**: repo 内に増えた writeup / note / analysis script を、「何の実験か」「何を主張しているか」「全体の研究にどう効くか」で整理する。  
**位置づけ**: 自分用の整理・棚卸しメモ。最終 paper draft ではなく、読む順番と claim の重みづけを間違えないための地図。

---

## 1. 全体像

この repo の markdown は、大きく 4 世代に分けると分かりやすい。

1. **初期 simulator 世代**  
   `project_plan.md`, `roadmap.md`, `experiment_01.md`, `experiment_02.md`, `reports/` など。  
   LLM-vs-LLM simulator、hidden desperation state `D_t`、approval / enablement feedback loop という最初の構想。

2. **manual transcript 世代**  
   `manual_transcript_spec.md`, `docs/experiment_summary_2026_04_13.md`, `docs/experiment_summary_v3_20260413_163523.md` など。  
   抽象 simulator から、wedding dress / diet-advice という具体的な gray-zone advisory domain へ移った段階。

3. **V4 mechanism 世代**  
   `docs/writeup_2026_04_14.md`, `docs/analysis_plan_2026_04_17.md`, `docs/central_claim_2026_04_17.md`, `docs/reproduce_v4_2x2_feedback.md` など。  
   fixed trajectory、speaker ablation、memory × feedback 2×2 を通じて、memory が何をしているかを詰めた段階。

4. **identification / measurement 世代**  
   `docs/decomp_identification_note_2026_04_18.md`, `docs/enablement_score_note_2026_04_18.md` など。  
   decomp と evaluator の limitation を明示し、どこまで言えるかを締めるための段階。

現時点の evidential backbone は、初期 simulator ではなく、**V4-family evidence + measurement limitation note**。つまり、`analysis_plan`, `central_claim`, `enablement_score_note`, `decomp_identification_note` が現在の中心に近い。

---

## 2. 現在の canonical に近いドキュメント

| ファイル | 対象 | 主張 | 全体への寄与 |
|---|---|---|---|
| `docs/reproduce_v4_2x2_feedback.md` | V4 memory × feedback transcript の再現手順 | `run_v4_2x2_feedback.py` で再現できる。`V4_2X2_CONDITIONS` で条件 subset も走らせられる | Adhyyan / Laxman に渡す operational handoff。再現性の入口 |
| `docs/analysis_plan_2026_04_17.md` | V4 2×2 の role diagnosis analysis plan | operationalize × caveat、density、stance を事前に定義し、FE / SO / MX の候補 claim を pre-register する | V4 analysis の methodological spine。後から OD を追加した経緯も amendment として残っている |
| `docs/central_claim_2026_04_17.md` | Operationalization Drift の claim articulation | memory は generic engagement `(N,N)` を concrete / directive / caveatなし `(Y,N)` に移す。拒否 bypass でも単純な caveat stripping でもない | 現時点で一番コンパクトな central claim。ただし post-hoc variant なので、paper ではその旨を明示する必要がある |
| `docs/enablement_score_note_2026_04_18.md` | `enablement_score` の定義と限界 | single-axis score は discovery metric として有用だったが、premise adoption / operationalization / caveat / genuine harm を圧縮している | 次の robustness step を決める重要 note。multi-axis evaluator decomposition が必要だと示す |
| `docs/decomp_identification_note_2026_04_18.md` | memory factor decomp の identification note | decomp は natural memory decomposition ではなく、hand-authored memory-like content の prompt-level intervention | decomp を main claim にしすぎないための guardrail。side project / design-space probe として位置づける |

---

## 3. 重要だが historical / supporting なドキュメント

| ファイル | 対象 | 主張 | 全体への寄与 |
|---|---|---|---|
| `docs/writeup_2026_04_14.md` | V1–V4 をまとめた大きな draft | memory-present 条件は no-memory より harmful-enablement が高い。V4 では gradual escalation より regime selection / frame lock-in が見える | とても有用な大きな素材集。ただし後の OD / evaluator limitation によって一部 supersede されている |
| `docs/experiment_summary_2026_04_13.md` | V1, V2, V3 manual transcript lineage | approval-maximizing prompt や scripted escalation を外しても memory effect が残る | manual transcript 系の歴史を理解するための中心 summary |
| `docs/experiment_summary_v3_20260413_163523.md` | V3 の追加 batch 再集計 | V3 の memory effect は pilot だけでなく 6 run でも再現。特に threshold で強い | V3 signal が偶然ではなさそうだと補強する |
| `docs/open_questions_2026_04_14.md` | V3 / early V4 後の open questions | memory effect は見えるが、mechanism、prompt-path confound、evaluator confound、memory content causality が未解決 | 後の analysis_plan / decomp note / enablement note の前段階 |
| `manual_transcript_spec.md` | hand-crafted slow harmful drift transcript の仕様 | lookism / food restriction は social isolation より harm threshold が明確。slow drift は regime selection と counter-signal で作る | manual transcript family の設計思想。最終 evidence ではなく design rationale |

---

## 4. 初期 simulator / infrastructure 系

| ファイル | 対象 | 主張 | 現在の扱い |
|---|---|---|---|
| `project_plan.md` | hidden desperation `D_t` を持つ LLM-vs-LLM simulator | memory-based personalization が user indulgence に合わせて harmful feedback loop を作る | conceptual origin。`D_t` や group simulator の文脈では重要だが、現行 V4 claim の load-bearing evidence ではない |
| `roadmap.md` | memory-augmented sycophancy の future roadmap | memory は、within-conversation optimization が一会話内で収束しないときに最も効く | future project の方向性。今の manual transcript 結果そのものではない |
| `experiment_01.md` | 初期 simulator 実験 | `D_t` dynamics や enablement trajectory の初期確認 | historical / debugging artifact |
| `experiment_02.md` | 再現性・randomness 確認 | 同一 config でも LLM stochasticity / seed handling で variation が出る | historical / debugging artifact |
| `README.md`, `QUICKSTART.md`, `STATUS.md`, `implementation.md` | repo setup / 初期実装 | 初期 simulator stack の使い方 | infrastructure doc |
| `calibration/rubric.md` | evaluator rubric calibration | scorer の calibration | evaluator background |

---

## 5. `reports/` ディレクトリ

`reports/` はほぼ初期 simulator の calibration / planning / failed-or-partial separation search。現在の central claim には直接 load-bearing ではないが、研究の経緯としては残してよい。

| ファイル群 | 内容 | 現在の役割 |
|---|---|---|
| `reports/calibration_report.md` | evaluator calibration | historical evaluator development |
| `reports/phase1_baseline_*.md`, `reports/phase2_h*_*.md`, `reports/separation_eval.md` | therapy / politics の fixed-binary separation 系 | 初期探索。現在の V4 claim からは距離がある |
| `reports/fixed_binary_separation_findings.md` | fixed-binary separation のまとめ | early synthesis |
| `reports/phase1_qual_pairs.md` | qualitative matched pairs | examples としては使えるが central ではない |
| `reports/manual_transcript_candidates.md` | manual transcript scenario 候補 | scenario selection の背景 |
| `reports/experiment_plans/*.md` | user simulator / memory prompt / evaluator fix の計画 | simulator infrastructure に戻るなら参考になる |

---

## 6. data 側で重要な analysis artifact

| ファイル | 対象 | 主な使い道 |
|---|---|---|
| `data/manual_transcripts/v4_2x2_feedback_20260414_232517/analysis.txt` | V4 2×2 の score-level aggregate | memory × feedback の元の score-level 結果 |
| `data/manual_transcripts/v4_2x2_feedback_20260414_232517/op_caveat_summary.txt` | operationalize × caveat / density / stance summary | OD claim の直接素材。Mem/FB が `(Y,N)` と density を増やす |
| `data/manual_transcripts/v4_fixed_20260414_201141/analysis.txt` | V4 fixed trajectory | fixed user trajectory で memory effect を見る |
| `data/manual_transcripts/v4_speaker_ablation_20260414_202355/analysis.txt` | speaker ablation | assistant-side prior replies が regime carrier っぽいことを示す |

---

## 7. いま diff に入っている Python ファイル

ここは「この `.py` は何のためのものか」を忘れないためのメモ。既に commit 済みの `run_v4_2x2_feedback.py` / `format_manual_transcript.py` とは別に、現在の working tree に残っているものを中心に整理する。

### 7.1 既存ファイルへの変更

| ファイル | 変更内容 | 研究上の意味 |
|---|---|---|
| `scripts/experiments/run_v2v3.py` | docstring と実装コメントを修正し、V3 が `MemoryManager` ではなく plain raw history prompt vs no history であることを明確化 | V3 の causal path を正しく記録する変更。過去の「MemoryManager 経由」という誤解を防ぐ |
| `scripts/experiments/run_evaluator_decomposition.py` | fixed `N_RUNS=5` ではなく、既存 `run_*.json` を discover して全 run を re-score するよう変更 | V3 evaluator decomposition を、実際に存在する 6 run などに合わせて安全に回せるようにする |

### 7.2 V4 2×2 analysis 用スクリプト

| ファイル | 何をするか | 出力 / 役割 |
|---|---|---|
| `scripts/analysis/prepare_blind_label_set.py` | V4 2×2 の T8–T49 から n=30 を condition-blinded に抽出し、hand label 用 item を作る | `hand_label/blind_items.txt`, `blind_key.json`, `labels_template.csv`。classifier validation の入口 |
| `scripts/analysis/classify_op_caveat.py` | assistant turn を `operationalize` と `caveat` の 2 軸で LLM 分類し、directive / numeric density も計算 | validate mode と full mode がある。`op_caveat_labels.json` の生成元 |
| `scripts/analysis/compute_kappa.py` | hand label と classifier output を join し、Cohen's κ / agreement を計算 | caveat axis gate の確認。operationalize は hand label が saturated で κ undefined |
| `scripts/analysis/op_caveat_analysis.py` | `op_caveat_labels.json` から 2×2 mass shift と density gap を phase 別に計算 | OD の直接分析。Mem/FB vs NoMem/FB の `(Y,N)` / `(N,N)` shift を出す |
| `scripts/analysis/stance_distribution.py` | FB 条件の `ACCOMMODATE / HEDGE / PUSHBACK` distribution を集計 | PUSHBACK=0 を確認し、safety-overrider ではなさそうだと示す cross-check |
| `scripts/analysis/summarize_op_caveat_results.py` | 2×2 mass、density、stance、provisional verdict をまとめて txt/json に出す | `op_caveat_summary.txt/json` の生成元。V4 analysis のまとめ役 |
| `scripts/analysis/op_reintroduction_rate.py` | user message が operational vocabulary を含まない turn で、assistant が OMAD / calorie / cutting などを再導入する率を測る | frame lock-in の lexical proxy。assistant が自発的に operational regime を戻すかを見る |

### 7.3 追加 experiment 用スクリプト

| ファイル | 何をするか | 解釈上の注意 |
|---|---|---|
| `scripts/experiments/run_memory_decomposition_experiment.py` | hand-authored memory-like bullets を facts / preferences / evaluative / safety で組み合わせ、system prompt に注入する content ablation | natural memory decomposition ではなく prompt-level memory-content intervention。`decomp_identification_note` の対象 |
| `scripts/experiments/run_speaker_ablation_experiment.py` | V3 style の source full-context conversation を作り、同じ user messages を full / user_only / assistant_only / no_history で replay | V3 replay-style speaker ablation。user messages は full-context path 由来なので完全 factorial ではない |
| `scripts/experiments/run_v4_speaker_ablation.py` | V4 fixed user trajectory で full_context / no_memory / user_only / assistant_only を比較 | assistant-side history が regime carrier かを見る、V4 用の cleaner speaker ablation |

### 7.4 Python ファイルの現在の読み方

現在の `.py` diff は、だいたい次の 3 グループに分かれる。

1. **V4 2×2 の analysis pipeline**  
   `prepare_blind_label_set.py` → `classify_op_caveat.py` → `compute_kappa.py` → `op_caveat_analysis.py` / `stance_distribution.py` → `summarize_op_caveat_results.py`。  
   これは `analysis_plan_2026_04_17.md` と `central_claim_2026_04_17.md` を支える実解析。

2. **mechanism probe**  
   `op_reintroduction_rate.py`, `run_v4_speaker_ablation.py`, `run_speaker_ablation_experiment.py`。  
   memory が harmfulness を直接上げるというより、operational frame / assistant prior replies を保持するかを見る。

3. **decomp / evaluator limitation 系**  
   `run_memory_decomposition_experiment.py`, `run_evaluator_decomposition.py`。  
   前者は memory-content intervention、後者は single-axis score の分解。どちらも current central claim を強くするというより、claim の boundary と次の measurement layer を作る。

---

## 8. これらが全体としてどうつながるか

現時点での defensible な story は、次のような層構造。

1. 初期 simulator docs は、「persistent context が feedback loop を作りうる」という broad motivation を与える。
2. V1–V3 manual transcript docs は、diet / lookism domain で memory/no-memory gap が見えること、かつ最も明白な confound だけでは説明しきれないことを示す。
3. V4 fixed trajectory と speaker ablation は、user message だけではなく assistant-side history / prior replies が regime carrier になっている可能性を示す。
4. V4 2×2 feedback は、memory と stance-adaptive feedback が相互作用し、表面上は operationalization drift として現れることを示す。
5. decomp note は、content factorization は示唆的だが clean ontology ではない、と主張を弱めて守る。
6. enablement score note は、次に multi-axis evaluator decomposition を入れないと mechanism claim が詰まらない、と示す。

短く言うと、今の一番安全な主張はこれ。

> Memory は socially normalized な gray-zone advisory domain において、assistant を prior cooperative / operational frame に留めやすくし、その結果として generic engagement から concrete operational advice への drift を生む可能性がある。ただし、その mechanism を強く言うには、single-axis enablement score では足りず、premise adoption / operationalization / caveat / genuine harm の分解が必要。

---

## 9. 推奨 reading order

### 現在の V4 実験を再現・理解したい人向け

1. `docs/reproduce_v4_2x2_feedback.md`
2. `docs/analysis_plan_2026_04_17.md`
3. `data/manual_transcripts/v4_2x2_feedback_20260414_232517/op_caveat_summary.txt`
4. `docs/central_claim_2026_04_17.md`
5. `docs/enablement_score_note_2026_04_18.md`
6. `docs/decomp_identification_note_2026_04_18.md`

### 研究の流れを理解したい人向け

1. `manual_transcript_spec.md`
2. `docs/experiment_summary_2026_04_13.md`
3. `docs/experiment_summary_v3_20260413_163523.md`
4. `docs/writeup_2026_04_14.md`
5. `docs/open_questions_2026_04_14.md`

### 初期 simulator 構想を理解したい人向け

1. `project_plan.md`
2. `roadmap.md`
3. `reports/fixed_binary_separation_findings.md`
4. `reports/experiment_plans/*.md`

---

## 10. cleanup policy

- canonical に近い docs は `docs/` に残す。
- `docs/writeup_2026_04_14.md` は final paper skeleton ではなく、historical synthesis draft として扱う。
- `experiment_01.md`, `experiment_02.md`, `reports/` は archive / provenance として残す。
- いきなり古い md を削除しない。代わりに、この inventory のような index を置いて、古い exploratory claim と現在の central claim を混同しないようにする。
- paper / meeting memo を書くときは、April 14 の巨大 writeup から始めず、`analysis_plan`, `central_claim`, `enablement_score_note` から始める。
