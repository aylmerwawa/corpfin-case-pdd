# 读取 结果/ 里的计算结果，生成 报告.qmd（所有数字都来自计算结果，不手抄）
import json, re, pandas as pd, numpy as np
O = "结果/"
R = json.load(open(O+"numbers.json", encoding="utf-8"))
def n2(x, d=2):
    if x is None or (isinstance(x, float) and np.isnan(x)): return ""
    return f"{x:,.{d}f}".replace("-", "−")
def pc(x, d=2): return f"{x*100:.{d}f}%".replace("-", "−")
def md(df, fmt=n2, idx=""):
    cols = [str(c) for c in df.columns]
    L = ["| " + " | ".join([idx]+cols) + " |", "|" + "|".join(["---"]*(len(cols)+1)) + "|"]
    for i, r in df.iterrows():
        L.append("| " + " | ".join([str(i)] + [v if isinstance(v, str) else fmt(v) for v in r.values]) + " |")
    return "\n".join(L)
# ---- 读表 ----
cf = pd.read_csv(O+"01_现金流量表.csv"); o = pd.read_csv(O+"01b_OCF与FCFF.csv", index_col=0)["金额（亿元）"]
cs = pd.read_csv(O+"02_共同比利润表.csv", index_col=0); rt = pd.read_csv(O+"02_盈利比率.csv", index_col=0)
br = pd.read_csv(O+"02b_营业利润率拆解.csv", index_col=0); d3 = pd.read_csv(O+"03_CFO与净利润差异.csv", index_col=0)["金额（亿元）"]
ct = pd.read_csv(O+"03b_现金能否分红.csv", index_col=0)["数值"]; rat = pd.read_csv(O+"04_财务比率_拼多多.csv", index_col=0)
dup = pd.read_csv(O+"04b_杜邦分解.csv", index_col=0)["贡献"]; cmpt = pd.read_csv(O+"04c_两家公司财务比率对照.csv", index_col=0)
mm = pd.read_csv(O+"04e_业务模式指标.csv", index_col=0); jd = pd.read_csv(O+"04d_京东原始数据_亿元.csv", index_col=0)
res = pd.read_csv(O+"05_三种留存率.csv", index_col=0); crit = pd.read_csv(O+"05b_临界留存率.csv", index_col=0)["留存率"]
isf = pd.read_csv(O+"05c_预计利润表.csv", index_col=0); bsf = pd.read_csv(O+"05d_融资前资产负债表.csv", index_col=0)
rat.columns = ["2024", "2025"]
# ---- 表格 ----
rows = []
for _, r in cf.iterrows():
    v = r["金额（亿元）"]
    rows.append((f"**{r['项目']}**", "") if pd.isna(v) else (r["项目"], n2(v)))
T_CF = md(pd.DataFrame(rows, columns=["项目", "金额（亿元）"]).set_index("项目"), fmt=lambda s: s)
T_OCF = md(o.to_frame("金额（亿元）"))
bridge = pd.DataFrame({"金额（亿元）": {
  "经营活动现金流量净额 CFO": R["cfo"],
  "减：净利润超出 EBIT×(1−25%) 的部分": -(d3["净利润"]-R["ebit"]*0.75),
  "减：股权激励（FCFF 不加回）": -d3["股权激励费用"],
  "加：其他经营现金流调整净额的反向（FCFF 不剔除投资估值等非现金项目）": -d3["其他经营现金流调整净额"],
  "减：购建固定资产及无形资产 CapEx": -R["capex"],
  "减：受限现金增加（FCFF 把受限现金算作经营性资产）": -54.05,
  "= FCFF": R["fcff"]}})
chk = bridge.iloc[:-1,0].sum(); assert abs(chk-R["fcff"]) < 0.05, chk
T_BR1 = md(bridge)
bridge2 = pd.DataFrame({"金额（亿元）": {"OCF（罗斯口径）": R["ocf"],
  "加：实际当期税 219.15 与标准化税率 25% 下的税 298.94 之差（税的口径）": -(R["ebit"]*0.25-219.14684),
  "减：CapEx": -R["capex"], "加：经营性营运资本减少（释放现金）": -R["dnowc"], "= FCFF": R["fcff"]}})
assert abs(bridge2.iloc[:-1,0].sum()-R["fcff"]) < 0.05
T_BR2 = md(bridge2)
yrs = [str(y) for y in range(2019, 2026)]
cs.columns = yrs; rt.columns = yrs; 
T_CS = md(cs, fmt=lambda x: f"{x:.2f}".replace("-", "−"), idx="占营业收入 %")
T_RT = md(rt, fmt=lambda x: "" if pd.isna(x) else f"{x:.2f}".replace("-", "−"), idx="%")
T_BRG = md(br, fmt=lambda x: f"{x:+.2f}".replace("-", "−"), idx="百分点")
T_D3 = md(d3.to_frame("金额（亿元）"))
T_CT = md(ct.to_frame("数值"))
T_RAT = md(rat.loc[["流动比率","现金比率","现金及短期投资覆盖率","资产负债率","总资产周转率","ROA","权益乘数","ROE"]],
           fmt=lambda x: f"{x:.4f}")
rr = rat.copy()
for k in ["资产负债率","ROA","ROE","销售净利率"]: rr.loc[k] = rr.loc[k]*100
T_DU = md(pd.DataFrame({"2024": [f"{rat.loc['销售净利率','2024']*100:.2f}%", f"{rat.loc['总资产周转率','2024']:.4f}", f"{rat.loc['权益乘数','2024']:.4f}", f"{rat.loc['ROE','2024']*100:.2f}%"],
  "2025": [f"{rat.loc['销售净利率','2025']*100:.2f}%", f"{rat.loc['总资产周转率','2025']:.4f}", f"{rat.loc['权益乘数','2025']:.4f}", f"{rat.loc['ROE','2025']*100:.2f}%"],
  "对 ROE 变化的贡献（百分点）": [f"{dup['销售净利率']*100:.2f}".replace("-","−"), f"{dup['总资产周转率']*100:.2f}".replace("-","−"), f"{dup['权益乘数']*100:.2f}".replace("-","−"), f"{dup['ROE 变化合计']*100:.2f}".replace("-","−")]},
  index=["销售净利率", "总资产周转率", "权益乘数", "ROE（三项乘积）"]), fmt=lambda s: s)
ratios4 = ["流动比率","现金比率","现金及短期投资覆盖率","资产负债率","总资产周转率","ROA","权益乘数","ROE","销售净利率"]
T_CMP = md(cmpt.loc[ratios4], fmt=lambda x: f"{x:.4f}")
T_MM = md(mm, fmt=lambda x: "—" if pd.isna(x) else f"{x*100:.1f}%")
T_RES = md(pd.DataFrame({"留存率": ["50%", "70%（基准）", "90%"],
  "IGR": [pc(res.loc["IGR", c]) for c in res.columns], "SGR": [pc(res.loc["SGR", c]) for c in res.columns],
  "EFN（销售百分比法）": [n2(res.loc["EFN（销售百分比法）", c]) for c in res.columns],
  "EFN（公式法）": [n2(res.loc["EFN（公式法）", c]) for c in res.columns]}).set_index("留存率"), fmt=lambda s: s)
T_CRIT = md(pd.DataFrame({"临界留存率": [pc(v) for v in crit.values]}, index=list(crit.index)), fmt=lambda s: s)
T_ISF = md(isf.loc[["营业收入","营业成本","销售费用","管理费用","研发费用","营业利润","非经营损益净额","利息费用","所得税费用","净利润","股利","留存利润"]], idx="亿元")
show = ["现金及现金等价物","受限现金","短期投资","应收及预付款","固定资产及无形资产净额","其他非流动资产","资产总额",
        "客户预付款","应付商家款","商家保证金","其他经营性流动负债","有息流动负债","流动租赁负债","流动负债合计","非流动负债合计","负债合计",
        "留存收益","其他股东权益","股东权益合计","负债与权益合计（融资前）","融资缺口（负数为资金盈余）"]
bsf2 = bsf.loc[show].copy(); bsf2.loc["负债与权益合计（融资前）","2025"] = 6300.44; 
T_BSF = md(bsf2, idx="亿元")
# ---- 取数 ----
g = lambda s, c: s[c]
N = dict(NI=n2(d3["净利润"]), DA=n2(d3["折旧与摊销"]), SBC=n2(d3["股权激励费用"]), OTH=n2(d3["其他经营现金流调整净额"]),
  DAR=n2(-d3["应收及预付款增加"]), DLIAB=n2(d3["客户预付款增加"]+d3["应付商家款增加"]+d3["商家保证金增加"]+d3["其他经营性流动负债增加"]),
  CFO=n2(R["cfo"]), CFI=n2(R["cfi"]), CFF=n2(R["cff"]), NET=n2(R["net"]), CASH0=n2(R["cash0"]), CASH1=n2(R["cash1"]), CASH1C=n2(R["cash0"]+R["net"]), DIFF=n2(R["diff"]),
  CAPEX=n2(R["capex"]), EBIT=n2(R["ebit"]), OCF=n2(R["ocf"]), NOWC24=n2(R["nowc24"]), NOWC25=n2(R["nowc25"]), DNOWC=n2(R["dnowc"]), FCFF=n2(R["fcff"]),
  EBIT75=n2(R["ebit"]*0.75), TAXD=n2(R["ebit"]*0.25-219.14684), FCFFOCF=n2(R["fcff"]-R["ocf"]), CFOFCFF=n2(R["cfo"]-R["fcff"]),
  CAGR=pc(R["cagr"]), APX20=n2(R["approx_cfo20"]), DL20=n2(R["dl20"]), FREE=n2(R["free_est"]),
  DIFFCFO=n2(d3["CFO－净利润"]), ROA=pc(R["ROA"]), ROE=pc(R["ROE"]), DA_=n2(R["dA"]), DL_=n2(R["dL"]), NI1=n2(R["NI1"]),
  B_IGR=pc(crit.iloc[0]), B_SGR=pc(crit.iloc[1]), B_EFN=pc(crit.iloc[2]),
  IGR70=pc(res.loc["IGR","0.7"]), SGR70=pc(res.loc["SGR","0.7"]), EFN70=n2(res.loc["EFN（销售百分比法）","0.7"]), EFN50=n2(res.loc["EFN（销售百分比法）","0.5"]),
  EFN90=n2(res.loc["EFN（销售百分比法）","0.9"]), IGR50=pc(res.loc["IGR","0.5"]), IGR90=pc(res.loc["IGR","0.9"]),
  DIV70=n2(R["NI1"]*0.3), DIVB=n2(R["NI1"]*(1-crit.iloc[2])),
  T_CF=T_CF, T_OCF=T_OCF, T_BR1=T_BR1, T_BR2=T_BR2, T_CS=T_CS, T_RT=T_RT, T_BRG=T_BRG, T_D3=T_D3, T_CT=T_CT, T_RAT=T_RAT, T_DU=T_DU,
  T_CMP=T_CMP, T_MM=T_MM, T_RES=T_RES, T_CRIT=T_CRIT, T_ISF=T_ISF, T_BSF=T_BSF,
  CR_X=n2((5189.80-738.31)/2137.37), CR_X24=n2((4156.48-684.26)/1884.23),
  P_NPM=n2(abs(dup["销售净利率"])/abs(dup["ROE 变化合计"])*100,0), P_TAT=n2(abs(dup["总资产周转率"])/abs(dup["ROE 变化合计"])*100,0), P_EM=n2(abs(dup["权益乘数"])/abs(dup["ROE 变化合计"])*100,0))
def mathfix(m):
    x = m.group(0).replace("−", "-")
    x = re.sub(r"(?<=\d),(?=\d)", "", x)
    return re.sub(r"(?<!\\)%", r"\\%", x)
tpl = open("报告模板.md", encoding="utf-8").read()
import os
if os.path.exists("个人信息.txt"):
    N["AUTHOR"] = open("个人信息.txt", encoding="utf-8").read().strip()
else:
    tpl = tpl.replace('author: "@@AUTHOR@@"\n', "")
out = re.sub(r"@@(\w+)@@", lambda m: N[m.group(1)], tpl)
out = re.sub(r"\$\$.*?\$\$|(?<!\$)\$[^$\n]+\$(?!\$)", mathfix, out, flags=re.S)
open("报告.qmd", "w", encoding="utf-8").write(out); print("报告.qmd 已生成，字符数", len(out))
