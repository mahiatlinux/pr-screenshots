import json
from core.inference.safetensors_agentic import run_safetensors_tool_loop
from state.ssh_approvals import approved_hosts, reset_ssh_approvals
from state.tool_approvals import resolve_tool_decision

for verdict in ['deny','allow']:
    reset_ssh_approvals()
    turns=iter(['<tool_call>{"name":"terminal","arguments":{"command":"ssh deploy@approved.example uptime"}}</tool_call>', 'Done.'])
    def single_turn(messages):
        yield next(turns)
    execution=[]
    def execute(name, arguments, **kwargs):
        execution.append(sorted(approved_hosts('loop-ssh')))
        return 'recorded'
    events=[]
    for event in run_safetensors_tool_loop(single_turn=single_turn,messages=[{'role':'user','content':'Deploy'}],tools=[{'type':'function','function':{'name':'terminal'}}],execute_tool=execute,session_id='loop-ssh',confirm_tool_calls=True,permission_mode='ask'):
        events.append(event)
        if event['type']=='tool_start' and event.get('awaiting_confirmation'):
            assert resolve_tool_decision(event['approval_id'],verdict,session_id='loop-ssh')
    assert execution == ([['approved.example']] if verdict=='allow' else [])
    assert approved_hosts('loop-ssh') == (frozenset(['approved.example']) if verdict=='allow' else frozenset())
    print(json.dumps({'decision':verdict,'execution_approvals':execution,'events':[e['type'] for e in events]}))
