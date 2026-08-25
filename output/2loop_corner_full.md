# QEDCalc two-loop full process report: Corner pair

Diagram multiplicity: **2**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

## 1. Raw input expressions

### `input/corner_4_2loop_bare_feynman_gauge.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\rho \frac{1}{m-\rlap{/}p'+\rlap{/}l-i\varepsilon} \\
\gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

### `input/corner_5_2loop_bare_feynman_gauge.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \\
\gamma_\rho \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

## 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/03_corner_2図_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

### QEDCalc サンプルプログラム説明書兼計算過程説明書：corner 2図

#### 0. この資料の目的

2ループ corner contribution（左右の inner-vertex insertion に対応する2図）について、raw 2図の同定、magnetic projector、1ループ renormalized inner vertex、UV subdivergence subtraction、soft/hard sector、有限解析値、self-energy insertion との IR 相殺までを QEDCalc の複数 Phase と対応させる。corner は5群の中で最も処理層が多いので、1本のサンプルへ無理に押し込まず、段階ごとのサンプルを一本道に並べる。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **corner 2図** である。

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

#### 1. 元の入力となる2つの Feynman 図

##### 1.1 【人が決める】2図の非可換順序

Feynman gauge の raw inputs は次である。

###### diagram 4

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\rho \frac{1}{m-\rlap{/}p'+\rlap{/}l-i\varepsilon} \\
\gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

###### diagram 5

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \\
\gamma_\rho \frac{1}{m-\rlap{/}p+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

2図は外部 photon vertex に対して inner vertex correction が左右に入る組である。電子線上の gamma/propagator 順序は人が図から確定する。

##### 1.2 【QEDCalc】raw pair の topology を監査する

###### この段階へ入る入力は何か

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

###### QEDCalc 内部で入力をセットする部分

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

###### 何を検査しているか

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
###### QEDCalc の実際の出力

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

###### この段階で得るもの／次へ渡すもの

この段階ではまだ $F_2(0)$ の値は計算していない。得たものは、

1. 入力した2式の非可換順序が正しく parse できたこと。
2. diagram 4 / 5 のどちらに inner vertex subgraph があるか。
3. $q=0$ でどの denominator が二重になるか。
4. 2図を「renormalized inner vertex + mirror」として扱える topology であること。

である。次節以降では、この topology 情報を使って **inner vertex を on-shell renormalize すること**と、**外側 vertex から $F_2(0)$ を抽出すること**を別々に進める。

#### 2. なぜ bare 2図のままでは計算を閉じないか

##### 2.1 【人が決める】renormalized inner vertex として組み直す

inner vertex subgraph は UV divergent なので、bare vertex をそのまま外側 loop へ入れて最後に一括 subtraction するのではなく、**1ループ on-shell-renormalized inner vertex** として整理してから outer insertion を評価する。

記号的には

$$
\Gamma_\alpha^{(1),\mathrm R} =
\Gamma_\alpha^{(1),\mathrm{bare}} +
\delta\Gamma_\alpha^{(1)}
$$

を外側の1ループ vertex skeleton に挿入する。この局所 subtraction の意味と on-shell scheme の採用は人が理解する必要がある。

#### 3. magnetic projector

##### 3.1 【人が決める】$F_2(0)$ の抽出

###### この段階で導出したい式

vertex correction の計算結果は、そのままでは $F_1$ と $F_2$ を同時に含む。一般の on-shell electromagnetic vertex は

$$
\Gamma_\mu(p',p) =
F_1(q^2)\gamma_\mu +
\frac{i\sigma_{\mu\nu}q^\nu}{2m}F_2(q^2)
$$

である。異常磁気能率に必要なのは $F_2(0)$ なので、ここで人が導出しておくべきものは、**計算した vertex matrix element から $F_1$ を消して $F_2$ だけを取り出す projector** である。

###### Breit frame を選ぶ

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

##### 3.2 【QEDCalc】corner 2図の $q$ 一次 projector polynomial を生成する

###### この段階へ入る式

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

###### QEDCalc が作る出力式

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
###### 実際に得られる出力

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

###### 次段階へ渡すもの

次の Feynman parameter / Gaussian reduction へ渡すのは、この $P_4(k,l)$、$P_5(k,l)$ と各 denominator power である。したがって、ここから先は元資料にあった数百項の gamma 行列展開を人が追い直す必要はない。

#### 4. Feynman parameter family と平方完成

##### 4.1 【人が決める】parameterization の構造

6本の physical propagator を Feynman parameter でまとめ、2つの loop momenta の二次形式を平方完成する。corner では split parameter を保持することで numerator の $q$ dependence と inner/outer subgraph ownership を追えるようにする。

##### 4.2 【QEDCalc】$q=0$ parametric family を生成

###### この段階へ入る入力

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

#### 5. UV subdivergence と local counterterm

##### 5.1 【人が決める】どの subgraph を subtraction するか

corner の UV divergence は inner vertex subgraph に局在する。したがって、UV scaling chart を選び、bare residue と local $B\gamma$ counterterm residue が一致することを確認する。

##### 5.2 【QEDCalc】bare residue と local residue を exact 比較

###### 入力

入力は Phase 33/34 までに得た parametric denominator family と projector numerator、および人が 5.1 で選んだ inner-vertex UV scaling chart である。局所 counterterm 側には、別紙Aで独立導出した on-shell vertex subtraction の $B\gamma_\rho$ 構造を使う。

bare 側と local 側で比較する量は同じ UV scaling の residue であり、概念的には

$$
R_{\rm bare}(x,y,z;\rho)
\quad\text{and}\quad
R_{B\gamma}(x,y,z;\rho)
$$

である。

###### 出力

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

#### 6. renormalized inner vertex の sector 分解

##### 6.1 【接続】1ループ renormalization の出力を outer loop へ渡す

元資料で導出した1ループ vertex renormalization では、inner vertex を $K$ sector、$z$ sector、$\kappa$ sector などへ分解する。この分解は発散 cancellation と有限部分の ownership を明確にするためである。

##### 6.2 【QEDCalc】sector identities を監査する

###### 入力

入力は前節で UV subtraction 済みとなった inner vertex を、元計算資料で導出した $K$ sector、$z$ sector、$\kappa$ sector に分けた式である。ここでは sector 分解そのものの物理的意味は人が決め、QEDCalc は各 sector の代数恒等式を検査する。

###### 出力

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

#### 7. soft IR sector

##### 7.1 【人が決める】photon mass regulator を残す

corner は IR divergent なので $\rho=\lambda/m$ を最後まで保持する。soft scaling を先に取り、$\ln(1/\rho)$ の係数を独立に取り出す。

##### 7.2 【QEDCalc】soft kernel と IR coefficient

###### 入力

入力は renormalized corner kernel の soft scaling limit である。人が 7.1 で $\rho=\lambda/m$ を残すと決めた後、QEDCalc には soft variables $U,R,S,v$ で書かれた leading kernel を渡す。

###### 出力

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

#### 8. momentum shift correction と hard/z sectors

##### 8.1 【人が理解する】shift で numerator も変わる

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

##### 8.2 【QEDCalc】解析 sector を合成する

###### 入力

入力は、(i) primary hard-sector kernel、(ii) 8.1 の momentum shift によって生じる numerator correction、(iii) $z$ sector の3組である。これらは互いに異なる由来を持つので、QEDCalc では別関数として評価してから最後に足す。

###### 出力

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

#### 9. soft/hard ownership

corner では一時期、数値 route が finite total ではなく hard remainder を返していることが判明した。現在は

$$
A_{\mathrm C,fin}=H_{\mathrm{fin}}+C_{\mathrm{soft}}
$$

という ownership を exact に監査し、soft finite constant を二重加算しないよう固定している。メイン trial の soft/hard diagnostic split residual が0であることがこの確認に相当する。

#### 10. self-energy insertion との IR 相殺

##### 10.1 【QEDCalc】log coefficient を pair で検査する

###### 入力

入力は corner 側で独立に得た

$$
C_{\rm IR}^{\rm C}=+1
$$

と、self-energy insertion 側の raw-to-final audit から得た

$$
C_{\rm IR}^{\rm S}=-1
$$

である。同じ regulator $\rho=\lambda/m$ と同じ $\ln(1/\rho)$ convention に直してから比較する。

###### 出力

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

#### 11. Phase 77 release checkpoint

Phase 77 は sector route と soft/hard route の2本が同じ closed form に到達すること、さらに IR cancellation をまとめて exact check する。通常の regression ではこの Phase を使う。

#### 12. 現在の自動化境界

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

#### 13. 最短再計算手順

1. Phase 32 で raw 2図 topology を確認。
2. Phase 34 で projector を確認。
3. Phase 33/35/36 で parametric family と UV subtraction を確認。
4. 必要に応じ Phase 42～76 の詳細 audits で ownership/sign/overlap を追う。
5. `corner_2loop_trial.py` で analytic sectors を確認。
6. Phase 77 または `run_v090_validation.bat` で completion regression を確認。

#### 14. この資料で省略できた手計算

6 denominator の展開、数百項の Dirac/Lorentz algebra、Gaussian tensor reduction、UV scaling residue の項別比較、soft overlap の大量の局所展開、hard/z sector の単純代数は QEDCalc の Phase 群へ移した。一方、**どの subgraph を renormalize するか、soft/hard をどう定義するか、IR regulator をいつ外すか**という物理判断は本文に残した。

#### 15. 参照元と再実行ファイル

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

#### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

## 3. Recorded runtime artifacts

| Artifact | Type | Lines | Bytes |
| --- | --- | ---: | ---: |
| `output/corner_2loop_trial.md` | `md` | 125 | 2715 |

## 4. Recorded Markdown stages

### 4.1 `output/corner_2loop_trial.md`

### QEDCalc corner (IIc) two-loop trial

Generated: 2026-08-22T10:21:01

#### Scope

This trial starts from the independently derived UV-finite parameter representation and its sector decomposition. The complete six-denominator magnetic-projector integrand is not yet regenerated automatically from the original two-loop LaTeX expression. The trial verifies the soft IR coefficient, the momentum-shift correction, the hard/z-sector analytic bookkeeping, and the self-energy IR cancellation.

#### Leading physical-measure soft kernel

$$
\frac{2 R S U v \left(4 R + S + 4 v\right)}{\left(R + v\right)^{2} \left(U^{2} + 1\right) \left(R + S + v\right)^{4}}
$$

#### S-integrated soft kernel

$$
\frac{2 R v}{\left(R + v\right)^{3}}
$$

#### Exact coefficient of log(1/rho)

$$
1
$$

#### Diagnostic soft finite constant

$$
- \log{\left(8 \right)} - \frac{7}{4} + \log{\left(2 \right)}^{2} + \frac{\pi^{2}}{6}
$$

#### Diagnostic hard remainder

$$
- \frac{\pi^{2}}{9} - \frac{25}{24} - \frac{\zeta\left(3\right)}{2} - \log{\left(2 \right)}^{2} + \log{\left(2^{3 + \frac{\pi^{2}}{3}} \right)}
$$

#### Soft+hard diagnostic split difference

$$
0
$$

#### Common momentum-shift action on p'-k

$$
p'-k\;\longrightarrow\;- u v + 1\,p'u v - u\,p''-k
$$

#### Primary K+kappa^2 hard-sector group

$$
- \frac{19}{3} - \frac{15 \zeta\left(3\right)}{8} + \frac{11 \pi^{2}}{36} + \frac{3 \pi^{2} \log{\left(2 \right)}}{4}
$$

#### Momentum-shift correction

$$
- \frac{\pi^{2}}{4} - \frac{\pi^{2} \log{\left(2 \right)}}{6} + \frac{3 \zeta\left(3\right)}{4} + \frac{8}{3}
$$

#### Complete K+kappa^2 hard sector

$$
- \frac{11}{3} - \frac{9 \zeta\left(3\right)}{8} + \frac{\pi^{2}}{18} + \frac{7 \pi^{2} \log{\left(2 \right)}}{12}
$$

#### z sector

$$
- \frac{\pi^{2} \log{\left(2 \right)}}{4} + \frac{5 \zeta\left(3\right)}{8} + \frac{7}{8}
$$

#### Corner finite part

$$
- \frac{67}{24} - \frac{\zeta\left(3\right)}{2} + \frac{\pi^{2}}{18} + \frac{\pi^{2} \log{\left(2 \right)}}{3}
$$

#### Independent closed-form checkpoint

$$
- \frac{67}{24} - \frac{\zeta\left(3\right)}{2} + \frac{\pi^{2}}{18} + \frac{\pi^{2} \log{\left(2 \right)}}{3}
$$

#### Difference

$$
0
$$

#### Corner asymptotic coefficient A_C(rho)

$$
\log{\left(\frac{2^{\frac{\pi^{2}}{3}}}{\rho} \right)} - \frac{67}{24} - \frac{\zeta\left(3\right)}{2} + \frac{\pi^{2}}{18}
$$

#### Corner IR-log coefficient

$$
1
$$

#### Self-energy insertion IR-log coefficient

$$
-1
$$

#### Combined IR-log coefficient

$$
0
$$

#### Combined finite part after IR cancellation

$$
- \frac{7}{3} - \frac{\zeta\left(3\right)}{2} + \frac{\pi^{2} \log{\left(2 \right)}}{3}
$$

#### Result

PASS: the independently derived corner-sector decomposition and the self-energy IR cancellation are reproduced exactly.

---

## 5. Large algebra/reduction files

No graph-specific CSV/TXT artifact is currently stored.

## 6. Release-layer status

No Phase 77 Markdown artifact is currently stored; rerun that scientific phase when a freshly regenerated checkpoint is required.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.
