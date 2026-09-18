# `run_three_loop_master_basis_all.bat` 操作説明書・仕様書

## 1. 目的

`run_three_loop_master_basis_all.bat` は、QEDCalc の 3 ループ電子頂点補正における **Stage-2: canonical family ごとの master-basis 確定処理**を、複数 family に対して連続実行するための最上位バッチです。

主な目的は次のとおりです。

- canonical family ごとの baseline seed を計算する
- one-axis boundary seed `r+1 / s+1 / d+1` を計算する
- seed を変えても master basis が安定かを監査する
- seed-dependent の場合は mandatory union reduction に自動移行する
- candidate master basis の closure を検証する
- 最終的に `promotion-ready` 監査成果物を作る
- 中断後に、既存の監査結果や checkpoint を再利用して再開する
- 一度に処理する canonical family 数を制限して、安全に unattended 実行する

このバッチは **canonical registry を自動更新しません**。
master basis が確定しても、`canonical_family_registry.py` への正式登録は、成果物を確認した後に Git 上で別途行います。

---

## 2. 動作環境

想定環境は次のとおりです。

- Windows 11
- QEDCalc リポジトリ
- Python 仮想環境
  - `.venv\Scripts\python.exe`
- WSL / Linux
- Kira
- FireFly
- Fermat

QEDCalc からは Windows 側の BAT を実行し、重い Kira / FireFly 計算は WSL 側で行います。

実行前に、通常はリポジトリを最新化します。

```powershell
git pull
```

---

## 3. 基本構文

```powershell
.\run_three_loop_master_basis_all.bat plan [START_FAMILY] [MAX_FAMILIES]
.\run_three_loop_master_basis_all.bat run [START_FAMILY] [MAX_FAMILIES]
.\run_three_loop_master_basis_all.bat status
.\run_three_loop_master_basis_all.bat resume [MAX_FAMILIES]
```

4つのモードがあります。

| モード | 用途 |
|---|---|
| `plan` | 実行予定だけ確認する。Kira は起動しない |
| `run` | 指定地点から実計算を開始する |
| `status` | checkpoint と自動再開位置を表示する |
| `resume` | 最初の未完了 family を自動検出して再開する |

---

## 4. canonical family と diagram の違い

本バッチの実行単位は **Feynman 図そのものではなく canonical family** です。

例えば、

```text
Q12_full -> Q12 / Q35
```

なので、

- `Q12` は1つの Feynman 図
- `Q35` も1つの Feynman 図
- `Q12_full` は Q12 と Q35 をまとめて扱う1つの canonical family

です。

したがって、

```text
MAX_FAMILIES=5
```

は「5図」ではなく、**最大5 canonical families** を意味します。

例えば現在の schedule で Q12 から5 familyなら、

```text
Q12_full
Q17_full
Q18_full
Q20_full
Q22_full
```

の5 familyです。

これらがそれぞれ2図をカバーする場合、元の Feynman 図としては合計10図をカバーします。

---

## 5. `plan` モード

### 5.1 用途

実計算を始める前に、

- 何 family が選択されるか
- どの family から始まるか
- どの seed が既存結果として再利用されるか
- どの seed を新規計算するか
- おおよその実行時間

を確認します。

### 5.2 例

```powershell
.\run_three_loop_master_basis_all.bat plan Q12_full 2
```

これは、

- Q12_full から開始
- 最大2 canonical families
- 実計算はしない

という意味です。

### 5.3 表示例

```text
selected families: 2
selected canonical families: 2 / max 2
covered diagrams in selected families: 4
first family: Q12_full
last family: Q17_full
```

### 5.4 REUSE 表示

既存の正式な seed audit または checkpoint がある場合、その seed は再計算せず再利用します。

例:

```text
REUSE Q12_full baseline    r8s3d0 firefly via audit: ...
REUSE Q12_full boundary-r r9s3d0 firefly via audit: ...
REUSE Q12_full boundary-s r8s4d0 firefly via audit: ...
REUSE Q12_full boundary-d r8s3d1 firefly via audit: ...
```

この表示により、「なぜその seed が SKIP されたか」を確認できます。

### 5.5 時間見積り

`plan` は、過去の実測履歴から次の3値を表示します。

```text
low
median
high
```

これは **現在未実行の baseline / boundary seed 計算**に対する目安です。

重要:

```text
union/candidate-closure rescue time is not included until a family proves unstable
```

と表示されるように、seed-dependent family で必要になる

- mandatory union reduction
- candidate closure
- no-rerun closure re-audit

の追加時間は、初期見積りには含まれません。

したがって、`high` は「全処理時間の厳密な上限」ではありません。

---

## 6. `run` モード

### 6.1 基本例

```powershell
.\run_three_loop_master_basis_all.bat run Q12_full 2
```

意味:

- Q12_full から開始
- 未完了 canonical family を最大2 family処理
- 既存の合格済み seed audit は再利用
- family が promotion-ready になるまで自動処理
- 1 family 完了後、次の family へ進む

### 6.2 family ごとの処理フロー

各 family では、概ね次の順序で処理します。

```text
既存結果の確認
  |
  +-- baseline が未実行 -> FireFly/Kira 実行
  |
  +-- boundary-r が未実行 -> FireFly/Kira 実行
  |
  +-- boundary-s が未実行 -> FireFly/Kira 実行
  |
  +-- boundary-d が未実行 -> FireFly/Kira 実行
  |
  v
boundary aggregate audit
  |
  +-- stable
  |     |
  |     v
  |   promotion-ready
  |
  +-- seed-dependent / unstable
        |
        v
      mandatory union reduction
        |
        v
      candidate closure
        |
        v
      no-rerun closure re-audit
        |
        v
      promotion-ready
```

---

## 7. baseline と one-axis boundary

標準的には1 familyにつき、次の4 seed を扱います。

```text
baseline
boundary-r
boundary-s
boundary-d
```

例えば baseline が、

```text
r8s3d0
```

なら、

```text
baseline   r8s3d0
boundary-r r9s3d0
boundary-s r8s4d0
boundary-d r8s3d1
```

です。

これらを比較し、baseline の master representatives が seed 拡張に対して安定かを調べます。

---

## 8. stable family

baseline と各 boundary で master basis が安定している場合、baseline の master set を候補として採用できます。

その場合、controller は stable-one-axis-baseline の proof として promotion-ready artifact を生成します。

概念的には、

```text
baseline masters
  =
boundary-r でも維持
  =
boundary-s でも維持
  =
boundary-d でも維持
```

であることを確認します。

---

## 9. seed-dependent family と union rescue

boundary の一部で baseline master が維持されない場合、baseline の master set をそのまま正式採用しません。

例えば Q12_full では、

```text
baseline r8s3d0 : 82 masters
r9s3d0          : 82, retained 82/82
r8s4d0          : 82, retained 82/82
r8s3d1          : 66, retained 63/82

intersection : 63
union        : 85
```

となったため、

```text
stable under tested one-axis extensions: False
union reduction needed: True
```

です。

この場合、自動的に次へ進みます。

```text
85-form union
  |
  v
mandatory-union reduction
  |
  v
candidate master basis
  |
  v
candidate closure
  |
  v
no-rerun closure re-audit
  |
  v
promotion-ready
```

baseline の master 数と、最終 master 数は一致するとは限りません。

---

## 10. promotion-ready

family の master basis が必要な監査を通過すると、

```text
output\three_loop_integral_family_audit\
three_loop_<family>_promotion_ready.json
```

が生成されます。

例:

```text
three_loop_q12_full_promotion_ready.json
```

この成果物には概ね、

- family
- baseline seed
- 提案 master-basis ID
- master count
- master-basis source
- proof mode
- proof audit
- audit_pass

が記録されます。

ただし、ここで **canonical registry は自動変更されません**。

promotion-ready artifact を人間が確認した後、

```text
canonical_family_registry.py
```

を Git 上で正式更新します。

これは unattended 長時間計算中に、実行コード自身が registry を書き換えないための安全設計です。

---

## 11. `MAX_FAMILIES`

### 11.1 意味

`MAX_FAMILIES` は、その1回の unattended 実行で処理する **未完了 canonical family の最大数**です。

例:

```powershell
.\run_three_loop_master_basis_all.bat run Q12_full 2
```

なら、Q12_full から始めて最大2 familyです。

### 11.2 promotion-ready family

すでに promotion-ready の family は未完了対象から除外されます。

したがって `MAX_FAMILIES=2` は、

「schedule 上の2項目」

ではなく、

**選択開始位置以降の未完了 family を最大2つ**

という意味です。

### 11.3 初回運用の推奨

最初から大きな値を指定せず、

```text
2 families
  ->
結果確認
  ->
5 families
  ->
さらに拡大
```

のように段階的に増やす方が安全です。

---

## 12. `status` モード

### 12.1 実行

```powershell
.\run_three_loop_master_basis_all.bat status
```

### 12.2 用途

主に次を確認します。

- checkpoint の状態
- pass / fail / running などの件数
- 直近の失敗情報
- 自動再開すべき最初の family

例:

```text
auto-resume family: Q18_full
```

この family 名を利用者が覚えておく必要はありません。

---

## 13. `resume` モード

### 13.1 family 名なしで再開

```powershell
.\run_three_loop_master_basis_all.bat resume
```

controller が、

- promotion-ready artifact
- checkpoint
- 既存の成功 seed audit

を調べ、最初の未完了 family を自動検出します。

### 13.2 再開時にも family 数制限

```powershell
.\run_three_loop_master_basis_all.bat resume 2
```

なら、自動検出した未完了地点から最大2 canonical familiesを処理します。

PC 再起動後などは、

```powershell
git pull
.\run_three_loop_master_basis_all.bat status
.\run_three_loop_master_basis_all.bat resume 2
```

という使い方が基本です。

---

## 14. 再利用される成果物

controller は、成功済み seed reduction を再利用します。

正式な generic seed audit の例:

```text
three_loop_q12_full_firefly_r8s3d0_generic_audit.json
three_loop_q12_full_firefly_r9s3d0_generic_audit.json
three_loop_q12_full_firefly_r8s4d0_generic_audit.json
three_loop_q12_full_firefly_r8s3d1_generic_audit.json
```

対応する master list の例:

```text
q12_full_firefly_r8s3d0_masters.txt
```

再利用した seed は `plan` で `REUSE` と表示されます。

---

## 15. checkpoint

checkpoint は概ね次に保存されます。

```text
output\three_loop_integral_family_audit\
three_loop_master_basis_batch_checkpoint.json
```

seed step ごとに、

- family
- phase
- seed
- solver
- status
- elapsed time
- detail

などが記録されます。

主な status は、

```text
running
pass
fail
soft-fail
```

などです。

---

## 16. runtime history

実測時間は、

```text
output\three_loop_integral_family_audit\
three_loop_master_basis_runtime_history.json
```

へ蓄積されます。

`plan` の low / median / high は、このローカル実測履歴を優先して使用します。

データが不足する場合は、過去の既定サンプルから広めの推定値を使います。

---

## 17. FireFly の stale-state 対策

seed 計算を新規実行する際は、古い FireFly 状態が新規計算へ混入しないよう、関連ディレクトリを削除してから Kira を起動します。

代表例:

```text
results
sectormappings
tmp
firefly_saves
ff_save
firefly_saves_alt
pyred
```

これは過去に発生した、

```text
Validation failed: Entry 0 does not match the black-box result!
```

のような stale FireFly save 問題を避けるためです。

---

## 18. エラー時の基本動作

### 18.1 seed reduction が失敗

baseline / boundary の Kira または audit が失敗した場合、その family で停止します。

次の family へは進みません。

### 18.2 boundary aggregate audit が失敗

監査結果を信用できないため停止します。

### 18.3 union reduction が失敗

その family で停止します。

### 18.4 candidate closure

通常の text-equation closure audit は、Kira 自体が完了していても non-master target の人間可読式が出力されないため、非0終了する場合があります。

そのためこの段階は provisional として扱い、続いて必ず、

```text
no-rerun closure re-audit
```

を実行します。

最終判定は no-rerun re-audit を優先します。

---

## 19. 中断・PC再起動時の挙動

seed level の成功結果は generic audit と checkpoint に残るため、再開時に再利用できます。

したがって、

```text
baseline PASS
boundary-r PASS
boundary-s 実行中にPC停止
```

なら、再開後は baseline と boundary-r を再利用し、未完了地点から進みます。

ただし、現行実装では **union reduction / candidate closure の途中段階は seed step と同じ粒度では完全には再利用されません**。

例えば、

```text
union reduction 完了
  ->
candidate closure の途中でPC停止
```

のようなケースでは、`resume` 後に union rescue フローへ再度入り、union reduction が再実行される可能性があります。

つまり現在の restart granularity は、

- baseline / boundary seed: 高い再利用性
- family-ready: 再利用可能
- union / closure の中間段階: 再実行の可能性あり

です。

この点は unattended 運用上の既知仕様です。

---

## 20. 実行例

### 20.1 まず2 familyだけ試す

計画:

```powershell
.\run_three_loop_master_basis_all.bat plan Q12_full 2
```

実行:

```powershell
.\run_three_loop_master_basis_all.bat run Q12_full 2
```

### 20.2 次回は5 family

```powershell
.\run_three_loop_master_basis_all.bat plan Q18_full 5
.\run_three_loop_master_basis_all.bat run Q18_full 5
```

ただし、開始 family を利用者が覚えていない場合は `resume` を使います。

### 20.3 PC再起動後

```powershell
git pull
.\run_three_loop_master_basis_all.bat status
.\run_three_loop_master_basis_all.bat resume 2
```

### 20.4 family 数制限なしで全未完了を対象

```powershell
.\run_three_loop_master_basis_all.bat plan
```

または、

```powershell
.\run_three_loop_master_basis_all.bat run
```

ただし長時間 unattended 実行になる可能性が高いため、通常は `MAX_FAMILIES` を指定する方が安全です。

---

## 21. 推奨運用

通常は次の流れを推奨します。

```text
1. git pull
2. plan で対象 family と REUSE を確認
3. MAX_FAMILIES を小さめに指定
4. run
5. 終了後にログ確認
6. promotion-ready JSON を確認
7. canonical registry を reviewed Git change として更新
8. 次の batch へ
```

初回の unattended 実行では、

```text
MAX_FAMILIES=2
```

程度から始め、正常性を確認してから5以上へ増やすのが安全です。

---

## 22. 本バッチが自動化する範囲

自動化対象:

- family schedule の読み込み
- baseline / boundary seed の不足判定
- FireFly/Kira seed reduction
- 既存 seed audit の再利用
- runtime 記録
- boundary aggregate audit
- stable 判定
- mandatory union reduction
- candidate closure
- no-rerun re-audit
- promotion-ready artifact 生成
- 次 family への連続実行
- 最初の未完了 family の自動検出

自動化しないもの:

- `canonical_family_registry.py` の正式更新
- master integral の解析的評価
- epsilon expansion
- 各 diagram の最終 `F2(0)`
- 72図全体の3ループ `g-2` 係数の最終合成

---

## 23. 関連ファイル

主な実装は次のとおりです。

```text
run_three_loop_master_basis_all.bat

examples/
  three_loop_master_basis_batch_controller.py
  three_loop_master_basis_pipeline.py
  three_loop_master_basis_boundary_audit.py

three_loop/
  master_basis_batch.py
  master_basis_api.py
  master_basis_schedule.py
```

補助 BAT:

```text
run_three_loop_master_basis_seed.bat
run_three_loop_master_basis_union_reduction.bat
run_three_loop_master_basis_candidate_closure.bat
run_three_loop_master_basis_candidate_closure_reaudit.bat
```

作業履歴:

```text
doc/THREE_LOOP_WORKLOG.md
```

---

## 24. 現在の設計上の重要原則

1. canonical family を Stage-2 の原子的な処理単位とする
2. 重い計算結果は可能な限り再利用する
3. seed-dependent master representatives を baseline の見た目だけで正式採用しない
4. one-axis boundary で不安定なら mandatory union を使う
5. candidate closure の最終判定には no-rerun re-audit を用いる
6. unattended 計算中に executable registry を書き換えない
7. batch サイズは `MAX_FAMILIES` で利用者が安全側に制限できる
8. PC停止後は family 名を覚えていなくても `resume` できる
9. `plan` で実行前に REUSE 根拠まで確認できる
10. 長時間計算は family ごとに promotion-ready まで完結させてから次へ進む

---

## 25. 最短操作早見表

### 初回確認

```powershell
git pull
.\run_three_loop_master_basis_all.bat plan Q12_full 2
```

### 実行

```powershell
.\run_three_loop_master_basis_all.bat run Q12_full 2
```

### 状態確認

```powershell
.\run_three_loop_master_basis_all.bat status
```

### 中断後の再開

```powershell
git pull
.\run_three_loop_master_basis_all.bat status
.\run_three_loop_master_basis_all.bat resume 2
```

### 少し大きな batch に拡大

```powershell
.\run_three_loop_master_basis_all.bat resume 5
```
