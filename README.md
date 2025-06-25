# fashion-chatbot

패션 추천 챗봇을 개발해서 사람들에게 패션 코디의 접근성을 높여주는 프로젝트


# kakao business 채널 개설 및 챗봇 만들기

kakao business 홈페이지 이동 후 오른쪽상단 '내 비즈니스' 클릭
왼쪽 상단 '채널' 클릭 후 새 채널 만들기
채널 개설 후 생성한 채널에 들어가서 오른쪽 하단 '채널 공개'와 '검색 허용' on으로 변경
왼쪽 상단 채널의 '챗봇' 클릭
'봇 만들기' 클릭

# aws lambda 설정

aws lambda에 접속하여 '함수생성'을 클릭
함수 이름, 런타임(python 3.10), 아키텍처(x86_64) 설정 후 함수 생성
함수 코드 작성 후 deploy 클릭
구성 - 환경변수 - 편집에 들어가서 openai_api 설정 후 저장 (openai_api키 발급받을때 결제수단 등록)
cmd나 powershell에서 로컬환경에 python 디렉토리 생성 후 pip install openai == 0.28.1 설치
설치된 디렉토리를 zip 파일로 압축 (위와 같은 방법으로 pip translate==3.6.1도 설치 후 압축)

# 계층 추가

계층 - 계층 생성 클릭 후 이름, zip파일 업로드, 호환 아키텍처, 호환 런타임 설정 후 '생성' 클릭
add a layer 클릭 후 사용자 지정 계층으로 zip 파일 2개 업로드

