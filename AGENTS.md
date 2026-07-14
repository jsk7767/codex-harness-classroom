# codex-harness-classroom

## WHAT

이 저장소는 Obsidian 지식창고를 먼저 확인하고 Codex의 세 담당 직원이 순차적으로 홍보 문안을 만드는 한국어 교실용 플러그인이다.

## WHY

학습자가 코드나 TOML을 직접 고치지 않고도 근거 확인, 작성, 품질 검수를 분리해 허위 가게 정보를 막는다.

## HOW

- 플러그인 Skill의 스캐폴더만으로 하네스를 생성한다.
- Main Commander → Fact Checker → Content Writer → Quality Checker → PASS/FAIL 순서를 지킨다.
- 읽기 전용 독립 감사만 병렬 실행할 수 있다. 같은 파일을 쓰는 작업은 직렬로 실행한다.
- 메뉴, 가격, 할인, 영업시간, 주차, 후기, 고객 발언 및 기타 사업 사실을 지식창고 근거 없이 만들지 않는다.
- 증거는 사용자 제공 Obsidian vault 루트 기준 상대 경로를 `[근거: notes/store.md]` 형식으로만 기록한다.
- 변경 후 `python -m unittest discover -s tests -v`와 `python scripts/validate_repo.py`를 실행한다.
- 외부 패키지, 서비스, 인증정보, 원격 설치를 추가하지 않는다.
