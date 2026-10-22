import asyncio
import json
from types import SimpleNamespace
import httpx
import pytest
from amplifier_decisions import DecisionRequest, Question
from amplifier_module_provider_jev import JevProvider, mount

QUESTIONS=(Question('visible','predicate','Visible?'), Question('next','choice','Choose',{'save':'Save','cancel':'Cancel'}), Question('progress','score','Rate',levels=('None','Done')))
REQUEST=DecisionRequest({'page':'Synthetic'},QUESTIONS,allow_external_state=True)
PAYLOAD={'model':'jev-test','usage':{'input_tokens':5},'answers':{'visible':{'type':'noul','noul':.9},'next':{'type':'choice','choice':'save','probabilities':{'save':.9,'cancel':.1},'confidence':.8},'progress':{'type':'score','score':.8,'probabilities':{'0':.2,'1':.8},'confidence':.7}}}

def coordinator():
    c=SimpleNamespace(caps={},mounted=[])
    c.get_capability=lambda name:c.caps.get(name)
    c.register_capability=lambda name,value:c.caps.__setitem__(name,value)
    async def mounted(*args,**kwargs):c.mounted.append(args)
    c.mount=mounted
    return c

async def test_reuses_configured_account_and_transport_without_ambient_key(monkeypatch):
    monkeypatch.delenv('TYPESAFE_API_KEY',raising=False)
    seen=[]
    def handler(req):
        seen.append(req)
        return httpx.Response(200,json=PAYLOAD,headers={'x-request-id':'owned'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider=JevProvider(api_key='private-configured',client=client)
        backend=provider.decision_backend({'model':'jev-test'})
        result=await backend.decide(REQUEST)
        assert all(a.status=='answered' for a in result.answers.values())
        assert seen[0].headers['authorization']=='Bearer private-configured'
        assert json.loads(seen[0].content)['questions']['visible']['type']=='noul'
        assert result.request_id=='owned' and result.usage=={'input_tokens':5}
        assert 'private' not in repr(result)
        await backend.close();await provider.close()
        assert not client.is_closed

@pytest.mark.parametrize('status',[302,400,401,413,422,429,500])
async def test_failures_are_redacted_and_not_retried(status):
    seen=[]
    def handler(req):
        seen.append(req);return httpx.Response(status,text='PRIVATE-EVIDENCE',headers={'location':'https://other.test'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        backend=JevProvider(api_key='key',client=client).decision_backend({'model':'jev-test'})
        result=await backend.decide(REQUEST)
        assert len(seen)==1 and 'PRIVATE' not in repr(result)
        assert all(a.status in {'invalid','unavailable'} for a in result.answers.values())

async def test_no_consent_or_invalid_question_makes_no_call():
    provider=JevProvider(api_key='key');backend=provider.decision_backend({'model':'jev-test'})
    for request in [DecisionRequest('x',QUESTIONS),DecisionRequest('x',(),allow_external_state=True)]:
        await backend.decide(request)
        assert provider._client is None

async def test_cancel_propagates_and_timeout_has_no_retry():
    calls=[]
    async def handler(req):
        calls.append(req);await asyncio.sleep(20)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        backend=JevProvider(api_key='key',client=client).decision_backend({'model':'jev-test'})
        timed=await backend.decide(DecisionRequest('x',QUESTIONS,timeout_seconds=.01,allow_external_state=True))
        assert timed.answers['next'].reason=='timeout' and len(calls)==1
        task=asyncio.create_task(backend.decide(REQUEST));await asyncio.sleep(.01);task.cancel()
        with pytest.raises(asyncio.CancelledError):await task
        assert len(calls)==2

async def test_opt_in_and_decision_only_mount_and_owned_cleanup():
    c=coordinator();assert await mount(c,{'api_key':'key'}) is None
    assert not c.caps
    cleanup=await mount(c,{'api_key':'key','decisions':{'enabled':True,'backends':{
        'browser':{'enabled':True,'model':'jev-test'},'computer':{'enabled':False,'model':'jev-test'}}}})
    assert list(c.caps['decision.backends'])==['browser'] and not c.mounted
    replacement=object();c.caps['decision.backends']['browser']=replacement
    await cleanup();assert c.caps['decision.backends']['browser'] is replacement
