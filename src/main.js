const { app, BrowserWindow, ipcMain, shell, dialog, Menu } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');
const https = require('https');

let mainWindow;
let runningProcesses = new Map();

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        x: 100,
        y: 100,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, '../assets/icon.ico'),
        title: 'Computer Vision Applications',
        show: false
    });
    console.log('BrowserWindow created');

    mainWindow.loadFile(path.join(__dirname, 'index.html'))
    .then(() => {
        console.log('index.html loaded successfully');
        mainWindow.show();
        // Only open dev tools in development
        if (process.env.NODE_ENV === 'development') {
            mainWindow.webContents.openDevTools();
        }
    })
    .catch(err => {
        console.error('Failed to load index.html:', err);
    });

    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
        console.error('Failed to load content:', errorCode, errorDescription);
    });

    mainWindow.on('closed', () => {
        // Arrêter tous les processus Python en cours
        for (const [appName, process] of runningProcesses) {
            if (process && !process.killed) {
                process.kill();
            }
        }
        runningProcesses.clear();
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    createWindow();
    setupAutoUpdater();
    checkForUpdates();
    createMenu();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Fonction pour obtenir le chemin des ressources selon l'environnement
function getResourcePath() {
    if (app.isPackaged) {
        // Dans l'exécutable, avec asar:false, les ressources sont dans resources/app
        return path.join(process.resourcesPath, 'app');
    } else {
        // En développement, utiliser __dirname
        return path.join(__dirname, '..');
    }
}

// Fonction pour copier récursivement un dossier
function copyFolderRecursive(src, dest) {
    if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest, { recursive: true });
    }
    
    const files = fs.readdirSync(src);
    for (const file of files) {
        const srcPath = path.join(src, file);
        const destPath = path.join(dest, file);
        
        if (fs.statSync(srcPath).isDirectory()) {
            copyFolderRecursive(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}

// Fonction pour créer un fichier batch temporaire
function createTempBatchFile(appInfo) {
    const tempDir = path.join(os.tmpdir(), 'computer-vision-app');
    if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
    }
    
    // Créer un dossier temporaire pour cette application
    const appTempDir = path.join(tempDir, appInfo.name);
    if (fs.existsSync(appTempDir)) {
        // Supprimer le dossier existant
        fs.rmSync(appTempDir, { recursive: true, force: true });
    }
    
    // Copier tous les fichiers et dossiers de l'application
    try {
        copyFolderRecursive(appInfo.path, appTempDir);
        console.log(`Files copied to temp dir: ${appTempDir}`);
    } catch (error) {
        console.error('Error copying files:', error);
    }
    
    const tempBatchPath = path.join(tempDir, `${appInfo.name}-launch.bat`);
    const batchContent = `@echo off
echo ====================================
echo   ${appInfo.name}
echo ====================================
echo.

REM Changer vers le répertoire temporaire de l'application
cd /d "${appTempDir}"

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
)

echo Installation/Mise à jour des dépendances...
pip install opencv-python mediapipe numpy

echo.
echo Lancement de l'application...
echo.

REM Lancer l'application Python
echo Démarrage de ${appInfo.name}...
python main.py

echo Application terminée
pause
`;
    
    fs.writeFileSync(tempBatchPath, batchContent);
    return tempBatchPath;
}

// IPC Handlers
ipcMain.handle('get-python-apps', () => {
    const resourcePath = getResourcePath();
    const appsDir = path.join(resourcePath, 'python-apps');
    const categoriesPath = path.join(resourcePath, 'config/categories.json');
    const apps = [];
    let categories = {};

    console.log('DEBUG: Resource path:', resourcePath);
    console.log('DEBUG: Apps directory:', appsDir);
    console.log('DEBUG: Categories path:', categoriesPath);
    console.log('DEBUG: Apps directory exists:', fs.existsSync(appsDir));
    console.log('DEBUG: Categories file exists:', fs.existsSync(categoriesPath));

    try {
        // Charger les catégories depuis le fichier JSON
        if (fs.existsSync(categoriesPath)) {
            const categoriesFile = fs.readFileSync(categoriesPath);
            categories = JSON.parse(categoriesFile).categories;
            console.log('DEBUG: Categories loaded:', Object.keys(categories));
        } else {
            console.log('DEBUG: Categories file not found!');
        }

        // Scanner les applications et les associer aux catégories
        const categoryKeys = Object.keys(categories);
        for (const category of categoryKeys) {
            const categoryPath = path.join(appsDir, category);
            if (fs.existsSync(categoryPath) && fs.statSync(categoryPath).isDirectory()) {
                const categoryApps = fs.readdirSync(categoryPath);
                
                for (const appName of categoryApps) {
                    const appPath = path.join(categoryPath, appName);
                    if (fs.statSync(appPath).isDirectory()) {
                        const mainPyPath = path.join(appPath, 'main.py');
                        const batchPath = path.join(appPath, 'launch.bat');
                        
                        if (fs.existsSync(mainPyPath)) {
                            apps.push({
                                name: appName,
                                category: category,
                                path: appPath,
                                mainPy: mainPyPath,
                                batchFile: batchPath,
                                hasLauncher: fs.existsSync(batchPath)
                            });
                        }
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error reading Python apps:', error);
    }
    
    // Retourner les applications et les catégories
    return { apps, categories };
});

ipcMain.handle('launch-python-app', async (event, appInfo) => {
    try {
        // Arrêter le processus précédent s'il existe
        if (runningProcesses.has(appInfo.name)) {
            const oldProcess = runningProcesses.get(appInfo.name);
            if (oldProcess && !oldProcess.killed) {
                oldProcess.kill();
            }
        }

        let process;
        
        if (app.isPackaged) {
            // Dans l'exécutable, créer un batch temporaire et lancer Python directement
            const tempBatchPath = createTempBatchFile(appInfo);
            
            // Lancer directement le fichier batch
            process = spawn('cmd', ['/c', tempBatchPath], {
                cwd: path.dirname(tempBatchPath),
                stdio: 'ignore',
                detached: true,
                windowsHide: false
            });
        } else {
            // En développement, utiliser le comportement normal
            if (appInfo.hasLauncher && fs.existsSync(appInfo.batchFile)) {
                // Lancer via le fichier batch
                process = spawn('cmd', ['/c', appInfo.batchFile], {
                    cwd: appInfo.path,
                    stdio: 'ignore',
                    detached: true,
                    windowsHide: false
                });
            } else {
                // Lancer directement Python
                process = spawn('python', [appInfo.mainPy], {
                    cwd: appInfo.path,
                    stdio: 'ignore',
                    detached: true,
                    windowsHide: false
                });
            }
        }

        runningProcesses.set(appInfo.name, process);

        process.on('error', (error) => {
            console.error(`Error launching ${appInfo.name}:`, error);
            runningProcesses.delete(appInfo.name);
        });

        process.on('exit', (code) => {
            console.log(`${appInfo.name} exited with code ${code}`);
            runningProcesses.delete(appInfo.name);
        });

        return { success: true, message: `${appInfo.name} lancé avec succès` };
    } catch (error) {
        console.error('Error launching app:', error);
        return { success: false, message: error.message };
    }
});

ipcMain.handle('stop-python-app', async (event, appName) => {
    try {
        if (runningProcesses.has(appName)) {
            const process = runningProcesses.get(appName);
            if (process && !process.killed) {
                process.kill();
                runningProcesses.delete(appName);
                return { success: true, message: `${appName} arrêté` };
            }
        }
        return { success: false, message: 'Processus non trouvé' };
    } catch (error) {
        return { success: false, message: error.message };
    }
});

ipcMain.handle('get-running-apps', () => {
    return Array.from(runningProcesses.keys());
});

ipcMain.handle('open-external', async (event, url) => {
    try {
        await shell.openExternal(url);
        return { success: true };
    } catch (error) {
        return { success: false, message: error.message };
    }
});

ipcMain.handle('show-message', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
});

// Auto-updater functions
function setupAutoUpdater() {
    // Configuration de l'auto-updater
    autoUpdater.setFeedURL({
        provider: 'github',
        owner: 'web-app-ia',
        repo: 'vision2',
        private: false
    });

    // Événements de l'auto-updater
    autoUpdater.on('checking-for-update', () => {
        console.log('Recherche de mise à jour...');
        if (mainWindow) {
            mainWindow.webContents.send('update-status', {
                type: 'checking',
                message: 'Recherche de mise à jour...'
            });
        }
    });

    autoUpdater.on('update-available', (info) => {
        console.log('Mise à jour disponible:', info.version);
        if (mainWindow) {
            mainWindow.webContents.send('update-status', {
                type: 'available',
                message: `Mise à jour disponible: ${info.version}`,
                version: info.version
            });
        }
    });

    autoUpdater.on('update-not-available', (info) => {
        console.log('Aucune mise à jour disponible');
        if (mainWindow) {
            mainWindow.webContents.send('update-status', {
                type: 'not-available',
                message: 'Application à jour'
            });
        }
    });

    autoUpdater.on('error', (err) => {
        console.error('Erreur de mise à jour:', err);
        if (mainWindow) {
            mainWindow.webContents.send('update-status', {
                type: 'error',
                message: 'Erreur lors de la vérification des mises à jour'
            });
        }
    });

    autoUpdater.on('download-progress', (progressObj) => {
        let log_message = "Téléchargement: " + progressObj.percent + '%';
        log_message = log_message + ' (' + progressObj.transferred + "/" + progressObj.total + ')';
        console.log(log_message);
        if (mainWindow) {
            mainWindow.webContents.send('update-status', {
                type: 'downloading',
                message: log_message,
                percent: progressObj.percent
            });
        }
    });

    autoUpdater.on('update-downloaded', (info) => {
        console.log('Mise à jour téléchargée');
        if (mainWindow) {
            mainWindow.webContents.send('update-status', {
                type: 'downloaded',
                message: 'Mise à jour prête à installer',
                version: info.version
            });
        }
        
        // Demander à l'utilisateur s'il veut redémarrer
        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Mise à jour prête',
            message: 'La mise à jour a été téléchargée. Voulez-vous redémarrer maintenant?',
            buttons: ['Redémarrer', 'Plus tard'],
            defaultId: 0
        }).then((result) => {
            if (result.response === 0) {
                autoUpdater.quitAndInstall();
            }
        });
    });
}

// Fonction pour vérifier les mises à jour via GitHub API
function checkGitHubUpdates() {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.github.com',
            path: '/repos/web-app-ia/vision2/releases/latest',
            method: 'GET',
            headers: {
                'User-Agent': 'computer-vision-app'
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const release = JSON.parse(data);
                    resolve({
                        version: release.tag_name.replace('v', ''),
                        downloadUrl: release.assets[0]?.browser_download_url,
                        releaseNotes: release.body
                    });
                } catch (error) {
                    reject(error);
                }
            });
        });
        
        req.on('error', reject);
        req.end();
    });
}

// Fonction pour télécharger une mise à jour
function downloadUpdate(url, destination) {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(destination);
        
        https.get(url, (response) => {
            response.pipe(file);
            
            file.on('finish', () => {
                file.close();
                resolve(destination);
            });
            
            file.on('error', (error) => {
                fs.unlink(destination, () => {});
                reject(error);
            });
        }).on('error', reject);
    });
}

function checkForUpdates() {
    if (process.env.NODE_ENV !== 'development') {
        if (app.isPackaged) {
            // Pour les versions empaquetées, utiliser l'auto-updater
            autoUpdater.checkForUpdatesAndNotify();
        } else {
            // Pour les versions de développement, vérifier manuellement
            console.log('Mode développement - vérification des mises à jour désactivée');
        }
    }
}

function createMenu() {
    const template = [
        {
            label: 'Fichier',
            submenu: [
                {
                    label: 'Actualiser',
                    accelerator: 'CmdOrCtrl+R',
                    click: () => {
                        if (mainWindow) {
                            mainWindow.reload();
                        }
                    }
                },
                { type: 'separator' },
                {
                    label: 'Quitter',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Aide',
            submenu: [
                {
                    label: 'Vérifier les mises à jour',
                    click: () => {
                        checkForUpdates();
                    }
                },
                { type: 'separator' },
                {
                    label: 'À propos',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'À propos',
                            message: 'Computer Vision App',
                            detail: `Version: ${app.getVersion()}\n\nUne collection d'applications de vision par ordinateur avec des jeux interactifs.`
                        });
                    }
                },
                {
                    label: 'GitHub',
                    click: () => {
                        shell.openExternal('https://github.com/web-app-ia/vision2');
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// IPC pour les mises à jour
ipcMain.handle('check-for-updates', () => {
    checkForUpdates();
});

ipcMain.handle('check-github-updates', async () => {
    try {
        const updateInfo = await checkGitHubUpdates();
        const currentVersion = app.getVersion();
        
        if (updateInfo.version !== currentVersion) {
            return {
                updateAvailable: true,
                currentVersion,
                newVersion: updateInfo.version,
                downloadUrl: updateInfo.downloadUrl,
                releaseNotes: updateInfo.releaseNotes
            };
        }
        
        return { updateAvailable: false, currentVersion };
    } catch (error) {
        console.error('Error checking GitHub updates:', error);
        return { error: error.message };
    }
});

ipcMain.handle('download-github-update', async (event, downloadUrl) => {
    try {
        const tempDir = path.join(os.tmpdir(), 'computer-vision-app-update');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }
        
        const fileName = path.basename(downloadUrl);
        const downloadPath = path.join(tempDir, fileName);
        
        await downloadUpdate(downloadUrl, downloadPath);
        
        return { success: true, filePath: downloadPath };
    } catch (error) {
        console.error('Error downloading update:', error);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('install-update', () => {
    autoUpdater.quitAndInstall();
});

ipcMain.handle('open-downloaded-update', (event, filePath) => {
    shell.openPath(filePath);
});
