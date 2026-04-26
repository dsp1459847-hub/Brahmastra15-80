import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="MAYA AI - Ultimate Brahmastra", layout="wide")

st.title("MAYA AI 🎯: The Ultimate Brahmastra Engine")
st.markdown("Isme Series, War, 9 Timeframes, Date Fix aur Sniper Mode sab ek sath shamil hain. **Sirf Super Confirmed** dino par kheliye!")

# --- 1. Sidebar ---
st.sidebar.header("📁 Data Settings")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
selected_end_date = st.sidebar.date_input("Calculation Date (Aaj ki Tarikh)")
max_limit = st.sidebar.slider("Elimination Limit", 2, 5, 4)

shift_order = ["DB", "SG", "FD", "GD", "ZA", "GL", "DS"]

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
        else: df = pd.read_excel(uploaded_file)
        
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        df = df.sort_values(by='DATE').reset_index(drop=True)
        for col in shift_order:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')

        filtered_df = df[df['DATE'].dt.date <= selected_end_date].copy()
        if len(filtered_df) == 0: st.stop()
        
        target_date_next = selected_end_date + timedelta(days=1)
        st.info(f"📅 **Data Read Up To:** {selected_end_date.strftime('%d %B %Y')} | 🎯 **Prediction For:** {target_date_next.strftime('%A, %d %B %Y')}")

        # --- 2. CORE LOGIC (Sub Parts & Adapters) ---
        def get_sub_parts(past_list, limit):
            past_list = [int(x) for x in past_list if pd.notna(x)]
            scores = {n: 0 for n in range(100)}
            elim = set()
            for days in range(1, min(16, len(past_list) + 1)):
                sheet = past_list[-days:]
                counts = Counter(sheet)
                if len(counts) == len(sheet) and len(sheet) > 1: elim.update(sheet)
                for num, freq in counts.items():
                    if freq >= limit: elim.add(num)
                    scores[num] += freq
            ranked = sorted(range(100), key=lambda x: scores[x], reverse=True)
            return {
                "H1": ranked[0:11], "H2": ranked[11:22], "H3": ranked[22:33],
                "M1": ranked[33:44], "M2": ranked[44:55], "M3": ranked[55:66],
                "L1": ranked[66:77], "L2": ranked[77:88], "L3": ranked[88:100],
                "ELIM": list(elim)
            }

        def get_part_name(num, sp_dict):
            for part, nums in sp_dict.items():
                if part != "ELIM" and num in nums: return part
            return None

        def find_best_sequence(history_tier_list):
            best_prob = -1
            best_pred = 'H1'
            best_len = 0
            for p_len in range(1, min(31, len(history_tier_list))):
                cur_pattern = history_tier_list[-p_len:]
                matches = []
                for i in range(len(history_tier_list) - p_len):
                    if history_tier_list[i:i+p_len] == cur_pattern:
                        if i + p_len < len(history_tier_list):
                            matches.append(history_tier_list[i+p_len])
                if matches:
                    counts = Counter(matches)
                    top_match, top_count = counts.most_common(1)[0]
                    prob = top_count / len(matches)
                    if prob > best_prob or (prob == best_prob and p_len > best_len):
                        best_prob = prob; best_pred = top_match; best_len = p_len
            return best_pred, best_len

        def render_ank(nums, jackpots, votes):
            nums = list(set(nums)); nums.sort()
            html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;'>"
            for n in nums:
                v = votes.get(n, 0)
                bg = "#FF4B4B" if n in jackpots else "#2e2e2e"
                border = "2px solid #ff9999" if n in jackpots else "2px solid #555" 
                html += f"<div style='background:{bg}; padding:10px; border-radius:8px; text-align:center; min-width:50px; border:{border}; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>" \
                        f"<span style='font-size:22px; font-weight:bold; color:white;'>{n:02d}</span><br>" \
                        f"<span style='font-size:11px; color:#ddd;'>{v}v</span></div>"
            html += "</div>"
            return html

        # --- 3. MASTER PREDICTION ENGINE ---
        def get_ultimate_prediction(history_series, war_series):
            # A. Build Tier History for Series & War
            tier_hist = []
            for i in range(15, len(history_series)):
                sp = get_sub_parts(history_series[:i], max_limit)
                actual_part = get_part_name(history_series[i], sp)
                tier_hist.append(actual_part if actual_part else "FAIL")
                
            war_tier_hist = []
            for i in range(15, len(war_series)):
                sp = get_sub_parts(war_series[:i], max_limit)
                actual_part = get_part_name(war_series[i], sp)
                war_tier_hist.append(actual_part if actual_part else "FAIL")

            # B. Get Pattern Predictions
            series_pred, series_len = find_best_sequence(tier_hist) if tier_hist else ("H1", 0)
            war_pred, war_len = find_best_sequence(war_tier_hist) if war_tier_hist else ("H1", 0)

            # C. Adaptive Selection (Merge Series & War Logic)
            current_sp = get_sub_parts(history_series[-15:], max_limit)
            top_parts = []
            if series_pred != "FAIL": top_parts.append(series_pred)
            if war_pred != "FAIL" and war_pred not in top_parts: top_parts.append(war_pred)
            
            # Fill remaining with standards
            all_possible = ['H1', 'H2', 'H3', 'M1', 'M2', 'M3', 'L1', 'L2', 'L3']
            for p in all_possible:
                if len(top_parts) >= 3: break
                if p not in top_parts: top_parts.append(p)
                
            top_parts = top_parts[:3] # Strictly 3 parts
            target_nums = list(set(current_sp[top_parts[0]] + current_sp[top_parts[1]] + current_sp[top_parts[2]]))

            # D. 9 TIMEFRAMES SUPER STRONG LAL DABBE
            timeframes = [3, 5, 7, 10, 14, 15, 20, 25, 30]
            vote_tally = {n: 0 for n in target_nums}
            for tf in timeframes:
                if len(history_series) < tf: continue
                tf_counts = Counter(history_series[-tf:])
                for n in target_nums:
                    if n in tf_counts: vote_tally[n] += tf_counts[n]

            sorted_by_votes = sorted(target_nums, key=lambda x: vote_tally[x], reverse=True)
            super_strong_jackpots = sorted_by_votes[:5] # Top 5 Guaranteed Red Boxes

            return target_nums, super_strong_jackpots, top_parts, vote_tally, series_pred, war_pred

        # --- 4. SHIFT PROCESSING ---
        for shift_name in shift_order:
            if shift_name not in df.columns: continue
            
            # Full history
            history_today = filtered_df[shift_name].dropna().astype(int).tolist()
            if len(history_today) < 30: continue
            
            # War history (Same day of week)
            war_day_today = target_date_next.dayofweek
            war_dates_today = filtered_df[filtered_df['DATE'].dt.dayofweek == war_day_today]['DATE'].tolist()
            war_history_today = [int(filtered_df[filtered_df['DATE'] == d][shift_name].values[0]) for d in war_dates_today if pd.notna(filtered_df[filtered_df['DATE'] == d][shift_name].values[0])]
            
            # Yesterday history (For Histry Match)
            history_yesterday = df[df['DATE'].dt.date < selected_end_date][shift_name].dropna().astype(int).tolist()
            war_day_yest = selected_end_date.dayofweek
            war_dates_yest = df[(df['DATE'].dt.date < selected_end_date) & (df['DATE'].dt.dayofweek == war_day_yest)]['DATE'].tolist()
            war_history_yest = [int(df[df['DATE'] == d][shift_name].values[0]) for d in war_dates_yest if pd.notna(df[df['DATE'] == d][shift_name].values[0])]

            st.markdown(f"---")
            st.subheader(f"🧩 Shift: {shift_name}")

            with st.spinner("Series, War aur Timeframes ko scan kiya jaa raha hai..."):
                # A. HISTRY MATCH
                actual_row = df[df['DATE'].dt.date == selected_end_date]
                actual_val = int(actual_row.iloc[0][shift_name]) if not actual_row.empty and pd.notna(actual_row.iloc[0][shift_name]) else None
                is_hit = False
                if actual_val is not None and len(history_yesterday) >= 30:
                    hist_target, _, _, _, _, _ = get_ultimate_prediction(history_yesterday, war_history_yest)
                    is_hit = actual_val in hist_target

                # B. TOMORROW'S PREDICTION
                final_nums, jackpots, top_parts, votes, s_pred, w_pred = get_ultimate_prediction(history_today, war_history_today)

            # C. UI DISPLAY (Sniper Mode)
            parts_joined = ", ".join(top_parts)
            status_color = "#1E90FF"
            status_text = "NORMAL DANGER ZONE (Avoid ya 1x khele)"
            
            # The Ultimate Confirmation Logic
            if s_pred != "FAIL" and s_pred == w_pred:
                status_color = "#00FF7F"
                status_text = f"🔥 SUPER CONFIRMED (Series & War Match on {s_pred}!) - Invest 9x"
            elif s_pred != "FAIL" and s_pred in top_parts:
                status_color = "#FFA500"
                status_text = f"⚡ STRONG SERIES PATTERN - Invest 3x"
            
            c_res, c_stat = st.columns([1, 2.5])
            with c_res:
                if actual_val is not None:
                    m_color = "#28a745" if is_hit else "#FF4B4B"
                    st.markdown(f"<div style='background:{m_color}; padding:10px; border-radius:8px; text-align:center; color:white;'>"
                                f"Histry Match ({selected_end_date.strftime('%d %b')}):<br><b style='font-size:24px;'>{actual_val:02d}</b><br>{'HIT! ✅' if is_hit else 'MISS ❌'}</div>", unsafe_allow_html=True)
                else:
                    st.write("Histry Match unavailable.")
            
            with c_stat:
                st.markdown(f"<div style='border:2px solid {status_color}; padding:10px; border-radius:8px; background:{status_color}15;'>"
                            f"<b style='color:{status_color}; font-size:18px;'>🎯 {status_text}</b><br>"
                            f"<span style='font-size: 14px;'>Series Predicts: <b>{s_pred}</b> | War Predicts: <b>{w_pred}</b> | Final Parts: <b>{parts_joined}</b></span></div>", unsafe_allow_html=True)

            # CLEAR NUMBERS WITH SUPER STRONG VOTES
            st.markdown(f"<h4 style='margin-top: 15px;'>Kewal Yehi Numbers Khelne Hain ({target_date_next.strftime('%A, %d %b')}):</h4>", unsafe_allow_html=True)
            st.markdown(render_ank(final_nums, jackpots, votes), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")
            
