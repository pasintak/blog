document.addEventListener('DOMContentLoaded', function() {
  // 모든 코드 블록을 찾아서 복사 버튼 추가
  const codeBlocks = document.querySelectorAll('pre.highlight');
  
  codeBlocks.forEach(function(codeBlock) {
    // 버튼 생성
    const copyButton = document.createElement('button');
    copyButton.className = 'copy-code-button';
    copyButton.type = 'button';
    copyButton.innerHTML = '<i class="fas fa-copy"></i>';
    copyButton.setAttribute('aria-label', '코드 복사');
    copyButton.setAttribute('title', '클립보드에 복사');
    
    // 버튼 클릭 이벤트 처리
    copyButton.addEventListener('click', function() {
      const code = codeBlock.querySelector('code').innerText;
      
      // 클립보드에 복사
      navigator.clipboard.writeText(code).then(function() {
        // 버튼 상태 변경 (체크 아이콘으로)
        copyButton.innerHTML = '<i class="fas fa-check"></i>';
        
        // 3초 후 원래 아이콘으로 복원
        setTimeout(function() {
          copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        }, 3000);
      }).catch(function(err) {
        console.error('클립보드 복사 실패:', err);
      });
    });
    
    // 코드 블록에 버튼 추가
    codeBlock.insertBefore(copyButton, codeBlock.firstChild);
  });
}); 