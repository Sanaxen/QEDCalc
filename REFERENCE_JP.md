# QEDCalc v0.90.0 リファレンスマニュアル

## 1. 目的

QEDCalc は、長大な QED 摂動計算を、小さく検証可能な数学・物理処理へ分解して実行するための数式処理基盤です。物理的な処理順序は人間が決め、QEDCalc は機械的な代数処理を担当し、各段階の中間結果を監査できる形で残します。

v0.90.0 では、電子異常磁気能率の2ループ7図について、将来の変更から守るための完成 baseline が固定されました。

基本方針は次のとおりです。

- 人間が物理的な計算経路を決める。
- 非可換な因子順序は明示的に保持し、失われた順序を推測しない。
- Dirac 代数、trace、projector、Feynman parameter 化、loop shift、tensor reduction、renormalization、IBP reduction、regression を分離した処理として扱う。
- 中間式を LaTeX / Markdown で確認できるようにする。
- 未定義記号、不完全な basis、未対応 topology を勝手に推測しない。
- 可能な箇所では exact symbolic residual = 0 を checkpoint とする。

1ループ頂点補正サンプルは

$$
F_2(0)=\frac{\alpha}{2\pi}
$$

を再現します。

2ループ完成 baseline は

$$
A_1^{(4)}
=
\frac{197}{144}
+\frac{\pi^2}{12}
+\frac34\zeta(3)
-\frac{\pi^2}{2}\ln2
$$

を再現します。

---

## 2. 現在のバージョンと環境

現在の release baseline は **QEDCalc v0.90.0** です。

正式な package version は `pyproject.toml` を基準とします。

scientific calculation layer の主な環境は次のとおりです。

- Windows 11
- Python 3.11+
- SymPy 1.13+

`setup_env.bat` を実行すると `.venv` を作成し、必要 package を導入します。

v0.90 の標準ライブラリ2ループ regression は SymPy が無い環境でも実行できます。その場合、scientific symbolic checkpoint は失敗ではなく明示的に SKIPPED となります。

---

## 3. 主なディレクトリ構成

```text
QEDCalc/
├─ data/
├─ doc/
├─ examples/
├─ input/
├─ output/
├─ qedcalc/
│  ├─ config/
│  ├─ core/
│  ├─ history/
│  ├─ latex/
│  ├─ operations/
│  ├─ parser/
│  └─ validation/
├─ tests/
├─ conventions.txt
├─ pyproject.toml
├─ README.md
├─ README_JP.md
├─ REFERENCE.md
├─ REFERENCE_JP.md
├─ ROADMAP.md
└─ CHANGELOG.md
```

v0.90 のドキュメント整理以前の累積版は `doc/archive/` に保存します。

---

## 4. QED-LaTeX 入力

QEDCalc は一般的な LaTeX 全体を解析する parser ではなく、QED 計算に必要な限定された LaTeX 構造を扱います。

代表的な構造は次のとおりです。

- scalar symbol
- Lorentz vector / index
- gamma matrix
- Feynman slash
- metric tensor
- scalar product
- fermion / photon propagator 構造
- 可換積
- 非可換積
- loop-integral expression

特に重要なのは、fermion chain の順序を明示的に保持する点です。QEDCalc は、いったん失われた非可換順序を後から推測しません。

基本入口は

```python
from qedcalc import parse_latex
expr = parse_latex(source)
```

です。

---

## 5. 計算規約

`conventions.txt` には、計算規約に依存する設定をまとめています。

代表例：

- metric signature
- gauge
- renormalization scheme
- dimensional-regularization dimension
- MS / MS-bar subtraction
- subdiagram に coupling、loop measure、$i$ factor を含めるかどうか

読み込みは

```python
from qedcalc.config import load_conventions
conv = load_conventions()
```

です。

未対応規約を別規約へ黙って置き換えることはしません。たとえば Feynman gauge 専用 bridge で covariant gauge が未実装なら、longitudinal term を落とすのではなく未対応として停止します。

---

## 6. 主な数式処理機能

### 6.1 Dirac / Lorentz 代数

1ループおよび検証済み2ループ経路で必要な gamma contraction、Dirac trace、Lorentz contraction を処理します。長大な projector trace では、不要な巨大 metric expression を作らず scalar polynomial へ直接縮約する経路もあります。

### 6.2 Feynman parameter 化

単純 pole および正の整数べきの分母を parameter 化できます。多ループ二次形式の平方完成と、分子への simultaneous loop shift も処理できます。

### 6.3 tensor reduction

一般 $D$ 次元の even-rank isotropic tensor reduction を備え、多ループでは平方完成後の inverse quadratic matrix を使った mixed tensor reduction を行えます。

### 6.4 dimensional regularization / pole

UV / IR regulator を区別した bookkeeping、Laurent pole 抽出、dimensional-regularization convention factor の適用が可能です。

### 6.5 counterterm / subdiagram

counterterm 定義、明示的 insertion / replacement、subdiagram relation、compatible forest、contracted graph、Taylor subtraction、BPHZ local counterterm を独立 layer として扱います。

有限な on-shell counterterm は pole だけから推測しません。物理的 renormalization condition は明示入力です。

### 6.6 IBP / Laporta 基盤

denominator-family representation、generic IBP equation、有限 sparse Laporta elimination、sector signature、symmetry canonicalization、exact-rational probe、rational reconstruction など、ordinary ladder の開発で使った基盤を備えています。

---

## 7. magnetic form factor

on-shell electromagnetic vertex を

$$
\Gamma_\mu^{\mathrm R}(p',p)
=
\gamma_\mu F_1(q^2)
+\frac{i\sigma_{\mu\nu}q^\nu}{2m}F_2(q^2)
$$

と分解すると、電子異常磁気能率は

$$
a_e=F_2(0)
$$

です。

QEDCalc には $F_1$ を除去して $F_2$ を抽出する検証済み projector 経路があります。ただし ordinary ladder の finite-$q$, $D$ 次元 projector など、図の計算経路によって具体的な projector 表現は異なります。

---

## 8. v0.90.0 で完了した2ループ7図

2ループ7図は次の5クラスに分かれます。

| クラス | 図数 | release checkpoint |
|---|---:|---|
| crossed ladder | 1 | Phase 78 |
| ordinary ladder | 1 | Phase 81 |
| corner | 2 | Phase 77 |
| self-energy insertion | 2 | Phase 80 |
| vacuum polarization | 1 | Phase 79 |
| 7図統合 audit | 合計7 | Phase 82 |
| 完成2ループ regression | 合計7 | Phase 83 |

### 8.1 crossed ladder

検証済み経路は

$$
\text{raw graph}
\longrightarrow
\text{magnetic projector}
\longrightarrow
\text{projective representation}
\longrightarrow
\text{one-variable kernel}
\longrightarrow
\text{endpoint assembly}
$$

です。

最終係数は

$$
A_{\mathrm X}
=
\frac16
+\frac{13\pi^2}{36}
+\frac54\zeta(3)
-\frac{5\pi^2}{6}\ln2
$$

です。

Karplus--Kroll の歴史的な $1/32$ 差の発生箇所は provenance 課題として未解決ですが、現代的な crossed-ladder 最終値の未確定を意味しません。

### 8.2 ordinary ladder

corrected physical spin-sum route は

$$
72\text{ projector terms}
\longrightarrow
40\text{ canonical IBP targets}
\longrightarrow
12\text{ analytic masters}
$$

まで閉じています。

bare result は

$$
A_{\mathrm L,bare}
=
-\frac{3}{4(D-4)}
+\frac{107}{48}
+\frac{\pi^2}{18}
+O(D-4)
$$

です。

on-shell subtraction 後は

$$
A_{\mathrm L}
=
\frac{11}{48}
+\frac{\pi^2}{18}
$$

です。

### 8.3 corner 2図

raw pair parse、magnetic projection、inner vertex UV subtraction、renormalized sector、soft/hard ownership、IR asymptotic まで接続されています。

$$
A_{\mathrm C}
=
\ln\frac1\rho
-\frac{67}{24}
+\frac{\pi^2}{18}
-\frac12\zeta(3)
+\frac{\pi^2}{3}\ln2
+o(1)
$$

です。

### 8.4 self-energy insertion 2図

左右の raw insertion diagram を、self-energy subdiagram detection、on-shell renormalization、outer reinsertion、finite integration、IR asymptotic まで監査します。

$$
A_{\mathrm S}
=
\ln\rho
+\frac{11}{24}
-\frac{\pi^2}{18}
+o(1)
$$

です。

したがって corner と self-energy の IR logarithm は

$$
\ln\frac1\rho+\ln\rho=0
$$

と exact に相殺します。

### 8.5 vacuum polarization

complete raw input、closed electron-loop trace detection、Dirac trace、tensor reduction、transversality、on-shell subtraction、outer magnetic insertion、endpoint evaluation まで接続されています。

$$
A_{\mathrm{VP}}
=
\frac{119}{36}
-\frac{\pi^2}{3}
$$

です。

---

## 9. 2ループ完成 regression

実行は

```text
run_v090_validation.bat
```

です。

標準ライブラリだけの Phase-83 regression では、次を確認します。

```text
Phase-83 complete two-loop regression PASS
diagram count = 7
IR log residual = 0
ordinary ladder reduction = 72 -> 40 -> 12
total basis coefficients = ('197/144', '1/12', '3/4', '-1/2', '0')
historical 1/32 origin resolved = False
QEDCalc 0.90.0
v0.90 validation PASS
```

基底は

$$
\left\{
1,
\pi^2,
\zeta(3),
\pi^2\ln2,
\ln\frac1\rho
\right\}
$$

です。

最後の 0 は IR logarithm の exact cancellation を表します。

固定 baseline は

```text
data/two_loop_v090_baseline.json
```

に保存されています。

---

## 10. v0.90.0 時点の自動化境界

QEDCalc は現時点では **高次 QED 摂動計算の半自動処理基盤** と表現するのが適切です。任意の Feynman 図を完全自動で解く solver ではありません。

### 自動または強く支援できる部分

- QED-LaTeX parse
- ordered algebraic representation
- 一部 topology / subdiagram detection
- Dirac algebra / trace
- magnetic projection
- Feynman parameter 化
- multi-loop square completion / shift
- tensor reduction
- 一部 UV / IR / counterterm audit
- IBP / Laporta infrastructure
- graph-specific analytic checkpoint
- 2ループ全体 release regression

### 人間の物理判断が必要な部分

- 元の Feynman 図から正しい非可換 Feynman-rule 式を作る、または監査すること
- 複数の routing がある場合の momentum routing 選択
- どの subgraph をどの physical condition で renormalize するかの判断
- 有効な variable transformation、sector split、endpoint strategy の選択
- graph-specific output を次の specialized stage へどう接続するかの判断
- 新規 topology に対する master-integral representation の選択

QEDCalc は、物理を推測してブラックボックス化するよりも、追跡可能な計算経路を優先します。

---

## 11. ドキュメント

- `README.md` — English Quick Start
- `README_JP.md` — 日本語 Quick Start
- `REFERENCE.md` — English current reference
- `REFERENCE_JP.md` — 日本語 current reference
- `ROADMAP.md` — 現行 development roadmap
- `CHANGELOG.md` — 現行 release history summary
- `doc/QEDCalc_2loop_5sample_manuals_v2/` — 2ループ5図群の計算過程説明書兼サンプルプログラム説明書
- `doc/QEDCalc_2loop_Milestone_Automation_Scope_and_Remaining_Manual_Work_EN.md` — 2ループ自動化到達点 English report
- `doc/QEDCalc_2loop_Milestone_Automation_Scope_and_Remaining_Manual_Work_JP.md` — 同日本語版
- `doc/archive/` — v0.90 documentation cleanup 前の累積履歴版

---

## 12. 現在の制限と次の方向

v0.90 では2ループ完成結果を baseline として固定しました。今後は3ループへ進む前後で、2ループで成功した machinery の一般化を進めます。

優先候補は次のとおりです。

1. topology から ordered amplitude への一般化
2. divergent subgraph 検出と renormalization plan の一般化
3. magnetic projector API の統一
4. parameter / sector strategy library の再利用化
5. master integral / IBP 自動化の拡張
6. v0.90 の2ループ regression を保護したまま3ループ対応へ進む

詳細は `ROADMAP.md` を参照してください。
