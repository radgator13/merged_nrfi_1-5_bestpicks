import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import os
from datetime import datetime

# Set full screen width
st.set_page_config(page_title="MLB Dashboard (NRFI + 1-5 + Best Picks)", layout="wide")

# Sidebar Navigation
st.sidebar.title("⚾ MLB Predictive Tools")
page = st.sidebar.selectbox(
    "Choose Module:",
    ["NRFI Predictor", "1-5 Inning Predictor", "Best Picks Today"]
)

# ---------------
# Load shared data
# ---------------
@st.cache_data
def load_nrfi_data():
    pred = pd.read_csv("data/mlb_nrfi_predictions.csv")
    results = pd.read_csv("data/mlb_nrfi_results_full.csv")
    model = joblib.load("model_rf_real.pkl")
    return pred, results, model

@st.cache_data
def load_1to5_data():
    df = pd.read_csv('data/mlb_boxscores_1to5_model_full_predictions.csv')
    df['Game Date'] = pd.to_datetime(df['Game Date'])
    return df

# Load once at start
nrfi_pred_df, nrfi_results_df, rf_model = load_nrfi_data()
innings_df = load_1to5_data()

# Process NRFI data
nrfi_df = nrfi_pred_df.merge(
    nrfi_results_df[['Game Date', 'Away Team', 'Home Team', 'Actual_1st_Inning_Runs', 'Prediction_Result']],
    on=['Game Date', 'Away Team', 'Home Team'],
    how='left'
)

def assign_nrfi_fireball(prob):
    if prob >= 70: return "🔥🔥🔥🔥🔥"
    elif prob >= 65: return "🔥🔥🔥🔥"
    elif prob >= 55: return "🔥🔥🔥"
    elif prob >= 50: return "🔥🔥"
    elif prob >= 45: return "🔥"
    else: return "no value"

if 'Predicted_NRFI_Probability' in nrfi_df.columns:
    nrfi_df['Fireball_Rating'] = nrfi_df['Predicted_NRFI_Probability'].apply(assign_nrfi_fireball)

# Confidence assignment for 1-5 predictions
def assign_1to5_confidence(row):
    gap = row['Predicted_Runs_1to5'] - row['Target_Line']
    if row['Predicted_Over_4_5'] == "Over":
        if gap >= 1.5: return "🔥🔥🔥🔥🔥"
        elif gap >= 1.0: return "🔥🔥🔥🔥"
        elif gap >= 0.5: return "🔥🔥🔥"
        elif gap >= 0.25: return "🔥🔥"
        else: return "🔥"
    elif row['Predicted_Over_4_5'] == "Under":
        if gap <= -1.5: return "🔥🔥🔥🔥🔥"
        elif gap <= -1.0: return "🔥🔥🔥🔥"
        elif gap <= -0.5: return "🔥🔥🔥"
        elif gap <= -0.25: return "🔥🔥"
        else: return "🔥"
    else:
        return "🔥"

innings_df['Confidence'] = innings_df.apply(assign_1to5_confidence, axis=1)

# ----------------
# NRFI Predictor Module
# ----------------
if page == "NRFI Predictor":
    st.title("⚾ MLB NRFI Predictions Dashboard")
    st.subheader("NRFI Model Predictions and Fireball Ratings")

    available_dates = sorted(pd.to_datetime(nrfi_df['Game Date']).unique())
    selected_date = st.date_input("Select Game Date:", value=datetime.today(), min_value=available_dates[0], max_value=available_dates[-1])
    selected_date_str = selected_date.strftime('%Y-%m-%d')

    view_option = st.radio("View Mode:", ["All Predictions", "Best Fireballs Only"])

    filtered_nrfi = nrfi_df[nrfi_df['Game Date'] == selected_date_str]

    if view_option == "Best Fireballs Only":
        filtered_nrfi = filtered_nrfi[filtered_nrfi['Fireball_Rating'].isin(["🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"])]

    if not filtered_nrfi.empty:
        st.dataframe(filtered_nrfi[['Away Team', 'Home Team', 'Fireball_Rating', 'Predicted_NRFI_Probability']])
    else:
        st.write("No NRFI predictions available for this date.")

# ----------------
# 1-5 Inning Predictor Module
# ----------------
elif page == "1-5 Inning Predictor":
    st.title("⚾ MLB 1-5 Inning Over/Under Model Dashboard")

    selected_date = st.date_input("Select a date to view games:", value=pd.to_datetime("today"))

    played_df = innings_df[innings_df['Actual_Runs_1to5'] != "Pending"]
    pending_df = innings_df[innings_df['Actual_Runs_1to5'] == "Pending"]

    played_today = played_df[played_df['Game Date'] == pd.to_datetime(selected_date)]
    pending_today = pending_df[pending_df['Game Date'] == pd.to_datetime(selected_date)]

    st.subheader(f"📋 Played Games on {selected_date.strftime('%Y-%m-%d')}")
    if not played_today.empty:
        st.dataframe(played_today)
    else:
        st.write("🚫 No played games for this date.")

    st.subheader(f"🔮 Pending Games on {selected_date.strftime('%Y-%m-%d')}")
    if not pending_today.empty:
        st.dataframe(pending_today)
    else:
        st.write("🚫 No pending games for this date.")

    st.header("📊 Model Accuracy")

    daily_total = len(played_today)
    daily_correct = (played_today['Predicted_Over_4_5'] == played_today['Actual_Over_4_5']).sum()
    daily_accuracy = (daily_correct / daily_total) if daily_total > 0 else 0

    rolling_total = len(played_df)
    rolling_correct = (played_df['Predicted_Over_4_5'] == played_df['Actual_Over_4_5']).sum()
    rolling_accuracy = (rolling_correct / rolling_total) if rolling_total > 0 else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Daily Accuracy", value=f"{daily_accuracy:.2%}")
    with col2:
        st.metric(label="Rolling Accuracy", value=f"{rolling_accuracy:.2%}")

# ----------------
# Best Picks Module
# ----------------
elif page == "Best Picks Today":
    st.title("🔥 Best Picks Based on Model Confidence")

    selected_date = st.date_input("Select Game Date:", value=pd.to_datetime("today"))
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    best_fireballs = ["🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"]

    # --- NRFI Best Picks ---
    st.subheader("⚾ NRFI Best Picks")

    nrfi_best_all = nrfi_df[nrfi_df['Fireball_Rating'].isin(best_fireballs)]
    nrfi_best_today = nrfi_best_all[nrfi_best_all['Game Date'] == selected_date_str]

    if not nrfi_best_today.empty:
        st.dataframe(
            nrfi_best_today[['Away Team', 'Home Team', 'Fireball_Rating', 'Predicted_NRFI_Probability']]
            .sort_values(by='Predicted_NRFI_Probability', ascending=False)
        )
    else:
        st.write("🚫 No NRFI best picks for this date.")

    nrfi_today_final = nrfi_best_today[nrfi_best_today['Prediction_Result'].isin(["✅ HIT", "❌ MISS"])]
    nrfi_today_wins = (nrfi_today_final['Prediction_Result'] == "✅ HIT").sum()
    nrfi_today_losses = (nrfi_today_final['Prediction_Result'] == "❌ MISS").sum()
    nrfi_today_total = nrfi_today_wins + nrfi_today_losses
    nrfi_today_pct = nrfi_today_wins / nrfi_today_total if nrfi_today_total > 0 else 0

    nrfi_completed = nrfi_best_all[
        (nrfi_best_all['Prediction_Result'].isin(["✅ HIT", "❌ MISS"])) &
        (pd.to_datetime(nrfi_best_all['Game Date']) <= pd.to_datetime(selected_date))
    ]
    nrfi_total_wins = (nrfi_completed['Prediction_Result'] == "✅ HIT").sum()
    nrfi_total_losses = (nrfi_completed['Prediction_Result'] == "❌ MISS").sum()
    nrfi_total = nrfi_total_wins + nrfi_total_losses
    nrfi_total_pct = nrfi_total_wins / nrfi_total if nrfi_total > 0 else 0

    st.markdown(f"📅 **NRFI Daily Record ({selected_date_str})**: {nrfi_today_wins}-{nrfi_today_losses} ({nrfi_today_pct:.2%})")
    st.markdown(f"📈 **NRFI Rolling Record (Season to {selected_date_str})**: {nrfi_total_wins}-{nrfi_total_losses} ({nrfi_total_pct:.2%})")

    # --- 1-5 Inning Best Picks ---
    st.subheader("⚾ 1-5 Inning Best Picks")

    innings_best_all = innings_df[innings_df['Confidence'].isin(best_fireballs)]
    innings_best_today = innings_best_all[innings_best_all['Game Date'] == pd.to_datetime(selected_date)]

    if not innings_best_today.empty:
        st.dataframe(
            innings_best_today[['Away Team', 'Home Team', 'Confidence', 'Predicted_Runs_1to5', 'Target_Line']]
            .sort_values(by='Confidence', ascending=False)
        )
    else:
        st.write("🚫 No 1-5 inning best picks for this date.")

    inn_today_final = innings_best_today[innings_best_today['Actual_Over_4_5'].isin(["Over", "Under"])]
    inn_today_wins = (inn_today_final['Predicted_Over_4_5'] == inn_today_final['Actual_Over_4_5']).sum()
    inn_today_losses = len(inn_today_final) - inn_today_wins
    inn_today_total = inn_today_wins + inn_today_losses
    inn_today_pct = inn_today_wins / inn_today_total if inn_today_total > 0 else 0

    innings_completed = innings_best_all[
        (innings_best_all['Actual_Over_4_5'].isin(["Over", "Under"])) &
        (pd.to_datetime(innings_best_all['Game Date']) <= pd.to_datetime(selected_date))
    ]
    inn_total_wins = (innings_completed['Predicted_Over_4_5'] == innings_completed['Actual_Over_4_5']).sum()
    inn_total_losses = len(innings_completed) - inn_total_wins
    inn_total = inn_total_wins + inn_total_losses
    inn_total_pct = inn_total_wins / inn_total if inn_total > 0 else 0

    st.markdown(f"📅 **1-5 Daily Record ({selected_date_str})**: {inn_today_wins}-{inn_today_losses} ({inn_today_pct:.2%})")
    st.markdown(f"📈 **1-5 Rolling Record (Season to {selected_date_str})**: {inn_total_wins}-{inn_total_losses} ({inn_total_pct:.2%})")
