# -*- coding: utf-8 -*-

import sys
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time, random

ignored_exceptions = (StaleElementReferenceException,) #NoSuchElementException
wait_time = 11

options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument('window-size=1200x600')

browser = WebDriver(executable_path='/home/nifty/workspace/archive_today_copytest/chromedriver', chrome_options=options)

# 검색할 사이트 설정(site address)
QUERYs = ["daum.net", "www.daum.net"]


# 링크 목록 저장할 파일 이름의 접두어(반드시 로마자로 할 것)
file_head = "archive_today-"

def get_snapshots(soup, no_row):
	cover, contents = [], []

	for row in range(50):
		address, title = "", ""
		css_select = "#row"+ str(row)
		try:			
			addr = soup.select(css_select + " .TEXT-BLOCK a")[1].string 
			titl = soup.select(css_select + " .TEXT-BLOCK a")[0].string 
			if addr: address = addr
			if titl: title = titl
			cover.append((address, title))
			
			row_links = [l['href'] for l in soup.select(css_select + " .THUMBS-BLOCK  a")]
			row_dates = [d.string for d in soup.select(css_select + " .THUMBS-BLOCK a > div")]
			if not no_row:
				for n in no_row:
					if row == n:
						extra = re.compile("#extrathumbs_ ")
						row_links.insert(-2, soup.select_one(extra + " div > a").string) 
						row_dates.insert(-2, soup.select_one(extra + " div > a > div").string)
			contents.append((row_links, row_dates))
			for i in row_links:
				links_only.append(i)
		except: pass
	return zip(cover, contents)


def save_sheet(q_no, shots):
	file_name = file_head+str(q_no+1) + ".txt"
	with open(file_name, "a", encoding='utf-8') as f:
		for (cvr, cnt) in shots:
			rl, rd = cnt
			a, t = cvr
			for l, d in zip(rl, rd):
				f.write("\t".join([l, d, a, t]))
				f.write("\n")
		print(str(q_no+1) + "번째 사이트 주소의 스냅샷 중 "+str(offset+1)+"번째부터 저장함(하나의 주소에 여러 스냅샷 포함)")


if __name__ == "__main__":
	file_name = ""

	for QUERY_no, QUERY in enumerate(QUERYs):
		browser.get( "https://archive.today/offset=0/" + QUERY)

		browser.implicitly_wait(random.randint(6,11))

		# 검색 결과 마지막 쪽수 추출
		last_page = 1 # 1쪽 이내일 때 기본값 설정
		try:
			lastpageloc = "#pager"
			pages = WebDriverWait(browser, wait_time, ignored_exceptions = ignored_exceptions).until(EC.presence_of_element_located((By.CSS_SELECTOR, lastpageloc)))
		
			# total_snapshots = pages.text[:pages.text.find("개")] # 한글 지원 사이트
			total_snapshots = pages.text.split(" ")[-2] # 영문 지원 사이트
		
			last_page = (int(total_snapshots.strip()))//50 + 1
			# last_page = (int(total_snapshots.strip()))//50 - 15
			print("검색 결과 전체 "+ total_snapshots +" 개,",last_page,"번에 나누어 저장하겠습니다." )

		except: 
			print("검색 결과 50개 미만, 1쪽 이내" )
			pass

		# 페이지별로 스냅샷 추출
		page, offset = 0, 0
		# page, offset = 0, 800

		while page < last_page :
			browser.implicitly_wait(wait_time)
			last_elem = "#CONTENT"
			WebDriverWait(browser, wait_time, ignored_exceptions = ignored_exceptions).until(EC.presence_of_element_located((By.CSS_SELECTOR, last_elem)))
			browser.implicitly_wait(1)

			mores = []
			# more 단추 눌러주기
			try: 
				mores = browser.find_elements_by_tag_name("button") 
				for l, more in enumerate(mores):
					print("추가 스냅샷 ", l+1, " 열기")
					more.click()
			except: 
				print("no mores")
				pass

			html = browser.page_source
			html = BeautifulSoup(html, "lxml")
			no_row, links_only = [], []

# more 가 있는 행번호 확인			
			if mores == []:
				pass
			elif not mores:
				extrathumbs = html.select(re.compile("#extrathumbs_"))
				for extra in extrathumbs:
					no_row.append(int(extra.id[extra.id.find("_")+1:]))

# 스냅샷 목록 추출
			snapshots = get_snapshots(html, no_row)

# 날짜, 아카이브 파일(zip) 목록을 tsv 파일로 저장하기
			save_sheet(QUERY_no, snapshots) 

# 스냅샷 링크 하나씩 눌러서 저장
			for link in links_only: 
				browser.get(link)
				browser.implicitly_wait(random.randint(6,11))
				ziplink = WebDriverWait(browser, wait_time, ignored_exceptions = ignored_exceptions).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,".zip")))
				time.sleep(1)
				ziplink.send_keys(Keys.CONTROL + Keys.ENTER)
				time.sleep(5)

				# print("다운로드할 디렉토리 접근권한이 문제되는 경우")
				# print("해당 디렉토리의 상위 디렉토리로 가서 ")
				# print("sudo chmod -R 777 해당디렉토리이름")
				# print("실행 끝나고 돌려놓을 것")

			if page < (last_page - 1) : # 다음 쪽으로 넘어가기
				offset += 50
				archive_today_url = "https://archive.today/offset="+ str(offset) + QUERY
				browser.get(archive_today_url)
				page += 1
			else: 
				print(QUERY_no+1, "번째 검색어(",QUERY,")에 대한 검색 결과 마지막 페이지까지 저장")
				break

	print("총" + str(len(QUERYs)) +"개 사이트 주소에 대한 모든 아카이브 자료 저장 완료")
	browser.quit()