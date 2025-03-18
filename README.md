# 옵시디언-Jekyll 변환 도구

이 도구는 옵시디언(Obsidian) 마크다운 파일을 Jekyll 블로그 포스트로 자동 변환해주는 유틸리티입니다.

## 주요 기능

- 옵시디언 마크다운 파일을 Jekyll 포맷으로 자동 변환
- 한글 프론트매터 및 해시태그 지원
- 위키링크 자동 변환 (`[[파일명]]` → Jekyll 호환 형식)
- **변경된 파일만 변환** (효율적인 업데이트)
- 기존 파일 자동 덮어쓰기 (원본 파일 수정 후 재변환 가능)

## 사용 방법

### 1. 요구 사항

- Python 3.6 이상
- 필요한 Python 패키지: `pyyaml`

패키지 설치:
```bash
pip install pyyaml
```

### 2. 설정 변경

`convert_obsidian.bat` 파일을 열고 다음 설정을 필요에 맞게 수정하세요:

```batch
set OBSIDIAN_DIR=D:\obsidian\a\main      # 옵시디언 볼트 경로
set JEKYLL_DIR=D:\github_repo\pasintak\pasintak  # Jekyll 블로그 루트 경로
set DEFAULT_CATEGORY=옵시디언             # 기본 카테고리
set FORCE_ALL=0                          # 0: 변경된 파일만, 1: 모든 파일 강제 변환
```

### 3. 실행

`convert_obsidian.bat` 파일을 더블클릭하여 실행하면 자동으로 변환이 시작됩니다.

### 4. 결과 확인

변환된 파일은 Jekyll 블로그의 `_posts` 디렉토리에 저장됩니다.

## 변환 규칙

1. **파일명 변환**:
   - 원본: `개발 블로그 테스트문서1.md`
   - 변환: `2025-03-19-개발-블로그-테스트문서1.md`

2. **프론트매터 변환**:
   - 옵시디언 프론트매터에서 제목, 날짜, 태그 등 추출
   - Jekyll 호환 프론트매터로 자동 변환

3. **날짜 처리**:
   - 옵시디언 프론트매터의 `만든 날짜` 필드 인식 (예: `2025년 3월 19일 0시 57분`)
   - 파일명에 날짜 자동 포함

4. **위키링크 변환**:
   - 원본 파일명 → Jekyll 파일명으로 자동 매핑
   - 일반 링크 `[[파일명]]`과 임베딩 링크 `![[파일명]]` 모두 지원

5. **변경 감지**:
   - 파일 해시값을 기반으로 변경된 파일만 변환
   - 변경되지 않은 파일은 건너뛰어 빠른 처리

## 옵시디언 파일 수정 후 재변환

원본 옵시디언 파일을 수정한 후 다시 변환 도구를 실행하면, 수정된 파일만 자동으로 감지하여 변환합니다. 변경되지 않은 파일은 처리하지 않아 효율적입니다.

## 강제 변환 옵션

모든 파일을 강제로 변환하려면:
1. `convert_obsidian.bat` 파일에서 `set FORCE_ALL=1`로 설정
2. 또는 명령줄에서 `--force` 옵션 사용

## 명령줄에서 직접 실행

배치 파일 대신 명령줄에서 직접 실행할 수도 있습니다:

```bash
# 변경된 파일만 변환
python obsidian_to_jekyll.py --obsidian "D:\obsidian\a\main" --jekyll "D:\github_repo\pasintak\pasintak" --category "옵시디언"

# 모든 파일 강제 변환
python obsidian_to_jekyll.py --obsidian "D:\obsidian\a\main" --jekyll "D:\github_repo\pasintak\pasintak" --category "옵시디언" --force
```

## 주의사항

- 변환 전 중요한 파일은 백업해두세요.
- Jekyll 블로그의 `_config.yml`에 `jekyll-wikilinks` 플러그인이 설정되어 있어야 위키링크가 제대로 작동합니다.
- 캐시 파일은 `.cache` 디렉토리에 저장됩니다. 문제가 있을 경우 이 디렉토리를 삭제하고 다시 시도하세요. 