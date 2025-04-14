@echo off
chcp 65001
:: 设置项目主入口文件和输出文件名
set MAIN_SCRIPT=main.py
set EXE_NAME=GaaraTools
set DIST_DIR=dist
set BUILD_DIR=build

:: 检查是否安装 PyInstaller
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller 未安装，请运行以下命令安装：
    echo pip install pyinstaller
    pause
    exit /b
)

:: 删除旧的构建目录
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%

:: 检查是否已存在目标 exe 文件
if exist %DIST_DIR%\%EXE_NAME%.exe (
    echo 检测到已存在的 %EXE_NAME%.exe 文件。
    for /f %%a in ('wmic os get localdatetime ^| find "."') do set DATE=%%a
    set DATE=%DATE:~0,8%
    set BACKUP_NAME=%EXE_NAME%_%DATE%.exe
    ren "%DIST_DIR%\%EXE_NAME%.exe" "%BACKUP_NAME%"
    if %errorlevel% equ 0 (
        echo 已将原文件重命名为：%DIST_DIR%\%BACKUP_NAME%
    ) else (
        echo 重命名失败，请检查文件权限或路径。
        pause
        exit /b
    )
)

:: 打包为单个 exe 文件
echo 正在打包...
pyinstaller --onefile --noconsole --name %EXE_NAME% --distpath %DIST_DIR% --workpath %BUILD_DIR% %MAIN_SCRIPT%

:: 检查打包是否成功
if exist %DIST_DIR%\%EXE_NAME%.exe (
    echo 打包完成！可执行文件已生成：%DIST_DIR%\%EXE_NAME%.exe
) else (
    echo 打包失败，请检查错误信息。
)

pause
