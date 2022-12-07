
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import requests
import key


cred = credentials.Certificate(key.keyPath)
app = firebase_admin.initialize_app(cred)
db = firestore.client()

lineList = ["신분당선"]

def delWaste(item):
    return {
        'subwayId': item['subwayId'], 
        'statnNm': item['statnNm'],  
        'statnTnm': item['statnTnm'], 
        'trainSttus': item['trainSttus'],
        'trainNo': item['trainNo']
                                }

while True:
        for line in lineList:
            print("라인 처리중")
            url = f"http://swopenAPI.seoul.go.kr/api/subway/{key.publicDataKey}/json/realtimePosition/0/30/{line}"
            try:
                response = requests.get(url).json()["realtimePositionList"]
                trains = list(map(delWaste, response))
                trainNoList = list(map(lambda item: item["trainNo"], trains))
                print(trainNoList)
                print("열차데이터 완료")
                doc_ref = db.collection(u"{}".format(line))
                docs = doc_ref.stream()
                for doc in docs:  #db에는 있지만 api에 없는 열차(운행이 종료되었거나 정보가 제공되지 않는 열차 db에서 삭제
                    if not(doc.id in trainNoList):
                        doc_ref.document(u"{}".format(doc.id)).delete()
                        print("deleted: {}".format(doc.id))    

                for train in trains:  #공공데이터 db에 업로드
                    doc_ref.document(u"{}".format(train["trainNo"])).set(train)
                    print("updated: {}".format(train["trainNo"]))
            except:
                print("데이터에 문제 생김")        
            
            time.sleep(2)        
                            

