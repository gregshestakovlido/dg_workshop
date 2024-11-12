import time
import DGmodel as DG

initial_st_eth = 9808927
initial_others_staked_eth = 23914309
initial_steth_in_opposition = 0

def process_turn(game_log,dg_instance,stETH_PER_PLAYER):
    dg_instance.reset_dg_instance()
    scenario=DG.simulation(initial_st_eth,initial_others_staked_eth,0)
    current_timestamp=int(time.time())
    scenario.generate_events_flow(current_timestamp,current_timestamp+86400*700)
    initial_point=current_timestamp+86400
    for turn in game_log:
        scenario.change_opposition_stETH_amount(stETH_PER_PLAYER*game_log[turn]['result'],initial_point+game_log[turn]['step']*86400)

    try:
        dg_instance.process_simulation(scenario)
    except IndexError:
        return dg_instance

    return dg_instance