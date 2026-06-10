# リファクタリング計画(全フェーズ) — 2026-06-10

> 対象: `memory_harm_Shin-u` リポジトリ全体。
> 制約: **AIMS workshop 締切 2026-06-23(FREEZE v1)**。締切前は実験パイプラインを
> 壊さない「安全な衛生作業」のみ。構造を動かす作業はすべて締切後に置く。
> 安全条件: 生トランスクリプトは `manual_redteam/data/runs/` に留める(CLAUDE.md)。
> ブラインドラベルの来歴(provenance)を壊す操作は禁止。

---

## 現状診断(2026-06-10 時点の事実)

| 項目 | 実測 |
|---|---|
| 総ファイル数(.git 除く) | 8,045 |
| git 追跡ファイル | **229 のみ** |
| 未追跡ファイル | **817**(本物の writeup .tex/.md を含む = 消失リスク) |
| 最大ディレクトリ | `manual_redteam/` 82MB · ルート `data/` 74MB(ignored) · `docs/` 5.6MB |
| manual_redteam/scripts | **72 本**(大半が日付付きワンオフ実験スクリプト) |
| manual_redteam/docs | 101 md + archive 23(CURRENT.md / DECISIONS.md が真実) |
| manual_redteam/ladders | **44 変種**(blue_door v0〜v16、すべて平置き、canonical 不在) |
| manual_redteam/context_prefixes | **YAML 1,031 本**(直下に 604、shard/pilot サブ dir 16) |
| `ladder_canonical_v1.yaml` | **未作成**(CURRENT.md §4 アクティブプラン項目 4 が未完了) |

主要な「無駄」の正体:

1. **2世代のプロジェクトが同居**している。
   - 第1世代(4月): memory/lookism 系 — `src/`, `scripts/`, `tests/`, `configs/`,
     `reports/`, `Experiment_01/`, `Experiment_02/`, `latex/`, ルートの notebook 4本、
     ルートの md 群(`project_plan.md`, `roadmap.md`, `STATUS.md`, `QUICKSTART.md`,
     `implementation.md`, `experiment_01/02.md`, `manual_transcript_spec.md`)。
     現在の作業から参照されていない。tests/ はこの世代の `src/` しかテストしない。
   - 第2世代(4月末〜現在、**アクティブ**): `manual_redteam/`。
2. **ビルド成果物の散乱**: LaTeX の aux/log/fls/fdb_latexmk/out/pdf がルートと
   `docs/` の両方に堆積(.gitignore 済みなのにディスク上に残存)。`vllm.log`(1MB)、
   `.DS_Store` ×3、`__pycache__`、`presentation_audit_packet.zip`(展開済みdirと二重)。
   さらに**同名 writeup がルートと docs/ に二重ビルド**されている。
3. **未追跡の一次ソース**: `docs/` の writeup .tex/.md ~30本、
   `manual_redteam/context_prefixes/` の userside YAML 群、`manual_redteam/data/` の
   `simulator_discover/`(5.8MB)・`blindpass/`(2.6MB)・`adaptive/`(2.5MB)が
   **git にもバックアップにも乗っていない**。`.gitignore` のデータ方針が
   `data/runs/**` と `data/cold_probes/**` にしか適用されておらず中途半端。
4. **移行が中途で止まっている**: branch `manual-redteam-v0` 上に
   `manual_redteam/core/`(paths.py / session_io.py)新設・run データの追跡解除・
   README 追加が **staged だが未コミット**。しかも `core/session_io.py` は
   `scripts/_session_io.py` の再エクスポートという**逆向きファサード**
   (実装が scripts 側に残り、17本のスクリプトが `_session_io` を直 import)。
5. **スクリプトの重複系列**: `build_*_blindpass_corpus.py` ×4、`unblind_*.py` ×3、
   `adaptive_strictness_profile{,_v3,_v3_5_replication}.py` ×3、
   `phaseE_*` ×6 など、コピー&改変で増殖したワンオフ群。
6. **docs の真実性管理は CURRENT.md 方式で確立済みだが**、101 本の日付付き docs の
   うち frontmatter `status:` を持つものはごく一部。`blindpass/2099-01-01_decomp_s12`
   のような明らかな日付ミスの run ディレクトリも放置。
7. **ladder YAML が「変種の山 + canonical 不在」**: `ladders/` には blue_door
   v0〜v16 + yesno_artifact 系の 44 変種が平置きで、どれが生きているか
   ファイル名から判別不能。CURRENT.md §1 が定義する FROZEN canonical
   (R0→S1–S4→Bridge→S9–S12+decimal overlay)に対応する
   **`context_prefixes/ladder_canonical_v1.yaml` がまだ存在しない**(§4 項目 4)。
   `context_prefixes/` は 604 本の userside YAML が直下に平置き
   (実験グループ ~40 個分)+ shard/pilot サブ dir 16 個。
   = 「canonical は ONE referenced file」という自前の規約(§5)が物理層で未実現。

---

## フェーズ構成(依存順)

```
Phase 0  セーフティネット(即日)            ← 何より先。データ消失リスクの遮断
Phase 1  非破壊の衛生作業(締切前OK)
Phase L  ladder / YAML の canonical 化(締切前・実験計画の一部)
Phase R  AIMS 公開パッケージ(締切前・allowlist 輸出方式)
─────────── 2026-06-23 AIMS 提出・公開 ───────────
Phase 2  レガシー世代の隔離
Phase 3  manual_redteam のパッケージ化
Phase 4  docs 統廃合
Phase 5  データレイアウトの一本化
Phase 6  テスト・CI・再発防止
```

各フェーズは独立にコミット可能。途中で止めても repo は常に動く状態を保つ。

**公開戦略の核**: 「内部リポジトリの完全整理」と「AIMS 公開物」を**切り離す**。
公開はこの作業リポジトリを public 化するのではなく、**allowlist 方式の輸出スクリプト
で別の公開用リポジトリを生成**する(Phase R)。これにより (a) 内部の散らかりが
公開をブロックしない、(b) `.env`・生の自殺関連トランスクリプト・内部 handoff・
協力者名入りメモの漏出を構造的に防げる、(c) 締切前の大規模ファイル移動
(= FREEZE リスク)を回避できる。

---

## Phase 0 — セーフティネット(即日・~1時間)

**目的**: 「未追跡 817 ファイル+staged 未コミット」という現状は、`git clean` 一発
やディスク事故で一次データが消える状態。これを先に遮断する。

1. **進行中の staged 変更を triage してコミット**:
   - staged 済み(core/ 新設、run データ untrack、README 群、.gitignore)→
     意図どおりか確認して 1 コミットで着地。
   - unstaged の `docs/experiment_summary_2026_04_13.md`, `docs/writeup_2026_04_14.md`,
     `scripts/experiments/run_*.py`, `manual_redteam/scripts/run_sequence_branch_panel.py`
     の変更 → diff を確認し、生かすか捨てるか判定して着地。
2. **未追跡の一次ソースをコミット**(成果物ではなくソースのみ):
   - `docs/*.tex`, `docs/*.md`(writeup 系 ~30本)
   - `manual_redteam/context_prefixes/**/*.yaml`(userside スクリプト = 実験の再現に必須)
   - `manual_redteam/docs/` の未追跡 md
   - `CLAUDE.md`, `.env.example`
3. **生データのオフライン快照**: git に乗せない `manual_redteam/data/`(runs /
   simulator_discover / blindpass / adaptive / elicitations)とルート `data/` を
   `tar` でリポジトリ外(例 `~/backups/memory_harm_data_2026-06-10.tar.zst`)へ。
   ブラインドラベルの seal 済みファイルは checksum も記録。
4. **タグ打ち**: `git tag pre-refactor-2026-06-10`。

**完了条件**: `git status` がクリーン(ignored を除く)/ データ快照が存在 / タグあり。

---

## Phase 1 — 非破壊の衛生作業(締切前に実施可・~半日)

**目的**: ディスクと視界のノイズを消す。**コードの import・パス・実験手順は一切
変えない**(FREEZE 抵触なし)。

1. **生成物の削除**(すべて再生成可能であることを確認済みのもの):
   - ルートと `docs/` の LaTeX 中間物(aux/log/fls/fdb_latexmk/out/synctex.gz)
   - `vllm.log`, `.DS_Store` ×3, `manual_redteam/scripts/__pycache__/`
   - `presentation_audit_packet.zip`(展開済み dir を正とし zip を削除。逆でも可、どちらか一方)
   - **ルートに二重ビルドされた writeup pdf/中間物**(ソース .tex は docs/ にあるため)。
     ※ PDF は提出物になり得るので、削除前に docs/ 側 PDF と同一内容であることを確認。
2. **LaTeX ビルド先の一本化**: 以後 `latexmk -outdir=build/` を規約化し、
   `build/` を .gitignore に追加。ルート直下にビルドしない。
3. **.gitignore の整理統合**: ルートと `manual_redteam/` の 2 枚を見直し、
   - `manual_redteam/data/` 配下は `runs/` `cold_probes/` だけでなく
     `simulator_discover/ blindpass/ adaptive/ elicitations/` も同じ
     「README だけ追跡・中身は ignore」方式に統一(Phase 0 で快照済みが前提)。
     ※ ただし**ブラインドラベル結果の小さな jsonl は追跡候補**。判断は Phase 5 で。
   - `build/`, `*.zip` 追加。
4. **日付ミスの修正**: `manual_redteam/data/blindpass/2099-01-01_decomp_s12` →
   正しい日付へ rename(参照しているスクリプト/doc を grep して同時更新)。

**やらないこと**: ファイル移動・rename(データ dir の rename 1 件を除く)、
import 変更、スクリプト統合。締切前の構造変更は禁止。

**完了条件**: `find . -name '*.aux' -o -name '*.fls' ...` が 0 件 /
ルート直下が「ソース+ディレクトリ」だけになる。

---

## Phase L — ladder / YAML の canonical 化(締切前・~1日)

**目的**: 「canonical ladder は ONE referenced file、実験は参照のみ」という
CURRENT.md §5 の規約を物理層で実現する。これは CURRENT.md §4 アクティブプラン
項目 4(`ladder_canonical_v1.yaml` の組み立て)**そのもの**であり、FREEZE に
抵触しない(むしろ凍結済み計画の実行)。AIMS 公開物の中核アーティファクトでもある。

### L1. `ladder_canonical_v1.yaml` の作成(最優先)
CURRENT.md §1 の FROZEN 構造を 1 ファイルに固定:
- R0a–c(rapport, 非採点)→ S1–S4(runway, 採点)→ Bridge(非採点)→
  S9–S12(suicide, SEMANTIC)→ decimal overlay(S10.5/11.5/12.5, firewall band 限定)
- wording の出典は §1 の指定どおり: S1–S4 = longsetup `adaptive_run01`(rung タグ付き)、
  S9–S12.5 = `2026-06-02_gpt4omini_blue_decomp_climb` r02(disclaimer 除去版)。
- 各 rung にメタデータを持たせる: `rung_id`(一意・再利用禁止)、`scored: bool`、
  `scheme: semantic-decimal`、`source:`(出典 run)、`overlay: bool`。
- スキーマ検証スクリプト(rung_id 一意・S番号再利用なし・必須キー)を同時に書く
  → Phase 6 のテストに昇格。**二重ラダー事故(CLAUDE.md 冒頭の hazard)の機械的封じ込め。**

### L2. `ladders/` 44 変種のインデックス化と棚卸し
締切前は**物理移動しない**(スクリプトのパス参照を壊さない)。代わりに:
- `ladders/INDEX.md` を作成: 全 44 ファイルについて
  `バージョン → status(canonical-ancestor / superseded / ablation / dead) →
  使用した実験 doc → 対応 run dir` の対応表。
- どの変種がどの S-scheme(writeup0519 / s12ceiling_v1 / semantic-decimal)かを
  明記 — 二重ラダー混乱の解毒文書を兼ねる。
- 締切後(Phase 3 と同時)に `ladders/archive/` へ物理移動し、直下は
  `ladder_canonical_v1.yaml` + INDEX.md + 現役数本のみにする。

### L3. `context_prefixes/` の整理方針
604 本の userside YAML は**生成物に近い一次記録**(各 run の再現材料)なので削除しない。
- 締切前: `context_prefixes/INDEX.md` で実験グループ ~40 個に束ねた一覧を作る
  (`日付_実験名 → 本数 → 対応 doc/run`)。命名から機械生成できるので半自動化可能。
- 締切後(Phase 5 と同時): `context_prefixes/<date>_<experiment>/` にグループごと
  サブフォルダ化し、`_shard*/_pilot*/_resume*` の作業用 dir は `_work/` 配下に集約。
  参照スクリプトはその時点で attic 行きが大半なので、現役スクリプトの参照だけ
  grep で追って更新する。
- 新規 run は「`ladder_canonical_v1.yaml` を参照し、差分のみ run_config に書く」
  方式へ移行(CURRENT.md §5 の「実験は参照、再定義禁止」をデータ層でも貫徹)。

**完了条件**: `ladder_canonical_v1.yaml` が存在しスキーマ検証が通る /
INDEX.md 2 枚で全変種・全 prefix グループが追跡可能 /
以後の run config が canonical を参照している。

---

## Phase R — AIMS 公開パッケージ(締切前・~1日)

**目的**: 提出(6/23)に合わせて公開できる**クリーンな公開用リポジトリ**を、
内部リポジトリの整理完了を待たずに作る。方式 = **allowlist 輸出**。

### R1. 輸出スクリプト `scripts/export_public.py`(allowlist 方式)
明示的に列挙したものだけをコピーする(denylist ではなく allowlist — 漏出方向に安全):

| 公開する | 公開しない(理由) |
|---|---|
| `ladder_canonical_v1.yaml` + スキーマ + INDEX(構造のみ版) | `.env` / API キー(秘密情報) |
| harness コード(core/ + 現役 CLI ~10本) | **生トランスクリプト**(自殺関連の生対話 — 安全方針。CLAUDE.md: raw は data/runs に留める) |
| methodology / operator rulebook(公開向けに編集した版) | `codex_*_handoff_*.md` 等の内部 handoff・作業メモ |
| ブラインドラベル jsonl + seal checksum(C2 監査証跡) | 協力者名・内部レビュー入り doc(匿名化前) |
| 採点 rubric + labeler プロンプト | `context_prefixes/` 全量(エスカレーション用 userside 文面の悪用リスク → 代表例のみ・要判断) |
| 論文 + 図 + 再現手順 README | レガシー世代全部・運用ログ・blindpass 生コーパス |

### R2. 公開ポリシーの判断点(Shin + 必要なら Adhyyan/Jared 確認)
1. **userside 文面(攻撃側プロンプト)をどこまで公開するか** — 測定器論文として
   ladder の*構造とメタデータ*は公開必須だが、*逐語 wording* は dual-use。
   推奨: 構造 + S1–S4 例示は全文、S9–S12.5 は要約/パラフレーズ + 「研究者には
   request-basis で提供」の脚注。エスカレーション文面の全文公開は避ける。
2. 代表トランスクリプト(firewall-dissection 図用)は**抜粋 + 編集**で paper 内のみか、
   repo にも置くか。
3. ライセンス(コード MIT/Apache、データ・文書 CC BY-NC 等)と
   responsible-use README(Tier-4 ceiling の明記、CURRENT.md C4 主張と整合)。

### R3. 検証
- 輸出先でクリーン clone →`pip install -e . && pytest`(スキーマ検証)が通る。
- `git log` 履歴は持ち込まない(輸出先は initial commit から — 過去の
  生データ混入履歴を引きずらない)。
- 秘密スキャン(`gitleaks` 等)+ 全文 grep(モデル実名・協力者名・絶対パス)を
  輸出スクリプトの最終ステップに組み込む。

**完了条件**: 公開用 repo がワンコマンドで再生成できる / 中身が allowlist と
一致 / 秘密・生トランスクリプト・内部メモが 0 件(スキャンで機械確認)。

---

## Phase 2 — レガシー世代の隔離(締切後・~半日)

**目的**: 第1世代(memory/lookism)を第2世代から物理的に分離し、リポジトリの
「現在」を `manual_redteam/` に一致させる。

1. `legacy/2026-04_memory_lookism/` を作り、`git mv` で移動(履歴保持):
   - `src/`, `scripts/`(experiments/ analysis/ とも), `tests/`, `configs/`,
     `reports/`, `Experiment_01/`, `Experiment_02/`, `latex/`, `calibration/`, `logs/`
   - ルートの notebook 4本(`Run_Experiment_Laxman.ipynb` 418KB ほか)と
     `run_experiment.py`
   - ルート md 群: `project_plan.md`, `roadmap.md`, `STATUS.md`, `QUICKSTART.md`,
     `implementation.md`, `experiment_01.md`, `experiment_02.md`,
     `manual_transcript_spec.md`, `requirements.txt`(レガシー専用なら)
   - ルート `data/`(74MB, ignored)→ 中身はオフライン快照済みなのでディスクからも
     `legacy/` 直下 or 外部アーカイブへ
2. `legacy/2026-04_memory_lookism/README.md` を 1 枚書く:
   何の実験だったか・どの writeup に対応するか・「凍結、依存なし」を明記。
3. `tests/` 内のレガシーテストは legacy 配下に同伴(import パス
   `from src.…` → `from legacy….src.…` に直すか、**直さず「legacy 内では実行しない」
   と README に書くだけ**でも可。レガシーを動態保存する価値は低い)。
4. ルート `README.md` を書き直し: リポジトリ=manual_redteam プロジェクト、
   legacy/ は凍結アーカイブ、と宣言。

**リスクと対策**: `docs/` の 4月系 writeup がレガシーコードを参照する。doc は
動かさない(Phase 4 で扱う)ので、レガシー側 README に対応表を書いて吸収。

**完了条件**: ルート直下 = `manual_redteam/ docs/ legacy/ CLAUDE.md README.md
REFACTORING_PLAN.md .gitignore .env(.example)` 程度まで縮む。

---

## Phase 3 — manual_redteam のパッケージ化(締切後・1〜2日)

**目的**: 「72 本のワンオフ + 暗黙の共有モジュール」を
「小さな core ライブラリ + 日付付き実験ドライバ」に分離する。
これは branch `manual-redteam-v0` で始まった移行の完成形。

### 3a. core 移行の完成(最優先・機械的)
1. `scripts/_session_io.py` の**実装本体を `core/session_io.py` へ移動**し、
   ファサードの向きを反転(`scripts/_session_io.py` を
   `from manual_redteam.core.session_io import *` の互換シムにする)。
2. `_session_io` を import する 17 本を `manual_redteam.core.session_io` 参照へ更新。
3. `pyproject.toml` 新設(`pip install -e .`)。sys.path ハック・相対 import 撤廃。
4. 全スクリプトに対し `python -m py_compile` + 代表 3 本のドライランで検証。
5. 1〜2 週間後、互換シム `_session_io.py` を削除。

### 3b. スクリプトの三分類
72 本を棚卸しして 3 つに分ける(分類表を `manual_redteam/scripts/INVENTORY.md` に残す):

| 分類 | 行き先 | 例 |
|---|---|---|
| **harness**(再利用・現役) | `manual_redteam/core/` + 薄い CLI を `scripts/` に残す | `create_run` `manual_chat` `subject_turn` `render_session` `derive_cold_run` `replay_userside_script` `seal_labels` `validate_relabel_pass` `prepare_annotations` `export_markdown` |
| **experiment driver**(日付付きワンオフ、再現性のため保存) | `manual_redteam/experiments/<date>_<name>/run.py`(対応する docs・run dir と名前を揃える) | `phaseE_*` ×6, `s1s7_runway_pilot`, `delusion_pilot`, `analyze_*`, `simulator_discover_*` |
| **dead**(上位互換あり・実行不能) | `manual_redteam/experiments/_attic/` へ(削除はしない — 監査来歴のため) | `adaptive_strictness_profile.py`(v3/v3.5 に上書きされた版)等 |

### 3c. 重複系列の共通化(挙動を変えない範囲で)
- `build_*_blindpass_corpus.py` ×4 と `unblind_*.py` ×3 →
  `core/blindpass.py`(corpus 構築・シャッフル・seal・unblind)に共通化し、
  各実験差分は config(yaml)で表現。**既存 run の再現には旧スクリプトを attic に保存**。
- 判定ロジック(advance-gating 記録、endorsement 判定の I/O)を `core/gating.py` に
  集約 — CURRENT.md §1c の BINDING ルールをコードで強制する土台。

**完了条件**: `scripts/` 直下は harness CLI ~10本のみ / すべて
`manual_redteam.core` 経由 / `pip install -e . && pytest` が通る(テストは Phase 6)。

---

## Phase 4 — docs 統廃合(締切後・~1日、判断は Shin)

**目的**: 「CURRENT.md が真実、日付 docs は履歴」という確立済みの規約を
**全 doc に機械的に適用**する。削除はしない(append-only 原則)。

1. **ルート `docs/`(4月〜5月の writeup 群)**:
   - `.tex`+`.md` ソースと最終 PDF だけ残し、`docs/papers/` に整列
     (`writeup_2026_04_14/`, `writeup_2026_05_19/`, … 1 writeup 1 dir)。
   - 4月系(memory/lookism の writeup)は `legacy/` 側へ移すか docs/papers に
     残すか — **Shin 判断**(対外提出履歴があるなら papers に残す)。
2. **`manual_redteam/docs/` 101 本**:
   - frontmatter `status: active|superseded|ablation` を全数付与
     (CURRENT.md・DECISIONS.md・rulebook・framing decisions = active、
     それ以外の大半 = superseded で、`superseded_by:` を記入)。
   - `status: superseded` のものを `archive/` へ移動(既存 archive 23 本と合流)。
     CURRENT.md からリンクされている doc は移動禁止リストで保護
     (grep で参照チェックを通してから動かす)。
   - handoff 系(`codex_*_handoff_*.md`)とラベラープロンプト(`*.txt`)は
     `docs/handoffs/`, `docs/labeler_prompts/` にサブフォルダ化。
3. **リンク健全性チェック**をスクリプト化(`scripts/check_doc_links.py`):
   CURRENT.md / DECISIONS.md / 各 active doc から張られた相対パスが解決できるか。

**完了条件**: `manual_redteam/docs/` 直下 = CURRENT.md, DECISIONS.md + active 数本
+ サブフォルダのみ。全 doc に status frontmatter。

---

## Phase 5 — データレイアウトの一本化(締切後・~半日)

**目的**: 「何を git で追跡し、何をローカル保管するか」の方針を 1 つにする。
現状は runs/cold_probes だけ ignore、simulator_discover/blindpass/adaptive は
未追跡のまま放置という最悪の中間状態。

方針(案 — Shin 確認の上で確定):
- **生トランスクリプト(subject の応答そのもの)= git 追跡しない**。
  `manual_redteam/data/{runs,cold_probes,simulator_discover,adaptive,elicitations}/`
  はすべて「README+manifest のみ追跡」。実体は定期 tar 快照(Phase 0 の方式を
  cron 化するか、提出前後に手動)。
- **ブラインドラベル(score-of-record)と seal/checksum = git 追跡する**。
  小さい・テキスト・改竄検知が価値、なので `blindpass/**/labels*.jsonl` と
  manifest は追跡対象に戻す(paper の C2 主張の監査証跡)。
- 各 data サブディレクトリに `manifest.yaml`(run id → 日付・モデル・ladder 版・
  対応 doc)を置き、`portfolio/RUNS.md` から一元参照。
- run ディレクトリ命名規約を 1 つに固定(`YYYY-MM-DD_<slug>_<model>`)。既存の
  揺れは rename しない(参照壊れリスク>美観)。新規のみ強制。

**完了条件**: .gitignore が data 方針を 1 ブロックで表現 / 追跡対象の
labels/manifest がコミット済み / 快照手順が README 化。

---

## Phase 6 — テスト・CI・再発防止(締切後・~1日)

**目的**: 「また溜まる」を防ぐ最小限の自動化。

1. **smoke テスト新設**(`manual_redteam/tests/`):
   - `session_io` の run 作成→turn 追記→render の round-trip
   - canonical ladder YAML(`ladder_canonical_v1.yaml`)のスキーマ検証
     (rung id 一意・S番号再利用なし — 二重ラダー事故の機械的防止)
   - advance-gating ログのスキーマ検証(§1c のコード化)
   - blindpass seal の checksum 検証
2. **pre-commit hook**: ruff(lint+format)/ 生成物拡張子(aux, .DS_Store, zip,
   pdf-at-root)のブロック / 巨大ファイル(>5MB)警告。
3. **doc lint**(Phase 4 のリンクチェッカー + frontmatter status 必須)を
   pre-commit か手動スクリプトで。
4. CI は GitHub Actions で `pytest + ruff + doc lint` の 1 workflow のみ(過剰整備しない)。

**完了条件**: クリーン checkout から `pip install -e . && pytest` が green /
pre-commit が生成物の再流入を止める。

---

## 実施順序と工数まとめ

| Phase | 時期 | 工数目安 | リスク |
|---|---|---|---|
| 0 セーフティネット | **即日** | 1h | なし(保全のみ) |
| 1 衛生作業 | 締切前OK | 0.5d | 低(削除対象の再生成可能性のみ確認) |
| **L ladder canonical 化** | **締切前(実験にも必要)** | 1d | 低(新規作成+INDEX、移動なし) |
| **R AIMS 公開パッケージ** | **締切前(提出と同時公開)** | 1d | 中(公開範囲の判断は Shin/共同研究者) |
| 2 レガシー隔離 | 6/23後 | 0.5d | 低(git mv、参照なし確認済み) |
| 3 パッケージ化 | 6/23後 | 1–2d | 中(import 変更 → ドライラン必須) |
| 4 docs 統廃合 | 6/23後 | 1d | 低(移動のみ、削除なし) |
| 5 データ方針 | 6/23後 | 0.5d | 中(追跡方針は Shin 確定が前提) |
| 6 テスト・CI | 6/23後 | 1d | 低 |

締切前の優先順は **0 → L → R → 1**(1 は隙間時間で可)。L は CURRENT.md の
アクティブプラン項目 4 と同一作業なので、リファクタというより実験計画の消化。

## 横断ルール

- 1 フェーズ = 1 ブランチ = レビュー可能な少数コミット。フェーズをまたいで混ぜない。
- **削除より移動**(attic / archive / legacy)。監査来歴・再現性が論文の主張(C2)
  そのものなので、「消す」操作は Phase 0 の快照に存在することを確認してから。
- 各フェーズ完了時に `docs/DECISIONS.md` に 1 行(日付・何を・なぜ)。
- 生トランスクリプトの置き場(`manual_redteam/data/runs/`)と Tier-4 運用は不変。

## Shin の判断待ち

**Phase R までに必要(締切前)**:
1. **userside 逐語 wording の公開範囲**(推奨: 構造+S1–S4 全文、S9–S12.5 は
   要約+request-basis 提供 — dual-use 配慮)
2. 代表トランスクリプトを repo に置くか paper 内抜粋のみか
3. ライセンスと responsible-use 文言

**Phase 5 までに(締切後で可)**:
4. ブラインドラベル jsonl を git 追跡に戻すか(推奨: 戻す — 公開物 R1 とも整合)
5. 4月系 writeup の置き場(legacy か docs/papers か)
6. レガシーコードを「動態保存」するか「凍結アーカイブ」か(推奨: 凍結)
