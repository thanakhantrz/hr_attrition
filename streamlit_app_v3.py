import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="HR Attrition Dashboard", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .insight { background: #e8f5e9; border-left: 4px solid #1D9E75; padding: 10px 14px;
               border-radius: 0 8px 8px 0; font-size: 13px; color: #2C2C2A; margin-top: 10px; }
    .resume-box { background: #f4f6fb; border: 1.5px solid #378ADD; border-radius: 10px;
                  padding: 20px 24px; margin-bottom: 18px; }
    .resume-title { font-size: 17px; font-weight: 700; color: #2C2C2A; margin-bottom: 4px; }
    .resume-tools { font-size: 13px; color: #378ADD; margin-bottom: 12px; }
    .resume-bullet { font-size: 13px; color: #3a3a3a; line-height: 2; }
    .tag { display: inline-block; background: #e3edf9; color: #378ADD; border-radius: 20px;
           padding: 3px 12px; font-size: 12px; margin: 2px 3px; }
    .section-divider { border: none; border-top: 1.5px solid #e5e3db; margin: 28px 0 18px; }
    .about-text { font-size: 13px; color: #555; line-height: 1.8; }
    .bench-card { background: #f8f9fa; border-radius: 10px; padding: 16px 18px;
                  border-left: 4px solid #378ADD; margin-bottom: 12px; }
    .bench-source { font-size: 11px; color: #888; margin-top: 6px; }
    .above { color: #E24B4A; font-weight: 600; }
    .below { color: #1D9E75; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("hr_attrition_clean_v2.csv")

df = load_data()

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=52)
st.sidebar.markdown("## HR Attrition Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", ["📊 Dashboard", "🌍 Benchmarks", "📄 Resume"])

st.sidebar.markdown("---")
st.sidebar.markdown("**Filters** *(Dashboard only)*")
dept_filter = st.sidebar.multiselect("Department", df['Department'].unique(), default=df['Department'].unique())
gender_filter = st.sidebar.multiselect("Gender", df['Gender'].unique(), default=df['Gender'].unique())
ot_filter = st.sidebar.radio("Overtime", ["All", "Yes", "No"])

filtered = df[df['Department'].isin(dept_filter) & df['Gender'].isin(gender_filter)]
if ot_filter != "All":
    filtered = filtered[filtered['OverTime'] == ot_filter]

st.sidebar.markdown("---")
st.sidebar.caption("Built by Thanakhan Kongkoet\nPython · Streamlit · Plotly")

# ── Dashboard Page ────────────────────────────────────────
if page == "📊 Dashboard":
    st.title("📊 HR Attrition Analytics Dashboard")
    st.caption("IBM HR Employee Attrition Dataset — 1,470 employee records · 19 variables")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Employees", f"{len(df):,}")
    with col2:
        rate = df['Attrition'].value_counts(normalize=True)['Yes'] * 100
        st.metric("Attrition Rate", f"{rate:.1f}%", delta="+5.8% vs global avg (18%)", delta_color="inverse")
    with col3:
        st.metric("Avg Monthly Income", f"${df['MonthlyIncome'].mean():,.0f}")
    with col4:
        ot = (df['OverTime'] == 'Yes').mean() * 100
        st.metric("Overtime Workers", f"{ot:.1f}%")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Attrition drivers")

    col1, col2 = st.columns(2)
    with col1:
        dept_attr = filtered.groupby('Department')['AttritionBinary'].mean().mul(100).reset_index()
        dept_attr.columns = ['Department', 'Attrition Rate (%)']
        fig = px.bar(dept_attr, x='Attrition Rate (%)', y='Department', orientation='h',
                     color='Attrition Rate (%)', color_continuous_scale=['#B5D4F4','#E24B4A'],
                     title="Attrition rate by department")
        fig.update_layout(showlegend=False, height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight">HR has the highest attrition — nearly 1 in 3 employees leave. Prioritise retention programs here first.</div>', unsafe_allow_html=True)

    with col2:
        ot_data = filtered.groupby('OverTime')['AttritionBinary'].mean().mul(100).reset_index()
        ot_data.columns = ['Overtime', 'Attrition Rate (%)']
        fig = px.bar(ot_data, x='Overtime', y='Attrition Rate (%)',
                     color='Overtime', color_discrete_map={'Yes':'#E24B4A','No':'#1D9E75'},
                     title="Overtime vs. attrition")
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight">Overtime workers are 3× more likely to leave — the strongest single predictor in this dataset.</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        age_attr = filtered.groupby('AgeGroup', observed=True)['AttritionBinary'].mean().mul(100).reset_index()
        age_attr.columns = ['Age Group', 'Attrition Rate (%)']
        fig = px.bar(age_attr, x='Age Group', y='Attrition Rate (%)',
                     color='Attrition Rate (%)', color_continuous_scale=['#B5D4F4','#E24B4A'],
                     title="Attrition by age group")
        fig.update_layout(showlegend=False, height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight">Employees under 25 are 3× more likely to leave than those aged 45+.</div>', unsafe_allow_html=True)

    with col4:
        sat_attr = filtered.groupby('JobSatisfaction')['AttritionBinary'].mean().mul(100).reset_index()
        sat_attr.columns = ['Job Satisfaction (1–4)', 'Attrition Rate (%)']
        fig = px.line(sat_attr, x='Job Satisfaction (1–4)', y='Attrition Rate (%)',
                      markers=True, title="Job satisfaction vs. attrition",
                      color_discrete_sequence=['#E24B4A'])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight">Every point increase in satisfaction reduces attrition. Score 1 employees are twice as likely to leave as score 4.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Income & work-life balance")

    col5, col6 = st.columns(2)
    with col5:
        fig = px.histogram(filtered, x='MonthlyIncome', color='Attrition',
                           color_discrete_map={'Yes':'#E24B4A','No':'#378ADD'},
                           barmode='overlay', opacity=0.7,
                           title="Income distribution: stayed vs. left")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        left_inc = filtered[filtered['Attrition']=='Yes']['MonthlyIncome'].mean()
        stay_inc = filtered[filtered['Attrition']=='No']['MonthlyIncome'].mean()
        st.markdown(f'<div class="insight">Employees who left earned ${left_inc:,.0f}/month vs ${stay_inc:,.0f} for those who stayed — a ${stay_inc-left_inc:,.0f} gap.</div>', unsafe_allow_html=True)

    with col6:
        wlb_attr = filtered.groupby('WorkLifeBalance')['AttritionBinary'].mean().mul(100).reset_index()
        wlb_attr.columns = ['Work-Life Balance (1–4)', 'Attrition Rate (%)']
        wlb_attr['Label'] = ['1 (Bad)', '2 (Good)', '3 (Better)', '4 (Best)']
        fig = px.bar(wlb_attr, x='Label', y='Attrition Rate (%)',
                     color='Attrition Rate (%)', color_continuous_scale=['#1D9E75','#E24B4A'],
                     title="Work-life balance vs. attrition")
        fig.update_layout(showlegend=False, height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight">Poor work-life balance nearly doubles attrition risk. Workload management is the clearest retention lever.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Department × Satisfaction heatmap")
    pivot = filtered.groupby(['Department','JobSatisfaction'])['AttritionBinary'].mean().mul(100).reset_index()
    pivot.columns = ['Department','Job Satisfaction','Attrition Rate (%)']
    fig = px.density_heatmap(pivot, x='Job Satisfaction', y='Department',
                             z='Attrition Rate (%)', color_continuous_scale='RdYlGn_r',
                             title="Attrition heatmap: Dept × Satisfaction", text_auto='.0f')
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight">Darkest cell = highest risk. R&D employees with low satisfaction show 37% attrition. HR figures may fluctuate due to small department size.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("🚨 High-risk employee segment")
    high_risk = filtered[
        (filtered['OverTime'] == 'Yes') &
        (filtered['JobSatisfaction'] <= 2) &
        (filtered['Age'] < 30)
    ][['Age','Department','JobRole','MonthlyIncome','OverTime','JobSatisfaction','WorkLifeBalance','Attrition']]
    st.caption(f"{len(high_risk)} employees flagged — under 30, working overtime, satisfaction score ≤ 2")
    st.dataframe(high_risk.head(20), use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""> **Key recommendation:** Focus retention efforts on **young (under 25),
    overtime-assigned employees in HR and R&D with low satisfaction scores**.
    Targeted interventions — workload review, compensation adjustment, and early engagement programs —
    are most likely to reduce overall attrition.""")

# ── Benchmark Page ────────────────────────────────────────
elif page == "🌍 Benchmarks":
    our_rate = df['Attrition'].value_counts(normalize=True)['Yes'] * 100
    our_sat_pct = (df['JobSatisfaction'] >= 3).mean() * 100
    our_ot = (df['OverTime'] == 'Yes').mean() * 100

    st.title("🌍 Industry Benchmark Comparison")
    st.caption("Comparing our dataset against real-world 2024–2025 HR industry reports")

    st.info("**Why this matters:** Analysing data in isolation tells you what's happening inside a company. Comparing against global benchmarks tells you whether it's a company problem or an industry-wide trend — a critical distinction for any HR recommendation.")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Overall attrition rate")

    bench_attrition = pd.DataFrame({
        'Source': ['Our Dataset', 'Mercer 2024 (predicted turnover)', 'SHRM 2024 (voluntary)', 'Global healthy benchmark'],
        'Attrition Rate (%)': [our_rate, 20.0, 23.0, 10.0],
        'Type': ['Our Data', 'Benchmark', 'Benchmark', 'Target']
    })
    colors = {'Our Data': '#378ADD', 'Benchmark': '#888780', 'Target': '#1D9E75'}
    fig = px.bar(bench_attrition, x='Source', y='Attrition Rate (%)',
                 color='Type', color_discrete_map=colors,
                 title="Attrition rate: our data vs. industry benchmarks",
                 text='Attrition Rate (%)')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=380, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    diff = our_rate - 20.0
    direction = "above" if diff > 0 else "below"
    colour_class = "above" if diff > 0 else "below"
    st.markdown(f"""
    <div class="bench-card">
        Our attrition rate of <strong>{our_rate:.1f}%</strong> is
        <span class="{colour_class}">{abs(diff):.1f} percentage points {direction}</span>
        Mercer's 2024 predicted global turnover average of 20%.
        SHRM reports voluntary attrition averaged 23% in 2024, placing our dataset within a realistic range.
        The widely cited "healthy" benchmark is below 10%, which most real companies do not achieve.
        <div class="bench-source">Sources: Mercer Global Talent Trends 2024 · SHRM 2024 Benchmarking · AIHR People Analytics Guide 2026</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Employee engagement & satisfaction")

    bench_engage = pd.DataFrame({
        'Group': ['Our Dataset\n(satisfied, score ≥3)', 'Gallup 2024\n(engaged globally)', 'Gallup 2024\n(not engaged)', 'Gallup 2024\n(actively disengaged)'],
        'Percentage (%)': [our_sat_pct, 21.0, 62.0, 15.0],
        'Type': ['Our Data', 'Engaged', 'Not Engaged', 'Disengaged']
    })
    fig2 = px.bar(bench_engage, x='Group', y='Percentage (%)',
                  color='Type',
                  color_discrete_map={
                      'Our Data': '#378ADD',
                      'Engaged': '#1D9E75',
                      'Not Engaged': '#BA7517',
                      'Disengaged': '#E24B4A'
                  },
                  title="Satisfaction/engagement: our data vs. Gallup 2024 global report",
                  text='Percentage (%)')
    fig2.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
    fig2.update_layout(height=380, showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""
    <div class="bench-card">
        <strong>{our_sat_pct:.0f}%</strong> of employees in our dataset rated satisfaction at 3 or above.
        Gallup's 2025 State of the Global Workplace report found global employee engagement
        fell to <strong>21% in 2024</strong> — down from 23% in 2023 — costing the world economy
        an estimated $438 billion in lost productivity. The drop was sharpest among managers,
        where engagement fell from 30% to 27% in a single year.
        <div class="bench-source">Source: Gallup State of the Global Workplace 2025 Report (covering 2024 data)</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Attrition rate by industry (global 2024–2025)")

    industry_bench = pd.DataFrame({
        'Industry': ['Travel & Hospitality', 'Retail & Sales', 'Technology', 'Healthcare',
                     'Professional Services', 'Finance', 'Education', 'Government'],
        'Avg Monthly Turnover (%)': [2.8, 2.4, 2.1, 2.0, 1.9, 1.7, 1.8, 1.4]
    })
    industry_bench['Annualised (%)'] = (industry_bench['Avg Monthly Turnover (%)'] * 12).round(1)
    fig3 = px.bar(industry_bench.sort_values('Annualised (%)'),
                  x='Annualised (%)', y='Industry', orientation='h',
                  color='Annualised (%)', color_continuous_scale=['#B5D4F4','#E24B4A'],
                  title="Annualised attrition rate by industry — BambooHR 2024–2025 benchmark",
                  text='Annualised (%)')
    fig3.update_traces(texttemplate='%{text}%', textposition='outside')
    fig3.update_layout(height=400, showlegend=False, coloraxis_showscale=False, xaxis_range=[0, 45])
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("""
    <div class="bench-card">
        Travel & Hospitality leads all sectors with ~33.6% annualised turnover, while Government
        sits lowest at ~16.8%. Our dataset at 23.8% sits in the middle range — comparable to
        Technology and Professional Services. This context matters: a 23.8% rate in a tech firm
        is unremarkable, but the same rate in a government agency would be alarming.
        <div class="bench-source">Source: BambooHR Employee Turnover Benchmarking Report, Oct 2024–Mar 2025</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Cost of attrition")
    avg_salary = df['MonthlyIncome'].mean() * 12
    attrition_count = int(len(df) * our_rate / 100)
    cost_low = attrition_count * avg_salary * 0.50
    cost_high = attrition_count * avg_salary * 2.00

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Employees who left", f"{attrition_count:,}")
    with col2:
        st.metric("Estimated cost (low)", f"${cost_low/1_000_000:.1f}M", help="50% of annual salary per departure (Gallup estimate)")
    with col3:
        st.metric("Estimated cost (high)", f"${cost_high/1_000_000:.1f}M", help="200% of annual salary per departure (SHRM estimate)")

    st.markdown(f"""
    <div class="bench-card">
        According to Gallup, replacing one employee costs between 50% and 200% of their annual salary.
        At an average salary of ${avg_salary:,.0f}/year and {attrition_count} departures,
        this company's estimated annual attrition cost ranges from
        <strong>${cost_low/1_000_000:.1f}M to ${cost_high/1_000_000:.1f}M</strong>.
        This figure, presented to a leadership team, reframes attrition from an HR metric
        into a direct financial risk — which is how senior decision-makers respond to it.
        <div class="bench-source">Source: Gallup — The Cost of Employee Turnover · SHRM Benchmarking</div>
    </div>
    """, unsafe_allow_html=True)

# ── Resume Page ───────────────────────────────────────────
elif page == "📄 Resume":
    st.title("📄 Project Resume")
    st.caption("Copy resume descriptions tailored to the role you're applying for.")

    tab1, tab2 = st.tabs(["🧑‍💼 HR Role Version", "📈 Analyst Role Version"])

    with tab1:
        st.markdown("""
        <div class="resume-box">
            <div class="resume-title">HR Attrition Analytics Dashboard</div>
            <div class="resume-tools">Tools: Python (pandas, matplotlib, seaborn) · Streamlit · Plotly</div>
            <div class="resume-bullet">
            • Analysed 1,470 employee records to identify key drivers of workforce attrition
              across department, age, income, overtime, and job satisfaction dimensions<br>
            • Identified overtime as the strongest single predictor —
              overtime workers showed 3× higher attrition than average<br>
            • Benchmarked findings against Mercer 2024 and Gallup 2025 global reports,
              contextualising a 23.8% attrition rate within industry norms<br>
            • Built an interactive dashboard with department and gender filters
              for HR decision-makers, deployed on Streamlit Cloud<br>
            • Surfaced actionable insight: highest-risk segment is employees under 25 in HR
              with low satisfaction scores, recommending targeted early-career engagement programs
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Skills demonstrated:**")
        for tag in ["Data Analysis","People Analytics","Attrition Modelling","Benchmark Research","Dashboard Design","Python","Streamlit","HR Strategy"]:
            st.markdown(f'<span class="tag">{tag}</span>', unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class="resume-box">
            <div class="resume-title">HR Attrition Analytics Dashboard</div>
            <div class="resume-tools">Tools: Python (pandas, matplotlib, seaborn) · Streamlit · Plotly</div>
            <div class="resume-bullet">
            • Designed and executed end-to-end data analysis pipeline
              on 1,470-record HR dataset across 19 variables<br>
            • Performed EDA to surface attrition patterns by department, tenure,
              income band, overtime status, and satisfaction score<br>
            • Applied data validation techniques to detect and correct a synthetic data flaw
              where work-life balance showed an inverted attrition relationship<br>
            • Cross-referenced findings with Mercer 2024, Gallup 2025, SHRM, and BambooHR
              industry benchmarks to contextualise internal metrics against global standards<br>
            • Modelled estimated annual cost of attrition at $8.7M–$34.9M using
              Gallup and SHRM cost-per-departure formulas<br>
            • Deployed interactive 3-page dashboard on Streamlit Cloud
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Skills demonstrated:**")
        for tag in ["EDA","Data Validation","Benchmark Analysis","Pipeline Design","Python","Plotly","Streamlit","Statistical Analysis","Business Framing"]:
            st.markdown(f'<span class="tag">{tag}</span>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("About the project")
    st.markdown("""
    <div class="about-text">
    This dashboard was built as a portfolio project to demonstrate applied data analysis skills
    in the context of Human Resources. The dataset is modelled after the IBM HR Employee Attrition
    dataset structure, with 1,470 employee records and 19 variables.<br><br>
    The analysis covers 9 dimensions of attrition risk and includes a benchmark comparison page
    drawing from Mercer Global Talent Trends 2024, Gallup State of the Global Workplace 2025,
    SHRM 2024 benchmarks, and BambooHR's industry turnover report (Oct 2024–Mar 2025).<br><br>
    The project also involved identifying and correcting a data generation flaw — demonstrating
    data validation and critical thinking beyond basic charting.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Tech stack")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Analysis**")
        st.markdown("- Python 3\n- pandas\n- numpy")
    with col2:
        st.markdown("**Visualisation**")
        st.markdown("- Plotly Express\n- matplotlib\n- seaborn")
    with col3:
        st.markdown("**Deployment**")
        st.markdown("- Streamlit\n- Streamlit Cloud\n- GitHub")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.caption("Built by Thanakhan Kongkoet · Faculty of Arts, Silpakorn University · Bangkok, Thailand")
