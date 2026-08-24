# QEDCalc サンプルプログラム説明書兼計算過程説明書：ordinary ladder 1図

## 0. この資料の目的

2ループ ordinary ladder 1図について、D次元 Pauli projector、72項の projector 展開、40 canonical target、12 master basis、on-shell subtraction を経て renormalized $F_2(0)$ を得るまでを説明する。ordinary ladder は $(D-4)\times1/(D-4)$ の有限残差を持つため、特に「なぜ4次元へ早く置いてはいけないか」を明示する。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **ordinary ladder 1図** である。

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
\mathcal I_{\rm L}^{\rm raw}
\longrightarrow
\mathcal P_{F_2}^{(D)}
\longrightarrow
72\text{ terms}
\longrightarrow
40\text{ targets}
\longrightarrow
12\text{ masters}
\longrightarrow
F_{2,\rm L}^{\rm bare}(0)
\longrightarrow
F_{2,\rm L}^{\rm R}(0)
$$

である。

## 1. 元の入力となる Feynman 図

### 1.1 【人が決める】Feynman 則と D 次元

ordinary ladder は2本の内部 photon が交差しない図である。Feynman gauge で、raw input は次である。

$$
\frac{e^4}{(2\pi)^8 i^2}
\int d^Dk\,d^Dl
\gamma^\rho
\frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon}
\gamma^\alpha
\frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon}
\gamma_\mu
\frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon}
\gamma_\alpha
\frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon}
\gamma_\rho
\frac{1}{-k^2-i\varepsilon}
\frac{1}{-l^2-i\varepsilon}
$$

ここで積分 measure を最初から $d^4k\,d^4l$ とせず $d^Dk\,d^Dl$ とする。理由は UV pole と $D$ 依存 numerator の積が有限定数を生むためであり、途中で $D=4$ とするとその有限部を失う。

## 2. raw LaTeX を denominator family へ落とす

### 2.1 【QEDCalc】parse と electron propagator detection

#### この段階へ入る入力

入力は前節の ordinary ladder complete RHS であり、ファイル

`input/ordinary_ladder_2loop_bare.tex`

に LaTeX として保存されている。人が図から確定した非可換順序を、そのまま保持した式でなければならない。

#### QEDCalc へ実際に渡す入力

```python
raw_source = RAW.read_text(encoding='utf-8')
raw_diagram = parse_loop_integral_latex(raw_source)
raw_info = analyze_raw_ordinary_ladder(raw_diagram)
```

である。つまり `raw_info` は入力ではなく、raw LaTeX を解析した結果である。

#### QEDCalc が認識すべき denominator

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

#### QEDCalc の出力

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

## 3. D次元 Pauli projector

### 3.1 【人が決める】projector の ansatz

#### 何を導出するのか

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

### 3.2 【QEDCalc】trace 方程式を解く

#### QEDCalc への入力

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

## 4. $q\to0$ の有限 projector：$A_0$ と $C_1$

### 4.1 【人が決める】なぜ $A_0$ と $C_1$ に分けるか

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

## 5. Dirac/Lorentz 代数を scalar integrals へ

### 5.1 【QEDCalc】raw q=0 numerator と scalar-product rules

#### 入力

入力は parse 済み ordinary-ladder electron chain と、4節で得た finite $q\to0$ projector の $A_0,C_1$ combination である。

#### 出力

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

## 6. 72 projector terms → 40 targets → 12 master basis

### 6.1 【QEDCalc】corrected spin-sum projector と reduction data

#### 入力

入力は前節の scalar-integral term table と、ordinary-ladder IBP family の index convention である。

#### 出力

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

### 6.2 【人が理解する】72、40、12 の意味

- **72**：corrected finite-$q$ spin-sum projector を scalar integral monomial へ分解した非零項。
- **40**：対称性・zero sector・同値関係などを整理した canonical reduction targets。
- **12**：最終的に必要な terminal master basis。

これは「72個の Feynman 図」という意味ではない。

### 6.3 【QEDCalc】bare finite coefficient の再構成

#### 入力

入力は12 master basis の係数と、それぞれの $D=4-2\epsilon$ Laurent 展開である。

#### 出力

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

## 7. renormalization subtraction

### 7.1 【人が決める】何を subtraction するか

ordinary ladder 単体の bare graph は UV pole を持つので、1ループ vertex renormalization の counterterm insertion を加える。on-shell scheme では必要な量は $F_2^{(1)}(D,0)$ と $Z_1^{(1)}$ である。

### 7.2 【QEDCalc】1-loop ingredients と subtraction series

#### 入力

入力は bare ladder Laurent series と、人が7.1で指定した on-shell vertex counterterm $Z_1^{(1)}F_2^{(1)}$ である。

#### 出力

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

## 8. Phase 81 end-to-end checkpoint

Phase 81 は 72→40→12 の master reconstruction と subtraction を1つの completion checkpoint としてまとめる。高精度 numerical extended audit が利用できる環境では master values から bare finite を再構成し、標準 validation では保存データの exact invariant を確認する。

**該当コード：`examples/phase81_ordinary_ladder_end_to_end_checkpoint.py` 118～140 行**

```python
    "## On-shell subtraction",
    "",
    "$$",
    r"Z_1^{(1)}F_2^{(1)}=-\frac{3}{4\delta}+2+O(\delta).",
    "$$",
    "",
    f"Pole coefficient: `{sub_pole}`",
    f"Finite subtraction: `{sub_finite}`",
    "",
    "The pole cancels against the bare ladder pole, while the finite subtraction removes 2.",
    "",
    "## Renormalized ordinary ladder",
    "",
    "$$",
    r"A_{\mathrm L}=\frac{11}{48}+\frac{\pi^2}{18}.",
    "$$",
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

## 9. 現在の自動化境界

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

## 10. 最短再計算手順

1. `input/ordinary_ladder_2loop_bare.tex` を確認。
2. `ladder_2loop_trial.py` で raw family と projector/subtraction を確認。
3. Phase 14 または Phase 81 で 72→40→12→bare を再構成。
4. Phase 81 で renormalized coefficient を確認。
5. `run_v090_validation.bat` で7図統合値が壊れていないことを確認。

## 11. この資料で省略できた手計算

29個・33個の scalar integral を人が逐一展開する作業、IBP 行列消去、12 master への係数集約、Laurent series の大量整理、pole cancellation の項別照合は、現在のサンプルと reduction data から再現できる。そのため本資料では「なぜその reduction が必要か」と「どのデータが入力か」を残し、数百行の機械代数は省略する。

## 12. 参照元と再実行ファイル

- 元計算資料：`ladder_F2_4/ladder_Feynman図から最終結果_統合版_修正版.md`
- 完成導出：`ladder_F2_4/QED_2loop_ordinary_ladder_独立導出_完成版.md`
- 詳細別冊：`ladder_F2_4/ladder_計算詳細別冊_修正版.md`
- raw input：`input/ordinary_ladder_2loop_bare.tex`
- main sample：`examples/ladder_2loop_trial.py`
- finite master checkpoint：Phase 14
- release closure：Phase 81

代表実行は `run_ladder_2loop_demo.bat`、`run_phase14_ladder_finite_checkpoint_demo.bat`、`run_phase81_ordinary_ladder_end_to_end_checkpoint.bat`。全体 regression は `run_v090_validation.bat`。


---

## 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。
