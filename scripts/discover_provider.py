"""TASK-013 / TEST-009: read-only discovery; never logs headers, keys or error bodies."""
import asyncio
import json
import os
from pathlib import Path
import httpx
from masklab.runtime import load_env_file
from masklab.provider import ENDPOINT
from masklab.store import now

async def main():
    load_env_file('.env')
    endpoint=os.environ['NEBIUS_BASE_URL'].rstrip('/')
    if endpoint != ENDPOINT:raise ValueError('Endpoint not allowlisted')
    key=os.environ['NEBIUS_API_KEY'];model=os.environ['NEBIUS_MODEL']
    async with httpx.AsyncClient(timeout=30,follow_redirects=False) as client:
        try:
            r=await client.get(endpoint+'/models',headers={'Authorization':'Bearer '+key})
            if r.status_code!=200:raise ValueError(f'Model discovery HTTP {r.status_code}; response omitted')
            models=r.json().get('data',[]);selected=next((m for m in models if m.get('id')==model),None)
            result={'timestamp':now(),'endpoint':endpoint,'selected_model':model,'listed':selected is not None,'model_count':len(models),'inference_access':'UNVERIFIED'}
            if selected:
                allowed={'id','owned_by','created','context_length','max_model_len','pricing','capabilities','supported_parameters','metadata','architecture','input_token_price','output_token_price'}
                result['catalog_record']={k:v for k,v in selected.items() if k in allowed}
                result['catalog_fields']=sorted(selected)
            text=json.dumps(result,indent=2)
            if key in text:raise ValueError('Secret reflected by provider; output blocked')
            Path('artifacts/live-verification/discovery.json').write_text(text)
            print(text)
            for path in ('/openapi.json','/docs'):
                doc=await client.get('https://api.tokenfactory.nebius.com'+path)
                if doc.status_code==200:
                    Path('artifacts/live-verification/provider'+('.json' if path.endswith('json') else '.html')).write_bytes(doc.content)
                    print(json.dumps({'public_document':path,'status':doc.status_code,'bytes':len(doc.content)}))
        except httpx.HTTPError:
            raise SystemExit('Discovery transport failed; credential/request details omitted') from None

asyncio.run(main())
