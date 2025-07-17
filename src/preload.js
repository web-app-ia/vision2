const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    getPythonApps: () => ipcRenderer.invoke('get-python-apps'),
    launchPythonApp: (appInfo) => ipcRenderer.invoke('launch-python-app', appInfo),
    stopPythonApp: (appName) => ipcRenderer.invoke('stop-python-app', appName),
    getRunningApps: () => ipcRenderer.invoke('get-running-apps'),
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    showMessage: (options) => ipcRenderer.invoke('show-message', options)
});
