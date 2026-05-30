import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="HR Attrition Dashboard", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .insight { background: #e8f5e9; border-left: 4px solid #1D9E75; padding: 10px 14px;
               border-radius: 0 8px 8px 0; font-size: 13px; color: #2C2C2A; margin-top: 10px; }
    .section-divider { border: none; border-top: 1.5px solid #e5e3db; margin: 24px 0 16px; }
    .bench-card { background: #f8f9fa; border-radius: 10px; padding: 16px 18px;
                  border-left: 4px solid #378ADD; margin-bottom: 12px; font-size: 13px; }
    .bench-source { font-size: 11px; color: #888; margin-top: 6px; }
    .resume-block { background: #f4f6fb; border: 1.5px solid #378ADD; border-radius: 10px;
                    padding: 20px 24px; margin-bottom: 16px; }
    .resume-title { font-size: 16px; font-weight: 700; color: #2C2C2A; margin-bottom: 4px; }
    .resume-tools { font-size: 12px; color: #378ADD; margin-bottom: 10px; }
    .tag { display: inline-block; background: #e3edf9; color: #378ADD; border-radius: 20px;
           padding: 3px 12px; font-size: 12px; margin: 2px 3px; }
    .ds-badge { display: inline-block; padding: 3px 10px; border-radius: 20px;
                font-size: 11px; font-weight: 600; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Load all datasets ─────────────────────────────────────
@st.cache_data
def load_all():
    ibm = pd.read_csv("hr_attrition_clean_v2.csv")
    ibm['Dataset'] = 'IBM Corp (2016)'
    ibm['RemoteWork'] = 'On-site'
    ibm['StockOptions'] = 0

    tech = pd.read_csv("hr_techco_2024.csv")
    tech['Dataset'] = 'Tech Co (2024)'

    return ibm, tech, pd.concat([ibm, tech], ignore_index=True)

d1, d2, all_data = load_all()

DATASET_META = {
    'IBM Corp (2016)': {'color': '#378ADD', 'employees': len(d1),
                        'note': 'Traditional firm (2016). On-site only. 1,470 employees across Sales, R&D, and HR.'},
    'Tech Co (2024)':  {'color': '#1D9E75', 'employees': len(d2),
                        'note': '2024 tech startup. Hybrid/remote. Stock options. Younger, higher-paid employees.'},
}

DATASETS = {
    'IBM Corp (2016)': d1,
    'Tech Co (2024)':  d2,
}

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=48)
st.sidebar.markdown("## HR Attrition Dashboard")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["📊 Dashboard", "📊 Compare Datasets", "🌍 Benchmarks"])
st.sidebar.markdown("---")

# ── Dataset selector (shown on dashboard pages) ───────────
if page == "📊 Dashboard":
    st.sidebar.markdown("**Dataset**")
    selected_ds = st.sidebar.selectbox("Select company", list(DATASETS.keys()))
    df = DATASETS[selected_ds]
    meta = DATASET_META[selected_ds]

    st.sidebar.markdown("**Filters**")
    dept_opts = df['Department'].unique().tolist()
    dept_filter = st.sidebar.multiselect("Department", dept_opts, default=dept_opts)
    gender_opts = df['Gender'].unique().tolist()
    gender_filter = st.sidebar.multiselect("Gender", gender_opts, default=gender_opts)
    ot_filter = st.sidebar.radio("Overtime", ["All", "Yes", "No"])
    filtered = df[df['Department'].isin(dept_filter) & df['Gender'].isin(gender_filter)]
    if ot_filter != "All":
        filtered = filtered[filtered['OverTime'] == ot_filter]

st.sidebar.markdown("---")
st.sidebar.caption("Built by Thanakhan Kongkoet\nPython · Streamlit · Plotly")

# ════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    badge_color = meta['color']
    st.title("📊 HR Attrition Analytics Dashboard")
    st.markdown(f'<span class="ds-badge" style="background:{badge_color}22; color:{badge_color}; border: 1px solid {badge_color}">🏢 {selected_ds}</span>', unsafe_allow_html=True)
    st.caption(meta['note'])

    rate = filtered['AttritionBinary'].mean() * 100
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Employees", f"{len(filtered):,}")
    with col2: st.metric("Attrition Rate", f"{rate:.1f}%")
    with col3: st.metric("Avg Monthly Income", f"${filtered['MonthlyIncome'].mean():,.0f}")
    with col4: st.metric("Overtime Workers", f"{(filtered['OverTime']=='Yes').mean()*100:.1f}%")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Attrition drivers")
    col1, col2 = st.columns(2)

    with col1:
        d = filtered.groupby('Department')['AttritionBinary'].mean().mul(100).reset_index()
        d.columns = ['Department','Attrition Rate (%)']
        fig = px.bar(d, x='Attrition Rate (%)', y='Department', orientation='h',
                     color='Attrition Rate (%)', color_continuous_scale=['#B5D4F4','#E24B4A'],
                     title="By department")
        fig.update_layout(height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        d = filtered.groupby('OverTime')['AttritionBinary'].mean().mul(100).reset_index()
        d.columns = ['Overtime','Attrition Rate (%)']
        fig = px.bar(d, x='Overtime', y='Attrition Rate (%)',
                     color='Overtime', color_discrete_map={'Yes':'#E24B4A','No':'#1D9E75'},
                     title="Overtime vs. attrition")
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        d = filtered.groupby('AgeGroup', observed=True)['AttritionBinary'].mean().mul(100).reset_index()
        d.columns = ['Age Group','Attrition Rate (%)']
        fig = px.bar(d, x='Age Group', y='Attrition Rate (%)',
                     color='Attrition Rate (%)', color_continuous_scale=['#B5D4F4','#E24B4A'],
                     title="By age group")
        fig.update_layout(height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        d = filtered.groupby('JobSatisfaction')['AttritionBinary'].mean().mul(100).reset_index()
        d.columns = ['Job Satisfaction (1–4)','Attrition Rate (%)']
        fig = px.line(d, x='Job Satisfaction (1–4)', y='Attrition Rate (%)', markers=True,
                      title="Job satisfaction vs. attrition", color_discrete_sequence=['#E24B4A'])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Income & work-life balance")
    col5, col6 = st.columns(2)

    with col5:
        fig = px.histogram(filtered, x='MonthlyIncome', color='Attrition',
                           color_discrete_map={'Yes':'#E24B4A','No':'#378ADD'},
                           barmode='overlay', opacity=0.7, title="Income distribution")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        li = filtered[filtered['Attrition']=='Yes']['MonthlyIncome'].mean()
        si = filtered[filtered['Attrition']=='No']['MonthlyIncome'].mean()
        st.markdown(f'<div class="insight">Left avg: ${li:,.0f} · Stayed avg: ${si:,.0f} · Gap: ${si-li:,.0f}/month</div>', unsafe_allow_html=True)

    with col6:
        d = filtered.groupby('WorkLifeBalance')['AttritionBinary'].mean().mul(100).reset_index()
        d.columns = ['WLB Score','Attrition Rate (%)']
        d['Label'] = ['1 (Bad)','2 (Good)','3 (Better)','4 (Best)']
        fig = px.bar(d, x='Label', y='Attrition Rate (%)',
                     color='Attrition Rate (%)', color_continuous_scale=['#1D9E75','#E24B4A'],
                     title="Work-life balance vs. attrition")
        fig.update_layout(height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Department × Satisfaction heatmap")
    pivot = filtered.groupby(['Department','JobSatisfaction'])['AttritionBinary'].mean().mul(100).reset_index()
    pivot.columns = ['Department','Job Satisfaction','Attrition Rate (%)']
    fig = px.density_heatmap(pivot, x='Job Satisfaction', y='Department',
                             z='Attrition Rate (%)', color_continuous_scale='RdYlGn_r',
                             title="Highest-risk combinations", text_auto='.0f')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    # Remote work chart only for Tech Co
    if 'RemoteWork' in filtered.columns and selected_ds == 'Tech Co (2024)':
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.subheader("Tech Co extras")
        col7, col8 = st.columns(2)
        with col7:
            d = filtered.groupby('RemoteWork')['AttritionBinary'].mean().mul(100).reset_index()
            d.columns = ['Work Mode','Attrition Rate (%)']
            fig = px.bar(d, x='Work Mode', y='Attrition Rate (%)',
                         color='Work Mode', color_discrete_map={'Remote':'#1D9E75','Hybrid':'#378ADD','On-site':'#E24B4A'},
                         title="Remote work vs. attrition")
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="insight">On-site employees show the highest attrition — consistent with 2024 Stanford research showing hybrid work cuts voluntary attrition by 33%.</div>', unsafe_allow_html=True)
        with col8:
            d = filtered.groupby('StockOptions')['AttritionBinary'].mean().mul(100).reset_index()
            d.columns = ['Stock Option Level','Attrition Rate (%)']
            fig = px.line(d, x='Stock Option Level', y='Attrition Rate (%)', markers=True,
                          title="Stock options vs. attrition", color_discrete_sequence=['#1D9E75'])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="insight">Employees with no stock options are significantly more likely to leave — equity is a strong long-term retention tool in tech.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("🚨 High-risk segment")
    high_risk = filtered[
        (filtered['OverTime']=='Yes') &
        (filtered['JobSatisfaction']<=2) &
        (filtered['Age']<30)
    ]
    cols_show = ['Age','Department','JobRole','MonthlyIncome','OverTime','JobSatisfaction','WorkLifeBalance','Attrition']
    cols_show = [c for c in cols_show if c in high_risk.columns]
    st.caption(f"{len(high_risk)} employees flagged — under 30, overtime, satisfaction ≤ 2")
    st.dataframe(high_risk[cols_show].head(20), use_container_width=True)

# ════════════════════════════════════════════════════════
# PAGE: COMPARE DATASETS
# ════════════════════════════════════════════════════════
elif page == "📊 Compare Datasets":
    st.title("📊 Dataset Comparison")
    st.caption("Side-by-side comparison of all three company profiles")

    # Summary metrics
    st.subheader("At a glance")
    col1, col2, col3 = st.columns(3)
    for col, (name, ds) in zip([col1, col2, col3], DATASETS.items()):
        meta = DATASET_META[name]
        with col:
            st.markdown(f'<span class="ds-badge" style="background:{meta["color"]}22; color:{meta["color"]}; border:1px solid {meta["color"]}">{name}</span>', unsafe_allow_html=True)
            st.metric("Employees", f"{len(ds):,}")
            st.metric("Attrition Rate", f"{ds['AttritionBinary'].mean()*100:.1f}%")
            st.metric("Avg Income", f"${ds['MonthlyIncome'].mean():,.0f}/mo")
            st.metric("Overtime %", f"{(ds['OverTime']=='Yes').mean()*100:.1f}%")
            st.caption(meta['note'])

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Attrition rate comparison")

    # Overall attrition bar
    summary = pd.DataFrame([{
        'Company': name,
        'Attrition Rate (%)': round(ds['AttritionBinary'].mean()*100, 1),
        'Color': DATASET_META[name]['color']
    } for name, ds in DATASETS.items()])
    fig = px.bar(summary, x='Company', y='Attrition Rate (%)',
                 color='Company', color_discrete_map={n: DATASET_META[n]['color'] for n in DATASETS},
                 text='Attrition Rate (%)', title="Overall attrition rate by company")
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(height=350, showlegend=False, yaxis_range=[0, 40])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Overtime impact (across all companies)")
    ot_rows = []
    for name, ds in DATASETS.items():
        for ot_val in ['Yes', 'No']:
            sub = ds[ds['OverTime'] == ot_val]
            ot_rows.append({'Company': name, 'Overtime': ot_val,
                            'Attrition Rate (%)': round(sub['AttritionBinary'].mean()*100, 1)})
    ot_df = pd.DataFrame(ot_rows)
    fig = px.bar(ot_df, x='Company', y='Attrition Rate (%)', color='Overtime', barmode='group',
                 color_discrete_map={'Yes':'#E24B4A','No':'#1D9E75'},
                 title="Overtime vs. attrition — all companies")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight">Overtime consistently drives attrition across all three datasets — making it a universal risk factor regardless of company type, era, or industry.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Job satisfaction impact (across all companies)")
    sat_rows = []
    for name, ds in DATASETS.items():
        for score in [1, 2, 3, 4]:
            sub = ds[ds['JobSatisfaction'] == score]
            sat_rows.append({'Company': name, 'Satisfaction': score,
                             'Attrition Rate (%)': round(sub['AttritionBinary'].mean()*100, 1)})
    sat_df = pd.DataFrame(sat_rows)
    fig = px.line(sat_df, x='Satisfaction', y='Attrition Rate (%)', color='Company',
                  markers=True, color_discrete_map={n: DATASET_META[n]['color'] for n in DATASETS},
                  title="Satisfaction vs. attrition — all companies")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight">All three companies show the same downward trend: higher satisfaction = lower attrition. The Tech Co (2024) starts at a higher baseline but drops steeply — suggesting satisfaction has an even stronger retention effect in tech roles.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Age group attrition (across all companies)")
    age_rows = []
    for name, ds in DATASETS.items():
        for grp in ['Under 25','25–34','35–44','45+']:
            sub = ds[ds['AgeGroup']==grp]
            if len(sub) > 0:
                age_rows.append({'Company': name, 'Age Group': grp,
                                 'Attrition Rate (%)': round(sub['AttritionBinary'].mean()*100, 1)})
    age_df = pd.DataFrame(age_rows)
    fig = px.bar(age_df, x='Age Group', y='Attrition Rate (%)', color='Company', barmode='group',
                 color_discrete_map={n: DATASET_META[n]['color'] for n in DATASETS},
                 title="Age group attrition — all companies")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight">The Tech Co shows notably higher attrition in the 25–34 bracket — this is the most mobile career stage in tech, where engineers receive heavy external recruitment pressure. The traditional companies show steeper cliffs at under 25.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Income gap: left vs. stayed")
    gap_rows = []
    for name, ds in DATASETS.items():
        left = ds[ds['Attrition']=='Yes']['MonthlyIncome'].mean()
        stayed = ds[ds['Attrition']=='No']['MonthlyIncome'].mean()
        gap_rows.append({'Company': name, 'Group': 'Left', 'Avg Income ($)': round(left)})
        gap_rows.append({'Company': name, 'Group': 'Stayed', 'Avg Income ($)': round(stayed)})
    gap_df = pd.DataFrame(gap_rows)
    fig = px.bar(gap_df, x='Company', y='Avg Income ($)', color='Group', barmode='group',
                 color_discrete_map={'Left':'#E24B4A','Stayed':'#378ADD'},
                 title="Income gap between employees who left vs. stayed")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight">The income gap is widest at the Tech Co — employees who left earned significantly less than those who stayed. In tech, where salary data is highly transparent, compensation competitiveness has a direct impact on retention.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# PAGE: BENCHMARKS
# ════════════════════════════════════════════════════════
elif page == "🌍 Benchmarks":
    st.title("🌍 Industry Benchmark Comparison")
    st.caption("Comparing our datasets against real-world 2024–2025 HR industry reports")
    st.info("**Why this matters:** Benchmarks tell you whether a company's attrition is a company-specific problem or an industry-wide trend — a critical distinction for any HR recommendation.")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Attrition rate vs. global benchmarks")

    bench = pd.DataFrame({
        'Source': ['IBM Corp (2016)', 'Tech Co (2024)',
                   'Mercer 2024 (predicted)', 'SHRM 2024 (voluntary)', 'Healthy target (<10%)'],
        'Rate (%)': [
            round(d1['AttritionBinary'].mean()*100, 1),
            round(d2['AttritionBinary'].mean()*100, 1),
            20.0, 23.0, 10.0
        ],
        'Type': ['Our Data','Our Data','Benchmark','Benchmark','Target']
    })
    fig = px.bar(bench, x='Source', y='Rate (%)', color='Type',
                 color_discrete_map={'Our Data':'#378ADD','Benchmark':'#888780','Target':'#1D9E75'},
                 text='Rate (%)', title="Attrition: our data vs. benchmarks")
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=380, yaxis_range=[0, 38])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div class="bench-card">
        Mercer's 2024 Global Talent Trends predicted ~20% average turnover. SHRM reports voluntary
        attrition averaged 23% in 2024. Our IBM-style datasets (23–24%) sit within the normal range.
        The Tech Co at 28.4% is elevated but consistent with tech sector norms, where competition
        for talent is highest.
        <div class="bench-source">Sources: Mercer Global Talent Trends 2024 · SHRM 2024 · AIHR 2026</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Employee engagement (Gallup 2025)")
    gallup = pd.DataFrame({
        'Category': ['Engaged (21%)', 'Not Engaged (62%)', 'Actively Disengaged (15%)', 'Our Dataset\nSatisfied (score ≥3)'],
        'Percentage': [21, 62, 15, round((d1['JobSatisfaction']>=3).mean()*100, 0)],
        'Type': ['Global','Global','Global','Our Data']
    })
    fig = px.bar(gallup, x='Category', y='Percentage', color='Type',
                 color_discrete_map={'Global':'#888780','Our Data':'#378ADD'},
                 text='Percentage', title="Global engagement breakdown — Gallup 2025 report")
    fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
    fig.update_layout(height=350, showlegend=False, yaxis_range=[0, 80])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div class="bench-card">
        Gallup's 2025 report found global employee engagement fell to 21% in 2024 — down from 23%
        in 2023 — costing an estimated $438 billion in lost global productivity. Manager engagement
        dropped sharpest, from 30% to 27% in one year.
        <div class="bench-source">Source: Gallup State of the Global Workplace 2025</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Industry turnover rates (BambooHR 2024–2025)")
    industry = pd.DataFrame({
        'Industry': ['Travel & Hospitality','Retail & Sales','Technology','Healthcare',
                     'Professional Services','Finance','Education','Government'],
        'Annualised Rate (%)': [33.6, 28.8, 25.2, 24.0, 22.8, 20.4, 21.6, 16.8]
    })
    fig = px.bar(industry.sort_values('Annualised Rate (%)'), x='Annualised Rate (%)', y='Industry',
                 orientation='h', color='Annualised Rate (%)', color_continuous_scale=['#B5D4F4','#E24B4A'],
                 text='Annualised Rate (%)', title="Annualised attrition by industry")
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(height=400, coloraxis_showscale=False, xaxis_range=[0, 44])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Cost of attrition calculator")
    sel = st.selectbox("Select company to estimate", list(DATASETS.keys()))
    dsel = DATASETS[sel]
    rate_sel = dsel['AttritionBinary'].mean()
    avg_sal = dsel['MonthlyIncome'].mean() * 12
    n_left = int(len(dsel) * rate_sel)
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Employees who left", f"{n_left:,}")
    with col2: st.metric("Est. cost (low, 50%)", f"${n_left * avg_sal * 0.5 / 1e6:.1f}M")
    with col3: st.metric("Est. cost (high, 200%)", f"${n_left * avg_sal * 2.0 / 1e6:.1f}M")
    st.markdown(f"""
    <div class="bench-card">
        Based on Gallup's formula (50–200% of annual salary per departure),
        <strong>{sel}</strong> with {n_left} departures and avg salary ${avg_sal:,.0f}/year
        faces an estimated annual attrition cost of
        <strong>${n_left*avg_sal*0.5/1e6:.1f}M – ${n_left*avg_sal*2.0/1e6:.1f}M</strong>.
        <div class="bench-source">Source: Gallup — The Cost of Employee Turnover</div>
    </div>
    """, unsafe_allow_html=True)
