# QEDCalc v0.51.0

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
