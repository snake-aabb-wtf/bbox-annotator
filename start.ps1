# 标注工具启动脚本 (Windows / PowerShell)
# 兼容 Python 3.8~3.12（项目依赖 numpy<2，无 Python 3.13 的二进制轮子）
#
# 用法：
#   方式一：在文件资源管理器里右键本文件 -> 用 PowerShell 运行
#   方式二：在 PowerShell 中执行
#           powershell -ExecutionPolicy Bypass -File start.ps1
#   （若系统执行策略禁止脚本，需加 -ExecutionPolicy Bypass）

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

$VenvDir    = Join-Path $ScriptDir 'venv'
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'
$ReqFile    = Join-Path $ScriptDir 'requirements.txt'
$MainPy     = Join-Path $ScriptDir 'main.py'
$LogFile    = Join-Path $ScriptDir 'annotate.log'

function Get-CompatiblePython {
    $candidates = @('python')
    $local = [System.Environment]::GetEnvironmentVariable('LOCALAPPDATA')
    if ($local) { $candidates += Join-Path $local 'Programs\Python\Python312\python.exe' }
    $candidates += 'C:\Python312\python.exe'
    $candidates += Join-Path $env:USERPROFILE 'AppData\Local\Programs\Python\Python312\python.exe'

    foreach ($p in $candidates) {
        if (-not (Test-Path $p)) { continue }
        try {
            $ver = (& $p -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null)
            if ($ver -match '^(\d+)\.(\d+)$') {
                $maj = [int]$Matches[1]; $min = [int]$Matches[2]
                if ($maj -lt 3 -or ($maj -eq 3 -and $min -le 12)) { return $p }
            }
        } catch { }
    }
    return $null
}

# 1) 选择兼容的 Python 解释器
$PythonExe = Get-CompatiblePython
if (-not $PythonExe) {
    Write-Host '[ERROR] 未找到 Python 3.8~3.12，请安装后重试。' -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}
Write-Host "[setup] 使用 Python: $PythonExe"

# 2) 创建 / 校验虚拟环境
if (-not (Test-Path $VenvPython)) {
    Write-Host '[setup] 正在创建虚拟环境 ...'
    & $PythonExe -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[ERROR] 创建虚拟环境失败！' -ForegroundColor Red
        Read-Host 'Press Enter to exit'
        exit 1
    }
    Write-Host '[setup] 虚拟环境已创建'
} else {
    $vver = (& $VenvPython -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null)
    if ($vver -match '^(\d+)\.(\d+)$') {
        $maj = [int]$Matches[1]; $min = [int]$Matches[2]
        if ($maj -ge 3 -and $min -gt 12) {
            Write-Host '[setup] 现有虚拟环境 Python 版本不兼容，正在重建 ...'
            Remove-Item $VenvDir -Recurse -Force
            & $PythonExe -m venv $VenvDir
        }
    }
}

# 3) 安装依赖（仅当 cv2 无法导入时）
try {
    & $VenvPython -c "import cv2" 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host '[setup] 依赖已就绪'
} catch {
    Write-Host '[setup] 正在安装依赖 opencv-python numpy Pillow ...'
    & $VenvPython -m pip install -r $ReqFile -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[ERROR] 安装依赖失败！请检查网络连接' -ForegroundColor Red
        Read-Host 'Press Enter to exit'
        exit 1
    }
    Write-Host '[setup] 依赖安装完成'
}

# 4) 轮转日志
if (Test-Path $LogFile) {
    Copy-Item $LogFile (Join-Path $ScriptDir 'annotate.log.bak') -Force
    Remove-Item $LogFile -Force
}

# 5) 启动
Write-Host '========================================'
Write-Host '   标注工具 - 人体检测'
Write-Host '========================================'
Write-Host ' 鼠标: 左键画框  右键删框  滚轮缩放  中键平移'
Write-Host ' 键盘: D下一张  A上一张  S保存  Z撤销'
Write-Host '       C清空  R重置缩放  H帮助  Q退出'
Write-Host '========================================'
Write-Host " 日志: $LogFile"
Write-Host ''

Start-Process -FilePath $VenvPython -ArgumentList '-X','utf8',$MainPy -WindowStyle Normal
Write-Host '已启动，等待窗口 ...'
Start-Sleep -Seconds 2