from __future__ import print_function
import httplib2
import os
import io
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload,MediaIoBaseDownload

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
#官方制式例外處理
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Python OCR'

def get_credentials():
    '''
      取得有效的憑證 若沒有憑證或憑證失效就會自動取得新的憑證
      傳回值:取得的憑證
    '''
    credentials_path = os.path.join('./','google-ocr-credential.json')
    store = Storage(credentials_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow,store,flags)
        else:
            credentials = tools.run(flow,store)
            print('憑證儲存於:'+credentials_path)
    return credentials

def main():
    #取得憑證建立google雲端硬碟的API服務物件
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive','v3',http=http)
    #包含文字內容的圖片檔案(png/jpg/bmp/gif)
    imgfile = 'sample.jpg'
    #輸出辨識的文字
    txtfile = 'output.txt'
    #上傳成google文件檔 讓google雲端硬碟自動辨識文字
    mime = 'application/vnd.google-apps.document'
    res = service.files().create(
        body = {
            'name':imgfile,
            'mimeType':mime},
        media_body = MediaFileUpload(imgfile,mimetype=mime, resumable=True)
    ).execute()
    #下載辨識結果 儲存為文字檔
    downloader = MediaIoBaseDownload(
        io.FileIO(txtfile,'wb'),
        service.files().export_media(
            fileId = res['id'],mimeType='text/plain'))
    done = False
    while done is False:
        status,done = downloader.next_chunk()
if __name__ == '__main__':
    main()