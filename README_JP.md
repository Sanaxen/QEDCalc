# QEDCalc v0.90.0

QEDCalc は、QED の長い計算を小さな処理関数へ分解し、人間が物理的な手順を決めながら計算を進めるための試作ツールです。

既定の1ループ頂点補正サンプルでは、LaTeX 入力から処理を順番に適用し、最終的に

$$
F_2(0)=\frac{\alpha}{2\pi}
$$

まで到達します。

v0.10.0 以降は、2ループ以上へ拡張するための多ループ基盤も追加しています。v0.13.x では subdiagram / forest bookkeeping と counterterm subtraction の管理層、v0.14.0 では contracted graph・Taylor subtraction・Zimmermann forest sum を追加しました。v0.16.0 では、明示的な factor 順序から contracted topology の実際の QED amplitude を組み立てる層と、$k^\mu l^\nu$ などの混合多ループ tensor reduction を追加しています。

## ドキュメント

- `README.md`：日本語クイックスタート
- `README_EN.md`：English Quick Start
- `REFERENCE.md`：日本語リファレンスマニュアル
- `REFERENCE_EN.md`：English Reference Manual
- `CHANGELOG.md`：変更履歴
- `ROADMAP.md`：開発ロードマップ

## 動作環境

- Windows 11
- Python 3.11 以上
- SymPy 1.13 以上

## 初回セットアップ

展開したフォルダで `setup_env.bat` を実行してください。

このバッチは `.venv` を作成し、`requirements.txt` に記載されたライブラリを仮想環境へ導入します。

以前の版で壊れた `.venv` が残っている場合は、`.venv` フォルダを削除してから再実行してください。


## 計算規約 `conventions.txt`

QEDCalc は、計算途中で規約を質問して停止しません。プロジェクト直下の `conventions.txt` を計算開始時に読み込みます。

既定値は次のとおりです。

```text
[Spacetime]
metric_signature = +---
dimreg_dimension = 4 - 2*epsilon

[Gauge]
gauge = feynman

[Renormalization]
renormalization_scheme = on_shell
dimreg_subtraction = MSbar
msbar_factor = true

[Subdiagram]
subdiagram_include_coupling = true
subdiagram_include_loop_measure = true
subdiagram_include_i = true

[Normalization]
coupling_symbol = e
loop_measure_denominator_latex = (2\pi)^4
loop_i_factor_latex = i
```

`subdiagram_include_*` は、1ループ subdiagram を縮約したときに coupling、loop measure、$i$ をその subdiagram が所有するかを指定します。既定設定では、2ループ self-energy insertion を $S\Sigma S$ へ縮約した後の outer prefactor は設定から自動的に

$$
\frac{e^2}{(2\pi)^4 i}
$$

と構成されます。

設定内容だけを確認する場合は `run_conventions_demo.bat` を実行してください。未知の設定キー、不正な値、現在未対応の gauge などは対話入力へフォールバックせずエラーになります。

## 1ループ頂点補正サンプル

`run_qedcalc.bat` を実行します。

入力：

```text
input\vertex_1loop_integrand.tex
```

出力：

```text
output\vertex_1loop_session.md
```

## 多ループ基盤デモ

`run_multiloop_demo.bat` を実行します。

出力：

```text
output\multiloop_foundation.md
```

このデモでは、2個のループ運動量、行列平方完成、多ループ分子同時シフト、一般 Feynman parameter 化、$D$ 次元標準積分、counterterm 置換を確認できます。

## Topology / amplitude デモ

`run_topology_demo.bat` を実行します。

出力：

```text
output\topology_amplitude_demo.md
```

このデモでは、明示的な factor 順序から bare amplitude を組み立て、declared subdiagram を局所 counterterm vertex へ縮約します。また、2ループ二次形式に対する混合 rank-2 / rank-4 tensor reduction を確認できます。

## 記号定義

入力で使用可能な記号は `symbols.txt` で事前定義します。

```text
[Scalar]
m
e
\alpha
\varepsilon
\lambda
epsilon_UV
epsilon_IR

[Constants]
i
\pi

[Vector]
p
p'
q
k
l
r

[Index]
\mu
\nu
\rho
\sigma
\alpha
\beta
\lambda
```

ギリシャ文字は LaTeX 表記で記述します。未定義記号は推測せずエラーになります。

## Markdown 数式出力

表示数式は必ず前後に空行を置きます。

```markdown
Text

$$
formula
$$

Text
```

## テスト

`run_tests.bat` を実行してください。

v0.40.0 では 175 テストを通過しています。

詳細な API、数式規約、制限事項は `REFERENCE.md` を参照してください。


## v0.16.0 時点の主な追加機能

- `symmetric_even_rank()`：rank 2, 4, 6, 8, ... の一般偶数 rank tensor reduction
- `dimreg_scale_factor()`：MS / MS-bar の $\mu^{2L\epsilon}$ 規約因子
- `renormalized_dimreg_series()`：規約因子適用、Laurent 展開、minimal subtraction
- `bookkeep_uv_ir()`：UV、IR、mixed UV/IR pole の分離
- `qed_counterterm_library()`：$\delta Z_1$, $\delta Z_2$, $\delta m$, $\delta Z_3$ の標準構造
- `contract_graph()`：宣言済み forest から contracted graph $G/F$ の topology を生成
- `taylor_operator()`：全次数指定の多変数 Taylor subtraction
- `bphz_local_counterterm()` / `bphz_subtract()`：局所 BPHZ subtraction
- `forest_formula()`：compatible forest の符号付き和を構成

詳細は `REFERENCE.md` を参照してください。


## v0.16.0 Zimmermann / BPHZ デモ

Windows では次を実行します。

```text
run_forest_demo.bat
```

結果は `output/forest_subtraction_demo.md` に保存されます。


## v0.16.0: 最初の2ループ実戦試験

`run_vp_2loop_demo.bat` で vacuum polarization 図の試験を実行できる。閉じた電子ループの Dirac trace から有限2変数積分までを処理し、最終係数 `119/36 - pi^2/3` を数値結果から認識する。

## v0.17.0: 2つ目の2ループ実戦試験 — self-energy insertion

v0.17.0 では、左右の electron self-energy insertion 2図を2つ目の実戦対象として追加した。

QEDCalc は明示的に切り出した1ループ self-energy subdiagram に対して、Dirac numerator の縮約、Feynman-parameter shift、odd-loop term の除去、on-shell counterterm の式、UV subdivergence cancellation、logarithm の rational parameter 表現、有限積分の数値／解析 cross-check を行う。

最終 checkpoint は

$$
A_{\mathrm S}
=
-\frac12\ln\rho^{-2}
+\frac{11}{24}
-\frac{\pi^2}{18}
$$

である。元の2ループ aligned LaTeX 全体を一つの expression として完全 parse する方式ではなく、self-energy subdiagram を topology metadata として明示する方式を採用している。

実行は `run_self_energy_2loop_demo.bat`。

## v0.18.0: ordinary ladder 2ループ試験

`run_ladder_2loop_demo.bat` を追加しました。D次元 projector、scalar-product denominator basis、75項 integral-family table の検証、1ループ subtraction を処理し、

$$
F_{2,\mathrm L}^{(4)}(0)=\left(\frac{\alpha}{\pi}\right)^2\left(\frac{11}{48}+\frac{\pi^2}{18}\right)
$$

を再現します。v0.26.0 では、資料に保存されている historical 75係数監査表も raw bare ladder から完全再生成できます。ただし、この75表は後の監査で修正された spin-sum trace 順序とは別物として明示的に管理します。


## v0.19.0: crossed ladder 2ループ試験

`run_crossed_ladder_2loop_demo.bat` を追加しました。資料で独立導出された projective parameter 表示から、$V$ に線形な $\Delta,W$、$h,t,q$ 変換、1変数 dilogarithm canonical kernel、$q=1/2$ sector、endpoint-safe 合成、全微分境界項との発散相殺を検証し、

$$
F_{2,\mathrm X}^{(4)}(0)
=
\left(\frac{\alpha}{\pi}\right)^2
\left[
\frac16
+\frac{13\pi^2}{36}
+\frac54\zeta(3)
-\frac{5\pi^2}{6}\ln2
\right]
$$

を再現します。現段階では、元の数百項の raw Dirac reduction から5変数 integrand $G_{\mathrm X}$ を完全自動生成してはいません。projective / one-variable reduction 以降をQEDCalcが検証する構成です。


## v0.20.0: corner (IIc) 2ループ試験

`run_corner_2loop_demo.bat` を追加しました。今回の試験では、独立導出済みの UV-finite parameter representation から、soft scaling、IR logarithm の exact coefficient、momentum-shift correction、$K+\kappa^2$ hard sector、$z$ sector、self-energy insertion との IR cancellation を別々に検証します。

soft region からは

$$
\int_0^1dv\int_0^\infty dR\int_0^\infty dS\,G(R,S,v)=1
$$

を SymPy により再確認し、$\ln(1/\rho)$ の係数が exact に1であることを検証します。

有限部分は

$$
H_{K\kappa}
=
-\frac{11}{3}-\frac98\zeta(3)+\frac{\pi^2}{18}+\frac{7\pi^2}{12}\ln2
$$

と

$$
A_z
=
\frac78+\frac58\zeta(3)-\frac{\pi^2}{4}\ln2
$$

を独立に保持し、

$$
A_{\mathrm C,fin}
=
-\frac{67}{24}+\frac{\pi^2}{18}-\frac12\zeta(3)+\frac{\pi^2}{3}\ln2
$$

を再現します。

また self-energy insertion 側の IR coefficient $-1$ と合わせて regulator logarithm が exact に相殺することを確認します。

現段階では、元の2ループ6-denominator LaTeX式から magnetic projector 後の UV-finite parameter kernel を完全自動生成してはいません。今回の trial は、その独立導出済み kernel 以降をQEDCalcで再検証するものです。

## v0.21.0: bare 2ループLaTeX入力の開始

v0.21.0 では、2ループ vacuum polarization 図について、閉じた電子ループの分子だけではなく、bare 2-loop RHS 全体を次の形で入力できるようになりました。

```latex
-\frac{e^4}{(2\pi)^8 i^2}
\int d^4k\,d^4l
\gamma^\rho
\frac{1}{m-\rlap{/}p'+\rlap{/}k-i\varepsilon}
\cdots
\operatorname{tr}\left[
\frac{1}{m-\rlap{/}l-\rlap{/}k-i\varepsilon}
\gamma^\alpha
\frac{1}{m-\rlap{/}l-i\varepsilon}
\gamma^\beta
\right]
\cdots
```

`parse_loop_integral_latex()` は、overall normalization、loop measure、integrand を分離して保持します。integrand 内の `DiracTrace` は自動検出され、その内部の fermion propagator を scalarize した後、trace numerator と scalar denominator を分離できます。

現段階では overall normalization はユーザーの規約を壊さないため LaTeX text のまま保持します。outer diagram 全体から renormalized scalar kernel までを一命令で生成する段階にはまだ達していません。


## v0.22.1: bare self-energy insertion の自動検出

v0.22.1 では、左右の self-energy insertion 2図について、bare 2-loop RHS 全体を1つの LaTeX 入力として読み込めるようにしました。電子線上の

$$
S(r)\,\gamma^\alpha\,S(r-l)\,\gamma^\beta\,S(r)
$$

という反復 propagator 構造と、別因子として存在する $l$ photon を順序情報から自動検出します。右図では $r=p-k$、左図では $r'=p'-k$ を自動認識し、

$$
S(r)\Sigma^{(1)}(r)S(r)
$$

へ縮約します。既存の on-shell UV cancellation check が成功した後は、同じ topology を $\Sigma_R^{(1)}$ として出力できます。内部 photon の numerator reduction は現段階では Feynman gauge の metric 部分を使用します。

## v0.25.0: ordinary ladder raw-input bridge

ordinary ladder でも、元の bare 2-loop RHS を `input/ordinary_ladder_2loop_bare.tex` から直接読み込めるようになりました。

QEDCalc は raw 式から自動で、

- symbolic dimension `D` の $d^Dk\,d^Dl$
- 4本の電子 propagator の運動量と $E_1,E_2,E_3,E_4$
- photon denominators $K=-k^2$, $L=-l^2$
- auxiliary denominator $H=-(k+l)^2$
- bare integral-family index $J(1,1,0,1,1,1,1)$
- $q=0$ の Dirac numerator $N_\mu^{(0)}$

を生成します。scalar-product の denominator-basis 規則も、固定表ではなく denominator 定義の連立方程式から再導出できます。

v0.26.0 では historical general-$q^2$ projector trace から75項の監査表そのものを raw bare 式から完全再生成できます。v0.27.0 では一般 IBP 恒等式生成器と有限疎 Laporta 消去コアまで実装済みです。残る大きな課題は seed 領域の自動拡張、sector/zero-sector 処理、完全な master-integral reduction です。

## v0.25.0 の追加

- 任意長の $D$ 次元 Clifford trace を追加。
- fully-contracted trace の高速 SymPy 経路を追加。
- raw ordinary ladder から $A_0$ projector trace を再生成。
- $A_0$ の29 scalar integrals を raw bare LaTeX から自動生成。
- `run_ladder_a0_trace_demo.bat` を追加。

## v0.26.0: general-$q^2$ ladder trace audit

`run_ladder_general_q_trace_demo.bat` を追加しました。raw ordinary-ladder LaTeX から一般 $q^2$ の長い $D$ 次元 trace を評価し、資料に保存されている historical 75-term audit table を **75/75 完全一致**で再生成します。

重要：この75係数表は、資料の後半で監査対象となった projector-first trace 順序、

$$
\operatorname{Tr}\left[(\rlap{/}p'+m)O_\mu(\rlap{/}p+m)\Gamma_{\mathrm L}^{\mu}\right]
$$

に対応します。監査後の正しい spin-sum trace 順序、

$$
\operatorname{Tr}\left[(\rlap{/}p'+m)\Gamma_{\mathrm L}^{\mu}(\rlap{/}p+m)O_\mu\right]
$$

は別ルートとして保持し、historical 75 CSV と混同しません。現在の実装では corrected spin-sum route は72 monomialを生成します。

出力：

```text
output\ladder_general_q_raw_trace_trial.md
output\ladder_general_q_75_coefficients_generated.csv
output\ladder_general_q_corrected_spin_sum_generated.csv
```


## v0.27.0: IBP / finite Laporta core

`run_ibp_demo.bat` を追加しました。一般の多ループ denominator family に対して

$$
0=\int d^{LD}k\,
rac{\partial}{\partial k_i^\mu}\left(v^\mu\prod_a D_a^{-n_a}
ight)
$$

から疎な IBP 方程式を自動生成します。ordinary ladder の7分母 family では bare seed $J(1,1,0,1,1,1,1)$ から $\partial_k,\partial_l$ と $k,l,p,p'$ の組合せによる8本のIBPを生成できます。

有限式集合に対する symbolic Laporta 消去器も追加しました。1ループ tadpole では $J(2)$ を $J(1)$ へ自動reduceし、ordinary ladder の bare-seed 8式でも8個のpivotを消去できます。第1近傍seed生成では8 seed、64 IBP、181 distinct integral まで自動生成します。完全な7分母 master reduction には、sector ordering、zero-sector detection、seed closure、より高速な係数簡約が次に必要です。


## v0.29.0: family symmetry と generic-rank probe

ordinary ladder の4元 symmetry group を使って積分指数を canonicalize できます。degree-2 domain は 36 seed から24代表へ、IBP に現れる distinct integral は623から335へ減少します。係数だけを exact rational point に specialize する generic-rank probe では、degree-2 system から162 pivotを高速に確認できます。これは任意運動学の symbolic reduction の代替ではなく、rank/closure診断です。


## 追加: exact rational reconstruction (v0.31.0)

Generic exact-rational probe で得た Laporta reduction の係数から、$D,z$ の有理関数を復元する機能を追加した。浮動小数点は使用せず、training に使っていない holdout 点で完全一致した場合だけ採用する。ordinary ladder corrected route の代表例として、$J(-1,0,0,1,1,1,1)$ と $J(0,0,1,1,0,1,1)$ の係数を再構成できる。現段階では全 target の完全再構成ではなく、adaptive degree / pole avoidance / finite-field acceleration が次の課題である。

## 追加: corrected 40 target 全体の再構成監査 (v0.32.0)

`run_full_target_reconstruction_demo.bat` は、corrected ordinary-ladder projector から得た 40 個の symmetry-canonical target 全体に対して exact-rational Laporta reduction と $D,z$ 有理関数再構成を適用します。

重要な変更点は、target が Laporta の pivot になっただけでは「master 候補まで reduce できた」と判定しないことです。`reduce_integral()` を最後まで適用し、6 個の stable candidate 以外の積分が 1 個でも残れば、その target の係数補間を禁止します。

現時点の corrected route では、40 target の内訳は次のとおりです。

- stable candidate basis 自身: 6
- 6 candidate のみへ閉じ、holdout 検証付きで係数再構成成功: 6
- non-candidate residue が残るため再構成を保留: 28
- basis には閉じたが degree bound 内で再構成失敗: 0

この結果から、次のボトルネックは rational interpolation の次数ではなく、terminal residue を追加 seed として扱う closure 側にあることが分かりました。全 residue の近傍を一括追加する方法は系を急激に膨張させるため、次版では sector と residue priority に基づく段階的 closure scheduler を導入します。


## v0.34.0 residue-aware closure scheduler

corrected ordinary-ladder の terminal residue を target 影響度と sector 単位で順位付けし、一括近傍展開を避けて bounded seed を追加する scheduler を追加しました。baseline 84 seed から terminal residue 自身30個を段階追加すると、114 seed / 906 IBP / 823 pivot となり、residue-bearing target は 28 から 27 へ減少します。実行例は `run_residue_scheduler_demo.bat` です。

## v0.34.0: incremental phase-2 residue scheduling

114-seed phase-1 系を毎回全消去し直さず、追加seed自身のIBPだけを既存823 pivotでreduceして新pivotを追加する incremental Laporta extension を導入しました。sector 96/80 の22 neighborhood seedを安全にスクリーニングし、terminal residueへ直接効く7 seedから2 seedを選択します。`run_phase2_scheduler_demo.bat` で確認できます。


## v0.35.0: phase-3 factorized lower subtopologies

v0.34.0 で選択した2 seedを実際に phase-1 rule へ追加すると、pivot は 823 から 837 へ増えるものの、recursive reduction 後の residue-bearing target は 27 のままでした。これは高次数 residue が消えるのではなく、より低次数の lower-sector integral へ descent するためです。

新しい `factorized_one_denominator_per_loop()` は、各 active denominator の loop-space quadratic form を解析し、L-loop sector が L 本の独立な rank-one denominator へ分離できるかを判定します。ordinary ladder では terminal residue 3個を one-loop massive tadpole の積として認識でき、これらを genuine two-loop master 候補から除外すると residue-bearing target は **27 -> 18** へ減少します。`is_scaleless_zero_sector_extended()` は、正の分母で拘束されない自由 loop direction を持つ sector も scaleless zero と判定します。実行例は `run_phase3_factorized_demo.bat` です。


### v0.37.0: directional depth-2 master-candidate audit

ordinary ladder で残った3つの provisional local master candidate に対し、first-neighborhood より一段広い directional depth-2 seed を試験できるようになりました。

`directional_depth2_seeds()` は各積分指数を同じ方向へ2段動かした小さな監査用 seed domain を生成し、`diagnose_directional_depth2_irreducibility()` は既存の triangular Laporta rule を再利用して residue 自身が新しい pivot になるかを調べます。

3候補はいずれも3つの独立 exact-rational probe で pivoting seed が0でした。これは global master proof ではないため、QEDCalc は引き続き **depth-2-stable provisional master candidates** として扱います。

実行例: `run_phase5_depth2_master_demo.bat`

### v0.39.0: full degree-2 Cartesian 監査

ordinary ladder の残る3候補について、first-neighbor、directional depth-2 に加えて mixed two-direction degree-2 seed を全て監査する。primary exact-rational probe では3候補とも full bounded degree-2 domain で pivot 0。837-pivot rule set は portable JSON checkpoint として保存し、監査を高速に再実行できる。

実行: `run_phase6_full_degree2_master_demo.bat`


## v0.39.0: 3-probe full degree-2 audit

ordinary ladderの3 provisional master candidatesは、3つの独立exact-rational probeすべてでcomplete bounded degree-2 Cartesian neighborhood全体にわたり非pivotでした。3つのbaselineはいずれも837 pivotsです。incremental Laportaはpersistent reduction cacheを共有するよう高速化されています。これはglobal master proofではなくbounded auditです。


## v0.40.0: 3-probe full bounded degree-3 audit

ordinary ladder の3つの provisional master candidate に対し、既に監査済みの degree <= 2 seed を除いた bounded degree-3 shell を生成し、symmetry canonicalization 後に sector batch 単位で incremental Laporta へ追加する。

新しい API は `degree3_shell_seeds()` と `diagnose_full_degree3_irreducibility()`。3つの独立 exact-rational probe すべてで基準 Laporta 系は 837 pivots で一致し、degree-3 shell は candidate 1/2/3 について 72/84/84 seeds だった。全9 probe/candidate 組合せで candidate 自身は新pivotにならなかった。

したがって3候補は full bounded degree-3 domain まで安定した provisional master candidates として扱える。ただしこれは global master-count proof ではない。


## v0.41.0: ordinary ladder の完全 symbolic coefficient table

corrected spin-sum route の 40 canonical target は、現在 12 terminal basis integral へ完全に閉じています。

全 $40\times12=480$ 成分のうち、非零係数は151個です。各非零係数 $c_{ia}(D,z)$ は exact rational function として再構成し、91個のCartesian-grid点と、gridに含まれない3つの独立 exact-rational probe の合計94点でexact一致を確認しています。

完全表は `data\ladder_corrected_40target_12basis_symbolic_reduction.csv`、非零成分だけの表は `output\ladder_corrected_40target_symbolic_nonzero.csv` です。

実行確認は `run_phase9_full_symbolic_reduction_demo.bat` を使用してください。


## v0.42.0: ordinary ladder 12 basis の評価層

v0.41.0 で得た40 canonical target -> 12 terminal basis の次段階として、v0.42.0 は basis integral 自身の評価層を追加します。`classify_ordinary_ladder_terminal_basis()` は12積分を分類し、全12積分について7分母定義から projective Feynman-parameter polynomial $U$, $F$, $\Delta=F/U$ を自動生成します。

generic $z$ では basis 0, 1, 3 が factorized lower sector です。さらに magnetic form factor に必要な $z=0$ では $E_1=E_4$, $E_2=E_3$ の退化を利用でき、basis 2, 4 も tadpole product へ落ちます。basis 5, 6 は one-massless/two-equal-mass vacuum sunset、basis 7, 9 は massless bubble を先に積分した generalized on-shell one-loop integral として Gamma 関数だけで評価できます。

したがって $z=0$ では **9/12 basis が exact analytic** となり、残る genuine two-loop master は **basis 8, 10, 11 の3個**です。式は convention-free Euclidean scalar integral として保持し、Minkowski の $i$、Wick rotation 符号、$(2\pi)^D$、renormalization scale は convention layer 側で付与します。

実行: `run_phase10_basis_evaluation_demo.bat`


## v0.43.0: ordinary ladder $z=0$ basis の完全解析評価

v0.42.0 で未解決だった basis 8, 10, 11 は、$z=0$ では独立な3 masterではありません。$E_1=E_4$, $E_3=E_2$ を最初から用いる reduced family $(K,L,H,E_2,E_4)$ を構成すると、

$$
T_n=
\int\frac{d^Dk\,d^Dl}{L\,H\,E_2\,E_4^n},
\qquad n=1,2,3
$$

となります。degree-1 の symbolic IBP だけで $T_2,T_3$ は $T_1$ と lower sectors へ reduce できます。lower sectors は scaleless で0、または massless two-point subloop + generalized on-shell one-loop integral として Gamma 関数で評価できます。

残る $T_1$ は Cheng--Wu gauge $x_{E_2}+x_{E_4}=1$ を用いると1変数 hypergeometric integral まで落ち、Euler--Beta 積分後の ${}_3F_2(1)$ は上下パラメータの相殺により ${}_2F_1(1)$ となります。Gauss summation により $T_1$ も Gamma 関数だけで閉じます。

したがって ordinary ladder の terminal basis は、

$$
\boxed{12/12\ \text{exact at } z=0}
$$

となりました。再生成デモは `run_phase11_complete_basis_demo.bat` です。


## v0.44.0: ordinary ladder projector/reduction 合成

補正済み72項を対称性で40 targetへまとめ、40 x 12 の厳密な symbolic IBP reduction と合成する層を追加しました。`z -> 0` で `1/z^2` は残らず、12基底の厳密な `z=0` 値を使うと全 `1/z` 係数も厳密に0になります。有限部には basis 0, 1, 3, 5, 6, 7, 8 の一次 `z` 微分だけが追加で必要です。


## v0.45.0: crossed ladder raw bridge / symmetry IBP

- crossed raw projector: 95 scalar-integral monomial
- graph reversal symmetry で 95 target -> 52 canonical target
- exact probe で 416 IBP rows / 378 pivots / 40 target pivot
- 残る12 target は first-neighbor、directional depth-2、mixed degree-2 のいずれでも P1 では non-pivot
- 3 independent probes で baseline の残る12 target は完全一致
- raw six-denominator scalar core から Symanzik U/F を自動生成（degree 2 / 3）

残る主要課題は projected numerator から詳細導出資料の projective kernel への自動接続です。

## v0.46.0：crossed ladder の q 一次 magnetic-projector bridge

raw crossed numerator に `p'=p+q` を代入して q 一次まで展開する経路を追加した。完全展開後は q^0 が144 chain、q^1 が84 chainとなり、詳細導出の `144+48+36=228` と一致する。

q=0 では中央2本の electron denominator が一致するため、`K,L,Dk,Dkl,Dl`、powers `(1,1,1,2,1)` の5分母 family を構成する。一般 Symanzik 生成器から、手計算で導入した `Delta`、`W` と measure factor `y` を独立に再生成する。

Breit frame の明示 4x4 Dirac 行列と on-shell spinor による magnetic projector の規格化検証も追加した。F1 係数は厳密に0、F2係数は厳密に1となる。denominator の q 一次補正 `2*x*k.q + y*(k+l).q` も独立オブジェクトとして生成する。

実行：`run_phase20_crossed_qlinear_bridge_demo.bat`


## v0.55.0 progress note

Self-energy insertion is now closed from the raw two diagrams through on-shell renormalization to the final analytic result. Corner (IIc) now has a raw two-diagram parser/topology bridge, q=0 five-parameter denominator family, split-parameter q derivatives, and explicit q-linear magnetic projector generation. The next corner stage is the Gaussian/subtraction bridge to the existing UV-finite parameter representation.


## v0.56.0 progress note

corner (IIc) の raw 2図について、v0.55 で生成した q-linear magnetic projector 多項式を streaming 方式で平方完成・tensor reduction・2-loop Gaussian integral へ流し、bare five-simplex kernel `G4`, `G5` まで自動生成できるようになりました。第4図・第5図の UV chart では両方とも residue が one-loop magnetic density の `1/2` に factorize し、local `B gamma_rho` subtraction を引いた residue は exact に0になります。

この local subtraction は UV boundary の監査用です。物理的 finite normalization の最終表現としては使用せず、次段では renormalized inner vertex remainder の `K`, `m^2/kappa^2`, `z` sector を生成し、outer magnetic projector へ直接挿入します。


## v0.57.0 progress note

The physical on-shell-renormalized corner inner vertex is now represented as three explicit sectors rather than being conflated with the five-simplex local UV diagnostic subtraction. The corrected decomposition keeps the K_nu/Lambda_prime^2 sector, analytically closes the z-sector to log(Lambda_prime^2/Lambda0^2), and rewrites the kappa^2 sector as a simple denominator difference 1/Lambda0^2-1/Lambda_prime^2. Phase 36 checks both identities exactly and verifies that the explicitly subtracted gamma_nu sectors vanish at Lambda_prime^2=Lambda0^2.

### v0.62 corner status

Phase 43 now audits the UV-divergent inner radial gamma channel in `D=4-2 epsilon` instead of assuming four-dimensional Dirac algebra before the pole is expanded.  It exposes an exact evanescent finite local term that must be propagated through the physical on-shell subtraction before the corner finite normalization can be trusted.

### v0.63 corner progress

Phase 44 propagates the D-dimensional phase-43 evanescent local term through the on-shell charge subtraction and the generated outer Breit projector. The local `-3/2 gamma_nu` term cancels exactly between the bare inner vertex and `B gamma_nu`; no physical corner finite shift remains from this local term.

### v0.64 corner Phase 45

Phase 45 separates the remaining corner discrepancy into inner-operator and outer-convention parts. The raw-generated physical inner remainder is reconstructed exactly in the three-sector form by defining `K_nu^gen = C_nu/2 - 2 f(u) gamma_nu`; all four operator residuals vanish. An independent local `gamma_nu` insertion then calibrates the outer projector against the one-loop Schwinger kernel. The raw projector/Gaussian kernel has exact ratio `-4`; after the already documented Eq.(42) factor `1/4` the residual ratio is `-1`. This sign is recorded as a diagnostic and is not patched by hand.


## v0.66.0 / v0.67.0 corner 更新

v0.66.0 では、有限 photon mass を保持した log sector の denominator cancellation を再監査した。outer photon scalar denominator を $P=\rho^2-k^2$、outer electron scalar denominator を $E=-D(k)$ とすると、

$$
\frac{A_K k^2+A_DD}{P E^2L_z}=-\frac{A_K}{E^2L_z}-\frac{A_D}{P E L_z}+\frac{A_K\rho^2}{P E^2L_z}
$$

である。以前の実装では最初の2 family の符号が逆で、最後の photon-mass residual family が欠落していた。v0.66.0 はこの恒等式を exact residual 0 で検証してから修正している。

v0.67.0 の Phase 49 は、保存済み final formula を入力するのではなく、独立に保存されていた on-shell $K_\nu$ operator を current 4x4 gamma 規約へ転記し、full outer magnetic projector を再実行する。使用する operator decomposition は、

$$
K_\nu=K_\nu^{\mathrm{pres}}+(1-u)(1-uv)D(k)\gamma_\nu+2k^2\left[1-u+u^2v(1-v)\right]\gamma_\nu
$$

である。`corner_historical_K_projector_audit()` は、outer electron denominator の $q$ 微分まで含めて、

$$
\boxed{
P_K=D(k)Q_K+R_{\mathrm{odd}}
}
$$

を再生成する。さらに、

$$
\boxed{
R_{\mathrm{odd}}=k_1k_2\,\mathcal R(k_0,k_1^2,k_2^2,k_3^2;u,v)
}
$$

を exact に因数分解するため、平方完成後の対称積分では $R_{\mathrm{odd}}$ が消えることをコード側だけで再確認できる。

Phase 49 の term count は、`base/transverse/Q_K/remainder = 21/14/21/4`。`P_K-DQ_K-R_odd` は exact に0である。実行は `run_phase49_corner_historical_K_projector_audit.bat`。

重要：この historical $Q_K$ は、v0.61 以降の raw $C_\nu$ から作った `lp_quotient` と同一オブジェクトとして扱わない。現在の corner finite-part discrepancy の本命は、raw $C_\nu$ representation と独立 $K_\nu$ representation の operator/family correspondence に残っている。v0.67.0 はこの境界を明示しており、最終有限定数を hand-fit していない。


## v0.68.0 corner Phase 50 / 51

Phase 49 の historical $K_\nu$ bridge は、

$$
P_K=D(k)Q_K+R_{\mathrm{odd}}
$$

という保存済み構造を再生成するための structural audit であった。しかし、この条件だけでは Karplus--Kroll から current notation への explicit $i$、$\sigma_{\mu\nu}$、$\overline{\Lambda}$ の符号変換を一意に固定できない。

Phase 50 では historical $K_\nu$ を7個の tensor basis に分け、raw $C_\nu$ から独立生成される current magnetic projector と一致する係数を線形方程式として解いた。canonical representative は、

$$
\boxed{
(-1,\ 1,\ 0,\ -1,\ i,\ 1,\ -\tfrac12)
}
$$

である。第3 basis は magnetic projector に対して exact に null なので係数0を選ぶ。解決後は、

$$
\boxed{K_\nu^{\mathrm{current}}=\frac12 C_\nu-2f(u)\gamma_\nu}
$$

に対応する base、transverse、common numerator がすべて exact residual 0 で一致する。したがって v0.61 以降の $+C_\nu/(2\Lambda'^2)$ rational sign は、この convention-resolved $K_\nu$ と矛盾しない。

Phase 51 では、current rational remainder を historical な $K+\kappa^2$ 分解へ戻し、

$$
\frac{C_\nu}{2\Lambda'^2}-\frac{2f\gamma_\nu}{\Lambda_0^2}=\frac{K_\nu^{\mathrm{current}}}{\Lambda'^2}+2f\gamma_\nu\left(\frac1{\Lambda'^2}-\frac1{\Lambda_0^2}\right).
$$

を operator、common quotient、odd remainder、Gaussian template の各段階で exact に確認した。よって remaining corner finite-part discrepancy の原因は rational LP/$K$ sector ではない。

次の主対象は log sector である。v0.66 の denominator cancellation を、分解後の family からではなく元の

$$
\gamma_\nu\ln\frac{\Lambda'^2}{\Lambda_0^2}
$$

から直接再生成し、その後 soft-region importance sampling を用いた finite-$\rho$ QMC を再実行する。


## v0.70.0 corner Phase 52: log sector の unsplit 直接再構成

Phase 51 までに rational $K+\kappa^2$ sector と current $LP+B_\gamma$ route の exact 同値性を確認したため、Phase 52 では残る log sector を分割前の式から直接再生成する。

出発点は、

$$
\ln\frac{\Lambda'^2}{\Lambda_0^2}=(\Lambda'^2-\Lambda_0^2)\int_0^1\frac{dz}{\Lambda_0^2+z(\Lambda'^2-\Lambda_0^2)}
$$

であり、

$$
\Lambda'^2-\Lambda_0^2=u^2v(1-v)k^2+uv(1-u)D(k)
$$

を denominator cancellation 前のまま保持する。実装では $P E^2L_z$ の4-factor familyを直接 Feynman parameter 化し、$n=4$ Gaussian masterへ渡す。

`corner_log_unsplit_audit()` は、

- direct unsplit Gaussian template
- direct finite-$\rho$ parameter kernel
- $\Lambda'^2-\Lambda_0^2$ の $k^2$ / $D(k)$ 係数
- v0.66 の3-family splitへ分解する前の exact scalar identity
- Gaussian pole audit

を返す。

Phase 52 では direct template に $\Gamma(0)$ pole が存在せず、scalar split residual も exact に0となる。uniform scrambled Sobolによる補助的な数値比較でも、$\rho=0.05$ の log-sector direct integral と3-family split integralは同じ約 $0.32$ へ収束する。ただし soft endpoint の分散が残るため、このQMC値自体は回帰判定には使用しない。

次段階は direct/split の両方へ同じ soft importance map を適用し、log sector の数値一致を統計誤差内まで縮めた後、corner全体の有限部を再評価することである。


## v0.70.0 corner Phase 53 / 54

Phase 53 では soft regionを重点化しながら全積分領域を覆う projective importance mapを追加した。$u$ 方向は

$$
u=\rho\left[\exp(Lt)-1\right],\qquad L=\ln\frac{1+\rho}{\rho}
$$

とし、outer simplexは

$$
r=\frac{ux}{1-x},\qquad s=\frac{uy}{1-y}
$$

$$
a_d=\frac{r}{1+r+s},\qquad a_p=\frac{s}{1+r+s},\qquad a_l=\frac{1}{1+r+s}
$$

で写す。endpointとsimplex sum、Jacobianは exact に監査する。

巨大展開済みkernelをsoft endpointで直接評価すると桁落ちが起きるため、数値評価では compact Gaussian templateをその場で $H,B,Q$ へ代入する。この経路を使うと、$\rho=0.1,0.05,0.02$ で direct unsplit log route と3-family split routeの差は scrambled-Sobolの推定誤差内へ入る。したがって log-sector splitは数値的にも独立routeと整合する。

Phase 54 では1-loop vertex subtraction coefficient $B$ の finite normalizationを $D=4-2\epsilon$ radial masterから独立生成する。有限 integrandは

$$
u\left[-\ln L-\frac12-\frac{2f(u)}{L}\right],\qquad L=u^2+\rho^2(1-u)
$$

となる。small-$\rho$ 展開から、

$$
B_{\rm fin}(\rho)=2\ln\rho+\frac{11}{4}+o(1)
$$

を得る。$A^{(1)}(0)=1/2$ を用いると、countertermのlocal finite constantは

$$
A_{\rm CT,fin}\supset-\frac{11}{8}
$$

である。

この $-11/8$ は最終 corner値から合わせた補正ではなく、1-loop subtractionから独立に生成した監査基準である。現時点ではこれを current corner kernelへ後付けしない。次の課題は current Eq. (32) routeがこのlocal finite normalizationを既に含むかどうかを operator/normalization levelで判定することである。


### v0.70.0 corner update

Phase 55 tracks the complete local finite $B\gamma_\nu$ normalization through the on-shell subtraction. The logarithmic, radial $-1/2$, and rational local pieces cancel independently, so the $-11/8$ counterterm constant is not an extra contribution to append to the renormalized Eq. (32) remainder.

Phase 56 rederives the sequential normalization directly from the current Feynman-rule factors. One side gives $\alpha^2/(8\pi^4)$ and the mirror pair gives $\alpha^2/(4\pi^4)$; after the common outer-loop $\pi^2$ this is exactly $\frac14(\alpha/\pi)^2$. The API also records that every physical parameter kernel requires an external $u\,du$ measure.

The remaining corner task is now the non-uniform soft-region overlap and a controlled full-corner QMC convergence audit.

## v0.71.0 corner Phase 57 / 58: large-$r$ soft overlap

Phase 57 reproduces the non-uniform $a_d=ur$ corner found in the independent derivation.  With

$$
D_r = a_l^2v^2-a_l^2+2a_lrv+a_l+r^2
$$

the generated $K$ and $\kappa^2$ soft kernels satisfy

$$
\boxed{\lim_{r\to\infty} r\left(\mathcal K_K+\mathcal K_{\kappa^2}\right) = \frac{8v}{(1-a_l)^2}}
$$

exactly.  Therefore the $a_d=ur$ sector contains a genuine $1/r$ overlap and the limits $\rho\to0$ and the parameter boundary are non-uniform.

For numerical add-subtract stabilization, QEDCalc also provides the smooth profile

$$
\mathcal O(r) = \frac{8v}{(1-a_l)^2}\frac{r}{1+r^2}.
$$

The difference $\mathcal K_K+\mathcal K_{\kappa^2}-\mathcal O$ has zero $1/r$ coefficient.  The finite part of this profile is not a physical correction by itself; subtraction and analytic add-back must use the same domain.

Phase 58 attaches the overlap to the actual simplex boundary.  Since $a_p=1-a_l-a_d\ge0$ and $a_d=ur$,

$$
\boxed{R_{\max} = \frac{1-a_l}{u}}
$$

is the exact upper endpoint.  The smooth overlap integral then carries

$$
\boxed{\lim_{u\to0} \left[-u\frac{d}{du}I_{\rm ov}\right] = \frac{8v}{(1-a_l)^2}}
$$

so the large-$r$ tail owns an explicit $\ln(1/u)$ contribution.  The next step is to apply this add-subtract pair to the compact finite-$\rho$ full-corner kernel with identical cutoff ownership and test QMC convergence.

### v0.72.0 corner update

Phase 59 places the large-$r$ overlap subtraction and analytic add-back on the identical physical simplex cutoff.  The recombination is exact and the subtracted joint soft kernel has no $1/r$ tail.

Phase 60 analytically normalizes the measure-included joint soft density.  The spatial soft density integrates to one, which fixes that the universal IR logarithm belongs to the combined soft density rather than to LP, $B_\gamma$, or a log family separately.  The next implementation step is therefore to construct the finite-$\rho$ **joint** compact density before applying the Phase-59 subtraction.


### v0.73.0 corner update

Phase 61 では、Phase 60 の measure 込み joint soft density を実際の有限 simplex、

$$
R+S\leq \frac{1}{\rho U}
$$

上で解析積分した。$R=qx$, $S=q(1-x)$ とすると有限 triangle の規格化 $N(T,v)$ は閉形式で得られ、

$$
N(0,v)=0,
\qquad
N(\infty,v)=1
$$

を満たす。tail は、

$$
1-N(T,v)=\frac{2v\ln T+v(1-2\ln v)}{T}+o(T^{-1})
$$

である。$T=1/(\rho U)$ を戻すと有限-domain correction は $O(\rho\ln(1/\rho))$ で消える。したがって primary soft triangle の有限 cutoff は order-one の corner finite mismatch の原因にはならない。

Phase 62 では Karplus--Kroll printed Eq. (28) と raw shift-consistent routing の ownership を監査した。QEDCalc の raw shift は、

$$
p'-k\longrightarrow(1-uv)p'-u(1-v)p''-k
$$

を生成する。一方 printed expression の $p''$ coefficient は $-v(1-u)$ であり、shift-consistent minus printed の差は、

$$
\boxed{v-u}
$$

である。stored hard-primary checkpoint は printed 側、`corner_shift_correction_result()` は shift-consistent hard result へ移すための correction である。finite-$\rho$ raw kernel は既に shift-consistent なので、この correction を再度加えてはならない。


## v0.74.0: Phase 63 pure finite-rho matching ownership

Phase 63 separates the analytic matching condition from archived numerical checkpoints.
The shift-consistent hard sector and the analytic z sector already satisfy

$$
M_{\mathrm{match}}^{\mathrm{analytic}} = A_{\mathrm C,fin}-H_{K\kappa}^{\mathrm{shift}}-A_z =0.
$$

Therefore no additional finite matching constant may be appended to the corner result.
`corner_pure_matching_audit()` stores the old corrected finite-rho QMC numbers only as regression checkpoints; they are not inputs to any symbolic kernel or analytic coefficient.
For the smallest archived point,

$$
\rho=0.002,
\qquad
M_{\mathrm{match}}(\rho)=-0.0034390586\ldots,
$$

with the archived uncertainty $0.00638$, so the checkpoint is statistically compatible with the exact zero-matching condition.
The next implementation target is to regenerate the independent corrected finite-parameter reference kernels $I_K$, $I_{\kappa^2}$ and $I_z$ and compare them pointwise with the current raw-generated physical kernels.



## v0.75.0: Phase 64 reproducible finite-rho corner evaluator

Phase 64 turns the current SymPy-generated corner parameter kernels into a reproducible optional numerical diagnostic. The evaluator owns the physical measure, parameter domains, soft-importance Jacobians, and the Eq. (42) normalization in one place.

The generated kernels do not contain the outer factor or the inner parameter measure. The evaluator therefore applies

$$
\mathcal N_{\mathrm C}=\frac14
$$

and

$$
d\mu_u=u\,du
$$

exactly once.

The family domains are different and are kept explicit: LP and the two full log families use a two-simplex; $B_\gamma$ and the photon-cancel log family use a one-simplex. The local $B_\gamma$ sector is independent of $v$, so its omitted $v$ integration equals one rather than an additional numerical dimension.

`corner_finite_rho_qmc()` uses only the current generated kernels. Archived corrected QMC values are not inputs to the integrand. At $\rho=0.05$, a small diagnostic run reproduces the known current-route mismatch rather than hiding it, which makes the discrepancy a package-level reproducible regression target.

The active corner question is now narrower: the largest discrepancy sits in the rational remainder. The raw inner-radial bridge and the physical on-shell bridge display opposite signs for the nonlocal $C_\nu/(2\Lambda'^2)$ term. Phase 50 compared against a current-route target and therefore does not by itself provide a non-circular proof of that sign. The next audit must fix the raw-radial to physical-remainder sign using the complete Feynman prefactor/Wick convention, not by fitting the final corner constant.

### Two-loop seven-diagram status

| sector | diagrams | SymPy status |
| --- | ---: | --- |
| corner pair | 2 | raw diagrams through renormalized parameter kernels complete; final finite-rho reconciliation still open |
| self-energy insertions | 2 | raw-to-final analytic result complete |
| vacuum polarization | 1 | raw-to-final analytic result complete |
| ordinary ladder | 1 | raw-to-final analytic result complete |
| crossed ladder | 1 | raw-to-final analytic result complete |

Thus five of the seven diagrams are closed raw-to-final. The remaining two are the corner pair, where the symbolic derivation is deep into the final parameter representation and the unresolved issue is a finite normalization/sign ownership inside the rational remainder rather than missing raw-diagram machinery.


## v0.76.0：corner rational sector の符号決着と secondary-overlap QMC

Phase 65 では raw inner-loop radial master の relative sign を独立に固定した。QEDCalc の raw inner chain convention では、

$$
\frac{1}{i\pi^2}\int\frac{d^4r}{(r^2-L+i0)^3}=-\frac{1}{2L}
$$

であるため、raw radial bridge は $+\gamma_\nu\log(\Lambda'^2/\Lambda_0^2)$ と $-C_\nu/(2\Lambda'^2)$ を生成する。

Phase 66 では physical on-shell remainder の $C_\nu$ 符号を charge condition から独立に確定した。$k=0$ では、

$$
\frac{C_0(0)}{2\Lambda_0^2}=\frac{2f(u)}{\Lambda_0^2}\gamma_0
$$

であり、on-shell $B\gamma_0$ subtraction は $-2f(u)\gamma_0/\Lambda_0^2$ である。したがって physical remainder は $+C_\nu/(2\Lambda'^2)$ でのみ時間成分が exact に0になる。raw radial の $-C/2$ を physical kernelへ直接コピーしてはならない。

Phase 67 では $B_\gamma$ line family をLPの2-simplexへ exact に埋め込み、$a_d=ur$ の secondary overlap を logarithmic $r$ sampling で評価した。measure identity と Jacobian は exact residual 0 である。しかし、この overlap-aware QMCでも rational finite remainder は corrected hard valueへ移動しなかった。したがって現在の order-one mismatch は numerical tail sampling ではなく、generated rational kernel の algebraic assembly に残っている。

次の監査対象は、Phase 49 の historical full-$K_\nu$ projector から得た $Q_K$ と current `lp_quotient` の多項式差である。


## v0.77.0：corner historical K sector の denominator-cancellation 監査

Phase 68 は historical $K_\nu$ を $K_\nu^{\mathrm{pres}}$、explicit $D(k)\gamma_\nu$、explicit $k^2\gamma_\nu$ の3 sectorへ分離し、それぞれを full magnetic projectorへ独立に通す。SymPy の exact polynomial division により、$D(k)\gamma_\nu$ sector の base / transverse は共に $D(k)$ を因子に持ち、$k^2\gamma_\nu$ sector の base / transverse は共に $k^2$ を因子に持つことを確認した。

したがって denominator cancellation を projector 後にも厳密に実行できる。Phase 69 では q-denominator derivativeまで含めて再結合し、3 sectorを次の familyへ落とした。

$$
\mathcal F_{\mathrm{pres}} \in (K^1D^2\Lambda'^1), \qquad n=4.
$$

$$
\mathcal F_D \in (K^1D^1\Lambda'^1), \qquad n=3.
$$

$$
\mathcal F_{k^2} \in (D^2\Lambda'^1), \qquad n=3.
$$

各familyの polynomial division remainder はすべて transverse odd であり、対称積分では消える。これにより current の一括 n=4 Gaussian route と historical cancellation-first route の中間表現の差が明示化された。次段では n=3 sectorを $D=4-2\epsilon$ で保持し、pole cancellation後の finite residualを監査する。


### Phase 70：convention-resolved cancellation-first rational kernels

Phase 50 の current convention を Phase 68--69 の sector decompositionへ適用し、$K_{\mathrm{pres}}$、$D$-cancel、$k^2$-cancel、$\kappa^2/\Lambda'$、$\kappa^2/\Lambda_0$ の5 kernelを独立にGaussian化した。すべて pole-free である。

小規模QMCでは $\rho=0.05$ において current all-in-one rational routeより有限部が大きく移動することを確認した。ただし $\rho$ をさらに小さくすると、5 sectorに対する現行generic soft mapでは分散が大きくなるため、その数値は物理判定には用いない。次段では cancellation-first sector専用のsoft / secondary-overlap mapを導入する。

## v0.78.0：cancellation-first 専用 secondary-overlap map

Phase 71 では Phase 70 の5つの rational sector に対して、generic soft map ではなく secondary overlap を直接解像する座標を導入した。

三角領域を持つ `preserving`、`D_cancel`、`kappa_Lp` は `a_l=y, a_d=u*r` とし、`r` を厳密な上限 `(1-y)/u` まで対数的にサンプリングする。1次元領域の `k2_cancel`、`kappa_L0` も `a_d=u*r` とし、上限 `1/u` まで同様に対数化する。Jacobian と境界は symbolic に residual 0 を確認しているため、積分領域や物理 measure は変更していない。

数値誤差は1本の Sobol net を独立標本とみなす近似ではなく、独立 scramble 間のばらつきから評価する。power 12、8 scramble の診断では `rational_minus_log` は rho=0.02, 0.01, 0.005, 0.002 に対してそれぞれ約 0.0881, 0.1614, 0.1907, 0.2063 となり、小さい rho でも有限に追跡できるようになった。

これは rational sector 単独の診断であり、既知の corner 最終定数を入力・fit してはいない。次段は、この安定化した cancellation-first rational route と独立生成済み log sector を同一規約で結合し、full corner finite constant を直接監査することである。

## v0.79.0：Phase 72 full stabilized corner audit

Phase 71 で安定化した cancellation-first rational route と、Phase 52 で split 前から独立生成していた direct log kernel を同一の `1/4` 規約で初めて結合した。direct log は Phase 53 の soft bijectionで積分し、独立 Sobol scramble 間のばらつきを誤差とする。

小さい $\rho$ でも direct log sector は約 0.082 に安定しており、rational route も Phase 71 map では有限に追跡できる。しかし両者を結合した有限部は約 +0.29 へ向かい、解析 checkpoint

$$
-\frac{67}{24}+\frac{\pi^2}{18}-\frac12\zeta(3)+\frac{\pi^2}{3}\ln2
$$

の数値値 $-0.5640209413\ldots$ とは一致しない。checkpoint は出力後の比較にのみ使い、kernel の補正・fit・正規化には使用していない。

したがって残課題は QMC の soft sampling ではなく、cancellation-first rational kernel と direct-log kernel の間に残る **sector / finite-term ownership** の監査である。次段では full finite discrepancy を sector 別に分解し、historical hard-primary / shift-correction / z-sector のどの generated intermediate と差が発生するかを点検する。

## v0.80.0：Phase 73 finite-rho cancellation / Wick ownership

Phase 72 の有限値不一致を、既知の最終定数で補正せずに分解するため、Minkowski 分母 cancellation と Wick/Gaussian 符号 ownership を分離して監査する。

`corner_phase73_finite_rho_cancellation_wick_audit()` は

- `D/E=-1` (`E=-D`)
- `-(1/2)k^2/P = 1/2-rho^2/(2P)` (`P=rho^2-k^2`)
- n=4 -> n=3 cancellation に伴う Minkowski scalar master の `(-1)^n` parity

を exact に固定する。これにより Phase 70 の leading D/k2 cancellation 符号は Wick parity 込みで正しいことが分かる。一方、有限 rho では k2 sector に `-rho^2/(2P)` residual が別に残る。ただしこれは rho^2 で消えるため、現在の O(1) finite mismatch の主因にはなり得ない。

実行：`run_phase73_corner_cancellation_wick_audit.bat`

## v0.81.0：Phase 74 finite-ρ residual の非一様極限

Phase 73 で分離した `-ρ^2/(2P)` は、固定された非零 `k^2` では `ρ→0` で消えます。しかし soft 領域 `k^2=ρ^2 χ` では O(1) のまま残ります。したがって積分前に「ρ^2 が付いているから無視できる」と判断することはできません。Phase 74 はこの極限の非可換性を exact に固定し、Phase 64 と Phase 71 の rational route を既知の最終値を使わず比較できる診断を追加します。

実行: `run_phase74_corner_k2_mass_nonuniform.bat`

## v0.82.0：Phase 75 retained-photon residual と cancellation 符号の訂正

Phase 74 で保持すべきことが分かった `rho^2/P` residual を、Phase 69 の `k2_cancel_quotient` から元の `P D^2 Lp` family 上に直接再構成した。さらに各 `D` / `k^2` sector を「cancel 前の n=4 Gaussian family」と「cancel 後の n=3 family」で単独比較した結果、Phase 73 で外付けした n=4→n=3 Wick-parity 比は Gaussian helper の denominator continuation と二重計上になっていたことが判明した。

したがって reduced sector の係数は `D_cancel=-1`, `k2_cancel=+1/2` であり、retained photon residual は n=4 のまま `-rho^2/(2P)` を保持する。修正後の cancellation-first rational route は Phase 64 の独立 `LP+B_gamma` route と有限 rho で数値誤差範囲内に閉じる。解析 corner 定数は符号決定には使用していない。

実行: `run_phase75_corner_retained_photon_route_closure.bat`

## v0.83.0：Phase 76 soft finite ownership の復元

Phase 72 では `rational - log(1/rho) + direct-log` の安定化極限を corner 全有限部と呼んでいましたが、これは ownership の誤りでした。この極限は leading soft logarithm とともに soft region を差し引いた **hard remainder** です。

独立に導出済みの soft finite constant

$$
C_{\rm soft}=\frac{\pi^2}{6}+\ln^2 2-3\ln2-\frac74
$$

を一度だけ戻すと、

$$
A_{\rm C,fin}=H_{\rm fin}+C_{\rm soft}
$$

となります。Phase 76 はこの恒等式を exact residual 0 で監査し、既知の最終値を数値 kernel の入力・fit・補正値として使用しません。

検証：`run_v083_validation.bat`

## v0.84.0：Phase 77 corner end-to-end closure checkpoint

Phase 76 で soft finite ownership が確定したため、Phase 77 は corner 図の解析結果を一つの end-to-end checkpoint に固定する。

独立に整理された2経路、

$$
A_{\mathrm C,fin}^{(\mathrm{sector})}
=H_{\mathrm{primary}}+\Delta H_{\mathrm{shift}}+Z
$$

と、

$$
A_{\mathrm C,fin}^{(\mathrm{match})}
=H_{\mathrm fin}+C_{\mathrm soft}
$$

を別々に組み立て、両者の差を exact residual 0 で監査する。さらに、

$$
A_{\mathrm C,fin}
=-\frac{67}{24}+\frac{\pi^2}{18}-\frac12\zeta(3)+\frac{\pi^2}{3}\ln2
$$

への residual も0である。

IR 部分についても corner の係数 $+1$ と self-energy insertion pair の係数 $-1$ を同じ checkpoint で監査し、合計 logarithm が exact に0になることを確認する。

`corner_phase77_numerical_checkpoint()` は Phase 76 の stabilized QMC を同じ解析 checkpoint に接続するが、解析値を kernel の入力、fit、規格化には使用しない。

検証：`run_v084_validation.bat`

高精度の有限 $\rho$ 走査：`run_phase77_corner_end_to_end_checkpoint.bat`

## v0.85.0：Phase 78 crossed ladder end-to-end closure

crossed ladder の現代的な独立導出経路を1個の checkpoint に統合した。Breit magnetic projector は F1 係数0、F2係数1を厳密に再確認する。raw から再生成した1変数 kernel と automatic Hermite/canonical reduction の差は厳密に0、endpoint cutoff logarithm の残差も0、half-sector と endpoint-sector を合成した最終解析結果は closed form と厳密一致する。

Karplus--Kroll 1950年の旧値との差 1/32 は、正しい crossed-ladder result の不確定性ではなく歴史的 provenance 監査として別管理する。Phase 78 はその差の発生箇所を推測して閉じたことにはしない。

実行：`run_phase78_crossed_end_to_end_checkpoint.bat`。検証：`run_v085_validation.bat`。

## v0.86.0: vacuum polarization end-to-end checkpoint

Phase 79 は vacuum polarization 図について、D次元 transversality、on-shell subtraction、有限 D->4 kernel、外側 magnetic insertion、z積分、primitive/endpoints、最終係数を1つの exact checkpoint にまとめます。

最終結果は

$$
A_{\mathrm{VP}}=\frac{119}{36}-\frac{\pi^2}{3}
$$

で、全 closure residual は 0 です。`run_v086_validation.bat` を実行してください。

## v0.88.0：Phase 81 ordinary ladder end-to-end closure

ordinary ladder の corrected spin-sum projector を 72 項から graph symmetry で 40 target にまとめ、既存の exact symbolic IBP reduction を通して 12 master basis へ接続する。leading magnetic-projector の $1/z$ pole は master の exact $z=0$ 値を入れた物理和で residual 0 になる。

12 master の解析評価から bare finite coefficient

$$
C_{\mathrm{bare}}=\frac{107}{48}+\frac{\pi^2}{18}
$$

を独立再構成し、one-loop on-shell subtraction

$$
Z_1^{(1)}F_2^{(1)}=-\frac{3}{4\delta}+2+O(\delta)
$$

を引くことで

$$
A_{\mathrm L}=\frac{11}{48}+\frac{\pi^2}{18}
$$

へ閉じる。最終係数は 72→40→12 の master reconstruction の入力には使わず、出力側 checkpoint としてのみ比較する。

実行：`run_phase81_ordinary_ladder_end_to_end_checkpoint.bat`。検証：`run_v088_validation.bat`。

## v0.89.0 / Phase 82 — 2ループ7図の統合 validation

`run_v089_validation.bat` は Python 標準ライブラリだけで、crossed ladder 1図、ordinary ladder 1図、corner 2図、self-energy insertion 2図、vacuum polarization 1図の合計7図を統合監査する。各寄与を `1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)` の基底係数として有理数のまま加算するため、最終係数と IR log 相殺は浮動小数点認識に依存しない。


## v0.90.0: 2ループ完成版 regression

`run_v090_validation.bat` は、2ループ7図全体の完成状態を1本のバッチで監査する。

必須監査は Python 標準ライブラリだけで実行し、次を確認する。

- crossed ladder 1図
- ordinary ladder 1図
- corner 2図
- self-energy insertion 2図
- vacuum polarization 1図
- 合計7図
- corner / self-energy の IR logarithm exact cancellation
- ordinary ladder の `72 -> 40 -> 12` reduction invariant
- 最終基底係数 `(197/144, 1/12, 3/4, -1/2, 0)`

したがって最終結果は

$$
A_1^{(4)}
=
\frac{197}{144}
+\frac{\pi^2}{12}
+\frac34\zeta(3)
-\frac{\pi^2}{2}\ln2
$$

である。

SymPy が利用可能な環境では、同じ validation batch が Phase 77–80 の解析 checkpoint も追加で再実行する。Karplus--Kroll 旧 crossed-ladder 値との差 `1/32` は、正しい現代値の不確定性ではなく、1950年の計算上の発生箇所が未特定の歴史的 provenance 課題として残す。
