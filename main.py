import streamlit as st
import pandas as pd
import DGmodel as DG
import time
import utils

pd.options.display.float_format = "{:,.0f}".format

if 'DG_model' not in st.session_state:
    DG_instance = DG.DG_instance(
        SignallingEscrowMinLockTime=5 * 60 * 60,
        ProposalExecutionMinTimelock=3 * 24 * 60 * 60,
        FirstSealRageQuitSupport=0.1,
        SecondSealRageQuitSupport=0.5,
        VetoSignallingDeactivationMaxDuration=3 * 24 * 60 * 60,
        DynamicTimelockMinDuration=5 * 24 * 60 * 60,
        DynamicTimelockMaxDuration=45 * 24 * 60 * 60,
        VetoSignallingMinActiveDuration=5 * 60 * 60,
        RageQuitExtensionDelay=7 * 24 * 60 * 60,
        RageQuitEthClaimTimelockGrowthStartSeqNumber=0,
        RageQuitEthWithdrawalsMinDelay=60 * 24 * 60 * 60,
        RageQuitEthWithdrawalsMaxDelay=180 * 24 * 60 * 60,
        RageQuitEthWithdrawalsDelayGrowth=15 * 24 * 60 * 60,
        VetoCooldownDuration=5 * 60 * 60)
    st.session_state['DG_model'] = DG_instance

if 'players_amount' not in st.session_state:
    st.session_state['players_amount'] = 20

if 'game_log' not in st.session_state:
    st.session_state['game_log'] = {}

if 'total_in' not in st.session_state:
    st.session_state['total_in'] = 0

if 'total_out' not in st.session_state:
    st.session_state['total_out'] = 0

if 'stETH_per_player' not in st.session_state:
    st.session_state['stETH_per_player'] = 0

if 'turn_result' not in st.session_state:
    st.session_state['turn_result'] = pd.DataFrame()

if 'display_df' not in st.session_state:
    st.session_state['display_df'] = pd.DataFrame()


st.title('Dual Governance The Game')

st.sidebar.write('**Actions**')

with st.sidebar.form("Players amount"):
    st.write('Enter amount of players')
    new_players_amount = st.number_input('Enter amount', step=1)

    start_new_game = st.form_submit_button('Start New Game')
    if start_new_game:
        st.session_state['players_amount'] = new_players_amount
        st.session_state['stETH_per_player'] = utils.initial_st_eth/new_players_amount
        st.session_state['game_log'] = {}
        st.session_state['total_in'] = 0
        st.session_state['total_out'] = 0
        st.session_state['turn_result'] = pd.DataFrame()
        st.session_state['display_df'] = pd.DataFrame()

with st.sidebar.form("Start a new scenario"):
    st.write('New Scenario')
    start_new_scenario = st.form_submit_button('Start New Scenario')
    if start_new_scenario:
        st.session_state['game_log'] = {}
        st.session_state['total_in'] = 0
        st.session_state['total_out'] = 0
        st.session_state['turn_result'] = pd.DataFrame()
        st.session_state['display_df'] = pd.DataFrame()


with st.sidebar.form("Turn info"):
    st.write('Enter turn info')
    day = st.number_input('Day number', step=1)
    amount_in = st.number_input('Amount in', step=1)
    amount_out = st.number_input('Amount out', step=1)
    process_turn = st.form_submit_button('Process Turn')
    show_futrure = st.form_submit_button('Show Futrure')
    if process_turn:
        st.session_state['total_in'] +=  amount_in
        st.session_state['total_out'] += amount_out

        try:
            st.session_state['game_log'][day] = {'step': int(day), 'result': amount_in - amount_out, 'amount_in': amount_in,
                              'amount_out': amount_out}
        except TypeError:
            st.session_state['game_log'][day] = {'step': int(day), 'result': 0, 'amount_in': 0, 'amount_out': 0}

        current_timestamp = int(time.time())
        turn_result=utils.process_turn(game_log=st.session_state['game_log'],dg_instance=st.session_state['DG_model'],stETH_PER_PLAYER=st.session_state['stETH_per_player']).show_log()
        try:
            turn_result['start_date'] = pd.to_datetime(turn_result['timestamp'], unit='s').dt.strftime('%d-%m-%Y')
            turn_result['end_date'] = pd.to_datetime(turn_result['end_timestamp'], unit='s').dt.strftime('%d-%m-%Y')
            display_df = turn_result[turn_result['timestamp'] < (current_timestamp + day * 86400 + 86400 * 2)]
            display_df = display_df[['event', 'start_date', 'end_date', 'waiting_time']]
        except TypeError:
            display_df = pd.DataFrame({'event': [], 'start_date': [], 'end_date': [], 'waiting_time': []})

        st.session_state['turn_result'] = turn_result
        st.session_state['display_df'] = display_df

    if show_futrure:
        current_timestamp = int(time.time())
        display_df = st.session_state['turn_result'][st.session_state['turn_result']['timestamp'] < (current_timestamp + day * 86400 + 86400 * 2)]
        display_df = display_df[['event', 'start_date', 'end_date', 'waiting_time']]
        st.session_state['display_df'] = display_df

st.markdown(
    """
    <style>
    .custom-dataframe table {
        font-size: 30px;  /* Font size */
        font-family: Arial, sans-serif;  /* Font family */
        width: 100%;  /* Make table take full width of the container */
    }
    .custom-dataframe {
        width: 140%;  /* Width of the entire table container */
        margin: 0;  /* Center-align the table */
    }
    </style>
    """, unsafe_allow_html=True
)

col1, col2 =  st.columns(2)

with col1:
    st.write(f"Total in: {st.session_state['total_in']}")

with col2:
    st.write(f"Total out: {st.session_state['total_out']}")


# Display the DataFrame as HTML with custom styling
st.markdown(f"<div class='custom-dataframe'>{st.session_state['display_df'].to_html(index=False)}</div>", unsafe_allow_html=True)




