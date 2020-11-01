# archive_analysis

 archive.today 에 아카이브된 사이트 자료를 다운로드 받는다

- 스냅샷의 목록을 추출해서 tsv 파일로 저장한다
- selenium + chrome을 통해 스냅샷 압축 파일(.zip)을 다운로드 받는다.
- 다운로드 받을 디렉토리는 별도 설정할 수 없다(크롬 드라이버의 한계)
- 쿼리당 3000개까지만 검색결과를 보여주므로 쿼리 목록을 적절히 설정해야 한다
- waiting time 충분하지 않으면 로봇으로 인식해 아카이브된 페이지 대신 캡챠 화면을 다운받게 된다
