# QEDCalc v0.51.0 リファレンスマニュアル

## 1. 目的

QEDCalc は、ファインマン図から得た式をブラックボックスで一括処理するのではなく、QED 計算を小さな数学・物理操作へ分割して処理するためのツールです。

基本方針は次のとおりです。

- 人間が処理順序を決める。
- Dirac 代数、分母整理、Feynman parameter 化、運動量シフト、射影などを独立関数に分ける。
- 各段階の式を LaTeX / Markdown で検算できるようにする。
- 未定義記号や不完全な basis を勝手に推測しない。
- 1ループ専用処理から、2ループ・3ループ・4ループへ段階的に一般化する。

既定の1ループ頂点補正サンプルは、最終的に

$$
F_2(0)=\frac{\alpha}{2\pi}
$$

を得ます。

---

## 2. 動作環境とセットアップ

### 2.1 動作環境

- Windows 11
- Python 3.11 以上
- SymPy 1.13 以上

### 2.2 初回セットアップ

`setup_env.bat` を実行します。

処理内容：

1. `.venv` 作成
2. pip 更新
3. `requirements.txt` のライブラリ導入

QEDCalc 本体は展開フォルダから直接実行します。

### 2.3 実行バッチ

- `run_qedcalc.bat`：1ループ頂点補正サンプル
- `run_multiloop_demo.bat`：多ループ基盤デモ
- `run_tests.bat`：pytest

---

## 3. 主なディレクトリ

```text
qedcalc/
├─ input/
├─ output/
├─ examples/
├─ qedcalc/
│  ├─ config/
│  ├─ core/
│  ├─ history/
│  ├─ latex/
│  ├─ operations/
│  ├─ parser/
│  └─ validation/
├─ tests/
├─ symbols.txt
├─ setup_env.bat
├─ run_qedcalc.bat
├─ run_multiloop_demo.bat
└─ run_tests.bat
```

---

## 4. `symbols.txt`

QED-LaTeX 入力で使用する記号を事前定義します。

### `[Scalar]`

質量、結合定数、正則化パラメータなど。

### `[Constants]`

$i$, $\pi$ など。

### `[Vector]`

外部運動量・ループ運動量。

### `[Index]`

Lorentz 添字。

ギリシャ文字は LaTeX 表記を使用します。

例えば新しい添字 $\omega$ を使う場合は、

```text
[Index]
\omega
```

を追加します。

未定義記号は自動推測しません。

---


## 4A. `conventions.txt` — 計算規約

v0.26.0 でも、規約依存の設定を `conventions.txt` に集約します。計算途中の対話プロンプトはありません。

読み込み API：

```python
from qedcalc.config import load_conventions

conv = load_conventions()
```

`load_conventions()` は既定でプロジェクト直下の `conventions.txt` を読みます。任意パスも指定できます。

主な項目：

- `metric_signature`: `+---` または `-+++`
- `gauge`: `feynman` または `covariant`
- `renormalization_scheme`: `on_shell`, `MS`, `MSbar`, `BPHZ`
- `dimreg_dimension`: 既定 `4 - 2*epsilon`
- `dimreg_subtraction`: `MS`, `MSbar`, `none`
- `msbar_factor`: $S_\epsilon=(4\pi e^{-\gamma_E})^\epsilon$ を使用するか
- `subdiagram_include_coupling`
- `subdiagram_include_loop_measure`
- `subdiagram_include_i`
- `coupling_symbol`
- `loop_measure_denominator_latex`
- `loop_i_factor_latex`

規約オブジェクトは `QEDConventions` です。

```python
conv.compact_outer_one_loop_prefactor_latex()
```

は、2ループ図から1ループ subdiagram を縮約した後に残る outer normalization を、`subdiagram_include_*` の所有規則から構成します。既定値では、

$$
\frac{e^2}{(2\pi)^4 i}
$$

です。

`contract_self_energy_to_outer_loop()` は、`outer_prefactor_latex` を省略すると `conventions.txt` を読み、上記 prefactor を自動使用します。明示的な `outer_prefactor_latex=...` は互換性と特殊規約用の override として残しています。

```python
contract_self_energy_to_outer_loop(
    diagram,
    conventions=conv,
    renormalized=True,
)
```

self-energy raw bridge は現在 `gauge=feynman` の完全自動 numerator reduction に対応します。`gauge=covariant` を指定した場合、longitudinal contribution を勝手に捨てず `NotImplementedError` で停止します。

`dimreg_scale_factor()` と `renormalized_dimreg_series()` も `conventions=conv` を受け取り、`dimreg_subtraction` と `msbar_factor` を参照できます。

設定の確認用に、

```text
run_conventions_demo.bat
```

を用意しています。出力は `output/conventions.md` です。

---

## 5. QED-LaTeX parser

主要 API：

```python
from qedcalc import parse_latex

expr = parse_latex(source)
```

現在の主要対応構文：

- `\gamma^\mu`, `\gamma_\mu`
- `\rlap{/}p`
- `g_{\mu
u}`
- `\frac{A}{B}`
- $p^2$
- $p\cdot k$
- 括弧、加減算、積

Dirac 行列を含む積は `NCProduct` として順序を保存します。

一般 LaTeX 全体を解釈する parser ではありません。

---

## 6. 主要内部表現

`qedcalc/core/expression.py` に定義されています。

| クラス | 用途 |
|---|---|
| `Symbol` | スカラー・定数 |
| `Vector` | 4元運動量 |
| `Index` | Lorentz 添字 |
| `Gamma` | gamma 行列 |
| `Slash` | Feynman slash |
| `Metric` | metric tensor |
| `ScalarProduct` | Lorentz スカラー積 |
| `VectorComponent` | ベクトル成分 |
| `Product` | 可換積 |
| `NCProduct` | 非可換積 |
| `Fraction` | 分数 |
| `FeynmanParamIntegral` | unit-power Feynman parameter 積分 |
| `GeneralFeynmanParamIntegral` | 一般分母指数 Feynman parameter 積分 |
| `CompletedSquare` | 1ループ平方完成 |
| `MultiLoopCompletedSquare` | 多ループ行列平方完成 |
| `SpinorSandwich` | 外部 spinor に挟まれた演算子 |
| `FormFactorDecomposition` | $F_1,F_2$ 分解 |
| `PoleTerm` | UV/IR pole |
| `LaurentResult` | pole と有限部の分離結果 |
| `Counterterm` | counterterm 定義 |
| `CountertermInsertion` | counterterm 挿入・置換結果 |

---

## 7. LaTeX renderer

```python
from qedcalc import render_latex

latex = render_latex(expr)
```

内部表現を検算用 LaTeX へ戻します。


### 7.1 内部識別子と LaTeX 表示名

内部処理では ASCII の識別子を使う場合がありますが、`render_latex()` は数式表示時に QED の標準的な LaTeX 記法へ変換します。

| 内部識別子 | LaTeX 出力 |
|---|---|
| `deltaZ1` | `\delta Z_{1}` |
| `deltaZ2` | `\delta Z_{2}` |
| `deltaZ3` | `\delta Z_{3}` |
| `delta_m` | `\delta m` |
| `zeta` | `\zeta` |
| `eta` | `\eta` |
| `omega` | `\omega` |
| `epsilon_UV` | `\epsilon_{\mathrm{UV}}` |
| `epsilon_IR` | `\epsilon_{\mathrm{IR}}` |

したがって、counterterm の表示は例えば

$$
\delta Z_1\gamma_\mu
$$

となり、内部名 `deltaZ1` がそのまま数式へ露出することはありません。

負号を持つ積因子は、引き算と誤認しないよう括弧付きで表示します。

---

## 8. 1ループ処理機能

### 8.1 propagator 処理

`qedcalc.operations.propagator`

フェルミオン propagator を Dirac 分子とスカラー分母へ変換します。

### 8.2 numerator / denominator 分離

被積分式を Dirac 分子とスカラー分母へ分離します。

### 8.3 Dirac / Lorentz 代数

主な処理：

- slash 展開
- gamma 縮約
- metric 縮約
- 外部 Dirac 方程式
- Gordon reduction

### 8.4 1ループ平方完成

`complete_square()` は現在の1ループ分母規約で

$$
-k^2+2A\cdot k+C
$$

を平方完成します。

### 8.5 対称積分

`drop_odd_loop_terms()`：奇数次ループ運動量項を除去。

`symmetric_rank2()`：rank-2 の4次元対称積分規則。

`symmetric_rank4()`：一般次元 $D$ に対して

$$
l^\mu l^
u l^\rho l^\sigma
\longrightarrow
\frac{l^4}{D(D+2)}
\left(
g^{\mu
u}g^{\rho\sigma}
+g^{\mu\rho}g^{
u\sigma}
+g^{\mu\sigma}g^{
u\rho}
\right)
$$

を適用します。

---

## 9. 多ループ運動量

### 9.1 `declare_loop_momenta()`

```python
loops = declare_loop_momenta(symbols, ("k", "l"))
```

`symbols.txt` の `[Vector]` と照合してループ運動量を宣言します。

### 9.2 `complete_multiloop_square()`

多ループ二次形式を

$$
K^T M K+2K\cdot B+C
$$

として解釈し、

$$
\left(K+M^{-1}B\right)^T
M
\left(K+M^{-1}B\right)
+C-B^TM^{-1}B
$$

へ平方完成します。

```python
completed = complete_multiloop_square(expr, ("k", "l"))
```

行列 $M$ が特異な場合はエラーになります。

### 9.3 `shifted_multiloop_denominator()`

平方完成後の新ループ運動量へ変換した分母を生成します。

### 9.4 `shift_multiloop_momenta_in_numerator()`

v0.11.0 追加。

多ループ平方完成で得た全シフトを、分子へ**同時に**適用します。

```python
shifted_num = shift_multiloop_momenta_in_numerator(
    numerator,
    completed,
    ("ell1", "ell2"),
)
```

対応対象：

- `Slash(k)`
- `VectorComponent(k, ...)`
- `ScalarProduct(k,l)`
- `Add`, `Product`, `NCProduct`, `Fraction`, `Power`

逐次置換ではなく同時置換するため、$k\cdot l$ のような混合構造を壊しません。

---

## 10. Feynman parameter 化

### 10.1 `feynman_parameterize()`

3分母・unit power の1ループ用関数。

### 10.2 `feynman_parameterize_n()`

$N$ 個の unit-power 分母に対して

$$
\frac{1}{D_1\cdots D_N}
=
(N-1)!
\int_{\Delta_{N-1}}
\frac{d^{N-1}x}
{\left(\sum_i x_iD_i\right)^N}
$$

を構成します。

### 10.3 `feynman_parameterize_powers()`

v0.11.0 追加。

正整数 $a_i$ に対し、

$$
\frac{1}{D_1^{a_1}\cdots D_N^{a_N}}
=
\frac{\Gamma(A)}{\prod_i\Gamma(a_i)}
\int_{\Delta_{N-1}}
\frac{
\prod_i x_i^{a_i-1}
}{
\left(\sum_i x_iD_i\right)^A
}
d^{N-1}x,
\qquad
A=\sum_i a_i
$$

を構成します。

例：

```python
expr = Fraction(
    Symbol("N"),
    Product(Power(Symbol("D1"),2), Symbol("D2"), Power(Symbol("D3"),3))
)
fp = feynman_parameterize_powers(expr)
```

現在、指数は正整数に限定しています。

---

## 11. 一般 $D$ 次元標準ループ積分

### 11.1 `euclidean_scalar_loop_integral()`

v0.11.0 追加。

$$
\int d^Dl\,
\frac{(l^2)^r}{(l^2+\Delta)^n}
$$

に対して

$$
\pi^{D/2}
\Delta^{D/2+r-n}
\frac{
\Gamma(r+D/2)\Gamma(n-r-D/2)
}{
\Gamma(D/2)\Gamma(n)
}
$$

を SymPy 式として返します。

```python
result = euclidean_scalar_loop_integral(
    denominator_power=3,
    numerator_power=1,
    dimension=D,
    delta=Delta,
)
```

**重要：** この関数は Euclidean 標準積分だけを扱います。Wick rotation による $i$、符号、$(2\pi)^{-D}$、$\mu^{2\epsilon}$、MS-bar 因子などは自動で挿入しません。

### 11.2 `dimensional_regularized_loop_series()`

$$
D=4-2\epsilon
$$

を代入し、$\epsilon$ の Laurent 展開を SymPy series として返します。

```python
series = dimensional_regularized_loop_series(2, 0, epsilon, Delta, order=0)
```

この関数も renormalization scheme の因子は自動挿入しません。

---

## 12. UV / IR pole

`extract_laurent_poles()` は、スカラー式から指定 regulator の負べき項と有限部を分離します。

```python
uv = extract_laurent_poles(expr, "epsilon_UV", "UV", 2)
```

UV と IR を区別したい場合は `epsilon_UV`, `epsilon_IR` のように別記号を使用します。

---

## 13. counterterm

### 13.1 `make_counterterm()`

```python
ct = make_counterterm(
    "delta_Z1",
    Symbol("deltaZ1"),
    Gamma(mu),
    loop_order=1,
)
```

counterterm の名称、係数、構造、loop order を保持します。

### 13.2 `counterterm_contribution()`

counterterm を代数的寄与へ変換します。

### 13.3 `add_counterterms()`

元の式へ明示的に counterterm 寄与を加えます。

### 13.4 `replace_factor_with_counterterm()`

v0.11.0 追加。

トップレベル `Product` / `NCProduct` の指定因子を counterterm 構造へ置換します。

```python
insertion = replace_factor_with_counterterm(chain, 1, ct)
result = insertion.result
```

QEDCalc は、どの頂点や propagator に counterterm を入れるべきかを自動推測しません。因子位置は呼び出し側が明示します。

### 13.5 `insert_counterterm_factor()`

指定因子の前または後へ counterterm 寄与を挿入します。

これは一般的な代数操作です。実際の QED counterterm 図で「置換」と「挿入」のどちらが物理的に正しいかは、対象図と規約に応じて呼び出し側が選択します。

---

## 14. $F_2(0)$ の1ループ処理

既定の1ループサンプルでは、current を $\gamma_\mu$, $p_\mu$, $q_\mu$ 構造へ整理し、Gordon pair から magnetic form factor を抽出します。

途中で

$$
F_{2,\mathrm{num}}
=
4m^2(x+y)(1-x-y)
$$

および

$$
\Delta
=
m^2(x+y)^2
$$

が得られます。

残る parameter 積分は

$$
\int_0^1dx
\int_0^{1-x}dy\,
\frac{4(1-x-y)}{x+y}
=
2
$$

となり、最終的に

$$
F_2(0)
=
\frac{\alpha}{2\pi}
$$

となります。

---

## 15. Markdown 履歴

`MarkdownSession` は各処理段階を `.md` へ保存します。

表示数式は必ず

```markdown
Text

$$
formula
$$

Text
```

となるため、数式対応 Markdown viewer で直接確認できます。

---

## 16. v0.12.0 追加機能

### 16.1 一般偶数 rank tensor reduction

`qedcalc.operations.loop.symmetric_even_rank()` は、1本のループ運動量に対する任意の偶数 rank $2n$ の等方的 tensor reduction を行います。

基本公式は、

$$
l^{\mu_1}\cdots l^{\mu_{2n}}
\longrightarrow
\frac{(l^2)^n}
{D(D+2)\cdots(D+2n-2)}
\sum_{\mathrm{pairings}}
g^{\mu_i\mu_j}\cdots
$$

です。

rank 6 では全15通りの完全 pairings を自動生成します。$D=4$ の係数は、

$$
\frac{1}{4\cdot6\cdot8}
=
\frac{1}{192}
$$

です。

使用例：

```python
out = symmetric_even_rank(expr, loop="l", dimension=4)
```

`dimension` には `4` のような整数だけでなく、SymPy の $D$ や $4-2\epsilon$ も指定できます。

### 16.2 dimensional-regularization 規約層

`qedcalc.operations.renormalization` を追加しました。

QEDCalc の MS-bar 規約では、1ループあたり、

$$
S_\epsilon
=
\left(
4\pi e^{-\gamma_E}
\right)^\epsilon
$$

を用います。$L$ ループでは、

$$
\mu^{2L\epsilon}S_\epsilon^L
$$

を scale factor とします。

主な API：

```python
dimreg_scale_factor(loop_order, epsilon, mu, scheme="MSbar")
apply_dimreg_convention(expr, loop_order, epsilon, mu, scheme="MSbar")
pole_part(expr, epsilon)
minimal_subtract(expr, epsilon)
renormalized_dimreg_series(...)
```

`scheme="MS"` の場合は、

$$
\mu^{2L\epsilon}
$$

のみを用います。

`renormalized_dimreg_series()` は、規約因子、Laurent 展開、pole part、minimal subtraction 後の式を別々に返します。規約操作をブラックボックス化しないための設計です。

### 16.3 UV / IR bookkeeping

`bookkeep_uv_ir()` は独立な regulator、

$$
\epsilon_{\mathrm{UV}},
\qquad
\epsilon_{\mathrm{IR}}
$$

を用いて、各項を次に分類します。

- UV pole のみ
- IR pole のみ
- UV/IR mixed pole
- finite part
- regulator の正冪を含む regular remainder

例えば、

$$
\frac{A}{\epsilon_{\mathrm{UV}}^2}
+
\frac{B}{\epsilon_{\mathrm{IR}}}
+
\frac{C}{\epsilon_{\mathrm{UV}}\epsilon_{\mathrm{IR}}}
+
F
$$

を、それぞれ独立に保持します。

### 16.4 QED counterterm library

次の標準 counterterm builder を追加しました。

```python
qed_vertex_counterterm(...)
qed_electron_wavefunction_counterterm(...)
qed_mass_counterterm(...)
qed_photon_wavefunction_counterterm(...)
qed_counterterm_library(...)
```

構造はそれぞれ概念的に、

$$
\delta Z_1\gamma_\mu
$$

$$
\delta Z_2\rlap{/}p
$$

$$
\delta m
$$

および、

$$
\delta Z_3
\left(
k^2g_{\mu
u}-k_\mu k_
u
\right)
$$

です。

係数の値そのものは renormalization scheme や loop order に依存するため、QEDCalc は勝手に決定しません。構造と挿入操作を分離して保持します。

---

## 17. v0.13.x の subdiagram / counterterm 管理

v0.13.x では、裸の代数式だけから divergent subgraph を推測するのではなく、図の topology 情報を明示的に保持する方式を採用しています。

主な API：

```python
Subdiagram(...)
relation(...)
forest_compatible(...)
enumerate_forests(...)
CountertermAssignment(...)
assemble_renormalized_amplitude(...)
renormalization_plan(...)
minimal_r_operation(...)
```

`Subdiagram` には subgraph 名、種類、loop order、構成要素、UV/IR 分類などを登録します。これにより nested / disjoint / overlapping の関係を判定し、forest-compatible な組を列挙できます。

MS / MS-bar 系では、評価済み subdiagram の pole 部分から

$$
C(\gamma)
=
-\operatorname{Pole}[\gamma]
$$

として counterterm pole を生成し、subdivergence subtraction 後の overall pole subtraction まで段階的に管理できます。

一方、on-shell scheme の有限 counterterm は renormalization condition に依存するため、pole 部分だけから自動決定しません。

---

## 18. 現在の制限

v0.16.0 は、1ループ頂点補正を最後まで処理でき、多ループ計算用の topology・renormalization・tensor 基盤も持っています。ただし「任意の2ループ図を完全自動評価する」段階ではありません。

主な未実装・制限：

- branching graph や非連続 block contraction を表現する richer topology template
- Minkowski 積分の $i$、Wick rotation、$(2\pi)^{-D}$ を含む完全な規約管理
- 任意複素指数の Feynman parameter 化
- IBP reduction
- master integral database / interface
- sector decomposition
- 一般2ループ diagram の end-to-end 自動処理

設計方針として、これらも大きな一括関数ではなく、小さな検証可能な処理関数として追加します。

---

## 19. テスト

v0.19.0：100 tests passed。

`run_tests.bat` で実行できます。

---

## 20. contracted graph / Taylor subtraction / forest formula

主な API：

```python
ContractedGraph
TaylorSubtractionSpec
contract_graph(...)
taylor_operator(...)
apply_taylor_spec(...)
bphz_local_counterterm(...)
bphz_subtract(...)
forest_formula(...)
```

### 20.1 Contracted graph

`contract_graph()` は宣言済み subdiagram を局所 topology vertex `CT[...]` へ縮約し、$G/F$ の topology を保持します。nested forest は内側から外側へ縮約します。

この機能は topology bookkeeping であり、bare algebraic expression だけから縮約後の QED amplitude を推測しません。

### 20.2 Taylor subtraction operator

`taylor_operator()` は明示した可換変数について全次数 $\leq\omega$ の多変数 Taylor 多項式を返します。

$$
t^{\omega}f(p) = \sum_{|a|\leq\omega}\frac{(p-p_0)^a}{a!}\left.\partial^a f\right|_{p=p_0}
$$

`TaylorSubtractionSpec` は subdiagram、外部変数、subtraction degree、展開点を保持します。

### 20.3 BPHZ local counterterm

`bphz_local_counterterm()` は

$$
C_{\mathrm{BPHZ}}(\gamma) = -t_{\gamma}^{\omega(\gamma)}\Gamma_{\gamma}
$$

を返します。

`bphz_subtract()` は

$$
\left(1-t_{\gamma}^{\omega}\right)\Gamma_{\gamma}
$$

を返します。MS / $\overline{\mathrm{MS}}$ pole subtraction とは別機能です。

### 20.4 Zimmermann forest sum

`forest_formula()` は compatible forest を列挙し、各 forest の contracted topology を生成し、$(-1)^{|F|}$ の符号を付けて和を構成します。

各 contracted graph に対応する algebraic amplitude は `amplitude_provider` で明示します。これにより、失われた topology を bare 式から逆推定して誤った amplitude を生成することを防ぎます。

---

## 21. topology から amplitude を構築する層

### 21.1 `TopologyFactor`

1個の topology identifier と、それに割り当てる QED 式を対応付けます。

```python
TopologyFactor(factor_id, expression, commutative=False)
```

`commutative=False` の factor は順序を保持した非可換積へ入ります。光子分母など、明示的に可換と判断できる factor だけ `commutative=True` にします。

### 21.2 `QEDAmplitudeTemplate`

Feynman 図に対応する factor の**明示的な順序**を保持します。

```python
QEDAmplitudeTemplate(graph_name, factors)
```

QEDCalc は bare の代数式から失われた topology 順序を逆推定しません。

### 21.3 `build_bare_amplitude()`

明示された factor 順序から bare amplitude を組み立てます。

### 21.4 `build_contracted_amplitude()`

`ContractedGraph` と各 subdiagram に対応する局所 vertex を受け取り、$G/F$ の代数振幅を構成します。

安全性のため、現在は ordered template 上で subdiagram が連続 block として表現できる場合だけ自動置換します。非連続な factor 集合を勝手に並べ替えることはせず、エラーにします。

これは fermion line 上の vertex / self-energy subdiagram のように順序が明確な場合に適しています。branching topology や非連続 contraction は、将来 richer graph template で扱います。

---

## 22. 複数ループ運動量を含む tensor reduction

### 22.1 `symmetric_multiloop_tensor()`

平方完成後の loop dependence が

$$
Q = L^TML
$$

だけになっている場合、異なる loop momentum の component を含む偶数 rank tensor を $M^{-1}$ を用いて縮約します。

$n$ 個の loop momentum、Lorentz 次元 $D$ に対して、積分変数全体の次元を

$$
N = nD
$$

とします。rank $2r$ では、

$$
L_{i_1}^{\mu_1}\cdots L_{i_{2r}}^{\mu_{2r}} \longrightarrow \frac{Q^r}{N(N+2)\cdots(N+2r-2)}\sum_{\mathrm{pairings}}\prod\left[(M^{-1})_{ij}g^{\mu
u}\right]
$$

を使います。

例えば rank 2 なら、

$$
L_i^\mu L_j^
u \longrightarrow \frac{Q}{nD}(M^{-1})_{ij}g^{\mu
u}
$$

です。

この関数は**平方完成後、integrand が loop momentum に関して $Q$ のみへ依存する段階で使用する**必要があります。一般の非等方的な numerator へ無条件に適用してはいけません。

---

## 23. v0.16.0 の自動化境界

現在、自動化できる範囲：

- 明示 factor template から bare amplitude を構成
- declared subdiagram の contracted topology を構成
- 対応する local vertex が与えられた contracted amplitude を構成
- 多ループ平方完成
- 複数 loop momentum の混合 tensor reduction
- forest / Taylor subtraction / counterterm bookkeeping

まだ自動推測しないもの：

- bare algebraic expression だけから Feynman graph topology を復元する処理
- 非連続 topology block の自動再配線
- branching graph を含む任意 contracted graph の完全自動 Feynman-rule 生成

この境界は、誤った diagram topology を静かに生成しないための意図的な制限です。


---

## 2ループ vacuum polarization 実戦試験

v0.16.0 では、これまで解析した2ループ資料のうち vacuum polarization 図を最初の実戦対象として採用した。

理由は、この図が

$$
\text{closed electron loop}
\longrightarrow
\Pi_R(k^2)
\longrightarrow
\text{one-loop magnetic vertex kernel}
$$

と subdiagram 単位に分離しやすく、QEDCalc の既存機能を連結して検証できるためである。

入力ファイルは `input/vacuum_polarization_subloop.tex` であり、閉じた電子ループの numerator

$$
\left(m+\rlap{/}l+\rlap{/}k\right)
\gamma^\alpha
\left(m+\rlap{/}l\right)
\gamma^\beta
$$

を QED-LaTeX として読み込む。

### `dirac_trace_4d(expr)`

4次元 Dirac trace を評価する。現在は trace 内の Gamma/Slash 個数が 0, 2, 4 の場合に対応し、奇数個の trace は0とする。4個の場合は

$$
\operatorname{tr}(\gamma^\mu\gamma^
u\gamma^\rho\gamma^\sigma)
=
4\left(
 g^{\mu
u}g^{\rho\sigma}
-g^{\mu\rho}g^{
u\sigma}
+g^{\mu\sigma}g^{
u\rho}
\right)
$$

を使用する。

この機能により vacuum polarization subloop の numerator は資料の

$$
N^{\alpha\beta}
=
4\left[
(l+k)^\alpha l^\beta
+(l+k)^\beta l^\alpha
-g^{\alpha\beta}(l+k)\cdot l
+m^2g^{\alpha\beta}
\right]
$$

に対応する tensor 構造へ展開される。

その後、既存の loop shift、odd-term removal、rank-2 symmetric reduction を適用する。

### vacuum polarization scalar kernel

`qedcalc.operations.vacuum_polarization` に次を追加した。

- `vp_hat_renormalized_integrand(k2, m, z)`
- `vp_gminus2_double_integrand(x, z)`
- `vp_z_integrated_kernel(x)`
- `vp_numeric_coefficient(dps=50)`
- `vp_recognize_analytic(value)`

on-shell subtraction 後の dimensionless scalar vacuum polarization は

$$
\widehat\Pi_R(k^2)
=
2\int_0^1 dz\,z(1-z)
\ln\left[
\frac{m^2}{m^2-k^2z(1-z)}
\right]
$$

である。

外側の magnetic kernel と結合した係数は

$$
A_{\mathrm{VP}}
=
2\int_0^1dx\,(1-x)
\int_0^1dz\,z(1-z)
\ln\left[
1+\frac{x^2}{1-x}z(1-z)
\right]
$$

として評価する。

v0.16.0 の数値評価は

$$
A_{\mathrm{VP}}
=
0.0156874218591026826107252222635\ldots
$$

となり、`nsimplify` に {1, $\pi^2$} basis を与える独立な解析認識により

$$
\boxed{
A_{\mathrm{VP}}
=
\frac{119}{36}
-
\frac{\pi^2}{3}
}
$$

を得る。

### 現在の自動化境界

v0.16.0 では、元の2ループ式全体に含まれる `\\int`, `\\operatorname{tr}`, gauge-propagator brace 構造を一つの LaTeX expression として完全 parse するところまでは実装していない。

そのため現在は、Feynman topology を明示し、閉じた electron loop を subdiagram として切り出した後、その numerator を LaTeX 入力として処理する。

この制限は計算結果を埋め込むためのものではなく、式だけから失われた topology を推測しないという QEDCalc の安全方針による。将来は diagram-level input schema を追加して、bare two-loop expression と subdiagram metadata を同時に入力できるようにする。


## 25. v0.18.0 self-energy insertion 2ループ実戦試験

### 25.1 目的

左右の electron self-energy insertion 2図を、1ループ self-energy subdiagram と outer magnetic vertex に分離して処理する。

### 25.2 追加 API

`qedcalc.operations.self_energy` に以下を追加した。

- `self_energy_delta(a, r2, m, photon_mass)`
- `self_energy_delta0(a, m, photon_mass)`
- `onshell_counterterms_from_ab(A, B, r2, m)`
- `uv_cancellation_numerator(a, m, rslash)`
- `log_ratio_parameter_kernel(a, z, r2, m, photon_mass)`
- `log_ratio_prefactor(a, r2, m)`
- `finite_four_parameter_integrand(a, z, b, q)`
- `finite_b_integrated_kernel(a, z, q)`
- `finite_one_variable_kernel(x)`
- `finite_part_numeric()`
- `finite_part_recognize()`
- `ir_part_asymptotic(rho)`
- `total_self_energy_coefficient(rho)`

### 25.3 numerator checkpoint

Feynman-gauge self-energy numerator を

$$
\gamma^\alpha
\left(
m+\rlap{/}r-\rlap{/}l
\right)
\gamma_\alpha
$$

とすると、4次元 Dirac algebra により

$$
4m-2\rlap{/}r+2\rlap{/}l
$$

となる。$l=t+ar$ と shift し、odd $t$ term を除くと

$$
4m-2(1-a)\rlap{/}r
$$

を得る。

### 25.4 on-shell counterterm

$$
\Sigma(r)=mA(r^2)+\rlap{/}r B(r^2)
$$

に対し、

$$
\delta m
=
m\left[A(m^2)+B(m^2)\right]
$$

$$
\delta Z_2
=
B(m^2)+2m^2\left[A'(m^2)+B'(m^2)\right]
$$

を `onshell_counterterms_from_ab()` で生成できる。

### 25.5 UV cancellation checkpoint

renormalized self-energy の UV numerator は

$$
N_{\mathrm{UV}}
=
4m-2(1-a)\rlap{/}r-2m(1+a)+2(\rlap{/}r-m)(1-a)
$$

で、QEDCalc は

$$
N_{\mathrm{UV}}=0
$$

を確認する。

### 25.6 finite / IR checkpoints

有限部分は

$$
A_A(0)
=
-\frac1{24}-\frac{\pi^2}{18}
$$

IR 部分は

$$
A_B(\rho)
=
\ln\rho+\frac12+o(1)
$$

であり、合計は

$$
A_{\mathrm S}
=
-\frac12\ln\rho^{-2}+\frac{11}{24}-\frac{\pi^2}{18}
$$

となる。

### 25.7 自動化境界

元の左右2本の2ループ aligned LaTeX 全体を一発で parse して subdiagram を自動発見する機能はまだない。現版では self-energy subdiagram を明示し、その後の代数、on-shell subtraction、UV check、有限積分 cross-check を自動化する。
---

## 26. 2ループ ordinary ladder 実戦試験

### 26.1 到達結果

ordinary ladder の renormalized 寄与について、

$$
F_{2,\mathrm L}^{(4)}(0)
=
\left(\frac{\alpha}{\pi}\right)^2
\left[
\frac{11}{48}
+\frac{\pi^2}{18}
\right]
$$

を checkpoint として再現する。

### 26.2 `ladder_projector_coefficients()`

$D$ 次元 Pauli projector の係数

$$
a
=
\frac{2}{z(D-2)(z-4)}
$$

$$
b
=
\frac{Dz-2z+4}{z(D-2)(z-4)^2}
$$

を返す。

### 26.3 $D$ 次元 outer-gamma identity

`contract_outer_gamma_ddim_one()` は

$$
\gamma^\rho\gamma^\alpha\gamma_\rho
=
(2-D)\gamma^\alpha
$$

を、`contract_outer_gamma_ddim_two()` は

$$
\gamma^\rho\gamma^\alpha\gamma^\beta\gamma_\rho
=
4g^{\alpha\beta}
+(D-4)\gamma^\alpha\gamma^\beta
$$

を適用する。後者の $(D-4)$ 項は UV pole と掛かって有限寄与を生むため、4次元へ早期に固定しない。

### 26.4 scalar-product denominator basis

`ladder_scalar_product_rules()` は

$$
k^2=-K
$$

$$
l^2=-L
$$

$$
k\cdot l=\frac{K+L-H}{2}
$$

$$
p'\cdot k=\frac{E_1-K}{2}
$$

$$
p\cdot k=\frac{E_4-K}{2}
$$

$$
p'\cdot l=\frac{E_2-H-E_1+K}{2}
$$

$$
p\cdot l=\frac{E_3-H-E_4+K}{2}
$$

を返す。

### 26.5 integral family と75係数表

`LadderIntegralIndex` は

$$
J(n_K,n_L,n_H,n_1,n_2,n_3,n_4)
$$

の指数を保持する。負指数は numerator power を表す。

`load_ladder_coefficient_table()` は `data/ladder_Ddim_75_coefficients.csv` を読み込み、重複 index を拒否する。現在の配布表は75 monomial を含み、代表係数を回帰テストで検証している。

v0.26.0 では、historical projector-first trace 順序に対応する75係数監査表を raw bare ladder から完全再生成できる。なお、この75表は後に監査・修正された physical spin-sum trace 順序とは明示的に区別する。一般 IBP/Laporta reduction は引き続き未実装である。

### 26.6 subtraction

`one_loop_f2_dimensional()` は

$$
F_2^{(1l)}(D,0)
=
\frac{5-D}{2(D-3)}
$$

を返す。

`one_loop_z1_dimensional()` は

$$
Z_1^{(1l)}
=
-\frac12\frac{D-1}{(D-3)(D-4)}
$$

を返す。$\delta=D-4$ とすれば、積は

$$
F_{2,\mathrm{sub}}^{(2)}(0)
=
-\frac{3}{4\delta}
+2
+O(\delta)
$$

となる。

bare checkpoint

$$
F_{2,\mathrm L}^{\mathrm{bare}}
=
-\frac{3}{4\delta}
+\frac{107}{48}
+\frac{\pi^2}{18}
+O(\delta)
$$

との差を取ると pole が相殺し、

$$
F_{2,\mathrm L}^{\mathrm R}(0)
=
\frac{11}{48}
+\frac{\pi^2}{18}
$$

を得る。

### 26.7 実行

`run_ladder_2loop_demo.bat` を実行する。出力は `output/ladder_2loop_trial.md`。

## 27. v0.19.0 crossed ladder 2ループ実戦試験

### 27.1 自動化の範囲

この試験では、独立導出資料にある projective parameter / 1変数 reduction を入力 checkpoint として使用する。元の crossed-ladder Feynman 式から数百項の raw Dirac 展開を経て5変数 integrand $G_{\mathrm X}$ を生成する部分は、まだ完全自動化していない。

### 27.2 projective forms

`crossed_projective_forms()` は

$$
\Delta
=
RS+RV+SU+UV-1
$$

$$
W
=
R^2S+R^2V+RS^2-2RS+S^2U
$$

を返す。両者が $V$ に一次であることを検証できる。

### 27.3 $h,t,q$ 変換

`crossed_h_log_argument()` と `crossed_tq_transform()` は

$$
h=S(R+U)-1
$$

$$
t=\frac1{h+1},
\qquad
q=\frac{R}{h+1}
$$

および Jacobian

$$
\left|\frac{\partial(h,R)}{\partial(t,q)}\right|
=
\frac1{t^3}
$$

を扱う。`crossed_tq_log_argument()` は

$$
\frac{q^2+(1-2q)t}{q^2(1-t)}
$$

を返す。

### 27.4 canonical dilogarithm kernel

`crossed_canonical_kernel()` は

$$
L=\ln q,
\qquad
M=\ln(1-q),
\qquad
D(q)=\operatorname{Li}_2(q)-\operatorname{Li}_2\left(2-\frac1q\right)
$$

を用いた canonical one-variable kernel を返す。

### 27.5 $q=1/2$ sector

`crossed_half_sector_result()` は標準積分

$$
\int_0^1\frac{\ln^2x}{x^2-1}dx
=
-\frac74\zeta(3)
$$

$$
\int_0^1\frac{\ln x}{x^2-1}dx
=
\frac{\pi^2}{8}
$$

$$
\int_0^1\frac{\ln x\ln(1+x)}{x^2-1}dx
=
-\frac7{16}\zeta(3)+\frac{\pi^2}{8}\ln2
$$

を合成し、

$$
I_{1/2}
=
\pi^2-\frac{5\pi^2}{6}\ln2-\frac{35}{12}\zeta(3)
$$

を返す。

### 27.6 endpoint-safe integration

`crossed_dilog_reflection_sum()` は

$$
D(q)+D(1-q)
=
\frac{\pi^2}{6}+\frac12L^2+\frac12M^2-2LM
$$

を使い、endpoint sector の dilogarithm を消去する。`crossed_endpoint_combined_kernel()` は、$1/q$ と $1/(q-1)$ sector を分離したまま積分せず、$q\to1-q$ 後に合成した integrand を返す。

`crossed_endpoint_asymptotics()` は cutoff logarithm $\ell=\ln\varepsilon$ の cubic / quadratic / linear divergence と全微分境界項が相殺することを検証する。発散和は

$$
0
$$

となり、有限境界項は

$$
I_{\mathrm{boundary}}
=
\frac16-\frac{\pi^2}{9}
$$

である。

### 27.7 最終結果

`crossed_final_result()` は

$$
I_{\mathrm X}
=
\frac16+\frac{13\pi^2}{36}+\frac54\zeta(3)-\frac{5\pi^2}{6}\ln2
$$

を返す。したがって

$$
F_{2,\mathrm X}^{(4)}(0)
=
\left(\frac{\alpha}{\pi}\right)^2 I_{\mathrm X}
$$

となる。

### 27.8 実行

`run_crossed_ladder_2loop_demo.bat` を実行する。出力は `output/crossed_ladder_2loop_trial.md`。



## 28. v0.21.0 corner (IIc) 2ループ試験

### 28.1 適用範囲

`qedcalc.operations.corner` は、corner (IIc) の独立導出で得られた UV-finite parameter representation 以降を再検証する。元の6-denominator 2ループ LaTeX 式から projector 後の有限 kernel を完全自動生成する機能はまだ未実装である。

### 28.2 soft kernel と IR logarithm

`corner_soft_kernel()` は

$$
\mathcal S
=
\frac{2RSUv(4R+S+4v)}{(R+v)^2(1+U^2)(R+S+v)^4}
$$

を返す。`corner_soft_spatial_kernel()` は普遍因子 $U/(1+U^2)$ を除いた $R,S,v$ kernel を返す。

`corner_soft_integrate_S()` は

$$
\int_0^\infty dS\,G(R,S,v)
=
\frac{2Rv}{(R+v)^3}
$$

を返し、さらに $R$ 積分は1になる。したがって `corner_soft_ir_coefficient()` は exact に1を返す。

### 28.3 momentum shift

`corner_shifted_p_minus_k()` は共通 loop shift による

$$
p'-k
\longrightarrow
(1-uv)p'-u(1-v)p''-k
$$

の各係数を返す。特に $p''$ の係数 $-u(1-v)$ を明示的に保持し、旧shiftとの混同を防ぐ。

### 28.4 diagnostic soft/hard split

`corner_soft_finite_constant()` は

$$
C_{\mathrm{soft}}
=
\frac{\pi^2}{6}+\ln^22-3\ln2-\frac74
$$

を返す。`corner_hard_remainder_from_soft_split()` と合わせると $A_{\mathrm C,fin}$ を再現する。ただしこの分解は診断用であり、sector bookkeeping の最終和に $C_{\mathrm{soft}}$ を別加算してはならない。

### 28.5 hard sector と z sector

`corner_hard_primary_result()` は

$$
H_{K\kappa}^{(1)}
=
-\frac{19}{3}-\frac{15}{8}\zeta(3)+\frac{11\pi^2}{36}+\frac34\pi^2\ln2
$$

を返す。

`corner_shift_correction_result()` は正しい momentum shift から生じる追加積分群

$$
\Delta A_{\mathrm{shift}}
=
\frac83-\frac{\pi^2}{4}-\frac{\pi^2}{6}\ln2+\frac34\zeta(3)
$$

を返す。したがって `corner_hard_total_result()` は

$$
H_{K\kappa}
=
-\frac{11}{3}-\frac98\zeta(3)+\frac{\pi^2}{18}+\frac{7\pi^2}{12}\ln2
$$

となる。

`corner_z_sector_result()` は

$$
A_z
=
\frac78+\frac58\zeta(3)-\frac{\pi^2}{4}\ln2
$$

を返す。

### 28.6 最終有限部

`corner_finite_result()` は

$$
A_{\mathrm C,fin}
=
-\frac{67}{24}+\frac{\pi^2}{18}-\frac12\zeta(3)+\frac{\pi^2}{3}\ln2
$$

を返す。`corner_result_difference()` は独立 checkpoint との差を exact に0へ簡約する。

`corner_full_asymptotic(rho)` は $o(1)$ を除き、

$$
A_{\mathrm C}(\rho)
=
\ln\frac1\rho+A_{\mathrm C,fin}
$$

を返す。

### 28.7 self-energy insertion との IR 相殺

`corner_self_energy_ir_cancellation()` は corner の IR-log coefficient $+1$ と self-energy insertion pair の coefficient $-1$ を保持し、合計が exact に0であることを確認する。

### 28.8 実行

`run_corner_2loop_demo.bat` を実行する。結果は `output/corner_2loop_trial.md` に保存される。

## 29. v0.21.0 bare 2ループ入力と closed-loop 自動抽出

### 29.1 `LoopIntegralExpression`

bare loop integral RHS を

$$
\mathcal N
\int d^Dk\,d^Dl\,
\mathcal I(k,l)
$$

として保持する内部型です。

- `prefactor_latex`: overall normalization を元の LaTeX のまま保持
- `loops`: loop momentum の tuple
- `dimension`: 積分次元
- `integrand`: QEDCalc の構造化式

### 29.2 `parse_loop_integral_latex()`

対応する基本形は

```latex
<prefactor> \int d^4k\,d^4l <integrand>
```

です。v0.21.0 では `\operatorname{tr}[...]`、`k_\rho`、`k^\rho` も構造として読み取ります。

### 29.3 `DiracTrace`

`\operatorname{tr}[...]` は文字列ではなく `DiracTrace(argument)` として保持されます。

`find_dirac_traces()` は integrand 内の trace を列挙し、`require_single_dirac_trace()` は trace が1個であることを検証します。

### 29.4 `reduce_trace_subdiagram_4d()`

trace 内部について、

1. propagator recognition
2. fermion propagator scalarization
3. numerator / denominator separation
4. numerator の4次元Dirac trace

を順に実行します。

したがって vacuum polarization の閉じた電子ループについて、元の bare 2-loop RHS から直接、trace numerator と scalar denominator へ到達できます。

### 29.5 現在の自動化境界

v0.21.0 で自動化された範囲は、

$$
\text{bare 2-loop RHS}
\rightarrow
\text{DiracTrace detection}
\rightarrow
\text{propagator scalarization}
\rightarrow
\text{trace numerator}
\rightarrow
l=r-zk
\rightarrow
\text{rank-2 reduction}
$$

です。

その後の transverse tensor の完全再構成、on-shell subtraction、outer magnetic kernel への接続は既存の専用層を使っています。今後はこの境界を外側へ広げます。


# 33. v0.22.1 — bare self-energy insertion bridge

## 33.1 対応入力

左右の self-energy insertion 2図を bare 2-loop RHS 全体として `parse_loop_integral_latex()` へ渡せます。

`find_self_energy_subdiagrams(diagram)` は、電子線上の

$$
S(r)\,\gamma^\alpha\,S(r-l)\,\gamma^\beta\,S(r)
$$

という連続5因子を検出します。両端の fermion propagator が同一で、中央 propagator との差が1つの loop momentum のみであることを構造的に検査します。さらに、その loop momentum のみに依存し、$\alpha,\beta$ を結ぶ photon factor が別因子として存在することを要求します。

## 33.2 API

- `find_self_energy_subdiagrams(diagram)`
- `require_single_self_energy_subdiagram(diagram)`
- `contract_self_energy_subdiagram(diagram, renormalized=False)`
- `contract_self_energy_to_outer_loop(diagram, outer_prefactor_latex=None, conventions=None, renormalized=False)`

検出結果 `SelfEnergySubdiagramMatch` は、左右位置、subloop momentum、外側電子 momentum、factor index、gamma index、photon factor を保持します。

## 33.3 numerator reduction

Feynman gauge の metric 部分では、raw middle propagator から

$$
\gamma^\alpha\left(m+\rlap{/}r-\rlap{/}l
ight)\gamma_\alpha
=4m-2\rlap{/}r+2\rlap{/}l
$$

を生成します。右図では $r=p-k$、左図では $r=p'-k$ が自動推論されます。

## 33.4 compact outer diagram

`contract_self_energy_to_outer_loop()` は subloop $l$ の measure を外側表現から除き、

$$
S(r)\Sigma^{(1)}(r)S(r)
$$

を含む1-loop outer diagram を返します。v0.25.0 では coupling normalization の所有規則を `conventions.txt` で明示し、`outer_prefactor_latex` を省略した場合は設定から outer prefactor を構成します。`outer_prefactor_latex` は特殊規約用の明示 override として利用できます。

既存の on-shell counterterm 処理で UV numerator が0になることを確認した後、`renormalized=True` を用いて

$$
S(r)\Sigma_R^{(1)}(r)S(r)
$$

と表示できます。

## 33.5 現在の制限

- subdiagram topology は式の順序から検出しますが、存在しない topology を推測して再配線しません。
- internal photon の numerator reduction は現段階では Feynman-gauge metric 部分を選択します。一般 covariant gauge の longitudinal part を raw式から最後まで自動処理する機能は未実装です。
- on-shell counterterm の有限部分は既存の $A(r^2),B(r^2)$ 層で処理します。raw general-gauge subloop から $A,B$ を完全自動再構成する部分は今後の対象です。

この版では全118テストが成功しています。


---

## 30. v0.25.0 ordinary ladder raw-input bridge

### 30.1 symbolic $D$ loop measure

`parse_loop_integral_latex()` は、数値次元だけでなく、

$$
\int d^Dk\,d^Dl
$$

を保持できるようになりました。`LoopIntegralExpression.dimension` はこの場合 `D` を保持します。

### 30.2 `analyze_raw_ordinary_ladder()`

入力は bare ordinary-ladder RHS 全体です。関数は電子線上の4本の propagator を順序付きで検出し、

$$
E_1\longleftrightarrow p'-k
$$

$$
E_2\longleftrightarrow p'-k-l
$$

$$
E_3\longleftrightarrow p-k-l
$$

$$
E_4\longleftrightarrow p-k
$$

と同定します。さらに2本の photon denominator から、

$$
K=-k^2
$$

$$
L=-l^2
$$

を確認します。IBP family を閉じる補助 denominator として、

$$
H=-(k+l)^2
$$

を exponent 0 で導入するため、bare graph は、

$$
J(1,1,0,1,1,1,1)
$$

と表現されます。

### 30.3 `derive_ladder_scalar_product_rules_from_family()`

この関数は既知の置換表を返すのではなく、$K,L,H,E_1,\ldots,E_4$ の定義を連立一次方程式として解きます。例えば、

$$
k\cdot l
=
\frac{K+L-H}{2}
$$

$$
p'\cdot k
=
\frac{E_1-K}{2}
$$

$$
p'\cdot l
=
\frac{E_2-H-E_1+K}{2}
$$

などを再導出します。既存の denominator-basis 規則との一致は回帰テストで確認します。

### 30.4 `raw_ladder_q0_numerator()`

scalarize した bare numerator に $p'=p$ を構造的に適用し、資料の $A_0$ branch の出発点、

$$
N_\mu^{(0)}
=
\gamma^\rho
\left(m+\rlap{/}p-\rlap{/}k\right)
\gamma^\alpha
\left(m+\rlap{/}p-\rlap{/}k-\rlap{/}l\right)
\gamma_\mu
\left(m+\rlap{/}p-\rlap{/}k-\rlap{/}l\right)
\gamma_\alpha
\left(m+\rlap{/}p-\rlap{/}k\right)
\gamma_\rho
$$

を raw graph から生成します。

### 30.5 現在の自動化境界

ここまでの family 検出と $q=0$ numerator 生成は raw bare LaTeX から自動です。一方、次の処理はまだ checkpoint/data-assisted です。

- 長い $D$ 次元 projector trace から75係数を完全生成する処理
- 75項から master integral へ落とす一般 IBP/Laporta reduction

したがって `ladder_Ddim_75_coefficients.csv` は引き続き独立導出済みの検証データとして使用します。


---

## 31. v0.25.0：任意長 $D$ 次元 Clifford trace と ordinary ladder $A_0$ の完全再生成

### 31.1 `dirac_trace_ddim()`

従来の4次元 trace 関数は、短い Gamma/Slash 列を対象としていました。v0.25.0 では、偶数本の任意長 Clifford word に対して、

$$
\operatorname{Tr}
\left(
\gamma^{\mu_1}\cdots\gamma^{\mu_{2n}}
\right)
$$

を再帰的な pairing で評価する `dirac_trace_ddim()` を追加しました。$\gamma_5$ は対象外です。trace 規格化は、

$$
\operatorname{Tr}(1)=4
$$

です。

### 31.2 `contract_fully_scalar_lorentz()`

長い trace から生成された metric と vector component が完全縮約された scalar である場合、Lorentz index network を解析し、

$$
g^{\mu
u}p_\mu q_
u
\longrightarrow
p\cdot q
$$

や閉じた metric loop、

$$
g^\mu{}_{\mu}
\longrightarrow
D
$$

を処理します。free index や3回以上現れる不正な index は推測せずエラーにします。

### 31.3 `dirac_trace_fully_contracted_sympy()`

ordinary ladder のような長い projector trace では、metric tensor を全て中間式として生成すると式が急増します。そのため、v0.25.0 では完全縮約される trace 専用の高速経路を追加しました。

この関数は、

1. Dirac numerator を scalar coefficient と Clifford word に分解する。
2. 同じ Clifford word をまとめる。
3. perfect pairing をキャッシュする。
4. metric expression を明示生成せず、pairing を直接 scalar product へ縮約する。
5. 最終結果を SymPy scalar polynomial として返す。

という処理を行います。

### 31.4 `ladder_a0_projector_trace_sympy()`

raw ordinary-ladder input から生成した $q=0$ numerator を用いて、

$$
A_0
=
\operatorname{Tr}
\left[
(\rlap{/}P+m)
N_\mu^{(0)}
(\rlap{/}P+m)
\gamma^\mu
\right]
$$

を直接評価します。

これにより、以前は資料側の checkpoint として扱っていた長い $D$ 次元 trace を、QEDCalc 自身が bare ladder 式から再実行できるようになりました。

### 31.5 `ladder_a0_denominator_polynomial()`

trace 後に、

$$
P^2=m^2
$$

および、

$$
P\cdot k
=
\frac{A-K}{2}
$$

$$
P\cdot l
=
\frac{B-H-A+K}{2}
$$

$$
k\cdot l
=
\frac{K+L-H}{2}
$$

などを適用し、結果を $K,L,H,A,B$ の polynomial へ変換します。

### 31.6 `ladder_a0_integral_table()`

$q=0$ の bare denominator、

$$
KLA^2B^2
$$

に対して、numerator polynomial の各 monomial を、

$$
J(n_K,n_L,n_H,n_A,n_B)
$$

へ変換します。

raw bare ladder LaTeX からこの処理を通した結果、資料で独立に得られていた値と同じく、

$$
\boxed{
A_0\text{ の scalar integral 数}=29
}
$$

を自動再生成します。

生成結果は、

`output/ladder_A0_29_coefficients_generated.csv`

へ保存できます。

### 31.7 実行用バッチ

`run_ladder_a0_trace_demo.bat`

を実行すると、

- raw bare ladder の読み込み
- $q=0$ numerator の生成
- 任意長 $D$ 次元 Clifford trace
- Lorentz scalar 化
- denominator polynomial 化
- 29 scalar integral の収集

を行い、

`output/ladder_A0_raw_trace_trial.md`

を生成します。

### 31.8 現在の残課題

ordinary ladder の historical 一般 $q^2$ branch については v0.26.0 で、

$$
P_\mu^{(2)}N_{\mathrm L}^{\mu}
$$

を完全展開し、資料で監査用に保存されている75係数表そのものを raw bare 式から再生成できるようになりました。

したがって v0.25.0 の自動化境界は、

$$
\boxed{
\text{raw bare ladder}
\rightarrow
A_0\text{ の29積分生成}
}
$$

および historical 一般 $q^2$ の75係数生成まで完全自動です。一般 IBP 方程式生成器と有限疎 Laporta 消去コアは v0.27.0 で実装済みです。完全な master reduction は次段階です。


## 32. v0.26.0：一般 $q^2$ ordinary ladder trace と75係数監査表の完全再生成

### 32.1 trace エンジンの高速化

有限 $q$ では scalar-product の種類が増えるため、pairing ごとに SymPy 式を逐次加算する方法は急速に遅くなります。v0.26.0 では各 Clifford pairing を

```text
(D のべき, scalar-product monomial)
```

という正規形キーへ変換し、整数係数を辞書で集約してから最後に SymPy 式を構築します。`_pairing_patterns()` と Clifford word trace 自体もキャッシュされます。

### 32.2 `ladder_general_q_projector_result()`

```python
ladder_general_q_projector_result(raw, trace_order="archived")
ladder_general_q_projector_result(raw, trace_order="spin_sum")
```

`archived` は資料に保存された75係数CSVを生成した historical projector-first trace、

$$
\operatorname{Tr}\left[(\rlap{/}p'+m)O_\mu(\rlap{/}p+m)\Gamma_{\mathrm L}^{\mu}\right]
$$

を再現します。この経路では raw bare ladder から **75個の integral-family monomial が生成され、`data/ladder_Ddim_75_coefficients.csv` と75個すべて完全一致**します。

一方 `spin_sum` は監査後の正しい順序、

$$
\operatorname{Tr}\left[(\rlap{/}p'+m)\Gamma_{\mathrm L}^{\mu}(\rlap{/}p+m)O_\mu\right]
$$

と、監査後の有限-$q$ projector coefficients を使用します。この経路は historical CSV と同一視しません。現在は72 monomialを生成します。

### 32.3 `ladder_corrected_projector_coefficients()`

監査後の係数を返します。

$$
a(z)=-\frac{2}{z(D-2)(z-4)}
$$

$$
b(z)=-\frac{Dz-2z+4}{z(D-2)(z-4)^2}
$$

### 32.4 table comparison / CSV output

```python
compare_ladder_integral_tables(generated, reference)
write_ladder_general_q_integral_table_csv(table, path)
```

比較結果は `missing`, `extra`, `mismatched` に分離されます。historical route の回帰テストでは3項目すべて空になります。

### 32.5 実行デモ

```text
run_ladder_general_q_trace_demo.bat
```

出力：

```text
output/ladder_general_q_raw_trace_trial.md
output/ladder_general_q_75_coefficients_generated.csv
output/ladder_general_q_corrected_spin_sum_generated.csv
```

### 32.6 重要な解釈

75係数表を完全再生成できることは、historical calculation の再現性監査として重要です。しかし、後の trace-order 監査で物理的 projector の順序が修正されているため、QEDCalc は75表を最終物理結果の projector として自動採用しません。最終 $F_2(0)$ には引き続き監査済みの有限極限 $A_0$ と $C_1=B_1-2A_1$ の route を使用します。

v0.27.0 で一般 IBP 方程式生成器と有限疎 Laporta 消去器を追加しました。残る大きな自動化課題は seed closure、sector/zero-sector 処理、完全な master-integral reduction です。


## 33. v0.27.0：一般 IBP 方程式生成器と有限 Laporta 消去

### 33.1 基本恒等式

`qedcalc.operations.ibp` を追加した。積分 family

$$
J(n_1,\ldots,n_N)
=\int d^{LD}k\,\prod_{a=1}^{N}D_a^{-n_a}
$$

に対して、

$$
0
=\int d^{LD}k\,\frac{\partial}{\partial k_i^\mu}\left[v^\mu\prod_aD_a^{-n_a}\right]
$$

を自動生成する。$v$ は loop momentum または external momentum を選べる。

### 33.2 denominator derivative の basis 還元

$ v\cdot\partial_{k_i}D_a $ に現れる $k\cdot l$, $k\cdot p$, $l\cdot p'$ などは `IntegralFamily.scalar_product_rules` を通じて denominator symbols と external invariants へ戻す。ordinary ladder では既存の $K,L,H,E_1,\ldots,E_4$ basis をそのまま使用する。未還元 `SP__...` atom が残ればエラーにする。

### 33.3 ordinary ladder bridge

`ordinary_ladder_ibp_family()` は

$$
(K,L,H,E_1,E_2,E_3,E_4)
$$

を持つ7分母 family を生成する。on-shell invariants は

$$
p^2=p'^2=m^2,\qquad p\cdot p'=m^2\left(1-\frac z2\right)
$$

として保持する。bare seed

$$
J(1,1,0,1,1,1,1)
$$

に対し、$\partial_k,\partial_l$ と $k,l,p,p'$ の組合せから8本のIBPを生成できる。

### 33.4 有限疎 Laporta 消去

`laporta_eliminate()` は有限なIBP式集合に対し、積分指数の難易度順にpivotを選び、symbolic sparse elimination を行う。これは完全なLaporta driverではなく、seed集合が既に与えられた場合の有限消去コアである。

1ループtadpole family $T=k^2-m^2$ では

$$
(D-2)J(1)-2m^2J(2)=0
$$

を生成し、$J(1)$ をprotected integralとすると

$$
J(2)=\frac{D-2}{2m^2}J(1)
$$

までreduceする。

ordinary ladder のbare-seed 8式では31個のdistinct integralが現れ、8個のpivotを有限消去できる。

### 33.5 seed と sector

`sector_signature()`、`sector_id()`、`first_neighbor_seeds()` を追加した。ordinary ladder のbare seedの第1近傍は8 seedであり、そこから64本のIBPと181個のdistinct integralが生成される。現段階では64式全体の完全消去を既定demoでは実行しない。

### 33.6 現在の境界

完全な7分母Laporta reductionには次が残る。

- sector ordering と symmetry
- scaleless / zero-sector detection
- seed domain の反復拡張とclosure判定
- rational-function coefficient field の高速簡約
- master integral の固定と境界条件
- 生成ruleの永続化と再利用

したがって v0.27.0 は「IBP式を作る段階」から「有限Laporta消去を実行できる段階」へ進んだ版であり、ordinary ladder 75項をmaster integralへ完全reduceする版ではない。


## 31. v0.29.0: ordinary ladder の family symmetry と generic-rank probe

ordinary ladder の7分母 family に、2つの生成元からなる4元の対称群を導入した。

外線交換では $E_1\\leftrightarrow E_4$, $E_2\\leftrightarrow E_3$、loop 再パラメータ化 $k\\to k+l$, $l\\to-l$ では $K\\leftrightarrow H$, $E_1\\leftrightarrow E_2$, $E_3\\leftrightarrow E_4$ となる。積分指数は orbit 内の辞書式最小代表へ canonicalize する。

degree-2 bounded domain は 36 seed から 24 symmetry representative へ減少し、IBP に現れる distinct integral は 623 から 335 へ減少する。

また symbolic reduction と切り離した診断として、係数のみを exact rational point $D=37/10$, $z=2/5$, $m^2=1$ に specialize する generic-rank probe を追加した。この有限 degree-2 system では forward sparse elimination が 162 pivot を生成する。これは任意 $D,z$ に対する解析 reduction rule ではなく、seed closure と rank を高速に監査するための機能である。


## 追加: exact rational reconstruction (v0.31.0)

Generic exact-rational probe で得た Laporta reduction の係数から、$D,z$ の有理関数を復元する機能を追加した。浮動小数点は使用せず、training に使っていない holdout 点で完全一致した場合だけ採用する。ordinary ladder corrected route の代表例として、$J(-1,0,0,1,1,1,1)$ と $J(0,0,1,1,0,1,1)$ の係数を再構成できる。現段階では全 target の完全再構成ではなく、adaptive degree / pole avoidance / finite-field acceleration が次の課題である。


## v0.34.0: residue-aware closure scheduler

v0.32.0 で corrected ordinary-ladder の 40 canonical target のうち 28 target に non-candidate residue が残ることが確認された。全 residue の degree-1 近傍を一括追加すると IBP 系が急膨張するため、v0.34.0 では residue の影響度を測って sector 単位で段階的に seed を追加する scheduler を導入した。

主な API は次のとおり。

- `residue_impact_profile()`：各 terminal residue が何個の target を阻害しているかを集計する。
- `residue_sector_profile()`：residue を sector ごとにまとめ、blocked target 数と新規 seed cost を集計する。
- `schedule_residue_sectors()`：新規 seed 数の上限を守りながら、impact / cost の高い sector から追加候補を選ぶ。

corrected ordinary-ladder の baseline 84-seed 系では、上位 sector は次のようになった。

- sector 96：22 target、1 new residue seed
- sector 82：18 target。ただし residue は既に baseline seed に含まれるため新規 seed cost は 0
- sector 80：17 target、1 new residue seed

第1フェーズでは近傍展開をせず terminal residue 自身だけを追加した。30個の新規 residue seed を追加すると、

- seed：84 → 114
- IBP row：666 → 906
- pivot：598 → 823
- residue-bearing target：28 → 27

となり、一括近傍展開のような計算爆発を避けながら 1 target を追加で完全 closure できた。

重要なのは、`score` は「この sector を追加すれば必ず target がその数だけ解ける」という意味ではなく、**どの residue sector が多くの target に現れ、少ない新規 direct seed で触れられるか**を表す scheduler priority である点である。

次段階では 114-seed 系で terminal residue を再集計し、高優先 sector の degree-1 neighborhood を厳しい seed budget の下で1 sectorずつ追加する。

## v0.34.0 — incremental Laporta と phase-2 scheduler

`reduce_ibp_equation_with_rules()` と `extend_laporta_rules_incrementally()` は既存の三角Laporta ruleを再利用し、新seedのIBPだけを追加処理します。`evaluate_neighborhood_seed_candidates()` は新pivotが既知terminal residueを直接解くかを調べ、`schedule_neighborhood_seeds()` はblocked targetの限界カバレッジで少数seedを選びます。ordinary ladder のphase-1系では22候補中7候補にdirect impactがあり、2 seedでblocked-target union 26をカバーします。これはclosure完了数ではなくscheduler metricです。


## v0.35.0 — factorized lower-subtopology classifier

新API `denominator_loop_direction()`、`loop_denominator_rank()`、`has_free_scaleless_loop_direction()`、`factorized_one_denominator_per_loop()`、`factorized_euclidean_scalar_value()` を追加した。propagator denominator の loop-space quadratic form が rank 1 で、L-loop sector に L 本の独立 denominator だけが存在する場合、可逆な線形 loop 変数変換で各 denominator を別々の loop variable に割り当てられる。ordinary ladder の `(0,0,0,0,0,1,1)`、`(0,0,0,0,1,0,1)`、`(0,0,0,0,2,0,3)` はこの条件を満たし、determinant は -1 なので Jacobian は unit である。これらは genuine two-loop master ではなく one-loop massive tadpole product として扱う。

phase-2 の2 seedを実際に追加した recursive reduction では 27 target が residue-bearing のままだが、上記3 lower sector を既知として分類すると 18 target に減る。残る terminal residue kind は3種類である。extended zero-sector diagnostic は、例えば `(0,0,0,0,0,0,2)` のように1つの loop direction が全く denominator に拘束されないsectorを scaleless zero と判定する。main Laporta pruning は後方互換性と速度のため従来の保守的 zero-sector 判定を保持し、extended 判定は scheduler/lower-sector 診断で明示的に使用する。

## 36. v0.36.0: 残る3積分の local master-candidate 診断

v0.35.0 で factorized lower subtopology を除外した後に残った3種類の terminal residue に対し、first-neighborhood の各 seed から生成した IBP を既存の triangular rule で incremental reduction し、その residue 自身を新しい pivot にできるかを調べる。

`diagnose_first_neighbor_irreducibility()` は、この有限範囲の診断を一般の `IntegralFamily` に対して行う。ordinary ladder では3 residue それぞれについて、新規 canonical first-neighbor seed 7個を試したが pivoting seed は0個だった。

したがって3積分を **provisional local master candidates** として扱うと、corrected non-factorized candidate basis は6個から9個になる。既知の factorized lower sectors と合わせれば、corrected 40 canonical targets に残っていた terminal non-basis residue はなくなる。

ただし、これは first-neighborhood に限定した局所的な IBP 既約性診断であり、3積分が大域的に真の master integral であることの証明ではない。より広い seed domain、独立な reduction system、または解析的 master-count argument による確認が今後必要である。


## 37. v0.37.0: directional depth-2 と multi-probe master-candidate 監査

### 37.1 `directional_depth2_seeds()`

first-neighborhood を全degree-2 Cartesian domainへ一気に広げると Laporta 系が急膨張するため、v0.37.0 では各指数方向を同じ方向へ2段だけ進める bounded audit domain を導入した。正の分母指数は $+2$、非正の numerator slot は $-2$ とする。symmetry canonicalization と existing-seed 除外を適用して返す。

### 37.2 `diagnose_directional_depth2_irreducibility()`

各 directional depth-2 seed のIBPだけを生成し、既存 triangular rule で incremental reduction する。terminal residue 自身が新しい pivot になるseedを記録する。

これは global irreducibility の証明ではない。

### 37.3 `build_specialized_laporta_rules()`

同じ canonical seed domain を複数の exact-rational $(D,z,\ldots)$ point で独立に再構築するための補助API。特定probeでの偶然のrank dropを監査する用途を想定する。

### 37.4 ordinary ladder の監査結果

残る3候補はfirst-neighborhoodでは全てpivot 0だった。さらに directional depth-2 では候補ごとに5--7個の新規canonical seedを試し、3つの独立 exact-rational probe 全てでpivot 0だった。各probeで基準Laporta rule数は837で一致した。

したがって3候補を **depth-2-stable provisional master candidates** と呼ぶ。ただし full degree-2 Cartesian domain や独立 reduction system による global proof はまだ行っていない。

実行: `run_phase5_depth2_master_demo.bat`


## 38. v0.38.0: full degree-2 Cartesian master-candidate 監査

### 38.1 `mixed_degree2_seeds()`

`bounded_seed_domain(..., max_extra_degree=2)` から中心、first-neighbor、同一方向depth-2、既存seedを除き、異なる2方向を1段ずつ動かす mixed degree-2 seed だけを返す。symmetry canonicalization 後の集合を使用する。

### 38.2 `diagnose_mixed_degree2_irreducibility()`

各 mixed seed が追加するIBPだけを既存triangular Laporta ruleへincrementalに流し、対象residue自身が新pivotになるかを検査する。ordinary ladder のprimary probeでは3候補について mixed pivot seedは0だった。

phase-2の116-seed baselineにすでに含まれるseedを除くと、新しいfull degree-2 seed数は3候補についてそれぞれ32、19、33。このうちmixed seedは18、10、21であり、すべて非pivotだった。first-neighborとdirectional depth-2も既監査なので、primary probeではcomplete bounded degree-2 Cartesian neighborhood全体で非pivotを確認した。

### 38.3 portable Laporta checkpoint

`write_laporta_rule_checkpoint()` / `read_laporta_rule_checkpoint()` はReductionRule集合をJSONへ保存・復元する。Python pickleに依存せず、exact-rational probeの837-pivot rule setを再利用できる。

これは依然としてbounded auditであり、global master-integral proofではない。独立reduction systemまたはより広いseed domainによる検証は残る。

実行: `run_phase6_full_degree2_master_demo.bat`


## 39. v0.39.0: 3独立probeでのfull degree-2監査

### 39.1 目的

v0.38.0ではprimary exact-rational probeだけでcomplete bounded degree-2 Cartesian neighborhoodを監査した。v0.39.0では同じ116-seed phase-2 baselineを残り2つの独立probeでも再構築し、mixed degree-2 classまで含めて3候補を再監査する。

使用probeは

$$
(D,z)=\left(\frac{37}{10},\frac{2}{5}\right),\quad\left(\frac{41}{11},\frac{3}{7}\right),\quad\left(\frac{29}{8},-\frac{1}{3}\right)
$$

であり、3系ともbaselineは837 pivotsになった。

### 39.2 結果

3候補についてmixed seed数はそれぞれ18、10、21。probe 2およびprobe 3でも、full mixed batchをincrementalに追加した後に候補自身がpivotになるケースは0だった。first-neighborとdirectional depth-2はv0.37.0で3probe監査済みなので、これにより3つの独立probeすべてでcomplete bounded degree-2 Cartesian domain全体が非pivotであることを確認した。

ただしこれは依然としてbounded-domainの証拠であり、global master-integral proofではない。

### 39.3 `build_integral_reducer()`

従来は新しいIBP rowごとに837-rule mapとrecursive cacheを作り直していた。`build_integral_reducer()` は1つのtriangular rule setに対するpersistent reducerを生成し、`extend_laporta_rules_incrementally()` は同じcacheを全new rowで共有する。これによりmulti-probe mixed auditを実用時間で処理できるようになった。

実行: `run_phase7_three_probe_full_degree2_demo.bat`


## v0.40.0: 3-probe full bounded degree-3 audit

ordinary ladder の3つの provisional master candidate に対し、既に監査済みの degree <= 2 seed を除いた bounded degree-3 shell を生成し、symmetry canonicalization 後に sector batch 単位で incremental Laporta へ追加する。

新しい API は `degree3_shell_seeds()` と `diagnose_full_degree3_irreducibility()`。3つの独立 exact-rational probe すべてで基準 Laporta 系は 837 pivots で一致し、degree-3 shell は candidate 1/2/3 について 72/84/84 seeds だった。全9 probe/candidate 組合せで candidate 自身は新pivotにならなかった。

したがって3候補は full bounded degree-3 domain まで安定した provisional master candidates として扱える。ただしこれは global master-count proof ではない。


## 41. v0.41.0: corrected ordinary-ladder の完全 symbolic reduction

### 41.1 40 target から12 basisへの閉包

corrected spin-sum general-$q^2$ route から得られる40個の symmetry-canonical target は、3つの独立 exact-rational 837-pivot checkpoint すべてで同一の12 terminal integralへ閉じる。内訳は9個のnon-factorized provisional basis候補と3個のfactorized lower subtopologyである。

### 41.2 全151非零係数の解析再構成

$40\times12=480$ 成分のうち151成分が非零である。各係数 $c_{ia}(D,z)$ は91点のCartesian gridから exact rational function として再構成し、gridに含まれない3つの独立probe

$$
(D,z)=\left(\frac{37}{10},\frac25\right),\quad\left(\frac{41}{11},\frac37\right),\quad\left(\frac{29}{8},-\frac13\right)
$$

でもexact一致を確認する。したがって各非零係数には94個のexact validation pointがある。gridだけで一致し独立probeで不一致になる補間式は採用しない。

完全行列は `data/ladder_corrected_40target_12basis_symbolic_reduction.csv` に保存する。非零151成分だけの表は `output/ladder_corrected_40target_symbolic_nonzero.csv` である。

### 41.3 denominator-guided reconstruction

`infer_allowed_univariate_denominator()` は、既知のIBP singular factorsだけを許可し、1変数sliceから最小の許容分母をexactに推定する。`reconstruct_bivariate_with_known_denominator()` は既知分母 $Q(D,z)$ を固定し、Cartesian grid上で分子多項式だけをtensor-product interpolationして、gridとholdoutの双方をexact検証する。

最も複雑だった

$$
J(-2,1,1,1,0,1,1)
$$

の basis 6 係数では、分母

$$
4(D-4)(D-3)(D-2)(2D-7)(3D-8)(z-4)
$$

を用いた構造化再構成によって、91 grid点と3独立probeすべてに一致する解析式を得た。

実行: `run_phase9_full_symbolic_reduction_demo.bat`

これは ordinary ladder の IBP coefficient reduction の完成を意味する。一方、12 basis integral 自身の解析評価、および crossed ladder / corner への同じraw-to-IBP経路の横展開は次段階である。


## 42. v0.42.0: ordinary ladder 12 basis integral の評価層

### 42.1 全12 basis の projective parameter 表現

`scalar_feynman_parametric_representation()` は scalar integral family の正指数 denominator から、

$$
I=\pi^{LD/2}\frac{\Gamma(\nu-LD/2)}{\prod_i\Gamma(n_i)}\int_{\sum x_i=1}\!\left(\prod_i x_i^{n_i-1}\right)\frac{U^{\nu-(L+1)D/2}}{F^{\nu-LD/2}}
$$

の convention-free Euclidean projective representation を構成する。ordinary ladder では7分母の quadratic form から $U=\det A$、$\Delta=B^T A^{-1}B$、$F=U\Delta$ を自動生成する。全12 basis で $U$ は2次、$F$ は3次のhomogeneous polynomialになることを回帰テストで確認する。

### 42.2 generic-z の factorized lower sector

basis 0, 1, 3 は generic $z$ の時点で one-loop massive tadpole の積へ因数分解する。`massive_tadpole_euclidean()` と既存の factorized-subtopology classifier により exact Gamma-function value を得る。

### 42.3 z=0 で9/12を解析評価

$z=0$ では $p'=p$ なので $E_1=E_4$、$E_2=E_3$ となる。これにより basis 2 は $T_2T_1$、basis 4 は $T_2^2$ へ退化する。basis 5, 6 は one-massless/two-equal-mass vacuum sunset となり、Schwinger parameter 積分から `one_massless_two_massive_vacuum_euclidean()` で Gamma 関数表示を得る。basis 7, 9 は massless bubble を先に積分し、残った generalized on-shell one-loop integral を `massless_bubble_on_shell_electron_euclidean()` で評価する。

したがって exact analytic な basis index は

$$
0,1,2,3,4,5,6,7,9
$$

であり、残る genuine two-loop $z=0$ master は

$$
8,10,11
$$

の3個である。これは master-integral evaluation 問題を12個から3個へ縮約したことを意味する。

### 42.4 規約境界

ここで返す値は convention-free Euclidean scalar integral である。Minkowski の $i$、Wick rotation の符号、$(2\pi)^D$ measure、$\mu^{2\epsilon}$、$S_\epsilon$ などは `conventions.txt` / dimreg layer で別途付与する。

実行: `run_phase10_basis_evaluation_demo.bat`


## 43. v0.45.0: $z=0$ terminal basis 12/12 完全解析評価

### 43.1 reduced $T_n$ family

$z=0$ では $E_1=E_4$, $E_3=E_2$ なので、旧 basis 8, 10, 11 は

$$
T_n=\int\frac{d^Dk\,d^Dl}{L\,H\,E_2\,E_4^n},\qquad n=1,2,3
$$

へ統一されます。`ordinary_ladder_z0_reduced_ibp_family()` は auxiliary $K$ を含む $(K,L,H,E_2,E_4)$ family を生成し、`ordinary_ladder_z0_T_ibp_reductions()` は degree-1 seed から $T_2,T_3$ の symbolic reduction を再生成します。

$$
T_2=-\frac{D-3}{2m^2}T_1-\frac{1}{2m^2}A
$$

および

$$
T_3=
\frac{(D-6)(D-4)(D-3)}{8(m^2)^2(D-5)}T_1
+\frac{(D-4)^2}{2(m^2)^2(D-5)}A
+\frac{D-4}{4m^2(D-5)}E
$$

となります。$A,E$ は `massless_two_point_then_on_shell_electron_euclidean()` で Gamma 関数評価されます。

### 43.2 $T_1$ の Cheng--Wu / Gauss 評価

$D=4-2\epsilon$ とし、$x_{E_2}+x_{E_4}=1$ を選ぶと、2つのmassless parameterを積分した後は

$$
\frac{1}{(1-\epsilon)(1-2\epsilon)}
\int_0^1dt\,
 t^{-1+\epsilon}
\left[(1-t)^{-1+\epsilon}-(1-t)^{-\epsilon}\right]
{}_2F_1(2\epsilon,1;2-\epsilon;t)
$$

だけが残ります。Euler--Beta公式で ${}_3F_2(1)$ に変換すると上下パラメータが相殺し、Gauss公式によりGamma関数だけへ閉じます。実装は `ordinary_ladder_T1_z0_euclidean()` です。

### 43.3 完了状態

`ordinary_ladder_basis_z0_evaluations()` は12 basisすべてを `exact` として返します。未解決basisは0です。`run_phase11_complete_basis_demo.bat` がIBP relation、lower-sector分類、$T_1$ closed form、および12/12のCSVを再生成します。


## 44. v0.44.0: projector/reduction 合成と z 極監査

`qedcalc.operations.ladder_assembly` は補正済み72項を40個の対称 target にまとめ、v0.41 の 40 x 12 symbolic reduction と合成します。`ladder_basis_z_pole_residues()` と `ladder_basis_z_double_pole_coefficients()` で `z -> 0` の極を監査し、`ladder_projector_leading_z_pole_cancellation()` で v0.43 の正確な z=0 基底値を使った全 `1/z` 係数の消去を確認します。v0.41 reduction matrix は `m^2=1` 規格化です。有限部で必要な一次微分は basis 0,1,3,5,6,7,8 に限られます。

## 44. v0.45.0：crossed ladder の対称性と raw-to-parametric bridge

crossed の7スロット family は `(K,L,H,E1,E2,E3,E4)` を使い、`H=-(k+l)^2` は補助分母です。外線交換 `p<->p'` とループ交換 `k<->l` を同時に行うと、`K<->L`、`E1<->E4`、`E2<->E3`、`H` 固定という厳密な分母置換対称性が得られます。これを使うと corrected projector の95 target は52個の代表へ減ります。

exact-rational probe `(D,z,m2)=(37/10,2/5,1)` では、対称化後の target seed 系は416 IBP行、378 pivot となり、52 target のうち40個が pivot します。残る12個は bounded first-neighbor audit で pivoting seed が0でした。したがって次段階は無制限な seed 拡大ではなく、degree-2 監査または z=0 専用縮約です。

`crossed_bare_scalar_parametric_representation()` は `K,L,E1,E2,E3,E4` から標準6分母 crossed scalar integral の Symanzik `U,F` を自動生成します。`U` は2次、`F` は3次の斉次多項式です。これにより denominator レベルでは raw family から projective integration まで接続しました。projected numerator から projective kernel への自動変換は引き続き未完の層です。

## 45. v0.47.0：crossed ladder q 一次 projector bridge

`crossed_raw_numerator_q_expansion()` は完全な raw crossed numerator に `p'=p+q` を導入し、非可換積を展開して q 一次まで保持する。結果は q^0 が144項、q^1 が84項である。

`crossed_q0_five_denominator_family()` と `crossed_q0_parametric_bridge()` は q=0 の5分母 family `(K,L,Dk,Dkl,Dl)`、powers `(1,1,1,2,1)` を構成する。一般 Symanzik 生成器から

$$
U=(x+y+u)(y+z+v)-y^2=\Delta
$$

および

$$
F=(y+z+v)(x+y)^2-2y(x+y)(y+z)+(x+y+u)(y+z)^2=W
$$

を独立に再生成し、parameter measure の monomial も `y` となる。

`crossed_denominator_q1_correction()` は

$$
\delta\mathcal D=2x\,k\cdot q+y(k+l)\cdot q
$$

を返す。`crossed_breit_projector_check()` は明示4×4 Dirac行列と Breit-frame spinor を用い、F1係数0、F2係数1を厳密に確認する。

## 46. v0.50.0：crossed ladder の U 積分・三角領域・raw kernel・Hermite reduction

生成済みの V 部分分数の後で `h=S(R+U)-1` を用いる。元の領域 `S>=1` から `0<=U<=h-R+1` が得られる。`Y=R+U` とすると、残る U 依存は Y の多項式を Y の単項式冪で割った形になるため、一般 CAS 積分を使わず単項式 primitive だけで厳密に U 積分を行う。

続いて `h=(1-t)/t`, `R=q/t` と変換すると Jacobian は `1/t^3`、領域は `0<t<q<1` となる。logarithm の引数も `(q^2+(1-2q)t)/(q^2(1-t))` と再生成される。

t 積分では下端 cutoff を残し、rational sector と logarithmic sector を合成した後で極限を取る。`log(epsilon)` の係数は厳密に 0 となり、1変数 raw kernel は `1,L,M,L^2,LM,D(q)` の基底で閉じる。

`crossed_automatic_hermite_reduction()` は L, M, D(q) の微分を含めて rational Horowitz-Ostrogradsky reduction を段階的に適用し、保存済み係数表を使わずに `R,T,U,V,P,Q,Z` と simple-pole canonical kernel を再生成する。結果は独立導出資料の total-derivative primitive および canonical kernel と厳密一致する。

実行バッチは `run_phase23_crossed_u_tq_bridge_demo.bat`、`run_phase24_crossed_raw_q_kernel_demo.bat`、`run_phase25_crossed_automatic_hermite_demo.bat`。

## 51. v0.51.0：crossed ladder canonical kernel の独立解析評価

crossed ladder の最終解析評価では、`q=1/2` sector の3個の標準積分値と endpoint finite 定数を最終入力値として直接使用しないようにした。`crossed_standard_integrals_derived()` は奇数項 zeta 和と alternating Euler sum から half-sector の標準積分を構成する。`crossed_endpoint_canonical_integral_derived()` は endpoint-safe canonical kernel から `L^2, LM, M^2, L, M, 1` の係数を自動抽出し、cutoff を残したまま厳密積分する。

`crossed_endpoint_asymptotics_derived()` は自動 Hermite reduction で得た全微分 primitive から endpoint 境界項を再生成する。`q->1` 側の `D(q)` 級数は正確な `D'(q)` と `D(1)=0` から生成し、`q->0` 側は dilogarithm inversion の実枝漸近式を使う。canonical part と boundary part の3次・2次・1次 cutoff logarithm は厳密に相殺する。

`crossed_final_result()` はこれらの再生成値だけから最終係数を合成する。`crossed_expected_result()` は独立導出後の回帰比較にのみ使用する。

実行：`run_phase26_crossed_independent_analytic_demo.bat`
