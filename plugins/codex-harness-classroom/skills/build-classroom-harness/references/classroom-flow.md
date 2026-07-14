# 수업 흐름

1. `codex plugin marketplace add jsk7767/codex-harness-classroom --ref main --json`을 실행한다.
2. `codex plugin add codex-harness-classroom@codex-harness-classroom --json`을 실행한다.
3. 새 Codex 세션을 열고 `내 가게 홍보팀 하네스를 구성해줘`라고 입력한다.
4. 목표 폴더와 Obsidian vault(보통 `my-llm-wiki`) 경로를 알려 준다.
5. Codex가 bundled scaffolder의 absolute path를 사용해 dry-run, 생성, validator PASS를 차례로 실행한다. validator는 파일 구조, 안전한 근거 경로, 빈 근거 파일, 초안 문장과 근거 원문의 최소 텍스트 일치를 확인한다.
6. 생성된 목표 폴더를 새 Codex 세션으로 연다. 프로젝트 범위의 custom agents는 새 세션에서 로드된다.
7. Codex에 `_workspace/promotional-draft.md` 끝에 근거 없는 `전 메뉴 20% 할인!`을 추가하고 validator를 실행해 달라고 요청한다. 학습자가 파일을 직접 편집하지 않는다.
8. FAIL을 확인한 뒤 Codex에 방금 추가한 문장만 삭제하고 validator를 다시 실행해 달라고 요청해 PASS를 확인한다.

증거 문법은 `[근거: notes/store.md]` 하나만 사용하며 경로는 사용자 제공 Obsidian vault의 루트 기준 상대 경로다.

전체 복사용 프롬프트는 저장소의 `README_KO.md`를 따른다.
