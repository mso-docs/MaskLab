"""TASK-003: REQ-009/012/020/021. Simulation cannot masquerade as inference."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
import json
import os
from pathlib import Path
from decimal import Decimal
import httpx
from .contracts import canonical, strict_json
from .budget import configured_ledger

ENDPOINT = 'https://api.tokenfactory.nebius.com/v1'


@dataclass
class ProviderError(Exception):
    code: str
    uncertain: bool = False
    transient: bool = False


class SimulatedProvider:
    simulation = True
    async def complete(self, request, cfg, ordinal):
        await asyncio.sleep(0.01)
        scenario = cfg['simulation_scenario']
        if scenario == 'mixed':
            scenario = ['success','invalid','refusal','timeout','transient','unknown_usage'][int(request['key'][-1]) % 6]
        if scenario == 'timeout':
            raise ProviderError('SIMULATED_ACCEPTED_TIMEOUT', uncertain=True)
        if scenario == 'transient' and ordinal == 1:
            raise ProviderError('SIMULATED_RATE_LIMIT', transient=True)
        # This intentionally does not receive the answer key. It emits fixed strings to exercise scoring.
        text = '{"answer":"5"}'
        if scenario == 'invalid':
            text = 'SIMULATED malformed final response'
        refusal = scenario == 'refusal'
        if refusal:
            text = 'SIMULATED refusal'
        return {'final_text': text, 'refused': refusal, 'usage': None if scenario == 'unknown_usage' else {'input_tokens': 30, 'output_tokens': 8}, 'provider_request_id': 'simulated-' + str(ordinal), 'serving_revision': 'simulated-contract-v1', 'endpoint': 'simulated://local', 'simulation': True, 'raw_metadata': {'finish_reason': 'stop', 'simulation': True}}


class NebiusProvider:
    simulation = False
    def __init__(self, capability_file=None, transport=None):
        self.endpoint = os.getenv('NEBIUS_BASE_URL', ENDPOINT).rstrip('/')
        if self.endpoint != ENDPOINT:
            raise ValueError('Endpoint is not allowlisted')
        self.key = os.getenv('NEBIUS_API_KEY', '')
        self.capability_file = capability_file or os.getenv('MASKLAB_CAPABILITIES_FILE', '')
        self.transport = transport

    def capabilities(self):
        if not self.capability_file:
            raise ValueError('External reviewed capability/price file required; live semantics unverified')
        try:
            value = strict_json(Path(self.capability_file).read_bytes())
        except (OSError,ValueError):
            raise ValueError('Cannot read reviewed capability configuration; private file details omitted') from None
        if value.get('endpoint') != self.endpoint or value.get('output_parameter') not in ('max_tokens','max_completion_tokens') or value.get('billed_output_includes_reasoning') is not True:
            raise ValueError('Review actual output/reasoning billing semantics before enabling inference')
        return value

    def preflight(self, cfg, require_funding=True):
        if not self.key:
            raise ValueError('Nebius credential missing; configure externally on the server')
        cap = self.capabilities()
        if require_funding:
            approved = Decimal(os.getenv('MASKLAB_APPROVED_SPEND_USD', '0'))
            if not approved.is_finite() or not 0 < approved <= 10 or Decimal(cfg['budget_usd']) > approved:
                raise ValueError('Explicit paid-call authorization and sufficient approved ceiling required')
            ledger = configured_ledger().snapshot()
            if ledger['halted']:
                raise ValueError('Cumulative spend ledger is halted; reconcile usage before more calls')
        if Decimal(cfg['budget_usd']) <= 0 or Decimal(cfg['input_price_per_million']) <= 0 or Decimal(cfg['output_price_per_million']) <= 0:
            raise ValueError('Live calls require nonzero reviewed prices and budget')
        for model in cfg['models']:
            details = cap.get('models', {}).get(model)
            if not details or (not details.get('inference_verified') and cfg.get('purpose') != 'access_smoke'):
                raise ValueError('Inference access unverified for selected model; explicit funded smoke required')
            if 'temperature' not in details.get('parameters', []):
                raise ValueError('Selected model does not explicitly support temperature')
            if str(details.get('input_price_per_million')) != cfg['input_price_per_million'] or str(details.get('output_price_per_million')) != cfg['output_price_per_million']:
                raise ValueError('Protocol price differs from reviewed capability file')
            for name in ('enable_thinking','response_format'):
                if cfg.get(name) is not None and name not in details.get('parameters',[]):
                    raise ValueError('Unsupported explicitly selected provider parameter: '+name)
        if cfg.get('output_parameter') and cfg['output_parameter'] != cap['output_parameter']:
            raise ValueError('Frozen output-cap parameter differs from reviewed capability')
        if cfg.get('dual_output_cap') and not cap.get('dual_output_cap'):
            raise ValueError('Dual output ceiling is not reviewed for this model')
        return cap

    def bind_config(self,cfg):
        cap=self.capabilities()
        settings=cfg.model_dump()
        for field in ('output_parameter','dual_output_cap','enable_thinking','response_format','service_tier'):
            if settings[field] is None:
                settings[field]=cap.get(field)
        bound=type(cfg).model_validate(settings)
        self.preflight(bound.model_dump())
        return bound

    async def list_models(self):
        if not self.key:
            raise ValueError('Server credential missing')
        async with httpx.AsyncClient(timeout=30, follow_redirects=False, transport=self.transport) as client:
            try:
                result = await client.get(self.endpoint + '/models', headers={'Authorization': 'Bearer ' + self.key})
                result.raise_for_status()
                return {'models': [x['id'] for x in result.json().get('data', [])], 'inference_access': 'UNVERIFIED', 'endpoint': self.endpoint}
            except (httpx.HTTPError, ValueError, KeyError):
                raise ValueError('Model discovery failed; provider details omitted to protect credentials') from None

    async def complete(self, request, cfg, ordinal):
        cap = self.preflight(cfg)
        output_parameter=cfg.get('output_parameter') or cap['output_parameter']
        payload = {'model': request['key'][0], 'messages': request['messages'], 'temperature': cfg['temperature'], output_parameter: cfg['max_output_tokens'], 'stream': False, 'n':1, 'store':False, 'service_tier':cfg.get('service_tier') or 'default'}
        if cfg.get('dual_output_cap'):
            payload.update(max_tokens=cfg['max_output_tokens'],max_completion_tokens=cfg['max_output_tokens'])
        if cfg.get('enable_thinking') is not None:
            payload['chat_template_kwargs']={'enable_thinking':cfg['enable_thinking']}
        if cfg.get('response_format'):
            payload['response_format']={'type':cfg['response_format']}
        async with httpx.AsyncClient(timeout=httpx.Timeout(60, connect=10), follow_redirects=False, transport=self.transport) as client:
            try:
                response = await client.post(self.endpoint + '/chat/completions', headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'}, json=payload)
            except (httpx.ConnectTimeout, httpx.ConnectError):
                raise ProviderError('CONNECT_FAILED', transient=True) from None
            except httpx.HTTPError:
                raise ProviderError('AMBIGUOUS_TRANSPORT', uncertain=True) from None
        if response.status_code == 429:
            raise ProviderError('RATE_LIMITED', transient=True)
        if response.status_code >= 500:
            raise ProviderError('AMBIGUOUS_PROVIDER_ERROR', uncertain=True)
        if response.status_code != 200:
            raise ProviderError('PROVIDER_REJECTED_' + str(response.status_code))
        try:
            data = response.json()
            if data.get('model') != request['key'][0]:
                raise ProviderError('SERVED_MODEL_MISMATCH',uncertain=True)
            choice = data['choices'][0]
            msg = choice['message']
            text = msg.get('content') or ''
            if not isinstance(text, str) or len(text.encode()) > 1024*1024:
                raise ValueError('Invalid response size/type')
            usage = data.get('usage')
            normalized_usage = None
            if usage and all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('prompt_tokens','completion_tokens')):
                normalized_usage = {'input_tokens': usage['prompt_tokens'], 'output_tokens': usage['completion_tokens']}
                reasoning = (usage.get('completion_tokens_details') or {}).get('reasoning_tokens')
                total = usage.get('total_tokens')
                if reasoning is not None and (type(reasoning) is not int or not 0 <= reasoning <= usage['completion_tokens']):
                    normalized_usage=None
                elif total is not None and (type(total) is not int or total != usage['prompt_tokens']+usage['completion_tokens']):
                    normalized_usage=None
                elif reasoning is not None:
                    normalized_usage['reasoning_tokens']=reasoning
                if normalized_usage is not None and total is not None:
                    normalized_usage['total_tokens']=total
            # Only reviewed fields are retained. No headers, tokens, reasoning traces or provider error bodies.
            return {'final_text': text, 'refused': bool(msg.get('refusal')), 'usage': normalized_usage, 'provider_request_id': str(data.get('id','unknown'))[:200], 'serving_revision': str(data.get('system_fingerprint') or 'unknown')[:200], 'endpoint': self.endpoint, 'simulation': False, 'raw_metadata': {'finish_reason': str(choice.get('finish_reason','unknown'))[:80], 'model': str(data.get('model','unknown'))[:200], 'provider_created': data.get('created'), 'service_tier': data.get('service_tier') or 'unknown', 'usage_details': {'completion_tokens_details': (usage or {}).get('completion_tokens_details'), 'prompt_tokens_details': (usage or {}).get('prompt_tokens_details')}}}
        except (ValueError, KeyError, TypeError, IndexError):
            raise ProviderError('AMBIGUOUS_MALFORMED_RESPONSE', uncertain=True) from None


def provider_for(cfg):
    return SimulatedProvider() if cfg['provider'] == 'simulated' else NebiusProvider()
