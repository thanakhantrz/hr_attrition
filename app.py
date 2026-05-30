import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="HR Attrition Dashboard", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .metric-card { background: #f8f9fa; border-radius: 10px; padding: 16px; text-align: center; }
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
    .about-header { font-size: 15px; font-weight: 600; color: #2C2C2A; margin-bottom: 6px; }
    .about-text { font-size: 13px; color: #555; line-height: 1.8; }
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

page = st.sidebar.radio("Navigate", ["📊 Dashboard", "📄 Resume"])

st.sidebar.markdown("---")
st.sidebar.markdown("**Filters**")
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
        st.metric("Attrition Rate", f"{rate:.1f}%", delta="-3.2% vs industry avg", delta_color="inverse")
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
        st.markdown(f'<div class="insight">Employees who left earned ${left_inc:,.0f}/month on average vs ${stay_inc:,.0f} for those who stayed — a ${stay_inc-left_inc:,.0f} gap.</div>', unsafe_allow_html=True)

    with col6:
        wlb_attr = filtered.groupby('WorkLifeBalance')['AttritionBinary'].mean().mul(100).reset_index()
        wlb_attr.columns = ['Work-Life Balance (1–4)', 'Attrition Rate (%)']
        wlb_attr['Label'] = ['1 (Bad)', '2 (Good)', '3 (Better)', '4 (Best)']
        fig = px.bar(wlb_attr, x='Label', y='Attrition Rate (%)',
                     color='Attrition Rate (%)', color_continuous_scale=['#1D9E75','#E24B4A'],
                     title="Work-life balance vs. attrition")
        fig.update_layout(showlegend=False, height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight">Poor work-life balance nearly doubles attrition risk. Combined with overtime data, workload management is the clearest retention lever.</div>', unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.subheader("Department × Satisfaction heatmap")

    pivot = filtered.groupby(['Department','JobSatisfaction'])['AttritionBinary'].mean().mul(100).reset_index()
    pivot.columns = ['Department','Job Satisfaction','Attrition Rate (%)']
    fig = px.density_heatmap(pivot, x='Job Satisfaction', y='Department',
                             z='Attrition Rate (%)', color_continuous_scale='RdYlGn_r',
                             title="Attrition heatmap: which dept + satisfaction level is highest risk?",
                             text_auto='.0f')
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="insight">Darkest cell = highest risk. R&D employees with low satisfaction (score 1) show 37% attrition — the most urgent intervention target. Note: HR figures may be unstable due to small department size.</div>', unsafe_allow_html=True)

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
    st.markdown("""
    > **Key recommendation:** Focus retention efforts on **young (under 25), overtime-assigned employees
    in HR and R&D with low satisfaction scores**. These represent the highest-risk segment.
    Targeted interventions — workload review, compensation adjustment, and early engagement programs —
    are most likely to reduce overall attrition.
    """)
