# QEDCalc two-loop full process report: Crossed ladder

Diagram multiplicity: **1**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

## 1. Raw input expressions

### `input/crossed_ladder_2loop_bare.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\mu \\
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\rho \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

## 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/01_crossed_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

### QEDCalc サンプルプログラム説明書兼計算過程説明書：crossed ladder 1図

#### 0. この資料の目的

2ループ電子頂点補正の crossed ladder 1図について、元の Feynman 図から $F_2(0)$ の解析係数へ到達する流れを、v0.90.0 の QEDCalc サンプルと対応させて説明する。元資料では Dirac/Lorentz 代数や多変数積分の長い途中式を保存したが、本資料ではそのうち機械的に再生成できる部分を QEDCalc へ委ねる。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **crossed ladder 1図** である。

本資料では各段階を次の3種類に区別する。

- **【人が決める】**：diagram の同定、Feynman gauge の採用、on-shell 条件、どの form factor を求めるか、どの変数変換を行うかなど、物理的意味を伴う選択。
- **【QEDCalc】**：LaTeX parse、Dirac 代数、loop shift、odd 項除去、tensor reduction、IBP、式の簡約、解析積分の機械的部分、residual の exact check など。
- **【接続】**：人が導出した式を QEDCalc の入力形式へ移す、または QEDCalc の出力を次の物理的段階へ解釈する部分。

重要なのは、QEDCalc は Feynman 図の意味を勝手に推測して全計算をブラックボックス処理するプログラムではないことである。**処理順序は人が決め、長大で機械的な代数を QEDCalc/SymPy に渡す**。QEDCalc の設計思想もこの分離にある。

#### 0.1 この資料の読み方

各計算段階では原則として次の順序で記載する。

1. なぜ次の処理が必要か。
2. 人が導出・選択しなければならない内容。
3. QEDCalc に渡す LaTeX または数式入力。
4. 実際のサンプルプログラムのファイル名と行番号。
5. QEDCalc の主要出力。
6. その出力を次の段階でどう使うか。

したがって、コードブロックだけを飛び飛びに読むのではなく、**「入力式がなぜその形になるか」→「コード」→「出力の物理的意味」**の順に読む。

#### 0.2 数式と規約

- 外部電子は on-shell とする。
- 電子質量を $m$ とする。
- 外部 photon momentum は $q=p'-p$ とする。
- anomalous magnetic moment は Pauli form factor $F_2(0)$ から得る。
- 必要な箇所では $D$ 次元を保持し、最後に $D\to4$ を取る。
- IR 正則化が必要な図では photon mass $\lambda$ と $\rho=\lambda/m$ を用いる。


#### 0.3 本資料での「人」と「QEDCalc」の受け渡しの書き方

この資料では、計算の各段階を単に「人が行う」「QEDCalc が行う」と分類するだけではなく、必ず次の受け渡しを明示する。

1. **前段階から入ってくる式・データ**：この段階を始める時点で何が既知なのか。
2. **人が用意する入力**：Feynman 図の読み取り、運動学、renormalization 条件、変数変換など、物理的・解析的判断を伴う部分。
3. **QEDCalc に実際に渡る入力**：LaTeX ファイル、SymPy 式、index table、parameter family など、プログラムが直接受け取るもの。
4. **サンプルコード**：QEDCalc v0.90.0 のどのファイルの何行が処理を行うか。
5. **QEDCalc の出力**：数式として何が得られ、どの residual / term count / table が検算されるか。
6. **次段階へ渡すもの**：得られた出力のうち、次の物理計算で実際に使用するもの。

したがって、関数が引数なしで呼ばれている場合も「入力なし」という意味ではない。関数内部で `input/*.tex` を読む場合、あるいは前段階で確定した topology・kinematics が関数内部に実装されている場合は、それを明示する。

また、長大な数十～数百項の多項式を QEDCalc が生成する場合、本資料ではその多項式を人が再び手計算することを目的としない。その場合でも、**何という多項式を生成したか、その数学的定義、項数、入力変数、次段階での使われ方**は必ず記載する。完全展開式は QEDCalc の生成物として再出力できる形を保つ。


#### 0.4 全工程の入出力一覧

| 工程 | 人が用意・判断するもの | QEDCalc に渡る入力 | QEDCalc の主な出力 | 次へ渡すもの |
|---|---|---|---|---|
| raw graph | crossed topology と非可換 electron-chain 順序 | `input/crossed_ladder_2loop_bare.tex` | ordered denominator family、scalar-product rules | crossed scalar family |
| magnetic projector | $F_2(0)$ projector の運動学と規格化 | parsed raw graph + projector convention | $\sum_j c_j(D,z)J_j$ の scalar-integral table | projected integral family |
| projective 化 | 6 physical denominators を parameter 化する方針 | denominator family | Symanzik/projective polynomials $U,F$ | projective integrand |
| triangular bridge | $h=(1-t)/t$, $R=q/t$ を選ぶ | projective kernel | Jacobian、log argument、domain residual $0$ | $0<t<q<1$ kernel |
| 1変数化 | 積分順序を選ぶ | triangular kernel | raw one-variable rational/log/dilog kernel | $\mathcal F_{\rm X}^{\rm raw}(q)$ |
| canonical reduction | total derivative を積分値に影響しない形で分離する | raw 1-variable kernel | canonical kernel + boundary term | endpoint-friendly kernel |
| endpoint evaluation | cutoff cancellation を分離して評価する | canonical kernel | half-sector、endpoint-sector、boundary cancellation | $A_{\rm X}$ |
| release checkpoint | corrected result と歴史的 $1/32$ provenance を区別 | analytic sector outputs | exact closure | crossed ladder 最終寄与 |

数学的な流れだけを書けば、

$$
\begin{aligned}
\mathcal I_{\rm X}^{\rm raw} \longrightarrow \mathcal P_{F_2}\mathcal I_{\rm X}^{\rm raw} \longrightarrow (U,F) \longrightarrow \mathcal F_{\rm X}^{\rm raw}(q) \longrightarrow \mathcal F_{\rm X}^{\rm canonical}(q) \longrightarrow \\
A_{\rm X}
\end{aligned}
$$

である。以下の各節では、この矢印1本ごとに「誰が何を準備し、QEDCalc が何を返すか」を詳しく説明する。

#### 1. 元の入力となる Feynman 図

##### 1.1 【人が決める】diagram から Feynman 則の式を作る

crossed ladder では、2本の内部 photon 線が電子線上で交差する。電子線に沿った Dirac 行列の順序は可換ではないので、**図を見て電子線上の頂点順序を確定すること**は人間側の仕事である。

Feynman gauge にすると、QEDCalc に保存されている raw input は次である。

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\mu \\
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\rho \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

この式で ordinary ladder と異なる重要点は、右端側の4本目の電子 propagator が $p-k$ ではなく $p-l$ を含むことである。したがって denominator family も ordinary ladder のものをそのまま流用してはいけない。

##### 1.2 【QEDCalc】raw LaTeX を parse し crossed 専用 family を作る

###### この段階へ入る入力

入力は前節に表示した complete crossed-ladder RHS で、QEDCalc では

`input/crossed_ladder_2loop_bare.tex`

に保存している。特に ordinary ladder と区別する情報は electron propagator の順序であり、右側の propagator が $p-l$ を含む点を失ってはいけない。

###### QEDCalc へ実際に渡す入力

```python
source = (ROOT/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')
parsed = parse_loop_integral_latex(source)
raw = analyze_raw_crossed_ladder(parsed)
```

である。`raw` は出力 object であり、入力式そのものではない。

###### QEDCalc の出力

QEDCalc は raw RHS を

$$
\begin{aligned}
\mathcal I_{\rm X}^{\rm raw} \longrightarrow \\
\left( \text{ordered electron denominators}, \text{crossed family index}, \text{scalar-product rules} \right)
\end{aligned}
$$

へ分解する。

その後 projector を作用させると、長大な Dirac/Lorentz numerator は scalar-integral monomial table に変わる。つまり出力の数学的意味は

$$
\mathcal P_{F_2}\mathcal I_{\rm X}^{\rm raw} =
\sum_j c_j(D,z)\,J_j(D,z)
$$

という scalar integral の線形結合である。

Phase 15 は raw LaTeX を直接読み、crossed ladder として electron denominator の並びを解析し、専用の scalar-product rules を作る。

**該当コード：`examples/phase15_crossed_raw_projector_trial.py` 11～16 行**

```python
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')
raw=analyze_raw_crossed_ladder(parse_loop_integral_latex(source))
result=crossed_general_q_projector_result(raw)
csv_path=write_ladder_general_q_integral_table_csv(result.integral_table,ROOT/'output'/'crossed_corrected_spin_sum_95_coefficients.csv')
rules=derive_crossed_scalar_product_rules_from_family()
```
QEDCalc の出力は、electron denominator labels、bare family index、crossed 専用 scalar-product rules、および corrected spin-sum projector から生成された scalar-integral monomial table である。

ここで QEDCalc が行っているのは「図を crossed ladder だと推測する」ことではない。**人が crossed ladder の正しい raw 式を与えた後、その非可換積と denominator 構造を機械的に分解する**。

#### 2. $F_2(0)$ を取り出す必要がある理由

##### 2.1 【人が決める】求める物理量

###### projector そのものの導出

crossed ladder でも物理的な抽出原理は corner と同じである。対称 Breit frame を取り、

$$
q^\mu=(0,q,0,0),
\qquad
p^\mu=\left(E,-\frac q2,0,0\right),
\qquad
p'^\mu=\left(E,+\frac q2,0,0\right)
$$

とすると、$q$ 一次まで

$$
\bar u(p')\Gamma_0u(p)=F_1(0)+O(q^2)
$$

$$
\bar u(p')\Gamma_2u(p) = -\frac{iq}{2m}[F_1(0)+F_2(0)]+O(q^2)
$$

である。したがって

$$
\boxed{
F_2(0) =
\lim_{q\to0}
\left[
\frac{2mi}{q}\bar u(p')\Gamma_2u(p) -
\bar u(p')\Gamma_0u(p)
\right]
}
$$

を使う。この式を元の crossed ladder integral の $\gamma_\mu$ に適用する、という判断が人側の仕事である。

renormalized electromagnetic vertex は

$$
\Gamma_\mu^{\mathrm R}(p',p) =
\gamma_\mu F_1(q^2) +
\frac{i\sigma_{\mu\nu}q^\nu}{2m}F_2(q^2)
$$

と分解する。異常磁気能率は $F_2(0)$ なので、元の巨大な vertex 全体ではなく Pauli 構造だけを抽出すればよい。

元の計算過程説明書では Breit frame で $\Gamma_0$ と $\Gamma_2$ を使う projector を導出している。ここで必要なのは、外部 spinor と $q$ の一次までの展開を使って $F_1$ 成分を消し $F_2$ 成分だけを残すことである。この projector の**物理的選択と規格化確認**は人が理解しておく必要があるが、trace 展開そのものは QEDCalc に任せられる。

##### 2.2 【QEDCalc】raw projector を生成する

###### 入力

入力は 1.2 で parse した `raw` object と、前節で確定した $D$ 次元 Pauli projector である。QEDCalc は electron chain の非可換順序を保ったまま gamma trace / spin sum を展開する。

###### 出力

出力 `result.integral_table` は、projector 後の式を

$$
F_{2,\rm X}^{\rm bare}(q^2) =
\sum_j c_j(D,z)J_j
$$

という scalar integral の表にしたものである。各行には denominator powers と係数が入り、元の数百項 gamma 代数はこの table に置き換わる。

Phase 15 の次の呼び出しが、raw crossed graph に projector を適用する部分である。

**該当コード：`examples/phase15_crossed_raw_projector_trial.py` 12～16 行**

```python
source=(ROOT/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')
raw=analyze_raw_crossed_ladder(parse_loop_integral_latex(source))
result=crossed_general_q_projector_result(raw)
csv_path=write_ladder_general_q_integral_table_csv(result.integral_table,ROOT/'output'/'crossed_corrected_spin_sum_95_coefficients.csv')
rules=derive_crossed_scalar_product_rules_from_family()
```
出力される integral table は、projector 後の長大な Dirac/Lorentz 代数を scalar integral の線形結合へ落としたものに相当する。元資料で数百項を目視する必要があった部分を、ここでは CSV と residual check に置き換えられる。

#### 3. denominator family から Feynman parameter 表示へ

##### 3.1 【人が決める】なぜ parameter 表示が必要か

2ループ積分を直接 $k,l$ で積分するのではなく、6本の物理 denominator を Feynman parameter でまとめ、二次形式を平方完成して loop momentum を消す。これは解析方針として人が選ぶ。

物理 denominator は、2本の photon と4本の electron propagator である。補助 denominator $H=-(k+l)^2$ は numerator scalar product を同じ family 内で表すために導入し、bare graph では指数0とする。

##### 3.2 【QEDCalc】Symanzik/projective polynomial を生成する

###### 入力

入力は projector 後の crossed scalar family と、6本の physical denominator $K,L,E_1,E_2,E_3,E_4$ の power である。補助 denominator $H$ は numerator bookkeeping 用なので bare graph では power 0 とする。

###### 出力

QEDCalc は Feynman parameters を導入し、2-loop quadratic form から projective polynomials

$$
U(\alpha_i),
\qquad
F(\alpha_i; q^2,m^2)
$$

を生成する。さらに total degree と homogeneity を検査する。次段階へ渡すのは、loop momenta を消去した projective integrand の denominator backbone である。

**該当コード：`examples/phase18_crossed_parametric_bridge_trial.py` 8～22 行**

```python
ROOT = Path(__file__).resolve().parents[1]
D,z,m2 = sp.symbols('D z m2')
rep = crossed_bare_scalar_parametric_representation(D,z,m2)
checks = crossed_bare_scalar_parametric_checks(D,z,m2)

out = ROOT/'output'/'phase18_crossed_parametric_bridge_trial.md'
lines = [
    '# Phase 18: crossed-ladder raw scalar-family to projective bridge','',
    'The six physical crossed denominators K,L,E1,E2,E3,E4 are taken directly from the generic crossed IBP family. H=-(k+l)^2 is auxiliary and has power zero.','',
    f'Active denominators: `{rep.active_denominators}`','',
    f'U total degree: **{checks["U_total_degree"]}**; homogeneous: **{checks["U_homogeneous"]}**.','',
    f'F total degree: **{checks["F_total_degree"]}**; homogeneous: **{checks["F_homogeneous"]}**.','',
    '## U','', '$$
', sp.latex(rep.U), '
$$','',
    '## F','', '$$
', sp.latex(rep.F), '
$$','',
    'This bridge is denominator-level. The remaining raw-to-projective gap is the projected numerator polynomial and its reduction to the hand-audited V-partial-fraction kernel.',''
```
ここで出力される $U$ と $F$ は homogeneous であることも検査される。これにより、元資料で手計算していた denominator の平方完成・projective 化の機械部分を再生成できる。

#### 4. 多変数積分を三角領域へ変換する

##### 4.1 【人が決める】変数変換の目的

projective 表示のままでは多変数積分が長い。元の導出では $V$ を先に積分し、さらに $h$ と $R$ を

$$
h=\frac{1-t}{t},\qquad R=\frac{q}{t}
$$

と変換することで領域を

$$
0<t<q<1
$$

へ変える。この変数変換を採用する理由は、残った積分が rational/log/dilog の1変数 kernel へ縮約しやすくなるためである。

##### 4.2 【QEDCalc】Jacobian と logarithm argument を exact check する

###### 入力

入力は projective 表示から $V$ を先に積分した kernel と、人が選んだ

$$
h=\frac{1-t}{t},
\qquad
R=\frac{q}{t}
$$

という変数変換である。

###### 出力

QEDCalc は変換 Jacobian、積分領域 $0<t<q<1$、logarithm argument を symbolic に再計算し、手導出との差を residual として返す。`jacobian_difference=0`、`log_argument_difference=0` がこの段階の合格条件である。

**該当コード：`examples/phase23_crossed_u_tq_bridge_trial.py` 7～26 行**

```python
ROOT = Path(__file__).resolve().parents[1]
u = crossed_h_u_integrated_kernel_checks()
tq = crossed_tq_preintegration_checks()
assert u["upper_endpoint_S"] == 1
assert tq["jacobian_difference"] == 0
assert tq["log_argument_difference"] == 0

lines = [
    "# Phase 23: crossed-ladder analytic U integration and triangular bridge", "",
    "After V integration use h=S(R+U)-1. The original S>=1 domain gives", "",
    "$$
", r"0\le U\le h-R+1.", "
$$", "",
    "With Y=R+U, every generated U integrand is polynomial(Y)/Y^p, so the U integral is evaluated exactly by monomial primitives and log((h+1)/R).", "",
    "After", "",
    "$$
", r"h=\frac{1-t}{t},\qquad R=\frac{q}{t},", "
$$", "",
    "the Jacobian is 1/t^3 and the domain becomes", "",
    "$$
", r"0<t<q<1.", "
$$", "",
    "The generated logarithm argument is", "",
    "$$
", r"\frac{q^2+(1-2q)t}{q^2(1-t)}.", "
$$", "",
    f"U-integrated component operation counts: `{u['component_operation_counts']}`", "",
    f"(t,q) component operation counts: `{tq['component_operation_counts']}`", "",
```
主要な出力は Jacobian $1/t^3$ と logarithm argument

$$
\frac{q^2+(1-2q)t}{q^2(1-t)}
$$

である。ここまで来れば、元資料の長い変数変換の代数確認を人が繰り返す必要はない。

#### 5. $t$ 積分から raw 1変数 kernel を作る

##### 5.1 【QEDCalc】cutoff を残して rational/log sector を合成する

###### 入力

入力は三角領域 $0<t<q<1$ の2変数 kernel である。endpoint singularity を途中で失わないよう、必要な cutoff を残したまま $t$ 積分を行う。

###### 出力

QEDCalc は

$$
\mathcal F_{\rm X}^{\rm raw}(q) =
R(q)+L(q)\ln q+M(q)\ln(1-q)+D(q)\,\Phi(q)
$$

のような rational/log/dilog からなる1変数 kernel を返す。ここで $D(q)$ は dilogarithm combination である。次段階ではこの raw kernel を total derivative と canonical kernel に分解する。

endpoint を別々に積分すると見かけの $\ln\varepsilon$ が現れるので、cutoff を最後まで保持して sector を合成する必要がある。Phase 24 はこれを自動で行う。

**該当コード：`examples/phase24_crossed_raw_q_kernel_trial.py` 7～26 行**

```python
ROOT = Path(__file__).resolve().parents[1]
checks = crossed_raw_one_variable_kernel_checks()
difference = crossed_raw_to_canonical_difference()
assert checks["cutoff_log_coefficient"] == 0
assert checks["unexpected_polylogs"] == ()
assert difference == 0

lines = [
    "# Phase 24: crossed-ladder raw one-variable kernel regeneration", "",
    "The t integral is generated directly from the Phase-23 triangular kernel.", "",
    "A lower cutoff epsilon is retained until the rational and logarithmic sectors are combined. Its logarithmic coefficient cancels exactly:", "",
    "$$
", r"C_{\ln\varepsilon}=0.", "
$$", "",
    "The resulting one-variable kernel closes on", "",
    "$$
", r"1,\quad L,\quad M,\quad L^2,\quad LM,\quad D(q),", "
$$", "",
    r"with $L=\ln q$, $M=\ln(1-q)$ and $D(q)=\operatorname{Li}_2(q)-\operatorname{Li}_2(2-1/q)$.", "",
    "Using the audited total-derivative primitive G(q), the exact symbolic check gives", "",
    "$$
", r"\mathcal F_{\rm raw}(q)-\frac{d\mathcal G}{dq}-\mathcal F_{\rm can}(q)=0.", "
$$", "",
    f"Raw-kernel operation count: **{checks['operation_count']}**.", "",
]
(ROOT / "output" / "phase24_crossed_raw_q_kernel_trial.md").write_text("\n".join(lines), encoding="utf-8")
```
QEDCalc は

$$
C_{\ln\varepsilon}=0
$$

を exact に確認し、raw kernel が

$$
1,\quad L,\quad M,\quad L^2,\quad LM,\quad D(q)
$$

の basis に閉じることを確認する。ここで $L=\ln q$、$M=\ln(1-q)$、$D(q)=\operatorname{Li}_2(q)-\operatorname{Li}_2(2-1/q)$ である。

#### 6. raw kernel を canonical kernel へ縮約する

##### 6.1 【QEDCalc】Hermite/total derivative reduction

###### 入力

入力は前節の raw one-variable kernel $\mathcal F_{\rm X}^{\rm raw}(q)$ である。

###### 出力

QEDCalc は rational part に Hermite reduction を施し、

$$
\mathcal F_{\rm X}^{\rm raw}(q) =
\mathcal F_{\rm X}^{\rm canonical}(q) +
\frac{d}{dq}B(q)
$$

という形にする。`B(q)` は boundary term として保持し、捨てない。これにより endpoint singular terms がどこへ移ったかを追跡できる。

raw kernel の rational part には total derivative に移せる成分がある。これを人が項ごとに探す代わりに Phase 25 が自動生成する。

**該当コード：`examples/phase25_crossed_automatic_hermite_trial.py` 4～24 行**

```python
ROOT = Path(__file__).resolve().parents[1]
c = crossed_automatic_hermite_checks()
assert c["G_difference"] == 0
assert c["canonical_difference"] == 0
assert c["raw_reconstruction_difference"] == 0

lines = [
    "# Phase 25: automatic crossed-ladder Hermite reduction", "",
    "The raw one-variable kernel is reduced without using a stored R,T,U,V,P,Q,Z table.", "",
    "The generated total-derivative coefficients are:", "",
]
for name in ("R", "T", "U", "V", "P", "Q", "Z"):
    lines += [f"## {name}(q)", "", "$$
", str(c[name]), "
$$", ""]
lines += [
    "The automatically generated primitive agrees with the audited primitive exactly,", "",
    "$$
", r"\mathcal G_{\rm auto}(q)-\mathcal G_{\rm audited}(q)=0.", "
$$", "",
    "The square-free remainder agrees with the audited canonical kernel exactly,", "",
    "$$
", r"\mathcal F_{\rm can,auto}(q)-\mathcal F_{\rm can,audited}(q)=0.", "
$$", "",
    "Finally,", "",
    "$$
", r"\mathcal F_{\rm raw}(q)-\frac{d\mathcal G_{\rm auto}}{dq}-\mathcal F_{\rm can,auto}(q)=0.", "
$$", "",
]
```
重要な出力は

$$
\mathcal F_{\rm raw}(q) -
\frac{d\mathcal G_{\rm auto}}{dq} -
\mathcal F_{\rm can,auto}(q) =0
$$

である。これは canonical kernel が「既知の最終値から逆算された式」ではなく raw kernel から機械的に再構成されたことを示す。

#### 7. canonical 1変数積分を解析する

##### 7.1 【人が決める】endpoint を分ける理由

$q=1/2$ を境に dilogarithm の実数表示や endpoint の扱いが変わるので、元資料では half sector と endpoint sector に分けている。これは branch と収束性を意識した解析上の選択である。

##### 7.2 【QEDCalc】sector の解析値と boundary cancellation を組み立てる

###### 入力

入力は canonical kernel、total-derivative boundary term、および人が決めた endpoint sector 分割である。

###### 出力

QEDCalc は $q=1/2$ 側の finite sector、$q\to0,1$ の endpoint sector、boundary contribution を別々に解析し、cutoff logarithms の係数が合計0になることを確認する。最後に

$$
A_{\rm X} =
\frac16 +
\frac{13\pi^2}{36} +
\frac54\zeta(3) -
\frac{5\pi^2}{6}\ln2
$$

を返す。

メイン trial の次の部分が、canonical kernel から各 sector を評価し最終値を組み立てる。

**該当コード：`examples/crossed_ladder_2loop_trial.py` 38～56 行**

```python
s.equation("Canonical one-variable kernel", sp.latex(crossed_canonical_kernel(q)))
s.equation("Dilogarithm reflection sum", sp.latex(crossed_dilog_reflection_sum(q)))

half = crossed_half_sector_result()
endfinite = crossed_endpoint_finite_result()
asym = crossed_endpoint_asymptotics()
endtotal = crossed_endpoint_total_result()
final = crossed_final_result()
expected = crossed_expected_result()

s.equation("q=1/2 sector", sp.latex(half))
s.equation("Endpoint canonical finite part", sp.latex(endfinite))
s.equation("Endpoint boundary finite part", sp.latex(asym.finite_boundary))
s.equation("Endpoint total", sp.latex(endtotal))
s.equation("Endpoint divergent-log cancellation", sp.latex(asym.divergent_sum))
s.equation("Crossed-ladder final coefficient", sp.latex(final))
s.equation("Independent closed-form checkpoint", sp.latex(expected))
s.equation("Difference", sp.latex(sp.simplify(final-expected)))
s.text("Result", "PASS: the analytic crossed-ladder coefficient matches the independent derivation.")
```
さらに Phase 26 は final closed form を入力として使わず、再生成した canonical standard integrals と endpoint boundary term から最終値を組み立てる。

**該当コード：`examples/phase26_crossed_independent_analytic_trial.py` 6～20 行**

```python
checks = crossed_independent_analytic_checks()
assert checks["divergent_sum"] == 0
assert checks["checkpoint_difference"] == 0

out = Path(__file__).resolve().parents[1] / "output" / "phase26_crossed_independent_analytic_trial.md"
lines = [
    "# Phase 26: crossed-ladder independent analytic evaluation", "",
    "The final analytic constant is assembled from the regenerated canonical kernel.",
    "The final closed-form checkpoint is used only after the derivation as a regression comparison.", "",
]
for key in ["A","B","C","half","endpoint_canonical_finite","boundary_finite","endpoint_total","divergent_sum","final","checkpoint_difference"]:
    lines += [f"## {key}", "", "$$
", sp.latex(checks[key]), "
$$", ""]
lines += ["## Result", "", "PASS: canonical standard integrals, endpoint finite part, automatic boundary term, and the final crossed-ladder constant are independently regenerated.", ""]
out.write_text("\n".join(lines), encoding="utf-8")
print("Phase-26 crossed independent analytic evaluation: PASS")
```
最終係数は

$$
A_{\mathrm X} =
\frac16 +
\frac{13\pi^2}{36} +
\frac54\zeta(3) -
\frac{5\pi^2}{6}\ln2
$$

である。

#### 8. release checkpoint

Phase 78 では projector normalization、endpoint divergent-log cancellation、final closed form を高速に exact check する。

**該当コード：`examples/phase78_crossed_end_to_end_checkpoint.py` 3～29 行**

```python
from qedcalc.operations.crossed_ladder import crossed_phase78_end_to_end_checkpoint

c = crossed_phase78_end_to_end_checkpoint()
for key in (
    "projector_residual_F1", "projector_residual_F2",
    "endpoint_divergent_residual", "final_closed_form_residual",
):
    assert sp.simplify(c[key]) == 0, (key, c[key])

out = Path(__file__).resolve().parents[1] / "output" / "phase78_crossed_end_to_end_checkpoint.md"
lines = [
    "# Phase 78: crossed-ladder end-to-end closure checkpoint", "",
    "The release-validation path checks the exact modern-route invariants without the expensive full raw-q-kernel regeneration.", "",
]
for key in (
    "projector_F1_coefficient", "projector_F2_coefficient",
    "endpoint_divergent_residual", "half_sector", "endpoint_total",
    "final", "closed_form", "final_closed_form_residual",
    "historical_karplus_kroll_gap",
):
    lines += [f"## {key}", "", "$$
", sp.latex(c[key]), "
$$", ""]
lines += [
    "## Heavy raw regeneration", "",
    "The existing raw-one-variable-kernel to automatic-Hermite/canonical residual audit remains available separately because rebuilding it is intentionally excluded from the fast release validation.", "",
    "## Historical 1/32 status", "",
    "The magnitude 1/32 is retained as a historical audit target only. Its precise location in the 1950 Karplus--Kroll algebra is not claimed to be resolved by this checkpoint.", "",
    "## Result", "", "PASS: projector normalization, endpoint cancellation, and final analytic assembly close exactly.", "",
```
したがって普段の再実行では Phase 78 を回せばよく、raw kernel まで再検証したいときだけ Phase 15～26 を順に使う。

#### 9. 現在の自動化境界

| 段階 | 状況 | 担当 |
|---|---|---|
| Feynman 図から正しい非可換順序の raw 式を作る | 人が確認 | 人 |
| raw LaTeX parse / crossed family | 自動 | QEDCalc |
| projector の物理的意味・規格化方針 | 人が理解 | 人 |
| corrected projector の Dirac/Lorentz 展開 | 自動 | QEDCalc |
| projective $U,F$ | 自動 | QEDCalc |
| 解析に有利な変数変換の採用 | 人が選択 | 人 |
| $U,V,t$ 等の機械積分・Jacobian 検算 | 自動 | QEDCalc |
| raw→canonical Hermite reduction | 自動 | QEDCalc |
| endpoint 分割の意味 | 人が理解 | 人 |
| sector 解析と final residual | 自動 | QEDCalc |

#### 10. 最短再計算手順

1. `input/crossed_ladder_2loop_bare.tex` を確認する。
2. Phase 15 で raw projector/family を再生成する。
3. Phase 18～24 で parameter bridge と raw one-variable kernel を再生成する。
4. Phase 25 で canonical reduction を exact check する。
5. Phase 26 で解析積分を再構成する。
6. 通常の regression は Phase 78 または `run_v090_validation.bat` で確認する。

#### 11. 歴史的 $1/32$ について

Karplus--Kroll 1950 の旧結果との差 $1/32$ は、**現代的 crossed ladder の最終値の未確定性ではない**。QEDCalc の current route は上記の独立経路で corrected value に exact に閉じている。未解決なのは、1950年の手計算のどの局所操作で $1/32$ が失われたかという provenance だけである。

#### 12. この資料で省略できた手計算

元の計算過程説明書に必要だった、数百項の Dirac 展開、scalar-product 置換、Jacobian の展開、cutoff log の係数比較、Hermite reduction の係数決定、最終 residual の照合は、現在は QEDCalc の再実行結果として確認できる。そのため本資料ではそれらの**全項展開そのもの**は掲載せず、入力・処理・出力の意味を残す。

#### 13. 参照元と再実行ファイル

本資料は主として次を対応付けて再構成した。

- 元計算資料：`crossed_ladder_F2_4/crossed_ladder_Feynman図から最終結果_統合版_全体見直し修正版.md`
- 詳細別冊：`crossed_ladder_F2_4/crossed_ladder_計算詳細別冊_全体見直し修正版.md`
- raw input：`input/crossed_ladder_2loop_bare.tex`
- main sample：`examples/crossed_ladder_2loop_trial.py`
- raw/projector：Phase 15
- projective bridge：Phase 18
- triangular bridge：Phase 23
- raw 1-variable kernel：Phase 24
- automatic Hermite reduction：Phase 25
- independent analytic evaluation：Phase 26
- release closure：Phase 78

代表的な実行バッチは `run_crossed_ladder_2loop_demo.bat` と `run_phase78_crossed_end_to_end_checkpoint.bat` である。全7図を含む regression は `run_v090_validation.bat` を使う。


---

#### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

## 3. Recorded runtime artifacts

| Artifact | Type | Lines | Bytes |
| --- | --- | ---: | ---: |
| `output/crossed_ladder_2loop_trial.md` | `md` | 111 | 2461 |
| `output/phase15_crossed_raw_projector_trial.md` | `md` | 45 | 942 |
| `output/phase16_crossed_ibp_baseline_trial.md` | `md` | 14 | 691 |
| `output/phase18_crossed_parametric_bridge_trial.md` | `md` | 23 | 1505 |
| `output/phase19_crossed_symmetry_baseline_trial.md` | `md` | 12 | 617 |
| `output/phase20_crossed_degree2_master_audit.md` | `md` | 8 | 555 |
| `output/phase20_crossed_qlinear_bridge_trial.md` | `md` | 47 | 1295 |
| `output/phase21_crossed_px_generation_trial.md` | `md` | 34 | 1200 |
| `output/phase22_crossed_v_bridge_trial.md` | `md` | 19 | 474 |
| `output/phase23_crossed_u_tq_bridge_trial.md` | `md` | 31 | 616 |
| `output/phase24_crossed_raw_q_kernel_trial.md` | `md` | 25 | 701 |
| `output/phase25_crossed_automatic_hermite_trial.md` | `md` | 65 | 1051 |
| `output/phase26_crossed_independent_analytic_trial.md` | `md` | 68 | 1122 |
| `output/phase78_crossed_end_to_end_checkpoint.md` | `md` | 69 | 1406 |
| `output/crossed_corrected_spin_sum_95_coefficients.csv` | `csv` | 96 | 8301 |
| `output/crossed_PX_generated.txt` | `txt` | 1 | 4628 |
| `output/crossed_PX_projective_generated.txt` | `txt` | 1 | 3603 |
| `output/crossed_phase17_first_neighbor_audit.csv` | `csv` | 21 | 646 |
| `output/crossed_phase19_remaining_target_local_audit.csv` | `csv` | 13 | 404 |
| `output/crossed_phase20_directional_depth2.csv` | `csv` | 13 | 391 |
| `output/crossed_phase20_mixed_degree2.csv` | `csv` | 13 | 403 |

## 4. Recorded Markdown stages

### 4.1 `output/crossed_ladder_2loop_trial.md`

### QEDCalc crossed-ladder two-loop trial

Generated: 2026-08-22T10:14:03

#### Scope

This trial starts from the independently derived projective/one-variable representation of the crossed-ladder graph. The raw several-hundred-term Dirac reduction is not yet regenerated automatically.

#### Projective Delta

$$
R S + R V + S U + U V - 1
$$

#### Projective W

$$
R^{2} S + R^{2} V + R S^{2} - 2 R S + S^{2} U
$$

#### Linearity check

degree_V(Delta)=1, degree_V(W)=1

#### h transformation

$$
\frac{1 - t}{t}
$$

#### R transformation

$$
\frac{q}{t}
$$

#### Jacobian

$$
\frac{1}{t^{3}}
$$

#### Reduced logarithm argument

$$
- \frac{q^{2} - 2 q t + t}{q^{2} \left(t - 1\right)}
$$

#### Canonical one-variable kernel

$$
\frac{\begin{gathered}
64 q \left(q - 1\right) \left(\log{\left(q \right)} - \log{\left(1 - q \right)}\right) \left(5 \log{\left(q \right)} + 6\right) {}+ \\
q \left(2 q - 1\right) \left(- 80 \log{\left(q \right)}^{2} + 80 \log{\left(q \right)} + 80 \operatorname{Li}_{2}\left(q\right) - 80 \operatorname{Li}_{2}\left(\frac{2 q - 1}{q}\right) - 41\right) {}+ \\
\left(q - 1\right) \left(2 q - 1\right) \\
\left(- 80 \log{\left(q \right)}^{2} + 160 \log{\left(q \right)} \log{\left(1 - q \right)} - 224 \log{\left(q \right)} + 384 \log{\left(1 - q \right)} - 80 \operatorname{Li}_{2}\left(q\right) + 80 \operatorname{Li}_{2}\left(\frac{2 q - 1}{q}\right) - 271\right)
\end{gathered}}{96 q \left(q - 1\right) \left(2 q - 1\right)}
$$

#### Dilogarithm reflection sum

$$
\frac{\log{\left(q \right)}^{2}}{2} - 2 \log{\left(q \right)} \log{\left(1 - q \right)} + \frac{\log{\left(1 - q \right)}^{2}}{2} + \frac{\pi^{2}}{6}
$$

#### q=1/2 sector

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} - \frac{35 \zeta\left(3\right)}{12} + \pi^{2}
$$

#### Endpoint canonical finite part

$$
- \frac{19 \pi^{2}}{36} + \frac{25 \zeta\left(3\right)}{6}
$$

#### Endpoint boundary finite part

$$
\frac{1}{6} - \frac{\pi^{2}}{9}
$$

#### Endpoint total

$$
- \frac{23 \pi^{2}}{36} + \frac{1}{6} + \frac{25 \zeta\left(3\right)}{6}
$$

#### Endpoint divergent-log cancellation

$$
0
$$

#### Crossed-ladder final coefficient

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

#### Independent closed-form checkpoint

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

#### Difference

$$
0
$$

#### Result

PASS: the analytic crossed-ladder coefficient matches the independent derivation.

---

### 4.2 `output/phase15_crossed_raw_projector_trial.md`

### Phase 15: crossed-ladder raw corrected-projector bridge

The complete bare crossed-ladder LaTeX input is parsed directly. The fourth electron denominator is p-l, not p-k, so a dedicated scalar-product basis is derived rather than reusing the ordinary-ladder family.

Electron labels: `('E1', 'E2', 'E3', 'E4')`

Bare family index: `(1, 1, 0, 1, 1, 1, 1)`

#### Derived scalar-product rules

$$
k_{2}=- K
$$

$$
l_{2}=- L
$$

$$
kl=- \frac{H}{2} + \frac{K}{2} + \frac{L}{2}
$$

$$
kpp=\frac{E_{1}}{2} - \frac{K}{2}
$$

$$
kp=\frac{E_{3}}{2} - \frac{E_{4}}{2} - \frac{H}{2} + \frac{L}{2}
$$

$$
lpp=- \frac{E_{1}}{2} + \frac{E_{2}}{2} - \frac{H}{2} + \frac{K}{2}
$$

$$
lp=\frac{E_{4}}{2} - \frac{L}{2}
$$

#### Corrected spin-sum projector

Generated scalar-integral monomials: **95**.

CSV: `output/crossed_corrected_spin_sum_95_coefficients.csv`

The next stage is crossed-family symmetry/zero-sector analysis and bounded IBP/Laporta closure.

---

### 4.3 `output/phase16_crossed_ibp_baseline_trial.md`

### Phase 16: crossed-ladder bounded IBP baseline

The 95 corrected crossed-ladder projector targets are used directly as a bounded seed set at one exact-rational generic probe. No floating-point rank test is used.

Probe: `$D=37/10$, $z=2/5$, $m^2=1$`.

- Projector targets: **95**
- IBP equations after zero-sector pruning: **760**
- Laporta pivots: **755**
- Projector targets already pivoted: **75**
- Projector targets not yet pivoted: **20**
- Direct terminal RHS integrals in this bounded system: **416**

This is a baseline diagnostic, not a completed reduction. The next phase should rank terminal residues by blocked-target impact and expand only the highest-impact crossed sectors.

---

### 4.4 `output/phase18_crossed_parametric_bridge_trial.md`

### Phase 18: crossed-ladder raw scalar-family to projective bridge

The six physical crossed denominators K,L,E1,E2,E3,E4 are taken directly from the generic crossed IBP family. H=-(k+l)^2 is auxiliary and has power zero.

Active denominators: `('K', 'L', 'E1', 'E2', 'E3', 'E4')`

U total degree: **2**; homogeneous: **True**.

F total degree: **3**; homogeneous: **True**.

#### U

$$
\begin{aligned}
cx_{1} cx_{2} + cx_{1} cx_{4} + cx_{1} cx_{5} + cx_{1} cx_{6} + cx_{2} cx_{3} + cx_{2} cx_{4} + cx_{2} cx_{5} {}+ \\
cx_{3} cx_{4} + cx_{3} cx_{5} + cx_{3} cx_{6} + cx_{4} cx_{6} + cx_{5} cx_{6}
\end{aligned}
$$

#### F

$$
- m_{2} \left(\begin{aligned}
- cx_{1} cx_{4}^{2} + cx_{1} cx_{4} cx_{5} z - 2 cx_{1} cx_{4} cx_{5} + cx_{1} cx_{4} cx_{6} z - 2 cx_{1} cx_{4} cx_{6} {}- \\
cx_{1} cx_{5}^{2} - 2 cx_{1} cx_{5} cx_{6} - cx_{1} cx_{6}^{2} - cx_{2} cx_{3}^{2} - 2 cx_{2} cx_{3} cx_{4} {}+ \\
cx_{2} cx_{3} cx_{5} z - 2 cx_{2} cx_{3} cx_{5} - cx_{2} cx_{4}^{2} + cx_{2} cx_{4} cx_{5} z - 2 cx_{2} cx_{4} cx_{5} {}- \\
cx_{2} cx_{5}^{2} - cx_{3}^{2} cx_{4} - cx_{3}^{2} cx_{5} - cx_{3}^{2} cx_{6} - cx_{3} cx_{4}^{2} + cx_{3} cx_{4} cx_{5} z {}- \\
2 cx_{3} cx_{4} cx_{5} - 2 cx_{3} cx_{4} cx_{6} - cx_{3} cx_{5}^{2} - 2 cx_{3} cx_{5} cx_{6} - cx_{3} cx_{6}^{2} {}- \\
cx_{4}^{2} cx_{6} + cx_{4} cx_{5} cx_{6} z - 2 cx_{4} cx_{5} cx_{6} - cx_{4} cx_{6}^{2} - cx_{5}^{2} cx_{6} - cx_{5} cx_{6}^{2}
\end{aligned}\right)
$$

This bridge is denominator-level. The remaining raw-to-projective gap is the projected numerator polynomial and its reduction to the hand-audited V-partial-fraction kernel.

---

### 4.5 `output/phase19_crossed_symmetry_baseline_trial.md`

### Phase 19: crossed-ladder symmetry-reduced IBP baseline

- Raw corrected projector targets: **95**
- Symmetry-canonical targets: **52**
- IBP rows after symmetry and zero-sector pruning: **416**
- Laporta pivots: **378**
- Canonical targets pivoted: **40**
- Canonical targets not pivoted: **12**

- Remaining targets with a pivoting first-neighbor seed: **0 / 12**

The crossed graph-reversal symmetry substantially reduces the bounded system. The twelve remaining targets are locally irreducible in the first neighborhood at the exact-rational probe; degree-2 or z=0-specialized reduction is the next bounded step.

---

### 4.6 `output/phase20_crossed_degree2_master_audit.md`

### Phase 20: crossed-ladder bounded degree-2 master-candidate audit

- Symmetry-canonical projector targets: **52**
- Remaining non-pivot targets entering the audit: **12**
- Targets pivoting in directional depth-2: **0 / 12**
- Targets pivoting in mixed Cartesian degree-2: **0 / 12**

Together with the Phase-19 first-neighbor audit, this exhausts the full bounded Cartesian degree-2 neighborhood of the twelve remaining target integrals at the primary exact-rational probe. Absence of a pivot is strong bounded evidence, not a global master-count proof.

---

### 4.7 `output/phase20_crossed_qlinear_bridge_trial.md`

### Phase 20: crossed-ladder q-linear magnetic-projector bridge

The raw crossed numerator is rewritten with p' = p + q and truncated at first order before the magnetic projector is assembled.

q^0 Dirac-chain terms: **144**.

q^1 Dirac-chain terms: **84** (=48+36).

Total through O(q): **228**.

#### q=0 five-denominator Feynman-parameter bridge

At q=0 the two central electron denominators coincide.  The scalar core is therefore K L Dk Dkl^2 Dl and the parameter powers are (1,1,1,2,1).

$$
a=x+y+u,\qquad b=y+z+v,\qquad c=y,\qquad r=x+y,\qquad s=y+z
$$

Automatically generated U:

$$
u v + u y + u z + v x + v y + x y + x z + y z
$$

Automatically generated F at rho=0:

$$
\begin{aligned}
u y^{2} + 2 u y z + u z^{2} + v x^{2} + 2 v x y + v y^{2} {}+ \\
x^{2} y + x^{2} z + x y^{2} + 2 x y z + x z^{2} {}+ \\
y^{2} z + y z^{2}
\end{aligned}
$$

Feynman-parameter numerator monomial: `$y` (expected y).

Exact checks: U-Delta = 0, F-W = 0, measure-y = 0.

#### Breit-frame projector normalization

F1 coefficient: **0**; F2 coefficient: **1**.

#### q-linear denominator correction

$$
2 SP^{k q} x + SP^{k q} y + SP^{l q} y
$$

This reproduces delta D = 2 x k.q + y (k+l).q.

The remaining gap to P_X is now isolated to external-spinor O(q), the 84 q-linear numerator chains, loop shifts/tensor reduction, and Gaussian recombination.

---

### 4.8 `output/phase21_crossed_px_generation_trial.md`

### Phase 21: automatic crossed-ladder P_X generation

The long projective numerator is reconstructed from the raw crossed Dirac chain; no stored P_X table is read.

#### Streaming route

1. Differentiate the two p'=p+q electron numerators before distributing the Dirac chain.
2. Apply the Breit magnetic projector at O(q).
3. Include the q-linear denominator correction D^-6 -> D^-6 - 6 deltaD D^-7.
4. Wick rotate and square-complete both loop momenta.
5. Reduce centered monomials by bivariate Gaussian/Wick moments term by term.
6. Collect only by powers of Delta and W, then form the common denominator.

P_X monomials: **244**.

Total degree: **8**; homogeneous: **True**.

Projective P_X monomials after scale removal: **227**.

#### Exact checks

Apparent Gamma(0) coefficient after the full sum: **0**.

Graph-reversal difference x<->z, u<->v: **0**.

deg_V(projective P_X) = **4**. Since Delta^4 W^2 has V-degree 6, the V-integrand is O(V^-2); the logarithmic 1/V coefficient therefore vanishes.

The generated integrand is

$$
G_{\mathrm X}=\frac{yP_{\mathrm X}}{4\Delta^4W^2}.
$$

The complete 244-term polynomial is written to output/crossed_PX_generated.txt rather than expanded inline here.

---

### 4.9 `output/phase22_crossed_v_bridge_trial.md`

### Phase 22: crossed-ladder V partial-fraction bridge

The six coefficients A4,A3,A2,A1,B2,B1 are generated by coefficient comparison rather than a general apart() call.

Exact rational sample reconstruction checks: **PASS**.

The simple-pole logarithmic coefficient is

$$
\frac{A_1}{R+U}+\frac{B_1}{R^2}=0.
$$

After h=S(R+U)-1, the generated logarithm argument is

$$
\frac{(h+1)\left[h+(R-1)^2\right]}{hR^2}.
$$

This matches the independent detailed derivation exactly.

---

### 4.10 `output/phase23_crossed_u_tq_bridge_trial.md`

### Phase 23: crossed-ladder analytic U integration and triangular bridge

After V integration use h=S(R+U)-1. The original S>=1 domain gives

$$
0\le U\le h-R+1.
$$

With Y=R+U, every generated U integrand is polynomial(Y)/Y^p, so the U integral is evaluated exactly by monomial primitives and log((h+1)/R).

After

$$
h=\frac{1-t}{t},\qquad R=\frac{q}{t},
$$

the Jacobian is 1/t^3 and the domain becomes

$$
0<t<q<1.
$$

The generated logarithm argument is

$$
\frac{q^2+(1-2q)t}{q^2(1-t)}.
$$

U-integrated component operation counts: `(286, 195, 100, 105)`

(t,q) component operation counts: `(263, 243, 72, 63)`

---

### 4.11 `output/phase24_crossed_raw_q_kernel_trial.md`

### Phase 24: crossed-ladder raw one-variable kernel regeneration

The t integral is generated directly from the Phase-23 triangular kernel.

A lower cutoff epsilon is retained until the rational and logarithmic sectors are combined. Its logarithmic coefficient cancels exactly:

$$
C_{\ln\varepsilon}=0.
$$

The resulting one-variable kernel closes on

$$
1,\quad L,\quad M,\quad L^2,\quad LM,\quad D(q),
$$

with $L=\ln q$, $M=\ln(1-q)$ and $D(q)=\operatorname{Li}_2(q)-\operatorname{Li}_2(2-1/q)$.

Using the audited total-derivative primitive G(q), the exact symbolic check gives

$$
\mathcal F_{\rm raw}(q)-\frac{d\mathcal G}{dq}-\mathcal F_{\rm can}(q)=0.
$$

Raw-kernel operation count: **269**.

---

### 4.12 `output/phase25_crossed_automatic_hermite_trial.md`

### Phase 25: automatic crossed-ladder Hermite reduction

The raw one-variable kernel is reduced without using a stored R,T,U,V,P,Q,Z table.

The generated total-derivative coefficients are:

#### R(q)

$$
3/(4*(q - 1)) + 17/(4*(q - 1)**2) + 35/(12*(q - 1)**3) + 1/(4*(q - 1)**4)
$$

#### T(q)

$$
-5/(12*(q - 1)) + 4/(3*(q - 1)**2) + 13/(12*(q - 1)**3)
$$

#### U(q)

$$
7/(4*(q - 1)) + 31/(6*(q - 1)**2) + 31/(12*(q - 1)**3)
$$

#### V(q)

$$
29/(12*(q - 1)) + 1/(4*(q - 1)**2)
$$

#### P(q)

$$
3/(32*(2*q - 1)) - 27/(4*(q - 1)) - 23/(6*(q - 1)**2)
$$

#### Q(q)

$$
-q/4 - 3/(32*(2*q - 1)) + 13/(12*(q - 1)) - 1/(16*q)
$$

#### Z(q)

$$
9*q/16 + 5/(4*(q - 1))
$$

The automatically generated primitive agrees with the audited primitive exactly,

$$
\mathcal G_{\rm auto}(q)-\mathcal G_{\rm audited}(q)=0.
$$

The square-free remainder agrees with the audited canonical kernel exactly,

$$
\mathcal F_{\rm can,auto}(q)-\mathcal F_{\rm can,audited}(q)=0.
$$

Finally,

$$
\mathcal F_{\rm raw}(q)-\frac{d\mathcal G_{\rm auto}}{dq}-\mathcal F_{\rm can,auto}(q)=0.
$$

---

### 4.13 `output/phase26_crossed_independent_analytic_trial.md`

### Phase 26: crossed-ladder independent analytic evaluation

The final analytic constant is assembled from the regenerated canonical kernel.
The final closed-form checkpoint is used only after the derivation as a regression comparison.

#### A

$$
- \frac{7 \zeta\left(3\right)}{4}
$$

#### B

$$
\frac{\pi^{2}}{8}
$$

#### C

$$
- \frac{7 \zeta\left(3\right)}{16} + \frac{\pi^{2} \log{\left(2 \right)}}{8}
$$

#### half

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} - \frac{35 \zeta\left(3\right)}{12} + \pi^{2}
$$

#### endpoint_canonical_finite

$$
- \frac{19 \pi^{2}}{36} + \frac{25 \zeta\left(3\right)}{6}
$$

#### boundary_finite

$$
\frac{1}{6} - \frac{\pi^{2}}{9}
$$

#### endpoint_total

$$
- \frac{23 \pi^{2}}{36} + \frac{1}{6} + \frac{25 \zeta\left(3\right)}{6}
$$

#### divergent_sum

$$
0
$$

#### final

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

#### checkpoint_difference

$$
0
$$

#### Result

PASS: canonical standard integrals, endpoint finite part, automatic boundary term, and the final crossed-ladder constant are independently regenerated.

---

### 4.14 `output/phase78_crossed_end_to_end_checkpoint.md`

### Phase 78: crossed-ladder end-to-end closure checkpoint

The release-validation path checks the exact modern-route invariants without the expensive full raw-q-kernel regeneration.

#### projector_F1_coefficient

$$
0
$$

#### projector_F2_coefficient

$$
1
$$

#### endpoint_divergent_residual

$$
0
$$

#### half_sector

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} - \frac{35 \zeta\left(3\right)}{12} + \pi^{2}
$$

#### endpoint_total

$$
- \frac{23 \pi^{2}}{36} + \frac{1}{6} + \frac{25 \zeta\left(3\right)}{6}
$$

#### final

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

#### closed_form

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

#### final_closed_form_residual

$$
0
$$

#### historical_karplus_kroll_gap

$$
\frac{1}{32}
$$

#### Heavy raw regeneration

The existing raw-one-variable-kernel to automatic-Hermite/canonical residual audit remains available separately because rebuilding it is intentionally excluded from the fast release validation.

#### Historical 1/32 status

The magnitude 1/32 is retained as a historical audit target only. Its precise location in the 1950 Karplus--Kroll algebra is not claimed to be resolved by this checkpoint.

#### Result

PASS: projector normalization, endpoint cancellation, and final analytic assembly close exactly.

---

## 5. Large algebra/reduction files

- `output/crossed_corrected_spin_sum_95_coefficients.csv` — 96 lines, 8301 bytes
- `output/crossed_PX_generated.txt` — 1 lines, 4628 bytes
- `output/crossed_PX_projective_generated.txt` — 1 lines, 3603 bytes
- `output/crossed_phase17_first_neighbor_audit.csv` — 21 lines, 646 bytes
- `output/crossed_phase19_remaining_target_local_audit.csv` — 13 lines, 404 bytes
- `output/crossed_phase20_directional_depth2.csv` — 13 lines, 391 bytes
- `output/crossed_phase20_mixed_degree2.csv` — 13 lines, 403 bytes

## 6. Release-layer status

Phase 78 artifact(s): `output/phase78_crossed_end_to_end_checkpoint.md`.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.
