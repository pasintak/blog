@echo off
chcp 65001
echo 옵시디언 마크다운 파일을 Jekyll 블로그 포스트로 변환합니다.
echo.

REM 설정을 여기서 변경하세요
set OBSIDIAN_DIR=D:\obsidian\a\hacking_study
set JEKYLL_DIR=D:\github_repo\pasintak\pasintak
set DEFAULT_CATEGORY=개발

REM 아나콘다 환경 활성화
call D:\anaconda3\Scripts\activate.bat D:\anaconda3

REM 강제 변환 여부 (1: 모든 파일 강제 변환, 0: 변경된 파일만 변환)
set FORCE_ALL=0

if "%FORCE_ALL%"=="1" (
    echo 모든 파일을 강제로 변환합니다...
    python obsidian_to_jekyll.py --obsidian "%OBSIDIAN_DIR%" --jekyll "%JEKYLL_DIR%" --category "%DEFAULT_CATEGORY%" --force
) else (
    echo 변경된 파일만 변환합니다...
    python obsidian_to_jekyll.py --obsidian "%OBSIDIAN_DIR%" --jekyll "%JEKYLL_DIR%" --category "%DEFAULT_CATEGORY%"
)

echo.
echo 완료! 엔터를 누르면 종료합니다.
pause > nul 