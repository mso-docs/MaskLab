"""TASK-003 / TEST-009/012/020/021: HTTP contract tests, never a live socket."""
import json
import pytest
import httpx
from masklab.provider import NebiusProvider, ProviderError, ENDPOINT
from masklab.contracts import ProtocolConfig

@pytest.fixture
def live(tmp_path,monkeypatch):
    model='nvidia/nemotron-contract'
    cap={'endpoint':ENDPOINT,'output_parameter':'max_tokens','billed_output_includes_reasoning':True,'models':{model:{'inference_verified':True,'parameters':['temperature'],'input_price_per_million':'1','output_price_per_million':'2'}}}
    file=tmp_path/'capabilities.json';file.write_text(json.dumps(cap))
    monkeypatch.setenv('NEBIUS_API_KEY','test-credential-never-retained')
    monkeypatch.setenv('MASKLAB_APPROVED_SPEND_USD','1')
    monkeypatch.delenv('NEBIUS_BASE_URL',raising=False)
    cfg=ProtocolConfig(provider='nebius',models=[model],budget_usd='1',input_price_per_million='1',output_price_per_million='2').model_dump()
    return file,cap,cfg

async def test_http_contract_metadata_redaction(live):
    file,cap,cfg=live
    def handler(req):
        data=json.loads(req.content)
        assert data['max_tokens']==512 and data['model']==cfg['models'][0] and data['stream'] is False
        return httpx.Response(200,json={'model':cfg['models'][0],'id':'provider-id','system_fingerprint':'revision','choices':[{'message':{'content':'{"answer":"A"}','reasoning_content':'PRIVATE TRACE NEVER RETAINED'},'finish_reason':'stop'}],'usage':{'prompt_tokens':12,'completion_tokens':4},'secret_extra':'DROP'},headers={'Authorization':'secret-header'})
    provider=NebiusProvider(str(file),httpx.MockTransport(handler))
    result=await provider.complete({'key':[cfg['models'][0]],'messages':[{'role':'user','content':'q'}]},cfg,1)
    assert result['usage']=={'input_tokens':12,'output_tokens':4}
    assert result['simulation'] is False and result['provider_request_id']=='provider-id'
    assert 'PRIVATE TRACE' not in json.dumps(result) and 'secret' not in json.dumps(result)

@pytest.mark.parametrize('status,uncertain,transient',[(429,False,True),(500,True,False),(503,True,False),(401,False,False),(400,False,False)])
async def test_http_failure_taxonomy(live,status,uncertain,transient):
    file,cap,cfg=live
    provider=NebiusProvider(str(file),httpx.MockTransport(lambda req:httpx.Response(status,json={'error':'secret canary'})))
    with pytest.raises(ProviderError) as e:await provider.complete({'key':[cfg['models'][0]],'messages':[]},cfg,1)
    assert e.value.uncertain is uncertain and e.value.transient is transient
    assert 'secret' not in e.value.code


def test_unverified_parameters_funding_and_prices_block(live,monkeypatch):
    file,cap,cfg=live
    cap['models'][cfg['models'][0]]['parameters']=[];file.write_text(json.dumps(cap))
    with pytest.raises(ValueError,match='temperature'):NebiusProvider(str(file)).preflight(cfg)
    cap['models'][cfg['models'][0]]['parameters']=['temperature'];cap['models'][cfg['models'][0]]['inference_verified']=False;file.write_text(json.dumps(cap))
    with pytest.raises(ValueError,match='Inference'):NebiusProvider(str(file)).preflight(cfg)
    cap['models'][cfg['models'][0]]['inference_verified']=True;file.write_text(json.dumps(cap))
    monkeypatch.setenv('MASKLAB_APPROVED_SPEND_USD','0')
    with pytest.raises(ValueError,match='authorization'):NebiusProvider(str(file)).preflight(cfg)

async def test_reasoning_usage_is_subset_not_double_charged(live):
    file,cap,cfg=live
    cfg.update(output_parameter='max_completion_tokens',dual_output_cap=True,enable_thinking=False,response_format='json_object')
    cap.update(output_parameter='max_completion_tokens',dual_output_cap=True)
    cap['models'][cfg['models'][0]]['parameters']+=['enable_thinking','response_format'];file.write_text(json.dumps(cap))
    def handler(req):
        body=json.loads(req.content)
        assert body['max_completion_tokens']==body['max_tokens']==512
        assert body['chat_template_kwargs']=={'enable_thinking':False}
        assert body['response_format']=={'type':'json_object'} and body['store'] is False
        return httpx.Response(200,json={'model':cfg['models'][0],'id':'receipt','choices':[{'message':{'content':'{"answer":"A"}'},'finish_reason':'stop'}],'usage':{'prompt_tokens':10,'completion_tokens':20,'total_tokens':30,'completion_tokens_details':{'reasoning_tokens':15}}})
    result=await NebiusProvider(str(file),httpx.MockTransport(handler)).complete({'key':[cfg['models'][0]],'messages':[]},cfg,1)
    assert result['usage']=={'input_tokens':10,'output_tokens':20,'reasoning_tokens':15,'total_tokens':30}
