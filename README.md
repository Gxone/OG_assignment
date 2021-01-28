## OG_assignment

- Django 풀스택 기반 설문조사 서비스
- 개발기간 : 2021/1/21 ~ 2021/1/28

<br />

### 실행 방법

- [설문조사 페이지](http://52.79.114.242:8000/survey/)
- [어드민 페이지](http://52.79.114.242:8000/admin/)
> admin / qweasd123 으로 접속

<br />

- [my_settings.py 구글 드라이브](https://drive.google.com/file/d/1CN7pf4ZluowtfYwmVOCLagjWoKmjr6hf/view?usp=sharing)
- [requirements](https://drive.google.com/file/d/1dSDPp916ItXhbc0NiDmwgmETFWafoZfB/view?usp=sharing) 에 패키지 정보 저장 (pip install -r requirements.txt)
- 관리자 페이지 Survey-Surveys에서 문항 및 선택지 모두 생성, 추가, 삭제 
- 관리자 페이지 Survey-Survey answers에서 action (Export to csv)을 통해 선택 응답을 csv 파일로 다운로드
- 관리자 페이지의 nav 에서 문항 별 설문조사 결과와 응답자 별 설문조사 결과페이지 링크

<br />

### ERD

![erd](https://user-images.githubusercontent.com/26542094/106050926-1ba1ab00-612b-11eb-9860-2258b3f4dfd5.png)

<br />

## 적용 기술 및 구현 기능

### 적용 기술

> - Front-End : Django 2.2 템플릿 엔진 기반
> - Back-End : Django 2.2, MySQL
> - Common : AWS(EC2,RDS), RESTful API

<br />

### 구현 기능

#### 설문조사 페이지

- [x] 관리자 페이지에서 문항, 선택지 생성 시 적용 
- [x] 모든 설문에 대한 응답과 전화 번호 입력 후 제출 가능
- [ ] check box 선택 개수 제한

<br />

#### 관리자 페이지

- [x] 설문 문항의 유형 select, radio, check box
- [x] 관리자 페이지에서 설문 문항 추가, 수정, 삭제 가능
- [x] 문항마다 선택지 별 응답 비율 확인 가능
- [x] 응답자마다 응답한 내용 확인 가능
- [x] 버튼을 통해 설문 결과 csv 파일로 다운

#### 공통
- [x] Aws Ec2, Rds, gunicorn
- [ ] nginx (배포 시 static 파일 적용)

<br />

![image](https://user-images.githubusercontent.com/26542094/106123698-9d322100-619d-11eb-9c66-2b400e376946.png)<br />

![image](https://user-images.githubusercontent.com/26542094/106123890-d7032780-619d-11eb-9156-cad32db65852.png)<br />

![image](https://user-images.githubusercontent.com/26542094/106123970-ebdfbb00-619d-11eb-946a-580418514d49.png)<br />

![image](https://user-images.githubusercontent.com/26542094/106123992-f13d0580-619d-11eb-9994-0bc6647fc18f.png)

![image](https://user-images.githubusercontent.com/26542094/106124051-02861200-619e-11eb-80bb-1babf4d1efee.png)
