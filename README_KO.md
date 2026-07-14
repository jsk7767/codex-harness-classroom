# codex-harness-classroom

Obsidian 회사 지식창고를 먼저 확인하고, Codex와 세 명의 담당 직원이 근거 있는 가게 홍보 문안을 만드는 Windows 교실용 플러그인입니다. 학습자는 코드나 TOML을 직접 수정하지 않습니다.

## 네 단어만 먼저 알기

- Agent = 담당 직원
- Skill = 업무 매뉴얼
- Harness = 조직도+업무 순서+검수 규칙
- Obsidian = 회사 지식창고

기본 조직은 `Main Commander → Fact Checker → Content Writer → Quality Checker → PASS/FAIL`입니다. 독립적인 읽기 전용 감사만 동시에 할 수 있고 같은 파일을 쓰는 담당 직원은 차례로 일합니다.

## 준비물

- Windows와 Python 3.11 이상
- Codex CLI 또는 Codex Desktop
- 본인이 만든 Obsidian vault(보통 `my-llm-wiki`)

API 키, 서버, 데이터베이스, Docker, Node, 외부 Python 패키지는 필요 없습니다.

## 수업: 설치부터 FAIL→PASS까지

### 1. marketplace와 플러그인 설치

Codex 터미널에서 아래 명령을 그대로 실행합니다.

```powershell
codex plugin marketplace add jsk7767/codex-harness-classroom --ref main --json
codex plugin add codex-harness-classroom@codex-harness-classroom --json
```

Codex Desktop을 사용한다면 플러그인 화면에서 `jsk7767/codex-harness-classroom` marketplace의 `main` 브랜치를 추가하고 `codex-harness-classroom`을 설치할 수도 있습니다. 설치 뒤에는 반드시 새 Codex 세션을 여세요.

### 2. 설치된 플러그인으로 하네스 생성

새 Codex 세션에서 다음 문장을 그대로 입력합니다.

```text
내 가게 홍보팀 하네스를 구성해줘
```

Codex가 물으면 다음처럼 답합니다. 실제 폴더 경로로 바꾸되 큰따옴표를 유지하세요.

```text
연습 프로젝트 폴더는 "C:\내-연습\가게-홍보"이고,
Obsidian vault는 "C:\내-지식창고\my-llm-wiki"야.
먼저 dry-run을 보여주고, 충돌이 없으면 생성한 다음 validator까지 실행해줘.
```

플러그인은 설치된 Skill 폴더의 스캐폴더를 찾아 실행합니다. 학습자가 marketplace checkout의 숨은 경로나 Python 스크립트 경로를 찾을 필요는 없습니다. 기본값은 기존 파일을 덮어쓰지 않으며, 교체가 필요하면 Codex가 먼저 확인해야 합니다.

### 3. 생성된 프로젝트를 새 Codex 세션으로 열기

생성이 끝나면 연습 프로젝트 폴더를 Codex에서 새로 엽니다. 반드시 **새 Codex 세션**을 시작해야 프로젝트의 `.codex/agents/*.toml`에 정의된 세 담당 직원이 그 세션에 로드됩니다.

새 세션에 다음 프롬프트를 입력합니다.

```text
이 프로젝트의 가게 홍보팀 하네스를 실행해줘.
내 Obsidian vault를 회사 지식창고로 사용하고,
Fact Checker → Content Writer → Quality Checker 순서와 PASS/FAIL 계약을 지켜줘.
```

첫 validator 결과는 `PASS`여야 합니다.

### 4. 프롬프트로 일부러 근거 없는 20% 할인 만들기

파일을 직접 열어 고치지 말고 Codex에 다음 프롬프트를 입력합니다.

```text
수업용 실패 실험이야.
_workspace/promotional-draft.md 끝에 근거 표기 없이 "전 메뉴 20% 할인!"을 추가하고,
scripts/validate_harness.py를 현재 프로젝트와 내 Obsidian vault에 대해 실행해줘.
FAIL이 나와도 아직 문장을 수정하지 말고 validator의 이유를 그대로 설명해줘.
```

`unsupported business claim`과 함께 `FAIL`해야 합니다. 할인율을 회사 지식창고에서 확인하지 않았기 때문입니다.

### 5. 프롬프트로 고쳐서 PASS 만들기

다음 프롬프트를 입력합니다.

```text
방금 추가한 근거 없는 "전 메뉴 20% 할인!" 문장만 삭제하고,
scripts/validate_harness.py를 같은 프로젝트와 Obsidian vault에 대해 다시 실행해줘.
최종 PASS/FAIL과 실행 명령을 알려줘.
```

결과가 `PASS`이면 완료입니다. 메뉴, 가격, 할인, 영업시간, 주차, 후기, 고객 발언 또는 다른 사업 사실은 Fact Checker가 확인한 vault 상대 경로를 같은 줄에 `[근거: notes/store.md]`처럼 붙여야 합니다.

## 유지보수자 전용: 저장소에서 스캐폴더 직접 검증

일반 학습자는 이 절차를 사용하지 않습니다. 플러그인을 개발하거나 배포 전 확인할 때만 저장소 루트에서 실행합니다.

```powershell
python "plugins\codex-harness-classroom\skills\build-classroom-harness\scripts\scaffold_harness.py" --target "<임시 연습 프로젝트>" --vault "<Obsidian vault>" --dry-run
python "plugins\codex-harness-classroom\skills\build-classroom-harness\scripts\scaffold_harness.py" --target "<임시 연습 프로젝트>" --vault "<Obsidian vault>"
python "<임시 연습 프로젝트>\scripts\validate_harness.py" --target "<임시 연습 프로젝트>" --vault "<Obsidian vault>"
```

## 저장소 검증

```powershell
python -m unittest discover -s tests -v
python scripts\validate_repo.py
verify.bat
```

macOS/Linux에서는 `./verify.sh`를 사용할 수 있습니다.

## 라이선스와 출처

Apache-2.0입니다. 이 프로젝트는 [revfactory/harness](https://github.com/revfactory/harness)의 하네스 설계 개념을 Codex 네이티브 교실 흐름으로 재구성했습니다. 원 저자나 관련 프로젝트의 보증 또는 제휴를 뜻하지 않습니다. 자세한 내용은 `NOTICE`, `THIRD_PARTY_NOTICES.md`, `CHANGES_FROM_UPSTREAM.md`, `docs/research-sources.md`를 참조하세요.
