#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import shutil
import yaml
import datetime
import time
from pathlib import Path
import argparse
import hashlib

def extract_front_matter(content):
    """옵시디언 마크다운 파일에서 프론트매터 추출"""
    front_matter = {}
    
    # 프론트매터가 있는지 확인
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                # 프론트매터 부분만 추출
                front_matter_text = parts[1].strip()
                front_matter = yaml.safe_load(front_matter_text) or {}
                
                # 만든 날짜 추출 (한글 형식: 2025년 3월 19일 0시 57분)
                if '만든 날짜' in front_matter:
                    date_str = front_matter['만든 날짜']
                    date_match = re.search(r'(\d+)년\s+(\d+)월\s+(\d+)일\s+(\d+)시\s+(\d+)분', date_str)
                    if date_match:
                        year, month, day, hour, minute = map(int, date_match.groups())
                        front_matter['date'] = datetime.datetime(year, month, day, hour, minute)
            except Exception as e:
                print(f"프론트매터 파싱 오류: {e}")
    
    return front_matter

def extract_tags_from_content(content):
    """마크다운 내용에서 해시태그 추출"""
    tags = []
    # #태그 형식 추출 (한글 태그 지원)
    hashtags = re.findall(r'#([\w가-힣]+)', content)
    for tag in hashtags:
        # 년, 월, 일, 시, 분과 같은 일반적인 시간 태그는 제외
        if tag not in ['년', '월', '일', '시', '분']:
            tags.append(tag)
    return tags

def create_jekyll_front_matter(title, date, categories=None, tags=None):
    """Jekyll 프론트매터 생성"""
    front_matter = {
        'title': title,
        'date': date.strftime('%Y-%m-%d')
    }
    
    if categories:
        front_matter['categories'] = categories
    
    if tags:
        front_matter['tags'] = tags
    
    return front_matter

def convert_wiki_links(content, file_mapping):
    """위키링크를 Jekyll 호환 형식으로 변환"""
    # 원본 링크를 유지하면서 Jekyll 형식도 추가
    def replace_wiki_link(match):
        orig_name = match.group(1)
        if orig_name in file_mapping:
            jekyll_name = file_mapping[orig_name]
            # 원본 링크 텍스트를 유지하고, Jekyll이 인식할 수 있는 형태로 링크 변환
            return f"[[{orig_name}|{jekyll_name}]]"
        return match.group(0)
    
    # 임베딩 위키링크 ![[파일명]] 변환
    def replace_embed_link(match):
        orig_name = match.group(1)
        if orig_name in file_mapping:
            jekyll_name = file_mapping[orig_name]
            # 원본 임베딩 링크 텍스트를 유지하고, Jekyll이 인식할 수 있는 형태로 링크 변환
            return f"![[{orig_name}|{jekyll_name}]]"
        return match.group(0)
    
    # 위키링크 변환
    content = re.sub(r'\[\[(.*?)\]\]', replace_wiki_link, content)
    # 임베딩 위키링크 변환
    content = re.sub(r'!\[\[(.*?)\]\]', replace_embed_link, content)
    
    return content

def get_file_hash(file_path):
    """파일의 해시값 계산 (변경 감지용)"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_file_mapping_cache(cache_file):
    """파일 매핑 캐시 로드"""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"캐시 파일 로드 오류: {e}")
    return {}

def save_file_mapping_cache(cache_file, mapping):
    """파일 매핑 캐시 저장"""
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            yaml.dump(mapping, f, allow_unicode=True)
    except Exception as e:
        print(f"캐시 파일 저장 오류: {e}")

def convert_obsidian_to_jekyll(obsidian_dir, jekyll_dir, category='옵시디언', force_all=False):
    """옵시디언 파일을 Jekyll 포스트로 변환"""
    # 출력 디렉토리 생성
    jekyll_posts_dir = os.path.join(jekyll_dir, '_posts')
    os.makedirs(jekyll_posts_dir, exist_ok=True)
    
    # 캐시 파일 경로
    cache_dir = os.path.join(jekyll_dir, '.cache')
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, 'obsidian_jekyll_cache.yaml')
    
    # 캐시 로드
    cache = load_file_mapping_cache(cache_file)
    file_hash_cache = cache.get('file_hash', {})
    title_mapping_cache = cache.get('title_mapping', {})
    
    # 변환된 파일명 매핑 (원본파일명 -> Jekyll파일명)
    file_mapping = {}
    updated_file_hash = {}
    
    # 파일 먼저 스캔하여 매핑 생성
    for root, _, files in os.walk(obsidian_dir):
        for file in files:
            if file.endswith('.md'):
                original_path = os.path.join(root, file)
                
                # 파일 내용 읽기
                with open(original_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 프론트매터 추출
                front_matter = extract_front_matter(content)
                
                # 제목과 날짜 결정
                title = os.path.splitext(file)[0]
                if 'title' in front_matter:
                    title = front_matter['title']
                
                date = datetime.datetime.now()
                if 'date' in front_matter:
                    date = front_matter['date']
                elif '만든 날짜' in front_matter:
                    # 이미 extract_front_matter에서 처리됨
                    if 'date' in front_matter:
                        date = front_matter['date']
                
                # Jekyll 파일명 생성 (YYYY-MM-DD-title.md)
                pattern = r'[^\w\-]'
                replaced_title = re.sub(pattern, '-', title)
                jekyll_filename = f"{date.strftime('%Y-%m-%d')}-{replaced_title}.md"
                jekyll_filename = re.sub(r'-+', '-', jekyll_filename)  # 중복 하이픈 제거
                
                # 매핑 저장
                file_mapping[title] = os.path.splitext(jekyll_filename)[0]
    
    # 기존 매핑과 병합 (위키링크 변환을 위해)
    for title, jekyll_name in title_mapping_cache.items():
        if title not in file_mapping:
            file_mapping[title] = jekyll_name
    
    # 변경된 파일 감지 및 변환
    files_converted = 0
    files_skipped = 0
    
    for root, _, files in os.walk(obsidian_dir):
        for file in files:
            if file.endswith('.md'):
                original_path = os.path.join(root, file)
                
                # 파일 해시 계산
                current_hash = get_file_hash(original_path)
                updated_file_hash[original_path] = current_hash
                
                # 파일이 변경되지 않았으면 스킵
                if not force_all and original_path in file_hash_cache and file_hash_cache[original_path] == current_hash:
                    files_skipped += 1
                    continue
                
                # 파일 내용 읽기
                with open(original_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 프론트매터 추출
                front_matter = extract_front_matter(content)
                
                # 제목과 날짜 결정
                title = os.path.splitext(file)[0]
                if 'title' in front_matter:
                    title = front_matter['title']
                
                date = datetime.datetime.now()
                if 'date' in front_matter:
                    date = front_matter['date']
                elif '만든 날짜' in front_matter:
                    if 'date' in front_matter:
                        date = front_matter['date']
                
                # 태그 추출
                tags = extract_tags_from_content(content)
                if 'tags' in front_matter and isinstance(front_matter['tags'], list):
                    tags.extend(front_matter['tags'])
                
                # 카테고리 결정
                categories = [category]
                if 'categories' in front_matter and isinstance(front_matter['categories'], list):
                    categories = front_matter['categories']
                
                # Jekyll 프론트매터 생성
                jekyll_front_matter = create_jekyll_front_matter(
                    title=title,
                    date=date,
                    categories=categories,
                    tags=list(set(tags))  # 중복 제거
                )
                
                # 프론트매터를 YAML 형식으로 변환
                jekyll_front_matter_str = yaml.dump(
                    jekyll_front_matter, 
                    allow_unicode=True,
                    default_flow_style=False
                )
                
                # 본문 추출 (원래 프론트매터 제외)
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        body = parts[2].strip()
                    else:
                        body = content
                else:
                    body = content
                
                # 위키링크 변환
                body = convert_wiki_links(body, file_mapping)
                
                # Jekyll 포스트 생성
                jekyll_content = f"---\n{jekyll_front_matter_str}---\n\n{body}"
                
                # Jekyll 파일명 생성
                pattern = r'[^\w\-]'
                replaced_title = re.sub(pattern, '-', title)
                jekyll_filename = f"{date.strftime('%Y-%m-%d')}-{replaced_title}.md"
                jekyll_filename = re.sub(r'-+', '-', jekyll_filename)  # 중복 하이픈 제거
                jekyll_path = os.path.join(jekyll_posts_dir, jekyll_filename)
                
                # 파일 저장
                with open(jekyll_path, 'w', encoding='utf-8') as f:
                    f.write(jekyll_content)
                
                files_converted += 1
                print(f"변환됨: {original_path} -> {jekyll_path}")
    
    # 캐시 업데이트 및 저장
    cache = {
        'file_hash': updated_file_hash,
        'title_mapping': file_mapping,
        'last_update': datetime.datetime.now().isoformat()
    }
    save_file_mapping_cache(cache_file, cache)
    
    print(f"\n총 {files_converted}개 파일 변환, {files_skipped}개 파일 스킵 (변경 없음)")

def main():
    parser = argparse.ArgumentParser(description='옵시디언 마크다운 파일을 Jekyll 블로그 포스트로 변환')
    parser.add_argument('--obsidian', required=True, help='옵시디언 볼트 디렉토리 경로')
    parser.add_argument('--jekyll', required=True, help='Jekyll 블로그 루트 디렉토리 경로')
    parser.add_argument('--category', default='옵시디언', help='기본 카테고리 (기본값: 옵시디언)')
    parser.add_argument('--force', action='store_true', help='모든 파일 강제 변환 (기본: 변경된 파일만)')
    
    args = parser.parse_args()
    
    convert_obsidian_to_jekyll(args.obsidian, args.jekyll, args.category, args.force)

if __name__ == "__main__":
    main() 