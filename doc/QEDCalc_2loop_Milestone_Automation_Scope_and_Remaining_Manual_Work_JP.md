# QEDCalc 2ループ到達点・自動化範囲・残る手動工程

## 0. この資料の目的

本資料は、QEDCalc v0.90.0 時点で電子異常磁気能率 $a_e$ の2ループ計算について、

- 何が実際に計算できるようになったか。
- どこまでを QEDCalc が自動処理できるか。
- どこに人間の物理的判断・入力式の導出が残っているか。
- 2ループ7図をどの程度再現可能な状態にできたか。
- 今後、自動化率を上げるには何を実装すべきか。

を、5種類のサンプル計算を横断して整理した総括資料である。

この資料は計算そのものの詳細導出を置き換えるものではない。個々の式の導出と QEDCalc の具体的な入出力については、次の5資料を参照する。

1. `01_crossed_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`
2. `02_ordinary_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`
3. `03_corner_2図_QEDCalcサンプル説明書兼計算過程説明書.md`
4. `04_self_energy_insertion_2図_QEDCalcサンプル説明書兼計算過程説明書.md`
5. `05_vacuum_polarization_QEDCalcサンプル説明書兼計算過程説明書.md`

---

## 1. 2ループ7図の構成

電子異常磁気能率の2ループ頂点補正は、本資料で採用した分類では次の7図から成る。

| 分類 | 図数 |
|---|---:|
| crossed ladder | 1 |
| ordinary ladder | 1 |
| corner | 2 |
| self-energy insertion | 2 |
| vacuum polarization | 1 |
| **合計** | **7** |

したがって、

$$
1+1+2+2+1=7
$$

である。

QEDCalc v0.90.0 では、この5種類・7図すべてについて release checkpoint が用意され、最終的に7図の和まで regression test できる状態になった。

---

## 2. 2ループ最終結果

電子異常磁気能率を

$$
a_e = \frac12 \left( \frac{\alpha}{\pi} \right) + A_1^{(4)} \left( \frac{\alpha}{\pi} \right)^2 + O(\alpha^3)
$$

と書く。

2ループ係数は、QEDCalc の7図統合 checkpoint により、

$$
\boxed{ A_1^{(4)} = \frac{197}{144} + \frac{\pi^2}{12} + \frac34\zeta(3) - \frac{\pi^2}{2}\ln2 }
$$

として再構成される。

QEDCalc v0.90.0 の統合 regression では、基底

$$
1, \quad \pi^2, \quad \zeta(3), \quad \pi^2\ln2, \quad \ln\frac1\rho
$$

に対する係数として、

$$
\boxed{ \left( \frac{197}{144}, \frac1{12}, \frac34, -\frac12, 0 \right) }
$$

を exact に得る。

最後の $0$ は、corner と self-energy insertion の赤外対数が完全に相殺していることを表す。

---

## 3. 「半自動処理」とは何を意味するか

QEDCalc は、現時点では Feynman 図の画像を与えれば自動的に最終 $a_e$ を返すプログラムではない。

一方で、従来は人間が大量に実行していた Dirac 代数、trace、projector、Feynman parameter 化、tensor reduction、IBP reduction、sector の恒等式確認、renormalization residual の検算などを、かなり広い範囲で機械処理できる。

したがって v0.90.0 時点の2ループ計算は、次の意味で「半自動」である。

$$
\boxed{ \text{人間が物理的な処理順序と正しい入力式を決める} \longrightarrow \text{QEDCalc が長大な代数処理を実行する} \longrightarrow \text{人間が物理的意味を確認して次段へ接続する} }
$$

この役割分担が現在の基本設計である。

---

## 4. 自動化レベルの分類

本資料では、各工程を次の4段階に分類する。

### レベル H：人が決める

物理的判断を必要とする工程である。

例：

- Feynman 図から非可換な gamma 行列・伝播関数の順序を決める。
- loop momentum routing を決める。
- どの subgraph が UV subdivergence を持つか判断する。
- どの renormalization condition を適用するか決める。
- IR regulator をどこまで残すか判断する。
- 解析しやすい変数変換・sector 分割を選ぶ。

この工程は、現在は QEDCalc に勝手に推測させない。

### レベル A：QEDCalc が自動処理

入力式と処理指示が正しく与えられれば、QEDCalc が代数処理を実行する工程である。

例：

- LaTeX の parse。
- propagator/subdiagram の検出。
- Dirac trace。
- gamma contraction。
- magnetic projector。
- loop shift。
- odd integrand の除去。
- tensor reduction。
- Feynman parameter family の生成。
- IBP reduction data の再構成。
- exact symbolic residual の検査。

### レベル C：人が接続する

前段の QEDCalc 出力を次段の専用計算へ渡す工程である。

数学そのものを手計算する必要は少ないが、

$$
\text{「この出力を次に何として使うか」}
$$

は人が理解して指定する。

### レベル R：release regression まで自動

一度確立した計算について、保存した invariant と解析値を再検証する工程である。

v0.90.0 では2ループ全体について、

- diagram count = 7
- IR log residual = 0
- ordinary ladder reduction = `72 -> 40 -> 12`
- 7図の exact basis sum

まで標準ライブラリだけで regression test できる。

---

## 5. 5種類の図に対する現在の自動化状況

### 5.1 crossed ladder 1図

計算の大きな流れは、

$$
\text{raw graph} \longrightarrow \text{magnetic projector} \longrightarrow \text{projective polynomials} \longrightarrow \text{triangular variables} \longrightarrow \text{raw one-variable kernel} \longrightarrow \text{canonical kernel} \longrightarrow \text{endpoint evaluation}
$$

である。

#### 人が決める部分

- crossed ladder の fermion chain の順序。
- loop momentum routing。
- $F_2(0)$ を取り出す projector の物理的意味。
- projective parameter 表示から三角領域へ移る変数変換の採用。
- endpoint singularity を分割して扱う方針。

#### QEDCalc が処理する部分

- raw LaTeX の parse。
- crossed 専用 denominator/projective family の生成。
- projector table の生成。
- Jacobian と logarithm argument の exact check。
- raw 1変数 kernel の構成。
- Hermite/total-derivative reduction。
- endpoint sector と boundary term の cancellation check。
- 最終解析係数の checkpoint。

最終結果は、

$$
\boxed{ A_{\mathrm X} = \frac16 + \frac{13\pi^2}{36} + \frac54\zeta(3) - \frac{5\pi^2}{6}\ln2 }
$$

である。

#### 残る手動性

最大の手動部分は、raw Feynman 図から「crossed ladder としてどの momentum routing・変数変換を採用するか」を決める部分である。

なお Karplus--Kroll の旧結果との差 $1/32$ が歴史的計算のどこで生じたかは未解決であるが、これは現在の crossed ladder 最終値の未確定を意味しない。

---

### 5.2 ordinary ladder 1図

ordinary ladder は2ループ7図の中でも、特に代数処理量の大きい例である。

全体は、

$$
\text{raw graph} \longrightarrow D\text{ dimensional projector} \longrightarrow \text{scalar integrals} \longrightarrow 72\text{ projector terms} \longrightarrow 40\text{ canonical targets} \longrightarrow 12\text{ master basis} \longrightarrow \text{bare coefficient} \longrightarrow \text{on-shell subtraction}
$$

と進む。

#### 人が決める部分

- $D$ 次元で計算する必要性。
- projector ansatz。
- $q\to0$ 極限で $A_0$ と $C_1=B_1-2A_1$ に分離する方針。
- on-shell renormalization でどの1ループ counterterm を組み合わせるか。

#### QEDCalc が処理する部分

- $D$ 次元 gamma trace。
- projector 係数を決める連立方程式。
- scalar integral への展開。
- 72 projector terms の生成。
- 40 canonical IBP targets への整理。
- 12 terminal master basis への reduction。
- bare finite coefficient の再構成。
- one-loop subtraction series の組み立て。
- renormalized coefficient の exact checkpoint。

bare 側は、

$$
A_{\mathrm L,bare} = -\frac{3}{4(D-4)} + \frac{107}{48} + \frac{\pi^2}{18} + O(D-4)
$$

まで再構成される。

on-shell subtraction 後は、

$$
\boxed{ A_{\mathrm L} = \frac{11}{48} + \frac{\pi^2}{18} }
$$

となる。

#### 2ループ半自動化の代表例

ordinary ladder の `72 -> 40 -> 12` は、QEDCalc を使う価値を最も分かりやすく示す。

人間が72項を手で展開・分類し、さらに IBP 関係を追跡する必要はなくなった。

一方で、「どの projector を使い、なぜその $q\to0$ 展開でよいか」は人間側に残る。

---

### 5.3 corner 2図

corner は、単なる長大代数よりも、UV subdivergence、renormalized inner vertex、soft/hard sector、IR regulator の扱いが難しい例である。

流れは、

$$
\text{raw pair} \longrightarrow \text{topology audit} \longrightarrow \text{magnetic projector} \longrightarrow \text{parametric family} \longrightarrow \text{UV local subtraction} \longrightarrow \text{renormalized sectors} \longrightarrow \text{soft/hard split} \longrightarrow \text{IR asymptotic}
$$

である。

#### 人が決める部分

- 2図の非可換順序。
- inner vertex subgraph を renormalization すべきこと。
- local UV counterterm の物理的意味。
- photon mass regulator

$$
\rho=\frac{\lambda}{m}
$$

を導入し、途中で $\rho=0$ にしないこと。
- soft/hard sector の物理的分離。

#### QEDCalc が処理する部分

- 2つの raw LaTeX ファイルの読み込みと topology audit。
- $q$ 一次 magnetic projector polynomial の生成。
- Feynman parameter family と平方完成データの生成。
- bare UV residue と local counterterm residue の exact 比較。
- renormalized sector identity の検査。
- soft kernel と IR log coefficient の抽出。
- momentum-shift correction、hard sector、$z$ sector の解析値合成。
- soft/hard ownership の exact check。
- self-energy insertion と組み合わせた IR cancellation。

corner 2図の和は、

$$
A_{\mathrm C} = \ln\frac1\rho - \frac{67}{24} + \frac{\pi^2}{18} - \frac12\zeta(3) + \frac{\pi^2}{3}\ln2 + o(1)
$$

である。

有限部は、

$$
\boxed{ A_{\mathrm C,fin} = -\frac{67}{24} + \frac{\pi^2}{18} - \frac12\zeta(3) + \frac{\pi^2}{3}\ln2 }
$$

となる。

#### 残る手動性

corner では、どの subgraph を renormalized inner vertex と見なすか、どの sector を soft として切り出すかなど、物理的構造の判断がまだ大きく人間側に残る。

---

### 5.4 self-energy insertion 2図

self-energy insertion では、raw 2図から内部 self-energy subdiagram を見つけて縮約し、on-shell renormalized self-energy を outer vertex へ戻す。

流れは、

$$
\text{raw pair} \longrightarrow \text{self-energy subdiagram detection} \longrightarrow \Sigma\text{ numerator reduction} \longrightarrow \Sigma_R\text{ on-shell subtraction} \longrightarrow \text{outer insertion} \longrightarrow \text{finite part + IR part}
$$

である。

#### 人が決める部分

- left/right insertion の Feynman-rule 順序。
- on-shell renormalization condition。
- self-energy の UV subtraction を実行してから outer loop へ戻すこと。
- IR asymptotic を取る前に $\rho$ を0へ置かないこと。

#### QEDCalc が処理する部分

- raw diagram 内の self-energy subdiagram pattern detection。
- subdiagram contraction。
- gamma contraction。
- loop shift、odd-term removal。
- UV cancellation の audit。
- compact outer diagram の生成。
- finite kernel の段階的積分。
- IR asymptotic の抽出。
- raw-to-final audit。
- corner との IR log cancellation。

結果は、

$$
A_{\mathrm S}(\rho) = \ln\rho + \frac{11}{24} - \frac{\pi^2}{18} + o(1)
$$

であり、

$$
\boxed{ A_{\mathrm S,fin} = \frac{11}{24} - \frac{\pi^2}{18} }
$$

となる。

corner の IR 項と合わせると、

$$
\ln\frac1\rho + \ln\rho = 0
$$

である。

この IR cancellation は v0.90.0 regression で exact に検査される。

---

### 5.5 vacuum polarization 1図

vacuum polarization は、閉じた electron loop を自動的に認識できるという点で、QEDCalc の topology-to-algebra 接続が比較的進んだ例である。

流れは、

$$
\text{complete raw graph} \longrightarrow \text{closed trace detection} \longrightarrow \text{Dirac trace} \longrightarrow \text{tensor reduction} \longrightarrow \Pi_R(k^2) \longrightarrow \text{outer magnetic kernel} \longrightarrow \text{analytic integration}
$$

である。

#### 人が決める部分

- complete raw Feynman-rule expression。
- 真空偏極 tensor が transverse form を持つことの物理的意味。
- on-shell charge renormalization condition

$$
\Pi_R(0)=0
$$

を採用すること。
- renormalized scalar vacuum-polarization function を outer photon propagator へ挿入すること。

#### QEDCalc が処理する部分

- complete raw diagram の parse。
- closed Dirac trace の検出。
- propagator scalarization。
- 4次元 Dirac trace。
- loop shift。
- odd term removal。
- rank-2 tensor reduction。
- transversality residual の検査。
- on-shell subtraction 後の有限 kernel。
- outer magnetic 2変数 kernel。
- $z$ 積分による1変数 kernel。
- primitive derivative と endpoint evaluation。

最終結果は、

$$
\boxed{ A_{\mathrm{VP}} = \frac{119}{36} - \frac{\pi^2}{3} }
$$

である。

#### 現状の特徴

vacuum polarization は complete raw LaTeX から closed electron loop を発見できるため、5種類の中では比較的「raw input からの自動化」が進んでいる。

ただし tensor の transverse decomposition をどう物理的に解釈し、どの renormalization condition を使うかは人が決める。

---

## 6. 5図群の自動化状況一覧

| 図 | raw式のparse | topology/subgraph検出 | Dirac/trace | projector | parameter/tensor | renormalization | 最終解析checkpoint | 主な人間判断 |
|---|---|---|---|---|---|---|---|---|
| crossed ladder | ○ | △ | ○ | ○ | ○ | ○ | ○ | routing、変数変換、endpoint分割 |
| ordinary ladder | ○ | △ | ○ | ○ | ○ | ○ | ○ | D次元projector、$A_0/C_1$ 分離 |
| corner 2図 | ○ | ○ | ○ | ○ | ○ | ○ | ○ | inner subgraph、soft/hard、IR regulator |
| self-energy 2図 | ○ | ○ | ○ | ○ | ○ | ○ | ○ | on-shell条件、outerへの再挿入 |
| vacuum polarization | ○ | ○ | ○ | ○ | ○ | ○ | ○ | transverse form、charge renormalization |

ここで、

- `○` は専用実装で自動処理可能。
- `△` は入力 topology や family を人が明示する必要がある。

ことを表す。

重要なのは、表のすべてが「任意の未知の2ループ図を完全自動で処理できる」という意味ではないことである。

現在の自動化は、**2ループ7図について検証済みの専用 route が存在する**という意味である。

---

## 7. 人が行う作業はどこまで減ったか

従来の完全な手計算では、次のような作業を人間が逐一行う必要があった。

- 数十～数百項の gamma 行列展開。
- Dirac trace の大量展開。
- Lorentz index contraction。
- loop momentum shift 後の分子再展開。
- odd term の除去。
- symmetric tensor integration。
- Feynman parameter denominator の整理。
- projector の $q$ 展開。
- IBP 関係の大量整理。
- UV pole の cancellation 確認。
- IR log coefficient の比較。
- endpoint singularity の cancellation 確認。

QEDCalc を使うことで、これらの多くは「入力式を正しく用意する」ことに置き換わった。

したがって、人間が読む計算過程説明書も、以前のように全展開項を記録する必要はなくなる。

今後の説明書では、

$$
\boxed{ \text{入力式をなぜ作るか} \;+ \text{その入力式をどう導出するか} \;+ \text{QEDCalc の入出力} }
$$

を残せば、長大な純代数展開そのものは原則として省略できる。

これは今回作成した5つの「QEDCalcサンプル説明書兼計算過程説明書」の基本方針でもある。

---

## 8. それでも人間が残すべき記述

自動化が進んでも、次の部分を文書から省いてはいけない。

### 8.1 元の Feynman 図から入力式を作る過程

Fermion propagator と gamma matrix の順序は非可換である。

したがって、図からどの順番で因子を並べたのかは、必ず人間が説明する必要がある。

### 8.2 なぜその projector を使うのか

QEDCalc が projector algebra を実行できても、

$$
F_2(0)
$$

が異常磁気能率に対応する理由と、projector が $F_1$ を除去して $F_2$ を抽出する理由は物理的説明として残す。

### 8.3 renormalization の対象と条件

QEDCalc が counterterm residual を exact に検査できても、

- どの subgraph を renormalize するか。
- on-shell scheme のどの条件を使うか。
- subtraction の物理的意味は何か。

は文書に残す。

### 8.4 IR regulator をいつ外せるか

特に corner/self-energy では、個別図で $\rho\to0$ としてはいけない。

$$
A_{\mathrm C}^{\mathrm{IR}} = \ln\frac1\rho
$$

と

$$
A_{\mathrm S}^{\mathrm{IR}} = \ln\rho
$$

を組み合わせてから極限を取ることが重要である。

### 8.5 変数変換・sector 分割の理由

計算機が式変形を確認できても、「なぜその変数変換を選んだか」は将来読み返すために残すべき情報である。

---

## 9. v0.90.0 で達成した regression 構造

QEDCalc v0.90.0 では、2ループ完成状態を壊していないことを、

`run_v090_validation.bat`

で確認できる。

標準ライブラリだけで実行する release regression では、

```text
Phase-83 complete two-loop regression PASS
diagram count = 7
IR log residual = 0
ordinary ladder reduction = 72 -> 40 -> 12
total basis coefficients = ('197/144', '1/12', '3/4', '-1/2', '0')
historical 1/32 origin resolved = False
QEDCalc 0.90.0
v0.90 validation PASS
```

まで確認する。

これは重要な区切りである。

今後 QEDCalc に3ループ処理や新しい一般化を追加しても、v0.90 regression を実行することで、2ループ計算に regression が入っていないか確認できる。

---

## 10. 現在まだ完全自動ではない部分

2ループ7図が計算できたことと、任意の2ループ Feynman 図が全自動で計算できることは別である。

現在の主な未自動化部分は次のとおりである。

### 10.1 Feynman 図そのものからの topology 自動認識

現在は主として、人間が Feynman 則に従った LaTeX expression を入力する。

将来的には、graph topology data から

- fermion chain ordering
- photon connection
- momentum routing
- symmetry/sign factor

を自動生成できれば、最初の人間作業を大きく減らせる。

### 10.2 任意の subgraph の自動 renormalization 判定

self-energy や vacuum polarization など特定 pattern の検出は進んでいる。

しかし任意 graph について、

$$
\text{divergent subgraphs} \longrightarrow \text{forest} \longrightarrow \text{local counterterms}
$$

を完全自動で構成し、正しい on-shell counterterm まで生成するところは今後の課題である。

### 10.3 最適な parameterization・変数変換の自動選択

crossed ladder や corner では、解析しやすい変数変換を人が選んでいる。

これは高ループになるほど大きな問題になる。

### 10.4 master integral の一般自動評価

ordinary ladder では12 master basis まで reduction できた。

しかし一般 graph について、未知の master integral を自動的に解析評価することは別問題である。

### 10.5 最終解析定数 basis の自動認識

現在は、$\pi^2$、$\zeta(3)$、$\pi^2\ln2$ など既知の解析構造を使って checkpoint を構成している。

高ループではより複雑な HPL、multiple zeta value、elliptic integral などが現れる可能性がある。

---

## 11. 今後の自動化優先順位

3ループへ進む前または並行して、自動化率を上げるなら次の順序が有効である。

### 優先度1：raw graph → ordered amplitude の一般化

人が最も間違えやすいのは、Feynman 図から非可換な因子順序を作る部分である。

ここを topology object から生成できれば大きい。

### 優先度2：subgraph detection → renormalization plan の一般化

現在の self-energy / vacuum-polarization 専用 detection を一般化し、

$$
\text{graph} \longrightarrow \text{UV divergent subgraphs} \longrightarrow \text{required counterterms}
$$

を自動提案できるようにする。

### 優先度3：projector construction の共通化

ordinary ladder、crossed ladder、corner で個別に使っている magnetic projector route を、より統一的な API にまとめる。

### 優先度4：parameter/sector strategy のライブラリ化

2ループで成功した変数変換・soft/hard split・endpoint handling を reusable strategy として蓄積する。

### 優先度5：3ループへの展開

上記を使って、3ループ72図を「図ごとに手作りする」のではなく、同じ topology/subgraph/projector/reduction machinery へ流せる割合を増やす。

---

## 12. 3ループへ進む際に2ループから引き継ぐべき設計原則

2ループ実装から、次の原則が有効だと分かった。

### 12.1 ブラックボックス化しない

最終数値だけを返すのではなく、

$$
\text{input} \longrightarrow \text{intermediate invariant} \longrightarrow \text{output}
$$

を段階ごとに保存する。

### 12.2 人の判断と機械代数を分離する

物理的判断を QEDCalc が勝手に推測しない。

判断した内容を explicit input として与え、その後の機械的処理を自動化する。

### 12.3 各段階に exact residual を持つ

「見た目が同じ」「数値が近い」ではなく、可能な限り symbolic residual が0になることを checkpoint にする。

### 12.4 数値積分だけに逃げない

発散・subtraction・IR cancellation があるため、高ループ積分を raw のまま数値積分するのではなく、先に代数的構造を整理する。

### 12.5 計算資料とプログラム説明書を分離しすぎない

今回の5サンプル資料のように、

- 人が導出する入力式。
- QEDCalc のコード。
- QEDCalc の出力。
- 出力を次にどう使うか。

を同じ資料でつなぐ方が、将来再現しやすい。

---

## 13. 現時点での評価

QEDCalc v0.90.0 時点では、2ループ7図について、

$$
\boxed{ \text{「完全手計算」から「人が物理を指示し、QEDCalc が代数を処理する半自動計算」へ移行できた} }
$$

と評価できる。

特に重要なのは、単に既知の最終値をプログラムへ埋め込んだのではなく、図ごとに異なる困難、

- crossed ladder の projective/endpoint 処理。
- ordinary ladder の $D$ 次元 projector と `72 -> 40 -> 12` reduction。
- corner の UV subdivergence と soft/hard ownership。
- self-energy insertion の subdiagram contraction と IR asymptotic。
- vacuum polarization の closed-loop trace と transversality。

を個別に通過し、それらを最後に7図の exact sum として統合した点である。

一方で、最も知的な部分、すなわち

$$
\boxed{ \text{何を計算すべきか、どの物理構造を分離すべきか、どの表現へ変換すべきか} }
$$

はまだ人間が担っている。

したがって現在の QEDCalc は「QED を自動で解くプログラム」ではない。

より正確には、

$$
\boxed{ \text{QED の高次摂動計算を、人間が追跡可能な形で半自動化する計算基盤} }
$$

である。

---

## 14. 2ループ完了時点の固定 checkpoint

今後3ループ以降へ進んでも、2ループについて次の値を固定 checkpoint とする。

### crossed ladder

$$
A_{\mathrm X} = \frac16 + \frac{13\pi^2}{36} + \frac54\zeta(3) - \frac{5\pi^2}{6}\ln2
$$

### ordinary ladder

$$
A_{\mathrm L} = \frac{11}{48} + \frac{\pi^2}{18}
$$

### corner 2図

$$
A_{\mathrm C} = \ln\frac1\rho - \frac{67}{24} + \frac{\pi^2}{18} - \frac12\zeta(3) + \frac{\pi^2}{3}\ln2
$$

### self-energy insertion 2図

$$
A_{\mathrm S} = \ln\rho + \frac{11}{24} - \frac{\pi^2}{18}
$$

### vacuum polarization

$$
A_{\mathrm{VP}} = \frac{119}{36} - \frac{\pi^2}{3}
$$

### IR cancellation

$$
\ln\frac1\rho + \ln\rho = 0
$$

### 7図総和

$$
\boxed{ A_1^{(4)} = \frac{197}{144} + \frac{\pi^2}{12} + \frac34\zeta(3) - \frac{\pi^2}{2}\ln2 }
$$

これらを QEDCalc 2ループ実装の基準値として今後も regression test する。

---

## 15. 関連ファイル

### サンプル計算説明書

- `01_crossed_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`
- `02_ordinary_ladder_QEDCalcサンプル説明書兼計算過程説明書.md`
- `03_corner_2図_QEDCalcサンプル説明書兼計算過程説明書.md`
- `04_self_energy_insertion_2図_QEDCalcサンプル説明書兼計算過程説明書.md`
- `05_vacuum_polarization_QEDCalcサンプル説明書兼計算過程説明書.md`

### QEDCalc release checkpoint

- Phase 77：corner end-to-end closure
- Phase 78：crossed ladder end-to-end closure
- Phase 79：vacuum polarization end-to-end closure
- Phase 80：self-energy insertion end-to-end closure
- Phase 81：ordinary ladder end-to-end closure
- Phase 82：seven-diagram release audit
- Phase 83：complete two-loop regression

### 2ループ完成 regression

`run_v090_validation.bat`

---

# 結論

2ループ7図については、QEDCalc v0.90.0 により、

$$
\boxed{ \text{計算過程を人間が理解・指定しながら、面倒な代数処理を QEDCalc に委ねる半自動処理} }
$$

が実現した。

これは単なる計算速度の改善ではない。

大量の手計算をコードへ移すことで、人間が確認すべき対象を

$$
\boxed{ \text{物理的な判断、入力式の正しさ、処理の接続、最終的な整合性} }
$$

へ集中させられるようになったことが、本実装の最も重要な到達点である。
