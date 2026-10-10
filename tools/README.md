# AI 도감 페이지 만들기

점수·장단점·후기를 고칠 때:
1. `assets/data.js`를 고쳐요.
2. 사이트 폴더 맨 위에서 `python3 tools/build.py`를 실행해요. (node 필요)
3. 바뀐 파일(index.html, ai 폴더, sitemap.xml 등)을 GitHub에 올려요.

직접 실행하기 어려우면 Claude에게 `tools/build.py`와 `assets/data.js`를 주고
"이렇게 고쳐서 페이지 다시 만들어 줘"라고 부탁하면 돼요.

디자인만 바꿀 때는 `assets/style.css`, 동작만 바꿀 때는 `assets/app.js`만 고치면 되고
다시 만들 필요는 없어요.

새 AI를 추가할 때:
- `assets/data.js`의 TOOLS 맨 아래에 붙이고, `no`(도감 번호)는 지금 가장 큰 번호 + 1로 정해요.
- 한 번 정한 도감 번호는 바꾸지 않아요. (공유된 링크와 사람들 기억이 꼬이지 않게)
