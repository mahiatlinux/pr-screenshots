import asyncio
import json
import os
from pathlib import Path
from types import SimpleNamespace
import pytest
from hub.services.models import gguf_variants
from hub.utils import download_manifest, inventory_scan, state_dir

@pytest.mark.parametrize('mode', ['local', 'offline', 'fallback', 'pinned'])
@pytest.mark.parametrize('transport', ['http', 'xet'])
@pytest.mark.parametrize('marker', [False, True])
def test_companion_lifecycle(tmp_path, monkeypatch, mode, transport, marker):
    repo = 'Org/CompanionRepo'
    quant = 'UD-Q4_K_XL'
    hub = tmp_path / 'hub'
    entry = hub / 'models--Org--CompanionRepo'
    snap = entry / 'snapshots' / ('a' * 40)
    snap.mkdir(parents=True)
    (entry / 'blobs').mkdir()
    (entry / 'refs').mkdir()
    (entry / 'refs/main').write_text(snap.name)
    name = 'Model-UD-Q4_K_XL.gguf'
    (snap / name).write_bytes(b'm')
    (snap / 'Model-Q8_0.gguf').write_bytes(b'8')
    monkeypatch.setattr(state_dir, 'cache_root', lambda: tmp_path / 'state')
    monkeypatch.setattr(inventory_scan, 'hf_cache_roots', lambda **kw: [hub])
    monkeypatch.setattr('utils.hf_cache_settings.get_hf_cache_paths', lambda: SimpleNamespace(hub_cache=hub))
    def offline(*a, **kw):
        raise OSError('offline fixture')
    monkeypatch.setattr(gguf_variants, 'list_gguf_variants', offline)
    kwargs = {'prefer_local_cache': mode in ('local', 'pinned'), 'offline': mode == 'offline'}
    if mode == 'pinned':
        kwargs['local_path'] = str(snap)
    download_manifest.write_manifest('model', repo, quant, [download_manifest.ExpectedFile(path=name, size=1), download_manifest.ExpectedFile(path='MTP/mtp-Q8_0.gguf', size=2)], transport, hub_cache=hub)
    if marker:
        download_manifest.write_cancel_marker('model', repo, quant, transport, hub_cache=hub)
    inventory_scan.invalidate_hf_cache_scans()
    result = asyncio.run(gguf_variants.get_gguf_variants_response(repo, **kwargs))
    row = next(v for v in result.variants if v.quant == quant)
    assert row.partial and not row.downloaded
    assert row.partial_transport == transport
    assert result.default_variant == 'Q8_0'
    (snap / 'MTP').mkdir()
    (snap / 'MTP/mtp-Q8_0.gguf').write_bytes(b'mt')
    download_manifest.clear_cancel_marker('model', repo, quant, hub_cache=hub)
    inventory_scan.invalidate_hf_cache_scans()
    complete = asyncio.run(gguf_variants.get_gguf_variants_response(repo, **kwargs))
    ready = next(v for v in complete.variants if v.quant == quant)
    assert ready.downloaded and not ready.partial
    assert complete.default_variant == quant
    inventory_scan.invalidate_hf_cache_scans()

def test_complete_sibling_with_newer_cancelled_attempt(tmp_path, monkeypatch):
    repo='Org/SiblingRepo'
    hub=tmp_path/'hub'
    entry=hub/'models--Org--SiblingRepo'
    old=entry/'snapshots/old'
    new=entry/'snapshots/new'
    old.mkdir(parents=True)
    new.mkdir()
    (old/'Model-Q4_K_M.gguf').write_bytes(b'4')
    (new/'Model-Q8_0.gguf').write_bytes(b'8')
    (entry/'blobs').mkdir()
    (entry/'refs').mkdir()
    (entry/'refs/main').write_text('new')
    os.utime(old,(1,1))
    os.utime(new,(2,2))
    monkeypatch.setattr(state_dir,'cache_root',lambda: tmp_path/'state')
    monkeypatch.setattr(inventory_scan,'hf_cache_roots',lambda **kw:[hub])
    monkeypatch.setattr('utils.hf_cache_settings.get_hf_cache_paths',lambda:SimpleNamespace(hub_cache=hub))
    download_manifest.write_cancel_marker('model',repo,'Q4_K_M','xet',hub_cache=hub)
    inventory_scan.invalidate_hf_cache_scans()
    result=asyncio.run(gguf_variants.get_gguf_variants_response(repo,prefer_local_cache=True))
    row=next(v for v in result.variants if v.quant=='Q4_K_M')
    assert row.downloaded and not row.partial
