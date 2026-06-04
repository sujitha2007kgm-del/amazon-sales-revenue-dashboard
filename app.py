import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Amazon Sales & Revenue Analytics", layout="wide", page_icon="📦")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700;800&family=DM+Mono&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background:#0f1117; color:#c8d0e0; }
.main { background:#0f1117; }
.block-container { padding: 2rem 2.5rem; }
section[data-testid="stSidebar"] { background:#1a1f2e; border-right:1px solid #2a3040; }
section[data-testid="stSidebar"] * { color:#c8d0e0 !important; }
.kpi { background:linear-gradient(135deg,#1a1f2e,#252b3b); border-radius:16px; padding:20px 24px; border-left:4px solid; margin-bottom:8px; }
.kpi-label { font-size:11px; text-transform:uppercase; letter-spacing:1.2px; color:#8892a4; margin-bottom:6px; }
.kpi-value { font-family:'DM Mono',monospace; font-size:26px; font-weight:800; letter-spacing:-1px; }
.stTabs [data-baseweb="tab-list"] { background:#1a1f2e; border-radius:12px; padding:4px; gap:4px; }
.stTabs [data-baseweb="tab"] { border-radius:10px; color:#8892a4; font-weight:600; font-size:13px; }
.stTabs [aria-selected="true"] { background:#00C9A7 !important; color:#0f1117 !important; }
.section-title { font-size:15px; font-weight:700; color:#c8d0e0; padding-bottom:8px; border-bottom:1px solid #2a3040; margin-bottom:14px; }
.insight { background:#1a1f2e; border-radius:12px; padding:14px 16px; margin-bottom:10px; border-left:4px solid; }
.cat-card { background:#252b3b; border-radius:12px; padding:16px; margin-bottom:10px; border-left:4px solid; }

</style>
""", unsafe_allow_html=True)

PAL = ["#00C9A7","#FF6B6B","#4ECDC4","#FFE66D","#A78BFA","#F97316","#38BDF8","#FB7185"]
DL  = dict(
    paper_bgcolor="#1a1f2e", plot_bgcolor="#1a1f2e",
    font=dict(family="DM Sans", color="#c8d0e0", size=12),
    xaxis=dict(gridcolor="#2a3040", tickfont_color="#8892a4"),
    yaxis=dict(gridcolor="#2a3040", tickfont_color="#8892a4"),
    margin=dict(l=10,r=10,t=36,b=10),
    legend=dict(bgcolor="#252b3b", bordercolor="#2a3040")
)

SAMPLE = pd.DataFrame([
    {"product_name":"Echo Dot (5th Gen)","category":"Electronics|Smart Speakers","discounted_price":"3499","actual_price":"4999","discount_percentage":"30","rating":"4.5","rating_count":"12450"},
    {"product_name":"Fire TV Stick 4K","category":"Electronics|Streaming","discounted_price":"3999","actual_price":"5999","discount_percentage":"33","rating":"4.3","rating_count":"8920"},
    {"product_name":"Boat Airdopes 141","category":"Electronics|Earbuds","discounted_price":"1299","actual_price":"4990","discount_percentage":"74","rating":"3.9","rating_count":"25600"},
    {"product_name":"Himalaya Face Wash","category":"Beauty|Face Care","discounted_price":"99","actual_price":"130","discount_percentage":"24","rating":"4.2","rating_count":"5400"},
    {"product_name":"Milton Thermosteel","category":"Kitchen|Bottles","discounted_price":"649","actual_price":"999","discount_percentage":"35","rating":"4.4","rating_count":"3200"},
    {"product_name":"Prestige Induction","category":"Kitchen|Appliances","discounted_price":"1799","actual_price":"2495","discount_percentage":"28","rating":"4.1","rating_count":"7800"},
    {"product_name":"Wildcraft Backpack","category":"Bags|Backpacks","discounted_price":"999","actual_price":"1999","discount_percentage":"50","rating":"4.0","rating_count":"1900"},
    {"product_name":"Mamaearth Vitamin C","category":"Beauty|Serums","discounted_price":"349","actual_price":"599","discount_percentage":"42","rating":"4.6","rating_count":"11200"},
    {"product_name":"JBL Flip 6","category":"Electronics|Speakers","discounted_price":"7999","actual_price":"11999","discount_percentage":"33","rating":"4.5","rating_count":"4500"},
    {"product_name":"Samsung 43 Smart TV","category":"Electronics|Televisions","discounted_price":"28990","actual_price":"42900","discount_percentage":"32","rating":"4.2","rating_count":"6700"},
    {"product_name":"Usha Mixer Grinder","category":"Kitchen|Appliances","discounted_price":"2299","actual_price":"3495","discount_percentage":"34","rating":"4.3","rating_count":"9100"},
    {"product_name":"Skybags Duffle Bag","category":"Bags|Travel","discounted_price":"1199","actual_price":"2499","discount_percentage":"52","rating":"3.8","rating_count":"2300"},
    {"product_name":"Lakme Eyeconic Kajal","category":"Beauty|Eyes","discounted_price":"219","actual_price":"275","discount_percentage":"20","rating":"4.4","rating_count":"18700"},
    {"product_name":"Pigeon Pressure Cooker","category":"Kitchen|Cookware","discounted_price":"799","actual_price":"1295","discount_percentage":"38","rating":"4.1","rating_count":"5600"},
    {"product_name":"Redmi Buds 4","category":"Electronics|Earbuds","discounted_price":"1499","actual_price":"2999","discount_percentage":"50","rating":"4.0","rating_count":"14200"},
])

def clean(df):
    df = df.copy()
    for c in ["discounted_price","actual_price"]:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(r"[₹,]","",regex=True), errors="coerce")
    df["discount_percentage"] = pd.to_numeric(df["discount_percentage"].astype(str).str.replace("%","",regex=False), errors="coerce")
    df["rating"]       = pd.to_numeric(df["rating"], errors="coerce")
    df["rating_count"] = pd.to_numeric(df["rating_count"].astype(str).str.replace(",","",regex=False), errors="coerce").fillna(0)
    df["main_category"] = df["category"].astype(str).str.split("|").str[0].str.strip()
    df["savings"] = df["actual_price"] - df["discounted_price"]
    return df.dropna(subset=["discounted_price","actual_price"])

def fmt(n):
    if n >= 1e7: return f"Rs.{n/1e7:.1f}Cr"
    if n >= 1e5: return f"Rs.{n/1e5:.1f}L"
    return f"Rs.{n:,.0f}"

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Amazon Intelligence")
    st.markdown("---")

    st.markdown("### 📥 Import Data")

    # ── DATA IMPORT: CSV or Excel ─────────────────────────────────────────────
    uploaded = st.file_uploader("Upload CSV or Excel file", type=["csv","xlsx","xls"])
    if uploaded:
        try:
            if uploaded.name.endswith((".xlsx",".xls")):
                df_raw = pd.read_excel(uploaded)
            else:
                df_raw = pd.read_csv(uploaded)
            df = clean(df_raw)
            st.success(f"✅ Loaded {len(df)} products from **{uploaded.name}**")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            df = clean(SAMPLE)
    else:
        df = clean(SAMPLE)
        st.info(f"📋 Using {len(df)} built-in sample products")
        st.caption("Upload your own CSV/Excel to analyse real data.")

    st.markdown("### 🔍 Filters & Slicers")
    cats = ["All"] + sorted(df["main_category"].dropna().unique().tolist())
    sel_cat  = st.selectbox("Category Slicer", cats)
    min_rat  = st.slider("Min Rating", 0.0, 5.0, 0.0, 0.5)
    max_dis  = st.slider("Max Discount %", 0, 100, 100, 5)
    price_min, price_max = int(df["discounted_price"].min()), int(df["discounted_price"].max())
    price_range = st.slider("Price Range (Rs.)", price_min, price_max, (price_min, price_max), step=50)

    sort_map = {"Rating":"rating","Discount %":"discount_percentage","Price":"discounted_price","Reviews":"rating_count","Savings":"savings"}
    sort_lbl = st.selectbox("Sort Products By", list(sort_map.keys()))
    sort_col = sort_map[sort_lbl]

# ─── FILTER DATA ──────────────────────────────────────────────────────────────
f = df.copy()
if sel_cat != "All":
    f = f[f["main_category"] == sel_cat]
f = f[
    (f["rating"] >= min_rat) &
    (f["discount_percentage"] <= max_dis) &
    (f["discounted_price"] >= price_range[0]) &
    (f["discounted_price"] <= price_range[1])
]

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-bottom:24px'>
  <div style='font-size:28px;font-weight:800;color:#fff;'>📦 Amazon Sales Intelligence Dashboard</div>
  <div style='font-size:13px;color:#5a6478;margin-top:4px'>{len(f)} products &nbsp;·&nbsp; {f['main_category'].nunique()} categories</div>
</div>""", unsafe_allow_html=True)

# ─── KPI CARDS ────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
kpis = [
    (c1,"Total Products",str(len(f)),"#00C9A7","📦"),
    (c2,"Catalog Value",fmt(f["actual_price"].sum()),"#38BDF8","💰"),
    (c3,"Avg Rating",f"{f['rating'].mean():.2f} ⭐" if len(f) else "N/A","#FFE66D","⭐"),
    (c4,"Avg Discount",f"{f['discount_percentage'].mean():.1f}%" if len(f) else "N/A","#A78BFA","🏷️"),
    (c5,"Total Savings",fmt(f["savings"].sum()),"#FF6B6B","💸"),
]
for col,label,val,color,icon in kpis:
    with col:
        st.markdown(f'<div class="kpi" style="border-left-color:{color}"><div class="kpi-label">{icon} {label}</div><div class="kpi-value" style="color:{color}">{val}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4 = st.tabs(["📊 Overview","🛒 Products","🗂️ Categories","💡 Insights"])

# ══ TAB 1 – OVERVIEW ══════════════════════════════════════════════════════════
with tab1:
    cat_df = f.groupby("main_category").agg(
        count=("product_name","count"),
        revenue=("discounted_price","sum"),
        avg_rating=("rating","mean")
    ).reset_index().sort_values("count",ascending=False)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Products by Category</div>', unsafe_allow_html=True)
        fig = px.bar(cat_df,x="main_category",y="count",color="main_category",
                     color_discrete_sequence=PAL,labels={"main_category":"","count":"Products"})
        fig.update_layout(**DL,showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        st.markdown('<div class="section-title">Discount Distribution</div>', unsafe_allow_html=True)
        lbls = ["0-20%","21-40%","41-60%","61-80%","81-100%"]
        f["disc_bucket"] = pd.cut(f["discount_percentage"],[0,20,40,60,80,100],labels=lbls,include_lowest=True)
        pie_df = f["disc_bucket"].value_counts().reset_index()
        pie_df.columns = ["Bucket","Count"]
        fig2 = px.pie(pie_df,names="Bucket",values="Count",hole=0.45,color_discrete_sequence=PAL)
        fig2.update_layout(**DL)
        st.plotly_chart(fig2,use_container_width=True)

    col3,col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-title">Rating vs Discount Scatter</div>', unsafe_allow_html=True)
        fig3 = px.scatter(f,x="discount_percentage",y="rating",color="main_category",
                          hover_name="product_name",color_discrete_sequence=PAL,opacity=0.75,
                          labels={"discount_percentage":"Discount %","rating":"Rating"})
        fig3.update_layout(**DL)
        st.plotly_chart(fig3,use_container_width=True)
    with col4:
        st.markdown('<div class="section-title">Avg Rating by Category</div>', unsafe_allow_html=True)
        fig4 = px.bar(cat_df.sort_values("avg_rating"),x="avg_rating",y="main_category",
                      orientation="h",color="avg_rating",
                      color_continuous_scale=["#FF6B6B","#FFE66D","#00C9A7"],range_color=[0,5],
                      labels={"avg_rating":"Avg Rating","main_category":""})
        fig4.update_layout(**DL,coloraxis_showscale=False)
        st.plotly_chart(fig4,use_container_width=True)

    # Revenue Trend (simulated using index as time proxy)
    st.markdown('<div class="section-title">Revenue Trend (Cumulative by Product)</div>', unsafe_allow_html=True)
    trend_df = f.sort_values("discounted_price",ascending=False).reset_index(drop=True)
    trend_df["cumulative_revenue"] = trend_df["discounted_price"].cumsum()
    fig_trend = px.area(trend_df, x=trend_df.index, y="cumulative_revenue",
                        color_discrete_sequence=["#00C9A7"],
                        labels={"x":"Product Index","cumulative_revenue":"Cumulative Revenue (Rs.)"})
    fig_trend.update_layout(**DL)
    fig_trend.update_traces(fill="tozeroy", line_color="#00C9A7", fillcolor="rgba(0,201,167,0.15)")
    st.plotly_chart(fig_trend,use_container_width=True)

# ══ TAB 2 – PRODUCTS ══════════════════════════════════════════════════════════
with tab2:
    top10 = f.sort_values(sort_col,ascending=False).head(10)
    col1,col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="section-title">Top 10 by {sort_lbl}</div>', unsafe_allow_html=True)
        fig5 = px.bar(top10.sort_values(sort_col),x=sort_col,y="product_name",
                      orientation="h",color=sort_col,
                      color_continuous_scale=["#A78BFA","#00C9A7"],
                      labels={sort_col:sort_lbl,"product_name":""})
        fig5.update_layout(**DL,coloraxis_showscale=False)
        st.plotly_chart(fig5,use_container_width=True)
    with col2:
        st.markdown('<div class="section-title">Price vs Savings Bubble</div>', unsafe_allow_html=True)
        fig6 = px.scatter(f.head(60),x="actual_price",y="discounted_price",
                          size="discount_percentage",color="main_category",
                          hover_name="product_name",color_discrete_sequence=PAL,opacity=0.8,
                          labels={"actual_price":"Actual Price","discounted_price":"Sale Price"})
        fig6.update_layout(**DL)
        st.plotly_chart(fig6,use_container_width=True)

    st.markdown('<div class="section-title">Product Details Table (Sortable)</div>', unsafe_allow_html=True)
    tbl = top10[["product_name","main_category","discounted_price","actual_price","discount_percentage","rating","rating_count","savings"]].copy()
    tbl.columns = ["Product","Category","Sale Price","Actual Price","Discount %","Rating","Reviews","Savings"]
    st.dataframe(
        tbl.style
           .format({"Sale Price":"Rs.{:,.0f}","Actual Price":"Rs.{:,.0f}","Discount %":"{:.1f}%","Rating":"{:.1f}","Reviews":"{:,.0f}","Savings":"Rs.{:,.0f}"})
           .background_gradient(subset=["Rating"],cmap="RdYlGn",vmin=0,vmax=5)
           .background_gradient(subset=["Discount %"],cmap="Blues")
           .background_gradient(subset=["Savings"],cmap="Greens"),
        use_container_width=True, height=380
    )

    # ── Export (CSV & Excel) ──────────────────────────────────────────────────
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button("⬇️ Download Filtered CSV", f.to_csv(index=False).encode(), "filtered_data.csv","text/csv")
    with col_dl2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            f.drop(columns=["disc_bucket"],errors="ignore").to_excel(w,index=False,sheet_name="Products")
        st.download_button("⬇️ Download as Excel", buf.getvalue(), "filtered_data.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ══ TAB 3 – CATEGORIES ════════════════════════════════════════════════════════
with tab3:
    cat2 = f.groupby("main_category").agg(
        count=("product_name","count"),
        revenue=("discounted_price","sum"),
        avg_rating=("rating","mean"),
        avg_discount=("discount_percentage","mean"),
        total_savings=("savings","sum")
    ).reset_index().sort_values("revenue",ascending=False)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Revenue by Category</div>', unsafe_allow_html=True)
        fig7 = px.bar(cat2,x="main_category",y="revenue",color="main_category",
                      color_discrete_sequence=PAL,text=cat2["revenue"].apply(fmt),
                      labels={"main_category":"","revenue":"Revenue"})
        fig7.update_traces(textposition="outside")
        fig7.update_layout(**DL,showlegend=False)
        st.plotly_chart(fig7,use_container_width=True)
    with col2:
        st.markdown('<div class="section-title">Avg Discount % by Category</div>', unsafe_allow_html=True)
        fig8 = px.bar(cat2.sort_values("avg_discount",ascending=False),
                      x="avg_discount",y="main_category",orientation="h",
                      color="avg_discount",color_continuous_scale=["#38BDF8","#A78BFA"],
                      labels={"avg_discount":"Avg Discount %","main_category":""})
        fig8.update_layout(**DL,coloraxis_showscale=False)
        st.plotly_chart(fig8,use_container_width=True)

    st.markdown('<div class="section-title">Category Performance Radar</div>', unsafe_allow_html=True)
    top5 = cat2.head(5)
    fig9 = go.Figure()
    for i,(_, row) in enumerate(top5.iterrows()):
        vals = [row["count"], row["avg_rating"]*20, row["avg_discount"]]
        fig9.add_trace(go.Scatterpolar(
            r=vals+[vals[0]],
            theta=["Products","Avg Rating","Avg Discount","Products"],
            fill="toself", name=row["main_category"],
            line_color=PAL[i%len(PAL)], fillcolor=PAL[i%len(PAL)], opacity=0.2
        ))
    fig9.update_layout(**DL,
        polar=dict(bgcolor="#1a1f2e",
                   radialaxis=dict(gridcolor="#2a3040",tickfont_color="#8892a4"),
                   angularaxis=dict(gridcolor="#2a3040",tickfont_color="#c8d0e0")),
        height=420)
    st.plotly_chart(fig9,use_container_width=True)

    st.markdown('<div class="section-title">Category Summary Cards</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(cat2),4))
    for idx,(_, row) in enumerate(cat2.iterrows()):
        color = PAL[idx%len(PAL)]
        with cols[idx%4]:
            st.markdown(f'''
            <div class="cat-card" style="border-left-color:{color}">
              <div style="font-size:13px;font-weight:700;color:#fff;margin-bottom:8px">{row["main_category"]}</div>
              <div style="font-size:12px;color:#8892a4">Products: <b style="color:{color}">{int(row["count"])}</b></div>
              <div style="font-size:12px;color:#8892a4">Avg Rating: <b style="color:#FFE66D">{row["avg_rating"]:.2f}</b></div>
              <div style="font-size:12px;color:#8892a4">Revenue: <b style="color:#00C9A7">{fmt(row["revenue"])}</b></div>
              <div style="font-size:12px;color:#8892a4">Savings: <b style="color:#FF6B6B">{fmt(row["total_savings"])}</b></div>
            </div>''', unsafe_allow_html=True)

# ══ TAB 4 – INSIGHTS ══════════════════════════════════════════════════════════
with tab4:
    col1,col2 = st.columns(2)
    groups = [
        ("🏆 Best Value Products","Rating ≥ 4 & Discount ≥ 30%",
         f[(f["rating"]>=4)&(f["discount_percentage"]>=30)]
           .assign(score=lambda x:x["discount_percentage"]+x["rating"]*10)
           .sort_values("score",ascending=False).head(6),
         "#00C9A7", lambda r:f"{r['discount_percentage']:.0f}% off", col1),
        ("⚠️ Overpriced Products","Rating < 3.5 & Discount < 20%",
         f[(f["rating"]<3.5)&(f["discount_percentage"]<20)]
           .sort_values("actual_price",ascending=False).head(6),
         "#FF6B6B", lambda r:fmt(r["actual_price"]), col2),
        ("💎 Premium Products","Price ≥ Rs.5000 & Rating ≥ 4",
         f[(f["actual_price"]>=5000)&(f["rating"]>=4)]
           .sort_values("actual_price",ascending=False).head(6),
         "#A78BFA", lambda r:fmt(r["actual_price"]), col1),
        ("🔥 Viral Products","Most Reviewed",
         f.sort_values("rating_count",ascending=False).head(6),
         "#FFE66D", lambda r:f"{int(r['rating_count']):,} reviews", col2),
    ]
    for title,desc,df_ins,color,badge,col in groups:
        with col:
            st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
            st.caption(desc)
            if df_ins.empty:
                st.info("No products match current filters.")
            else:
                for _,row in df_ins.iterrows():
                    name = row["product_name"][:42]+("..." if len(row["product_name"])>42 else "")
                    st.markdown(f'''
                    <div class="insight" style="border-left-color:{color}">
                      <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                          <div style="font-size:13px;font-weight:600;color:#c8d0e0">{name}</div>
                          <div style="font-size:11px;color:#5a6478">{row["main_category"]} · {row["rating"]:.1f} stars</div>
                        </div>
                        <div style="font-size:14px;font-weight:700;color:{color};font-family:monospace">{badge(row)}</div>
                      </div>
                    </div>''', unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown(f"<div style='text-align:center;font-size:11px;color:#2a3040;margin-top:40px'>Amazon Sales & Revenue analytics· {len(f)} products · Sales & Revenue Analysis Dashboard</div>", unsafe_allow_html=True)