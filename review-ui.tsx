import React from 'react';
import { createRoot } from 'react-dom/client';
import { UpdateBanner } from './src/components/tauri/update-banner';
import { DesktopUpdateControl } from './src/features/settings/components/desktop-update-control';
import { TauriUpdateContext } from './src/hooks/tauri-update-context';
import { setLocale, translate, LOCALES } from './src/i18n';
import './src/index.css';
const params = new URLSearchParams(location.search);
const external = params.get('external') !== 'false';
const manual = params.get('manual') === 'true';
const locale = params.get('locale') ?? 'en';
await setLocale(locale as any);
(window as any).expected = translate('settings.about.update.desktopExternalServer');
(window as any).locales = Object.keys(LOCALES);
(window as any).installs = 0;
const install = () => { (window as any).installs++; };
const info = { currentVersion: '2026.9.1', version: '2026.9.2' };
const controller = {status: 'available', info, checkError: null, hasChecked: true, isExternalServer: external, updatePolicyMode: manual ? 'manual_linux_package' : 'in_app', installUpdate: install, checkForUpdate: () => {}} as any;
createRoot(document.getElementById('root')!).render(<div style={{padding:16, maxWidth:640, margin:'0 auto'}}>
<h1 style={{fontSize:20, marginBottom:16}}>Desktop update banner</h1>
<UpdateBanner status="available" info={info as any} dismissed={false} lastFailure={null} isExternalServer={external} updatePolicyMode={controller.updatePolicyMode} manualReleaseUrl="https://github.com/unslothai/unsloth/releases" positioned={false} onInstall={install} onDismiss={() => {}} onCopyDiagnostics={async () => ({ok:true}) as any} />
<h2 style={{fontSize:20, marginTop:32, marginBottom:16}}>Settings update control</h2>
<div data-testid="settings-control"><TauriUpdateContext.Provider value={controller}><DesktopUpdateControl /></TauriUpdateContext.Provider></div>
</div>);
