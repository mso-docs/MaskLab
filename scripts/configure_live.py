"""TASK-013 / REQ-009/020/021: record the operator's explicit USD10 additional grant.
No inference. Does not expose or rewrite the key. Re-running cannot reset/increase the grant.
"""
import json
import os
from pathlib import Path
from masklab.runtime import load_env_file
from masklab.budget import SpendLedger
from masklab.provider import ENDPOINT
from masklab.store import now

root=Path(__file__).resolve().parents[1]
load_env_file(root/'.env')
model=os.environ['NEBIUS_MODEL']
discovery=json.loads((root/'artifacts/live-verification/discovery.json').read_text())
assert discovery['listed'] and discovery['selected_model']==model
identity='masklab-additional-nebius-20261028-usd10'
ledger=root/'artifacts/private/nebius-spend.sqlite3'
capfile=root/'artifacts/private/nebius-capabilities.json'
SpendLedger.initialize(ledger,identity,'10')
if not capfile.exists():
    cap={'schema_version':1,'reviewed_at':now(),'endpoint':ENDPOINT,'output_parameter':'max_completion_tokens','dual_output_cap':True,'enable_thinking':False,'response_format':'json_object','service_tier':'default','billed_output_includes_reasoning':True,'models':{model:{'inference_verified':False,'parameters':['temperature','enable_thinking','response_format','max_tokens','max_completion_tokens','service_tier'],'input_price_per_million':'0.06','output_price_per_million':'0.24','context_tokens':1048576}},'sources':['https://nebius.com/services/token-factory/models/nvidia-nemotron-models-inference','https://docs.tokenfactory.nebius.com/api-reference/inference/create-chat-completion','https://api.tokenfactory.nebius.com/openapi.json','https://github.com/nebius/nebius-physical-ai/blob/main/docs/workbench/token-factory-deprecation-verification.md'],'billing_review':'Reserve uncached input at list price and all completion tokens, including reasoning, at output price. Reasoning is a subset of completion, not an additional charge. max_completion_tokens bounds total generation; matching max_tokens supplied. Observed usage/cap behavior pending one-request smoke. Provider invoice not independently reconciled.'}
    fd=os.open(capfile,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(cap,f,indent=2)
updates={'MASKLAB_APPROVED_SPEND_USD':'10','MASKLAB_SPEND_LEDGER':str(ledger),'MASKLAB_AUTHORIZATION_ID':identity,'MASKLAB_CAPABILITIES_FILE':str(capfile)}
p=root/'.env';lines=p.read_text().splitlines();out=[];seen=set()
for line in lines:
    name=line.split('=',1)[0].strip()
    if name in updates:
        out.append(name+'='+updates[name]);seen.add(name)
    else:out.append(line)
out+=['','\n# Explicit operator authorization: USD10 cumulative additional inference; no automatic top-ups.']
out += [k+'='+v for k,v in updates.items() if k not in seen]
p.write_text('\n'.join(out)+'\n');os.chmod(p,0o600)
print(json.dumps({'selected_model':model,'additional_limit_usd':'10','guard_initialized':True,'inference_performed':False,'automatic_topups':False}))
