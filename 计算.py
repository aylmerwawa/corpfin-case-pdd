# 拼多多案例分析 2026：全部数据与计算（单位：人民币亿元）
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB", "Heiti TC", "STHeiti"]
plt.rcParams["axes.unicode_minus"] = False
OUT = "结果/"
Y = list(range(2019, 2026))
# ---------- 资料一：利润表 ----------
IS = pd.DataFrame({
 "营业收入": [301.42, 594.92, 939.50, 1305.58, 2476.39, 3938.36, 4318.46],
 "营业成本": [63.39, 192.79, 317.18, 314.62, 917.24, 1539.00, 1888.02],
 "销售费用": [271.74, 411.95, 448.02, 543.44, 821.89, 1113.01, 1252.88],
 "管理费用": [12.97, 15.07, 15.41, 39.65, 40.76, 75.53, 81.58],
 "研发费用": [38.70, 68.92, 89.93, 103.85, 109.52, 126.59, 164.96],
 "营业利润": [-85.38, -93.80, 68.97, 304.02, 586.99, 1084.23, 931.02],
 "非经营损益净额": [17.16, 29.58, 40.36, 59.13, 132.22, 242.78, 264.73],
 "利息费用": [1.46, 7.57, 12.31, 0.52, 0.44, 0.00, 0.00],
 "所得税费用": [0.00, 0.00, 19.34, 47.26, 118.50, 202.67, 217.33],
 "净利润": [-69.68, -71.80, 77.69, 315.38, 600.27, 1124.35, 978.43]}, index=Y)
# ---------- 资料二：资产负债表 ----------
BS = pd.DataFrame({
 "现金及现金等价物": [57.68, 224.21, 64.27, 343.26, 597.94, 577.68, 1089.01],
 "受限现金": [275.78, 524.22, 596.17, 579.74, 619.85, 684.26, 738.31],
 "短期投资": [352.89, 645.51, 865.17, 1151.13, 1574.15, 2737.92, 3134.08],
 "应收及预付款": [43.67, 101.29, 83.49, 92.05, 155.55, 156.62, 228.41],
 "流动资产合计": [730.01, 1495.24, 1609.09, 2166.18, 2947.50, 4156.48, 5189.80],
 "固定资产及无形资产净额": [20.36, 14.80, 29.05, 11.79, 10.01, 8.98, 13.21],
 "其他非流动资产": [10.20, 79.05, 173.96, 193.23, 523.27, 884.88, 1097.43],
 "资产总额": [760.57, 1589.09, 1812.10, 2371.20, 3480.78, 5050.34, 6300.44],
 "客户预付款": [6.06, 24.23, 11.67, 13.90, 21.45, 29.47, 33.79],
 "应付商家款": [299.26, 538.34, 625.10, 633.17, 749.97, 916.56, 1074.07],
 "商家保证金": [78.41, 109.26, 135.78, 150.58, 168.79, 164.61, 177.08],
 "其他经营性流动负债": [63.80, 145.79, 160.49, 226.37, 565.90, 699.44, 827.44],
 "有息流动负债": [8.99, 18.66, 0.00, 138.86, 6.49, 53.10, 0.00],
 "流动租赁负债": [1.16, 2.53, 4.27, 6.02, 16.42, 21.06, 24.99],
 "流动负债合计": [457.68, 838.82, 937.30, 1168.89, 1529.01, 1884.23, 2137.37],
 "非流动负债合计": [56.43, 148.51, 123.65, 24.60, 79.36, 32.98, 29.22],
 "负债合计": [514.10, 987.33, 1060.95, 1193.49, 1608.37, 1917.21, 2166.59],
 "留存收益": [-182.95, -254.75, -177.07, 151.93, 751.19, 1874.21, 2841.63],
 "其他股东权益": [429.42, 856.51, 928.21, 1025.78, 1121.23, 1258.92, 1292.22],
 "股东权益合计": [246.47, 601.76, 751.15, 1177.71, 1872.42, 3133.13, 4133.85]}, index=Y)
# ---------- 资料三：2025 年补充资料 ----------
S3 = dict(折旧摊销=6.01483, 股权激励=79.36971, 其他经营调整=-224.94706, 购建修正=1.20660,
          金融投资支出=420.78405, 关联方贷款=2.00000, 其他投资流入=0.00246, 可转债非现金修正=0.80881,
          其他筹资流入=0.01363, 汇率影响=-17.51111, 当期所得税=219.14684)
R = {}   # 汇总数字，供写报告用
# ================= 00 数据核对 =================
chk = {
 "营业利润=收入-成本-三项费用": (IS.营业收入-IS.营业成本-IS.销售费用-IS.管理费用-IS.研发费用-IS.营业利润).abs().max(),
 "净利润=营业利润+非经营-利息-税": (IS.营业利润+IS.非经营损益净额-IS.利息费用-IS.所得税费用-IS.净利润).abs().max(),
 "资产总额=流动+固定+其他非流动": (BS.流动资产合计+BS.固定资产及无形资产净额+BS.其他非流动资产-BS.资产总额).abs().max(),
 "流动资产四项之和": (BS.现金及现金等价物+BS.受限现金+BS.短期投资+BS.应收及预付款-BS.流动资产合计).abs().max(),
 "资产=负债+权益": (BS.资产总额-BS.负债合计-BS.股东权益合计).abs().max(),
 "流动负债六项之和": (BS[["客户预付款","应付商家款","商家保证金","其他经营性流动负债","有息流动负债","流动租赁负债"]].sum(axis=1)-BS.流动负债合计).abs().max()}
pd.Series(chk, name="最大绝对差").round(3).to_csv(OUT+"00_数据核对.csv", encoding="utf-8-sig")
print("== 00 数据核对（最大绝对差，亿元）"); print(pd.Series(chk).round(3).to_string())
# ================= 01 现金流量表（间接法）、OCF、FCFF =================
a, b = BS.loc[2025], BS.loc[2024]
d_ar = a.应收及预付款 - b.应收及预付款
d_liab = {k: a[k]-b[k] for k in ["客户预付款","应付商家款","商家保证金","其他经营性流动负债"]}
ni25 = IS.loc[2025,"净利润"]
cfo = ni25 + S3["折旧摊销"] + S3["股权激励"] + S3["其他经营调整"] - d_ar + sum(d_liab.values())
capex = (a.固定资产及无形资产净额 - b.固定资产及无形资产净额) + S3["折旧摊销"] + S3["购建修正"]
cfi = -capex - S3["金融投资支出"] - S3["关联方贷款"] + S3["其他投资流入"]
conv_cash = (b.有息流动负债 - a.有息流动负债) - S3["可转债非现金修正"]    # 可转债现金偿付
cff = -conv_cash + S3["其他筹资流入"]
net = cfo + cfi + cff + S3["汇率影响"]
cash0, cash1 = b.现金及现金等价物+b.受限现金, a.现金及现金等价物+a.受限现金
rows = [("经营活动", None),
 ("净利润", ni25), ("加：折旧与摊销", S3["折旧摊销"]), ("加：股权激励费用", S3["股权激励"]),
 ("加：其他经营现金流调整净额", S3["其他经营调整"]), ("减：应收及预付款增加", -d_ar),
 ("加：客户预付款增加", d_liab["客户预付款"]), ("加：应付商家款增加", d_liab["应付商家款"]),
 ("加：商家保证金增加", d_liab["商家保证金"]), ("加：其他经营性流动负债增加", d_liab["其他经营性流动负债"]),
 ("经营活动现金流量净额（CFO）", cfo),
 ("投资活动", None),
 ("购建固定资产及无形资产支付的现金", -capex), ("金融投资现金净支出", -S3["金融投资支出"]),
 ("关联方贷款现金净支出", -S3["关联方贷款"]), ("其他投资活动现金流入", S3["其他投资流入"]),
 ("投资活动现金流量净额", cfi),
 ("筹资活动", None),
 ("偿还可转债（扣除非现金修正后的现金偿付）", -conv_cash), ("其他筹资活动现金净流入", S3["其他筹资流入"]),
 ("筹资活动现金流量净额", cff),
 ("汇率变动影响", S3["汇率影响"]), ("现金及受限现金净增加额", net),
 ("期初现金余额（含受限现金）", cash0), ("期末现金余额（计算）", cash0+net),
 ("期末现金余额（资产负债表）", cash1), ("差异（舍入尾差）", cash1-(cash0+net))]
cf = pd.DataFrame(rows, columns=["项目","金额（亿元）"]); cf.to_csv(OUT+"01_现金流量表.csv", index=False, encoding="utf-8-sig")
print("\n== 01 现金流量表（2025，间接法）"); print(cf.round(2).to_string(index=False))
ebit = IS.loc[2025,"营业利润"] + IS.loc[2025,"非经营损益净额"]
ocf = ebit + S3["折旧摊销"] - S3["当期所得税"]
def nowc(r): return (r.受限现金 + r.应收及预付款) - (r.客户预付款 + r.应付商家款 + r.商家保证金 + r.其他经营性流动负债)
nowc25, nowc24 = nowc(a), nowc(b); dnowc = nowc25 - nowc24
fcff = ebit*(1-0.25) + S3["折旧摊销"] - capex - dnowc
o = pd.Series({"EBIT（营业利润+非经营损益净额）":ebit, "折旧与摊销":S3["折旧摊销"], "当期所得税":S3["当期所得税"],
 "OCF（罗斯口径）":ocf, "NOWC 2024":nowc24, "NOWC 2025":nowc25, "ΔNOWC（经营性营运资本增加额）":dnowc,
 "CapEx":capex, "EBIT×(1-25%)":ebit*0.75, "FCFF":fcff, "CFO":cfo})
o.round(2).to_csv(OUT+"01b_OCF与FCFF.csv", header=["金额（亿元）"], encoding="utf-8-sig")
print("\n== 01b OCF 与 FCFF"); print(o.round(2).to_string())
R.update(cfo=cfo, cfi=cfi, cff=cff, net=net, ebit=ebit, ocf=ocf, nowc24=nowc24, nowc25=nowc25, dnowc=dnowc, capex=capex, fcff=fcff,
         diff=cash1-(cash0+net), cash0=cash0, cash1=cash1)
# ================= 02 共同比利润表与盈利变化 =================
cs = pd.DataFrame({k: IS[k]/IS.营业收入 for k in ["营业成本","销售费用","管理费用","研发费用","营业利润","非经营损益净额","利息费用","所得税费用","净利润"]})*100
cs.insert(0,"营业收入",100.0); cs.T.round(2).to_csv(OUT+"02_共同比利润表.csv", encoding="utf-8-sig")
rt = pd.DataFrame({"毛利率":(1-IS.营业成本/IS.营业收入)*100, "销售费用率":cs.销售费用, "管理费用率":cs.管理费用,
                   "研发费用率":cs.研发费用, "营业利润率":cs.营业利润, "净利率":cs.净利润})
rt["收入增长率"] = IS.营业收入.pct_change()*100
rt.T.round(2).to_csv(OUT+"02_盈利比率.csv", encoding="utf-8-sig")
cagr = (IS.loc[2025,"营业收入"]/IS.loc[2019,"营业收入"])**(1/6)-1
print("\n== 02 共同比利润表（占收入 %）"); print(cs.T.round(2).to_string())
print("\n== 02 盈利比率（%）"); print(rt.T.round(2).to_string()); print(f"收入 CAGR 2019-2025（6 年）= {cagr*100:.2f}%")
def bridge(y0, y1):
    d = rt.loc[y1]-rt.loc[y0]
    return pd.Series({"营业成本率变化→贡献":-(cs.loc[y1,"营业成本"]-cs.loc[y0,"营业成本"]), "销售费用率变化→贡献":-(cs.loc[y1,"销售费用"]-cs.loc[y0,"销售费用"]),
      "管理费用率变化→贡献":-(cs.loc[y1,"管理费用"]-cs.loc[y0,"管理费用"]), "研发费用率变化→贡献":-(cs.loc[y1,"研发费用"]-cs.loc[y0,"研发费用"]),
      "营业利润率合计变化":cs.loc[y1,"营业利润"]-cs.loc[y0,"营业利润"]})
br = pd.concat({"2020→2021":bridge(2020,2021), "2024→2025":bridge(2024,2025)}, axis=1)
br.round(2).to_csv(OUT+"02b_营业利润率拆解.csv", encoding="utf-8-sig")
print("\n== 02b 营业利润率变化的来源（百分点）"); print(br.round(2).to_string())
R.update(cagr=cagr)
# 图：收入与净利润
fig, ax = plt.subplots(figsize=(8,4.4))
ax.bar(Y, IS.营业收入, color="#9db4d6", label="营业收入"); ax.set_ylabel("营业收入（亿元）")
ax2 = ax.twinx(); ax2.plot(Y, IS.净利润, color="#c0392b", marker="o", label="净利润"); ax2.axhline(0, color="gray", lw=.6)
ax2.set_ylabel("净利润（亿元）")
for x, v in zip(Y, IS.净利润): ax2.annotate(f"{v:.0f}", (x, v), textcoords="offset points", xytext=(0,6), ha="center", fontsize=8, color="#c0392b")
h1,l1 = ax.get_legend_handles_labels(); h2,l2 = ax2.get_legend_handles_labels(); ax.legend(h1+h2, l1+l2, loc="upper left")
ax.set_title("拼多多：营业收入与净利润（2019–2025）"); fig.tight_layout(); fig.savefig(OUT+"fig-02-收入与净利润.png", dpi=200); plt.close(fig)
# 图：费用率与利润率
fig, ax = plt.subplots(figsize=(8,4.4))
for c in ["毛利率","销售费用率","研发费用率","营业利润率","净利率"]: ax.plot(Y, rt[c], marker="o", label=c)
ax.axhline(0, color="gray", lw=.6); ax.set_ylabel("占营业收入比（%）"); ax.legend(ncol=3, fontsize=8); ax.set_title("毛利率、费用率与利润率"); fig.tight_layout()
fig.savefig(OUT+"fig-02b-费用率与利润率.png", dpi=200); plt.close(fig)
# ================= 03 利润与现金 =================
diff3 = pd.Series({"净利润":ni25, "折旧与摊销":S3["折旧摊销"], "股权激励费用":S3["股权激励"], "应收及预付款增加":-d_ar,
  "客户预付款增加":d_liab["客户预付款"], "应付商家款增加":d_liab["应付商家款"], "商家保证金增加":d_liab["商家保证金"],
  "其他经营性流动负债增加":d_liab["其他经营性流动负债"], "其他经营现金流调整净额":S3["其他经营调整"], "CFO":cfo, "CFO－净利润":cfo-ni25})
diff3.round(2).to_csv(OUT+"03_CFO与净利润差异.csv", header=["金额（亿元）"], encoding="utf-8-sig")
print("\n== 03 CFO 与净利润"); print(diff3.round(2).to_string())
# 亏损年份的近似 CFO（只含营运资本变动，不含折旧、股权激励等，仅作估算）
def approx_cfo(y):
    p, c = BS.loc[y-1], BS.loc[y]
    dl = sum(c[k]-p[k] for k in ["客户预付款","应付商家款","商家保证金","其他经营性流动负债"])
    return IS.loc[y,"净利润"] - (c.应收及预付款-p.应收及预付款) + dl, dl
ap20, dl20 = approx_cfo(2020)
print(f"\n2020 年净亏损 {IS.loc[2020,'净利润']:.2f}，经营性负债增加 {dl20:.2f}，近似 CFO（不含非现金项目）= {ap20:.2f}")
R.update(approx_cfo20=ap20, dl20=dl20)
cash_tot = a.现金及现金等价物 + a.受限现金
merch = a.应付商家款 + a.商家保证金
free_est = a.现金及现金等价物 - max(a.应付商家款 - a.受限现金, 0) - a.商家保证金
cashtab = pd.Series({"现金及现金等价物":a.现金及现金等价物, "受限现金":a.受限现金, "账面现金合计":cash_tot, "短期投资":a.短期投资,
  "应付商家款":a.应付商家款, "商家保证金":a.商家保证金, "客户预付款":a.客户预付款,
  "受限现金/应付商家款":a.受限现金/a.应付商家款, "应付商家款中受限现金覆盖不到的部分":max(a.应付商家款-a.受限现金,0),
  "现金及等价物扣除上述缺口和保证金后的估算":free_est})
cashtab.round(2).to_csv(OUT+"03b_现金能否分红.csv", header=["数值"], encoding="utf-8-sig")
print("\n== 03b 现金能否用于分红"); print(cashtab.round(2).to_string())
R.update(free_est=free_est)
# ================= 04 财务状况（期末口径） =================
def ratios(y):
    r, i = BS.loc[y], IS.loc[y]
    return pd.Series({"流动比率":r.流动资产合计/r.流动负债合计, "现金比率":r.现金及现金等价物/r.流动负债合计,
      "现金及短期投资覆盖率":(r.现金及现金等价物+r.短期投资)/r.流动负债合计, "资产负债率":r.负债合计/r.资产总额,
      "总资产周转率":i.营业收入/r.资产总额, "ROA":i.净利润/r.资产总额, "权益乘数":r.资产总额/r.股东权益合计, "ROE":i.净利润/r.股东权益合计,
      "销售净利率":i.净利润/i.营业收入})
rat = pd.concat({2024:ratios(2024), 2025:ratios(2025)}, axis=1); rat.round(4).to_csv(OUT+"04_财务比率_拼多多.csv", encoding="utf-8-sig")
print("\n== 04 拼多多财务比率"); print(rat.round(4).to_string())
# 杜邦：对数分解，三项贡献之和恰好等于 ROE 变化
r4, r5 = rat[2024], rat[2025]
lw = (r5.ROE-r4.ROE)/np.log(r5.ROE/r4.ROE)
dup = pd.Series({k: lw*np.log(r5[k]/r4[k]) for k in ["销售净利率","总资产周转率","权益乘数"]})
dup["ROE 变化合计"] = r5.ROE-r4.ROE
print("\n杜邦分解：ROE 变化（对数中点法，单位为 ROE 的小数）"); print((dup*100).round(2).to_string())
dup.to_csv(OUT+"04b_杜邦分解.csv", header=["贡献"], encoding="utf-8-sig")
# ================= 05 2026 预测 =================
g = 0.15; S0 = IS.loc[2025,"营业收入"]; NI1 = ni25*(1+g); TA = a.资产总额
spont = a.客户预付款 + a.应付商家款 + a.商家保证金
dA, dL = TA*g, spont*g
ROA, ROE = ni25/TA, ni25/a.股东权益合计
def igr(b): return ROA*b/(1-ROA*b)
def sgr(b): return ROE*b/(1-ROE*b)
def efn_pct(b): return dA - dL - b*NI1
def efn_formula(b): return TA/S0*(S0*g) - spont/S0*(S0*g) - (ni25/S0)*(S0*(1+g))*b
res = pd.DataFrame({b: {"IGR":igr(b), "SGR":sgr(b), "EFN（销售百分比法）":efn_pct(b), "EFN（公式法）":efn_formula(b)} for b in [.5,.7,.9]})
res.round(4).to_csv(OUT+"05_三种留存率.csv", encoding="utf-8-sig")
print("\n== 05 三种留存率（IGR、SGR 为小数；EFN 为亿元）"); print(res.round(4).to_string())
crit = pd.Series({"IGR=15% 的临界留存率":(g/(1+g))/ROA, "SGR=15% 的临界留存率":(g/(1+g))/ROE, "EFN=0 的临界留存率":(dA-dL)/NI1})
crit.round(4).to_csv(OUT+"05b_临界留存率.csv", header=["留存率"], encoding="utf-8-sig")
print("\n临界留存率"); print(crit.round(4).to_string())
print(f"\nROA={ROA:.4f} ROE={ROE:.4f}  ΔA={dA:.2f} 自发负债增加={dL:.2f} 2026净利润={NI1:.2f}")
# 预计利润表与融资前资产负债表（留存率 70%）
bb = 0.7
isf = (IS.loc[2025]*(1+g)).rename("2026E"); isf = pd.concat([IS.loc[2025].rename("2025"), isf], axis=1)
isf.loc["股利"] = [ni25*(1-bb), NI1*(1-bb)]; isf.loc["留存利润"] = [ni25*bb, NI1*bb]
isf.round(2).to_csv(OUT+"05c_预计利润表.csv", encoding="utf-8-sig")
grow_l = ["客户预付款","应付商家款","商家保证金"]
bsf = pd.DataFrame({"2025":a, "2026E":a.copy()})
for k in ["现金及现金等价物","受限现金","短期投资","应收及预付款","固定资产及无形资产净额","其他非流动资产"]: bsf.loc[k,"2026E"] = a[k]*(1+g)
for k in grow_l: bsf.loc[k,"2026E"] = a[k]*(1+g)
bsf.loc["资产总额","2026E"] = bsf.loc[["现金及现金等价物","受限现金","短期投资","应收及预付款","固定资产及无形资产净额","其他非流动资产"],"2026E"].sum()
bsf.loc["流动资产合计","2026E"] = bsf.loc[["现金及现金等价物","受限现金","短期投资","应收及预付款"],"2026E"].sum()
bsf.loc["流动负债合计","2026E"] = bsf.loc[["客户预付款","应付商家款","商家保证金","其他经营性流动负债","有息流动负债","流动租赁负债"],"2026E"].sum()
bsf.loc["负债合计","2026E"] = bsf.loc["流动负债合计","2026E"] + a.非流动负债合计
bsf.loc["留存收益","2026E"] = a.留存收益 + bb*NI1
bsf.loc["股东权益合计","2026E"] = bsf.loc["留存收益","2026E"] + a.其他股东权益
bsf.loc["负债与权益合计（融资前）","2026E"] = bsf.loc["负债合计","2026E"] + bsf.loc["股东权益合计","2026E"]
bsf.loc["融资缺口（负数为资金盈余）","2026E"] = bsf.loc["资产总额","2026E"] - bsf.loc["负债与权益合计（融资前）","2026E"]
bsf.loc["融资缺口（负数为资金盈余）","2025"] = 0
bsf.round(2).to_csv(OUT+"05d_融资前资产负债表.csv", encoding="utf-8-sig")
print("\n== 05d 融资前预计资产负债表（70% 留存）"); print(bsf.round(2).to_string())
R.update(ROA=ROA, ROE=ROE, dA=dA, dL=dL, NI1=NI1)
json.dump({k: float(v) for k,v in R.items()}, open(OUT+"numbers.json","w"), ensure_ascii=False, indent=1)
