# QEDCalc サンプルプログラム説明書兼計算過程説明書：vacuum polarization 1図

## 0. この資料の目的

内部 photon propagator に1ループ electron vacuum-polarization bubble を挿入した2ループ頂点図について、complete raw diagram から closed Dirac trace を見つけ、真空偏極 tensor、on-shell subtraction、outer magnetic kernel、2変数積分、最終解析値へ進む流れを説明する。この図は「subdiagram を抽出して低ループの既知構造へまとめる」という QEDCalc の使い方が最も明瞭な例である。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **vacuum polarization 1図** である。

本資料では各段階を次の3種類に区別する。

- **【人が決める】**：diagram の同定、Feynman gauge の採用、on-shell 条件、どの form factor を求めるか、どの変数変換を行うかなど、物理的意味を伴う選択。
- **【QEDCalc】**：LaTeX parse、Dirac 代数、loop shift、odd 項除去、tensor reduction、IBP、式の簡約、解析積分の機械的部分、residual の exact check など。
- **【接続】**：人が導出した式を QEDCalc の入力形式へ移す、または QEDCalc の出力を次の物理的段階へ解釈する部分。

重要なのは、QEDCalc は Feynman 図の意味を勝手に推測して全計算をブラックボックス処理するプログラムではないことである。**処理順序は人が決め、長大で機械的な代数を QEDCalc/SymPy に渡す**。QEDCalc の設計思想もこの分離にある。

## 0.1 この資料の読み方

各計算段階では原則として次の順序で記載する。

1. なぜ次の処理が必要か。
2. 人が導出・選択しなければならない内容。
3. QEDCalc に渡す LaTeX または数式入力。
4. 実際のサンプルプログラムのファイル名と行番号。
5. QEDCalc の主要出力。
6. その出力を次の段階でどう使うか。

したがって、コードブロックだけを飛び飛びに読むのではなく、**「入力式がなぜその形になるか」→「コード」→「出力の物理的意味」**の順に読む。

## 0.2 数式と規約

- 外部電子は on-shell とする。
- 電子質量を $m$ とする。
- 外部 photon momentum は $q=p'-p$ とする。
- anomalous magnetic moment は Pauli form factor $F_2(0)$ から得る。
- 必要な箇所では $D$ 次元を保持し、最後に $D\to4$ を取る。
- IR 正則化が必要な図では photon mass $\lambda$ と $\rho=\lambda/m$ を用いる。


## 0.3 本資料での「人」と「QEDCalc」の受け渡しの書き方

この資料では、計算の各段階を単に「人が行う」「QEDCalc が行う」と分類するだけではなく、必ず次の受け渡しを明示する。

1. **前段階から入ってくる式・データ**：この段階を始める時点で何が既知なのか。
2. **人が用意する入力**：Feynman 図の読み取り、運動学、renormalization 条件、変数変換など、物理的・解析的判断を伴う部分。
3. **QEDCalc に実際に渡る入力**：LaTeX ファイル、SymPy 式、index table、parameter family など、プログラムが直接受け取るもの。
4. **サンプルコード**：QEDCalc v0.90.0 のどのファイルの何行が処理を行うか。
5. **QEDCalc の出力**：数式として何が得られ、どの residual / term count / table が検算されるか。
6. **次段階へ渡すもの**：得られた出力のうち、次の物理計算で実際に使用するもの。

したがって、関数が引数なしで呼ばれている場合も「入力なし」という意味ではない。関数内部で `input/*.tex` を読む場合、あるいは前段階で確定した topology・kinematics が関数内部に実装されている場合は、それを明示する。

また、長大な数十～数百項の多項式を QEDCalc が生成する場合、本資料ではその多項式を人が再び手計算することを目的としない。その場合でも、**何という多項式を生成したか、その数学的定義、項数、入力変数、次段階での使われ方**は必ず記載する。完全展開式は QEDCalc の生成物として再出力できる形を保つ。


## 0.4 全工程の入出力一覧

| 工程 | 人が用意・判断するもの | QEDCalc に渡る入力 | QEDCalc の主な出力 | 次へ渡すもの |
|---|---|---|---|---|
| raw graph | closed electron loop を含む complete RHS | raw two-loop LaTeX | unique `DiracTrace` node、outer factors | VP subloop |
| trace numerator | propagator numerator identity | trace argument | $N^{\alpha\beta}(l,k)$ | tensor integral |
| shift/tensor reduction | Feynman parameter $z$ と shift | $N^{\alpha\beta}$ + denominators | even-$r$ tensor、rank-2 reduction | $\Pi^{\alpha\beta}$ |
| transversality | Ward identity により許される tensor form | reduced tensor | $k_\alpha\Pi^{\alpha\beta}=0$ residual | scalar $\Pi(k^2)$ |
| on-shell subtraction | $\Pi_R(0)=0$ | bare scalar VP | $\Pi_R(k^2)=\Pi(k^2)-\Pi(0)$ | finite insertion |
| outer magnetic kernel | VP scalarを photon line へ挿入 | $\Pi_R(k^2)$ + one-loop magnetic kernel | 2変数 $x,z$ integral | $A_{\rm VP}$ double integral |
| $z$ integration | analytic integration route | double kernel | one-variable kernel | $x$ integral |
| endpoint evaluation | primitive と endpoints を別検査 | one-variable kernel | primitive derivative residual $0$、endpoints | $119/36-\pi^2/3$ |
| release checkpoint | transverse/on-shell/final を同時検査 | analytic outputs | exact closure | VP 最終寄与 |

全体は

$$
\mathcal I_{\rm VP}^{\rm raw}
\longrightarrow
N^{\alpha\beta}
\longrightarrow
\Pi_R(k^2)
\longrightarrow
K_{F_2}(x,z)
\longrightarrow
A_{\rm VP}
$$

である。

## 1. 元の入力となる Feynman 図

### 1.1 【人が決める】complete raw RHS

$$
\mathcal I = -\frac{e^4}{(2\pi)^8 i^2}
\int d^4k\,d^4l
\gamma^\rho
\frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon}
\gamma_\mu
\frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon}
\gamma^\sigma
\left( -\left(
g_{\rho\alpha} +(1-\alpha)
\frac{k_\rho k_\alpha}{-k^2-i\varepsilon}
\right)
\frac{1}{-k^2-i\varepsilon}
\right)
\operatorname{tr}\left[
\frac{1}{m-\rlap{/}l-\rlap{/}k-i\varepsilon}
\gamma^\alpha
\frac{1}{m-\rlap{/}l-i\varepsilon}
\gamma^\beta
\right]
\left( -\left(
g_{\beta\sigma} +(1-\alpha)
\frac{k_\beta k_\sigma}{-k^2-i\varepsilon}
\right)
\frac{1}{-k^2-i\varepsilon}
\right)
$$

閉じた electron loop は $l$ 積分を含む `tr[...]` 部分である。図からこの closed loop が vacuum polarization subdiagram だと認識する物理的意味は人が理解する。

## 2. closed electron loop を抽出する

### 2.1 【QEDCalc】complete raw diagram の parse と trace detection

**該当コード：`examples/vacuum_polarization_2loop_trial.py` 17～32 行**

```python
ROOT = Path(__file__).resolve().parents[1]
source_path = ROOT / "input" / "vacuum_polarization_2loop_bare.tex"
out_path = ROOT / "output" / "vacuum_polarization_2loop_trial.md"

source = source_path.read_text(encoding="utf-8").strip()
diagram = parse_loop_integral_latex(source)
bridge = reduce_vp_subdiagram_from_bare_2loop_4d(diagram)
tr = bridge.trace_reduction

x, z, k2, m = sp.symbols("x z k2 m", positive=True)
pi_hat_integrand = vp_hat_renormalized_integrand(k2, m, z)
double_kernel = vp_gminus2_double_integrand(x, z)
H = vp_z_integrated_kernel(x)
numeric = vp_numeric_coefficient(40)
recognized = vp_recognize_analytic(numeric, 40)
expected = vp_expected_analytic()
```
`parse_loop_integral_latex()` が complete RHS を parse し、`reduce_vp_subdiagram_from_bare_2loop_4d()` が explicit `DiracTrace` node を見つけて propagator を scalarize する。

## 3. trace numerator の導出

### 3.1 【接続】propagator numerator

電子 propagator は

$$
\frac1{m-\rlap{/}a-i\varepsilon} =
\frac{m+\rlap{/}a}{m^2-a^2-i\varepsilon}
$$

なので closed loop numerator は

$$
(m+\rlap{/}l+\rlap{/}k)\gamma^\alpha(m+\rlap{/}l)\gamma^\beta
$$

となる。

### 3.2 【QEDCalc】Dirac trace、loop shift、odd-term removal、rank-2 reduction

#### 入力

入力は前節で導出した $N^{\alpha\beta}(l,k)$ と2本の electron denominator である。

#### 出力

QEDCalc は Feynman parameter $z$ を導入し、$l=r-zk$ と shift する。odd-$r$ 項を除去した後、

$$
r^\alpha r^\beta
\longrightarrow
\frac{g^{\alpha\beta}}{D}r^2
$$

の rank-2 symmetric reduction を適用する。出力は $g^{\alpha\beta}$ と $k^\alpha k^\beta$ の2 tensor structure だけを含む reduced numerator である。

メイン trial は bridge の中間出力をすべて Markdown へ保存する。

**該当コード：`examples/vacuum_polarization_2loop_trial.py` 42～49 行**

```python
session.equation("Bare two-loop RHS parsed from LaTeX", diagram)
session.text("Detected Dirac traces", str(len(find_dirac_traces(diagram.integrand))))
session.equation("Scalarized closed-loop fraction", tr.scalarized)
session.equation("Closed-loop trace numerator", tr.traced_numerator)
session.equation("Closed-loop scalar denominator", tr.scalar_denominator)
session.equation("After l = r - z k", bridge.shifted_trace_numerator)
session.equation("After removing odd powers of r", bridge.even_trace_numerator)
session.equation("After rank-2 symmetric tensor reduction", bridge.tensor_reduced_trace_numerator)
```
この出力により、旧資料にあった長い trace 展開を本文へ再掲する必要はない。必要なら生成結果を直接比較できる。

## 4. 真空偏極 tensor の transverse form

### 4.1 【人が理解する】Ward identity と tensor 構造

current conservation により renormalized vacuum polarization tensor は

$$
\Pi^{\alpha\beta}(k) =
\left(k^2g^{\alpha\beta}-k^\alpha k^\beta\right)\Pi(k^2)
$$

の transverse form でなければならない。これは単なる代数上の便利な分解ではなく gauge invariance の結果である。

### 4.2 【QEDCalc】transversality residual

#### 入力

入力は前節の reduced tensor integral である。

#### 出力

QEDCalc は coefficient を整理して

$$
\Pi^{\alpha\beta}(k) =
\left(k^2g^{\alpha\beta}-k^\alpha k^\beta\right)\Pi(k^2)
$$

の形へ再構成し、$k_\alpha\Pi^{\alpha\beta}$ の residual を計算する。出力0は Ward identity に必要な transversality が保たれたことを意味する。

Phase 27 raw-to-final audit は tensor-reduced numerator から transverse residual を検査する。

**該当コード：`examples/phase27_vacuum_polarization_raw_to_final.py` 11～27 行**

```python
ROOT=Path(__file__).resolve().parents[1]
diagram=parse_loop_integral_latex((ROOT/'input'/'vacuum_polarization_2loop_bare.tex').read_text(encoding='utf-8'))
raw=reduce_vp_subdiagram_from_bare_2loop_4d(diagram)
a=vp_raw_to_final_audit()

print('Phase-27 vacuum-polarization raw-to-final bridge')
print('Raw tensor-reduced numerator:')
print(render_latex(raw.tensor_reduced_trace_numerator))
print('Transverse residual:', a.transverse_residual)
print('D->4 subtracted VP integrand:', sp.factor(a.four_dimensional_integrand))
print('Generated double kernel:', sp.factor(a.double_kernel))
print('Generated z kernel H(x):', sp.factor(a.z_kernel))
print('Primitive derivative residual:', a.primitive_derivative_residual)
print('F(1):', a.endpoint_one)
print('F(0):', a.endpoint_zero)
print('Generated A_VP:', a.final_coefficient)
print('Checkpoint difference:', sp.simplify(a.final_coefficient-vp_expected_analytic()))
```
`Transverse residual: 0` が出ることで tensor 構造が閉じる。

## 5. on-shell subtraction

### 5.1 【人が決める】電荷 renormalization condition

physical charge を $k^2=0$ で定義する on-shell scheme では

$$
\Pi_R(k^2)=\Pi(k^2)-\Pi(0),\qquad \Pi_R(0)=0
$$

とする。この subtraction scheme の選択は物理的入力である。

### 5.2 【QEDCalc】finite $D\to4$ kernel

#### 入力

入力は bare scalar vacuum-polarization function $\Pi(k^2)$ と、人が5.1で指定した on-shell condition $\Pi_R(0)=0$ である。

#### 出力

QEDCalc は

$$
\Pi_R(k^2)=\Pi(k^2)-\Pi(0)
$$

を構成して UV constant を消し、$D\to4$ を取った有限 parameter kernel を返す。次節ではこの scalar correction を outer photon line に挿入する。

メイン trial は `vp_hat_renormalized_integrand(k2,m,z)` を呼び、subtracted scalar vacuum-polarization integrand を生成する。

**該当コード：`examples/vacuum_polarization_2loop_trial.py` 51～65 行**

```python
session.equation(
    "Reference transverse tensor checkpoint",
    r"\Pi^{\alpha\beta}(k)=\left(k^2g^{\alpha\beta}-k^\alpha k^\beta\right)\Pi(k^2)",
)
session.equation(
    "On-shell subtraction condition",
    r"\Pi_R(k^2)=\Pi(k^2)-\Pi(0),\qquad \Pi_R(0)=0",
)
session.equation("Renormalized scalar vacuum-polarization integrand", sp.latex(pi_hat_integrand))
session.equation("Two-parameter g-2 coefficient kernel", sp.latex(double_kernel))
session.equation("z-integrated kernel H(x)", sp.latex(H))
session.text("Numerical coefficient", f"A_VP = {numeric}")
session.equation("Analytic recognition from the numerical value", sp.latex(recognized))
session.equation("Reference analytic coefficient", sp.latex(expected))
session.text("Recognition check", "PASS" if sp.simplify(recognized - expected) == 0 else "FAIL")
```
ここで analytic recognition は導出の入力ではなく、生成された数値/解析積分の output-side check である。

## 6. outer magnetic vertex へ挿入する

### 6.1 【人が理解する】tensor から scalar propagator correction へ

transverse $\Pi_R$ を photon propagator の間に挟むと、外側 electron vertex では scalar correction として扱える。さらに1ループ magnetic projector を適用すると、2ループ VP contribution は2変数 kernel に還元できる。

### 6.2 【QEDCalc】2変数 kernel

#### 入力

入力は renormalized scalar $\Pi_R(k^2)$ と、1-loop magnetic vertex の Feynman parameter $x$ representation である。

#### 出力

QEDCalc は photon momentum $k^2$ を outer magnetic kernel の parameter expression に置換し、最終的に

$$
A_{\rm VP} =
2\int_0^1dx\,(1-x)
\int_0^1dz\,z(1-z)
\ln\left[
1+\frac{x^2}{1-x}z(1-z)
\right]
$$

という2変数積分を返す。これが以後の解析積分の入力である。

`vp_gminus2_double_integrand(x,z)` が outer magnetic parameter $x$ と VP parameter $z$ の kernel を返す。これが「subdiagram の計算結果を outer graph へ接続する」API である。

## 7. $z$ 積分から1変数 kernel へ

### 7.1 【QEDCalc】analytic $z$ integration

#### 入力

入力は前節の $x,z$ double integral である。

#### 出力

QEDCalc は $z$ 積分を解析的に実行し、$x$ だけの kernel $K_{\rm VP}(x)$ を返す。ここでは2変数積分を直接数値評価して終わらせず、次節で primitive と endpoint を独立に検算できる1変数形にすることが目的である。

`vp_z_integrated_kernel(x)` が $z$ 積分済み $H(x)$ を返す。Phase 27 では generated z kernel も出力される。元資料の $z$ 積分の部分分数・対数整理は、この関数の検証後は省略できる。

## 8. $x$ 積分と endpoint

### 8.1 【人が理解する】endpoint を個別に評価する理由

原始関数 $F(x)$ を作って $F(1)-F(0)$ を取るとき、各 endpoint には log を含む見かけの特異表現がある。したがって式をそのまま代入するのでなく limit を取る必要がある。

### 8.2 【QEDCalc】primitive derivative と endpoints

#### 入力

入力は1変数 kernel $K_{\rm VP}(x)$ と、その解析 primitive candidate である。

#### 出力

QEDCalc は

$$
\frac{d}{dx}P_{\rm VP}(x)-K_{\rm VP}(x)
$$

を symbolic に簡約して0になることを確認し、さらに $x=0,1$ の endpoint を別々に評価する。その差から

$$
\boxed{A_{\rm VP}=\frac{119}{36}-\frac{\pi^2}{3}}
$$

を得る。

Phase 27 は `primitive_derivative_residual`、`F(1)`、`F(0)` を出力し、primitive が本当に generated kernel の原始関数かを exact に確認する。最終係数は

$$
A_{\mathrm{VP}} =
\frac{119}{36} -
\frac{\pi^2}{3}
$$

である。

## 9. Phase 79 release checkpoint

Phase 79 は、transversality、on-shell subtraction、finite $D\to4$ kernel、outer insertion、$z$ kernel、primitive derivative、final closed form を一括で residual 0 と要求する。

**該当コード：`examples/phase79_vacuum_polarization_end_to_end_checkpoint.py` 2～25 行**

```python
from qedcalc.operations.vacuum_polarization import vp_phase79_end_to_end_checkpoint

c = vp_phase79_end_to_end_checkpoint()
assert c["transverse_residual"] == 0
assert c["on_shell_subtraction_residual"] == 0
assert c["four_dimensional_kernel_residual"] == 0
assert c["outer_insertion_kernel_residual"] == 0
assert c["z_kernel_residual"] == 0
assert c["primitive_derivative_residual"] == 0
assert c["final_closed_form_residual"] == 0

out = Path(__file__).resolve().parents[1] / "output" / "phase79_vacuum_polarization_end_to_end_checkpoint.md"
out.parent.mkdir(exist_ok=True)
lines = [
    "# Phase 79: vacuum-polarization end-to-end closure checkpoint", "",
    f"Transversality residual: `{c['transverse_residual']}`", "",
    f"On-shell subtraction residual: `{c['on_shell_subtraction_residual']}`", "",
    f"Finite D->4 kernel residual: `{c['four_dimensional_kernel_residual']}`", "",
    f"Outer magnetic insertion residual: `{c['outer_insertion_kernel_residual']}`", "",
    f"z-kernel residual: `{c['z_kernel_residual']}`", "",
    f"Primitive derivative residual: `{c['primitive_derivative_residual']}`", "",
    "Final coefficient:", "", "$$", str(c['final']), "$$", "",
    "Closed form:", "", "$$", str(c['closed_form']), "$$", "",
    f"Final residual: `{c['final_closed_form_residual']}`", "",
```
通常の regression ではこれだけを走らせれば、VP route の主要接続が壊れていないことを短時間で確認できる。

## 10. 現在の自動化境界

| 段階 | 状況 | 担当 |
|---|---|---|
| complete raw diagram 式 | 人が確認 | 人 |
| closed trace node detection | 自動 | QEDCalc |
| propagator scalarization / Dirac trace | 自動 | QEDCalc |
| loop shift / odd removal / tensor reduction | 自動 | QEDCalc |
| transverse tensor の物理的意味 | 人が理解 | 人 |
| transversality residual | 自動 | QEDCalc |
| on-shell subtraction scheme | 人 | 人 |
| subtracted scalar kernel | 自動 | QEDCalc |
| outer magnetic kernel | 自動 | QEDCalc |
| $z,x$ analytic integration / residual | 自動化済み | QEDCalc/SymPy |

## 11. 最短再計算手順

1. `input/vacuum_polarization_2loop_bare.tex` を確認。
2. `vacuum_polarization_2loop_trial.py` で raw trace bridge と downstream kernels を生成。
3. Phase 27 で raw-to-final audit。
4. Phase 79 で release checkpoint。
5. v0.90 regression で7図合計を確認。

## 12. この資料で省略できた手計算

closed trace の数十項展開、$l=r-zk$ 後の odd-term 判定、rank-2 tensor reduction、transverse tensor の係数比較、$z$ 積分の長い整理、primitive の微分照合は QEDCalc に移せる。本文に残す必要があるのは、closed loop が vacuum polarization である理由、transversality の意味、on-shell subtraction の意味、outer graph への接続である。

## 13. 参照元と再実行ファイル

- 元計算資料：`vacuum_polarization_F2_4/vacuum_polarization_F2_導出_全体見直し修正版.md`
- raw input：`input/vacuum_polarization_2loop_bare.tex`
- closed-loop numerator：`input/vacuum_polarization_subloop.tex`
- main sample：`examples/vacuum_polarization_2loop_trial.py`
- raw-to-final：Phase 27
- release closure：Phase 79

代表実行は `run_vp_2loop_demo.bat`、`run_phase27_vacuum_polarization_raw_to_final.bat`。全体 regression は `run_v090_validation.bat`。


---

## 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。
