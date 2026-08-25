# QEDCalc complete two-loop calculation record — all seven diagrams

The five graph-class reports below represent 1 + 1 + 2 + 2 + 1 = 7 diagrams.

Long display equations are wrapped automatically for readable GitHub/Markdown rendering.

## 1. Report index

| Class | Multiplicity | Report |
| --- | ---: | --- |
| Crossed ladder | 1 | `output/2loop_crossed_ladder_full.md` |
| Ordinary ladder | 1 | `output/2loop_ordinary_ladder_full.md` |
| Corner pair | 2 | `output/2loop_corner_full.md` |
| Self-energy insertion pair | 2 | `output/2loop_self_energy_full.md` |
| Vacuum polarization | 1 | `output/2loop_vacuum_polarization_full.md` |

## 2. Full graph-class records

### 2.1 Crossed ladder

Source: `output/2loop_crossed_ladder_full.md`

### QEDCalc two-loop full process report: Crossed ladder

Diagram multiplicity: **1**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

#### 1. Raw input expressions

##### `input/crossed_ladder_2loop_bare.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\mu \\
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\rho \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

#### 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/01_crossed_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

##### QEDCalc サンプルプログラム説明書兼計算過程説明書：crossed ladder 1図

###### 0. この資料の目的

2ループ電子頂点補正の crossed ladder 1図について、元の Feynman 図から $F_2(0)$ の解析係数へ到達する流れを、v0.90.0 の QEDCalc サンプルと対応させて説明する。元資料では Dirac/Lorentz 代数や多変数積分の長い途中式を保存したが、本資料ではそのうち機械的に再生成できる部分を QEDCalc へ委ねる。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **crossed ladder 1図** である。

本資料では各段階を次の3種類に区別する。

- **【人が決める】**：diagram の同定、Feynman gauge の採用、on-shell 条件、どの form factor を求めるか、どの変数変換を行うかなど、物理的意味を伴う選択。
- **【QEDCalc】**：LaTeX parse、Dirac 代数、loop shift、odd 項除去、tensor reduction、IBP、式の簡約、解析積分の機械的部分、residual の exact check など。
- **【接続】**：人が導出した式を QEDCalc の入力形式へ移す、または QEDCalc の出力を次の物理的段階へ解釈する部分。

重要なのは、QEDCalc は Feynman 図の意味を勝手に推測して全計算をブラックボックス処理するプログラムではないことである。**処理順序は人が決め、長大で機械的な代数を QEDCalc/SymPy に渡す**。QEDCalc の設計思想もこの分離にある。

###### 0.1 この資料の読み方

各計算段階では原則として次の順序で記載する。

1. なぜ次の処理が必要か。
2. 人が導出・選択しなければならない内容。
3. QEDCalc に渡す LaTeX または数式入力。
4. 実際のサンプルプログラムのファイル名と行番号。
5. QEDCalc の主要出力。
6. その出力を次の段階でどう使うか。

したがって、コードブロックだけを飛び飛びに読むのではなく、**「入力式がなぜその形になるか」→「コード」→「出力の物理的意味」**の順に読む。

###### 0.2 数式と規約

- 外部電子は on-shell とする。
- 電子質量を $m$ とする。
- 外部 photon momentum は $q=p'-p$ とする。
- anomalous magnetic moment は Pauli form factor $F_2(0)$ から得る。
- 必要な箇所では $D$ 次元を保持し、最後に $D\to4$ を取る。
- IR 正則化が必要な図では photon mass $\lambda$ と $\rho=\lambda/m$ を用いる。


###### 0.3 本資料での「人」と「QEDCalc」の受け渡しの書き方

この資料では、計算の各段階を単に「人が行う」「QEDCalc が行う」と分類するだけではなく、必ず次の受け渡しを明示する。

1. **前段階から入ってくる式・データ**：この段階を始める時点で何が既知なのか。
2. **人が用意する入力**：Feynman 図の読み取り、運動学、renormalization 条件、変数変換など、物理的・解析的判断を伴う部分。
3. **QEDCalc に実際に渡る入力**：LaTeX ファイル、SymPy 式、index table、parameter family など、プログラムが直接受け取るもの。
4. **サンプルコード**：QEDCalc v0.90.0 のどのファイルの何行が処理を行うか。
5. **QEDCalc の出力**：数式として何が得られ、どの residual / term count / table が検算されるか。
6. **次段階へ渡すもの**：得られた出力のうち、次の物理計算で実際に使用するもの。

したがって、関数が引数なしで呼ばれている場合も「入力なし」という意味ではない。関数内部で `input/*.tex` を読む場合、あるいは前段階で確定した topology・kinematics が関数内部に実装されている場合は、それを明示する。

また、長大な数十～数百項の多項式を QEDCalc が生成する場合、本資料ではその多項式を人が再び手計算することを目的としない。その場合でも、**何という多項式を生成したか、その数学的定義、項数、入力変数、次段階での使われ方**は必ず記載する。完全展開式は QEDCalc の生成物として再出力できる形を保つ。


###### 0.4 全工程の入出力一覧

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

###### 1. 元の入力となる Feynman 図

####### 1.1 【人が決める】diagram から Feynman 則の式を作る

crossed ladder では、2本の内部 photon 線が電子線上で交差する。電子線に沿った Dirac 行列の順序は可換ではないので、**図を見て電子線上の頂点順序を確定すること**は人間側の仕事である。

Feynman gauge にすると、QEDCalc に保存されている raw input は次である。

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\mu \\
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\rho \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

この式で ordinary ladder と異なる重要点は、右端側の4本目の電子 propagator が $p-k$ ではなく $p-l$ を含むことである。したがって denominator family も ordinary ladder のものをそのまま流用してはいけない。

####### 1.2 【QEDCalc】raw LaTeX を parse し crossed 専用 family を作る

######## この段階へ入る入力

入力は前節に表示した complete crossed-ladder RHS で、QEDCalc では

`input/crossed_ladder_2loop_bare.tex`

に保存している。特に ordinary ladder と区別する情報は electron propagator の順序であり、右側の propagator が $p-l$ を含む点を失ってはいけない。

######## QEDCalc へ実際に渡す入力

```python
source = (ROOT/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')
parsed = parse_loop_integral_latex(source)
raw = analyze_raw_crossed_ladder(parsed)
```

である。`raw` は出力 object であり、入力式そのものではない。

######## QEDCalc の出力

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

###### 2. $F_2(0)$ を取り出す必要がある理由

####### 2.1 【人が決める】求める物理量

######## projector そのものの導出

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

####### 2.2 【QEDCalc】raw projector を生成する

######## 入力

入力は 1.2 で parse した `raw` object と、前節で確定した $D$ 次元 Pauli projector である。QEDCalc は electron chain の非可換順序を保ったまま gamma trace / spin sum を展開する。

######## 出力

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

###### 3. denominator family から Feynman parameter 表示へ

####### 3.1 【人が決める】なぜ parameter 表示が必要か

2ループ積分を直接 $k,l$ で積分するのではなく、6本の物理 denominator を Feynman parameter でまとめ、二次形式を平方完成して loop momentum を消す。これは解析方針として人が選ぶ。

物理 denominator は、2本の photon と4本の electron propagator である。補助 denominator $H=-(k+l)^2$ は numerator scalar product を同じ family 内で表すために導入し、bare graph では指数0とする。

####### 3.2 【QEDCalc】Symanzik/projective polynomial を生成する

######## 入力

入力は projector 後の crossed scalar family と、6本の physical denominator $K,L,E_1,E_2,E_3,E_4$ の power である。補助 denominator $H$ は numerator bookkeeping 用なので bare graph では power 0 とする。

######## 出力

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

###### 4. 多変数積分を三角領域へ変換する

####### 4.1 【人が決める】変数変換の目的

projective 表示のままでは多変数積分が長い。元の導出では $V$ を先に積分し、さらに $h$ と $R$ を

$$
h=\frac{1-t}{t},\qquad R=\frac{q}{t}
$$

と変換することで領域を

$$
0<t<q<1
$$

へ変える。この変数変換を採用する理由は、残った積分が rational/log/dilog の1変数 kernel へ縮約しやすくなるためである。

####### 4.2 【QEDCalc】Jacobian と logarithm argument を exact check する

######## 入力

入力は projective 表示から $V$ を先に積分した kernel と、人が選んだ

$$
h=\frac{1-t}{t},
\qquad
R=\frac{q}{t}
$$

という変数変換である。

######## 出力

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

###### 5. $t$ 積分から raw 1変数 kernel を作る

####### 5.1 【QEDCalc】cutoff を残して rational/log sector を合成する

######## 入力

入力は三角領域 $0<t<q<1$ の2変数 kernel である。endpoint singularity を途中で失わないよう、必要な cutoff を残したまま $t$ 積分を行う。

######## 出力

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

###### 6. raw kernel を canonical kernel へ縮約する

####### 6.1 【QEDCalc】Hermite/total derivative reduction

######## 入力

入力は前節の raw one-variable kernel $\mathcal F_{\rm X}^{\rm raw}(q)$ である。

######## 出力

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

###### 7. canonical 1変数積分を解析する

####### 7.1 【人が決める】endpoint を分ける理由

$q=1/2$ を境に dilogarithm の実数表示や endpoint の扱いが変わるので、元資料では half sector と endpoint sector に分けている。これは branch と収束性を意識した解析上の選択である。

####### 7.2 【QEDCalc】sector の解析値と boundary cancellation を組み立てる

######## 入力

入力は canonical kernel、total-derivative boundary term、および人が決めた endpoint sector 分割である。

######## 出力

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

###### 8. release checkpoint

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

###### 9. 現在の自動化境界

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

###### 10. 最短再計算手順

1. `input/crossed_ladder_2loop_bare.tex` を確認する。
2. Phase 15 で raw projector/family を再生成する。
3. Phase 18～24 で parameter bridge と raw one-variable kernel を再生成する。
4. Phase 25 で canonical reduction を exact check する。
5. Phase 26 で解析積分を再構成する。
6. 通常の regression は Phase 78 または `run_v090_validation.bat` で確認する。

###### 11. 歴史的 $1/32$ について

Karplus--Kroll 1950 の旧結果との差 $1/32$ は、**現代的 crossed ladder の最終値の未確定性ではない**。QEDCalc の current route は上記の独立経路で corrected value に exact に閉じている。未解決なのは、1950年の手計算のどの局所操作で $1/32$ が失われたかという provenance だけである。

###### 12. この資料で省略できた手計算

元の計算過程説明書に必要だった、数百項の Dirac 展開、scalar-product 置換、Jacobian の展開、cutoff log の係数比較、Hermite reduction の係数決定、最終 residual の照合は、現在は QEDCalc の再実行結果として確認できる。そのため本資料ではそれらの**全項展開そのもの**は掲載せず、入力・処理・出力の意味を残す。

###### 13. 参照元と再実行ファイル

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

###### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

#### 3. Recorded runtime artifacts

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

#### 4. Recorded Markdown stages

##### 4.1 `output/crossed_ladder_2loop_trial.md`

##### QEDCalc crossed-ladder two-loop trial

Generated: 2026-08-22T10:14:03

###### Scope

This trial starts from the independently derived projective/one-variable representation of the crossed-ladder graph. The raw several-hundred-term Dirac reduction is not yet regenerated automatically.

###### Projective Delta

$$
R S + R V + S U + U V - 1
$$

###### Projective W

$$
R^{2} S + R^{2} V + R S^{2} - 2 R S + S^{2} U
$$

###### Linearity check

degree_V(Delta)=1, degree_V(W)=1

###### h transformation

$$
\frac{1 - t}{t}
$$

###### R transformation

$$
\frac{q}{t}
$$

###### Jacobian

$$
\frac{1}{t^{3}}
$$

###### Reduced logarithm argument

$$
- \frac{q^{2} - 2 q t + t}{q^{2} \left(t - 1\right)}
$$

###### Canonical one-variable kernel

$$
\frac{\begin{gathered}
64 q \left(q - 1\right) \left(\log{\left(q \right)} - \log{\left(1 - q \right)}\right) \left(5 \log{\left(q \right)} + 6\right) {}+ \\
q \left(2 q - 1\right) \left(- 80 \log{\left(q \right)}^{2} + 80 \log{\left(q \right)} + 80 \operatorname{Li}_{2}\left(q\right) - 80 \operatorname{Li}_{2}\left(\frac{2 q - 1}{q}\right) - 41\right) {}+ \\
\left(q - 1\right) \left(2 q - 1\right) \\
\left(- 80 \log{\left(q \right)}^{2} + 160 \log{\left(q \right)} \log{\left(1 - q \right)} - 224 \log{\left(q \right)} + 384 \log{\left(1 - q \right)} - 80 \operatorname{Li}_{2}\left(q\right) + 80 \operatorname{Li}_{2}\left(\frac{2 q - 1}{q}\right) - 271\right)
\end{gathered}}{96 q \left(q - 1\right) \left(2 q - 1\right)}
$$

###### Dilogarithm reflection sum

$$
\frac{\log{\left(q \right)}^{2}}{2} - 2 \log{\left(q \right)} \log{\left(1 - q \right)} + \frac{\log{\left(1 - q \right)}^{2}}{2} + \frac{\pi^{2}}{6}
$$

###### q=1/2 sector

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} - \frac{35 \zeta\left(3\right)}{12} + \pi^{2}
$$

###### Endpoint canonical finite part

$$
- \frac{19 \pi^{2}}{36} + \frac{25 \zeta\left(3\right)}{6}
$$

###### Endpoint boundary finite part

$$
\frac{1}{6} - \frac{\pi^{2}}{9}
$$

###### Endpoint total

$$
- \frac{23 \pi^{2}}{36} + \frac{1}{6} + \frac{25 \zeta\left(3\right)}{6}
$$

###### Endpoint divergent-log cancellation

$$
0
$$

###### Crossed-ladder final coefficient

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

###### Independent closed-form checkpoint

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

###### Difference

$$
0
$$

###### Result

PASS: the analytic crossed-ladder coefficient matches the independent derivation.

---

##### 4.2 `output/phase15_crossed_raw_projector_trial.md`

##### Phase 15: crossed-ladder raw corrected-projector bridge

The complete bare crossed-ladder LaTeX input is parsed directly. The fourth electron denominator is p-l, not p-k, so a dedicated scalar-product basis is derived rather than reusing the ordinary-ladder family.

Electron labels: `('E1', 'E2', 'E3', 'E4')`

Bare family index: `(1, 1, 0, 1, 1, 1, 1)`

###### Derived scalar-product rules

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

###### Corrected spin-sum projector

Generated scalar-integral monomials: **95**.

CSV: `output/crossed_corrected_spin_sum_95_coefficients.csv`

The next stage is crossed-family symmetry/zero-sector analysis and bounded IBP/Laporta closure.

---

##### 4.3 `output/phase16_crossed_ibp_baseline_trial.md`

##### Phase 16: crossed-ladder bounded IBP baseline

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

##### 4.4 `output/phase18_crossed_parametric_bridge_trial.md`

##### Phase 18: crossed-ladder raw scalar-family to projective bridge

The six physical crossed denominators K,L,E1,E2,E3,E4 are taken directly from the generic crossed IBP family. H=-(k+l)^2 is auxiliary and has power zero.

Active denominators: `('K', 'L', 'E1', 'E2', 'E3', 'E4')`

U total degree: **2**; homogeneous: **True**.

F total degree: **3**; homogeneous: **True**.

###### U

$$
\begin{aligned}
cx_{1} cx_{2} + cx_{1} cx_{4} + cx_{1} cx_{5} + cx_{1} cx_{6} + cx_{2} cx_{3} + cx_{2} cx_{4} + cx_{2} cx_{5} {}+ \\
cx_{3} cx_{4} + cx_{3} cx_{5} + cx_{3} cx_{6} + cx_{4} cx_{6} + cx_{5} cx_{6}
\end{aligned}
$$

###### F

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

##### 4.5 `output/phase19_crossed_symmetry_baseline_trial.md`

##### Phase 19: crossed-ladder symmetry-reduced IBP baseline

- Raw corrected projector targets: **95**
- Symmetry-canonical targets: **52**
- IBP rows after symmetry and zero-sector pruning: **416**
- Laporta pivots: **378**
- Canonical targets pivoted: **40**
- Canonical targets not pivoted: **12**

- Remaining targets with a pivoting first-neighbor seed: **0 / 12**

The crossed graph-reversal symmetry substantially reduces the bounded system. The twelve remaining targets are locally irreducible in the first neighborhood at the exact-rational probe; degree-2 or z=0-specialized reduction is the next bounded step.

---

##### 4.6 `output/phase20_crossed_degree2_master_audit.md`

##### Phase 20: crossed-ladder bounded degree-2 master-candidate audit

- Symmetry-canonical projector targets: **52**
- Remaining non-pivot targets entering the audit: **12**
- Targets pivoting in directional depth-2: **0 / 12**
- Targets pivoting in mixed Cartesian degree-2: **0 / 12**

Together with the Phase-19 first-neighbor audit, this exhausts the full bounded Cartesian degree-2 neighborhood of the twelve remaining target integrals at the primary exact-rational probe. Absence of a pivot is strong bounded evidence, not a global master-count proof.

---

##### 4.7 `output/phase20_crossed_qlinear_bridge_trial.md`

##### Phase 20: crossed-ladder q-linear magnetic-projector bridge

The raw crossed numerator is rewritten with p' = p + q and truncated at first order before the magnetic projector is assembled.

q^0 Dirac-chain terms: **144**.

q^1 Dirac-chain terms: **84** (=48+36).

Total through O(q): **228**.

###### q=0 five-denominator Feynman-parameter bridge

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

###### Breit-frame projector normalization

F1 coefficient: **0**; F2 coefficient: **1**.

###### q-linear denominator correction

$$
2 SP^{k q} x + SP^{k q} y + SP^{l q} y
$$

This reproduces delta D = 2 x k.q + y (k+l).q.

The remaining gap to P_X is now isolated to external-spinor O(q), the 84 q-linear numerator chains, loop shifts/tensor reduction, and Gaussian recombination.

---

##### 4.8 `output/phase21_crossed_px_generation_trial.md`

##### Phase 21: automatic crossed-ladder P_X generation

The long projective numerator is reconstructed from the raw crossed Dirac chain; no stored P_X table is read.

###### Streaming route

1. Differentiate the two p'=p+q electron numerators before distributing the Dirac chain.
2. Apply the Breit magnetic projector at O(q).
3. Include the q-linear denominator correction D^-6 -> D^-6 - 6 deltaD D^-7.
4. Wick rotate and square-complete both loop momenta.
5. Reduce centered monomials by bivariate Gaussian/Wick moments term by term.
6. Collect only by powers of Delta and W, then form the common denominator.

P_X monomials: **244**.

Total degree: **8**; homogeneous: **True**.

Projective P_X monomials after scale removal: **227**.

###### Exact checks

Apparent Gamma(0) coefficient after the full sum: **0**.

Graph-reversal difference x<->z, u<->v: **0**.

deg_V(projective P_X) = **4**. Since Delta^4 W^2 has V-degree 6, the V-integrand is O(V^-2); the logarithmic 1/V coefficient therefore vanishes.

The generated integrand is

$$
G_{\mathrm X}=\frac{yP_{\mathrm X}}{4\Delta^4W^2}.
$$

The complete 244-term polynomial is written to output/crossed_PX_generated.txt rather than expanded inline here.

---

##### 4.9 `output/phase22_crossed_v_bridge_trial.md`

##### Phase 22: crossed-ladder V partial-fraction bridge

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

##### 4.10 `output/phase23_crossed_u_tq_bridge_trial.md`

##### Phase 23: crossed-ladder analytic U integration and triangular bridge

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

##### 4.11 `output/phase24_crossed_raw_q_kernel_trial.md`

##### Phase 24: crossed-ladder raw one-variable kernel regeneration

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

##### 4.12 `output/phase25_crossed_automatic_hermite_trial.md`

##### Phase 25: automatic crossed-ladder Hermite reduction

The raw one-variable kernel is reduced without using a stored R,T,U,V,P,Q,Z table.

The generated total-derivative coefficients are:

###### R(q)

$$
3/(4*(q - 1)) + 17/(4*(q - 1)**2) + 35/(12*(q - 1)**3) + 1/(4*(q - 1)**4)
$$

###### T(q)

$$
-5/(12*(q - 1)) + 4/(3*(q - 1)**2) + 13/(12*(q - 1)**3)
$$

###### U(q)

$$
7/(4*(q - 1)) + 31/(6*(q - 1)**2) + 31/(12*(q - 1)**3)
$$

###### V(q)

$$
29/(12*(q - 1)) + 1/(4*(q - 1)**2)
$$

###### P(q)

$$
3/(32*(2*q - 1)) - 27/(4*(q - 1)) - 23/(6*(q - 1)**2)
$$

###### Q(q)

$$
-q/4 - 3/(32*(2*q - 1)) + 13/(12*(q - 1)) - 1/(16*q)
$$

###### Z(q)

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

##### 4.13 `output/phase26_crossed_independent_analytic_trial.md`

##### Phase 26: crossed-ladder independent analytic evaluation

The final analytic constant is assembled from the regenerated canonical kernel.
The final closed-form checkpoint is used only after the derivation as a regression comparison.

###### A

$$
- \frac{7 \zeta\left(3\right)}{4}
$$

###### B

$$
\frac{\pi^{2}}{8}
$$

###### C

$$
- \frac{7 \zeta\left(3\right)}{16} + \frac{\pi^{2} \log{\left(2 \right)}}{8}
$$

###### half

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} - \frac{35 \zeta\left(3\right)}{12} + \pi^{2}
$$

###### endpoint_canonical_finite

$$
- \frac{19 \pi^{2}}{36} + \frac{25 \zeta\left(3\right)}{6}
$$

###### boundary_finite

$$
\frac{1}{6} - \frac{\pi^{2}}{9}
$$

###### endpoint_total

$$
- \frac{23 \pi^{2}}{36} + \frac{1}{6} + \frac{25 \zeta\left(3\right)}{6}
$$

###### divergent_sum

$$
0
$$

###### final

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

###### checkpoint_difference

$$
0
$$

###### Result

PASS: canonical standard integrals, endpoint finite part, automatic boundary term, and the final crossed-ladder constant are independently regenerated.

---

##### 4.14 `output/phase78_crossed_end_to_end_checkpoint.md`

##### Phase 78: crossed-ladder end-to-end closure checkpoint

The release-validation path checks the exact modern-route invariants without the expensive full raw-q-kernel regeneration.

###### projector_F1_coefficient

$$
0
$$

###### projector_F2_coefficient

$$
1
$$

###### endpoint_divergent_residual

$$
0
$$

###### half_sector

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} - \frac{35 \zeta\left(3\right)}{12} + \pi^{2}
$$

###### endpoint_total

$$
- \frac{23 \pi^{2}}{36} + \frac{1}{6} + \frac{25 \zeta\left(3\right)}{6}
$$

###### final

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

###### closed_form

$$
- \frac{5 \pi^{2} \log{\left(2 \right)}}{6} + \frac{1}{6} + \frac{5 \zeta\left(3\right)}{4} + \frac{13 \pi^{2}}{36}
$$

###### final_closed_form_residual

$$
0
$$

###### historical_karplus_kroll_gap

$$
\frac{1}{32}
$$

###### Heavy raw regeneration

The existing raw-one-variable-kernel to automatic-Hermite/canonical residual audit remains available separately because rebuilding it is intentionally excluded from the fast release validation.

###### Historical 1/32 status

The magnitude 1/32 is retained as a historical audit target only. Its precise location in the 1950 Karplus--Kroll algebra is not claimed to be resolved by this checkpoint.

###### Result

PASS: projector normalization, endpoint cancellation, and final analytic assembly close exactly.

---

#### 5. Large algebra/reduction files

- `output/crossed_corrected_spin_sum_95_coefficients.csv` — 96 lines, 8301 bytes
- `output/crossed_PX_generated.txt` — 1 lines, 4628 bytes
- `output/crossed_PX_projective_generated.txt` — 1 lines, 3603 bytes
- `output/crossed_phase17_first_neighbor_audit.csv` — 21 lines, 646 bytes
- `output/crossed_phase19_remaining_target_local_audit.csv` — 13 lines, 404 bytes
- `output/crossed_phase20_directional_depth2.csv` — 13 lines, 391 bytes
- `output/crossed_phase20_mixed_degree2.csv` — 13 lines, 403 bytes

#### 6. Release-layer status

Phase 78 artifact(s): `output/phase78_crossed_end_to_end_checkpoint.md`.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.

---

### 2.2 Ordinary ladder

Source: `output/2loop_ordinary_ladder_full.md`

### QEDCalc two-loop full process report: Ordinary ladder

Diagram multiplicity: **1**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

#### 1. Raw input expressions

##### `input/ordinary_ladder_2loop_bare.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\mu \\
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma_\rho \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

#### 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/02_ordinary_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

##### QEDCalc サンプルプログラム説明書兼計算過程説明書：ordinary ladder 1図

###### 0. この資料の目的

2ループ ordinary ladder 1図について、D次元 Pauli projector、72項の projector 展開、40 canonical target、12 master basis、on-shell subtraction を経て renormalized $F_2(0)$ を得るまでを説明する。ordinary ladder は $(D-4)\times1/(D-4)$ の有限残差を持つため、特に「なぜ4次元へ早く置いてはいけないか」を明示する。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **ordinary ladder 1図** である。

本資料では各段階を次の3種類に区別する。

- **【人が決める】**：diagram の同定、Feynman gauge の採用、on-shell 条件、どの form factor を求めるか、どの変数変換を行うかなど、物理的意味を伴う選択。
- **【QEDCalc】**：LaTeX parse、Dirac 代数、loop shift、odd 項除去、tensor reduction、IBP、式の簡約、解析積分の機械的部分、residual の exact check など。
- **【接続】**：人が導出した式を QEDCalc の入力形式へ移す、または QEDCalc の出力を次の物理的段階へ解釈する部分。

重要なのは、QEDCalc は Feynman 図の意味を勝手に推測して全計算をブラックボックス処理するプログラムではないことである。**処理順序は人が決め、長大で機械的な代数を QEDCalc/SymPy に渡す**。QEDCalc の設計思想もこの分離にある。

###### 0.1 この資料の読み方

各計算段階では原則として次の順序で記載する。

1. なぜ次の処理が必要か。
2. 人が導出・選択しなければならない内容。
3. QEDCalc に渡す LaTeX または数式入力。
4. 実際のサンプルプログラムのファイル名と行番号。
5. QEDCalc の主要出力。
6. その出力を次の段階でどう使うか。

したがって、コードブロックだけを飛び飛びに読むのではなく、**「入力式がなぜその形になるか」→「コード」→「出力の物理的意味」**の順に読む。

###### 0.2 数式と規約

- 外部電子は on-shell とする。
- 電子質量を $m$ とする。
- 外部 photon momentum は $q=p'-p$ とする。
- anomalous magnetic moment は Pauli form factor $F_2(0)$ から得る。
- 必要な箇所では $D$ 次元を保持し、最後に $D\to4$ を取る。
- IR 正則化が必要な図では photon mass $\lambda$ と $\rho=\lambda/m$ を用いる。


###### 0.3 本資料での「人」と「QEDCalc」の受け渡しの書き方

この資料では、計算の各段階を単に「人が行う」「QEDCalc が行う」と分類するだけではなく、必ず次の受け渡しを明示する。

1. **前段階から入ってくる式・データ**：この段階を始める時点で何が既知なのか。
2. **人が用意する入力**：Feynman 図の読み取り、運動学、renormalization 条件、変数変換など、物理的・解析的判断を伴う部分。
3. **QEDCalc に実際に渡る入力**：LaTeX ファイル、SymPy 式、index table、parameter family など、プログラムが直接受け取るもの。
4. **サンプルコード**：QEDCalc v0.90.0 のどのファイルの何行が処理を行うか。
5. **QEDCalc の出力**：数式として何が得られ、どの residual / term count / table が検算されるか。
6. **次段階へ渡すもの**：得られた出力のうち、次の物理計算で実際に使用するもの。

したがって、関数が引数なしで呼ばれている場合も「入力なし」という意味ではない。関数内部で `input/*.tex` を読む場合、あるいは前段階で確定した topology・kinematics が関数内部に実装されている場合は、それを明示する。

また、長大な数十～数百項の多項式を QEDCalc が生成する場合、本資料ではその多項式を人が再び手計算することを目的としない。その場合でも、**何という多項式を生成したか、その数学的定義、項数、入力変数、次段階での使われ方**は必ず記載する。完全展開式は QEDCalc の生成物として再出力できる形を保つ。


###### 0.4 全工程の入出力一覧

| 工程 | 人が用意・判断するもの | QEDCalc に渡る入力 | QEDCalc の主な出力 | 次へ渡すもの |
|---|---|---|---|---|
| raw graph | ordinary ladder の非可換順序、$D$ 次元保持 | `input/ordinary_ladder_2loop_bare.tex` | 4 electron + 2 photon denominators、補助 $H$、$N_\mu^{(0)}$ | scalar family |
| general-$q^2$ projector | $A(z),B(z)$ と $F_2=aA+bB$ の ansatz | generic vertex + on-shell rules | $a(z),b(z)$ | Pauli projector |
| finite $q\to0$ projector | $B_0=2A_0$ と $C_1=B_1-2A_1$ | projector series | $F_2(0)$ の有限 combination | $A_0,C_1$ |
| Dirac/Lorentz reduction | どの scalar family で表すか | raw numerator + scalar-product rules | scalar integral terms | projector term table |
| IBP reduction | exact reduction を採用 | 72 projector terms | 40 canonical targets → 12 terminal bases | 12 master coefficients |
| master assembly | analytic master values | 12 basis expression | bare coefficient $107/48+\pi^2/18$ と UV pole | bare ladder |
| on-shell subtraction | $Z_1^{(1)}F_2^{(1)}$ を引く scheme | bare ladder + one-loop counterterm | $11/48+\pi^2/18$ | renormalized ladder |
| release checkpoint | reduction counts と最終係数を固定 | generated tables/checkpoint | `72 -> 40 -> 12` + final residual | regression baseline |

全体は

$$
\begin{aligned}
\mathcal I_{\rm L}^{\rm raw} \longrightarrow \mathcal P_{F_2}^{(D)} \longrightarrow 72\text{ terms} \longrightarrow 40\text{ targets} \longrightarrow 12\text{ masters} \longrightarrow F_{2,\rm L}^{\rm bare}(0) \longrightarrow \\
F_{2,\rm L}^{\rm R}(0)
\end{aligned}
$$

である。

###### 1. 元の入力となる Feynman 図

####### 1.1 【人が決める】Feynman 則と D 次元

ordinary ladder は2本の内部 photon が交差しない図である。Feynman gauge で、raw input は次である。

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\mu \\
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma_\rho \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

ここで積分 measure を最初から $d^4k\,d^4l$ とせず $d^Dk\,d^Dl$ とする。理由は UV pole と $D$ 依存 numerator の積が有限定数を生むためであり、途中で $D=4$ とするとその有限部を失う。

###### 2. raw LaTeX を denominator family へ落とす

####### 2.1 【QEDCalc】parse と electron propagator detection

######## この段階へ入る入力

入力は前節の ordinary ladder complete RHS であり、ファイル

`input/ordinary_ladder_2loop_bare.tex`

に LaTeX として保存されている。人が図から確定した非可換順序を、そのまま保持した式でなければならない。

######## QEDCalc へ実際に渡す入力

```python
raw_source = RAW.read_text(encoding='utf-8')
raw_diagram = parse_loop_integral_latex(raw_source)
raw_info = analyze_raw_ordinary_ladder(raw_diagram)
```

である。つまり `raw_info` は入力ではなく、raw LaTeX を解析した結果である。

######## QEDCalc が認識すべき denominator

4本の electron propagator と2本の photon propagatorから、ordinary ladder の physical family を

$$
K,
\ L,
\ E_1,
\ E_2,
\ E_3,
\ E_4
$$

として認識する。さらに numerator scalar products を同じ family に写すため、補助 denominator

$$
H=-(k+l)^2
$$

を指数0で加える。

この $H$ は Feynman 図に新しい線を追加したものではない。

######## QEDCalc の出力

出力は

- ordered electron momenta / labels
- base integral index
- denominator definitions
- scalar-product replacement rules
- $q=0$ raw Dirac numerator

である。数式的には

$$
\mathcal I_{\rm raw}
\longrightarrow
\left[
N_\mu^{(0)}(k,l),
K,L,E_1,E_2,E_3,E_4,H
\right]
$$

という変換である。

**該当コード：`examples/ladder_2loop_trial.py` 26～44 行**

```python
RAW=ROOT/'input'/'ordinary_ladder_2loop_bare.tex'

raw_source=RAW.read_text(encoding='utf-8')
raw_diagram=parse_loop_integral_latex(raw_source)
raw_info=analyze_raw_ordinary_ladder(raw_diagram)
lines.append('## 0. Raw bare two-loop LaTeX bridge\n')
lines.append('The ordinary-ladder RHS is parsed as one symbolic-D two-loop expression. QEDCalc detects the four ordered electron propagators and the two photon denominators before using any stored 75-term coefficient table.\n')
lines.append(math(r'\Lambda_{\mu,\mathrm L}^{(2)}\;\text{raw input}='+render_latex(raw_diagram)))
for label,mom in zip(raw_info.electron_labels,raw_info.electron_momenta):
    pretty=label[0]+'_{'+label[1:]+'}'
    lines.append(math(pretty+r'\;\longleftrightarrow\;'+render_latex(mom)))
lines.append(math(r'J_{\rm bare}=J'+str(raw_info.base_integral_index.as_tuple()).replace(' ','')))
lines.append('The auxiliary denominator is introduced with exponent zero in the bare graph so numerator powers generated by the projector can be represented in the same family.\n')
lines.append(math(r'H=-(k+l)^2'))
lines.append('### Scalar-product basis derived from the denominator definitions\n')
for lhs,rhs in derive_ladder_scalar_product_rules_from_family().items():
    lines.append(math(sp.latex(lhs)+r'='+sp.latex(rhs)))
lines.append('### Direct q=0 Dirac numerator generated from the raw graph\n')
lines.append(math(r'N_{\mu}^{(0)}='+render_latex(raw_ladder_q0_numerator(raw_info))))
```
このコードは raw RHS を1つの `LoopIntegralExpression` として parse し、4本の ordered electron propagator と2本の photon denominator を検出する。さらに numerator scalar product を同じ family で扱うため、補助 denominator

$$
H=-(k+l)^2
$$

を指数0で加える。

**人が理解すべき点**は、補助 denominator は新しい物理 propagator ではなく IBP/積分族の bookkeeping 用だということである。

###### 3. D次元 Pauli projector

####### 3.1 【人が決める】projector の ansatz

######## 何を導出するのか

一般の on-shell vertex

$$
\Gamma^\mu =
\gamma^\mu F_1(q^2) +
\frac{i\sigma^{\mu\nu}q_\nu}{2m}F_2(q^2)
$$

から $F_2$ だけを取り出すため、spin sum を使って2つの Lorentz scalar

$$
A(z) =
\operatorname{Tr}
\left[
(\rlap{/}p'+m)
\Gamma^\mu
(\rlap{/}p+m)
\gamma_\mu
\right]
$$

$$
B(z) =
(p'+p)_\mu
\operatorname{Tr}
\left[
(\rlap{/}p'+m)
\Gamma^\mu
(\rlap{/}p+m)
\right]
$$

を作る。ここで

$$
z=\frac{q^2}{m^2},
\qquad
p^2=p'^2=m^2,
\qquad
p\cdot p'=m^2-\frac{q^2}{2}
$$

である。

$A,B$ はそれぞれ $F_1,F_2$ の線形結合なので、

$$
F_2(q^2)=a(z)A(z)+b(z)B(z)
$$

と ansatz を置き、$F_1$ の係数を0、$F_2$ の係数を1にする2本の一次方程式を解けばよい。

この「どの trace を独立量として選ぶか」「on-shell 条件をどこで使うか」は人が決める。trace 展開と一次方程式の解法を QEDCalc/SymPy に任せる。

####### 3.2 【QEDCalc】trace 方程式を解く

######## QEDCalc への入力

入力は前節の

$$
\Gamma^\mu =
\gamma^\mu F_1 +
\frac{i\sigma^{\mu\nu}q_\nu}{2m}F_2
$$

と $A(z),B(z)$ の定義、さらに on-shell scalar-product rules である。

QEDCalc は $D$ 次元 gamma trace を展開し、

$$
A=A_1(D,z)F_1+A_2(D,z)F_2
$$

$$
B=B_1(D,z)F_1+B_2(D,z)F_2
$$

という2本の線形式を生成する。その後

$$
aA_1+bB_1=0,
\qquad
aA_2+bB_2=1
$$

を解く。

メイン trial では projector coefficients を関数呼び出しで得る。

**該当コード：`examples/ladder_2loop_trial.py` 46～50 行**

```python
a,b=ladder_projector_coefficients(D,z)
lines.append('## 1. D-dimensional Pauli projector coefficients\n')
lines.append(math(r'a='+sp.latex(a)))
lines.append(math(r'b='+sp.latex(b)))

```
出力は

$$
a(z)=-\frac{2}{z(D-2)(z-4)}
$$

$$
b(z)=-\frac{Dz-2z+4}{z(D-2)(z-4)^2}
$$

である。これを1ループ vertex に適用して Schwinger $F_2^{(1)}(0)=1/2$ を再現することが projector 規格化の独立検算になる。

###### 4. $q\to0$ の有限 projector：$A_0$ と $C_1$

####### 4.1 【人が決める】なぜ $A_0$ と $C_1$ に分けるか

一般 $q^2$ projector は $z=q^2/m^2\to0$ で見かけの $1/z$ を持つ。そこで

$$
A(z)=A_0+zA_1+O(z^2),\qquad B(z)=B_0+zB_1+O(z^2)
$$

と展開し、$q=0$ の identity $B_0=2A_0$ を使う。さらに

$$
C_1=B_1-2A_1
$$

を定義すると、有限な projector は

$$
F_2(0) = -\frac{C_1}{4(D-2)} -\frac{D-1}{8(D-2)}A_0
$$

となる。ここで「$A_1$ と $B_1$ を別々に求めず、有限 combination $C_1$ を直接作る」という方針が重要である。

###### 5. Dirac/Lorentz 代数を scalar integrals へ

####### 5.1 【QEDCalc】raw q=0 numerator と scalar-product rules

######## 入力

入力は parse 済み ordinary-ladder electron chain と、4節で得た finite $q\to0$ projector の $A_0,C_1$ combination である。

######## 出力

QEDCalc は gamma trace / spin sum 後の loop-momentum numerator を、denominator family から導出した scalar-product replacement rules で置換し、

$$
\sum_j c_j(D)J(n_{1j},\ldots,n_{7j})
$$

という scalar integral の線形結合に変換する。次段階へ渡すのはこの projector term table である。

メイン trial は q=0 numerator と denominator rules を生成する。

**該当コード：`examples/ladder_2loop_trial.py` 40～53 行**

```python
lines.append('### Scalar-product basis derived from the denominator definitions\n')
for lhs,rhs in derive_ladder_scalar_product_rules_from_family().items():
    lines.append(math(sp.latex(lhs)+r'='+sp.latex(rhs)))
lines.append('### Direct q=0 Dirac numerator generated from the raw graph\n')
lines.append(math(r'N_{\mu}^{(0)}='+render_latex(raw_ladder_q0_numerator(raw_info))))

a,b=ladder_projector_coefficients(D,z)
lines.append('## 1. D-dimensional Pauli projector coefficients\n')
lines.append(math(r'a='+sp.latex(a)))
lines.append(math(r'b='+sp.latex(b)))

lines.append('## 2. Scalar-product to denominator rules\n')
for lhs,rhs in ladder_scalar_product_rules().items():
    lines.append(math(sp.latex(lhs)+r'='+sp.latex(rhs)))
```
この段階で元資料の長い gamma trace を全項掲載する必要はなくなる。検算したい場合は生成された numerator と scalar-integral table を確認すればよい。

###### 6. 72 projector terms → 40 targets → 12 master basis

####### 6.1 【QEDCalc】corrected spin-sum projector と reduction data

######## 入力

入力は前節の scalar-integral term table と、ordinary-ladder IBP family の index convention である。

######## 出力

QEDCalc は同値な積分を canonicalize し、72個の projector terms を40個の canonical target にまとめる。次に exact symbolic IBP table を使い、その40 target を12個の terminal basis へ縮約する。ここで出力は数値ではなく、各 target を12 basis の線形結合として表した exact reduction data である。

current completion route は、corrected 72-term projector table と exact 40-to-12 symbolic reduction を合成する。Phase 14 の核は次である。

**該当コード：`examples/phase14_ladder_finite_checkpoint_trial.py` 9～28 行**

```python
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'phase14_ladder_finite_checkpoint_trial.md'
D=sp.Symbol('D'); z=sp.Symbol('z')
assembly=compose_ladder_projector_with_reduction(
    ROOT/'data'/'ladder_corrected_spin_sum_72_coefficients.csv',
    ROOT/'data'/'ladder_corrected_40target_12basis_symbolic_reduction.csv',
)
expr=ladder_projector_checkpoint_normalized_expression(assembly.basis_coefficients,D=D,mass_squared=1,z=z)
mp.mp.dps=80
f=sp.lambdify(D,expr,'mpmath')

def finite_at(delta):
    return f(4+delta) + mp.mpf(3)/(4*delta)

h=mp.mpf('1e-5')
sym=(finite_at(h)+finite_at(-h))/2
h2=mp.mpf('1e-6')
sym2=(finite_at(h2)+finite_at(-h2))/2
finite=(100*sym2-sym)/99
checkpoint=mp.mpf(107)/48+mp.pi**2/18
```
入力データは

- `data/ladder_corrected_spin_sum_72_coefficients.csv`
- `data/ladder_corrected_40target_12basis_symbolic_reduction.csv`

である。前者は projector 後の scalar integrals、後者は IBP/Laporta による exact reduction を保持する。

####### 6.2 【人が理解する】72、40、12 の意味

- **72**：corrected finite-$q$ spin-sum projector を scalar integral monomial へ分解した非零項。
- **40**：対称性・zero sector・同値関係などを整理した canonical reduction targets。
- **12**：最終的に必要な terminal master basis。

これは「72個の Feynman 図」という意味ではない。

####### 6.3 【QEDCalc】bare finite coefficient の再構成

######## 入力

入力は12 master basis の係数と、それぞれの $D=4-2\epsilon$ Laurent 展開である。

######## 出力

QEDCalc はすべてを再合成して bare ladder の Laurent series を作る。有限部は

$$
\frac{107}{48}+\frac{\pi^2}{18}
$$

となり、同時に残る1-loop vertex subdivergence pole も明示される。次節ではこの pole と対応する on-shell counterterm を引く。

Phase 14 は $D=4+\delta$ の Laurent behavior

$$
F_{2,\mathrm L}^{\mathrm{bare}} = -\frac{3}{4\delta} +C_{\mathrm{fin}} +O(\delta)
$$

から finite part を高精度で再構成する。解析結果は

$$
C_{\mathrm{fin}} =
\frac{107}{48} +
\frac{\pi^2}{18}
$$

である。

###### 7. renormalization subtraction

####### 7.1 【人が決める】何を subtraction するか

ordinary ladder 単体の bare graph は UV pole を持つので、1ループ vertex renormalization の counterterm insertion を加える。on-shell scheme では必要な量は $F_2^{(1)}(D,0)$ と $Z_1^{(1)}$ である。

####### 7.2 【QEDCalc】1-loop ingredients と subtraction series

######## 入力

入力は bare ladder Laurent series と、人が7.1で指定した on-shell vertex counterterm $Z_1^{(1)}F_2^{(1)}$ である。

######## 出力

QEDCalc は両 series を同じ $\epsilon$ convention で展開し、pole が消えることを exact に確認する。有限部では

$$
\left(\frac{107}{48}+\frac{\pi^2}{18}\right)-2 =
\frac{11}{48}+\frac{\pi^2}{18}
$$

を返す。

**該当コード：`examples/ladder_2loop_trial.py` 69～80 行**

```python
lines.append('## 4. D-dimensional one-loop subtraction ingredients\n')
lines.append(math(r'F_2^{(1l)}(D,0)='+sp.latex(one_loop_f2_dimensional(D))))
lines.append(math(r'Z_1^{(1l)}='+sp.latex(one_loop_z1_dimensional(D))))
sub=ladder_subtraction_series(delta,1)
lines.append(math(r'F_{2,\mathrm{sub}}^{(2)}(0)='+sp.latex(sub)))

lines.append('## 5. Bare checkpoint and UV subtraction\n')
bare=ladder_bare_checkpoint(delta)
final=ladder_renormalized_checkpoint(delta)
lines.append(math(r'F_{2,\mathrm L}^{\mathrm{bare}}='+sp.latex(bare)+r'+O(\delta)'))
lines.append(math(r'F_{2,\mathrm L}^{\mathrm R}(0)='+sp.latex(final)))
lines.append(math(r'F_{2,\mathrm L}^{(4)}(0)=\left(\frac{\alpha}{\pi}\right)^2\left['+sp.latex(final)+r'\right]'))
```
subtraction は

$$
Z_1^{(1)}F_2^{(1)} = -\frac{3}{4\delta} +2 +O(\delta)
$$

である。pole が bare ladder の pole と相殺し、有限部から2が引かれる。

したがって

$$
A_{\mathrm L} =
\frac{107}{48} +
\frac{\pi^2}{18} -2 =
\frac{11}{48} +
\frac{\pi^2}{18}
$$

となる。

###### 8. Phase 81 end-to-end checkpoint

Phase 81 は 72→40→12 の master reconstruction と subtraction を1つの completion checkpoint としてまとめる。高精度 numerical extended audit が利用できる環境では master values から bare finite を再構成し、標準 validation では保存データの exact invariant を確認する。

**該当コード：`examples/phase81_ordinary_ladder_end_to_end_checkpoint.py` 118～140 行**

```python
    "## On-shell subtraction",
    "",
    "$$
",
    r"Z_1^{(1)}F_2^{(1)}=-\frac{3}{4\delta}+2+O(\delta).",
    "
$$",
    "",
    f"Pole coefficient: `{sub_pole}`",
    f"Finite subtraction: `{sub_finite}`",
    "",
    "The pole cancels against the bare ladder pole, while the finite subtraction removes 2.",
    "",
    "## Renormalized ordinary ladder",
    "",
    "$$
",
    r"A_{\mathrm L}=\frac{11}{48}+\frac{\pi^2}{18}.",
    "
$$",
    "",
    f"Numerical end-to-end reconstruction: **{fmt(renormalized_numeric, 50)}**",
    f"Independent analytic value: **{fmt(renormalized_checkpoint, 50)}**",
    f"Absolute difference: **{fmt(abs(renormalized_difference) if renormalized_difference is not None else None, 12)}**",
    f"Symbolic renormalized residual: `{renormalized_symbolic_residual}`",
    "",
    "No final ordinary-ladder coefficient is fed into the 72 -> 40 -> 12 master reconstruction; the closed form is used only as the output-side checkpoint.",
```
最終値は

$$
F_{2,\mathrm L}^{(4)}(0) =
\left(\frac{\alpha}{\pi}\right)^2
\left[
\frac{11}{48} +
\frac{\pi^2}{18}
\right]
$$

である。

###### 9. 現在の自動化境界

| 段階 | 状況 | 担当 |
|---|---|---|
| diagram から D次元 raw 式を作る | 人が確認 | 人 |
| raw parse / propagator family | 自動 | QEDCalc |
| projector ansatz の物理的意味 | 人が理解 | 人 |
| projector trace 解法 | 自動 | QEDCalc/SymPy |
| $A_0,C_1$ への有限再編成 | 導出済み・実装 | 人 + QEDCalc |
| gamma/tensor → scalar integrals | 自動 | QEDCalc |
| 72→40→12 reduction | exact data と実装 | QEDCalc |
| master evaluation / Laurent assembly | 自動化済み | QEDCalc |
| on-shell subtraction のscheme選択 | 人 | 人 |
| subtraction algebra / residual | 自動 | QEDCalc |

###### 10. 最短再計算手順

1. `input/ordinary_ladder_2loop_bare.tex` を確認。
2. `ladder_2loop_trial.py` で raw family と projector/subtraction を確認。
3. Phase 14 または Phase 81 で 72→40→12→bare を再構成。
4. Phase 81 で renormalized coefficient を確認。
5. `run_v090_validation.bat` で7図統合値が壊れていないことを確認。

###### 11. この資料で省略できた手計算

29個・33個の scalar integral を人が逐一展開する作業、IBP 行列消去、12 master への係数集約、Laurent series の大量整理、pole cancellation の項別照合は、現在のサンプルと reduction data から再現できる。そのため本資料では「なぜその reduction が必要か」と「どのデータが入力か」を残し、数百行の機械代数は省略する。

###### 12. 参照元と再実行ファイル

- 元計算資料：`ladder_F2_4/ladder_Feynman図から最終結果_統合版_修正版.md`
- 完成導出：`ladder_F2_4/QED_2loop_ordinary_ladder_独立導出_完成版.md`
- 詳細別冊：`ladder_F2_4/ladder_計算詳細別冊_修正版.md`
- raw input：`input/ordinary_ladder_2loop_bare.tex`
- main sample：`examples/ladder_2loop_trial.py`
- finite master checkpoint：Phase 14
- release closure：Phase 81

代表実行は `run_ladder_2loop_demo.bat`、`run_phase14_ladder_finite_checkpoint_demo.bat`、`run_phase81_ordinary_ladder_end_to_end_checkpoint.bat`。全体 regression は `run_v090_validation.bat`。


---

###### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

#### 3. Recorded runtime artifacts

| Artifact | Type | Lines | Bytes |
| --- | --- | ---: | ---: |
| `output/ladder_2loop_trial.md` | `md` | 209 | 4900 |
| `output/ladder_A0_raw_trace_trial.md` | `md` | 65 | 3282 |
| `output/ladder_general_q_raw_trace_trial.md` | `md` | 60 | 2691 |
| `output/phase10_ladder_basis_evaluation_trial.md` | `md` | 143 | 5095 |
| `output/phase11_complete_ladder_basis_evaluation_trial.md` | `md` | 62 | 2364 |
| `output/phase12_ladder_assembly_trial.md` | `md` | 65 | 2195 |
| `output/phase13_ladder_z_derivative_trial.md` | `md` | 67 | 6223 |
| `output/phase14_ladder_finite_checkpoint_trial.md` | `md` | 27 | 1016 |
| `output/phase81_ordinary_ladder_end_to_end_checkpoint.md` | `md` | 52 | 1400 |
| `output/ladder_12basis_parametric_classification.csv` | `csv` | 13 | 5065 |
| `output/ladder_12basis_z0_complete_evaluation.csv` | `csv` | 13 | 3126 |
| `output/ladder_12basis_z0_evaluation.csv` | `csv` | 13 | 1437 |
| `output/ladder_A0_29_coefficients_generated.csv` | `csv` | 30 | 660 |
| `output/ladder_corrected_40target_symbolic_nonzero.csv` | `csv` | 152 | 16627 |
| `output/ladder_corrected_reconstructed_coefficients.csv` | `csv` | 6 | 465 |
| `output/ladder_corrected_stable_unreduced_candidates.csv` | `csv` | 7 | 105 |
| `output/ladder_corrected_target_reconstruction_status.csv` | `csv` | 41 | 3633 |
| `output/ladder_general_q_75_coefficients_generated.csv` | `csv` | 76 | 5238 |
| `output/ladder_general_q_corrected_spin_sum_generated.csv` | `csv` | 73 | 4481 |
| `output/ladder_historical_stable_unreduced_candidates.csv` | `csv` | 8 | 119 |
| `output/ladder_residue_impact_profile.csv` | `csv` | 33 | 761 |
| `output/ladder_residue_sector_priority.csv` | `csv` | 18 | 259 |
| `output/ladder_stable_unreduced_candidates.csv` | `csv` | 8 | 119 |
| `output/ladder_phase2_neighborhood_seed_ranking.csv` | `csv` | 23 | 658 |
| `output/ladder_phase3_factorized_lower_sectors.csv` | `csv` | 4 | 152 |
| `output/ladder_phase4_local_master_candidates.csv` | `csv` | 4 | 170 |
| `output/ladder_phase5_depth2_master_candidates.csv` | `csv` | 4 | 245 |
| `output/ladder_phase6_full_degree2_master_candidates.csv` | `csv` | 4 | 300 |
| `output/ladder_phase7_three_probe_full_degree2_audit.csv` | `csv` | 10 | 409 |
| `output/ladder_phase8_three_probe_full_degree3_audit.csv` | `csv` | 10 | 413 |

#### 4. Recorded Markdown stages

##### 4.1 `output/ladder_2loop_trial.md`

##### QEDCalc two-loop ordinary-ladder trial

This trial uses the supplied ordinary-ladder derivation as the checkpoint source. It does not yet regenerate all 75 coefficients from the raw D-dimensional Dirac trace.

###### 0. Raw bare two-loop LaTeX bridge

The ordinary-ladder RHS is parsed as one symbolic-D two-loop expression. QEDCalc detects the four ordered electron propagators and the two photon denominators before using any stored 75-term coefficient table.


$$
\begin{aligned}
\Lambda_{\mu,\mathrm L}^{(2)}\;\text{raw input} &= \frac{e^4}{(2\pi)^8 i^2}\,\int d^{D}k\,d^{D}l\,\gamma^{\rho} \\
&\quad \frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
&\quad \gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k + \rlap{/}l - \left(i\,\varepsilon\right)}\,\gamma_{\mu} \\
&\quad \frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k + \rlap{/}l - \left(i\,\varepsilon\right)} \\
&\quad \gamma_{\alpha}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
&\quad \gamma_{\rho}\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\,\frac{1}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}
\end{aligned}
$$


$$
E_{1}\;\longleftrightarrow\;p' - \left(k\right)
$$


$$
E_{2}\;\longleftrightarrow\;p' - \left(k\right) - \left(l\right)
$$


$$
E_{3}\;\longleftrightarrow\;p - \left(k\right) - \left(l\right)
$$


$$
E_{4}\;\longleftrightarrow\;p - \left(k\right)
$$


$$
J_{\rm bare}=J(1,1,0,1,1,1,1)
$$

The auxiliary denominator is introduced with exponent zero in the bare graph so numerator powers generated by the projector can be represented in the same family.


$$
H=-(k+l)^2
$$

####### Scalar-product basis derived from the denominator definitions


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
ppk=\frac{E_{1}}{2} - \frac{K}{2}
$$


$$
pk=\frac{E_{4}}{2} - \frac{K}{2}
$$


$$
ppl=- \frac{E_{1}}{2} + \frac{E_{2}}{2} - \frac{H}{2} + \frac{K}{2}
$$


$$
pl=\frac{E_{3}}{2} - \frac{E_{4}}{2} - \frac{H}{2} + \frac{K}{2}
$$

####### Direct q=0 Dirac numerator generated from the raw graph


$$
\begin{aligned}
N_{\mu}^{(0)} &= \gamma^{\rho}\,\left(m + \rlap{/}p - \left(\rlap{/}k\right)\right)\,\gamma^{\alpha}\,\left(m + \rlap{/}p - \left(\rlap{/}k\right) - \left(\rlap{/}l\right)\right)\,\gamma_{\mu} \\
&\quad \left(m + \rlap{/}p - \left(\rlap{/}k\right) - \left(\rlap{/}l\right)\right)\,\gamma_{\alpha}\,\left(m + \rlap{/}p - \left(\rlap{/}k\right)\right)\,\gamma_{\rho}
\end{aligned}
$$

###### 1. D-dimensional Pauli projector coefficients


$$
a=\frac{2}{z \left(D - 2\right) \left(z - 4\right)}
$$


$$
b=\frac{D z - 2 z + 4}{z \left(D - 2\right) \left(z - 4\right)^{2}}
$$

###### 2. Scalar-product to denominator rules


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
ppk=\frac{E_{1}}{2} - \frac{K}{2}
$$


$$
pk=\frac{E_{4}}{2} - \frac{K}{2}
$$


$$
ppl=- \frac{E_{1}}{2} + \frac{E_{2}}{2} - \frac{H}{2} + \frac{K}{2}
$$


$$
pl=\frac{E_{3}}{2} - \frac{E_{4}}{2} - \frac{H}{2} + \frac{K}{2}
$$

###### 3. Reproducible 75-term integral-family table

Loaded monomials: **75**.


$$
C_{1,1,0,1,1,1,1}=- 16 \left(z - 2\right)
$$


$$
C_{1,0,-1,1,1,1,1}=\frac{8 \left(D - 4\right)}{z - 4}
$$


$$
C_{0,0,-1,1,1,1,1}=\frac{8 \left(D - 2\right) \left(D - 1\right)}{\left(z - 4\right)^{2}}
$$


$$
C_{1,0,-1,1,1,1,0}=- \frac{4 \left(D - 2\right) \left(D - 1\right)}{\left(z - 4\right)^{2}}
$$


$$
C_{1,1,0,0,0,0,1}=\frac{4 \left(D - 4\right)}{z \left(z - 4\right)}
$$


$$
C_{1,1,0,0,1,-1,1}=- \frac{4 \left(D - 4\right)}{z \left(z - 4\right)}
$$

###### 4. D-dimensional one-loop subtraction ingredients


$$
F_2^{(1l)}(D,0)=\frac{5 - D}{2 \left(D - 3\right)}
$$


$$
Z_1^{(1l)}=\frac{1 - D}{2 \left(D - 4\right) \left(D - 3\right)}
$$


$$
F_{2,\mathrm{sub}}^{(2)}(0)=- \frac{3}{4 \delta} + 2 - 3 \delta + O\left(\delta^{2}\right)
$$

###### 5. Bare checkpoint and UV subtraction


$$
F_{2,\mathrm L}^{\mathrm{bare}}=\frac{\pi^{2}}{18} + \frac{107}{48} - \frac{3}{4 \delta}+O(\delta)
$$


$$
F_{2,\mathrm L}^{\mathrm R}(0)=\frac{11}{48} + \frac{\pi^{2}}{18}
$$


$$
F_{2,\mathrm L}^{(4)}(0)=\left(\frac{\alpha}{\pi}\right)^2\left[\frac{11}{48} + \frac{\pi^{2}}{18}\right]
$$

###### 6. Automation boundary

QEDCalc now parses the raw symbolic-D two-loop ladder RHS, detects E1..E4 and K,L, constructs the seven-denominator family including auxiliary H, derives the scalar-product basis from the denominator equations, and then automates the stored coefficient-table validation and D-dimensional subtraction. The q=0 A0 branch is now regenerated separately from the raw D-dimensional projector trace into 29 scalar integrals (see run_ladder_a0_trace_demo.bat). The historical general-q^2 75-term audit table is now regenerated from the raw projector trace. v0.27.0 also provides a generic IBP generator and finite sparse Laporta eliminator. The remaining step is complete seed closure/sector handling and master-integral reduction for the seven-denominator family.

---

##### 4.2 `output/ladder_A0_raw_trace_trial.md`

##### Ordinary ladder raw A0 trace trial

This file is generated by QEDCalc from the bare ordinary-ladder LaTeX input.

###### Raw A0 projector trace

The program constructs

$$
A_0=\operatorname{Tr}\left[(\rlap{/}P+m)N_\mu^{(0)}(\rlap{/}P+m)\gamma^\mu\right]
$$

and evaluates the arbitrary-length $D$-dimensional Clifford trace using the optimized fully-contracted trace engine.

###### Denominator polynomial

After imposing $P^2=m^2$ and replacing scalar products by the $K,L,H,A,B$ denominator basis, QEDCalc obtains

$$
4 \left(\begin{aligned}
A^{2} D^{2} H + 2 A^{2} D^{2} - 4 A^{2} D H - 8 A^{2} D + 4 A^{2} H + 8 A^{2} - A B D^{2} H - A B D^{2} K {}+ \\
A B D^{2} L + 4 A B D H + 4 A B D K - 4 A B D L + 4 A B D - 4 A B H - 4 A B K + 4 A B L {}+ \\
A D^{2} H^{2} - A D^{2} H K - A D^{2} H L + 2 A D^{2} H - 2 A D^{2} K - 2 A D^{2} L - 4 A D H^{2} {}+ \\
4 A D H K + 4 A D H L - 8 A D H + 8 A D K + 8 A D L + 4 A H^{2} - 4 A H K - 4 A H L - 8 A K {}- \\
8 A L - 16 A + B^{2} D^{2} K - 4 B^{2} D K - 4 B^{2} D + 4 B^{2} K + 8 B^{2} - B D^{2} H K + B D^{2} K^{2} {}- \\
B D^{2} K L + 4 B D H K + 4 B D H - 4 B D K^{2} + 4 B D K L + 4 B D L - 4 B H K - 8 B H {}+ \\
4 B K^{2} - 4 B K L - 8 B L - 16 B + D^{2} H K L + 2 D^{2} K L - 4 D H K L - 4 D H K - 4 D H L {}- \\
8 D K L - 8 D K - 8 D L + 4 H K L + 8 H K + 8 H L + 16 H + 8 K L + 16 K + 16 L + 32
\end{aligned}\right)
$$

###### Integral-family result

Number of distinct scalar integrals: **29**

The q=0 denominator is $KLA^2B^2$; numerator monomials are converted to $J(n_K,n_L,n_H,n_A,n_B)$.

| Integral index | Coefficient |
|---|---|
| `(-1, 1, 0, 2, 1)` | `$4 \left(D - 2\right)^{2}$ |
| `(0, 0, -1, 2, 2)` | `$4 \left(D - 2\right)^{2}$ |
| `(0, 0, 0, 2, 1)` | `$- 4 \left(D - 2\right)^{2}$ |
| `(0, 0, 0, 2, 2)` | `$8 \left(D - 2\right)^{2}$ |
| `(0, 1, -1, 1, 2)` | `$- 4 \left(D - 2\right)^{2}$ |
| `(0, 1, -1, 2, 1)` | `$- 4 \left(D - 2\right)^{2}$ |
| `(0, 1, -1, 2, 2)` | `$- 16 \left(D - 2\right)$ |
| `(0, 1, 0, 1, 1)` | `$- 4 \left(D - 2\right)^{2}$ |
| `(0, 1, 0, 1, 2)` | `$- 8 \left(D - 2\right)^{2}$ |
| `(0, 1, 0, 2, 0)` | `$4 \left(D - 2\right)^{2}$ |
| `(0, 1, 0, 2, 2)` | `$- 32 \left(D - 2\right)$ |
| `(1, 0, -1, 1, 2)` | `$- 4 \left(D - 2\right)^{2}$ |
| `(1, 0, -1, 2, 2)` | `$- 16 \left(D - 2\right)$ |
| `(1, 0, 0, 1, 1)` | `$4 \left(D - 2\right)^{2}$ |
| `(1, 0, 0, 1, 2)` | `$- 8 \left(D - 2\right)^{2}$ |
| `(1, 0, 0, 2, 1)` | `$16 \left(D - 2\right)$ |
| `(1, 0, 0, 2, 2)` | `$- 32 \left(D - 2\right)$ |
| `(1, 1, -2, 1, 2)` | `$4 \left(D - 2\right)^{2}$ |
| `(1, 1, -1, 0, 2)` | `$4 \left(D - 2\right)^{2}$ |
| `(1, 1, -1, 1, 1)` | `$- 4 \left(D - 2\right)^{2}$ |
| `(1, 1, -1, 1, 2)` | `$8 D \left(D - 4\right)$ |
| `(1, 1, -1, 2, 1)` | `$16 \left(D - 2\right)$ |
| `(1, 1, -1, 2, 2)` | `$64$ |
| `(1, 1, 0, 0, 2)` | `$8 \left(D - 2\right)^{2}$ |
| `(1, 1, 0, 1, 1)` | `$16 D$ |
| `(1, 1, 0, 1, 2)` | `$-64$ |
| `(1, 1, 0, 2, 0)` | `$- 16 \left(D - 2\right)$ |
| `(1, 1, 0, 2, 1)` | `$-64$ |
| `(1, 1, 0, 2, 2)` | `$128$ |

Generated CSV: `output/ladder_A0_29_coefficients_generated.csv`

###### Automation boundary

The complete $A_0$ 29-integral table is now regenerated from the raw bare ladder expression. The remaining ordinary-ladder gap is the general-$q^2$ Pauli-projector branch that generates the 75-term audit table, followed by a general IBP/Laporta reducer.

---

##### 4.3 `output/ladder_general_q_raw_trace_trial.md`

##### Ordinary ladder general-q raw projector trial

This file is generated by QEDCalc from the bare ordinary-ladder LaTeX input.

###### Purpose

The ordinary-ladder archive contains a 75-term general-$q^2$ coefficient table. Later auditing of the derivation identified that this table was generated with the historical projector-first trace ordering. QEDCalc now reproduces that table from the raw bare expression and keeps it explicitly separate from the corrected spin-sum trace ordering.

###### Historical archived trace ordering

The archived table uses

$$
\operatorname{Tr}\left[(\rlap{/}p\prime+m)O_\mu(\rlap{/}p+m)\Gamma_{\mathrm L}^{\mu}\right]
$$

Generated scalar-integral monomials: **75**

Missing indices versus archived CSV: **0**

Extra indices versus archived CSV: **0**

Coefficient mismatches versus archived CSV: **0**

Therefore the raw regeneration matches the archived 75-term CSV exactly.

####### Representative regenerated coefficients

| Integral index | Regenerated coefficient | Archived coefficient |
|---|---|---|
| `(1, 1, 0, 1, 1, 1, 1)` | `$- 16 \left(z - 2\right)$` | `$- 16 \left(z - 2\right)$` |
| `(1, 0, -1, 1, 1, 1, 1)` | `$\frac{8 \left(D - 4\right)}{z - 4}$` | `$\frac{8 \left(D - 4\right)}{z - 4}$` |
| `(0, 0, -1, 1, 1, 1, 1)` | `$\frac{8 \left(D - 2\right) \left(D - 1\right)}{\left(z - 4\right)^{2}}$` | `$\frac{8 \left(D - 2\right) \left(D - 1\right)}{\left(z - 4\right)^{2}}$` |
| `(1, 1, 0, 0, 0, 0, 1)` | `$\frac{4 \left(D - 4\right)}{z \left(z - 4\right)}$` | `$\frac{4 \left(D - 4\right)}{z \left(z - 4\right)}$` |

Generated CSV: `output/ladder_general_q_75_coefficients_generated.csv`

###### Corrected spin-sum trace ordering

The audited physical spin-sum ordering is

$$
\operatorname{Tr}\left[(\rlap{/}p\prime+m)\Gamma_{\mathrm L}^{\mu}(\rlap{/}p+m)O_\mu\right]
$$

Generated scalar-integral monomials: **72**

Missing archived indices: **3**

Extra indices: **0**

Coefficient mismatches on common indices: **72**

This result is intentionally not forced to match the historical 75-term CSV. The two trace conventions are stored as separate routes so a historical audit table cannot silently replace the corrected physical projector route.

Corrected-route CSV: `output/ladder_general_q_corrected_spin_sum_generated.csv`

###### Automation boundary

The archived 75-term general-$q^2$ coefficient table is now regenerated completely from the raw bare ladder expression. The remaining major ordinary-ladder automation gap is a general IBP/Laporta reducer. For the physical $F_2(0)$ derivation QEDCalc continues to use the audited finite-limit $A_0$ and $C_1=B_1-2A_1$ route rather than treating the historical 75-term audit table as the final projector.

---

##### 4.4 `output/phase10_ladder_basis_evaluation_trial.md`

##### QEDCalc phase-10 ordinary-ladder basis-evaluation trial

The v0.41 corrected ordinary-ladder reduction terminates on 12 basis integrals. v0.42 starts the evaluation layer for those basis objects.

###### Classification

Generic-z factorized lower sectors: **3**.

Exact analytic z=0 basis values: **9 / 12**.

Remaining genuine z=0 masters: **3** (basis 8, 10, 11).

All formulas below are convention-free Euclidean scalar integrals. Overall Minkowski i factors, Wick-rotation signs, (2pi)^D loop-measure normalization, and renormalization-scale factors belong to the convention layer.

###### z=0 analytic values

####### Basis 0: `(0, 0, 0, 0, 0, 1, 1)`

Status: **exact**. Method: `factorized_tadpoles_T1xT1`.

$$
\pi^{D} m_{2}^{D - 2} \Gamma^{2}\left(1 - \frac{D}{2}\right)
$$

####### Basis 1: `(0, 0, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `factorized_tadpoles_T1xT1`.

$$
\pi^{D} m_{2}^{D - 2} \Gamma^{2}\left(1 - \frac{D}{2}\right)
$$

####### Basis 2: `(0, 0, 0, 0, 1, 1, 1)`

Status: **exact**. Method: `z0_degenerate_factorization_T2xT1`.

$$
\pi^{D} m_{2}^{D - 3} \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - \frac{D}{2}\right)
$$

####### Basis 3: `(0, 0, 0, 0, 2, 0, 3)`

Status: **exact**. Method: `factorized_tadpoles_T2xT3`.

$$
\frac{\pi^{D} m_{2}^{D - 5} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - \frac{D}{2}\right)}{2}
$$

####### Basis 4: `(0, 0, 0, 1, 1, 1, 1)`

Status: **exact**. Method: `z0_degenerate_factorization_T2xT2`.

$$
\pi^{D} m_{2}^{D - 4} \Gamma^{2}\left(2 - \frac{D}{2}\right)
$$

####### Basis 5: `(0, 1, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `one_massless_two_massive_vacuum_111`.

$$
\frac{\pi^{D} m_{2}^{D - 3} \Gamma^{2}\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right)}{\Gamma\left(\frac{D}{2}\right) \Gamma\left(4 - D\right)}
$$

####### Basis 6: `(0, 1, 0, 0, 1, 0, 2)`

Status: **exact**. Method: `one_massless_two_massive_vacuum_112`.

$$
\frac{\pi^{D} m_{2}^{D - 4} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - \frac{D}{2}\right) \Gamma\left(4 - D\right) \Gamma\left(\frac{D}{2} - 1\right)}{\Gamma\left(\frac{D}{2}\right) \Gamma\left(5 - D\right)}
$$

####### Basis 7: `(0, 1, 1, 0, 0, 0, 1)`

Status: **exact**. Method: `massless_bubble_then_on_shell_E4`.

$$
\frac{\pi^{D} m_{2}^{D - 3} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma^{2}\left(\frac{D}{2} - 1\right) \Gamma\left(2 D - 5\right)}{\Gamma\left(D - 2\right) \Gamma\left(\frac{3 D}{2} - 3\right)}
$$

####### Basis 8: `(0, 1, 1, 0, 1, 0, 1)`

Status: **unresolved**. Method: `genuine_two_loop_z0_master`.

The current evaluator leaves this as a genuine two-loop master. Its automatically generated projective polynomials are:

$$
U=b9x1 b9x2 + b9x1 b9x3 + b9x1 b9x4 + b9x2 b9x4 + b9x3 b9x4
$$

$$
\begin{aligned}
F &= m_{2} \\
&\quad \left(b9x1 b9x3^{2} + 2 b9x1 b9x3 b9x4 + b9x1 b9x4^{2} + b9x2 b9x4^{2} + b9x3^{2} b9x4 + b9x3 b9x4^{2}\right)
\end{aligned}
$$

####### Basis 9: `(0, 1, 1, 1, 0, 0, 1)`

Status: **exact**. Method: `z0_E1_equals_E4_massless_bubble_E4_squared`.

$$
\frac{\pi^{D} m_{2}^{D - 4} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(4 - D\right) \Gamma^{2}\left(\frac{D}{2} - 1\right) \Gamma\left(2 D - 6\right)}{\Gamma\left(D - 2\right) \Gamma\left(\frac{3 D}{2} - 4\right)}
$$

####### Basis 10: `(0, 1, 1, 1, 0, 1, 1)`

Status: **unresolved**. Method: `genuine_two_loop_z0_master`.

The current evaluator leaves this as a genuine two-loop master. Its automatically generated projective polynomials are:

$$
\begin{aligned}
U &= b11x1 b11x2 + b11x1 b11x3 + b11x1 b11x4 + b11x1 b11x5 + b11x2 b11x3 + b11x2 b11x5 {}+ \\
&\quad b11x3 b11x4 + b11x4 b11x5
\end{aligned}
$$

$$
F = m_{2} \left(\begin{aligned}
b11x1 b11x3^{2} + 2 b11x1 b11x3 b11x4 + 2 b11x1 b11x3 b11x5 + b11x1 b11x4^{2} {}+ \\
2 b11x1 b11x4 b11x5 + b11x1 b11x5^{2} + b11x2 b11x3^{2} + 2 b11x2 b11x3 b11x5 + b11x2 b11x5^{2} {}+ \\
b11x3^{2} b11x4 + b11x3 b11x4^{2} + 2 b11x3 b11x4 b11x5 + b11x4^{2} b11x5 + b11x4 b11x5^{2}
\end{aligned}\right)
$$

####### Basis 11: `(0, 1, 1, 1, 1, 0, 2)`

Status: **unresolved**. Method: `genuine_two_loop_z0_master`.

The current evaluator leaves this as a genuine two-loop master. Its automatically generated projective polynomials are:

$$
\begin{aligned}
U &= b12x1 b12x2 + b12x1 b12x3 + b12x1 b12x4 + b12x1 b12x5 + b12x2 b12x3 + b12x2 b12x5 {}+ \\
&\quad b12x3 b12x4 + b12x4 b12x5
\end{aligned}
$$

$$
F = m_{2} \left(\begin{aligned}
b12x1 b12x3^{2} + 2 b12x1 b12x3 b12x4 + 2 b12x1 b12x3 b12x5 + b12x1 b12x4^{2} {}+ \\
2 b12x1 b12x4 b12x5 + b12x1 b12x5^{2} + b12x2 b12x3^{2} + 2 b12x2 b12x3 b12x5 + b12x2 b12x5^{2} {}+ \\
b12x3^{2} b12x4 + b12x3 b12x4^{2} + 2 b12x3 b12x4 b12x5 + b12x4^{2} b12x5 + b12x4 b12x5^{2}
\end{aligned}\right)
$$

###### Evaluation methods now available

1. Products of massive one-loop tadpoles.
2. z=0 degeneracies where E1=E4 and/or E2=E3.
3. The one-massless/two-equal-mass two-loop vacuum sunset in Gamma functions.
4. A massless bubble followed by a generalized on-shell massive one-loop integral.
5. Generic projective Feynman-parameter generation U, F, Delta for every one of the 12 basis integrals.

The next evaluation stage is therefore reduced to basis 8, 10, and 11.

Classification CSV: `output/ladder_12basis_parametric_classification.csv`

z=0 evaluation CSV: `output/ladder_12basis_z0_evaluation.csv`

---

##### 4.5 `output/phase11_complete_ladder_basis_evaluation_trial.md`

##### Phase 11: complete z=0 ordinary-ladder basis evaluation

All twelve terminal basis integrals are analytic in the convention-free Euclidean normalization.

###### 1. Reduced z=0 T family

At z=0, E1=E4 and E3=E2, so basis 8, 10 and 11 become

$$
T_n=\int\frac{d^Dk\,d^Dl}{L\,H\,E_2\,E_4^n},\qquad n=1,2,3.
$$

The reduced IBP family keeps K as an auxiliary denominator and uses (K,L,H,E2,E4). Degree-1 seeds already pivot T2 and T3.

####### T2 reduction

$$
T_2=-\frac{D-3}{2m^2}T_1-\frac{1}{2m^2}A,
$$

where the other lower sector in the raw IBP relation is scaleless and vanishes.

####### T3 reduction

$$
T_3=\frac{(D-6)(D-4)(D-3)}{8(m^2)^2(D-5)}T_1+\frac{(D-4)^2}{2(m^2)^2(D-5)}A+\frac{D-4}{4m^2(D-5)}E,
$$

with A and E given by massless two-point subloops followed by generalized on-shell one-loop electron integrals; both are Gamma-function closed forms.

###### 2. T1 Cheng-Wu reduction

Write D=4-2 epsilon and choose the Cheng-Wu gauge x_E2+x_E4=1. After integrating the two massless-line parameters, the remaining integral is

$$
\frac{1}{(1-\epsilon)(1-2\epsilon)}\int_0^1dt\,t^{-1+\epsilon}\left[(1-t)^{-1+\epsilon}-(1-t)^{-\epsilon}\right]{}_2F_1(2\epsilon,1;2-\epsilon;t).
$$

Using the Euler-Beta integral, the two terms become 3F2(1). A common upper/lower parameter cancels in each term, leaving Gauss-summable 2F1(1) functions. Hence T1 is Gamma-only.

$$
T_1=\pi^{4-2\epsilon}(m^2)^{-2\epsilon}\Gamma(2\epsilon)\,\mathcal I(\epsilon),
$$

with

$$
\begin{aligned}
\mathcal \\
I(\epsilon)=\frac{1}{(1-\epsilon)(1-2\epsilon)}\left[\frac{\Gamma(\epsilon)^2}{\Gamma(2\epsilon)}\frac{\Gamma(2-\epsilon)\Gamma(1-2\epsilon)}{\Gamma(1-\epsilon)\Gamma(2-2\epsilon)}-\Gamma(\epsilon)\Gamma(1-\epsilon)\frac{\Gamma(2-\epsilon)\Gamma(2-4\epsilon)}{\Gamma(2-3\epsilon)\Gamma(2-2\epsilon)}\right].
\end{aligned}
$$

###### 3. Completion status

- Exact z=0 terminal basis values: **12 / 12**
- Remaining unresolved z=0 basis integrals: **0**
- Basis 8: Cheng-Wu + hypergeometric reduction + Gauss summation
- Basis 10/11: dedicated z=0 symbolic IBP + Gamma lower sectors

Complete evaluation CSV: `output/ladder_12basis_z0_complete_evaluation.csv`

###### 4. Boundary of the result

These are convention-free Euclidean scalar-integral values. Overall Minkowski i factors, loop-measure conventions, renormalization-scale factors and the projector/reduction coefficients remain in their respective QEDCalc layers.

---

##### 4.6 `output/phase12_ladder_assembly_trial.md`

##### Phase 12: ordinary-ladder projector/reduction assembly

The corrected 72 raw projector monomials are first canonicalized under the ordinary-ladder graph symmetries and then composed with the exact 40-target x 12-basis symbolic IBP matrix.

- Corrected raw monomials: **72**
- Symmetry-canonical targets: **40**
- Terminal basis size: **12**

###### Leading z-pole audit

Several individual basis coefficients contain a simple magnetic-projector pole `1/z`. No `1/z^2` pole remains after composition.

Basis 0 residue:

$$
\frac{\left(D - 6\right) \left(D - 5\right) \left(D - 2\right) \left(5 D^{2} - 31 D + 46\right)}{2 \left(D - 4\right) \left(D - 3\right)^{2}}
$$

Basis 1 residue:

$$
\frac{\left(D - 2\right) \left(6 D^{4} - 98 D^{3} + 573 D^{2} - 1410 D + 1240\right)}{2 \left(D - 4\right) \left(D - 3\right) \left(3 D - 8\right)}
$$

Basis 3 residue:

$$
\frac{16 \left(D - 5\right) \left(D^{2} - 9 D + 16\right)}{\left(D - 4\right)^{2} \left(D - 3\right) \left(D - 2\right)}
$$

Basis 5 residue:

$$
\frac{9 D^{5} - 182 D^{4} + 1414 D^{3} - 5289 D^{2} + 9550 D - 6680}{\left(D - 4\right) \left(D - 3\right) \left(D - 2\right)}
$$

Basis 6 residue:

$$
\frac{4 \left(9 D^{5} - 182 D^{4} + 1414 D^{3} - 5289 D^{2} + 9550 D - 6680\right)}{\left(D - 4\right) \left(D - 3\right) \left(D - 2\right) \left(3 D - 8\right)}
$$

Basis 7 residue:

$$
\frac{3 D^{4} - 45 D^{3} + 251 D^{2} - 605 D + 530}{\left(D - 3\right) \left(D - 2\right)}
$$

Basis 8 residue:

$$
- \frac{4 \left(3 D^{4} - 45 D^{3} + 251 D^{2} - 605 D + 530\right)}{\left(D - 2\right) \left(3 D - 8\right)}
$$

After inserting the exact v0.43 values of all twelve basis integrals at z=0, the coefficient of the complete `1/z` term is

$$
0
$$

so the leading projector singularity cancels exactly.

###### What remains for the finite z->0 limit

Because some basis coefficients have `C_i(z)=r_i/z+c_i+...`, the finite term also contains `r_i I_i'(0)`. Therefore the exact z=0 basis values alone are not sufficient. The next stage is to derive and IBP-reduce the first z-derivatives of basis 0, 1, 3, 5, 6, 7, and 8 (zero weights can be skipped), then combine them with the regular coefficient parts and perform the epsilon expansion.

---

##### 4.7 `output/phase13_ladder_z_derivative_trial.md`

##### Phase 13: ordinary-ladder basis z-derivative reduction

The phase-12 projector audit shows derivative weights only for basis 0, 1, 3, 5, 6, 7, and 8. This phase checks which of those derivatives are actually nonzero and closes all required analytic sectors, including basis 8 through a D+2 dimensional shift followed by z=0 IBP reduction.

###### Basis 0: `(0, 0, 0, 0, 0, 1, 1)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

###### Basis 1: `(0, 0, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

###### Basis 3: `(0, 0, 0, 0, 2, 0, 3)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

###### Basis 5: `(0, 1, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `three_denominator_projective_beta`.

$$
\frac{4 \pi^{D} \Gamma^{2}\left(3 - \frac{D}{2}\right)}{D \left(D - 5\right) \left(D - 4\right) \left(D - 2\right)}
$$

###### Basis 6: `(0, 1, 0, 0, 1, 0, 2)`

Status: **exact**. Method: `three_denominator_projective_beta`.

$$
\frac{4 \pi^{D} \Gamma\left(3 - \frac{D}{2}\right) \Gamma\left(4 - \frac{D}{2}\right)}{D \left(D - 6\right) \left(D - 5\right) \left(D - 2\right)}
$$

###### Basis 7: `(0, 1, 1, 0, 0, 0, 1)`

Status: **exact**. Method: `z_independent_projective_F`.

$$
0
$$

###### Basis 8: `(0, 1, 1, 0, 1, 0, 1)`

Status: **exact**. Method: `dimension_shift_Dplus2_then_z0_IBP`.

$$
-\frac{\begin{gathered}
\pi^{D} \left(D - 2\right) \\
\left(19 D^{5} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) - 246 D^{4} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) + 18 D^{4} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 1\right) \Gamma\left(2 D - 4\right) - 8 D^{4} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) + 8 D^{4} \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right) + 1143 D^{3} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) - 194 D^{3} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 1\right) \Gamma\left(2 D - 4\right) + 116 D^{3} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) - 116 D^{3} \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right) - 2256 D^{2} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) + 676 D^{2} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 1\right) \Gamma\left(2 D - 4\right) - 632 D^{2} \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) + 632 D^{2} \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right) + 1600 D \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 3\right) - 760 D \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(D\right) \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right) \Gamma\left(\frac{3 D}{2} - 1\right) \Gamma\left(2 D - 4\right) + 1524 D \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) - 1524 D \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right) - 1360 \Gamma^{2}\left(\frac{D}{2}\right) \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - D\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(2 D - 2\right) + 1360 \Gamma^{2}\left(1 - \frac{D}{2}\right) \Gamma\left(\frac{D}{2} + 1\right) \Gamma^{2}\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right)\right)
\end{gathered}}{\begin{gathered}
16 D \left(D - 5\right) \left(D - 4\right) \left(D - 3\right) \left(2 D - 5\right) \Gamma\left(\frac{D}{2}\right) \\
\Gamma\left(D\right) \Gamma\left(D - 1\right) \Gamma\left(\frac{3 D}{2} - 2\right) \Gamma\left(\frac{3 D}{2} - 1\right)
\end{gathered}}
$$

###### Result

- Basis 0, 1, 3: derivative is exactly zero because the factorized lower-sector value is z-independent.
- Basis 7: derivative is exactly zero because its projective F polynomial contains no z.
- Basis 5 and 6: first derivatives are analytic Gamma-function expressions.
- Basis 8: the derivative is mapped to a D+2 shifted scalar integral and reduced by z=0 IBP to T1 plus known lower sectors.
- Remaining unresolved required first-z derivatives: **0**.

---

##### 4.8 `output/phase14_ladder_finite_checkpoint_trial.md`

##### Phase 14: convention-aware ordinary-ladder finite checkpoint

The corrected 72-term spin-sum projector, the exact 40-to-12 symbolic reduction, all twelve z=0 basis values, and every required first-z derivative are assembled without the historical final reduction checkpoint.

The convention-free Euclidean master layer is converted to the historical two-loop checkpoint measure by

$$
\frac{e^{-\gamma_E(D-4)}}{16\pi^D}.
$$

With $\delta=D-4$, the reconstructed Laurent behavior is

$$
F_{2,\mathrm L}^{\mathrm{bare}}=-\frac{3}{4\delta}+C_{\mathrm{fin}}+O(\delta).
$$

Numerically reconstructed finite constant: **2.7774780222827421454846518587600728587736922181285**.

$$
C_{\mathrm{fin}}=\frac{107}{48}+\frac{\pi^2}{18}.
$$

Independent numerical checkpoint value: **2.7774780222827421454908050555486750630729833004023**.

Absolute difference: **6.1531968e-21**.

This closes the ordinary-ladder path from the corrected raw projector table through IBP/master evaluation to the previously stored bare checkpoint.

---

##### 4.9 `output/phase81_ordinary_ladder_end_to_end_checkpoint.md`

##### Phase 81: ordinary ladder end-to-end checkpoint

QEDCalc version: `0.88.2`

###### Reduction chain

- corrected spin-sum projector table: 72 terms
- canonical IBP targets after symmetry combination: 40
- terminal analytic basis size: 12
- leading magnetic-projector z-pole residual: `0`

###### Bare finite coefficient

The full 40-to-12 basis assembly gives

$$
F_{2,\mathrm L}^{\mathrm{bare}}=-\frac{3}{4\delta}+C_{\mathrm{bare}}+O(\delta),
$$

Numerically reconstructed `C_bare`: **2.7774780222827421454846518587600728587736922181285**

Independent analytic checkpoint:

$$
C_{\mathrm{bare}}=\frac{107}{48}+\frac{\pi^2}{18}.
$$

Absolute reconstruction difference: **6.1531967886e-21**

###### On-shell subtraction

$$
Z_1^{(1)}F_2^{(1)}=-\frac{3}{4\delta}+2+O(\delta).
$$

Pole coefficient: `-3/4`
Finite subtraction: `2`

The pole cancels against the bare ladder pole, while the finite subtraction removes 2.

###### Renormalized ordinary ladder

$$
A_{\mathrm L}=\frac{11}{48}+\frac{\pi^2}{18}.
$$

Numerical end-to-end reconstruction: **0.77747802228274214548465185876007285877369221812845**
Independent analytic value: **0.77747802228274214549080505554867506307298330040227**
Absolute difference: **6.1531967886e-21**
Symbolic renormalized residual: `0`

No final ordinary-ladder coefficient is fed into the 72 -> 40 -> 12 master reconstruction; the closed form is used only as the output-side checkpoint.

---

#### 5. Large algebra/reduction files

- `output/ladder_12basis_parametric_classification.csv` — 13 lines, 5065 bytes
- `output/ladder_12basis_z0_complete_evaluation.csv` — 13 lines, 3126 bytes
- `output/ladder_12basis_z0_evaluation.csv` — 13 lines, 1437 bytes
- `output/ladder_A0_29_coefficients_generated.csv` — 30 lines, 660 bytes
- `output/ladder_corrected_40target_symbolic_nonzero.csv` — 152 lines, 16627 bytes
- `output/ladder_corrected_reconstructed_coefficients.csv` — 6 lines, 465 bytes
- `output/ladder_corrected_stable_unreduced_candidates.csv` — 7 lines, 105 bytes
- `output/ladder_corrected_target_reconstruction_status.csv` — 41 lines, 3633 bytes
- `output/ladder_general_q_75_coefficients_generated.csv` — 76 lines, 5238 bytes
- `output/ladder_general_q_corrected_spin_sum_generated.csv` — 73 lines, 4481 bytes
- `output/ladder_historical_stable_unreduced_candidates.csv` — 8 lines, 119 bytes
- `output/ladder_residue_impact_profile.csv` — 33 lines, 761 bytes
- `output/ladder_residue_sector_priority.csv` — 18 lines, 259 bytes
- `output/ladder_stable_unreduced_candidates.csv` — 8 lines, 119 bytes
- `output/ladder_phase2_neighborhood_seed_ranking.csv` — 23 lines, 658 bytes
- `output/ladder_phase3_factorized_lower_sectors.csv` — 4 lines, 152 bytes
- `output/ladder_phase4_local_master_candidates.csv` — 4 lines, 170 bytes
- `output/ladder_phase5_depth2_master_candidates.csv` — 4 lines, 245 bytes
- `output/ladder_phase6_full_degree2_master_candidates.csv` — 4 lines, 300 bytes
- `output/ladder_phase7_three_probe_full_degree2_audit.csv` — 10 lines, 409 bytes
- `output/ladder_phase8_three_probe_full_degree3_audit.csv` — 10 lines, 413 bytes

#### 6. Release-layer status

Phase 81 artifact(s): `output/phase81_ordinary_ladder_end_to_end_checkpoint.md`.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.

---

### 2.3 Corner pair

Source: `output/2loop_corner_full.md`

### QEDCalc two-loop full process report: Corner pair

Diagram multiplicity: **2**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

#### 1. Raw input expressions

##### `input/corner_4_2loop_bare_feynman_gauge.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\rho \frac{1}{m-\rlap{/}p'+\rlap{/}l-i\varepsilon} \\
\gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

##### `input/corner_5_2loop_bare_feynman_gauge.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \\
\gamma_\rho \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

#### 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/03_corner_2図_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

##### QEDCalc サンプルプログラム説明書兼計算過程説明書：corner 2図

###### 0. この資料の目的

2ループ corner contribution（左右の inner-vertex insertion に対応する2図）について、raw 2図の同定、magnetic projector、1ループ renormalized inner vertex、UV subdivergence subtraction、soft/hard sector、有限解析値、self-energy insertion との IR 相殺までを QEDCalc の複数 Phase と対応させる。corner は5群の中で最も処理層が多いので、1本のサンプルへ無理に押し込まず、段階ごとのサンプルを一本道に並べる。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **corner 2図** である。

本資料では各段階を次の3種類に区別する。

- **【人が決める】**：diagram の同定、Feynman gauge の採用、on-shell 条件、どの form factor を求めるか、どの変数変換を行うかなど、物理的意味を伴う選択。
- **【QEDCalc】**：LaTeX parse、Dirac 代数、loop shift、odd 項除去、tensor reduction、IBP、式の簡約、解析積分の機械的部分、residual の exact check など。
- **【接続】**：人が導出した式を QEDCalc の入力形式へ移す、または QEDCalc の出力を次の物理的段階へ解釈する部分。

重要なのは、QEDCalc は Feynman 図の意味を勝手に推測して全計算をブラックボックス処理するプログラムではないことである。**処理順序は人が決め、長大で機械的な代数を QEDCalc/SymPy に渡す**。QEDCalc の設計思想もこの分離にある。

###### 0.1 この資料の読み方

各計算段階では原則として次の順序で記載する。

1. なぜ次の処理が必要か。
2. 人が導出・選択しなければならない内容。
3. QEDCalc に渡す LaTeX または数式入力。
4. 実際のサンプルプログラムのファイル名と行番号。
5. QEDCalc の主要出力。
6. その出力を次の段階でどう使うか。

したがって、コードブロックだけを飛び飛びに読むのではなく、**「入力式がなぜその形になるか」→「コード」→「出力の物理的意味」**の順に読む。

###### 0.2 数式と規約

- 外部電子は on-shell とする。
- 電子質量を $m$ とする。
- 外部 photon momentum は $q=p'-p$ とする。
- anomalous magnetic moment は Pauli form factor $F_2(0)$ から得る。
- 必要な箇所では $D$ 次元を保持し、最後に $D\to4$ を取る。
- IR 正則化が必要な図では photon mass $\lambda$ と $\rho=\lambda/m$ を用いる。


###### 0.3 本資料での「人」と「QEDCalc」の受け渡しの書き方

この資料では、計算の各段階を単に「人が行う」「QEDCalc が行う」と分類するだけではなく、必ず次の受け渡しを明示する。

1. **前段階から入ってくる式・データ**：この段階を始める時点で何が既知なのか。
2. **人が用意する入力**：Feynman 図の読み取り、運動学、renormalization 条件、変数変換など、物理的・解析的判断を伴う部分。
3. **QEDCalc に実際に渡る入力**：LaTeX ファイル、SymPy 式、index table、parameter family など、プログラムが直接受け取るもの。
4. **サンプルコード**：QEDCalc v0.90.0 のどのファイルの何行が処理を行うか。
5. **QEDCalc の出力**：数式として何が得られ、どの residual / term count / table が検算されるか。
6. **次段階へ渡すもの**：得られた出力のうち、次の物理計算で実際に使用するもの。

したがって、関数が引数なしで呼ばれている場合も「入力なし」という意味ではない。関数内部で `input/*.tex` を読む場合、あるいは前段階で確定した topology・kinematics が関数内部に実装されている場合は、それを明示する。

また、長大な数十～数百項の多項式を QEDCalc が生成する場合、本資料ではその多項式を人が再び手計算することを目的としない。その場合でも、**何という多項式を生成したか、その数学的定義、項数、入力変数、次段階での使われ方**は必ず記載する。完全展開式は QEDCalc の生成物として再出力できる形を保つ。


###### 0.4 全工程の入出力一覧

| 工程 | 人が用意・判断するもの | QEDCalc に渡る入力 | QEDCalc の主な出力 | 次へ渡すもの |
|---|---|---|---|---|
| raw pair | diagram 4 / 5 の非可換順序 | 2つの `input/corner_*_bare_feynman_gauge.tex` | `r.diagram4`, `r.diagram5` = **解析結果**、inner side、$q=0$ powers | corner topology |
| magnetic projector | Breit frame から $F_2(0)$ 抽出式を導出 | diagram 4 / 5 chain + projector kinematics | $P_4(k,l)$ 68項、$P_5(k,l)$ 69項 | projected numerators |
| parameter family | split parameter を $q$ 微分まで保持 | $x,y,z,u,v,\rho,t$ と denominator powers | $a,b,c,r,s,\Delta,W,\Omega$、multiplicity、$q$ derivative coefficients | Gaussian family |
| UV subgraph | inner vertex を先に on-shell subtract | bare projected family + local counterterm | bare/local UV residues、exact cancellation | renormalized inner vertex |
| sector bridge | 1-loop renormalization output を outer loop に接続 | $\overline\Lambda_\rho$ の sector representation | rational/log sector identities | finite/IR sector kernels |
| soft sector | photon mass $\rho$ を保持 | soft limit of sector kernel | $\ln(1/\rho)$ coefficient $+1$、soft finite constant | soft ownership |
| hard/z sectors | momentum shift に伴う numerator correction を保持 | renormalized sector kernels | hard primary、shift correction、$z$ sector | $A_{\rm C,fin}$ |
| IR cancellation | self-energy 側の log と pair にする | corner log coefficient + self-energy coefficient | IR residual $0$ | finite 2-loop sum |
| release checkpoint | sector route と soft/hard route を独立照合 | analytic outputs | exact closed-form residual $0$ | corner 最終寄与 |

全体は

$$
\begin{aligned}
(\mathcal I_4^{\rm raw},\mathcal I_5^{\rm raw}) \longrightarrow (P_4,P_5) \longrightarrow \text{renormalized inner vertex} \longrightarrow \\
\text{soft + hard + }z\text{ sectors} \longrightarrow A_{\rm C}
\end{aligned}
$$

である。

###### 1. 元の入力となる2つの Feynman 図

####### 1.1 【人が決める】2図の非可換順序

Feynman gauge の raw inputs は次である。

######## diagram 4

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\rho \frac{1}{m-\rlap{/}p'+\rlap{/}l-i\varepsilon} \\
\gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

######## diagram 5

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \\
\gamma_\rho \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

2図は外部 photon vertex に対して inner vertex correction が左右に入る組である。電子線上の gamma/propagator 順序は人が図から確定する。

####### 1.2 【QEDCalc】raw pair の topology を監査する

######## この段階へ入る入力は何か

前節 1.1 で人が Feynman 図から確定した diagram 4 と diagram 5 の2本の式そのものが入力である。QEDCalc v0.90.0 では、この2式を次のファイルに保存している。

- `input/corner_4_2loop_bare_feynman_gauge.tex`
- `input/corner_5_2loop_bare_feynman_gauge.tex`

したがって、サンプルコード中の `r.diagram4` と `r.diagram5` は入力ではない。**2つの LaTeX ファイルを QEDCalc が読み取って解析した後の出力 object** である。

概念的には、入力は

$$
\mathcal I_4^{\rm raw}
\quad\text{and}\quad
\mathcal I_5^{\rm raw}
$$

であり、それぞれ前節に表示した完全な非可換 electron chain と2本の photon denominator を含む。

######## QEDCalc 内部で入力をセットする部分

`corner_raw_pair_audit()` の内部では、実際に次の処理を行う。

```python
root = Path(__file__).resolve().parents[2]
d4 = parse_loop_integral_latex(
    (root/'input'/'corner_4_2loop_bare_feynman_gauge.tex').read_text(encoding='utf-8')
)
d5 = parse_loop_integral_latex(
    (root/'input'/'corner_5_2loop_bare_feynman_gauge.tex').read_text(encoding='utf-8')
)
a4 = analyze_raw_corner(d4)
a5 = analyze_raw_corner(d5)
```

ここで `parse_loop_integral_latex()` は LaTeX を `LoopIntegralExpression` に変換し、`analyze_raw_corner()` が ordered electron propagator と photon denominator を解析する。

######## 何を検査しているか

$q=0$ とすると $p'=p$ になるため、同じ denominator が重なる。diagram 4 では $p-l$ 型 propagator が二重になり、diagram 5 では $p-k$ 型 propagator が二重になる。そのため、期待される denominator power は

$$
\text{diagram 4}:\quad (1,1,2,1,1)
$$

$$
\text{diagram 5}:\quad (2,1,1,1,1)
$$

である。さらに inner vertex subgraph は、diagram 4 では左側、diagram 5 では右側に存在する必要がある。

**該当コード：`examples/phase32_corner_raw_pair_bridge.py` 1～7 行**

```python
from qedcalc.operations.corner import corner_raw_pair_audit
r=corner_raw_pair_audit()
print('Phase-32 corner raw pair bridge')
for d in (r.diagram4,r.diagram5):
    print('diagram',d.diagram,'labels=',d.electron_labels,'q0 powers=',d.q0_denominator_powers,'inner side=',d.inner_vertex_side,'inner props=',d.inner_vertex_propagators)
print('renormalized template:',r.renormalized_outer_template)
print('Phase-32 corner raw pair bridge: PASS')
```
######## QEDCalc の実際の出力

このサンプルを実行すると、主要出力は次である。

```text
diagram 4 labels= ("p'-k", "p'-k-l", "p'-l", 'p-l')
q0 powers= (1, 1, 2, 1, 1)
inner side= left
inner props= ("p'-k-l", "p'-l")

diagram 5 labels= ("p'-k", 'p-k', 'p-k-l', 'p-l')
q0 powers= (2, 1, 1, 1, 1)
inner side= right
inner props= ('p-k-l', 'p-l')
```

数式として言えば、QEDCalc は raw graph を

$$
\begin{aligned}
\mathcal I_i^{\rm raw} \longrightarrow \\
\left( \text{ordered electron momenta}, \text{photon labels}, \text{$q=0$ denominator powers}, \text{inner vertex subgraph} \right)
\end{aligned}
$$

へ分解したことになる。

また、2図を renormalized inner vertex として再結合したときの外側 skeleton として

$$
\gamma^\rho S(p'-k)\gamma_\mu S(p-k)
\overline\Lambda_\rho(p-k,p)\frac{1}{K} +\text{mirror}
$$

に対応する template も返す。

######## この段階で得るもの／次へ渡すもの

この段階ではまだ $F_2(0)$ の値は計算していない。得たものは、

1. 入力した2式の非可換順序が正しく parse できたこと。
2. diagram 4 / 5 のどちらに inner vertex subgraph があるか。
3. $q=0$ でどの denominator が二重になるか。
4. 2図を「renormalized inner vertex + mirror」として扱える topology であること。

である。次節以降では、この topology 情報を使って **inner vertex を on-shell renormalize すること**と、**外側 vertex から $F_2(0)$ を抽出すること**を別々に進める。

###### 2. なぜ bare 2図のままでは計算を閉じないか

####### 2.1 【人が決める】renormalized inner vertex として組み直す

inner vertex subgraph は UV divergent なので、bare vertex をそのまま外側 loop へ入れて最後に一括 subtraction するのではなく、**1ループ on-shell-renormalized inner vertex** として整理してから outer insertion を評価する。

記号的には

$$
\Gamma_\alpha^{(1),\mathrm R} =
\Gamma_\alpha^{(1),\mathrm{bare}} +
\delta\Gamma_\alpha^{(1)}
$$

を外側の1ループ vertex skeleton に挿入する。この局所 subtraction の意味と on-shell scheme の採用は人が理解する必要がある。

###### 3. magnetic projector

####### 3.1 【人が決める】$F_2(0)$ の抽出

######## この段階で導出したい式

vertex correction の計算結果は、そのままでは $F_1$ と $F_2$ を同時に含む。一般の on-shell electromagnetic vertex は

$$
\Gamma_\mu(p',p) =
F_1(q^2)\gamma_\mu +
\frac{i\sigma_{\mu\nu}q^\nu}{2m}F_2(q^2)
$$

である。異常磁気能率に必要なのは $F_2(0)$ なので、ここで人が導出しておくべきものは、**計算した vertex matrix element から $F_1$ を消して $F_2$ だけを取り出す projector** である。

######## Breit frame を選ぶ

運動量移行を $x$ 方向に取り、

$$
q^\mu=(0,q,0,0)
$$

とする。外部電子を on-shell に保つため、対称な Breit frame

$$
p^\mu=
\left(E,-\frac q2,0,0\right),
\qquad
p'^\mu=
\left(E,+\frac q2,0,0\right)
$$

を使う。ここで

$$
E=\sqrt{m^2+\frac{q^2}{4}} =m+O(q^2)
$$

である。

スピンを $z$ 軸上向きに固定し、$\bar uu=1$ の規格化を使うと、$q$ の一次まで

$$
u(p)=
\begin{pmatrix}
1\\
0\\
0\\ -\dfrac{q}{4m}
\end{pmatrix} +O(q^2)
$$

$$
u(p')=
\begin{pmatrix}
1\\
0\\
0\\ +\dfrac{q}{4m}
\end{pmatrix} +O(q^2)
$$

となる。

$q$ は1方向だけなので、vertex の $\mu=0$ と $\mu=2$ 成分は

$$
\Gamma_0 =
F_1(q^2)\gamma_0 +
\frac{i\sigma_{01}q}{2m}F_2(q^2)
$$

$$
\Gamma_2 =
F_1(q^2)\gamma_2 +
\frac{i\sigma_{21}q}{2m}F_2(q^2)
$$

である。

明示的な Dirac 行列と上の spinor を作用させると、

$$
\bar u(p')\Gamma_0u(p) =
F_1(0)+O(q^2)
$$

一方、

$$
\bar u(p')\Gamma_2u(p) = -\frac{iq}{2m}
\left[F_1(0)+F_2(0)\right] +O(q^2)
$$

となる。したがって、

$$
\frac{2mi}{q}
\bar u(p')\Gamma_2u(p) =
F_1(0)+F_2(0)+O(q)
$$

であり、$\Gamma_0$ の matrix element を引けば

$$
\boxed{
F_2(0) =
\lim_{q\to0}
\left[
\frac{2mi}{q}
\bar u(p')\Gamma_2u(p) -
\bar u(p')\Gamma_0u(p)
\right]
}
$$

を得る。

これがこの後 QEDCalc に実装する magnetic projector の物理的入力である。**この projector の選択・導出は人が行い、長大な Dirac 行列積の展開だけを QEDCalc に任せる。**

####### 3.2 【QEDCalc】corner 2図の $q$ 一次 projector polynomial を生成する

######## この段階へ入る式

前節で導出した projector に対し、diagram 4 / 5 の electron chain の $\gamma_\mu$ を $\gamma_0$ と $\gamma_2$ に置き換え、外部 spinor と $q$ 一次展開を作用させる。

プログラムが扱う概念的入力は

$$
\mathcal N_{i,0}(k,l)
\equiv
\bar u(p')\,\mathcal C_i^{\mu=0}(k,l)\,u(p)
$$

および

$$
\mathcal N_{i,2}(k,l;q)
\equiv
\bar u(p')\,\mathcal C_i^{\mu=2}(k,l;q)\,u(p)
$$

である。ここで $i=4,5$、$\mathcal C_i$ は前節 1.1 の非可換 electron chain である。

なお `corner_raw_projector_polynomials()` は関数引数を取らないが、これは入力が無いという意味ではない。Phase 32 で確定した diagram 4 / 5 の topology と、上で導出した Breit-frame projector を関数内部に明示的な Dirac 行列として実装している。

内部では、$m=1$ 単位を使い、

$$
p=(1,0,0,0),
\qquad
q\!\!/=-\gamma^1
$$

として $q$ 一次係数を生成する。$k,l$ の4成分は symbolic variables のまま保持する。

######## QEDCalc が作る出力式

projector 後の多項式は、diagram $i$ ごとに

$$
P_i(k,l) =
2i\,M_{2,i}^{(1)}(k,l) -
M_{0,i}^{(0)}(k,l)
$$

という形で生成される。ここで $M_{2,i}^{(1)}$ は $\Gamma_2$ matrix element の $q$ 一次係数、$M_{0,i}^{(0)}$ は $\Gamma_0$ matrix element の $q^0$ 係数である。

これが、元の数百項 Dirac 代数を置き換える **QEDCalc の機械代数出力**である。

**該当コード：`examples/phase34_corner_raw_projector.py` 1～7 行**

```python
from qedcalc.operations.corner import corner_raw_projector_polynomials
r=corner_raw_projector_polynomials()
print('Phase-34 corner raw magnetic projector')
print('term counts:',r.term_counts)
print('diagram4 base nonzero:',r.diagram4_base!=0,'transverse q0 nonzero:',r.diagram4_transverse_zero!=0)
print('diagram5 base nonzero:',r.diagram5_base!=0,'transverse q0 nonzero:',r.diagram5_transverse_zero!=0)
print('Phase-34 corner raw magnetic projector: PASS')
```
######## 実際に得られる出力

v0.90.0 では

```text
term counts: (('4', 68, 42), ('5', 69, 42))
diagram4 base nonzero: True transverse q0 nonzero: True
diagram5 base nonzero: True transverse q0 nonzero: True
```

を得る。すなわち projector を作用させた $P_4(k,l)$ は68項、$P_5(k,l)$ は69項の多項式になる。また $\Gamma_2$ の $q=0$ transverse base は両図とも42項である。

ここで重要なのは「68項・69項」という数字そのものではない。**前節の人間が導出した projector が、raw electron chain に作用して具体的な loop-momentum polynomial に変換された**ことが出力である。

完全展開式は長大なので本文で手展開しない。必要なら `corner_raw_projector_polynomials()` の

- `diagram4_base`
- `diagram5_base`
- `diagram4_transverse_zero`
- `diagram5_transverse_zero`

を `sp.latex(...)` で出力すれば完全な LaTeX 式を再生成できる。

######## 次段階へ渡すもの

次の Feynman parameter / Gaussian reduction へ渡すのは、この $P_4(k,l)$、$P_5(k,l)$ と各 denominator power である。したがって、ここから先は元資料にあった数百項の gamma 行列展開を人が追い直す必要はない。

###### 4. Feynman parameter family と平方完成

####### 4.1 【人が決める】parameterization の構造

6本の physical propagator を Feynman parameter でまとめ、2つの loop momenta の二次形式を平方完成する。corner では split parameter を保持することで numerator の $q$ dependence と inner/outer subgraph ownership を追えるようにする。

####### 4.2 【QEDCalc】$q=0$ parametric family を生成

######## この段階へ入る入力

前節までで得たものは、

1. diagram 4 / 5 の $q=0$ denominator powers。
2. projector 後の numerator polynomial $P_4(k,l)$、$P_5(k,l)$。
3. $q$ differentiation が終わるまで二重 propagator を区別する必要があるという物理条件。

である。

Feynman parameter を $x,y,z,u,v$ と置くと、loop momenta $k,l$ の二次形式を

$$
a k^2+2c\,k\cdot l+b l^2 -2r\,p\cdot k -2s\,p\cdot l
$$

の形に整理する。QEDCalc へ渡す入力はこの parameter assignment であり、関数は symbolic parameters を受け取る。

**該当コード：`examples/phase33_corner_parametric_family.py` 1～11 行**

```python
from qedcalc.operations.corner import corner_q0_parametric_family
f=corner_q0_parametric_family()
print('Phase-33 corner q=0 parametric family')
print('a=',f.a,'b=',f.b,'c=',f.c,'r=',f.r,'s=',f.s)
print('Delta=',f.Delta)
print('W=',f.W)
print('Omega=',f.Omega)
print('multiplicities diagram4/5=',f.multiplicity4,f.multiplicity5)
print('q derivative diagram4=',f.qderivative4_k,f.qderivative4_l)
print('q derivative diagram5=',f.qderivative5_k,f.qderivative5_l)
print('Phase-33 corner q=0 parametric family: PASS')
```
QEDCalc は $\Delta,W,\Omega$、diagram 4/5 の multiplicity、$q$ derivative data を出す。これが以後の Gaussian/tensor reduction の denominator backbone になる。

###### 5. UV subdivergence と local counterterm

####### 5.1 【人が決める】どの subgraph を subtraction するか

corner の UV divergence は inner vertex subgraph に局在する。したがって、UV scaling chart を選び、bare residue と local $B\gamma$ counterterm residue が一致することを確認する。

####### 5.2 【QEDCalc】bare residue と local residue を exact 比較

######## 入力

入力は Phase 33/34 までに得た parametric denominator family と projector numerator、および人が 5.1 で選んだ inner-vertex UV scaling chart である。局所 counterterm 側には、別紙Aで独立導出した on-shell vertex subtraction の $B\gamma_\rho$ 構造を使う。

bare 側と local 側で比較する量は同じ UV scaling の residue であり、概念的には

$$
R_{\rm bare}(x,y,z;\rho)
\quad\text{and}\quad
R_{B\gamma}(x,y,z;\rho)
$$

である。

######## 出力

QEDCalc は両 residue を同一 variables で symbolic に生成し、

$$
R_{\rm sub}
\equiv
R_{\rm bare}-R_{B\gamma}
$$

を作る。期待する出力は

$$
\boxed{R_{\rm sub}=0}
$$

である。したがってここで得るものは有限値そのものではなく、**inner vertex UV subdivergence が local on-shell counterterm で完全に除去されたこと**である。次節へ渡すのは、この subtraction を施した renormalized inner-vertex kernel である。

**該当コード：`examples/phase35_corner_gaussian_uv_bridge.py` 9～25 行**

```python
print('Phase-35 corner streaming Gaussian + local B-gamma UV bridge')
r=corner_gaussian_bare_templates()
print('G4 compact-template operations:',sp.count_ops(r.G4))
print('G5 compact-template operations:',sp.count_ops(r.G5))
X=sp.Rational(2,5);Y=sp.Rational(1,4);Z=sp.Rational(1,3);rho=sp.Rational(1,7)
expected=sp.Rational(1,2)*X**2*(1-X)/(X**2+rho**2*(1-X))
for d in (4,5):
    bare=corner_uv_residue_sample(d,X,Y,Z,rho)
    uv=corner_local_uv_residue_sample(d,X,Y,Z,rho)
    sub=corner_uv_subtracted_residue_sample(d,X,Y,Z,rho)
    print(f'diagram {d}: bare UV residue =',bare)
    print(f'diagram {d}: local B-gamma residue =',uv)
    print(f'diagram {d}: subtracted residue =',sub)
    assert sp.simplify(bare-expected)==0
    assert sp.simplify(uv-expected)==0
    assert sub==0
print('Phase-35 corner streaming Gaussian + local B-gamma UV bridge: PASS')
```
両 diagram で

$$
R_{\mathrm{bare}}-R_{B\gamma}=0
$$

となり、subtracted residue が0になる。ここは「発散を数値的に小さくした」のではなく symbolic exact cancellation である。

###### 6. renormalized inner vertex の sector 分解

####### 6.1 【接続】1ループ renormalization の出力を outer loop へ渡す

元資料で導出した1ループ vertex renormalization では、inner vertex を $K$ sector、$z$ sector、$\kappa$ sector などへ分解する。この分解は発散 cancellation と有限部分の ownership を明確にするためである。

####### 6.2 【QEDCalc】sector identities を監査する

######## 入力

入力は前節で UV subtraction 済みとなった inner vertex を、元計算資料で導出した $K$ sector、$z$ sector、$\kappa$ sector に分けた式である。ここでは sector 分解そのものの物理的意味は人が決め、QEDCalc は各 sector の代数恒等式を検査する。

######## 出力

QEDCalc は

$$
\overline\Lambda_\rho^{(1),R} =
\Lambda_{\rho,K} +
\Lambda_{\rho,z} +
\Lambda_{\rho,\kappa}
$$

に対応する各 scalar coefficient を返し、$z$ 積分 identity、$\kappa$ denominator identity、on-shell で消える scalar combination の residual を計算する。出力 residual がすべて0であることにより、この sector representation を outer loop の入力として使用できる。

**該当コード：`examples/phase36_corner_renormalized_inner_vertex_bridge.py` 9～23 行**

```python
print('Phase-36 corner renormalized-inner-vertex sector bridge')
r=corner_renormalized_inner_vertex_sectors()
print('K sector:', r.K_sector)
print('z sector closed:', r.z_sector_closed)
print('kappa sector:', r.kappa_sector)
print('gamma total:', r.gamma_sector_closed)
print('z integral residual:', corner_inner_vertex_z_integral_residual())
print('kappa denominator identity residual:', corner_inner_vertex_kappa_difference_residual())
L0=sp.Symbol('L0', positive=True)
print('on-shell scalar coefficients:', corner_inner_vertex_sector_scalar_coefficients(lambda0_sq=L0,lambda_prime_sq=L0))
assert corner_inner_vertex_z_integral_residual() == 0
assert corner_inner_vertex_kappa_difference_residual() == 0
c=corner_inner_vertex_sector_scalar_coefficients(lambda0_sq=L0,lambda_prime_sq=L0)
assert all(sp.simplify(c[k]) == 0 for k in ('z_log','kappa_difference','gamma_total'))
print('Phase-36 corner renormalized-inner-vertex sector bridge: PASS')
```
$z$ integral residual、$\kappa$ denominator identity residual、on-shell scalar coefficients が0になることを確認する。これにより inner vertex の subtraction を outer calculation に渡す境界が固定される。

###### 7. soft IR sector

####### 7.1 【人が決める】photon mass regulator を残す

corner は IR divergent なので $\rho=\lambda/m$ を最後まで保持する。soft scaling を先に取り、$\ln(1/\rho)$ の係数を独立に取り出す。

####### 7.2 【QEDCalc】soft kernel と IR coefficient

######## 入力

入力は renormalized corner kernel の soft scaling limit である。人が 7.1 で $\rho=\lambda/m$ を残すと決めた後、QEDCalc には soft variables $U,R,S,v$ で書かれた leading kernel を渡す。

######## 出力

QEDCalc が最初に返すのは、まだ積分していない soft density

$$
\mathcal S(U,R,S,v)
$$

である。次に $S$ 積分、$R$ 積分を順に行い、logarithmic radial integral の係数を取り出す。最終的なこの節の出力は

$$
\boxed{C_{\rm IR}^{\rm C}=1}
$$

であり、corner contribution が

$$
A_{\rm C}^{\rm IR}=+\ln\frac1\rho
$$

を持つことを意味する。同時に diagnostic soft finite constant $C_{\rm soft}$ も返すが、これは ownership を確認するための量で、後で二重加算してはいけない。

メイン trial は次を計算する。

**該当コード：`examples/corner_2loop_trial.py` 32～38 行**

```python
U,R,S,v = sp.symbols("U R S v", positive=True)
s.equation("Leading physical-measure soft kernel", sp.latex(corner_soft_kernel(U,R,S,v)))
s.equation("S-integrated soft kernel", sp.latex(corner_soft_integrate_S(R,v)))
s.equation("Exact coefficient of log(1/rho)", sp.latex(corner_soft_ir_coefficient()))
s.equation("Diagnostic soft finite constant", sp.latex(corner_soft_finite_constant()))
s.equation("Diagnostic hard remainder", sp.latex(corner_hard_remainder_from_soft_split()))
s.equation("Soft+hard diagnostic split difference", sp.latex(corner_soft_hard_split_difference()))
```
QEDCalc は leading physical-measure soft kernel を $S$ で積分し、さらに残りを積分して

$$
C_{\mathrm{IR}}^{\mathrm C}=+1
$$

を exact に得る。つまり corner は $+\ln(1/\rho)$ を持つ。

###### 8. momentum shift correction と hard/z sectors

####### 8.1 【人が理解する】shift で numerator も変わる

平方完成で loop momentum を shift すると denominator だけでなく numerator の $p'-k$ も変わる。これを落とすと finite constant が変わる。

メイン trial は shift を

**該当コード：`examples/corner_2loop_trial.py` 40～48 行**

```python
u = sp.Symbol("u")
coeff = corner_shifted_p_minus_k(u,v)
shift_tex = (
    r"p'-k\;\longrightarrow\;"
    + sp.latex(coeff['p_prime']) + r"\,p'"
    + sp.latex(coeff['p_double_prime']) + r"\,p''"
    + r"-k"
)
s.equation("Common momentum-shift action on p'-k", shift_tex)
```
として明示する。

####### 8.2 【QEDCalc】解析 sector を合成する

######## 入力

入力は、(i) primary hard-sector kernel、(ii) 8.1 の momentum shift によって生じる numerator correction、(iii) $z$ sector の3組である。これらは互いに異なる由来を持つので、QEDCalc では別関数として評価してから最後に足す。

######## 出力

QEDCalc は

$$
H_{K\kappa}^{(1)},
\qquad
\Delta A_{\rm shift},
\qquad
A_z
$$

を返し、

$$
H_{K\kappa} =
H_{K\kappa}^{(1)}+\Delta A_{\rm shift}
$$

$$
A_{\rm C,fin} =
H_{K\kappa}+A_z
$$

を構成する。ここで `corner_result_difference()` の出力0が、独立 closed form と完全一致したことを意味する。次節へ渡すのは $A_{\rm C,fin}$ と soft/hard ownership 情報である。

**該当コード：`examples/corner_2loop_trial.py` 50～63 行**

```python
h1 = corner_hard_primary_result()
ds = corner_shift_correction_result()
h = corner_hard_total_result()
z = corner_z_sector_result()
finite = corner_finite_result()
expected = corner_expected_finite_result()

s.equation("Primary K+kappa^2 hard-sector group", sp.latex(h1))
s.equation("Momentum-shift correction", sp.latex(ds))
s.equation("Complete K+kappa^2 hard sector", sp.latex(h))
s.equation("z sector", sp.latex(z))
s.equation("Corner finite part", sp.latex(finite))
s.equation("Independent closed-form checkpoint", sp.latex(expected))
s.equation("Difference", sp.latex(corner_result_difference()))
```
主要出力は primary hard sector、shift correction、complete hard sector、$z$ sector、finite part である。

finite part は

$$
A_{\mathrm C,fin} = -\frac{67}{24} +
\frac{\pi^2}{18} -
\frac12\zeta(3) +
\frac{\pi^2}{3}\ln2
$$

となる。

###### 9. soft/hard ownership

corner では一時期、数値 route が finite total ではなく hard remainder を返していることが判明した。現在は

$$
A_{\mathrm C,fin}=H_{\mathrm{fin}}+C_{\mathrm{soft}}
$$

という ownership を exact に監査し、soft finite constant を二重加算しないよう固定している。メイン trial の soft/hard diagnostic split residual が0であることがこの確認に相当する。

###### 10. self-energy insertion との IR 相殺

####### 10.1 【QEDCalc】log coefficient を pair で検査する

######## 入力

入力は corner 側で独立に得た

$$
C_{\rm IR}^{\rm C}=+1
$$

と、self-energy insertion 側の raw-to-final audit から得た

$$
C_{\rm IR}^{\rm S}=-1
$$

である。同じ regulator $\rho=\lambda/m$ と同じ $\ln(1/\rho)$ convention に直してから比較する。

######## 出力

QEDCalc は

$$
C_{\rm IR}^{\rm total} =
C_{\rm IR}^{\rm C}+C_{\rm IR}^{\rm S}
$$

を作り、

$$
\boxed{C_{\rm IR}^{\rm total}=0}
$$

を返す。同時に有限部も加算し、IR regulator を除去しても残る有限 combination を出力する。

**該当コード：`examples/corner_2loop_trial.py` 65～73 行**

```python
rho = sp.Symbol("rho", positive=True)
s.equation("Corner asymptotic coefficient A_C(rho)", sp.latex(corner_full_asymptotic(rho)))
irc = corner_self_energy_ir_cancellation()
s.equation("Corner IR-log coefficient", sp.latex(irc.corner_log_coefficient))
s.equation("Self-energy insertion IR-log coefficient", sp.latex(irc.self_energy_log_coefficient))
s.equation("Combined IR-log coefficient", sp.latex(irc.total_log_coefficient))
s.equation("Combined finite part after IR cancellation", sp.latex(irc.combined_finite))

s.text("Result", "PASS: the independently derived corner-sector decomposition and the self-energy IR cancellation are reproduced exactly.")
```
current convention では

$$
C_{\mathrm{IR}}^{\mathrm C}=+1,\qquad C_{\mathrm{IR}}^{\mathrm S}=-1
$$

なので合計0である。これは self-energy 資料の符号監査済み表記と一致する。

###### 11. Phase 77 release checkpoint

Phase 77 は sector route と soft/hard route の2本が同じ closed form に到達すること、さらに IR cancellation をまとめて exact check する。通常の regression ではこの Phase を使う。

###### 12. 現在の自動化境界

| 段階 | 状況 | 担当 |
|---|---|---|
| 2つの raw diagram の式 | 人が確認 | 人 |
| raw topology pair audit | 自動 | QEDCalc |
| magnetic projector の物理的選択 | 人 | 人 |
| raw projector polynomial | 自動 | QEDCalc |
| parametric family / square completion data | 自動 | QEDCalc |
| inner vertex を on-shell renormalize する方針 | 人 | 人 |
| local UV residue/counterterm residual | 自動 | QEDCalc |
| soft scaling の物理的解釈 | 人 | 人 |
| soft coefficient / hard / z sector | 自動 | QEDCalc |
| final closed form / IR cancellation | 自動 | QEDCalc |

###### 13. 最短再計算手順

1. Phase 32 で raw 2図 topology を確認。
2. Phase 34 で projector を確認。
3. Phase 33/35/36 で parametric family と UV subtraction を確認。
4. 必要に応じ Phase 42～76 の詳細 audits で ownership/sign/overlap を追う。
5. `corner_2loop_trial.py` で analytic sectors を確認。
6. Phase 77 または `run_v090_validation.bat` で completion regression を確認。

###### 14. この資料で省略できた手計算

6 denominator の展開、数百項の Dirac/Lorentz algebra、Gaussian tensor reduction、UV scaling residue の項別比較、soft overlap の大量の局所展開、hard/z sector の単純代数は QEDCalc の Phase 群へ移した。一方、**どの subgraph を renormalize するか、soft/hard をどう定義するか、IR regulator をいつ外すか**という物理判断は本文に残した。

###### 15. 参照元と再実行ファイル

- 元計算資料：`corner_2図_F2_4/00_IIc_Feynman図から最終結果までの詳細導出_本文_修正版_全体見直し修正版.md`
- 1-loop renormalization/projector：`01_別紙A_...補助計算追記.md`
- parameter/Dirac/UV：`02_別紙B_...md`
- finite analytic evaluation：`03_別紙C_...md`
- self-energy IR cancellation：`04_別紙D_...md`
- raw inputs：`input/corner_4_2loop_bare_feynman_gauge.tex`、`input/corner_5_2loop_bare_feynman_gauge.tex`
- main sample：`examples/corner_2loop_trial.py`
- raw pair：Phase 32
- parametric family：Phase 33
- raw projector：Phase 34
- Gaussian/UV bridge：Phase 35
- renormalized inner vertex：Phase 36
- detailed sign/ownership/overlap audits：Phase 37～76
- release closure：Phase 77

代表実行は `run_corner_2loop_demo.bat` と `run_phase77_corner_end_to_end_checkpoint.bat`。途中の疑義を再監査するときだけ対応 Phase の `.bat` を使う。


---

###### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

#### 3. Recorded runtime artifacts

| Artifact | Type | Lines | Bytes |
| --- | --- | ---: | ---: |
| `output/corner_2loop_trial.md` | `md` | 125 | 2715 |

#### 4. Recorded Markdown stages

##### 4.1 `output/corner_2loop_trial.md`

##### QEDCalc corner (IIc) two-loop trial

Generated: 2026-08-22T10:21:01

###### Scope

This trial starts from the independently derived UV-finite parameter representation and its sector decomposition. The complete six-denominator magnetic-projector integrand is not yet regenerated automatically from the original two-loop LaTeX expression. The trial verifies the soft IR coefficient, the momentum-shift correction, the hard/z-sector analytic bookkeeping, and the self-energy IR cancellation.

###### Leading physical-measure soft kernel

$$
\frac{2 R S U v \left(4 R + S + 4 v\right)}{\left(R + v\right)^{2} \left(U^{2} + 1\right) \left(R + S + v\right)^{4}}
$$

###### S-integrated soft kernel

$$
\frac{2 R v}{\left(R + v\right)^{3}}
$$

###### Exact coefficient of log(1/rho)

$$
1
$$

###### Diagnostic soft finite constant

$$
- \log{\left(8 \right)} - \frac{7}{4} + \log{\left(2 \right)}^{2} + \frac{\pi^{2}}{6}
$$

###### Diagnostic hard remainder

$$
- \frac{\pi^{2}}{9} - \frac{25}{24} - \frac{\zeta\left(3\right)}{2} - \log{\left(2 \right)}^{2} + \log{\left(2^{3 + \frac{\pi^{2}}{3}} \right)}
$$

###### Soft+hard diagnostic split difference

$$
0
$$

###### Common momentum-shift action on p'-k

$$
p'-k\;\longrightarrow\;- u v + 1\,p'u v - u\,p''-k
$$

###### Primary K+kappa^2 hard-sector group

$$
- \frac{19}{3} - \frac{15 \zeta\left(3\right)}{8} + \frac{11 \pi^{2}}{36} + \frac{3 \pi^{2} \log{\left(2 \right)}}{4}
$$

###### Momentum-shift correction

$$
- \frac{\pi^{2}}{4} - \frac{\pi^{2} \log{\left(2 \right)}}{6} + \frac{3 \zeta\left(3\right)}{4} + \frac{8}{3}
$$

###### Complete K+kappa^2 hard sector

$$
- \frac{11}{3} - \frac{9 \zeta\left(3\right)}{8} + \frac{\pi^{2}}{18} + \frac{7 \pi^{2} \log{\left(2 \right)}}{12}
$$

###### z sector

$$
- \frac{\pi^{2} \log{\left(2 \right)}}{4} + \frac{5 \zeta\left(3\right)}{8} + \frac{7}{8}
$$

###### Corner finite part

$$
- \frac{67}{24} - \frac{\zeta\left(3\right)}{2} + \frac{\pi^{2}}{18} + \frac{\pi^{2} \log{\left(2 \right)}}{3}
$$

###### Independent closed-form checkpoint

$$
- \frac{67}{24} - \frac{\zeta\left(3\right)}{2} + \frac{\pi^{2}}{18} + \frac{\pi^{2} \log{\left(2 \right)}}{3}
$$

###### Difference

$$
0
$$

###### Corner asymptotic coefficient A_C(rho)

$$
\log{\left(\frac{2^{\frac{\pi^{2}}{3}}}{\rho} \right)} - \frac{67}{24} - \frac{\zeta\left(3\right)}{2} + \frac{\pi^{2}}{18}
$$

###### Corner IR-log coefficient

$$
1
$$

###### Self-energy insertion IR-log coefficient

$$
-1
$$

###### Combined IR-log coefficient

$$
0
$$

###### Combined finite part after IR cancellation

$$
- \frac{7}{3} - \frac{\zeta\left(3\right)}{2} + \frac{\pi^{2} \log{\left(2 \right)}}{3}
$$

###### Result

PASS: the independently derived corner-sector decomposition and the self-energy IR cancellation are reproduced exactly.

---

#### 5. Large algebra/reduction files

No graph-specific CSV/TXT artifact is currently stored.

#### 6. Release-layer status

No Phase 77 Markdown artifact is currently stored; rerun that scientific phase when a freshly regenerated checkpoint is required.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.

---

### 2.4 Self-energy insertion pair

Source: `output/2loop_self_energy_full.md`

### QEDCalc two-loop full process report: Self-energy insertion pair

Diagram multiplicity: **2**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

#### 1. Raw input expressions

##### `input/self_energy_insertion_left_2loop_bare.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma^\beta \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \\
\gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \left( -\left( g_{\rho\sigma} +(1-\alpha)\frac{k_\rho k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\left( -\left( g_{\alpha\beta} +(1-\alpha)\frac{l_\alpha l_\beta}{-l^2-i\varepsilon} \right) \frac{1}{-l^2-i\varepsilon} \right)
\end{aligned}
$$

##### `input/self_energy_insertion_right_2loop_bare.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \\
\gamma^\beta \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \left( -\left( g_{\rho\sigma} +(1-\alpha)\frac{k_\rho k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\left( -\left( g_{\alpha\beta} +(1-\alpha)\frac{l_\alpha l_\beta}{-l^2-i\varepsilon} \right) \frac{1}{-l^2-i\varepsilon} \right)
\end{aligned}
$$

##### `input/self_energy_subloop_numerator.tex`

$$
\gamma^\alpha
\left(
m+\rlap{/}r-\rlap{/}l
\right)
\gamma_\alpha
$$

#### 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/04_self_energy_insertion_2図_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

##### QEDCalc サンプルプログラム説明書兼計算過程説明書：self-energy insertion 2図

###### 0. この資料の目的

外部 vertex の左右電子 propagator に1ループ electron self-energy を挿入する2図について、raw diagram の自動検出、subloop contraction、on-shell counterterm、UV cancellation、finite part、IR logarithm、corner との相殺までを説明する。この図群は QEDCalc が raw 2図から subdiagram をかなり直接的に抽出できる例である。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **self-energy insertion 2図** である。

本資料では各段階を次の3種類に区別する。

- **【人が決める】**：diagram の同定、Feynman gauge の採用、on-shell 条件、どの form factor を求めるか、どの変数変換を行うかなど、物理的意味を伴う選択。
- **【QEDCalc】**：LaTeX parse、Dirac 代数、loop shift、odd 項除去、tensor reduction、IBP、式の簡約、解析積分の機械的部分、residual の exact check など。
- **【接続】**：人が導出した式を QEDCalc の入力形式へ移す、または QEDCalc の出力を次の物理的段階へ解釈する部分。

重要なのは、QEDCalc は Feynman 図の意味を勝手に推測して全計算をブラックボックス処理するプログラムではないことである。**処理順序は人が決め、長大で機械的な代数を QEDCalc/SymPy に渡す**。QEDCalc の設計思想もこの分離にある。

###### 0.1 この資料の読み方

各計算段階では原則として次の順序で記載する。

1. なぜ次の処理が必要か。
2. 人が導出・選択しなければならない内容。
3. QEDCalc に渡す LaTeX または数式入力。
4. 実際のサンプルプログラムのファイル名と行番号。
5. QEDCalc の主要出力。
6. その出力を次の段階でどう使うか。

したがって、コードブロックだけを飛び飛びに読むのではなく、**「入力式がなぜその形になるか」→「コード」→「出力の物理的意味」**の順に読む。

###### 0.2 数式と規約

- 外部電子は on-shell とする。
- 電子質量を $m$ とする。
- 外部 photon momentum は $q=p'-p$ とする。
- anomalous magnetic moment は Pauli form factor $F_2(0)$ から得る。
- 必要な箇所では $D$ 次元を保持し、最後に $D\to4$ を取る。
- IR 正則化が必要な図では photon mass $\lambda$ と $\rho=\lambda/m$ を用いる。


###### 0.3 本資料での「人」と「QEDCalc」の受け渡しの書き方

この資料では、計算の各段階を単に「人が行う」「QEDCalc が行う」と分類するだけではなく、必ず次の受け渡しを明示する。

1. **前段階から入ってくる式・データ**：この段階を始める時点で何が既知なのか。
2. **人が用意する入力**：Feynman 図の読み取り、運動学、renormalization 条件、変数変換など、物理的・解析的判断を伴う部分。
3. **QEDCalc に実際に渡る入力**：LaTeX ファイル、SymPy 式、index table、parameter family など、プログラムが直接受け取るもの。
4. **サンプルコード**：QEDCalc v0.90.0 のどのファイルの何行が処理を行うか。
5. **QEDCalc の出力**：数式として何が得られ、どの residual / term count / table が検算されるか。
6. **次段階へ渡すもの**：得られた出力のうち、次の物理計算で実際に使用するもの。

したがって、関数が引数なしで呼ばれている場合も「入力なし」という意味ではない。関数内部で `input/*.tex` を読む場合、あるいは前段階で確定した topology・kinematics が関数内部に実装されている場合は、それを明示する。

また、長大な数十～数百項の多項式を QEDCalc が生成する場合、本資料ではその多項式を人が再び手計算することを目的としない。その場合でも、**何という多項式を生成したか、その数学的定義、項数、入力変数、次段階での使われ方**は必ず記載する。完全展開式は QEDCalc の生成物として再出力できる形を保つ。


###### 0.4 全工程の入出力一覧

| 工程 | 人が用意・判断するもの | QEDCalc に渡る入力 | QEDCalc の主な出力 | 次へ渡すもの |
|---|---|---|---|---|
| raw pair | left/right insertion の electron-chain 順序 | complete raw two-loop LaTeX 2図 | insertion side、$r=p-k$ または $p'-k$、subloop match | $S(r)\Sigma(r)S(r)$ |
| numerator reduction | Feynman gauge の subloop を選ぶ | $\gamma^\alpha(m+\rlap{/}r-\rlap{/}l)\gamma_\alpha$ | $4m-2\rlap{/}r+2\rlap{/}l$、shift 後 odd-term removal | scalar self-energy numerator |
| on-shell renormalization | pole mass / residue 条件 | $\Sigma(r)=mA+\rlap{/}rB$ | $\delta m$, $\delta Z_2$, UV residual $0$, $\Sigma_R$ | renormalized insertion |
| logarithm rationalization | log を parameter integral に戻す方針 | renormalized logarithmic kernel | rational prefactor / denominator | finite multi-parameter integrand |
| finite part | integration order | $G_A$ | $A_A(0)=-1/24-\pi^2/18$ | finite contribution |
| IR part | $\rho\to0$ 前に asymptotic を取る | $A_B(\rho)$ kernel | $A_B=\ln\rho+1/2+o(1)$ | IR coefficient + finite constant |
| pair assembly | left/right 2図を足す | $A_A+A_B$ | $A_S=\ln\rho+11/24-\pi^2/18$ | self-energy pair |
| corner cancellation | regulator convention を揃える | $-\ln(1/\rho)$ と corner $+\ln(1/\rho)$ | residual $0$ | finite 2-loop sum |

全体は

$$
(\mathcal I_{S,L}^{\rm raw},\mathcal I_{S,R}^{\rm raw})
\longrightarrow
S\Sigma_R S
\longrightarrow
A_A+A_B
\longrightarrow
A_S
$$

である。

###### 1. 元の入力となる2図

####### 1.1 【人が決める】right insertion

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \\
\gamma^\beta \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \left( -\left( g_{\rho\sigma} +(1-\alpha)\frac{k_\rho k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\left( -\left( g_{\alpha\beta} +(1-\alpha)\frac{l_\alpha l_\beta}{-l^2-i\varepsilon} \right) \frac{1}{-l^2-i\varepsilon} \right)
\end{aligned}
$$

####### 1.2 【人が決める】left insertion

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma^\beta \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \\
\gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \left( -\left( g_{\rho\sigma} +(1-\alpha)\frac{k_\rho k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\left( -\left( g_{\alpha\beta} +(1-\alpha)\frac{l_\alpha l_\beta}{-l^2-i\varepsilon} \right) \frac{1}{-l^2-i\varepsilon} \right)
\end{aligned}
$$

両図の特徴は、self-energy subloop の前後で同じ outer electron propagator が繰り返され、内部に1本の electron propagator と photon propagator が挿入されることである。

###### 2. raw diagram から self-energy subdiagram を見つける

####### 2.1 【QEDCalc】pattern detection と contraction

メイン trial の最初の部分は、2つの complete raw RHS を parse し、self-energy block を検出する。

**該当コード：`examples/self_energy_insertion_2loop_trial.py` 23～37 行**

```python
ROOT=Path(__file__).resolve().parents[1]
raw_right_path=ROOT/'input/self_energy_insertion_right_2loop_bare.tex'
raw_left_path=ROOT/'input/self_energy_insertion_left_2loop_bare.tex'
raw_right=parse_loop_integral_latex(raw_right_path.read_text(encoding='utf-8'))
raw_left=parse_loop_integral_latex(raw_left_path.read_text(encoding='utf-8'))
right_match=find_self_energy_subdiagrams(raw_right)[0]
left_match=find_self_energy_subdiagrams(raw_left)[0]
right_red=contract_self_energy_subdiagram(raw_right)
left_red=contract_self_energy_subdiagram(raw_left)
source_path=ROOT/'input/self_energy_subloop_numerator.tex'
out_path=ROOT/'output/self_energy_insertion_2loop_trial.md'
source=source_path.read_text(encoding='utf-8').strip()
expr=parse_latex(source)
expanded=normalize_noncommutative_products(expand_expression(expr))
reduced=simplify_expression(contract_gamma(expanded))
```
`find_self_energy_subdiagrams()` は repeated outer electron propagator pattern を使い、left/right、subloop momentum、external electron momentum を記録する。`contract_self_energy_subdiagram()` は内部 block の numerator を抽出する。

ここでの重要点は、**人が subdiagram を手で切り出した式だけを入力する必要がない**ことである。complete raw diagram から topology pattern を見つけられる。

###### 3. self-energy numerator の Dirac 代数

####### 3.1 【接続】subloop numerator

Feynman gauge の metric part では numerator は

$$
\gamma^\alpha
\left(
m+\rlap{/}r-\rlap{/}l
\right)
\gamma_\alpha
$$

である。

####### 3.2 【QEDCalc】gamma contraction、shift、odd 項除去

######## 入力

入力は subloop numerator

$$
\gamma^\alpha(m+\rlap{/}r-\rlap{/}l)\gamma_\alpha
$$

と、electron/photon denominator をまとめる Feynman parameter $a$ である。

######## 出力

4次元 Clifford algebraから

$$
\gamma^\alpha\gamma_\alpha=4,
\qquad
\gamma^\alpha\rlap{/}v\gamma_\alpha=-2\rlap{/}v
$$

を使い、QEDCalc は

$$
4m-2\rlap{/}r+2\rlap{/}l
$$

を得る。さらに $l=t+ar$ と shift し、odd-$t$ を除去して

$$
4m-2\rlap{/}r+2a\rlap{/}r
$$

を次段階へ渡す。

**該当コード：`examples/self_energy_insertion_2loop_trial.py` 35～46 行**

```python
expr=parse_latex(source)
expanded=normalize_noncommutative_products(expand_expression(expr))
reduced=simplify_expression(contract_gamma(expanded))

a_sym=Symbol('a')
completed=CompletedSquare(
    loop=Vector('l'),
    shift=VectorLinearCombination(((a_sym, Vector('r')),)),
    remainder=Symbol('0'),
)
shifted=expand_commutative(shift_loop_momentum_in_numerator(reduced, completed, new_loop='t'))
even=simplify_expression(drop_odd_loop_terms(shifted, loop='t'))
```
最初の gamma contraction は

$$
\gamma^\alpha(m+\rlap{/}r-\rlap{/}l)\gamma_\alpha =
4m-2\rlap{/}r+2\rlap{/}l
$$

を返す。Feynman parameter $a$ を導入して $l=t+ar$ と shift し、odd $t$ 項を落とす。この部分は完全に機械代数である。

###### 4. on-shell renormalization

####### 4.1 【人が決める】renormalization condition

self-energy を

$$
\Sigma(r)=mA(r^2)+\rlap{/}r B(r^2)
$$

と分解し、physical pole の位置と residue が変わらない on-shell condition を課す。これから mass counterterm と wave-function counterterm が決まる。

QEDCalc では denominator

$$
\Delta(a,r^2)=a m^2+a(a-1)r^2+(1-a)\lambda^2
$$

と on-shell denominator

$$
\Delta_0(a)=a^2m^2+(1-a)\lambda^2
$$

を使う。

####### 4.2 【QEDCalc】UV cancellation と compact outer diagram

######## 入力

入力は $\Sigma(r)=mA(r^2)+\rlap{/}rB(r^2)$ の parameter 表示と、4.1で人が指定した on-shell 条件である。

######## 出力

QEDCalc は $A(m^2),B(m^2)$ と derivatives から $\delta m,\delta Z_2$ を構成し、renormalized numerator の UV coefficient が0になることを確認する。その後 complete two-loop graph を

$$
\gamma^\rho S(p'-k)\gamma_\mu S(r)\Sigma_R(r)S(r)\gamma_\rho D(k)
$$

という compact outer diagram に変換する。

**該当コード：`examples/self_energy_insertion_2loop_trial.py` 48～67 行**

```python
a,z,b,q,r2,m,lam,rslash,rho=sp.symbols('a z b q r2 m lambda rslash rho', positive=True)
delta=self_energy_delta(a,r2,m,lam)
delta0=self_energy_delta0(a,m,lam)
uv=sp.simplify(uv_cancellation_numerator(a,m,rslash))
conventions=load_conventions(ROOT/'conventions.txt')
outer_prefactor=conventions.compact_outer_one_loop_prefactor_latex()
right_compact_bare=contract_self_energy_to_outer_loop(raw_right, conventions=conventions, renormalized=False)
left_compact_bare=contract_self_energy_to_outer_loop(raw_left, conventions=conventions, renormalized=False)
right_compact_ren=contract_self_energy_to_outer_loop(raw_right, conventions=conventions, renormalized=(uv==0))
left_compact_ren=contract_self_energy_to_outer_loop(raw_left, conventions=conventions, renormalized=(uv==0))
logden=log_ratio_parameter_kernel(a,z,r2,m,lam)
logpref=log_ratio_prefactor(a,r2,m)
GA=finite_four_parameter_integrand(a,z,b,q)
B=finite_b_integrated_kernel(a,z,q)
F=finite_one_variable_kernel(a)
num=finite_part_numeric(55)
recognized=finite_part_recognize(num,50)
expected=finite_part_expected()
ir=ir_part_asymptotic(rho)
total=total_self_energy_coefficient(rho)
```
`uv_cancellation_numerator()` が0になることで、on-shell counterterm 後の UV numerator が代数的に消える。その後 `contract_self_energy_to_outer_loop(..., renormalized=True)` により $S\Sigma_R S$ を含む compact outer diagram へ変換する。

###### 5. logarithm を rational parameter integral に戻す

####### 5.1 【人が理解する】なぜ rationalization するか

renormalized self-energy には $\ln(\Delta/\Delta_0)$ が現れる。このまま外側 Feynman parameter 積分へ入れるより、補助 parameter $z$ を使って rational integrand に戻した方が QEDCalc の代数処理と積分 reduction を適用しやすい。

####### 5.2 【QEDCalc】log prefactor と denominator

######## 入力

入力は on-shell subtraction 後に残る logarithmic difference である。

######## 出力

QEDCalc は恒等式を使って log を追加 parameter $z$ の rational integral に戻し、分子 prefactor と denominator を別々の symbolic expression として返す。これにより後段の多変数積分を純粋な rational integrand $G_A$ として扱える。

メイン trial の `log_ratio_prefactor()` と `log_ratio_parameter_kernel()` がこの入力を作り、finite 4-parameter integrand $G_A$ へ接続する。コードは上の48～67行に含まれる。

###### 6. finite part $A_A$

####### 6.1 【QEDCalc】4変数 integrand → 1変数 kernel

######## 入力

入力は rationalized finite four-parameter integrand $G_A(a,b,q,z)$ である。

######## 出力

QEDCalc は解析的に積分可能な parameter を順に消去し、最終的に1変数 kernel とその definite integral を得る。finite sector の出力は

$$
\boxed{A_A(0)=-\frac1{24}-\frac{\pi^2}{18}}
$$

である。

メイン trial では

- `finite_four_parameter_integrand(a,z,b,q)`
- `finite_b_integrated_kernel(a,z,q)`
- `finite_one_variable_kernel(a)`
- `finite_part_numeric()`
- `finite_part_recognize()`

を順に呼ぶ。該当コードは 60～65 行である。

出力される finite part は

$$
A_A(0) = -\frac1{24} -
\frac{\pi^2}{18}
$$

である。

###### 7. IR part $A_B$

####### 7.1 【人が決める】$\rho$ を0にする前に asymptotic を取る

IR sector は photon mass regulator $\rho$ を持つ。積分の前に単純に $\rho=0$ としてはいけない。QEDCalc は small-$\rho$ asymptotic を

$$
A_B(\rho) =
\ln\rho +
\frac12 +o(1)
$$

として保持する。

####### 7.2 【QEDCalc】finite + IR を合成する

######## 入力

入力は finite sector $A_A(0)$ と、photon-mass regulator を保持した IR sector $A_B(\rho)$ である。

######## 出力

QEDCalc は

$$
A_B(\rho)=\ln\rho+\frac12+o(1)
$$

を得て、

$$
A_S(\rho)=A_A(0)+A_B(\rho)
$$

を構成する。したがって

$$
\boxed{A_S(\rho)=\ln\rho+\frac{11}{24}-\frac{\pi^2}{18}+o(1)}
$$

がこの節の出力である。

メイン trial の 66～67 行が `ir_part_asymptotic()` と `total_self_energy_coefficient()` を呼ぶ。結果は

$$
A_{\mathrm S}(\rho) =
\ln\rho +
\frac{11}{24} -
\frac{\pi^2}{18}
$$

であり、同値な表記は

$$
A_{\mathrm S}(\rho) = -\frac12\ln\rho^{-2} +
\frac{11}{24} -
\frac{\pi^2}{18}
$$

である。

###### 8. raw-to-final audit

Phase 31 は raw sample checks、raw UV archived difference、renormalized $G_A$ residual、finite、IR、total を一括で監査する。

**該当コード：`examples/phase31_self_energy_raw_to_final.py` 1～12 行**

```python
from qedcalc.operations.self_energy import self_energy_raw_to_final_audit
r=self_energy_raw_to_final_audit()
print('Phase-31 self-energy raw-to-final audit')
print('Raw sample checks:',r.raw_sample_checks)
print('Raw UV archived difference:',r.raw_uv_archived_difference)
print('Renormalized G_A residual:',r.renormalized_GA_residual)
print('Finite A:',r.finite_A)
print('IR B:',r.ir_B)
print('Total:',r.total)
print('Final checkpoint residual:',r.total_checkpoint_residual)
ok=all(x==0 for x in r.raw_sample_checks) and r.raw_uv_archived_difference==0 and r.renormalized_GA_residual==0 and r.total_checkpoint_residual==0
print('Phase-31 self-energy raw-to-final audit: PASS' if ok else 'FAIL')
```
最終 checkpoint residual が0なら、raw 2図から downstream analytic result までの接続が閉じている。

###### 9. corner との IR cancellation

corner は $+\ln(1/\rho)$、self-energy pair は $-\ln(1/\rho)$ を持つ。したがって

$$
\ln\frac1\rho+\ln\rho=0
$$

となる。current QEDCalc ではこの符号を Phase 80 で固定しており、旧資料に存在した逆符号表記は採用しない。

Phase 80 の core checks は raw sample residual、UV residual、renormalized $G_A$ residual、total residual、IR cancellation residual をすべて0と要求する。

**該当コード：`examples/phase80_self_energy_end_to_end_checkpoint.py` 1～11 行**

```python
from pathlib import Path
import sympy as sp
from qedcalc.operations.self_energy import self_energy_phase80_end_to_end_checkpoint
rho=sp.Symbol('rho', positive=True)
c=self_energy_phase80_end_to_end_checkpoint(rho)
checks=[
    all(x==0 for x in c.raw_sample_residuals),
    c.raw_uv_residual==0,
    c.renormalized_GA_residual==0,
    c.total_residual==0,
    c.ir_cancellation_residual==0,
```
###### 10. 現在の自動化境界

| 段階 | 状況 | 担当 |
|---|---|---|
| left/right raw Feynman expression | 人が確認 | 人 |
| subdiagram pattern detection | 自動 | QEDCalc |
| gamma contraction / loop shift | 自動 | QEDCalc |
| on-shell scheme の選択 | 人 | 人 |
| counterterm algebra / UV residual | 自動 | QEDCalc |
| logarithm rationalization | 自動 | QEDCalc |
| finite multi-parameter integrals | 自動化済み | QEDCalc/SymPy |
| IR asymptotic の regulator 解釈 | 人が理解 | 人 |
| total / corner cancellation residual | 自動 | QEDCalc |

###### 11. 最短再計算手順

1. raw left/right `.tex` を確認。
2. `self_energy_insertion_2loop_trial.py` で subdiagram detection と downstream outputs を生成。
3. Phase 31 で raw-to-final audit。
4. Phase 80 で release closure と corner IR cancellation を確認。
5. v0.90 regression で7図全体を確認。

###### 12. この資料で省略できた手計算

旧資料で長かった gamma contraction、counterterm 後 numerator の展開、log rationalization、4変数 integrand の展開、逐次積分の単純代数、IR/finite constant の数値認識は QEDCalc で再生成できる。残すべきなのは on-shell renormalization の意味と、IR limit の取り方である。

###### 13. 参照元と再実行ファイル

- 元計算資料：`self-energy_insertion_2図/self_energy_2図_Feynman図から最終結果_統合版_全体見直し修正版.md`
- 詳細別冊：`self_energy_2図_計算詳細別冊_全体見直し修正版.md`
- raw inputs：`input/self_energy_insertion_right_2loop_bare.tex`、`input/self_energy_insertion_left_2loop_bare.tex`
- subloop numerator：`input/self_energy_subloop_numerator.tex`
- main sample：`examples/self_energy_insertion_2loop_trial.py`
- analytic downstream：Phase 28
- raw bare bridge：Phase 29
- renormalized outer bridge：Phase 30
- raw-to-final：Phase 31
- release closure / IR sign：Phase 80

代表実行は `run_self_energy_2loop_demo.bat`、`run_phase31_self_energy_raw_to_final.bat`。全体 regression は `run_v090_validation.bat`。


---

###### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

#### 3. Recorded runtime artifacts

| Artifact | Type | Lines | Bytes |
| --- | --- | ---: | ---: |
| `output/self_energy_insertion_2loop_trial.md` | `md` | 202 | 8862 |
| `output/phase80_self_energy_end_to_end_checkpoint.md` | `md` | 31 | 469 |

#### 4. Recorded Markdown stages

##### 4.1 `output/self_energy_insertion_2loop_trial.md`

##### QEDCalc two-loop trial: self-energy insertion

Generated: 2026-08-22T11:10:31

###### Version

QEDCalc v0.23.0

###### Loaded conventions

- **metric_signature:** `+---`
- **gauge:** `feynman`
- **renormalization_scheme:** `on_shell`
- **dimreg_dimension:** `4 - 2*epsilon`
- **dimreg_subtraction:** `MSbar`
- **msbar_factor:** `true`
- **subdiagram_include_coupling:** `true`
- **subdiagram_include_loop_measure:** `true`
- **subdiagram_include_i:** `true`
- **coupling_symbol:** `e`
- **loop_measure_denominator_latex:** `(2\pi)^4`
- **loop_i_factor_latex:** `i`

###### Outer prefactor generated from conventions.txt

$$
\frac{e^{2}}{(2\pi)^4 i}
$$

###### Scope

v0.22 parses each bare two-loop self-energy-insertion RHS as one LoopIntegralExpression, discovers the open one-loop self-energy block from the repeated electron propagator pattern, identifies whether the insertion is left or right of the external photon vertex, and contracts it to S Sigma S. After the existing on-shell UV cancellation check passes, the same topology is rendered with Sigma_R. The internal-photon reduction currently selects the Feynman-gauge metric part; automatic finite on-shell counterterm reconstruction directly from the raw general-gauge expression remains a later step.

###### Raw right-insertion two-loop RHS

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2}\,\int d^{4}k\,d^{4}l\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k + \rlap{/}l - \left(i\,\varepsilon\right)}\,\gamma^{\beta}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right) \\
\left(-\left(g_{\alpha\beta} + \left(1 - \left(\alpha\right)\right)\,\frac{l_{\alpha}\,l_{\beta}}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

###### Right subdiagram detection

PASS: side=right, subloop=l, external momentum=p - \left(k\right)

###### Right self-energy numerator extracted from raw RHS

$$
4\left(m\right) - 2\left(\rlap{/}\left(p - \left(k\right)\right)\right) + 2\left(\rlap{/}l\right)
$$

###### Right compact bare outer diagram

$$
\begin{aligned}
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\Sigma^{(1)}\left(p - \left(k\right)\right) \\
\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

###### Raw left-insertion two-loop RHS

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2}\,\int d^{4}k\,d^{4}l\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k + \rlap{/}l - \left(i\,\varepsilon\right)} \\
\gamma^{\beta}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right) \\
\left(-\left(g_{\alpha\beta} + \left(1 - \left(\alpha\right)\right)\,\frac{l_{\alpha}\,l_{\beta}}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

###### Left subdiagram detection

PASS: side=left, subloop=l, external momentum=p' - \left(k\right)

###### Left self-energy numerator extracted from raw RHS

$$
4\left(m\right) - 2\left(\rlap{/}\left(p' - \left(k\right)\right)\right) + 2\left(\rlap{/}l\right)
$$

###### Left compact bare outer diagram

$$
\begin{aligned}
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\Sigma^{(1)}\left(p' - \left(k\right)\right)\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu} \\
\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

###### Self-energy subloop numerator input

$$
\gamma^{\alpha}\,\left(m + \rlap{/}r - \left(\rlap{/}l\right)\right)\,\gamma_{\alpha}
$$

###### After expansion and gamma contraction

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(\rlap{/}l\right)
$$

###### After l = t + a r

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(\rlap{/}t\right) + 2\left(a\,\rlap{/}r\right)
$$

###### After removing odd t terms

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(a\,\rlap{/}r\right)
$$

###### Self-energy denominator

$$
a m^{2} + a r_{2} \left(a - 1\right) + \lambda^{2} \left(1 - a\right)
$$

###### On-shell denominator

$$
a^{2} m^{2} + \lambda^{2} \left(1 - a\right)
$$

###### UV numerator after on-shell counterterms

$$
0
$$

###### UV cancellation check

PASS

###### Right compact renormalized outer diagram

$$
\begin{aligned}
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\Sigma_R^{(1)}\left(p - \left(k\right)\right) \\
\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

###### Left compact renormalized outer diagram

$$
\begin{aligned}
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\Sigma_R^{(1)}\left(p' - \left(k\right)\right)\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu} \\
\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

###### Rationalized logarithm prefactor

$$
- a \left(a - 1\right) \left(m^{2} - r_{2}\right)
$$

###### Rationalized logarithm denominator

$$
a^{2} m^{2} - a z \left(a - 1\right) \left(m^{2} - r_{2}\right) + \lambda^{2} \left(1 - a\right)
$$

###### Finite four-parameter integrand G_A

$$
\frac{\begin{gathered}
\left(a - 1\right) \left(b - q\right) \left(q - 1\right) \\
\left(4 a^{2} b q + 2 a^{2} b - 3 a^{2} q^{3} z - 3 a^{2} q^{2} z - 4 a b q + 4 a b + 6 a q^{3} z + 2 a q^{2} z - 3 q^{3} z + q^{2} z\right)
\end{gathered}}{\left(a b - q^{2} z \left(a - 1\right)\right)^{2}}
$$

###### Analytic b-integrated kernel

$$
\frac{\begin{gathered}
q \left(a - 1\right) \left(q - 1\right) \\
\left(a \left(5 a q + a - 5 q + 7\right) - \left(2 a \left(2 a q + a - 2 q + 2\right) - q z \left(a - 1\right) \left(5 a q + a - 5 q + 7\right)\right) \log{\left(\frac{- a + q z \left(a - 1\right)}{q z \left(a - 1\right)} \right)}\right)
\end{gathered}}{a^{2}}
$$

###### Final one-variable finite kernel

$$
\frac{\begin{gathered}
\frac{a^{2} \left(a - 1\right)^{2}}{4} - \frac{a^{2} \left(\left(1 - 3 a\right) \left(a - 1\right) + 1\right) \log{\left(a \right)}}{6} + \frac{a \left(a - 1\right)}{6} {}+ \\
\frac{\left(a - 1\right) \left(a^{2} \left(1 - 3 a\right) + a + 1\right) \log{\left(1 - a \right)}}{6}
\end{gathered}}{a^{2} \left(a - 1\right)}
$$

###### Finite coefficient numerical value

A_A = -0.5899780222827421454908045555486750630724843581250211812

###### Finite coefficient analytic recognition

$$
- \frac{\pi^{2}}{18} - \frac{1}{24}
$$

###### Finite coefficient reference

$$
- \frac{\pi^{2}}{18} - \frac{1}{24}
$$

###### Finite-part recognition check

PASS

###### IR part through O(rho^0)

$$
\log{\left(\rho \right)} + \frac{1}{2}
$$

###### Total self-energy-insertion coefficient

$$
\log{\left(\rho \right)} - \frac{\pi^{2}}{18} + \frac{11}{24}
$$

###### Equivalent conventional form

$$
A_{\mathrm S}=-\frac12\ln\rho^{-2}+\frac{11}{24}-\frac{\pi^2}{18}
$$

---

##### 4.2 `output/phase80_self_energy_end_to_end_checkpoint.md`

##### Phase 80: self-energy insertion end-to-end checkpoint

Raw sample residuals: `(0, 0, 0)`

Raw UV residual: `0`

Renormalized G_A residual: `0`

Finite part:

$$
- \frac{\pi^{2}}{18} - \frac{1}{24}
$$

IR part:

$$
\log{\left(\rho \right)} + \frac{1}{2}
$$

Total asymptotic:

$$
\log{\left(\rho \right)} - \frac{\pi^{2}}{18} + \frac{11}{24}
$$

Self-energy coefficient of $\log(1/\rho)$: `-1`

Corner coefficient of $\log(1/\rho)$: `1`

IR cancellation residual: `0`

---

#### 5. Large algebra/reduction files

No graph-specific CSV/TXT artifact is currently stored.

#### 6. Release-layer status

Phase 80 artifact(s): `output/phase80_self_energy_end_to_end_checkpoint.md`.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.

---

### 2.5 Vacuum polarization

Source: `output/2loop_vacuum_polarization_full.md`

### QEDCalc two-loop full process report: Vacuum polarization

Diagram multiplicity: **1**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

#### 1. Raw input expressions

##### `input/vacuum_polarization_2loop_bare.tex`

$$
\begin{aligned}
-\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \\
\left( -\left( g_{\rho\alpha} +(1-\alpha) \frac{k_\rho k_\alpha}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\operatorname{tr}\left[ \frac{1}{m-\rlap{/}l-\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}l-i\varepsilon} \gamma^\beta \right] \\
\left( -\left( g_{\beta\sigma} +(1-\alpha) \frac{k_\beta k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right)
\end{aligned}
$$

##### `input/vacuum_polarization_subloop.tex`

$$
(m+\rlap{/}l+\rlap{/}k)\gamma^\alpha(m+\rlap{/}l)\gamma^\beta
$$

#### 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/05_vacuum_polarization_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

##### QEDCalc サンプルプログラム説明書兼計算過程説明書：vacuum polarization 1図

###### 0. この資料の目的

内部 photon propagator に1ループ electron vacuum-polarization bubble を挿入した2ループ頂点図について、complete raw diagram から closed Dirac trace を見つけ、真空偏極 tensor、on-shell subtraction、outer magnetic kernel、2変数積分、最終解析値へ進む流れを説明する。この図は「subdiagram を抽出して低ループの既知構造へまとめる」という QEDCalc の使い方が最も明瞭な例である。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **vacuum polarization 1図** である。

本資料では各段階を次の3種類に区別する。

- **【人が決める】**：diagram の同定、Feynman gauge の採用、on-shell 条件、どの form factor を求めるか、どの変数変換を行うかなど、物理的意味を伴う選択。
- **【QEDCalc】**：LaTeX parse、Dirac 代数、loop shift、odd 項除去、tensor reduction、IBP、式の簡約、解析積分の機械的部分、residual の exact check など。
- **【接続】**：人が導出した式を QEDCalc の入力形式へ移す、または QEDCalc の出力を次の物理的段階へ解釈する部分。

重要なのは、QEDCalc は Feynman 図の意味を勝手に推測して全計算をブラックボックス処理するプログラムではないことである。**処理順序は人が決め、長大で機械的な代数を QEDCalc/SymPy に渡す**。QEDCalc の設計思想もこの分離にある。

###### 0.1 この資料の読み方

各計算段階では原則として次の順序で記載する。

1. なぜ次の処理が必要か。
2. 人が導出・選択しなければならない内容。
3. QEDCalc に渡す LaTeX または数式入力。
4. 実際のサンプルプログラムのファイル名と行番号。
5. QEDCalc の主要出力。
6. その出力を次の段階でどう使うか。

したがって、コードブロックだけを飛び飛びに読むのではなく、**「入力式がなぜその形になるか」→「コード」→「出力の物理的意味」**の順に読む。

###### 0.2 数式と規約

- 外部電子は on-shell とする。
- 電子質量を $m$ とする。
- 外部 photon momentum は $q=p'-p$ とする。
- anomalous magnetic moment は Pauli form factor $F_2(0)$ から得る。
- 必要な箇所では $D$ 次元を保持し、最後に $D\to4$ を取る。
- IR 正則化が必要な図では photon mass $\lambda$ と $\rho=\lambda/m$ を用いる。


###### 0.3 本資料での「人」と「QEDCalc」の受け渡しの書き方

この資料では、計算の各段階を単に「人が行う」「QEDCalc が行う」と分類するだけではなく、必ず次の受け渡しを明示する。

1. **前段階から入ってくる式・データ**：この段階を始める時点で何が既知なのか。
2. **人が用意する入力**：Feynman 図の読み取り、運動学、renormalization 条件、変数変換など、物理的・解析的判断を伴う部分。
3. **QEDCalc に実際に渡る入力**：LaTeX ファイル、SymPy 式、index table、parameter family など、プログラムが直接受け取るもの。
4. **サンプルコード**：QEDCalc v0.90.0 のどのファイルの何行が処理を行うか。
5. **QEDCalc の出力**：数式として何が得られ、どの residual / term count / table が検算されるか。
6. **次段階へ渡すもの**：得られた出力のうち、次の物理計算で実際に使用するもの。

したがって、関数が引数なしで呼ばれている場合も「入力なし」という意味ではない。関数内部で `input/*.tex` を読む場合、あるいは前段階で確定した topology・kinematics が関数内部に実装されている場合は、それを明示する。

また、長大な数十～数百項の多項式を QEDCalc が生成する場合、本資料ではその多項式を人が再び手計算することを目的としない。その場合でも、**何という多項式を生成したか、その数学的定義、項数、入力変数、次段階での使われ方**は必ず記載する。完全展開式は QEDCalc の生成物として再出力できる形を保つ。


###### 0.4 全工程の入出力一覧

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

###### 1. 元の入力となる Feynman 図

####### 1.1 【人が決める】complete raw RHS

$$
\begin{aligned}
\mathcal I &= -\frac{e^4}{(2\pi)^8 i^2} \int d^4k \\
&\quad d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \\
&\quad \left( -\left( g_{\rho\alpha} +(1-\alpha) \frac{k_\rho k_\alpha}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
&\quad \operatorname{tr}\left[ \frac{1}{m-\rlap{/}l-\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}l-i\varepsilon} \gamma^\beta \right] \\
&\quad \left( -\left( g_{\beta\sigma} +(1-\alpha) \frac{k_\beta k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right)
\end{aligned}
$$

閉じた electron loop は $l$ 積分を含む `tr[...]` 部分である。図からこの closed loop が vacuum polarization subdiagram だと認識する物理的意味は人が理解する。

###### 2. closed electron loop を抽出する

####### 2.1 【QEDCalc】complete raw diagram の parse と trace detection

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

###### 3. trace numerator の導出

####### 3.1 【接続】propagator numerator

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

####### 3.2 【QEDCalc】Dirac trace、loop shift、odd-term removal、rank-2 reduction

######## 入力

入力は前節で導出した $N^{\alpha\beta}(l,k)$ と2本の electron denominator である。

######## 出力

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

###### 4. 真空偏極 tensor の transverse form

####### 4.1 【人が理解する】Ward identity と tensor 構造

current conservation により renormalized vacuum polarization tensor は

$$
\Pi^{\alpha\beta}(k) =
\left(k^2g^{\alpha\beta}-k^\alpha k^\beta\right)\Pi(k^2)
$$

の transverse form でなければならない。これは単なる代数上の便利な分解ではなく gauge invariance の結果である。

####### 4.2 【QEDCalc】transversality residual

######## 入力

入力は前節の reduced tensor integral である。

######## 出力

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

###### 5. on-shell subtraction

####### 5.1 【人が決める】電荷 renormalization condition

physical charge を $k^2=0$ で定義する on-shell scheme では

$$
\Pi_R(k^2)=\Pi(k^2)-\Pi(0),\qquad \Pi_R(0)=0
$$

とする。この subtraction scheme の選択は物理的入力である。

####### 5.2 【QEDCalc】finite $D\to4$ kernel

######## 入力

入力は bare scalar vacuum-polarization function $\Pi(k^2)$ と、人が5.1で指定した on-shell condition $\Pi_R(0)=0$ である。

######## 出力

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

###### 6. outer magnetic vertex へ挿入する

####### 6.1 【人が理解する】tensor から scalar propagator correction へ

transverse $\Pi_R$ を photon propagator の間に挟むと、外側 electron vertex では scalar correction として扱える。さらに1ループ magnetic projector を適用すると、2ループ VP contribution は2変数 kernel に還元できる。

####### 6.2 【QEDCalc】2変数 kernel

######## 入力

入力は renormalized scalar $\Pi_R(k^2)$ と、1-loop magnetic vertex の Feynman parameter $x$ representation である。

######## 出力

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

###### 7. $z$ 積分から1変数 kernel へ

####### 7.1 【QEDCalc】analytic $z$ integration

######## 入力

入力は前節の $x,z$ double integral である。

######## 出力

QEDCalc は $z$ 積分を解析的に実行し、$x$ だけの kernel $K_{\rm VP}(x)$ を返す。ここでは2変数積分を直接数値評価して終わらせず、次節で primitive と endpoint を独立に検算できる1変数形にすることが目的である。

`vp_z_integrated_kernel(x)` が $z$ 積分済み $H(x)$ を返す。Phase 27 では generated z kernel も出力される。元資料の $z$ 積分の部分分数・対数整理は、この関数の検証後は省略できる。

###### 8. $x$ 積分と endpoint

####### 8.1 【人が理解する】endpoint を個別に評価する理由

原始関数 $F(x)$ を作って $F(1)-F(0)$ を取るとき、各 endpoint には log を含む見かけの特異表現がある。したがって式をそのまま代入するのでなく limit を取る必要がある。

####### 8.2 【QEDCalc】primitive derivative と endpoints

######## 入力

入力は1変数 kernel $K_{\rm VP}(x)$ と、その解析 primitive candidate である。

######## 出力

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

###### 9. Phase 79 release checkpoint

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
    "Final coefficient:", "", "$$
", str(c['final']), "
$$", "",
    "Closed form:", "", "$$
", str(c['closed_form']), "
$$", "",
    f"Final residual: `{c['final_closed_form_residual']}`", "",
```
通常の regression ではこれだけを走らせれば、VP route の主要接続が壊れていないことを短時間で確認できる。

###### 10. 現在の自動化境界

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

###### 11. 最短再計算手順

1. `input/vacuum_polarization_2loop_bare.tex` を確認。
2. `vacuum_polarization_2loop_trial.py` で raw trace bridge と downstream kernels を生成。
3. Phase 27 で raw-to-final audit。
4. Phase 79 で release checkpoint。
5. v0.90 regression で7図合計を確認。

###### 12. この資料で省略できた手計算

closed trace の数十項展開、$l=r-zk$ 後の odd-term 判定、rank-2 tensor reduction、transverse tensor の係数比較、$z$ 積分の長い整理、primitive の微分照合は QEDCalc に移せる。本文に残す必要があるのは、closed loop が vacuum polarization である理由、transversality の意味、on-shell subtraction の意味、outer graph への接続である。

###### 13. 参照元と再実行ファイル

- 元計算資料：`vacuum_polarization_F2_4/vacuum_polarization_F2_導出_全体見直し修正版.md`
- raw input：`input/vacuum_polarization_2loop_bare.tex`
- closed-loop numerator：`input/vacuum_polarization_subloop.tex`
- main sample：`examples/vacuum_polarization_2loop_trial.py`
- raw-to-final：Phase 27
- release closure：Phase 79

代表実行は `run_vp_2loop_demo.bat`、`run_phase27_vacuum_polarization_raw_to_final.bat`。全体 regression は `run_v090_validation.bat`。


---

###### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

#### 3. Recorded runtime artifacts

| Artifact | Type | Lines | Bytes |
| --- | --- | ---: | ---: |
| `output/vacuum_polarization_2loop_trial.md` | `md` | 109 | 5428 |
| `output/phase79_vacuum_polarization_end_to_end_checkpoint.md` | `md` | 27 | 365 |

#### 4. Recorded Markdown stages

##### 4.1 `output/vacuum_polarization_2loop_trial.md`

##### QEDCalc two-loop trial: vacuum polarization

Generated: 2026-08-22T11:10:33

###### Scope

v0.21 parses the bare two-loop RHS as one LoopIntegralExpression. The overall normalization is preserved as LaTeX, the k/l loop measures are structural objects, and the closed electron loop is discovered from an explicit DiracTrace node. The trace propagators are scalarized automatically before the trace numerator is evaluated. The final renormalized scalar VP kernel is still supplied by the dedicated renormalization layer rather than reconstructed from the complete outer diagram in one command.

###### Bare two-loop RHS parsed from LaTeX

$$
\begin{aligned}
-\frac{e^4}{(2\pi)^8 i^2}\,\int d^{4}k\,d^{4}l\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma^{\sigma}\,\left(-\left(g_{\rho\alpha} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\alpha}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right) \\
\operatorname{tr}\left[\frac{1}{m - \left(\rlap{/}l\right) - \left(\rlap{/}k\right) - \left(i\,\varepsilon\right)}\,\gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}l\right) - \left(i\,\varepsilon\right)}\,\gamma^{\beta}\right] \\
\left(-\left(g_{\beta\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\beta}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

###### Detected Dirac traces

1

###### Scalarized closed-loop fraction

$$
\frac{\left(m + \rlap{/}l + \rlap{/}k\right)\,\gamma^{\alpha}\,\left(m + \rlap{/}l\right)\,\gamma^{\beta}}{\left(m^{2} - \left(\left(-\left(l\right) - \left(k\right)\right)^{2}\right) - \left(i\,\varepsilon\right)\right)\,\left(m^{2} - \left(\left(-\left(l\right)\right)^{2}\right) - \left(i\,\varepsilon\right)\right)}
$$

###### Closed-loop trace numerator

$$
\begin{aligned}
4\left(m\,m\,g_{\alpha\beta}\right) + 4\left(l^{\alpha}\,l^{\beta} - \left(l\cdot l\,g_{\alpha\beta}\right) + l^{\beta}\,l^{\alpha}\right) {}+ \\
4\left(k^{\alpha}\,l^{\beta} - \left(k\cdot l\,g_{\alpha\beta}\right) + k^{\beta}\,l^{\alpha}\right)
\end{aligned}
$$

###### Closed-loop scalar denominator

$$
\left(m^{2} - \left(\left(-\left(l\right) - \left(k\right)\right)^{2}\right) - \left(i\,\varepsilon\right)\right)\,\left(m^{2} - \left(\left(-\left(l\right)\right)^{2}\right) - \left(i\,\varepsilon\right)\right)
$$

###### After l = r - z k

$$
\begin{aligned}
4\left(m\,m\,g_{\alpha\beta}\right) + 4\left(r^{\alpha}\,r^{\beta}\right) - 4\left(r^{\alpha}\,z\,k^{\beta}\right) {}- \\
4\left(z\,k^{\alpha}\,r^{\beta}\right) + 4\left(z\,k^{\alpha}\,z\,k^{\beta}\right) {}- \\
4\left(r\cdot r\,g_{\alpha\beta}\right) + 4\left(z\,r\cdot k\,g_{\alpha\beta}\right) + 4\left(z\,k\cdot r\,g_{\alpha\beta}\right) - 4\left(z\,z\,k\cdot k\,g_{\alpha\beta}\right) {}+ \\
4\left(r^{\beta}\,r^{\alpha}\right) - 4\left(r^{\beta}\,z\,k^{\alpha}\right) - 4\left(z\,k^{\beta}\,r^{\alpha}\right) + 4\left(z\,k^{\beta}\,z\,k^{\alpha}\right) + 4\left(k^{\alpha}\,r^{\beta}\right) {}- \\
4\left(k^{\alpha}\,z\,k^{\beta}\right) - 4\left(k\cdot r\,g_{\alpha\beta}\right) + 4\left(z\,k\cdot k\,g_{\alpha\beta}\right) + 4\left(k^{\beta}\,r^{\alpha}\right) - 4\left(k^{\beta}\,z\,k^{\alpha}\right)
\end{aligned}
$$

###### After removing odd powers of r

$$
\begin{aligned}
4\left(m\,m\,g_{\alpha\beta}\right) + 4\left(r^{\alpha}\,r^{\beta}\right) + 4\left(z\,k^{\alpha}\,z\,k^{\beta}\right) - 4\left(r\cdot r\,g_{\alpha\beta}\right) {}- \\
4\left(z\,z\,k\cdot k\,g_{\alpha\beta}\right) + 4\left(r^{\beta}\,r^{\alpha}\right) + 4\left(z\,k^{\beta}\,z\,k^{\alpha}\right) - 4\left(k^{\alpha}\,z\,k^{\beta}\right) {}+ \\
4\left(z\,k\cdot k\,g_{\alpha\beta}\right) - 4\left(k^{\beta}\,z\,k^{\alpha}\right)
\end{aligned}
$$

###### After rank-2 symmetric tensor reduction

$$
\begin{aligned}
4\left(m\,m\,g_{\alpha\beta}\right) + 4\left(\frac{1}{4}\left(g_{\alpha\beta}\,r\cdot r\right)\right) + 4\left(z\,k^{\alpha}\,z\,k^{\beta}\right) - 4\left(r\cdot r\,g_{\alpha\beta}\right) {}- \\
4\left(z\,z\,k\cdot k\,g_{\alpha\beta}\right) + 4\left(\frac{1}{4}\left(g_{\beta\alpha}\,r\cdot r\right)\right) + 4\left(z\,k^{\beta}\,z\,k^{\alpha}\right) - 4\left(k^{\alpha}\,z\,k^{\beta}\right) {}+ \\
4\left(z\,k\cdot k\,g_{\alpha\beta}\right) - 4\left(k^{\beta}\,z\,k^{\alpha}\right)
\end{aligned}
$$

###### Reference transverse tensor checkpoint

$$
\Pi^{\alpha\beta}(k)=\left(k^2g^{\alpha\beta}-k^\alpha k^\beta\right)\Pi(k^2)
$$

###### On-shell subtraction condition

$$
\Pi_R(k^2)=\Pi(k^2)-\Pi(0),\qquad \Pi_R(0)=0
$$

###### Renormalized scalar vacuum-polarization integrand

$$
- 2 z \left(z - 1\right) \log{\left(\frac{m^{2}}{k_{2} z \left(z - 1\right) + m^{2}} \right)}
$$

###### Two-parameter g-2 coefficient kernel

$$
2 z \left(x - 1\right) \left(z - 1\right) \log{\left(\frac{x^{2} z \left(z - 1\right) + x - 1}{x - 1} \right)}
$$

###### z-integrated kernel H(x)

$$
\frac{3 x^{3} \log{\left(1 - x \right)} - 5 x^{3} - 12 x^{2} - 18 x \log{\left(1 - x \right)} + 12 x + 12 \log{\left(1 - x \right)}}{9 x^{3}}
$$

###### Numerical coefficient

A_VP = 0.01568742185910268261072522226350517711766

###### Analytic recognition from the numerical value

$$
\frac{119}{36} - \frac{\pi^{2}}{3}
$$

###### Reference analytic coefficient

$$
\frac{119}{36} - \frac{\pi^{2}}{3}
$$

###### Recognition check

PASS

###### Two-loop anomalous-moment contribution

$$
a_{\mathrm{VP}}=\left(\frac{\alpha}{\pi}\right)^2\left(\frac{119}{36}-\frac{\pi^2}{3}\right)
$$

---

##### 4.2 `output/phase79_vacuum_polarization_end_to_end_checkpoint.md`

##### Phase 79: vacuum-polarization end-to-end closure checkpoint

Transversality residual: `0`

On-shell subtraction residual: `0`

Finite D->4 kernel residual: `0`

Outer magnetic insertion residual: `0`

z-kernel residual: `0`

Primitive derivative residual: `0`

Final coefficient:

$$
119/36 - pi**2/3
$$

Closed form:

$$
119/36 - pi**2/3
$$

Final residual: `0`

---

#### 5. Large algebra/reduction files

No graph-specific CSV/TXT artifact is currently stored.

#### 6. Release-layer status

Phase 79 artifact(s): `output/phase79_vacuum_polarization_end_to_end_checkpoint.md`.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.

---

## 3. Exact seven-diagram assembly

### Phase 82: seven-diagram end-to-end checkpoint

QEDCalc v0.89.0

#### Diagram classes

- crossed ladder: 1 diagram
- ordinary ladder: 1 diagram
- corner: 2 diagrams
- self-energy insertion: 2 diagrams
- vacuum polarization: 1 diagram
- total: 7 diagrams

#### Exact transcendental-basis sum

Basis: `1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)`

- X: `(1/6, 13/36, 5/4, -5/6, 0)`
- L: `(11/48, 1/18, 0, 0, 0)`
- C: `(-67/24, 1/18, -1/2, 1/3, 1)`
- S: `(11/24, -1/18, 0, 0, -1)`
- VP: `(119/36, -1/3, 0, 0, 0)`
- TOTAL: `(197/144, 1/12, 3/4, -1/2, 0)`

IR log residual: `0`

Final coefficient:

$$
A_1^{(4)} = \frac{197}{144} + \frac{\pi^2}{12} + \frac34\zeta(3) - \frac{\pi^2}{2}\ln2
$$

Exact basis residual: `0`

---

## 4. Complete two-loop regression

### Phase 83: complete two-loop regression checkpoint

QEDCalc v0.90.0

#### Completion matrix

| Phase | Diagram class | Multiplicity | Status | Release invariant |
| --- | --- | ---: | --- | --- |
| 77 | corner pair | 2 | PASS | sector + soft/hard + IR closure |
| 78 | crossed ladder | 1 | PASS | projector + endpoint + analytic closure |
| 79 | vacuum polarization | 1 | PASS | transversality + OS subtraction + final closure |
| 80 | self-energy insertion pair | 2 | PASS | raw-to-final + IR closure |
| 81 | ordinary ladder | 1 | PASS | 72 -> 40 -> 12 + OS subtraction |
| 82 | seven-diagram total | 7 | PASS | exact transcendental-basis sum |

#### Exact seven-diagram basis sum

Basis: `1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)`

- crossed_ladder: `(1/6, 13/36, 5/4, -5/6, 0)`
- ordinary_ladder: `(11/48, 1/18, 0, 0, 0)`
- corner_pair: `(-67/24, 1/18, -1/2, 1/3, 1)`
- self_energy_pair: `(11/24, -1/18, 0, 0, -1)`
- vacuum_polarization: `(119/36, -1/3, 0, 0, 0)`
- total: `(197/144, 1/12, 3/4, -1/2, 0)`

IR log residual: `0`

Final coefficient:

$$
A_1^{(4)} = \frac{197}{144} + \frac{\pi^2}{12} + \frac34\zeta(3) - \frac{\pi^2}{2}\ln2
$$

Exact basis residual: `0`

#### Regression baseline

- ordinary-ladder projector rows: `72`
- ordinary-ladder canonical IBP targets: `40`
- ordinary-ladder terminal master bases: `12`
- diagram count: `7`
- scientific-package-free release audit: `PASS`

#### Known unresolved provenance item

The crossed-ladder Karplus--Kroll historical gap has magnitude `1/32`.  Its precise lost term in the 1950 algebra remains unresolved.  This is not an uncertainty in the modern crossed-ladder value and is not used as an input to the two-loop closure.

#### Completion status

`TWO-LOOP RELEASE REGRESSION PASS`
