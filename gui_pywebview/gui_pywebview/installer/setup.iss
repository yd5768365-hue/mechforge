; MechForge AI - Inno Setup 安装脚本
; 用于创建专业的 Windows 安装程序

#define MyAppName "MechForge AI"
#define MyAppVersion "0.5.0"
#define MyAppPublisher "MechForge Team"
#define MyAppURL "https://github.com/yd5768365-hue/mechforge"
#define MyAppExeName "MechForgeAI.exe"

[Setup]
; 基本信息
AppId={{MECHFORGE-AI-0.5.0}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 输出配置
OutputDir=dist
OutputBaseFilename=MechForgeAI-{#MyAppVersion}-Setup
SetupIconFile=dj-whale.png
Compression=lzma2
SolidCompression=yes

; 安装目录
DefaultDirName={autopf}\MechForgeAI
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no

; 权限
PrivilegesRequiredOverridesAllowed=dialog
PrivilegesRequired=lowest

; 界面
WizardStyle=modern
WizardImageFile=installer\wizard-image.bmp
WizardSmallImageFile=installer\wizard-small-image.bmp

; 其他
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoTextVersion={#MyAppVersion}

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 主程序文件
Source: "dist\MechForgeAI\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\MechForgeAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 额外文件
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists("LICENSE")

[Icons]
; 开始菜单
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; 桌面快捷方式
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; 快速启动
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 安装完成后可选运行
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除的文件
Type: filesandordirs; Name: "{app}\cache"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\temp"

[Registry]
; 注册表项（可选）
Root: HKCU; Subkey: "Software\MechForgeAI"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\MechForgeAI"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey

[Code]
// 检查是否已安装
function InitializeSetup(): Boolean;
begin
  Result := True;
  // 可以在这里添加版本检查逻辑
end;

// 安装完成后的处理
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 安装完成后的额外操作
    // 例如：创建配置文件、初始化数据等
  end;
end;

// 卸载前的处理
function InitializeUninstall(): Boolean;
begin
  Result := True;
  // 可以在这里添加卸载确认对话框
end;
