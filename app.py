import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="MAYA AI - Ultimate Brahmastra", layout="wide")

st.title("MAYA AI 🏆: Ultimate Brahmastra (Sniper + Open Match)")
st.markdown("Isme **9 Timeframes**, **Series Pattern**, **War Pattern** aur **Correct Date Match** shamil hai. Ab har shift mein Super Strong (Lal Dabbe) dikhenge!")

# --- 1. Sidebar ---
st.sidebar.header("📁 Data Settings")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
selected_end_date = st.sidebar.date_input("Calculation Date (T)")
max_limit = st.sidebar.slider("Elimination Limit", 2, 5, 4)

shift_order = ["DB", "SG", "FD", "GD", "ZA", "GL", "DS"]

if uploaded_file is not None:
    try:
        # Data Loading
        if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
        else: df = pd.read_excel(uploaded_file)
        
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        df = df.sort_values(by='DATE').reset_index(drop=True)
        for col in shift_order:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')

        # Logic Dates
        # Hum Today (T) select karte hain
        filtered_df = df[df['DATE'].dt.date <= selected_end_date].copy()
        if len(filtered_df) == 0: 
            st.warning("Is tarikh ka data nahi hai.")
            st.stop()
        
        # Prediction aur Match Date = Today + 1 (T+1)
        target_date_next = selected_end_date + timedelta(days=1)
        
        st.info(f"📅 **Data Read Up To:** {selected_end_date.strftime('%d %B %Y')} | 🎯 **Prediction & Open Record Match:** {target_date_next.strftime('%d %B %Y')}")

        # --- 2. CORE LOGIC ---
        def get_sub_parts(past_list, limit):
            past_list = [int(x) for x in past_list if pd.notna(x)]
            scores = {n: 0 for n in range(100)}
            for days in range(1, min(16, len(past_list) + 1)):
                sheet = past_list[-days:]
                counts = Counter(sheet)
                for num, freq in counts.items(): scores[num] += freq
            ranked = sorted(range(100), key=lambda x: scores[x], reverse=True)
            return {
                "H1": ranked[0:11], "H2": ranked[11:22], "H3": ranked[22:33],
                "M1": ranked[33:44], "M2": ranked[44:55], "M3": ranked[55:66],
                "L1": ranked[66:77], "L2": ranked[77:88], "L3": ranked[88:100]
            }

        def find_best_sequence(history_tier_list):
            best_prob, best_pred, best_len = -1, 'H1', 0
            for p_len in range(1, min(31, len(history_tier_list))):
                cur_pattern = history_tier_list[-p_len:]
                matches = []
                for i in range(len(history_tier_list) - p_len):
                    if history_tier_list[i:i+p_len] == cur_pattern:
                        if i + p_len < len(history_tier_list): matches.append(history_tier_list[i+p_len])
                if matches:
                    top_m, top_c = Counter(matches).most_common(1)[0]
                    prob = top_c / len(matches)
                    if prob > best_prob or (prob == best_prob and p_len > best_len):
                        best_prob, best_pred, best_len = prob, top_m, p_len
            return best_pred

        def get_brahmastra_prediction(history_series, war_history):
            # A. Patterns
            tier_hist = []
            for i in range(15, len(history_series)):
                sp = get_sub_parts(history_series[:i], max_limit)
                for p, nums in sp.items():
                    if history_series[i] in nums:
                        tier_hist.append(p); break
                else: tier_hist.append('0')
            
            s_pred = find_best_sequence(tier_hist) if tier_hist else "H1"
            
            # B. Sniper Selection
            current_sp = get_sub_parts(history_series[-15:], max_limit)
            top_parts = [s_pred]
            all_p = ['H1', 'H2', 'H3', 'M1', 'M2', 'M3', 'L1', 'L2', 'L3']
            for p in all_p:
                if len(top_parts) >= 3: break
                if p not in top_parts: top_parts.append(p)
            
            target_nums = list(set(current_sp[top_parts[0]] + current_sp[top_parts[1]] + current_sp[top_parts[2]]))

            # C. SUPER STRONG VOTE LOGIC (Har shift mein Lal Dabbe)
            tfs = [3, 5, 7, 10, 14, 15, 20, 25, 30]
            vote_tally = {n: 0 for n in target_nums}
            for tf in tfs:
                if len(history_series) < tf: continue
                counts = Counter(history_series[-tf:])
                for n in target_nums:
                    if n in counts: vote_tally[n] += (counts[n] * (30/tf)) # Weightage
            
            jackpots = sorted(target_nums, key=lambda x: vote_tally[x], reverse=True)[:5]
            return target_nums, jackpots, top_parts, vote_tally

        def render_ank(nums, jackpots, votes):
            nums.sort()
            html = "<div style='display: flex; flex-wrap: wrap; gap: 8px;'>"
            for n in nums:
                bg = "#FF4B4B" if n in jackpots else "#2e2e2e"
                border = "2px solid #ff9999" if n in jackpots else "1px solid #444"
                v = int(votes.get(n, 0))
                html += f"<div style='background:{bg}; padding:10px; border-radius:8px; text-align:center; min-width:45px; border:{border};'>" \
                        f"<span style='font-size:22px; font-weight:bold; color:white;'>{n:02d}</span><br>" \
                        f"<span style='font-size:10px; color:#ddd;'>{v}v</span></div>"
            html += "</div>"
            return html

        # --- 3. DISPLAY SHIFTS ---
        for shift in shift_order:
            if shift not in df.columns: continue
            
            # Prediction for T+1 using data up to T
            history_today = filtered_df[shift].dropna().astype(int).tolist()
            if len(history_today) < 20: continue
            
            st.markdown("---")
            st.subheader(f"🧩 Shift: {shift}")

            with st.spinner(f"{shift} ka 'Open Record' match kiya jaa raha hai..."):
                # Prediction for Tomorrow (T+1)
                pred_nums, jackpots, parts, votes = get_brahmastra_prediction(history_today, [])
                
                # ACTUAL Result of Tomorrow (T+1) from full Excel
                actual_row_next = df[df['DATE'].dt.date == target_date_next]
                actual_val_next = int(actual_row_next.iloc[0][shift]) if not actual_row_next.empty and pd.notna(actual_row_next.iloc[0][shift]) else None
                
                is_hit = (actual_val_next in pred_nums) if actual_val_next is not None else False

            # UI Display
            c_res, c_stat = st.columns([1, 2.5])
            with c_res:
                if actual_val_next is not None:
                    m_color = "#28a745" if is_hit else "#FF4B4B"
                    st.markdown(f"<div style='background:{m_color}; padding:10px; border-radius:8px; text-align:center; color:white;'>"
                                f"Match Result ({target_date_next.strftime('%d %b')}):<br><b style='font-size:26px;'>{actual_val_next:02d}</b><br>{'HIT! ✅' if is_hit else 'MISS ❌'}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background:#555; padding:10px; border-radius:8px; text-align:center; color:white;'>"
                                f"Result ({target_date_next.strftime('%d %b')}):<br><b>Waiting...</b></div>", unsafe_allow_html=True)
            
            with c_stat:
                st.markdown(f"<div style='border:2px solid #00FF7F; padding:10px; border-radius:8px; background:#00FF7F15;'>"
                            f"<b style='color:#00FF7F; font-size:18px;'>🎯 SNIPER MODE ACTIVE (T+1 Match)</b><br>"
                            f"Selected Parts: <b>{', '.join(parts)}</b> | Har shift mein Super Strong Lal Dabbe tayyar hain.</div>", unsafe_allow_html=True)

            st.markdown(f"**Target Numbers For {target_date_next.strftime('%d %b')}:**")
            st.markdown(render_ank(pred_nums, jackpots, votes), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")
        
