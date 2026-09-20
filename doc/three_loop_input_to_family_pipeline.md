# 3ループ formal input → canonical family パイプライン

## 1. 目的

3ループ計算で途切れていた前段を、次の一本の経路として固定する。

```text
3loop_vertex_72_complete_equations.md
        ↓
input/three_loop/*.tex
        ↓
formal input graph data
        ↓
data/three_loop_topologies.json と厳密照合
        ↓
既存 canonical-family autodiscovery / registry
        ↓
45 canonical integral families
        ↓
既存 master-basis pipeline
```

今回追加する処理は **Kira / FireFly を起動しない**。したがって、別コンソールで実行中の

```powershell
.\run_three_loop_master_basis_all.bat resume 4
```

を止めたり、master-basis の計算結果を書き換えたりしない。

## 2. 正式入力

正式入力は次の72ファイル。

```text
input/three_loop/
  Q01.tex ... Q50.tex
  VP01.tex ... VP12.tex
  VP4A.tex
  VP4B.tex
  VP4C.tex
  VP22.tex
  LBL01.tex ... LBL06.tex
  manifest.json
```

個数は

```text
50 + 12 + 3 + 1 + 6 = 72
```

である。

各 `.tex` は、`3loop_vertex_72_complete_equations.md` に記載された完全な3ループ運動量積分式を保持する。

さらにコメントヘッダとして、

- diagram ID
- physical family
- source document
- graph metadata

を持つ。

これにより、式とgraph dataの対応がファイル単位で固定される。

## 3. manifest

`input/three_loop/manifest.json` は72入力について、

- diagram ID
- input path
- physical family
- source document
- SHA-256

を保持する。

監査時には各 `.tex` のSHA-256を再計算し、manifestと一致しなければ停止する。

したがって、式を変更したのに分類データだけ古いまま残る事故を検出できる。

## 4. graph data の扱い

現段階では、任意のraw LaTeXからFeynman graphを完全自動認識するとはしていない。

72図の原典では diagram ID と topology がすでにレビュー済みなので、正式入力では

```text
完全なLaTeX振幅 + reviewed graph metadata
```

を一組の入力データとして保存する。

そのgraph metadataを、独立に存在する既存の

```text
data/three_loop_topologies.json
```

と **72図すべて完全一致比較**する。

この構造は、将来 raw LaTeX → graph の自動認識を実装したときの72ケースの回帰正解データにもなる。

## 5. 実行

仮想環境をセットアップ済みのQEDCalcルートで、

```powershell
run_three_loop_input_to_family_audit.bat
```

を実行する。

処理は次の順序。

```text
72 formal .tex
    ↓
manifest / SHA-256 validation
    ↓
amplitude provenance sanity check
    ↓
graph metadata 読み出し
    ↓
data/three_loop_topologies.json と完全比較
    ↓
既存 build_global_classification()
    ↓
既存 apply_confirmed_family_registry()
    ↓
72 diagrams → 45 canonical families
```

## 6. 正常時の条件

少なくとも次を満たす必要がある。

```text
formal input diagrams          = 72
unique diagram IDs             = 72
physical family counts         = 50 / 12 / 3 / 1 / 6
graph/registry exact matches   = 72 / 72
classification complete        = True
canonical families             = 45
audit                          = PASS
```

## 7. 出力

```text
output/three_loop_input_pipeline/
  three_loop_input_to_family_audit.json
  three_loop_input_to_family_audit.md
```

Markdownには72図すべてについて、

```text
diagram
  → formal input
  → physical family
  → canonical family
  → current master_basis_id
```

を一覧化する。

したがって、例えば将来的に

```text
Q01.tex
  → Q01 graph
  → Q01_full
  → Q01_final60
```

という由来を一方向に追えるだけでなく、

```text
Q01_final60
  → Q01_full
  → Q01
  → input/three_loop/Q01.tex
```

と逆方向にも追える。

## 8. 現在の master-basis 計算との関係

今回のパイプラインは、既存の master-basis 計算の **前段**を補完する。

```text
72 formal Feynman amplitudes
        ↓
72 verified graph records
        ↓
45 canonical families
        ↓
run_three_loop_master_basis_all.bat
```

現在の `resume 4` を再スタートする必要はない。

canonical registry に新しい `master_basis_id` が昇格されれば、この前段監査を再実行するだけで provenance report にそのIDが反映される。

## 9. 再現性の基準

3ループ計算では、少なくとも

```text
source amplitude
 → formal input
 → graph
 → topology registry
 → canonical family
 → IBP/master-basis stage
```

まで、人間の記憶だけに依存する未記録の変換を挟まない。

最終的な目標は、この経路をさらに

```text
 → stable master basis
 → master integral evaluation
 → renormalization
 → 72-diagram sum
 → analytic three-loop coefficient
```

まで延長することである。
