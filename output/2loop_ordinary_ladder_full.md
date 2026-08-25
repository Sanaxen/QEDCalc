# QEDCalc two-loop full process report: Ordinary ladder

Diagram multiplicity: **1**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

## 1. Raw input expressions

### `input/ordinary_ladder_2loop_bare.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\mu \\
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma_\rho \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

## 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/02_ordinary_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

### QEDCalc サンプルプログラム説明書兼計算過程説明書：ordinary ladder 1図

#### 0. この資料の目的

2ループ ordinary ladder 1図について、D次元 Pauli projector、72項の projector 展開、40 canonical target、12 master basis、on-shell subtraction を経て renormalized $F_2(0)$ を得るまでを説明する。ordinary ladder は $(D-4)\times1/(D-4)$ の有限残差を持つため、特に「なぜ4次元へ早く置いてはいけないか」を明示する。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **ordinary ladder 1図** である。

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

#### 1. 元の入力となる Feynman 図

##### 1.1 【人が決める】Feynman 則と D 次元

ordinary ladder は2本の内部 photon が交差しない図である。Feynman gauge で、raw input は次である。

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^Dk\,d^Dl \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\mu \\
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma_\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma_\rho \frac{1}{-k^2-i\varepsilon} \frac{1}{-l^2-i\varepsilon}
\end{aligned}
$$

ここで積分 measure を最初から $d^4k\,d^4l$ とせず $d^Dk\,d^Dl$ とする。理由は UV pole と $D$ 依存 numerator の積が有限定数を生むためであり、途中で $D=4$ とするとその有限部を失う。

#### 2. raw LaTeX を denominator family へ落とす

##### 2.1 【QEDCalc】parse と electron propagator detection

###### この段階へ入る入力

入力は前節の ordinary ladder complete RHS であり、ファイル

`input/ordinary_ladder_2loop_bare.tex`

に LaTeX として保存されている。人が図から確定した非可換順序を、そのまま保持した式でなければならない。

###### QEDCalc へ実際に渡す入力

```python
raw_source = RAW.read_text(encoding='utf-8')
raw_diagram = parse_loop_integral_latex(raw_source)
raw_info = analyze_raw_ordinary_ladder(raw_diagram)
```

である。つまり `raw_info` は入力ではなく、raw LaTeX を解析した結果である。

###### QEDCalc が認識すべき denominator

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

###### QEDCalc の出力

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

#### 3. D次元 Pauli projector

##### 3.1 【人が決める】projector の ansatz

###### 何を導出するのか

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

##### 3.2 【QEDCalc】trace 方程式を解く

###### QEDCalc への入力

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

#### 4. $q\to0$ の有限 projector：$A_0$ と $C_1$

##### 4.1 【人が決める】なぜ $A_0$ と $C_1$ に分けるか

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

#### 5. Dirac/Lorentz 代数を scalar integrals へ

##### 5.1 【QEDCalc】raw q=0 numerator と scalar-product rules

###### 入力

入力は parse 済み ordinary-ladder electron chain と、4節で得た finite $q\to0$ projector の $A_0,C_1$ combination である。

###### 出力

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

#### 6. 72 projector terms → 40 targets → 12 master basis

##### 6.1 【QEDCalc】corrected spin-sum projector と reduction data

###### 入力

入力は前節の scalar-integral term table と、ordinary-ladder IBP family の index convention である。

###### 出力

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

##### 6.2 【人が理解する】72、40、12 の意味

- **72**：corrected finite-$q$ spin-sum projector を scalar integral monomial へ分解した非零項。
- **40**：対称性・zero sector・同値関係などを整理した canonical reduction targets。
- **12**：最終的に必要な terminal master basis。

これは「72個の Feynman 図」という意味ではない。

##### 6.3 【QEDCalc】bare finite coefficient の再構成

###### 入力

入力は12 master basis の係数と、それぞれの $D=4-2\epsilon$ Laurent 展開である。

###### 出力

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

#### 7. renormalization subtraction

##### 7.1 【人が決める】何を subtraction するか

ordinary ladder 単体の bare graph は UV pole を持つので、1ループ vertex renormalization の counterterm insertion を加える。on-shell scheme では必要な量は $F_2^{(1)}(D,0)$ と $Z_1^{(1)}$ である。

##### 7.2 【QEDCalc】1-loop ingredients と subtraction series

###### 入力

入力は bare ladder Laurent series と、人が7.1で指定した on-shell vertex counterterm $Z_1^{(1)}F_2^{(1)}$ である。

###### 出力

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

#### 8. Phase 81 end-to-end checkpoint

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

#### 9. 現在の自動化境界

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

#### 10. 最短再計算手順

1. `input/ordinary_ladder_2loop_bare.tex` を確認。
2. `ladder_2loop_trial.py` で raw family と projector/subtraction を確認。
3. Phase 14 または Phase 81 で 72→40→12→bare を再構成。
4. Phase 81 で renormalized coefficient を確認。
5. `run_v090_validation.bat` で7図統合値が壊れていないことを確認。

#### 11. この資料で省略できた手計算

29個・33個の scalar integral を人が逐一展開する作業、IBP 行列消去、12 master への係数集約、Laurent series の大量整理、pole cancellation の項別照合は、現在のサンプルと reduction data から再現できる。そのため本資料では「なぜその reduction が必要か」と「どのデータが入力か」を残し、数百行の機械代数は省略する。

#### 12. 参照元と再実行ファイル

- 元計算資料：`ladder_F2_4/ladder_Feynman図から最終結果_統合版_修正版.md`
- 完成導出：`ladder_F2_4/QED_2loop_ordinary_ladder_独立導出_完成版.md`
- 詳細別冊：`ladder_F2_4/ladder_計算詳細別冊_修正版.md`
- raw input：`input/ordinary_ladder_2loop_bare.tex`
- main sample：`examples/ladder_2loop_trial.py`
- finite master checkpoint：Phase 14
- release closure：Phase 81

代表実行は `run_ladder_2loop_demo.bat`、`run_phase14_ladder_finite_checkpoint_demo.bat`、`run_phase81_ordinary_ladder_end_to_end_checkpoint.bat`。全体 regression は `run_v090_validation.bat`。


---

#### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

## 3. Recorded runtime artifacts

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

## 4. Recorded Markdown stages

### 4.1 `output/ladder_2loop_trial.md`

### QEDCalc two-loop ordinary-ladder trial

This trial uses the supplied ordinary-ladder derivation as the checkpoint source. It does not yet regenerate all 75 coefficients from the raw D-dimensional Dirac trace.

#### 0. Raw bare two-loop LaTeX bridge

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

##### Scalar-product basis derived from the denominator definitions


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

##### Direct q=0 Dirac numerator generated from the raw graph


$$
\begin{aligned}
N_{\mu}^{(0)} &= \gamma^{\rho}\,\left(m + \rlap{/}p - \left(\rlap{/}k\right)\right)\,\gamma^{\alpha}\,\left(m + \rlap{/}p - \left(\rlap{/}k\right) - \left(\rlap{/}l\right)\right)\,\gamma_{\mu} \\
&\quad \left(m + \rlap{/}p - \left(\rlap{/}k\right) - \left(\rlap{/}l\right)\right)\,\gamma_{\alpha}\,\left(m + \rlap{/}p - \left(\rlap{/}k\right)\right)\,\gamma_{\rho}
\end{aligned}
$$

#### 1. D-dimensional Pauli projector coefficients


$$
a=\frac{2}{z \left(D - 2\right) \left(z - 4\right)}
$$


$$
b=\frac{D z - 2 z + 4}{z \left(D - 2\right) \left(z - 4\right)^{2}}
$$

#### 2. Scalar-product to denominator rules


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

#### 3. Reproducible 75-term integral-family table

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

#### 4. D-dimensional one-loop subtraction ingredients


$$
F_2^{(1l)}(D,0)=\frac{5 - D}{2 \left(D - 3\right)}
$$


$$
Z_1^{(1l)}=\frac{1 - D}{2 \left(D - 4\right) \left(D - 3\right)}
$$


$$
F_{2,\mathrm{sub}}^{(2)}(0)=- \frac{3}{4 \delta} + 2 - 3 \delta + O\left(\delta^{2}\right)
$$

#### 5. Bare checkpoint and UV subtraction


$$
F_{2,\mathrm L}^{\mathrm{bare}}=\frac{\pi^{2}}{18} + \frac{107}{48} - \frac{3}{4 \delta}+O(\delta)
$$


$$
F_{2,\mathrm L}^{\mathrm R}(0)=\frac{11}{48} + \frac{\pi^{2}}{18}
$$


$$
F_{2,\mathrm L}^{(4)}(0)=\left(\frac{\alpha}{\pi}\right)^2\left[\frac{11}{48} + \frac{\pi^{2}}{18}\right]
$$

#### 6. Automation boundary

QEDCalc now parses the raw symbolic-D two-loop ladder RHS, detects E1..E4 and K,L, constructs the seven-denominator family including auxiliary H, derives the scalar-product basis from the denominator equations, and then automates the stored coefficient-table validation and D-dimensional subtraction. The q=0 A0 branch is now regenerated separately from the raw D-dimensional projector trace into 29 scalar integrals (see run_ladder_a0_trace_demo.bat). The historical general-q^2 75-term audit table is now regenerated from the raw projector trace. v0.27.0 also provides a generic IBP generator and finite sparse Laporta eliminator. The remaining step is complete seed closure/sector handling and master-integral reduction for the seven-denominator family.

---

### 4.2 `output/ladder_A0_raw_trace_trial.md`

### Ordinary ladder raw A0 trace trial

This file is generated by QEDCalc from the bare ordinary-ladder LaTeX input.

#### Raw A0 projector trace

The program constructs

$$
A_0=\operatorname{Tr}\left[(\rlap{/}P+m)N_\mu^{(0)}(\rlap{/}P+m)\gamma^\mu\right]
$$

and evaluates the arbitrary-length $D$-dimensional Clifford trace using the optimized fully-contracted trace engine.

#### Denominator polynomial

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

#### Integral-family result

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

#### Automation boundary

The complete $A_0$ 29-integral table is now regenerated from the raw bare ladder expression. The remaining ordinary-ladder gap is the general-$q^2$ Pauli-projector branch that generates the 75-term audit table, followed by a general IBP/Laporta reducer.

---

### 4.3 `output/ladder_general_q_raw_trace_trial.md`

### Ordinary ladder general-q raw projector trial

This file is generated by QEDCalc from the bare ordinary-ladder LaTeX input.

#### Purpose

The ordinary-ladder archive contains a 75-term general-$q^2$ coefficient table. Later auditing of the derivation identified that this table was generated with the historical projector-first trace ordering. QEDCalc now reproduces that table from the raw bare expression and keeps it explicitly separate from the corrected spin-sum trace ordering.

#### Historical archived trace ordering

The archived table uses

$$
\operatorname{Tr}\left[(\rlap{/}p\prime+m)O_\mu(\rlap{/}p+m)\Gamma_{\mathrm L}^{\mu}\right]
$$

Generated scalar-integral monomials: **75**

Missing indices versus archived CSV: **0**

Extra indices versus archived CSV: **0**

Coefficient mismatches versus archived CSV: **0**

Therefore the raw regeneration matches the archived 75-term CSV exactly.

##### Representative regenerated coefficients

| Integral index | Regenerated coefficient | Archived coefficient |
|---|---|---|
| `(1, 1, 0, 1, 1, 1, 1)` | `$- 16 \left(z - 2\right)$` | `$- 16 \left(z - 2\right)$` |
| `(1, 0, -1, 1, 1, 1, 1)` | `$\frac{8 \left(D - 4\right)}{z - 4}$` | `$\frac{8 \left(D - 4\right)}{z - 4}$` |
| `(0, 0, -1, 1, 1, 1, 1)` | `$\frac{8 \left(D - 2\right) \left(D - 1\right)}{\left(z - 4\right)^{2}}$` | `$\frac{8 \left(D - 2\right) \left(D - 1\right)}{\left(z - 4\right)^{2}}$` |
| `(1, 1, 0, 0, 0, 0, 1)` | `$\frac{4 \left(D - 4\right)}{z \left(z - 4\right)}$` | `$\frac{4 \left(D - 4\right)}{z \left(z - 4\right)}$` |

Generated CSV: `output/ladder_general_q_75_coefficients_generated.csv`

#### Corrected spin-sum trace ordering

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

#### Automation boundary

The archived 75-term general-$q^2$ coefficient table is now regenerated completely from the raw bare ladder expression. The remaining major ordinary-ladder automation gap is a general IBP/Laporta reducer. For the physical $F_2(0)$ derivation QEDCalc continues to use the audited finite-limit $A_0$ and $C_1=B_1-2A_1$ route rather than treating the historical 75-term audit table as the final projector.

---

### 4.4 `output/phase10_ladder_basis_evaluation_trial.md`

### QEDCalc phase-10 ordinary-ladder basis-evaluation trial

The v0.41 corrected ordinary-ladder reduction terminates on 12 basis integrals. v0.42 starts the evaluation layer for those basis objects.

#### Classification

Generic-z factorized lower sectors: **3**.

Exact analytic z=0 basis values: **9 / 12**.

Remaining genuine z=0 masters: **3** (basis 8, 10, 11).

All formulas below are convention-free Euclidean scalar integrals. Overall Minkowski i factors, Wick-rotation signs, (2pi)^D loop-measure normalization, and renormalization-scale factors belong to the convention layer.

#### z=0 analytic values

##### Basis 0: `(0, 0, 0, 0, 0, 1, 1)`

Status: **exact**. Method: `factorized_tadpoles_T1xT1`.

$$
\pi^{D} m_{2}^{D - 2} \Gamma^{2}\left(1 - \frac{D}{2}\right)
$$

##### Basis 1: `(0, 0, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `factorized_tadpoles_T1xT1`.

$$
\pi^{D} m_{2}^{D - 2} \Gamma^{2}\left(1 - \frac{D}{2}\right)
$$

##### Basis 2: `(0, 0, 0, 0, 1, 1, 1)`

Status: **exact**. Method: `z0_degenerate_factorization_T2xT1`.

$$
\pi^{D} m_{2}^{D - 3} \Gamma\left(1 - \frac{D}{2}\right) \Gamma\left(2 - \frac{D}{2}\right)
$$

##### Basis 3: `(0, 0, 0, 0, 2, 0, 3)`

Status: **exact**. Method: `factorized_tadpoles_T2xT3`.

$$
\frac{\pi^{D} m_{2}^{D - 5} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - \frac{D}{2}\right)}{2}
$$

##### Basis 4: `(0, 0, 0, 1, 1, 1, 1)`

Status: **exact**. Method: `z0_degenerate_factorization_T2xT2`.

$$
\pi^{D} m_{2}^{D - 4} \Gamma^{2}\left(2 - \frac{D}{2}\right)
$$

##### Basis 5: `(0, 1, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `one_massless_two_massive_vacuum_111`.

$$
\frac{\pi^{D} m_{2}^{D - 3} \Gamma^{2}\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma\left(\frac{D}{2} - 1\right)}{\Gamma\left(\frac{D}{2}\right) \Gamma\left(4 - D\right)}
$$

##### Basis 6: `(0, 1, 0, 0, 1, 0, 2)`

Status: **exact**. Method: `one_massless_two_massive_vacuum_112`.

$$
\frac{\pi^{D} m_{2}^{D - 4} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - \frac{D}{2}\right) \Gamma\left(4 - D\right) \Gamma\left(\frac{D}{2} - 1\right)}{\Gamma\left(\frac{D}{2}\right) \Gamma\left(5 - D\right)}
$$

##### Basis 7: `(0, 1, 1, 0, 0, 0, 1)`

Status: **exact**. Method: `massless_bubble_then_on_shell_E4`.

$$
\frac{\pi^{D} m_{2}^{D - 3} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(3 - D\right) \Gamma^{2}\left(\frac{D}{2} - 1\right) \Gamma\left(2 D - 5\right)}{\Gamma\left(D - 2\right) \Gamma\left(\frac{3 D}{2} - 3\right)}
$$

##### Basis 8: `(0, 1, 1, 0, 1, 0, 1)`

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

##### Basis 9: `(0, 1, 1, 1, 0, 0, 1)`

Status: **exact**. Method: `z0_E1_equals_E4_massless_bubble_E4_squared`.

$$
\frac{\pi^{D} m_{2}^{D - 4} \Gamma\left(2 - \frac{D}{2}\right) \Gamma\left(4 - D\right) \Gamma^{2}\left(\frac{D}{2} - 1\right) \Gamma\left(2 D - 6\right)}{\Gamma\left(D - 2\right) \Gamma\left(\frac{3 D}{2} - 4\right)}
$$

##### Basis 10: `(0, 1, 1, 1, 0, 1, 1)`

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

##### Basis 11: `(0, 1, 1, 1, 1, 0, 2)`

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

#### Evaluation methods now available

1. Products of massive one-loop tadpoles.
2. z=0 degeneracies where E1=E4 and/or E2=E3.
3. The one-massless/two-equal-mass two-loop vacuum sunset in Gamma functions.
4. A massless bubble followed by a generalized on-shell massive one-loop integral.
5. Generic projective Feynman-parameter generation U, F, Delta for every one of the 12 basis integrals.

The next evaluation stage is therefore reduced to basis 8, 10, and 11.

Classification CSV: `output/ladder_12basis_parametric_classification.csv`

z=0 evaluation CSV: `output/ladder_12basis_z0_evaluation.csv`

---

### 4.5 `output/phase11_complete_ladder_basis_evaluation_trial.md`

### Phase 11: complete z=0 ordinary-ladder basis evaluation

All twelve terminal basis integrals are analytic in the convention-free Euclidean normalization.

#### 1. Reduced z=0 T family

At z=0, E1=E4 and E3=E2, so basis 8, 10 and 11 become

$$
T_n=\int\frac{d^Dk\,d^Dl}{L\,H\,E_2\,E_4^n},\qquad n=1,2,3.
$$

The reduced IBP family keeps K as an auxiliary denominator and uses (K,L,H,E2,E4). Degree-1 seeds already pivot T2 and T3.

##### T2 reduction

$$
T_2=-\frac{D-3}{2m^2}T_1-\frac{1}{2m^2}A,
$$

where the other lower sector in the raw IBP relation is scaleless and vanishes.

##### T3 reduction

$$
T_3=\frac{(D-6)(D-4)(D-3)}{8(m^2)^2(D-5)}T_1+\frac{(D-4)^2}{2(m^2)^2(D-5)}A+\frac{D-4}{4m^2(D-5)}E,
$$

with A and E given by massless two-point subloops followed by generalized on-shell one-loop electron integrals; both are Gamma-function closed forms.

#### 2. T1 Cheng-Wu reduction

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

#### 3. Completion status

- Exact z=0 terminal basis values: **12 / 12**
- Remaining unresolved z=0 basis integrals: **0**
- Basis 8: Cheng-Wu + hypergeometric reduction + Gauss summation
- Basis 10/11: dedicated z=0 symbolic IBP + Gamma lower sectors

Complete evaluation CSV: `output/ladder_12basis_z0_complete_evaluation.csv`

#### 4. Boundary of the result

These are convention-free Euclidean scalar-integral values. Overall Minkowski i factors, loop-measure conventions, renormalization-scale factors and the projector/reduction coefficients remain in their respective QEDCalc layers.

---

### 4.6 `output/phase12_ladder_assembly_trial.md`

### Phase 12: ordinary-ladder projector/reduction assembly

The corrected 72 raw projector monomials are first canonicalized under the ordinary-ladder graph symmetries and then composed with the exact 40-target x 12-basis symbolic IBP matrix.

- Corrected raw monomials: **72**
- Symmetry-canonical targets: **40**
- Terminal basis size: **12**

#### Leading z-pole audit

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

#### What remains for the finite z->0 limit

Because some basis coefficients have `C_i(z)=r_i/z+c_i+...`, the finite term also contains `r_i I_i'(0)`. Therefore the exact z=0 basis values alone are not sufficient. The next stage is to derive and IBP-reduce the first z-derivatives of basis 0, 1, 3, 5, 6, 7, and 8 (zero weights can be skipped), then combine them with the regular coefficient parts and perform the epsilon expansion.

---

### 4.7 `output/phase13_ladder_z_derivative_trial.md`

### Phase 13: ordinary-ladder basis z-derivative reduction

The phase-12 projector audit shows derivative weights only for basis 0, 1, 3, 5, 6, 7, and 8. This phase checks which of those derivatives are actually nonzero and closes all required analytic sectors, including basis 8 through a D+2 dimensional shift followed by z=0 IBP reduction.

#### Basis 0: `(0, 0, 0, 0, 0, 1, 1)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

#### Basis 1: `(0, 0, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

#### Basis 3: `(0, 0, 0, 0, 2, 0, 3)`

Status: **exact**. Method: `z_independent_factorized_lower`.

$$
0
$$

#### Basis 5: `(0, 1, 0, 0, 1, 0, 1)`

Status: **exact**. Method: `three_denominator_projective_beta`.

$$
\frac{4 \pi^{D} \Gamma^{2}\left(3 - \frac{D}{2}\right)}{D \left(D - 5\right) \left(D - 4\right) \left(D - 2\right)}
$$

#### Basis 6: `(0, 1, 0, 0, 1, 0, 2)`

Status: **exact**. Method: `three_denominator_projective_beta`.

$$
\frac{4 \pi^{D} \Gamma\left(3 - \frac{D}{2}\right) \Gamma\left(4 - \frac{D}{2}\right)}{D \left(D - 6\right) \left(D - 5\right) \left(D - 2\right)}
$$

#### Basis 7: `(0, 1, 1, 0, 0, 0, 1)`

Status: **exact**. Method: `z_independent_projective_F`.

$$
0
$$

#### Basis 8: `(0, 1, 1, 0, 1, 0, 1)`

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

#### Result

- Basis 0, 1, 3: derivative is exactly zero because the factorized lower-sector value is z-independent.
- Basis 7: derivative is exactly zero because its projective F polynomial contains no z.
- Basis 5 and 6: first derivatives are analytic Gamma-function expressions.
- Basis 8: the derivative is mapped to a D+2 shifted scalar integral and reduced by z=0 IBP to T1 plus known lower sectors.
- Remaining unresolved required first-z derivatives: **0**.

---

### 4.8 `output/phase14_ladder_finite_checkpoint_trial.md`

### Phase 14: convention-aware ordinary-ladder finite checkpoint

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

### 4.9 `output/phase81_ordinary_ladder_end_to_end_checkpoint.md`

### Phase 81: ordinary ladder end-to-end checkpoint

QEDCalc version: `0.88.2`

#### Reduction chain

- corrected spin-sum projector table: 72 terms
- canonical IBP targets after symmetry combination: 40
- terminal analytic basis size: 12
- leading magnetic-projector z-pole residual: `0`

#### Bare finite coefficient

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

#### On-shell subtraction

$$
Z_1^{(1)}F_2^{(1)}=-\frac{3}{4\delta}+2+O(\delta).
$$

Pole coefficient: `-3/4`
Finite subtraction: `2`

The pole cancels against the bare ladder pole, while the finite subtraction removes 2.

#### Renormalized ordinary ladder

$$
A_{\mathrm L}=\frac{11}{48}+\frac{\pi^2}{18}.
$$

Numerical end-to-end reconstruction: **0.77747802228274214548465185876007285877369221812845**
Independent analytic value: **0.77747802228274214549080505554867506307298330040227**
Absolute difference: **6.1531967886e-21**
Symbolic renormalized residual: `0`

No final ordinary-ladder coefficient is fed into the 72 -> 40 -> 12 master reconstruction; the closed form is used only as the output-side checkpoint.

---

## 5. Large algebra/reduction files

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

## 6. Release-layer status

Phase 81 artifact(s): `output/phase81_ordinary_ladder_end_to_end_checkpoint.md`.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.
