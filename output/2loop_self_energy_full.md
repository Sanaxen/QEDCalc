# QEDCalc two-loop full process report: Self-energy insertion pair

Diagram multiplicity: **2**.

This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.

Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\times`, or `\cdot`.

## 1. Raw input expressions

### `input/self_energy_insertion_left_2loop_bare.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma^\beta \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \\
\gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \left( -\left( g_{\rho\sigma} +(1-\alpha)\frac{k_\rho k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\left( -\left( g_{\alpha\beta} +(1-\alpha)\frac{l_\alpha l_\beta}{-l^2-i\varepsilon} \right) \frac{1}{-l^2-i\varepsilon} \right)
\end{aligned}
$$

### `input/self_energy_insertion_right_2loop_bare.tex`

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \\
\gamma^\beta \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \left( -\left( g_{\rho\sigma} +(1-\alpha)\frac{k_\rho k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\left( -\left( g_{\alpha\beta} +(1-\alpha)\frac{l_\alpha l_\beta}{-l^2-i\varepsilon} \right) \frac{1}{-l^2-i\varepsilon} \right)
\end{aligned}
$$

### `input/self_energy_subloop_numerator.tex`

$$
\gamma^\alpha
\left(
m+\rlap{/}r-\rlap{/}l
\right)
\gamma_\alpha
$$

## 2. Complete calculation-process guide

Source: `doc/QEDCalc_2loop_5sample_manuals_v2/04_self_energy_insertion_2図_QEDCalcサンプル説明書兼計算過程説明書.md`

This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.

### QEDCalc サンプルプログラム説明書兼計算過程説明書：self-energy insertion 2図

#### 0. この資料の目的

外部 vertex の左右電子 propagator に1ループ electron self-energy を挿入する2図について、raw diagram の自動検出、subloop contraction、on-shell counterterm、UV cancellation、finite part、IR logarithm、corner との相殺までを説明する。この図群は QEDCalc が raw 2図から subdiagram をかなり直接的に抽出できる例である。

この資料は、元の計算過程説明書を置き換えるものではない。元資料で丁寧に追った物理的判断のうち、QEDCalc に任せられる機械代数をサンプルプログラムへ移し、**人間が用意する入力と QEDCalc が返す出力の境界を明示した再計算用説明書**である。

対象は **self-energy insertion 2図** である。

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

#### 1. 元の入力となる2図

##### 1.1 【人が決める】right insertion

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p+\rlap{/}k+\rlap{/}l-i\varepsilon} \\
\gamma^\beta \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \left( -\left( g_{\rho\sigma} +(1-\alpha)\frac{k_\rho k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\left( -\left( g_{\alpha\beta} +(1-\alpha)\frac{l_\alpha l_\beta}{-l^2-i\varepsilon} \right) \frac{1}{-l^2-i\varepsilon} \right)
\end{aligned}
$$

##### 1.2 【人が決める】left insertion

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2} \int d^4k\,d^4l \gamma^\rho \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \gamma^\alpha \frac{1}{m-\rlap{/}p'+\rlap{/}k+\rlap{/}l-i\varepsilon} \gamma^\beta \frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon} \\
\gamma_\mu \frac{1}{m-\rlap{/}p+\rlap{/}k-i\varepsilon} \gamma^\sigma \left( -\left( g_{\rho\sigma} +(1-\alpha)\frac{k_\rho k_\sigma}{-k^2-i\varepsilon} \right) \frac{1}{-k^2-i\varepsilon} \right) \\
\left( -\left( g_{\alpha\beta} +(1-\alpha)\frac{l_\alpha l_\beta}{-l^2-i\varepsilon} \right) \frac{1}{-l^2-i\varepsilon} \right)
\end{aligned}
$$

両図の特徴は、self-energy subloop の前後で同じ outer electron propagator が繰り返され、内部に1本の electron propagator と photon propagator が挿入されることである。

#### 2. raw diagram から self-energy subdiagram を見つける

##### 2.1 【QEDCalc】pattern detection と contraction

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

#### 3. self-energy numerator の Dirac 代数

##### 3.1 【接続】subloop numerator

Feynman gauge の metric part では numerator は

$$
\gamma^\alpha
\left(
m+\rlap{/}r-\rlap{/}l
\right)
\gamma_\alpha
$$

である。

##### 3.2 【QEDCalc】gamma contraction、shift、odd 項除去

###### 入力

入力は subloop numerator

$$
\gamma^\alpha(m+\rlap{/}r-\rlap{/}l)\gamma_\alpha
$$

と、electron/photon denominator をまとめる Feynman parameter $a$ である。

###### 出力

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

#### 4. on-shell renormalization

##### 4.1 【人が決める】renormalization condition

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

##### 4.2 【QEDCalc】UV cancellation と compact outer diagram

###### 入力

入力は $\Sigma(r)=mA(r^2)+\rlap{/}rB(r^2)$ の parameter 表示と、4.1で人が指定した on-shell 条件である。

###### 出力

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

#### 5. logarithm を rational parameter integral に戻す

##### 5.1 【人が理解する】なぜ rationalization するか

renormalized self-energy には $\ln(\Delta/\Delta_0)$ が現れる。このまま外側 Feynman parameter 積分へ入れるより、補助 parameter $z$ を使って rational integrand に戻した方が QEDCalc の代数処理と積分 reduction を適用しやすい。

##### 5.2 【QEDCalc】log prefactor と denominator

###### 入力

入力は on-shell subtraction 後に残る logarithmic difference である。

###### 出力

QEDCalc は恒等式を使って log を追加 parameter $z$ の rational integral に戻し、分子 prefactor と denominator を別々の symbolic expression として返す。これにより後段の多変数積分を純粋な rational integrand $G_A$ として扱える。

メイン trial の `log_ratio_prefactor()` と `log_ratio_parameter_kernel()` がこの入力を作り、finite 4-parameter integrand $G_A$ へ接続する。コードは上の48～67行に含まれる。

#### 6. finite part $A_A$

##### 6.1 【QEDCalc】4変数 integrand → 1変数 kernel

###### 入力

入力は rationalized finite four-parameter integrand $G_A(a,b,q,z)$ である。

###### 出力

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

#### 7. IR part $A_B$

##### 7.1 【人が決める】$\rho$ を0にする前に asymptotic を取る

IR sector は photon mass regulator $\rho$ を持つ。積分の前に単純に $\rho=0$ としてはいけない。QEDCalc は small-$\rho$ asymptotic を

$$
A_B(\rho) =
\ln\rho +
\frac12 +o(1)
$$

として保持する。

##### 7.2 【QEDCalc】finite + IR を合成する

###### 入力

入力は finite sector $A_A(0)$ と、photon-mass regulator を保持した IR sector $A_B(\rho)$ である。

###### 出力

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

#### 8. raw-to-final audit

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

#### 9. corner との IR cancellation

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
#### 10. 現在の自動化境界

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

#### 11. 最短再計算手順

1. raw left/right `.tex` を確認。
2. `self_energy_insertion_2loop_trial.py` で subdiagram detection と downstream outputs を生成。
3. Phase 31 で raw-to-final audit。
4. Phase 80 で release closure と corner IR cancellation を確認。
5. v0.90 regression で7図全体を確認。

#### 12. この資料で省略できた手計算

旧資料で長かった gamma contraction、counterterm 後 numerator の展開、log rationalization、4変数 integrand の展開、逐次積分の単純代数、IR/finite constant の数値認識は QEDCalc で再生成できる。残すべきなのは on-shell renormalization の意味と、IR limit の取り方である。

#### 13. 参照元と再実行ファイル

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

#### 改訂注記（入出力連結の明示）

この版では、各 QEDCalc 処理について「関数名」だけでなく、**前段階から何が入力されるか、入力を人がどう準備するか、QEDCalc が何を返すか、その出力を次に何へ使うか**を明示した。特に引数なし関数についても、内部で読む input file または内部に固定された物理条件を入力として記述している。

## 3. Recorded runtime artifacts

| Artifact | Type | Lines | Bytes |
| --- | --- | ---: | ---: |
| `output/self_energy_insertion_2loop_trial.md` | `md` | 202 | 8862 |
| `output/phase80_self_energy_end_to_end_checkpoint.md` | `md` | 31 | 469 |

## 4. Recorded Markdown stages

### 4.1 `output/self_energy_insertion_2loop_trial.md`

### QEDCalc two-loop trial: self-energy insertion

Generated: 2026-08-22T11:10:31

#### Version

QEDCalc v0.23.0

#### Loaded conventions

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

#### Outer prefactor generated from conventions.txt

$$
\frac{e^{2}}{(2\pi)^4 i}
$$

#### Scope

v0.22 parses each bare two-loop self-energy-insertion RHS as one LoopIntegralExpression, discovers the open one-loop self-energy block from the repeated electron propagator pattern, identifies whether the insertion is left or right of the external photon vertex, and contracts it to S Sigma S. After the existing on-shell UV cancellation check passes, the same topology is rendered with Sigma_R. The internal-photon reduction currently selects the Feynman-gauge metric part; automatic finite on-shell counterterm reconstruction directly from the raw general-gauge expression remains a later step.

#### Raw right-insertion two-loop RHS

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2}\,\int d^{4}k\,d^{4}l\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k + \rlap{/}l - \left(i\,\varepsilon\right)}\,\gamma^{\beta}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right) \\
\left(-\left(g_{\alpha\beta} + \left(1 - \left(\alpha\right)\right)\,\frac{l_{\alpha}\,l_{\beta}}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

#### Right subdiagram detection

PASS: side=right, subloop=l, external momentum=p - \left(k\right)

#### Right self-energy numerator extracted from raw RHS

$$
4\left(m\right) - 2\left(\rlap{/}\left(p - \left(k\right)\right)\right) + 2\left(\rlap{/}l\right)
$$

#### Right compact bare outer diagram

$$
\begin{aligned}
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\Sigma^{(1)}\left(p - \left(k\right)\right) \\
\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

#### Raw left-insertion two-loop RHS

$$
\begin{aligned}
\frac{e^4}{(2\pi)^8 i^2}\,\int d^{4}k\,d^{4}l\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma^{\alpha}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k + \rlap{/}l - \left(i\,\varepsilon\right)} \\
\gamma^{\beta}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right) \\
\left(-\left(g_{\alpha\beta} + \left(1 - \left(\alpha\right)\right)\,\frac{l_{\alpha}\,l_{\beta}}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(l\cdot l\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

#### Left subdiagram detection

PASS: side=left, subloop=l, external momentum=p' - \left(k\right)

#### Left self-energy numerator extracted from raw RHS

$$
4\left(m\right) - 2\left(\rlap{/}\left(p' - \left(k\right)\right)\right) + 2\left(\rlap{/}l\right)
$$

#### Left compact bare outer diagram

$$
\begin{aligned}
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\Sigma^{(1)}\left(p' - \left(k\right)\right)\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu} \\
\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

#### Self-energy subloop numerator input

$$
\gamma^{\alpha}\,\left(m + \rlap{/}r - \left(\rlap{/}l\right)\right)\,\gamma_{\alpha}
$$

#### After expansion and gamma contraction

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(\rlap{/}l\right)
$$

#### After l = t + a r

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(\rlap{/}t\right) + 2\left(a\,\rlap{/}r\right)
$$

#### After removing odd t terms

$$
4\left(m\right) - 2\left(\rlap{/}r\right) + 2\left(a\,\rlap{/}r\right)
$$

#### Self-energy denominator

$$
a m^{2} + a r_{2} \left(a - 1\right) + \lambda^{2} \left(1 - a\right)
$$

#### On-shell denominator

$$
a^{2} m^{2} + \lambda^{2} \left(1 - a\right)
$$

#### UV numerator after on-shell counterterms

$$
0
$$

#### UV cancellation check

PASS

#### Right compact renormalized outer diagram

$$
\begin{aligned}
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\gamma_{\mu}\,\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\Sigma_R^{(1)}\left(p - \left(k\right)\right) \\
\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

#### Left compact renormalized outer diagram

$$
\begin{aligned}
\frac{e^{2}}{(2\pi)^4 i}\,\int d^{4}k\,\gamma^{\rho}\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)} \\
\Sigma_R^{(1)}\left(p' - \left(k\right)\right)\,\frac{1}{m - \left(\rlap{/}p'\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma_{\mu} \\
\frac{1}{m - \left(\rlap{/}p\right) + \rlap{/}k - \left(i\,\varepsilon\right)}\,\gamma^{\sigma} \\
\left(-\left(g_{\rho\sigma} + \left(1 - \left(\alpha\right)\right)\,\frac{k_{\rho}\,k_{\sigma}}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)\,\frac{1}{-\left(k\cdot k\right) - \left(i\,\varepsilon\right)}\right)
\end{aligned}
$$

#### Rationalized logarithm prefactor

$$
- a \left(a - 1\right) \left(m^{2} - r_{2}\right)
$$

#### Rationalized logarithm denominator

$$
a^{2} m^{2} - a z \left(a - 1\right) \left(m^{2} - r_{2}\right) + \lambda^{2} \left(1 - a\right)
$$

#### Finite four-parameter integrand G_A

$$
\frac{\begin{gathered}
\left(a - 1\right) \left(b - q\right) \left(q - 1\right) \\
\left(4 a^{2} b q + 2 a^{2} b - 3 a^{2} q^{3} z - 3 a^{2} q^{2} z - 4 a b q + 4 a b + 6 a q^{3} z + 2 a q^{2} z - 3 q^{3} z + q^{2} z\right)
\end{gathered}}{\left(a b - q^{2} z \left(a - 1\right)\right)^{2}}
$$

#### Analytic b-integrated kernel

$$
\frac{\begin{gathered}
q \left(a - 1\right) \left(q - 1\right) \\
\left(a \left(5 a q + a - 5 q + 7\right) - \left(2 a \left(2 a q + a - 2 q + 2\right) - q z \left(a - 1\right) \left(5 a q + a - 5 q + 7\right)\right) \log{\left(\frac{- a + q z \left(a - 1\right)}{q z \left(a - 1\right)} \right)}\right)
\end{gathered}}{a^{2}}
$$

#### Final one-variable finite kernel

$$
\frac{\begin{gathered}
\frac{a^{2} \left(a - 1\right)^{2}}{4} - \frac{a^{2} \left(\left(1 - 3 a\right) \left(a - 1\right) + 1\right) \log{\left(a \right)}}{6} + \frac{a \left(a - 1\right)}{6} {}+ \\
\frac{\left(a - 1\right) \left(a^{2} \left(1 - 3 a\right) + a + 1\right) \log{\left(1 - a \right)}}{6}
\end{gathered}}{a^{2} \left(a - 1\right)}
$$

#### Finite coefficient numerical value

A_A = -0.5899780222827421454908045555486750630724843581250211812

#### Finite coefficient analytic recognition

$$
- \frac{\pi^{2}}{18} - \frac{1}{24}
$$

#### Finite coefficient reference

$$
- \frac{\pi^{2}}{18} - \frac{1}{24}
$$

#### Finite-part recognition check

PASS

#### IR part through O(rho^0)

$$
\log{\left(\rho \right)} + \frac{1}{2}
$$

#### Total self-energy-insertion coefficient

$$
\log{\left(\rho \right)} - \frac{\pi^{2}}{18} + \frac{11}{24}
$$

#### Equivalent conventional form

$$
A_{\mathrm S}=-\frac12\ln\rho^{-2}+\frac{11}{24}-\frac{\pi^2}{18}
$$

---

### 4.2 `output/phase80_self_energy_end_to_end_checkpoint.md`

### Phase 80: self-energy insertion end-to-end checkpoint

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

## 5. Large algebra/reduction files

No graph-specific CSV/TXT artifact is currently stored.

## 6. Release-layer status

Phase 80 artifact(s): `output/phase80_self_energy_end_to_end_checkpoint.md`.

The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.
